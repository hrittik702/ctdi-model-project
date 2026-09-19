"""Phase 2.1: Spatio-temporal alignment of Air Quality and Meteorology domains.

Merges the cleaned hourly Air Quality (EPD) and surface Meteorology (ERA5 reanalysis)
datasets onto the canonical 16-station x 26,304-hour Cartesian grid (420,864 rows).

Strict Scope & Invariance Rules:
1. Preserve natural IEEE 754 NaNs in Air Quality (exactly 55,876 NaNs across 5 pollutants).
2. Maintain zero-missing completeness in Meteorology.
3. Maintain 'rainfall' strictly as rainfall (never renamed to visibility).
4. Dual sorting by (station_id, timestamp).
5. Output to data/interim/aligned/aligned_air_met_hourly.parquet.
"""

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERIM_AQ_PATH = PROJECT_ROOT / "data" / "interim" / "air_quality" / "clean_air_quality.parquet"
INTERIM_MET_PATH = PROJECT_ROOT / "data" / "interim" / "meteorology" / "clean_meteorology.parquet"
ALIGNED_DIR = PROJECT_ROOT / "data" / "interim" / "aligned"
OUTPUT_ALIGNED_AIR_MET = ALIGNED_DIR / "aligned_air_met_hourly.parquet"

EXPECTED_STATIONS = 16
EXPECTED_TIMESTAMPS = 26304
EXPECTED_TOTAL_ROWS = EXPECTED_STATIONS * EXPECTED_TIMESTAMPS  # 420,864

EXPECTED_AQ_NANS = {
    "pm25": 10657,
    "pm10": 11395,
    "no2": 11651,
    "o3": 11117,
    "so2": 11056,
    "total": 55876,
}


def align_air_and_meteorology() -> pd.DataFrame:
    """Execute Phase 2.1 temporal alignment between air quality and meteorology."""
    print("=" * 80)
    print("PHASE 2.1: TEMPORAL ALIGNMENT (AIR QUALITY + METEOROLOGY)")
    print("=" * 80)

    ALIGNED_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading Air Quality from: {INTERIM_AQ_PATH}")
    df_aq = pd.read_parquet(INTERIM_AQ_PATH)
    print(f"  AQ loaded: {len(df_aq):,} rows, {len(df_aq.columns)} columns")

    print(f"Loading Meteorology from: {INTERIM_MET_PATH}")
    df_met = pd.read_parquet(INTERIM_MET_PATH)
    print(f"  Met loaded: {len(df_met):,} rows, {len(df_met.columns)} columns")

    # 1. Structural assertions
    assert len(df_aq) == EXPECTED_TOTAL_ROWS, f"AQ row count mismatch: {len(df_aq)} vs {EXPECTED_TOTAL_ROWS}"
    assert len(df_met) == EXPECTED_TOTAL_ROWS, f"Met row count mismatch: {len(df_met)} vs {EXPECTED_TOTAL_ROWS}"

    # 2. Verify natural missing values in AQ
    aq_nans = {
        "pm25": int(df_aq["pm25"].isna().sum()),
        "pm10": int(df_aq["pm10"].isna().sum()),
        "no2": int(df_aq["no2"].isna().sum()),
        "o3": int(df_aq["o3"].isna().sum()),
        "so2": int(df_aq["so2"].isna().sum()),
    }
    aq_nans["total"] = sum(aq_nans.values())
    print(f"AQ Natural Missingness Audit: {aq_nans}")
    for k, v in EXPECTED_AQ_NANS.items():
        assert aq_nans[k] == v, f"AQ NaN mismatch for {k}: {aq_nans[k]} vs {v}"

    # 3. Verify zero missing values in Meteorology
    met_nans = {col: int(df_met[col].isna().sum()) for col in [
        "temperature", "relative_humidity", "pressure", "rainfall", "wind_direction", "wind_speed"
    ]}
    assert sum(met_nans.values()) == 0, f"Unexpected missing values in Meteorology: {met_nans}"

    # 4. Perform deterministic sort and merge
    df_aq_sorted = df_aq.sort_values(["station_id", "timestamp"]).reset_index(drop=True)
    df_met_sorted = df_met.sort_values(["station_id", "timestamp"]).reset_index(drop=True)

    # Primary key alignment check
    assert (df_aq_sorted["station_id"].values == df_met_sorted["station_id"].values).all(), "Station ID alignment mismatch"
    assert (df_aq_sorted["timestamp"].values == df_met_sorted["timestamp"].values).all(), "Timestamp alignment mismatch"

    # Merge datasets
    df_merged = pd.merge(
        df_aq_sorted,
        df_met_sorted[[
            "station_id", "timestamp", "pressure", "relative_humidity",
            "temperature", "rainfall", "wind_direction", "wind_speed"
        ]],
        on=["station_id", "timestamp"],
        how="inner",
    )

    assert len(df_merged) == EXPECTED_TOTAL_ROWS, f"Merged row count mismatch: {len(df_merged)} vs {EXPECTED_TOTAL_ROWS}"
    assert df_merged["station_id"].nunique() == EXPECTED_STATIONS
    assert df_merged["timestamp"].nunique() == EXPECTED_TIMESTAMPS

    # Verify column order
    ordered_cols = [
        "station_id", "station_name", "timestamp",
        "pm25", "pm10", "no2", "so2", "o3",
        "pressure", "relative_humidity", "temperature", "rainfall",
        "wind_direction", "wind_speed"
    ]
    df_merged = df_merged[ordered_cols]

    # Save output
    df_merged.to_parquet(OUTPUT_ALIGNED_AIR_MET, index=False, engine="pyarrow", compression="snappy")
    print(f"\nSaved aligned Air Quality + Meteorology dataset to: {OUTPUT_ALIGNED_AIR_MET}")
    print(f"  Shape: {df_merged.shape}")
    print(f"  Total Rows: {len(df_merged):,}")
    print(f"  Columns: {df_merged.columns.tolist()}")

    return df_merged


if __name__ == "__main__":
    align_air_and_meteorology()
