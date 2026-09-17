"""Phase 2.4 & 2.5: Multimodal Station-Level Fusion & 13-Channel Dataset Construction.

Merges aligned air quality, meteorology, and spatial traffic data into the
canonical 13-channel representation across 16 stations and 26,304 hours (420,864 station-hours).
Strictly preserves natural pollutant missingness and ensures immutability of raw data.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Input paths
ALIGNED_AIR_MET_PATH = PROJECT_ROOT / "data" / "interim" / "aligned" / "aligned_air_met_hourly.parquet"
TRAFFIC_STATION_PATH = PROJECT_ROOT / "data" / "interim" / "aligned" / "traffic_station_hourly.parquet"
STATION_META_PATH = PROJECT_ROOT / "data" / "raw" / "station_metadata" / "air_quality_stations.csv"

# Output paths
OUT_DIR = PROJECT_ROOT / "data" / "interim" / "aligned"
OUT_DATASET_PATH = OUT_DIR / "aligned_hourly_station_data.parquet"
OUT_SUMMARY_PATH = OUT_DIR / "aligned_dataset_summary.json"
OUT_DIST_MATRIX_PATH = OUT_DIR / "spatial_distance_matrix.npy"
OUT_DIST_LEGACY_PATH = PROJECT_ROOT / "data" / "interim" / "spatial_distance_matrix.npy"

# Canonical 13-channel specification matching CTDI Table I (Yu et al. 2025)
# with rainfall explicitly substituting unrecovered historical visibility.
CANONICAL_13_CHANNELS = [
    "pm25",
    "pm10",
    "no2",
    "so2",
    "o3",
    "pressure",
    "relative_humidity",
    "temperature",
    "rainfall",
    "wind_direction",
    "wind_speed",
    "traffic_speed",
    "traffic_congestion",
]

TARGET_STATION_COUNT = 16
TARGET_HOURS = 26304
TARGET_TOTAL_ROWS = TARGET_STATION_COUNT * TARGET_HOURS  # 420,864

# Verified natural air quality missingness counts from Phase 1
EXPECTED_AQ_NANS = {
    "pm25": 10657,
    "pm10": 11395,
    "no2": 11651,
    "so2": 11056,
    "o3": 11117,
}
TOTAL_EXPECTED_AQ_NANS = sum(EXPECTED_AQ_NANS.values())  # 55,876


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two coordinates in kilometers."""
    radius = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0) ** 2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return float(radius * c)


def compute_station_distance_matrix(df_meta: pd.DataFrame) -> np.ndarray:
    """Compute 16x16 pairwise station distance matrix sorted by station_id."""
    df_sorted = df_meta.sort_values("station_id").reset_index(drop=True)
    n = len(df_sorted)
    dist = np.zeros((n, n), dtype=np.float32)
    lats = df_sorted["latitude"].values
    lons = df_sorted["longitude"].values

    for i in range(n):
        for j in range(n):
            if i != j:
                dist[i, j] = haversine_distance_km(lats[i], lons[i], lats[j], lons[j])

    assert dist.shape == (16, 16), f"Expected (16, 16) distance matrix, got {dist.shape}"
    assert np.allclose(np.diag(dist), 0.0), "Distance matrix diagonal must be 0"
    assert np.allclose(dist, dist.T), "Distance matrix must be symmetric"
    return dist


def build_aligned_dataset():
    """Execute Phase 2.4 and 2.5 fusion and validation."""
    print("=" * 70)
    print("PHASE 2.4 & 2.5: MULTIMODAL STATION-LEVEL FUSION (13 CHANNELS)")
    print("=" * 70)

    # 1. Load Aligned Air Quality + Meteorology
    print(f"\n[1/6] Loading aligned air quality + meteorology from: {ALIGNED_AIR_MET_PATH}")
    df_air_met = pd.read_parquet(ALIGNED_AIR_MET_PATH)
    print(f"      Loaded {len(df_air_met):,} rows, {len(df_air_met.columns)} columns.")
    assert len(df_air_met) == TARGET_TOTAL_ROWS, f"Expected {TARGET_TOTAL_ROWS} rows, got {len(df_air_met)}"

    # 2. Load Traffic Station Hourly
    print(f"\n[2/6] Loading station-level traffic from: {TRAFFIC_STATION_PATH}")
    df_traffic = pd.read_parquet(TRAFFIC_STATION_PATH)
    print(f"      Loaded {len(df_traffic):,} rows, {len(df_traffic.columns)} columns.")

    # 3. Load Station Metadata
    print(f"\n[3/6] Loading station metadata from: {STATION_META_PATH}")
    df_meta = pd.read_csv(STATION_META_PATH)
    target_meta = df_meta[df_meta["in_ctdi_study"].astype(str).str.strip().str.lower() == "true"].copy()
    assert len(target_meta) == TARGET_STATION_COUNT, f"Expected {TARGET_STATION_COUNT} stations, got {len(target_meta)}"

    # Compute pairwise station distance matrix
    dist_matrix = compute_station_distance_matrix(target_meta)
    print(f"      Computed 16x16 pairwise station distance matrix.")
    print(f"      Mean distance: {dist_matrix[dist_matrix > 0].mean():.2f} km, Max: {dist_matrix.max():.2f} km.")

    # 4. Perform Left Join
    print(f"\n[4/6] Performing multimodal station-hour left join on (station_id, timestamp)...")
    traffic_renamed = df_traffic.rename(columns={
        "traffic_speed_station_hourly": "traffic_speed",
        "traffic_congestion_station_hourly": "traffic_congestion",
        "contributing_links_count": "traffic_contributing_links",
        "nearest_link_distance_km": "traffic_nearest_link_dist_km",
        "spatial_confidence_flag": "traffic_spatial_confidence",
    })

    merged = pd.merge(
        df_air_met,
        traffic_renamed,
        on=["station_id", "timestamp"],
        how="left",
    )

    # Sort strictly by station_id, timestamp
    merged = merged.sort_values(["station_id", "timestamp"]).reset_index(drop=True)

    print(f"      Merged rows: {len(merged):,} (exact primary grid preservation)")
    assert len(merged) == TARGET_TOTAL_ROWS, f"Join altered row count! Expected {TARGET_TOTAL_ROWS}, got {len(merged)}"

    # 5. Column Schema & 13-Channel Verification
    metadata_cols = ["station_id", "station_name", "timestamp"]
    auxiliary_cols = [
        "traffic_contributing_links",
        "traffic_nearest_link_dist_km",
        "traffic_spatial_confidence",
    ]

    all_cols = metadata_cols + CANONICAL_13_CHANNELS + auxiliary_cols
    final_df = merged[all_cols].copy()

    print(f"\n[5/6] Verifying schema and tensor integrity...")
    print(f"      Total columns: {len(final_df.columns)}")
    print(f"      Canonical 13 channels in order: {CANONICAL_13_CHANNELS}")

    # Assert natural AQ missingness
    total_aq_nans = 0
    for col, expected_nans in EXPECTED_AQ_NANS.items():
        actual_nans = int(final_df[col].isna().sum())
        assert actual_nans == expected_nans, (
            f"Pollutant {col} NaN mismatch! Expected {expected_nans}, got {actual_nans}"
        )
        total_aq_nans += actual_nans
    assert total_aq_nans == TOTAL_EXPECTED_AQ_NANS, (
        f"Total AQ NaNs mismatch! Expected {TOTAL_EXPECTED_AQ_NANS}, got {total_aq_nans}"
    )
    print(f"      [VERIFIED] Natural AQ missingness preserved: exactly {total_aq_nans:,} NaNs.")

    # Assert meteorology completeness
    met_cols = [
        "pressure",
        "relative_humidity",
        "temperature",
        "rainfall",
        "wind_direction",
        "wind_speed",
    ]
    for col in met_cols:
        met_nans = int(final_df[col].isna().sum())
        assert met_nans == 0, f"Meteorology channel {col} has unexpected NaNs: {met_nans}"
    assert (final_df["rainfall"] >= 0.0).all(), "Rainfall contains negative values"
    print(f"      [VERIFIED] Meteorology completeness: 0 missing values across all 6 channels.")

    # Assert traffic missingness and characteristics
    # Note: 151 hours had no traffic snapshot files in 2019-2021 raw archive.
    # Across 16 stations, this yields 16 * 151 = 2,416 missing station-hours.
    traffic_speed_nans = int(final_df["traffic_speed"].isna().sum())
    traffic_cong_nans = int(final_df["traffic_congestion"].isna().sum())
    expected_traffic_nans = TARGET_TOTAL_ROWS - len(df_traffic)
    assert traffic_speed_nans == expected_traffic_nans, (
        f"Expected {expected_traffic_nans} traffic NaNs, got {traffic_speed_nans}"
    )
    assert traffic_cong_nans == expected_traffic_nans, (
        f"Expected {expected_traffic_nans} congestion NaNs, got {traffic_cong_nans}"
    )

    # Valid observed traffic statistics
    valid_speed = final_df["traffic_speed"].dropna()
    valid_cong = final_df["traffic_congestion"].dropna()
    print(f"      [VERIFIED] Traffic coverage: {len(valid_speed):,} valid station-hours ({len(valid_speed)/len(final_df)*100:.2f}%), {traffic_speed_nans:,} natural missing hours.")
    print(f"      Traffic speed range: [{valid_speed.min():.2f}, {valid_speed.max():.2f}] km/h, mean: {valid_speed.mean():.2f} km/h")
    print(f"      Traffic congestion range: [{valid_cong.min():.4f}, {valid_cong.max():.4f}], mean: {valid_cong.mean():.4f}")

    # Assert tensor shape and reshapeability
    feature_matrix = final_df[CANONICAL_13_CHANNELS].to_numpy(dtype=np.float32)
    assert feature_matrix.shape == (TARGET_TOTAL_ROWS, 13), (
        f"Feature matrix shape mismatch: {feature_matrix.shape}"
    )
    tensor_3d = feature_matrix.reshape(TARGET_STATION_COUNT, TARGET_HOURS, 13)
    assert tensor_3d.shape == (16, 26304, 13), f"3D Tensor reshape failed: {tensor_3d.shape}"
    print(f"      [VERIFIED] Feature tensor shape: (420864, 13) -> reshapeable to (16, 26304, 13).")

    # 6. Save Outputs
    print(f"\n[6/6] Saving outputs...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save aligned dataset
    final_df.to_parquet(OUT_DATASET_PATH, engine="pyarrow", compression="snappy", index=False)
    file_size_mb = OUT_DATASET_PATH.stat().st_size / (1024 * 1024)
    print(f"      Saved aligned dataset: {OUT_DATASET_PATH} ({file_size_mb:.2f} MB)")

    # Save distance matrix
    np.save(OUT_DIST_MATRIX_PATH, dist_matrix)
    np.save(OUT_DIST_LEGACY_PATH, dist_matrix)
    print(f"      Saved distance matrices: {OUT_DIST_MATRIX_PATH} and {OUT_DIST_LEGACY_PATH}")

    # Build summary
    station_stats = {}
    for st_id, st_group in final_df.groupby("station_id"):
        st_name = st_group["station_name"].iloc[0]
        station_stats[int(st_id)] = {
            "station_name": st_name,
            "total_hours": len(st_group),
            "aq_nans_by_channel": {col: int(st_group[col].isna().sum()) for col in EXPECTED_AQ_NANS},
            "traffic_valid_hours": int(st_group["traffic_speed"].notna().sum()),
            "traffic_speed_mean": float(st_group["traffic_speed"].mean()),
            "traffic_congestion_mean": float(st_group["traffic_congestion"].mean()),
            "traffic_nearest_link_dist_km": float(st_group["traffic_nearest_link_dist_km"].iloc[0]),
            "traffic_spatial_confidence": str(st_group["traffic_spatial_confidence"].iloc[0]),
        }

    summary = {
        "status": "COMPLETE",
        "phase": "2.4_2.5_multimodal_fusion",
        "grid": {
            "total_rows": TARGET_TOTAL_ROWS,
            "unique_stations": TARGET_STATION_COUNT,
            "unique_hours": TARGET_HOURS,
            "temporal_range": ["2019-01-01 00:00:00", "2021-12-31 23:00:00"],
            "canonical_13_channels": CANONICAL_13_CHANNELS,
            "tensor_shape": [TARGET_TOTAL_ROWS, 13],
            "tensor_3d_shape": [TARGET_STATION_COUNT, TARGET_HOURS, 13],
        },
        "pollutant_natural_missingness": {
            "total_nans": total_aq_nans,
            "breakdown": EXPECTED_AQ_NANS,
        },
        "meteorology_completeness": {
            "missing_values": 0,
            "channels": met_cols,
        },
        "traffic_coverage": {
            "valid_station_hours": len(valid_speed),
            "missing_station_hours": traffic_speed_nans,
            "coverage_percentage": len(valid_speed) / len(final_df) * 100.0,
            "speed_mean_kmh": float(valid_speed.mean()),
            "speed_min_kmh": float(valid_speed.min()),
            "speed_max_kmh": float(valid_speed.max()),
            "congestion_mean": float(valid_cong.mean()),
            "congestion_min": float(valid_cong.min()),
            "congestion_max": float(valid_cong.max()),
        },
        "stations": station_stats,
    }

    with open(OUT_SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"      Saved summary report: {OUT_SUMMARY_PATH}")
    print("\n" + "=" * 70)
    print("PHASE 2.4 & 2.5 EXECUTION SUCCESSFUL")
    print("=" * 70)


if __name__ == "__main__":
    build_aligned_dataset()
