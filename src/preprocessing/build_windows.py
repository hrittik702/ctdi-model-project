"""Phase 3: 24-Hour Temporal Window Construction & Natural Missingness Representation.

Transforms the validated Phase 2 aligned hourly dataset (420,864 rows x 13 channels)
into chronological 24-hour sliding windows (length=24, stride=1) across 16 stations.
Constructs exact natural missingness masks M without imputation or artificial corruption.
Ensures zero station boundary crossing and prepares leakage-safe chronological splits.
"""

from pathlib import Path
import json
import time
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Input paths
INPUT_ALIGNED_PATH = PROJECT_ROOT / "data" / "interim" / "aligned" / "aligned_hourly_station_data.parquet"

# Output paths
OUT_DIR = PROJECT_ROOT / "data" / "interim" / "windows"
OUT_WINDOWS_PARQUET = OUT_DIR / "24h_windows.parquet"
OUT_MASKS_PARQUET = OUT_DIR / "missingness_masks.parquet"
OUT_METADATA_PARQUET = OUT_DIR / "window_metadata.parquet"
OUT_SUMMARY_JSON = OUT_DIR / "window_summary.json"

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

POLLUTANT_CHANNELS = ["pm25", "pm10", "no2", "so2", "o3"]

EXPECTED_STATIONS = 16
EXPECTED_HOURS_PER_STATION = 26304
EXPECTED_TOTAL_HOURLY_ROWS = 420864

EXPECTED_AQ_NANS = {
    "pm25": 10657,
    "pm10": 11395,
    "no2": 11651,
    "so2": 11056,
    "o3": 11117,
}
EXPECTED_TOTAL_AQ_NANS = 55876

WINDOW_LENGTH = 24
WINDOW_STRIDE = 1
EXPECTED_WINDOWS_PER_STATION = EXPECTED_HOURS_PER_STATION - WINDOW_LENGTH + 1  # 26,281
EXPECTED_TOTAL_WINDOWS = EXPECTED_STATIONS * EXPECTED_WINDOWS_PER_STATION      # 420,496

# Chronological split boundaries
TRAIN_END_TS = pd.Timestamp("2021-02-05 23:00:00")
VAL_START_TS = pd.Timestamp("2021-02-07 00:00:00")
VAL_END_TS = pd.Timestamp("2021-07-20 23:00:00")
TEST_START_TS = pd.Timestamp("2021-07-22 00:00:00")


def validate_input_dataset(df: pd.DataFrame):
    """Phase 3.1: Validate input aligned dataset."""
    print("\n[Phase 3.1] Validating input dataset structure...")
    assert len(df) == EXPECTED_TOTAL_HOURLY_ROWS, (
        f"Row count mismatch! Expected {EXPECTED_TOTAL_HOURLY_ROWS}, got {len(df)}"
    )

    stations = sorted(df["station_id"].unique().tolist())
    assert len(stations) == EXPECTED_STATIONS, f"Expected {EXPECTED_STATIONS} stations, got {len(stations)}"

    for st_id, group in df.groupby("station_id"):
        assert len(group) == EXPECTED_HOURS_PER_STATION, (
            f"Station {st_id} has {len(group)} rows, expected {EXPECTED_HOURS_PER_STATION}"
        )

    ts_min = str(df["timestamp"].min())
    ts_max = str(df["timestamp"].max())
    assert ts_min == "2019-01-01 00:00:00", f"Unexpected start timestamp: {ts_min}"
    assert ts_max == "2021-12-31 23:00:00", f"Unexpected end timestamp: {ts_max}"

    duplicates = int(df.duplicated(subset=["station_id", "timestamp"]).sum())
    assert duplicates == 0, f"Found {duplicates} duplicate station-hour records!"

    for idx, col in enumerate(CANONICAL_13_CHANNELS):
        assert col in df.columns, f"Canonical channel {idx} '{col}' missing from input!"
    assert df.columns[3:16].tolist() == CANONICAL_13_CHANNELS, "Canonical channel sequence mismatch!"

    print(f"  [PASS] Exactly {len(df):,} rows across {len(stations)} stations and {EXPECTED_HOURS_PER_STATION:,} hours.")
    print(f"  [PASS] Canonical 13 channels verified in exact sequence (rainfall at index 8 / channel #9).")


def audit_natural_missingness(df: pd.DataFrame) -> dict:
    """Phase 3.2: Audit natural pollutant and multi-modal missingness."""
    print("\n[Phase 3.2] Auditing natural missingness distributions...")
    total_aq_nans = 0
    pollutant_stats = {}

    for col, exp_nans in EXPECTED_AQ_NANS.items():
        nans = int(df[col].isna().sum())
        assert nans == exp_nans, f"Pollutant {col} NaN mismatch! Expected {exp_nans}, got {nans}"
        total_aq_nans += nans
        pollutant_stats[col] = {
            "total_observations": len(df),
            "observed_values": len(df) - nans,
            "missing_values": nans,
            "missing_percentage": round(nans / len(df) * 100.0, 4),
        }
    assert total_aq_nans == EXPECTED_TOTAL_AQ_NANS, (
        f"Total AQ NaNs mismatch! Expected {EXPECTED_TOTAL_AQ_NANS}, got {total_aq_nans}"
    )

    # Missingness by station
    st_missing = {}
    for st_id, group in df.groupby("station_id"):
        st_nans = int(group[POLLUTANT_CHANNELS].isna().sum().sum())
        st_missing[int(st_id)] = {
            "station_name": str(group["station_name"].iloc[0]),
            "missing_pollutant_cells": st_nans,
            "missing_percentage": round(st_nans / (len(group) * len(POLLUTANT_CHANNELS)) * 100.0, 4),
        }

    # Missingness by year, month, hour
    df_temp = df.copy()
    dt_series = pd.to_datetime(df_temp["timestamp"])
    df_temp["year"] = dt_series.dt.year
    df_temp["month"] = dt_series.dt.month
    df_temp["hour"] = dt_series.dt.hour

    year_missing = {
        int(yr): int(grp[POLLUTANT_CHANNELS].isna().sum().sum())
        for yr, grp in df_temp.groupby("year")
    }
    month_missing = {
        int(mo): int(grp[POLLUTANT_CHANNELS].isna().sum().sum())
        for mo, grp in df_temp.groupby("month")
    }
    hour_missing = {
        int(hr): int(grp[POLLUTANT_CHANNELS].isna().sum().sum())
        for hr, grp in df_temp.groupby("hour")
    }

    print(f"  [PASS] Preserved exact 55,876 natural pollutant NaNs (bit-for-bit match).")
    print(f"  By pollutant: {[(k, v['missing_values']) for k, v in pollutant_stats.items()]}")
    print(f"  By year: {year_missing}")

    return {
        "pollutant_missingness": pollutant_stats,
        "station_missingness": st_missing,
        "year_missingness": year_missing,
        "month_missingness": month_missing,
        "hour_missingness": hour_missing,
    }


def construct_windows_and_masks(df: pd.DataFrame):
    """Phase 3.3 to 3.8: Build sliding windows, masks, metadata and export Parquet."""
    print("\n[Phase 3.3 - 3.6] Constructing 24-hour sliding windows & natural masks...")
    t0 = time.time()

    # Pre-allocate containers
    meta_rows = []
    window_id_counter = 0

    # Dictionaries for pyarrow table creation
    windows_dict = {"window_id": [], "station_id": []}
    masks_dict = {"window_id": [], "station_id": []}
    for ch in CANONICAL_13_CHANNELS:
        windows_dict[ch] = []
        masks_dict[ch] = []

    # Sort deterministically by station_id, timestamp
    df_sorted = df.sort_values(["station_id", "timestamp"]).reset_index(drop=True)

    # Pollutant indices in CANONICAL_13_CHANNELS
    pollutant_indices = [CANONICAL_13_CHANNELS.index(p) for p in POLLUTANT_CHANNELS]

    for st_id, group in df_sorted.groupby("station_id", sort=True):
        st_name = str(group["station_name"].iloc[0])
        timestamps = group["timestamp"].to_numpy()
        dt_timestamps = pd.to_datetime(timestamps)

        # Contiguous feature array (26304, 13)
        feat_2d = np.ascontiguousarray(group[CANONICAL_13_CHANNELS].to_numpy(dtype=np.float32))

        # Natural mask: 1 if observed, 0 if NaN
        mask_2d = (~np.isnan(feat_2d)).astype(np.uint8)

        # Sliding window views with dtype-specific byte strides
        shape = (EXPECTED_WINDOWS_PER_STATION, WINDOW_LENGTH, len(CANONICAL_13_CHANNELS))
        feat_strides = (feat_2d.strides[0], feat_2d.strides[0], feat_2d.strides[1])
        mask_strides = (mask_2d.strides[0], mask_2d.strides[0], mask_2d.strides[1])

        win_view = np.lib.stride_tricks.as_strided(feat_2d, shape=shape, strides=feat_strides)
        mask_view = np.lib.stride_tricks.as_strided(mask_2d, shape=shape, strides=mask_strides)

        # Compute metadata per window
        for w_idx in range(EXPECTED_WINDOWS_PER_STATION):
            w_id = window_id_counter
            window_id_counter += 1

            start_t = dt_timestamps[w_idx]
            end_t = dt_timestamps[w_idx + WINDOW_LENGTH - 1]

            # Pollutant mask slice: (24, 5)
            # Missing cells in pollutants: where mask is 0
            w_mask = mask_view[w_idx]
            pollutant_mask_slice = w_mask[:, pollutant_indices]
            missing_pollutant_cells = int((pollutant_mask_slice == 0).sum())
            missing_total_cells = int((w_mask == 0).sum())

            # Assign chronological split with buffer
            if end_t <= TRAIN_END_TS:
                split = "train"
            elif start_t < VAL_START_TS:
                split = "buffer_train_val"
            elif end_t <= VAL_END_TS:
                split = "val"
            elif start_t < TEST_START_TS:
                split = "buffer_val_test"
            else:
                split = "test"

            meta_rows.append({
                "window_id": w_id,
                "station_id": int(st_id),
                "station_name": st_name,
                "start_timestamp": str(timestamps[w_idx]),
                "end_timestamp": str(timestamps[w_idx + WINDOW_LENGTH - 1]),
                "year": int(start_t.year),
                "month": int(start_t.month),
                "day": int(start_t.day),
                "start_hour": int(start_t.hour),
                "missing_pollutant_cells": missing_pollutant_cells,
                "missing_pollutant_pct": round(missing_pollutant_cells / (WINDOW_LENGTH * 5) * 100.0, 4),
                "has_missing_pollutant": missing_pollutant_cells > 0,
                "missing_total_cells": missing_total_cells,
                "temporal_split": split,
            })

            # Append to column lists for pyarrow
            windows_dict["window_id"].append(w_id)
            windows_dict["station_id"].append(int(st_id))
            masks_dict["window_id"].append(w_id)
            masks_dict["station_id"].append(int(st_id))

            for ch_idx, ch_name in enumerate(CANONICAL_13_CHANNELS):
                windows_dict[ch_name].append(win_view[w_idx, :, ch_idx].tolist())
                masks_dict[ch_name].append(mask_view[w_idx, :, ch_idx].tolist())

        print(f"  Processed station {st_id:2d} ({st_name:18s}): {EXPECTED_WINDOWS_PER_STATION:,} windows")

    assert window_id_counter == EXPECTED_TOTAL_WINDOWS, (
        f"Total windows mismatch! Expected {EXPECTED_TOTAL_WINDOWS}, got {window_id_counter}"
    )

    print(f"\n[Phase 3.8] Serializing output Parquet files to {OUT_DIR}...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Window Metadata Parquet
    df_meta = pd.DataFrame(meta_rows)
    df_meta.to_parquet(OUT_METADATA_PARQUET, index=False, engine="pyarrow", compression="snappy")
    meta_size_mb = OUT_METADATA_PARQUET.stat().st_size / (1024 * 1024)
    print(f"  Saved metadata: {OUT_METADATA_PARQUET} ({meta_size_mb:.2f} MB)")

    # 2. 24h Windows Parquet
    win_table = pa.Table.from_pydict(windows_dict)
    pq.write_table(win_table, OUT_WINDOWS_PARQUET, compression="snappy")
    win_size_mb = OUT_WINDOWS_PARQUET.stat().st_size / (1024 * 1024)
    print(f"  Saved windows:  {OUT_WINDOWS_PARQUET} ({win_size_mb:.2f} MB)")

    # 3. Missingness Masks Parquet
    mask_table = pa.Table.from_pydict(masks_dict)
    pq.write_table(mask_table, OUT_MASKS_PARQUET, compression="snappy")
    mask_size_mb = OUT_MASKS_PARQUET.stat().st_size / (1024 * 1024)
    print(f"  Saved masks:    {OUT_MASKS_PARQUET} ({mask_size_mb:.2f} MB)")

    # Compute summary statistics
    split_counts = df_meta["temporal_split"].value_counts().to_dict()
    missing_windows_count = int(df_meta["has_missing_pollutant"].sum())
    complete_windows_count = len(df_meta) - missing_windows_count
    max_missing_cells = int(df_meta["missing_pollutant_cells"].max())
    mean_missing_cells = float(df_meta["missing_pollutant_cells"].mean())

    summary = {
        "status": "COMPLETE",
        "phase": "3_temporal_window_construction",
        "elapsed_seconds": round(time.time() - t0, 2),
        "total_windows": len(df_meta),
        "windows_per_station": EXPECTED_WINDOWS_PER_STATION,
        "stations_count": EXPECTED_STATIONS,
        "window_length_hours": WINDOW_LENGTH,
        "stride_hours": WINDOW_STRIDE,
        "canonical_channels_count": len(CANONICAL_13_CHANNELS),
        "canonical_channels": CANONICAL_13_CHANNELS,
        "window_shape": [WINDOW_LENGTH, len(CANONICAL_13_CHANNELS)],
        "temporal_splits": split_counts,
        "missingness_summary": {
            "windows_with_missing_pollutant": missing_windows_count,
            "windows_with_zero_missing_pollutant": complete_windows_count,
            "pct_windows_with_missing_pollutant": round(missing_windows_count / len(df_meta) * 100.0, 4),
            "max_missing_pollutant_cells_in_window": max_missing_cells,
            "mean_missing_pollutant_cells_per_window": round(mean_missing_cells, 4),
            "total_pollutant_cells_per_window": WINDOW_LENGTH * len(POLLUTANT_CHANNELS),
        },
        "artifacts": {
            "windows_parquet": str(OUT_WINDOWS_PARQUET.relative_to(PROJECT_ROOT)),
            "windows_parquet_size_mb": round(win_size_mb, 2),
            "masks_parquet": str(OUT_MASKS_PARQUET.relative_to(PROJECT_ROOT)),
            "masks_parquet_size_mb": round(mask_size_mb, 2),
            "metadata_parquet": str(OUT_METADATA_PARQUET.relative_to(PROJECT_ROOT)),
            "metadata_parquet_size_mb": round(meta_size_mb, 2),
        },
    }

    with open(OUT_SUMMARY_JSON, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Saved summary:  {OUT_SUMMARY_JSON}")

    return summary


def run_phase_3():
    print("=" * 70)
    print("PHASE 3: 24-HOUR TEMPORAL WINDOWS & NATURAL MISSINGNESS MASKS")
    print("=" * 70)

    # 1. Load input dataset
    print(f"Loading aligned dataset from: {INPUT_ALIGNED_PATH}")
    df = pd.read_parquet(INPUT_ALIGNED_PATH)

    # 2. Phase 3.1: Validate input dataset
    validate_input_dataset(df)

    # 3. Phase 3.2: Natural missingness audit
    missing_audit = audit_natural_missingness(df)

    # 4. Phase 3.3 - 3.8: Construct and serialize windows, masks, metadata
    summary = construct_windows_and_masks(df)

    print("\n" + "=" * 70)
    print("PHASE 3 ARTIFACT GENERATION SUCCESSFUL")
    print(f"Total Windows: {summary['total_windows']:,} ({EXPECTED_WINDOWS_PER_STATION:,} / station)")
    print(f"Window Shape:  {summary['window_shape']}")
    print(f"Splits:        {summary['temporal_splits']}")
    print("=" * 70)


if __name__ == "__main__":
    run_phase_3()
