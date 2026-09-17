"""Source-specific cleaning and validation module for Hong Kong EPD air quality data.

Phase 1: Source-Specific Data Cleaning & Standardization
- Loads raw EPD hourly air quality data (2019-2021)
- Standardizes columns to canonical snake_case
- Validates 16 stations and 26,304 hourly timestamps (420,864 Cartesian grid records)
- Enforces strict chronological ordering and station identifier consistency
- Preserves native units (µg/m³) and legitimate natural missing values (NaNs)
- Strictly forbids interpolation, forward-filling, or mean-imputation
- Exports clean interim dataset and validation report
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

# Canonical pollutant columns and target units
CANONICAL_POLLUTANTS = ["pm25", "pm10", "no2", "so2", "o3"]
POLLUTANT_UNITS = {
    "pm25": "µg/m³",
    "pm10": "µg/m³",
    "no2": "µg/m³",
    "so2": "µg/m³",
    "o3": "µg/m³",
}

EXPECTED_STATIONS = 16
EXPECTED_TIMESTAMPS = 26304
EXPECTED_TOTAL_ROWS = EXPECTED_STATIONS * EXPECTED_TIMESTAMPS  # 420,864

# Audit reference counts from published CTDI paper / verified dataset
AUDIT_REFERENCE_MISSING = {
    "pm25": 10657,
    "pm10": 11395,
    "no2": 11651,
    "o3": 11117,
    "so2": 11056,
}
AUDIT_REFERENCE_TOTAL_MISSING = 55876


def clean_air_quality(
    raw_csv_path: Path,
    output_dir: Path,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean and validate raw Hong Kong EPD air quality dataset.

    Args:
        raw_csv_path: Path to raw air quality CSV.
        output_dir: Directory where interim outputs will be saved.

    Returns:
        Tuple of (clean_dataframe, validation_report_dict).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Air Quality] Loading raw data from {raw_csv_path}...")
    df_raw = pd.read_csv(raw_csv_path)
    initial_row_count = len(df_raw)

    # 1. Standardize column names to snake_case
    col_mapping = {c: c.strip().lower().replace("/", "_").replace(" ", "_") for c in df_raw.columns}
    df = df_raw.rename(columns=col_mapping)

    # Validate required canonical columns exist
    required_cols = ["station_id", "station_name", "timestamp"] + CANONICAL_POLLUTANTS
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' missing from air quality dataset.")

    # 2. Parse datetime with explicit timezone convention (Asia/Hong_Kong, UTC+8)
    # The timestamps represent standard HKT hourly timestamps (2019-01-01 00:00:00 to 2021-12-31 23:00:00)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    invalid_dates_count = df["timestamp"].isna().sum()

    # 3. Standardize station identifiers and names
    df["station_id"] = df["station_id"].astype(int)
    df["station_name"] = df["station_name"].astype(str).str.strip().str.upper()

    # 4. Chronological and station ordering
    df = df.sort_values(by=["timestamp", "station_id"]).reset_index(drop=True)

    # 5. Check duplicate station + timestamp records
    duplicate_count = int(df.duplicated(subset=["station_id", "timestamp"]).sum())
    if duplicate_count > 0:
        raise ValueError(f"Found {duplicate_count} duplicate (station_id, timestamp) records!")

    # 6. Verify grid structure
    unique_stations = sorted(df["station_id"].unique().tolist())
    station_count = len(unique_stations)
    unique_timestamps = df["timestamp"].nunique()
    min_ts = str(df["timestamp"].min())
    max_ts = str(df["timestamp"].max())

    if station_count != EXPECTED_STATIONS:
        raise ValueError(f"Expected {EXPECTED_STATIONS} stations, found {station_count}")
    if unique_timestamps != EXPECTED_TIMESTAMPS:
        raise ValueError(f"Expected {EXPECTED_TIMESTAMPS} timestamps, found {unique_timestamps}")
    if len(df) != EXPECTED_TOTAL_ROWS:
        raise ValueError(f"Expected {EXPECTED_TOTAL_ROWS} total rows, found {len(df)}")

    # 7. Check for negative or impossible numeric values
    negative_counts = {}
    for pol in CANONICAL_POLLUTANTS:
        neg_mask = df[pol] < 0.0
        neg_count = int(neg_mask.sum())
        negative_counts[pol] = neg_count
        if neg_count > 0:
            raise ValueError(f"Found {neg_count} negative values in {pol}!")

    # 8. Missingness audit (preserve natural NaNs strictly without imputation)
    missing_counts = {}
    missing_percentages = {}
    summary_stats = {}
    for pol in CANONICAL_POLLUTANTS:
        n_missing = int(df[pol].isna().sum())
        missing_counts[pol] = n_missing
        missing_percentages[pol] = round(float(n_missing / len(df) * 100), 4)
        series_valid = df[pol].dropna()
        summary_stats[pol] = {
            "count_valid": int(len(series_valid)),
            "count_missing": n_missing,
            "min": float(series_valid.min()),
            "max": float(series_valid.max()),
            "mean": round(float(series_valid.mean()), 4),
            "median": float(series_valid.median()),
            "std": round(float(series_valid.std()), 4),
            "unit": POLLUTANT_UNITS[pol],
        }

    total_pollutant_missing = sum(missing_counts.values())

    # Check match against reference audit
    audit_comparison = {
        "calculated_missing": missing_counts,
        "reference_missing": AUDIT_REFERENCE_MISSING,
        "calculated_total_missing": total_pollutant_missing,
        "reference_total_missing": AUDIT_REFERENCE_TOTAL_MISSING,
        "matches_reference_exactly": (missing_counts == AUDIT_REFERENCE_MISSING),
    }

    # Format output columns: keep canonical columns, format timestamp to ISO string
    df_clean = df[["station_id", "station_name", "timestamp"] + CANONICAL_POLLUTANTS].copy()
    df_clean["timestamp"] = df_clean["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Export to Parquet and CSV
    parquet_path = output_dir / "clean_air_quality.parquet"
    csv_path = output_dir / "clean_air_quality.csv"
    report_path = output_dir / "air_quality_validation.json"

    print(f"[Air Quality] Exporting clean dataset to {parquet_path}...")
    df_clean.to_parquet(parquet_path, index=False)
    print(f"[Air Quality] Exporting clean dataset to {csv_path}...")
    df_clean.to_csv(csv_path, index=False)

    report: Dict[str, Any] = {
        "source_domain": "Air Quality",
        "raw_source_file": str(raw_csv_path),
        "cleaned_parquet_file": str(parquet_path),
        "cleaned_csv_file": str(csv_path),
        "initial_rows": initial_row_count,
        "cleaned_rows": len(df_clean),
        "stations_count": station_count,
        "station_ids": unique_stations,
        "timestamps_count": unique_timestamps,
        "min_timestamp": min_ts,
        "max_timestamp": max_ts,
        "duplicates_detected": duplicate_count,
        "invalid_dates_detected": int(invalid_dates_count),
        "negative_values_detected": negative_counts,
        "missing_counts_per_pollutant": missing_counts,
        "missing_percentages_per_pollutant": missing_percentages,
        "total_criteria_pollutant_missing": total_pollutant_missing,
        "audit_comparison": audit_comparison,
        "pollutant_summary_statistics": summary_stats,
        "imputation_applied": False,
        "unit_conversions_applied": None,
        "canonical_units": POLLUTANT_UNITS,
        "status": "VERIFIED_VALID",
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[Air Quality] Validation report saved to {report_path}.")
    return df_clean, report
