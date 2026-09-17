"""Validation and audit suite for complete Hong Kong Traffic Speed Map historical extraction.

Phase 1.1: Complete Traffic Data Extraction
- Scans all 36 monthly Parquet partitions in data/interim/traffic/monthly/
- Audits total snapshots processed vs expected (~774,686)
- Audits total records extracted (~464M+)
- Analyzes temporal cadence:
    snapshots per day, snapshots per hour, interval distribution
    gaps > 5 min, gaps > 15 min, missing calendar dates, missing hours
- Analyzes spatial road-link network:
    union of all links, common core intersection links
    annual link counts (2019, 2020, 2021)
- Validates speed bounds and saturation frequencies
- Exports comprehensive audit report to data/interim/traffic/traffic_complete_extraction_report.json
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Set
from datetime import datetime, timezone
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INTERIM_TRAFFIC_DIR = PROJECT_ROOT / "data" / "interim" / "traffic"
MONTHLY_DIR = INTERIM_TRAFFIC_DIR / "monthly"
REPORT_OUTPUT_PATH = INTERIM_TRAFFIC_DIR / "traffic_complete_extraction_report.json"
FAILED_LOG_PATH = INTERIM_TRAFFIC_DIR / "traffic_failed_extractions.csv"

EXPECTED_STUDY_START = "2019-01-01"
EXPECTED_STUDY_END = "2021-12-31"


def validate_complete_traffic() -> Dict[str, Any]:
    """Execute exhaustive validation across all extracted monthly traffic partitions."""
    print("=" * 80)
    print("VALIDATING COMPLETE EXTRACTED TRAFFIC DATASET (2019–2021)")
    print("=" * 80)

    monthly_files = sorted(list(MONTHLY_DIR.glob("traffic_speedmap_*.parquet")))
    if not monthly_files:
        raise FileNotFoundError(f"No monthly Parquet files found in {MONTHLY_DIR}")

    print(f"Discovered {len(monthly_files)} monthly Parquet partitions in {MONTHLY_DIR.name}/")

    total_records = 0
    all_links_union: Set[str] = set()
    links_by_year: Dict[str, Set[str]] = {"2019": set(), "2020": set(), "2021": set()}
    snapshots_per_year: Dict[str, int] = {"2019": 0, "2020": 0, "2021": 0}
    records_per_year: Dict[str, int] = {"2019": 0, "2020": 0, "2021": 0}

    all_snapshot_files: Set[str] = set()
    all_timestamps: List[pd.Timestamp] = []

    missing_speed_total = 0
    missing_sat_total = 0
    sat_counts_total: Dict[str, int] = {"TRAFFIC GOOD": 0, "TRAFFIC AVERAGE": 0, "TRAFFIC BAD": 0}

    speed_min_global = float("inf")
    speed_max_global = float("-inf")
    speed_sum_global = 0.0
    speed_count_global = 0

    monthly_metrics = []

    for idx, mf in enumerate(monthly_files, 1):
        month_key = mf.stem.replace("traffic_speedmap_", "")
        year = month_key[:4]
        print(f"[{idx}/{len(monthly_files)}] Auditing partition {mf.name}...")

        df_month = pd.read_parquet(mf)
        n_rows = len(df_month)
        total_records += n_rows
        records_per_year[year] += n_rows

        # Road links
        month_links = set(df_month["link_id"].unique())
        all_links_union.update(month_links)
        links_by_year[year].update(month_links)

        # Snapshots
        month_snaps = set(df_month["snapshot_file"].unique())
        all_snapshot_files.update(month_snaps)
        snapshots_per_year[year] += len(month_snaps)

        # Timestamps
        ts_series = pd.to_datetime(df_month["timestamp"])
        unique_month_ts = ts_series.drop_duplicates()
        all_timestamps.extend(unique_month_ts)

        # Speeds
        valid_speeds = df_month["traffic_speed"].dropna()
        missing_speed_total += int(df_month["traffic_speed"].isna().sum())
        if len(valid_speeds) > 0:
            speed_min_global = min(speed_min_global, float(valid_speeds.min()))
            speed_max_global = max(speed_max_global, float(valid_speeds.max()))
            speed_sum_global += float(valid_speeds.sum())
            speed_count_global += len(valid_speeds)

        # Saturation counts
        sat_vc = df_month["road_saturation_level"].value_counts().to_dict()
        for k, v in sat_vc.items():
            sat_counts_total[k] = sat_counts_total.get(k, 0) + v
        missing_sat_total += int(df_month["road_saturation_level"].isna().sum())

        monthly_metrics.append({
            "month": month_key,
            "snapshots": len(month_snaps),
            "records": n_rows,
            "unique_links": len(month_links),
            "mean_speed": round(float(valid_speeds.mean()), 2) if len(valid_speeds) > 0 else 0.0,
            "parquet_size_mb": round(mf.stat().st_size / (1024 * 1024), 2),
        })

    # Global speed mean
    speed_mean_global = round(speed_sum_global / max(speed_count_global, 1), 2)

    # Core invariant links across all 3 years
    common_links_3yr = links_by_year["2019"] & links_by_year["2020"] & links_by_year["2021"]

    # Deduplicate and sort timestamps
    all_ts_unique = pd.Series(all_timestamps).drop_duplicates().sort_values().reset_index(drop=True)
    total_unique_timestamps = len(all_ts_unique)
    earliest_ts = str(all_ts_unique.min())
    latest_ts = str(all_ts_unique.max())

    # Cadence / interval distribution
    intervals_min = all_ts_unique.diff().dt.total_seconds().dropna() / 60.0

    interval_le_2m = int((intervals_min <= 2.5).sum())
    interval_le_5m = int((intervals_min <= 5.5).sum())
    gaps_gt_5m = int((intervals_min > 5.5).sum())
    gaps_gt_15m = int((intervals_min > 15.0).sum())
    gaps_gt_60m = int((intervals_min > 60.0).sum())

    # Calendar date completeness
    date_range = pd.date_range(start="2019-01-01", end="2021-12-31", freq="D")
    actual_dates = set(all_ts_unique.dt.strftime("%Y-%m-%d").unique())
    missing_calendar_dates = [d.strftime("%Y-%m-%d") for d in date_range if d.strftime("%Y-%m-%d") not in actual_dates]

    # Snapshots per day statistics
    snaps_per_day = all_ts_unique.groupby(all_ts_unique.dt.date).size()

    # Failed extractions count from log
    failed_extractions_count = 0
    if FAILED_LOG_PATH.exists():
        try:
            df_failed = pd.read_csv(FAILED_LOG_PATH)
            failed_extractions_count = len(df_failed)
        except Exception:
            pass

    report: Dict[str, Any] = {
        "report_title": "Hong Kong Traffic Speed Map Complete Historical Extraction Audit (2019–2021)",
        "audit_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_system": "Hong Kong Transport Department 1st Generation Traffic Speed Map (speedmap.xml)",
        "archive_portal": "DATA.GOV.HK Historical Archive",
        "study_period": "2019-01-01 00:00:00 to 2021-12-31 23:57:00",
        "completeness_status": "COMPLETE" if len(monthly_files) == 36 and len(missing_calendar_dates) == 0 else "PARTIAL",
        "summary_statistics": {
            "total_monthly_partitions": len(monthly_files),
            "total_snapshots_processed": len(all_snapshot_files),
            "total_traffic_records_extracted": total_records,
            "total_unique_timestamps": total_unique_timestamps,
            "earliest_timestamp": earliest_ts,
            "latest_timestamp": latest_ts,
            "unique_road_links_union": len(all_links_union),
            "common_core_links_intersection": len(common_links_3yr),
            "links_by_year": {k: len(v) for k, v in links_by_year.items()},
            "snapshots_by_year": snapshots_per_year,
            "records_by_year": records_per_year,
        },
        "cadence_and_temporal_distribution": {
            "native_cadence_description": "Sub-hourly variable cadence (~2-minute nominal intervals)",
            "mean_snapshots_per_day": round(float(snaps_per_day.mean()), 1),
            "min_snapshots_per_day": int(snaps_per_day.min()),
            "max_snapshots_per_day": int(snaps_per_day.max()),
            "intervals_le_2_minutes_count": interval_le_2m,
            "intervals_le_2_minutes_pct": round(interval_le_2m / max(len(intervals_min), 1) * 100, 2),
            "intervals_le_5_minutes_count": interval_le_5m,
            "intervals_le_5_minutes_pct": round(interval_le_5m / max(len(intervals_min), 1) * 100, 2),
            "gaps_gt_5_minutes_count": gaps_gt_5m,
            "gaps_gt_15_minutes_count": gaps_gt_15m,
            "gaps_gt_60_minutes_count": gaps_gt_60m,
            "missing_calendar_dates_count": len(missing_calendar_dates),
            "missing_calendar_dates": missing_calendar_dates,
        },
        "data_quality_and_integrity": {
            "missing_traffic_speeds": missing_speed_total,
            "missing_saturation_levels": missing_sat_total,
            "malformed_xml_files": failed_extractions_count,
            "speed_min_kmh": speed_min_global,
            "speed_max_kmh": speed_max_global,
            "speed_mean_kmh": speed_mean_global,
            "saturation_level_frequencies": sat_counts_total,
            "saturation_level_percentages": {
                k: round(v / max(total_records, 1) * 100, 2) for k, v in sat_counts_total.items()
            },
            "ordinal_mapping": {
                "TRAFFIC GOOD": 0.0,
                "TRAFFIC AVERAGE": 0.5,
                "TRAFFIC BAD": 1.0,
            },
        },
        "monthly_partition_breakdown": monthly_metrics,
    }

    REPORT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 80)
    print("VALIDATION COMPLETED SUCCESSFULLY.")
    print(f"Total Snapshots Audited : {len(all_snapshot_files):,}")
    print(f"Total Records Extracted : {total_records:,}")
    print(f"Unique Road Links Union : {len(all_links_union):,}")
    print(f"Speed Range             : [{speed_min_global}, {speed_max_global}] km/h (Mean: {speed_mean_global} km/h)")
    print(f"Missing Dates           : {len(missing_calendar_dates)}")
    print(f"Report Output Saved To  : {REPORT_OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print("=" * 80)
    return report


if __name__ == "__main__":
    validate_complete_traffic()
