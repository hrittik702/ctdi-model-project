"""Spatio-temporal alignment and multi-modal feature fusion for Hong Kong air quality research."""

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

# Paths and directories
raw_data_air = Path("data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv")
raw_data_meteor = Path("data/raw/meteorology/hourly_meteorology_16stations_2019_2021.csv")
raw_data_station = Path("data/raw/station_metadata/air_quality_stations.csv")
raw_data_traffic = Path("data/raw/traffic/hourly_traffic_16stations_2019_2021.csv")

interim_dir = Path("data/interim")
interim_dir.mkdir(parents=True, exist_ok=True)

out_parquet = interim_dir / "aligned_hourly_features.parquet"
out_dist = interim_dir / "spatial_distance_matrix.npy"

# Canonical channels matching CTDI benchmark specification (Yu et al. 2025)
pollutant_channels = [
    "pm25",
    "pm10",
    "no2",
    "o3",
    "so2",
]

meteor_channels = [
    "temperature",
    "relative_humidity",
    "wind_speed",
    "wind_direction",
    "pressure",
    "rainfall",
]

traffic_channels = [
    "traffic_speed",
    "traffic_volume",
]

canonical_channels = (
    pollutant_channels
    + meteor_channels
    + traffic_channels
)


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on Earth in kilometers."""
    radius = 6371.0  # Earth mean radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return float(radius * c)


def compute_haversine_distance_matrix(df_target_meta: pd.DataFrame) -> np.ndarray:
    """Compute and validate pairwise geographic distance matrix (in km) for target stations."""
    n = len(df_target_meta)
    dist_matrix = np.zeros((n, n), dtype=np.float32)
    lats = df_target_meta["latitude"].values
    lons = df_target_meta["longitude"].values

    for i in range(n):
        for j in range(n):
            if i == j:
                dist_matrix[i, j] = 0.0
            else:
                dist_matrix[i, j] = haversine_distance_km(lats[i], lons[i], lats[j], lons[j])

    # Assertions on distance matrix
    if dist_matrix.shape != (16, 16):
        raise ValueError(f"Expected distance matrix shape (16, 16), got {dist_matrix.shape}.")
    if not np.allclose(np.diag(dist_matrix), 0.0):
        raise ValueError("Distance matrix diagonal must be strictly 0.0.")
    if not np.allclose(dist_matrix, dist_matrix.T):
        raise ValueError("Distance matrix must be strictly symmetric.")

    return dist_matrix


def load_and_validate_station_metadata(
    meta_path: Path = raw_data_station,
) -> pd.DataFrame:
    """Load station metadata, validate the 16 target CTDI stations, and return sorted target metadata."""
    if not meta_path.exists():
        raise FileNotFoundError(f"Station metadata file not found at: {meta_path}")

    df_meta = pd.read_csv(meta_path)
    if "in_ctdi_study" not in df_meta.columns:
        raise ValueError(f"Column 'in_ctdi_study' missing from station metadata file: {meta_path}")

    # Interpret in_ctdi_study as a strict boolean filter
    df_meta["in_ctdi_study"] = df_meta["in_ctdi_study"].astype(str).str.strip().str.lower() == "true"

    df_target_meta = (
        df_meta[df_meta["in_ctdi_study"]]
        .copy()
        .sort_values("station_name")
        .reset_index(drop=True)
    )

    # Validate exact station count
    if len(df_target_meta) != 16:
        raise ValueError(
            f"Expected exactly 16 target stations with in_ctdi_study == True, but found {len(df_target_meta)}."
        )

    print("=" * 60)
    print("1. CTDI TARGET STATIONS VALIDATION")
    print("=" * 60)
    print(f"Number of CTDI target stations: {len(df_target_meta)}")
    for _, row in df_target_meta.iterrows():
        st_id = row.get("station_id", "N/A")
        print(f"  - {row['station_name']} (ID: {st_id}, Type: {row.get('station_type', 'N/A')})")

    return df_target_meta


def construct_expected_station_hour_grid(
    df_target_meta: pd.DataFrame,
    start_time: str = "2019-01-01 00:00:00",
    end_time: str = "2021-12-31 23:00:00",
) -> pd.DataFrame:
    """Construct the expected complete Cartesian grid of 16 stations x 26,304 hourly timestamps."""
    expected_timestamps = pd.date_range(start=start_time, end=end_time, freq="h")
    expected_hours = len(expected_timestamps)
    if expected_hours != 26304:
        raise ValueError(f"Expected 26,304 hours in study period, got {expected_hours}.")

    # Build Cartesian product: 16 stations x 26,304 hours = 420,864 rows
    grid_rows = []
    station_id_map = dict(zip(df_target_meta["station_name"], df_target_meta["station_id"]))

    for st_name in df_target_meta["station_name"]:
        st_id = station_id_map.get(st_name, np.nan)
        for ts in expected_timestamps:
            grid_rows.append({
                "station_id": st_id,
                "station_name": st_name,
                "timestamp": ts,
            })

    df_grid = pd.DataFrame(grid_rows)
    expected_total_rows = 16 * 26304
    if len(df_grid) != expected_total_rows:
        raise ValueError(f"Expected grid length {expected_total_rows}, got {len(df_grid)}.")

    return df_grid


def validate_and_load_source(
    source_name: str,
    source_path: Path,
    required_channels: List[str],
    df_target_meta: pd.DataFrame,
    df_grid: pd.DataFrame,
) -> pd.DataFrame:
    """Load, inspect, and validate an individual data source against the target stations and expected grid."""
    print("\n" + "=" * 60)
    print(f"VALIDATING SOURCE: {source_name.upper()}")
    print("=" * 60)

    if not source_path.exists():
        raise FileNotFoundError(f"{source_name} raw dataset not found at: {source_path}")

    df_source = pd.read_csv(source_path)

    # 1. Validate required columns
    for ch in required_channels:
        if ch not in df_source.columns:
            raise ValueError(
                f"Required column '{ch}' is missing from {source_name} source file ({source_path})."
            )

    if "station_name" not in df_source.columns or "timestamp" not in df_source.columns:
        raise ValueError(
            f"Source {source_name} must contain 'station_name' and 'timestamp' columns."
        )

    # 2. Timestamp and Timezone validation
    df_source["timestamp"] = pd.to_datetime(df_source["timestamp"])
    is_tz_aware = df_source["timestamp"].dt.tz is not None
    print(f"  Timestamp format: ISO datetime (Timezone-aware: {is_tz_aware})")
    if is_tz_aware:
        # Standardize to timezone-naive local Hong Kong timestamps
        df_source["timestamp"] = df_source["timestamp"].dt.tz_localize(None)

    # 3. Restrict explicitly to the 16 target stations
    df_source = df_source[df_source["station_name"].isin(df_target_meta["station_name"])].copy()

    # 4. Check for duplicate records on (station_name, timestamp)
    dup_mask = df_source.duplicated(subset=["station_name", "timestamp"])
    dup_count = int(dup_mask.sum())
    if dup_count > 0:
        raise ValueError(
            f"Found {dup_count} duplicate (station_name, timestamp) combinations in {source_name} dataset."
        )

    # 5. Check coverage relative to expected grid
    grid_index = set(zip(df_grid["station_name"], df_grid["timestamp"]))
    source_index = set(zip(df_source["station_name"], df_source["timestamp"]))
    missing_records_count = len(grid_index - source_index)

    print(f"  Total records: {len(df_source):,}")
    print(f"  Unique stations: {df_source['station_name'].nunique()}")
    print(f"  Timestamp range: {df_source['timestamp'].min()} to {df_source['timestamp'].max()}")
    print(f"  Duplicate records: {dup_count}")
    print(f"  Missing records relative to expected grid: {missing_records_count}")

    # 6. Report natural NaN counts per required channel
    print("  Natural NaN counts per feature:")
    for ch in required_channels:
        nan_count = int(df_source[ch].isna().sum())
        nan_pct = (nan_count / len(df_source)) * 100.0 if len(df_source) > 0 else 0.0
        print(f"    - {ch:<20}: {nan_count:,} NaNs ({nan_pct:.2f}%)")

    return df_source


def align_and_fuse_features(
    air_path: Path = raw_data_air,
    met_path: Path = raw_data_meteor,
    traffic_path: Path = raw_data_traffic,
    meta_path: Path = raw_data_station,
    out_parquet_path: Path = out_parquet,
    out_dist_path: Path = out_dist,
) -> Tuple[pd.DataFrame, np.ndarray]:
    """Perform strict, grid-preserving spatio-temporal alignment across air, meteorology, and real traffic sources."""
    print("\nBeginning spatio-temporal alignment pipeline...")

    # Step 1: Load and validate station metadata
    df_target_meta = load_and_validate_station_metadata(meta_path)

    # Step 2: Construct expected station-hour grid (420,864 combinations)
    df_grid = construct_expected_station_hour_grid(df_target_meta)
    print(f"\nConstructed expected Cartesian grid: {len(df_grid):,} station-hour rows.")

    # Step 3: Compute and save pairwise Haversine distance matrix
    print("\nComputing spatial distance matrix for target stations...")
    dist_matrix = compute_haversine_distance_matrix(df_target_meta)
    np.save(out_dist_path, dist_matrix)
    print(f"Saved verified spatial distance matrix to {out_dist_path} (Shape: {dist_matrix.shape}).")

    # Step 4: Validate and load air quality source
    df_air = validate_and_load_source(
        source_name="air_quality",
        source_path=air_path,
        required_channels=pollutant_channels,
        df_target_meta=df_target_meta,
        df_grid=df_grid,
    )

    # Step 5: Validate and load meteorology source
    df_met = validate_and_load_source(
        source_name="meteorology",
        source_path=met_path,
        required_channels=meteor_channels,
        df_target_meta=df_target_meta,
        df_grid=df_grid,
    )

    # Step 6: Validate and load traffic source (STRICT REAL DATA CHECK)
    print("\n" + "=" * 60)
    print("VALIDATING SOURCE: TRAFFIC")
    print("=" * 60)
    if not traffic_path.exists():
        raise FileNotFoundError(
            f"Real CTDI traffic dataset not found at '{traffic_path}'.\n"
            f"The CTDI research paper specifies that traffic features ('traffic_speed' and 'traffic_volume') "
            f"must come from real source traffic data (e.g. Hong Kong Traffic Speed Map / Transport Department detector streams).\n"
            f"Synthetic traffic generation has been completely removed. "
            f"Please provide the real raw traffic dataset before 13-channel alignment can produce the interim dataset."
        )

    df_traffic = validate_and_load_source(
        source_name="traffic",
        source_path=traffic_path,
        required_channels=traffic_channels,
        df_target_meta=df_target_meta,
        df_grid=df_grid,
    )

    # Step 7: Grid-preserving alignment (preserving temporal grid, keeping natural NaNs)
    print("\nPerforming grid-preserving alignment across all modalities...")
    df_aligned = pd.merge(
        df_grid,
        df_air[["station_name", "timestamp"] + pollutant_channels],
        on=["station_name", "timestamp"],
        how="left",
    )

    df_aligned = pd.merge(
        df_aligned,
        df_met[["station_name", "timestamp"] + meteor_channels],
        on=["station_name", "timestamp"],
        how="left",
    )

    df_aligned = pd.merge(
        df_aligned,
        df_traffic[["station_name", "timestamp"] + traffic_channels],
        on=["station_name", "timestamp"],
        how="left",
    )

    # Step 8: Final column ordering and validation
    ordered_cols = ["station_id", "station_name", "timestamp"] + canonical_channels
    df_final = (
        df_aligned[ordered_cols]
        .sort_values(["station_name", "timestamp"])
        .reset_index(drop=True)
    )

    expected_total_rows = 16 * 26304
    if len(df_final) != expected_total_rows:
        raise ValueError(
            f"Aligned row count mismatch: expected {expected_total_rows}, got {len(df_final)}."
        )

    # Step 9: Save interim parquet output
    df_final.to_parquet(out_parquet_path, index=False, engine="pyarrow")
    print(f"\nSuccessfully saved interim aligned dataset to: {out_parquet_path}")
    print(f"  Rows: {len(df_final):,}")
    print(f"  Columns: {len(df_final.columns)} -> {df_final.columns.tolist()}")

    return df_final, dist_matrix


def run_standalone_check():
    """Run standalone alignment validation. Validates metadata, air, meteorology, distance matrix,

    and verifies that traffic data requirement correctly halts execution instead of synthesizing fake data.
    """
    print("RUNNING ALIGNMENT PIPELINE VALIDATION...")
    try:
        align_and_fuse_features()
    except FileNotFoundError as err:
        print("\n" + "!" * 60)
        print("ALIGNMENT CORRECTLY HALTED AS EXPECTED:")
        print(err)
        print("!" * 60)
        print("\nResult: No synthetic traffic was created. Alignment correctly stopped.")


if __name__ == "__main__":
    run_standalone_check()
