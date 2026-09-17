"""Data provenance and cryptographic manifest generator for Phase 1.

Compiles complete provenance records for:
1. Clean Air Quality (EPD)
2. Clean Meteorology (ERA5 Surface Reanalysis)
3. Clean Traffic Speed Map (TD 1st Gen Speedmap)

Tracks the formal provenance chain:
    ORIGINAL RAW -> SOURCE-SPECIFIC CLEAN -> FUTURE ALIGNMENT -> FUTURE FINAL DATASET
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


def calculate_sha256(file_path: Path) -> str:
    """Compute SHA-256 cryptographic checksum of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def build_raw_manifest(raw_dir: Path, output_json: Path) -> Dict[str, Any]:
    """Compute exhaustive SHA-256 manifest of all files in raw directory."""
    raw_files = sorted([p for p in raw_dir.glob("**/*") if p.is_file()])
    manifest = {}
    for p in raw_files:
        rel_path = str(p.relative_to(raw_dir))
        manifest[rel_path] = {
            "sha256": calculate_sha256(p),
            "size_bytes": p.stat().st_size,
        }
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return manifest


def build_provenance_metadata(
    project_root: Path,
    output_json: Path,
) -> Dict[str, Any]:
    """Generate master provenance metadata record for Phase 1 prepared outputs."""
    output_json.parent.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).isoformat()

    provenance = {
        "metadata_version": "1.0",
        "phase": "PHASE 1 — SOURCE-SPECIFIC DATA CLEANING & STANDARDIZATION",
        "generation_timestamp_utc": now_iso,
        "provenance_chain_stage": "ORIGINAL RAW -> SOURCE-SPECIFIC CLEAN",
        "future_stages": ["FUTURE ALIGNMENT", "FUTURE FINAL DATASET"],
        "records": [
            {
                "domain": "Air Quality",
                "source_file": "data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv",
                "source_organization": "Environmental Protection Department, The Government of the Hong Kong SAR (HKEPD)",
                "source_url": "https://cd.epic.epd.gov.hk/EPICDI/air/station/",
                "original_columns": [
                    "station_id", "station_name", "timestamp", "pm25", "pm10", "no2", "o3", "so2", "nox", "co"
                ],
                "standardized_columns": [
                    "station_id", "station_name", "timestamp", "pm25", "pm10", "no2", "so2", "o3"
                ],
                "original_units": {
                    "pm25": "µg/m³", "pm10": "µg/m³", "no2": "µg/m³", "so2": "µg/m³", "o3": "µg/m³"
                },
                "standardized_units": {
                    "pm25": "µg/m³", "pm10": "µg/m³", "no2": "µg/m³", "so2": "µg/m³", "o3": "µg/m³"
                },
                "transformation_applied": [
                    "Header standardization to snake_case",
                    "ISO datetime parsing (Asia/Hong_Kong)",
                    "Chronological sorting by (timestamp, station_id)",
                    "Station identifier casting to integer and uppercase string",
                    "Strict preservation of natural IEEE 754 NaNs without imputation",
                    "Dual serialization to clean Parquet and CSV"
                ],
                "transformation_reason": (
                    "Ensure structural 16-station × 26,304-hour Cartesian grid integrity, "
                    "prevent silent data corruption, and preserve authentic empirical missingness "
                    "patterns for conditional generative modeling."
                ),
                "row_count_before": 420864,
                "row_count_after": 420864,
                "missing_values_before": {
                    "pm25": 10657, "pm10": 11395, "no2": 11651, "o3": 11117, "so2": 11056, "total": 55876
                },
                "missing_values_after": {
                    "pm25": 10657, "pm10": 11395, "no2": 11651, "o3": 11117, "so2": 11056, "total": 55876
                },
                "processing_date": now_iso[:10],
                "script_or_notebook_used": "src/preprocessing/clean_air_quality.py / notebooks/02_source_specific_cleaning.ipynb",
                "output_files": [
                    "data/interim/air_quality/clean_air_quality.parquet",
                    "data/interim/air_quality/clean_air_quality.csv",
                    "data/interim/air_quality/air_quality_validation.json"
                ]
            },
            {
                "domain": "Meteorology",
                "source_file": "data/raw/meteorology/hourly_meteorology_16stations_2019_2021.csv",
                "source_organization": "European Centre for Medium-Range Weather Forecasts (ECMWF) ERA5 / Open-Meteo API",
                "source_url": "https://archive-api.open-meteo.com/v1/archive",
                "original_columns": [
                    "station_id", "station_name", "timestamp", "temperature", "relative_humidity",
                    "wind_speed", "wind_direction", "pressure", "rainfall"
                ],
                "standardized_columns": [
                    "station_id", "station_name", "timestamp", "temperature", "relative_humidity",
                    "pressure", "rainfall", "wind_direction", "wind_speed"
                ],
                "original_units": {
                    "temperature": "°C", "relative_humidity": "%", "pressure": "hPa",
                    "rainfall": "mm", "wind_direction": "degrees", "wind_speed": "m/s"
                },
                "standardized_units": {
                    "temperature": "°C", "relative_humidity": "%", "pressure": "hPa",
                    "rainfall": "mm", "wind_direction": "degrees", "wind_speed": "m/s"
                },
                "transformation_applied": [
                    "Canonical snake_case column alignment",
                    "ISO datetime parsing (Asia/Hong_Kong)",
                    "Chronological sorting by (timestamp, station_id)",
                    "Station identifier casting to integer and uppercase string",
                    "Physical boundary verification (non-negative rainfall, 0-100% RH, 0-360° WD)",
                    "Preservation of rainfall as rainfall (never renamed to visibility)",
                    "Preservation of native wind speed (m/s) with documented conversion factor (3.6) for km/h",
                    "Dual serialization to clean Parquet and CSV"
                ],
                "transformation_reason": (
                    "Provide physically grounded, continuous meteorological features at the exact 16 monitoring "
                    "station coordinates; uphold scientific truth regarding the visibility-rainfall substitution."
                ),
                "row_count_before": 420864,
                "row_count_after": 420864,
                "missing_values_before": {
                    "temperature": 0, "relative_humidity": 0, "pressure": 0,
                    "rainfall": 0, "wind_direction": 0, "wind_speed": 0, "total": 0
                },
                "missing_values_after": {
                    "temperature": 0, "relative_humidity": 0, "pressure": 0,
                    "rainfall": 0, "wind_direction": 0, "wind_speed": 0, "total": 0
                },
                "processing_date": now_iso[:10],
                "script_or_notebook_used": "src/preprocessing/clean_meteorology.py / notebooks/02_source_specific_cleaning.ipynb",
                "output_files": [
                    "data/interim/meteorology/clean_meteorology.parquet",
                    "data/interim/meteorology/clean_meteorology.csv",
                    "data/interim/meteorology/meteorology_validation.json"
                ]
            },
            {
                "domain": "Traffic",
                "source_file": "data/raw/traffic/samples/historical_td_speedmap_*.xml",
                "source_organization": "Transport Department, The Government of the Hong Kong SAR (HKTD)",
                "source_url": "http://resource.data.one.gov.hk/td/speedmap.xml (Archived on DATA.GOV.HK)",
                "original_columns": [
                    "LINK_ID", "REGION", "ROAD_TYPE", "ROAD_SATURATION_LEVEL", "TRAFFIC_SPEED", "CAPTURE_DATE"
                ],
                "standardized_columns": [
                    "snapshot_file", "link_id", "traffic_speed", "traffic_congestion",
                    "traffic_congestion_ordinal", "capture_timestamp", "region", "road_type"
                ],
                "original_units": {
                    "TRAFFIC_SPEED": "km/h", "ROAD_SATURATION_LEVEL": "categorical string"
                },
                "standardized_units": {
                    "traffic_speed": "km/h",
                    "traffic_congestion": "categorical string",
                    "traffic_congestion_ordinal": "ordinal float [0.0, 1.0]"
                },
                "transformation_applied": [
                    "Safe XML streaming parsing using ElementTree with namespace resolution",
                    "Link ID preservation as discrete string identifiers",
                    "ISO datetime parsing for snapshot capture timestamps",
                    "Numeric speed parsing and boundary validation ([3, 109] km/h)",
                    "Raw categorical saturation preservation (TRAFFIC GOOD, TRAFFIC AVERAGE, TRAFFIC BAD)",
                    "Formal ordinal mapping definition (GOOD=0.0, AVERAGE=0.5, BAD=1.0) into explicit column",
                    "Zero spatial IDW or station aggregation applied in this source-specific phase",
                    "Dual serialization to clean Parquet and CSV"
                ],
                "transformation_reason": (
                    "Standardize sub-hourly traffic snapshots into validated link-level tables while preserving "
                    "exact raw link geometries and categorical states before multi-modal spatial projection."
                ),
                "row_count_before": 2413,
                "row_count_after": 2413,
                "missing_values_before": {
                    "traffic_speed": 0, "road_saturation_level": 0, "link_id": 0
                },
                "missing_values_after": {
                    "traffic_speed": 0, "traffic_congestion": 0, "link_id": 0
                },
                "processing_date": now_iso[:10],
                "script_or_notebook_used": "src/preprocessing/clean_traffic.py / notebooks/02_source_specific_cleaning.ipynb",
                "output_files": [
                    "data/interim/traffic/clean_traffic_speedmap_snapshots.parquet",
                    "data/interim/traffic/clean_traffic_speedmap_snapshots.csv",
                    "data/interim/traffic/traffic_source_cleaning_report.json"
                ]
            },
            {
                "domain": "Traffic (Complete 3-Year Historical Archive)",
                "source_file": "DATA.GOV.HK Historical Archive (36 monthly zip archives, 201901–202112)",
                "source_organization": "Transport Department, The Government of the Hong Kong SAR (HKTD)",
                "source_url": "https://app.data.gov.hk/v1/historical-archive/get-file?url=http%3A%2F%2Fresource.data.one.gov.hk%2Ftd%2Fspeedmap.xml&time=YYYYMM01",
                "original_columns": [
                    "LINK_ID", "REGION", "ROAD_TYPE", "ROAD_SATURATION_LEVEL", "TRAFFIC_SPEED", "CAPTURE_DATE"
                ],
                "standardized_columns": [
                    "timestamp", "link_id", "traffic_speed", "traffic_congestion", "region", "road_type"
                ],
                "original_units": {
                    "TRAFFIC_SPEED": "km/h", "ROAD_SATURATION_LEVEL": "categorical string"
                },
                "standardized_units": {
                    "traffic_speed": "km/h",
                    "traffic_congestion": "categorical string (GOOD, AVERAGE, BAD)"
                },
                "transformation_applied": [
                    "Parallel monthly stream extraction from DATA.GOV.HK historical archives",
                    "Streaming ElementTree XML parsing of 774,686 snapshot files",
                    "Fast regex/lxml timestamp parsing with Asia/Hong_Kong timezone alignment",
                    "Numeric speed parsing and physical validation ([0, 111] km/h)",
                    "Saturation category cleaning and normalization",
                    "Link ID string standardization (632 unique links in union, 590 common core)",
                    "Monthly partition serialization to Snappy-compressed Parquet (36 files)",
                    "Unified dataset symlink creation without spatial IDW or temporal aggregation"
                ],
                "transformation_reason": (
                    "Extract the complete 3-year historical traffic archive into standardized link-level "
                    "monthly partitions to serve as the ground truth input for Phase 2 spatial IDW interpolation."
                ),
                "total_snapshots_processed": 774686,
                "row_count_before": 466829497,
                "row_count_after": 466829497,
                "missing_values_before": {
                    "traffic_speed": 0, "traffic_congestion": 0, "link_id": 0
                },
                "missing_values_after": {
                    "traffic_speed": 0, "traffic_congestion": 0, "link_id": 0
                },
                "processing_date": now_iso[:10],
                "script_or_notebook_used": "src/preprocessing/extract_complete_traffic.py / src/preprocessing/validate_complete_traffic.py",
                "output_files": [
                    "data/interim/traffic/clean_traffic_speedmap_complete.parquet",
                    "data/interim/traffic/monthly/traffic_speedmap_YYYYMM.parquet",
                    "data/interim/traffic/traffic_complete_extraction_report.json",
                    "data/interim/traffic/traffic_failed_extractions.csv"
                ]
            }
        ]
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2)

    return provenance
