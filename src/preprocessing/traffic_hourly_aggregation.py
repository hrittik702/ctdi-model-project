"""Phase 2.2: Temporal aggregation of Hong Kong Traffic SpeedMap archive to hourly link-level data.

Aggregates all 466,829,497 sub-hourly records across 774,686 snapshots into a standardized
hourly link-level representation covering 2019-01-01 00:00:00 through 2021-12-31 23:00:00.

Formulation:
1. traffic_speed_hourly: Arithmetic mean of valid sub-hourly traffic_speed observations.
2. traffic_congestion_hourly: Arithmetic mean of continuous ordinal representations:
   - TRAFFIC GOOD    = 0.0
   - TRAFFIC AVERAGE = 0.5
   - TRAFFIC BAD     = 1.0
3. Quality metadata:
   - observation_count: Number of sub-hourly observations in the hour.
   - coverage_pct: Nominal coverage percentage based on ~2-min sampling (30 expected).
   - is_sufficient_observations: True if >= 10 observations present in the hour.

Outputs:
- data/interim/aligned/traffic_hourly_link_data.parquet (consolidated dataset)
- data/interim/aligned/traffic_hourly_summary.json (summary audit report)
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERIM_TRAFFIC_MONTHLY_DIR = PROJECT_ROOT / "data" / "interim" / "traffic" / "monthly"
ALIGNED_DIR = PROJECT_ROOT / "data" / "interim" / "aligned"
OUTPUT_HOURLY_TRAFFIC_PATH = ALIGNED_DIR / "traffic_hourly_link_data.parquet"
OUTPUT_SUMMARY_JSON = ALIGNED_DIR / "traffic_hourly_summary.json"

STUDY_START = "2019-01-01 00:00:00"
STUDY_END = "2021-12-31 23:00:00"


def process_month(file_path: Path) -> pd.DataFrame:
    """Process a single monthly Parquet file and return aggregated link-hour rows."""
    df = pd.read_parquet(
        file_path,
        columns=["timestamp", "link_id", "traffic_speed", "traffic_congestion_ordinal"]
    )

    # Format hourly timestamp: 'YYYY-MM-DDTHH:MM:SS' -> 'YYYY-MM-DD HH:00:00'
    df["hourly_timestamp"] = df["timestamp"].str[:10] + " " + df["timestamp"].str[11:13] + ":00:00"

    # Filter strictly to the 2019-2021 study period
    df = df[(df["hourly_timestamp"] >= STUDY_START) & (df["hourly_timestamp"] <= STUDY_END)]
    if df.empty:
        return pd.DataFrame()

    # Aggregate by link_id and hourly_timestamp
    agg = df.groupby(["link_id", "hourly_timestamp"], observed=True).agg(
        traffic_speed_hourly=("traffic_speed", "mean"),
        traffic_congestion_hourly=("traffic_congestion_ordinal", "mean"),
        observation_count=("traffic_speed", "count")
    ).reset_index()

    agg["traffic_speed_hourly"] = agg["traffic_speed_hourly"].round(2).astype("float32")
    agg["traffic_congestion_hourly"] = agg["traffic_congestion_hourly"].round(4).astype("float32")
    agg["observation_count"] = agg["observation_count"].astype("int16")
    agg["coverage_pct"] = (agg["observation_count"] / 30.0 * 100.0).clip(upper=100.0).round(1).astype("float32")
    agg["is_sufficient_observations"] = agg["observation_count"] >= 10

    return agg


def aggregate_complete_traffic_hourly() -> Dict[str, Any]:
    """Execute complete hourly aggregation across all 36 monthly traffic partitions."""
    print("=" * 80)
    print("PHASE 2.2: TRAFFIC TEMPORAL AGGREGATION TO HOURLY LINK-LEVEL DATA")
    print("=" * 80)

    ALIGNED_DIR.mkdir(parents=True, exist_ok=True)

    monthly_files = sorted(list(INTERIM_TRAFFIC_MONTHLY_DIR.glob("traffic_speedmap_*.parquet")))
    if not monthly_files:
        raise FileNotFoundError(f"No monthly files found in {INTERIM_TRAFFIC_MONTHLY_DIR}")

    print(f"Discovered {len(monthly_files)} monthly partitions to aggregate.")
    t_start = time.time()

    all_monthly_aggs: List[pd.DataFrame] = []
    total_raw_records = 0

    for idx, mf in enumerate(monthly_files, 1):
        t0 = time.time()
        agg_m = process_month(mf)
        elapsed = time.time() - t0
        all_monthly_aggs.append(agg_m)
        print(f"[{idx:02d}/36] Processed {mf.name:<32} -> {len(agg_m):>7,} link-hours ({elapsed:.2f}s)")

    print(f"\nConcatenating {len(all_monthly_aggs)} monthly aggregations...")
    df_all_hourly = pd.concat(all_monthly_aggs, ignore_index=True)
    df_all_hourly["link_id"] = df_all_hourly["link_id"].astype(str)
    df_all_hourly = df_all_hourly.sort_values(["link_id", "hourly_timestamp"]).reset_index(drop=True)

    total_time = time.time() - t_start
    print(f"Aggregation completed in {total_time:.2f}s.")
    print(f"Total aggregated link-hour rows: {len(df_all_hourly):,}")
    print(f"Unique road links: {df_all_hourly['link_id'].nunique()}")
    print(f"Unique hourly timestamps: {df_all_hourly['hourly_timestamp'].nunique():,}")

    # Write consolidated Parquet
    print(f"Serializing to: {OUTPUT_HOURLY_TRAFFIC_PATH}...")
    df_all_hourly.to_parquet(
        OUTPUT_HOURLY_TRAFFIC_PATH,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )
    file_size_mb = OUTPUT_HOURLY_TRAFFIC_PATH.stat().st_size / (1024 * 1024)
    print(f"Saved {OUTPUT_HOURLY_TRAFFIC_PATH.name} ({file_size_mb:.2f} MB)")

    # Quality and coverage audit
    summary = {
        "report_title": "Traffic Temporal Hourly Aggregation Summary",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_partitions": len(monthly_files),
        "total_link_hour_rows": len(df_all_hourly),
        "unique_road_links": int(df_all_hourly["link_id"].nunique()),
        "unique_hourly_timestamps": int(df_all_hourly["hourly_timestamp"].nunique()),
        "speed_min_kmh": float(df_all_hourly["traffic_speed_hourly"].min()),
        "speed_max_kmh": float(df_all_hourly["traffic_speed_hourly"].max()),
        "speed_mean_kmh": float(round(df_all_hourly["traffic_speed_hourly"].mean(), 2)),
        "congestion_min": float(df_all_hourly["traffic_congestion_hourly"].min()),
        "congestion_max": float(df_all_hourly["traffic_congestion_hourly"].max()),
        "congestion_mean": float(round(df_all_hourly["traffic_congestion_hourly"].mean(), 4)),
        "mean_observations_per_link_hour": float(round(df_all_hourly["observation_count"].mean(), 1)),
        "sufficient_observation_link_hours_pct": float(
            round(df_all_hourly["is_sufficient_observations"].mean() * 100.0, 2)
        ),
        "file_size_mb": round(file_size_mb, 2),
        "execution_time_seconds": round(total_time, 2)
    }

    with open(OUTPUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved audit summary to: {OUTPUT_SUMMARY_JSON}")

    return summary


if __name__ == "__main__":
    aggregate_complete_traffic_hourly()
