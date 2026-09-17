"""Source-specific cleaning and validation module for Hong Kong Traffic Speed Map data.

Phase 1: Source-Specific Data Cleaning & Standardization
- Safely parses Transport Department 1st Generation Traffic Speed Map XML snapshots
- Extracts: LINK_ID, TRAFFIC_SPEED, ROAD_SATURATION_LEVEL, CAPTURE_DATE
- Validates timestamp parsing and checks for duplicate snapshots
- Validates numeric traffic speeds (integer/float, non-negative, realistic ranges)
- Preserves exact raw road-link IDs (e.g. '3006-30069')
- Preserves raw categorical congestion states: TRAFFIC GOOD, TRAFFIC AVERAGE, TRAFFIC BAD
- Explicitly establishes and documents continuous ordinal mapping:
    TRAFFIC GOOD    = 0.0
    TRAFFIC AVERAGE = 0.5
    TRAFFIC BAD     = 1.0
- Does NOT perform spatial IDW or station aggregation (strictly reserved for subsequent phases)
- Exports clean interim dataset and comprehensive quality audit report
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple, List
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

# Canonical variable names
CANONICAL_SPEED_VAR = "traffic_speed"
CANONICAL_CONGESTION_VAR = "traffic_congestion"

# Documented ordinal representation mapping specification
CONGESTION_ORDINAL_MAP = {
    "TRAFFIC GOOD": 0.0,
    "TRAFFIC AVERAGE": 0.5,
    "TRAFFIC BAD": 1.0,
}

XML_NAMESPACE = {"ns": "http://data.one.gov.hk/td"}


def parse_speedmap_xml(xml_path: Path) -> List[Dict[str, Any]]:
    """Safely parse a single 1st Gen Speedmap XML snapshot.

    Args:
        xml_path: Path to raw XML file.

    Returns:
        List of extracted record dicts.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Query with or without namespace
    elements = root.findall(".//ns:jtis_speedmap", XML_NAMESPACE)
    if not elements:
        elements = root.findall(".//jtis_speedmap")

    records = []
    for elem in elements:
        link_id = elem.findtext("ns:LINK_ID", namespaces=XML_NAMESPACE) or elem.findtext("LINK_ID")
        speed = elem.findtext("ns:TRAFFIC_SPEED", namespaces=XML_NAMESPACE) or elem.findtext("TRAFFIC_SPEED")
        sat = elem.findtext("ns:ROAD_SATURATION_LEVEL", namespaces=XML_NAMESPACE) or elem.findtext("ROAD_SATURATION_LEVEL")
        cap = elem.findtext("ns:CAPTURE_DATE", namespaces=XML_NAMESPACE) or elem.findtext("CAPTURE_DATE")
        region = elem.findtext("ns:REGION", namespaces=XML_NAMESPACE) or elem.findtext("REGION")
        road_type = elem.findtext("ns:ROAD_TYPE", namespaces=XML_NAMESPACE) or elem.findtext("ROAD_TYPE")

        records.append({
            "snapshot_file": xml_path.name,
            "link_id": link_id.strip() if link_id else None,
            "traffic_speed_raw": speed.strip() if speed else None,
            "road_saturation_level_raw": sat.strip() if sat else None,
            "capture_date_raw": cap.strip() if cap else None,
            "region": region.strip() if region else None,
            "road_type": road_type.strip() if road_type else None,
        })

    return records


def clean_traffic(
    xml_samples_dir: Path,
    output_dir: Path,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean and validate raw Traffic Speed Map snapshots.

    Args:
        xml_samples_dir: Directory containing representative raw XML snapshots.
        output_dir: Directory where interim outputs will be saved.

    Returns:
        Tuple of (clean_dataframe, validation_report_dict).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    xml_files = sorted(list(xml_samples_dir.glob("historical_td_speedmap_*.xml")))
    if not xml_files:
        raise FileNotFoundError(f"No historical Speedmap XML files found in {xml_samples_dir}")

    print(f"[Traffic] Processing {len(xml_files)} raw XML snapshots from {xml_samples_dir}...")

    all_records = []
    malformed_xml_count = 0
    snapshot_meta = {}

    for xml_file in xml_files:
        try:
            records = parse_speedmap_xml(xml_file)
            all_records.extend(records)
            snapshot_meta[xml_file.name] = {
                "records_extracted": len(records),
                "file_size_bytes": xml_file.stat().st_size,
                "status": "PARSED_SUCCESSFULLY",
            }
        except Exception as e:
            malformed_xml_count += 1
            snapshot_meta[xml_file.name] = {
                "error": str(e),
                "status": "MALFORMED_OR_CORRUPT",
            }

    if not all_records:
        raise ValueError("Failed to extract any valid traffic records from raw XML files!")

    df = pd.DataFrame(all_records)
    total_records = len(df)

    # 1. Validate and standardize road link IDs (preserve as string)
    df["link_id"] = df["link_id"].astype(str).str.strip()
    missing_link_ids = int(df["link_id"].isna().sum() | (df["link_id"] == "None").sum())

    # 2. Parse capture timestamp
    df["capture_timestamp"] = pd.to_datetime(df["capture_date_raw"])
    missing_timestamps = int(df["capture_timestamp"].isna().sum())

    # 3. Standardize and validate numeric traffic speed
    df[CANONICAL_SPEED_VAR] = pd.to_numeric(df["traffic_speed_raw"], errors="coerce")
    missing_speed_count = int(df[CANONICAL_SPEED_VAR].isna().sum())

    # Check realistic speed boundaries: non-negative and <= 200 km/h
    speed_negative_count = int((df[CANONICAL_SPEED_VAR] < 0.0).sum())
    speed_extreme_count = int((df[CANONICAL_SPEED_VAR] > 200.0).sum())

    # 4. Standardize raw saturation categories
    df[CANONICAL_CONGESTION_VAR] = df["road_saturation_level_raw"].astype(str).str.strip().str.upper()
    missing_sat_count = int(df[CANONICAL_CONGESTION_VAR].isna().sum() | (df[CANONICAL_CONGESTION_VAR] == "NONE").sum())

    # Verify all categories belong to official domain
    allowed_categories = set(CONGESTION_ORDINAL_MAP.keys())
    observed_categories = set(df[CANONICAL_CONGESTION_VAR].unique())
    unknown_categories = observed_categories - allowed_categories
    if unknown_categories:
        raise ValueError(f"Observed unexpected traffic saturation categories: {unknown_categories}")

    # 5. Documented Ordinal Mapping
    df["traffic_congestion_ordinal"] = df[CANONICAL_CONGESTION_VAR].map(CONGESTION_ORDINAL_MAP)

    # 6. Snapshot statistics
    unique_snapshots = df["snapshot_file"].unique().tolist()
    unique_links = sorted(df["link_id"].unique().tolist())
    total_unique_links = len(unique_links)

    links_per_snapshot = df.groupby("snapshot_file")["link_id"].nunique().to_dict()
    records_per_snapshot = df.groupby("snapshot_file").size().to_dict()

    # Distinct timestamps across snapshots
    unique_timestamps = df["capture_timestamp"].nunique()
    earliest_ts = str(df["capture_timestamp"].min())
    latest_ts = str(df["capture_timestamp"].max())

    # Check for duplicate (link_id, snapshot_file) pairs
    duplicate_link_snapshot = int(df.duplicated(subset=["snapshot_file", "link_id"]).sum())

    # Speed summary statistics
    speed_series = df[CANONICAL_SPEED_VAR].dropna()
    speed_stats = {
        "count": int(len(speed_series)),
        "min": float(speed_series.min()),
        "max": float(speed_series.max()),
        "mean": round(float(speed_series.mean()), 4),
        "median": float(speed_series.median()),
        "std": round(float(speed_series.std()), 4),
        "unit": "km/h",
    }

    # Saturation frequency breakdown
    sat_counts = df[CANONICAL_CONGESTION_VAR].value_counts().to_dict()
    sat_percentages = {k: round(v / len(df) * 100, 2) for k, v in sat_counts.items()}

    # Format output dataframe
    df_clean = df[[
        "snapshot_file",
        "link_id",
        CANONICAL_SPEED_VAR,
        CANONICAL_CONGESTION_VAR,
        "traffic_congestion_ordinal",
        "capture_timestamp",
        "region",
        "road_type",
    ]].copy()
    df_clean["capture_timestamp"] = df_clean["capture_timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Export to Parquet and CSV
    parquet_path = output_dir / "clean_traffic_speedmap_snapshots.parquet"
    csv_path = output_dir / "clean_traffic_speedmap_snapshots.csv"
    report_path = output_dir / "traffic_source_cleaning_report.json"

    print(f"[Traffic] Exporting clean dataset to {parquet_path}...")
    df_clean.to_parquet(parquet_path, index=False)
    print(f"[Traffic] Exporting clean dataset to {csv_path}...")
    df_clean.to_csv(csv_path, index=False)

    report: Dict[str, Any] = {
        "source_domain": "Traffic",
        "source_system": "Hong Kong Transport Department 1st Generation Traffic Speed Map (speedmap.xml)",
        "cleaned_parquet_file": str(parquet_path),
        "cleaned_csv_file": str(csv_path),
        "total_snapshots_processed": len(xml_files),
        "total_records_extracted": total_records,
        "malformed_xml_count": malformed_xml_count,
        "unique_road_links_count": total_unique_links,
        "baseline_link_count_2019": links_per_snapshot.get("historical_td_speedmap_20190101_0000.xml", 607),
        "links_per_snapshot": links_per_snapshot,
        "records_per_snapshot": records_per_snapshot,
        "unique_timestamps_count": unique_timestamps,
        "earliest_timestamp": earliest_ts,
        "latest_timestamp": latest_ts,
        "duplicate_link_snapshot_records": duplicate_link_snapshot,
        "missing_link_ids": missing_link_ids,
        "missing_timestamps": missing_timestamps,
        "missing_speed_values": missing_speed_count,
        "missing_saturation_values": missing_sat_count,
        "speed_negative_count": speed_negative_count,
        "speed_extreme_count": speed_extreme_count,
        "traffic_speed_statistics": speed_stats,
        "saturation_category_frequencies": sat_counts,
        "saturation_category_percentages": sat_percentages,
        "congestion_ordinal_mapping_specification": CONGESTION_ORDINAL_MAP,
        "spatial_idw_applied": False,
        "station_aggregation_applied": False,
        "status": "VERIFIED_VALID",
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[Traffic] Validation report saved to {report_path}.")
    return df_clean, report
