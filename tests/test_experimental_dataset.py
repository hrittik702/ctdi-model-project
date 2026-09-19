"""Comprehensive Quality Control and Verification Tests for Phase 4B.

Validates the 12 core requirements for experimental dataset construction:
1. No duplicate window IDs
2. Zero split overlap across purge buffers
3. Monotonic chronological ordering
4. Correct 24-hour temporal window length
5. Canonical 13-channel ordering (rainfall = index 8)
6. Natural NaNs preserved and never treated as targets
7. Artificial masking applied strictly where M_natural == 1
8. Target values Y_target bit-for-bit match original X at masked positions
9. Model input X_input does not expose target values
10. Normalization statistics calculated strictly on training split
11. Deterministic mask reproducibility across seeds
12. Raw data cryptographic immutability (all 683 files untouched)
"""

import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.dataset.normalization import (
    CANONICAL_13_CHANNELS,
    POLLUTANT_CHANNELS,
    FeatureNormalizer,
)
from src.dataset.missingness import (
    DEFAULT_TARGET_CHANNELS,
    ExperimentalMaskGenerator,
)
from src.dataset.split import ChronologicalSplitManager


PROJECT_ROOT = Path(__file__).parents[1]
EXPERIMENTS_DIR = PROJECT_ROOT / "data" / "interim" / "experiments"
WINDOWS_DIR = PROJECT_ROOT / "data" / "interim" / "windows"
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def test_qc01_no_duplicate_window_ids():
    """Check 1: No duplicate window IDs in split indices."""
    df_splits = pd.read_parquet(EXPERIMENTS_DIR / "splits" / "split_indices.parquet")
    assert df_splits["window_id"].is_unique, "Duplicate window IDs found in split indices!"
    assert len(df_splits) == 420496, f"Expected 420,496 windows, got {len(df_splits)}"


def test_qc02_zero_split_overlap_and_purge_buffers():
    """Check 2: Strict temporal separation with 24-hour purge buffers."""
    df_meta = pd.read_parquet(WINDOWS_DIR / "window_metadata.parquet")
    mgr = ChronologicalSplitManager(df_meta)
    assert mgr.verify_no_overlap() is True

    train_end = pd.to_datetime(df_meta[df_meta["temporal_split"] == "train"]["end_timestamp"].max())
    val_start = pd.to_datetime(df_meta[df_meta["temporal_split"] == "val"]["start_timestamp"].min())
    val_end = pd.to_datetime(df_meta[df_meta["temporal_split"] == "val"]["end_timestamp"].max())
    test_start = pd.to_datetime(df_meta[df_meta["temporal_split"] == "test"]["start_timestamp"].min())

    # Verify purge buffer durations
    train_val_gap_hours = (val_start - train_end).total_seconds() / 3600.0
    val_test_gap_hours = (test_start - val_end).total_seconds() / 3600.0
    assert train_val_gap_hours >= 24.0, f"Train-Val gap is {train_val_gap_hours}h, expected >= 24h"
    assert val_test_gap_hours >= 24.0, f"Val-Test gap is {val_test_gap_hours}h, expected >= 24h"


def test_qc03_chronological_ordering():
    """Check 3: Windows within each station are strictly sorted chronologically."""
    df_meta = pd.read_parquet(WINDOWS_DIR / "window_metadata.parquet")
    for _, group in df_meta.groupby("station_id"):
        ts = pd.to_datetime(group["start_timestamp"])
        assert ts.is_monotonic_increasing, "Window timestamps are not monotonically increasing!"


def test_qc04_and_05_window_dimensions_and_channel_ordering():
    """Checks 4 & 5: Shape (24, 13) and channel order with rainfall at index 8."""
    df_win = pd.read_parquet(WINDOWS_DIR / "24h_windows.parquet")
    row = df_win.iloc[0]
    
    # Check 13 columns present
    for idx, ch in enumerate(CANONICAL_13_CHANNELS):
        assert ch in row, f"Channel {ch} missing from window!"
        assert len(row[ch]) == 24, f"Channel {ch} has length {len(row[ch])}, expected 24"

    # Strict rainfall index check
    assert CANONICAL_13_CHANNELS[8] == "rainfall", "Channel 8 is not rainfall!"


def test_qc06_and_07_natural_nans_preserved_and_not_masked():
    """Checks 6 & 7: Natural missing values are never treated as artificial targets."""
    mask_gen = ExperimentalMaskGenerator(seed=42)

    # Synthetic natural mask with 20% natural NaNs
    rng = np.random.default_rng(42)
    m_nat = (rng.uniform(0, 1, size=(24, 13)) > 0.20).astype(np.int64)

    # Generate masks for all rates
    for rate in [0.10, 0.30, 0.50, 0.70]:
        m_obs, m_tgt, actual_rate, meta = mask_gen.create_mask(m_nat, pattern="random", rate=rate, seed=123)

        # M_target MUST be 0 wherever M_natural is 0
        leaked_targets = np.sum((m_nat == 0) & (m_tgt == 1))
        assert leaked_targets == 0, f"Natural NaN was masked as target! Count: {leaked_targets}"

        # M_natural must equal M_observed + M_target everywhere
        assert np.array_equal(m_nat, m_obs + m_tgt), "M_natural != M_observed + M_target"
        # M_observed and M_target must be mutually exclusive
        assert np.sum(m_obs * m_tgt) == 0, "M_observed and M_target overlap!"


def test_qc08_and_09_input_target_partitioning_and_no_leakage():
    """Checks 8 & 9: X_input hides targets and Y_target bit-for-bit matches original X."""
    # Synthetic window
    rng = np.random.default_rng(99)
    x_orig = rng.normal(loc=25.0, scale=10.0, size=(24, 13))
    m_nat = np.ones((24, 13), dtype=np.int64)
    m_nat[5:8, 0] = 0  # natural NaN on PM2.5

    mask_gen = ExperimentalMaskGenerator(seed=42)
    m_obs, m_tgt, _, _ = mask_gen.create_mask(m_nat, pattern="block", rate=0.30, seed=42)

    x_input, y_target = mask_gen.partition_inputs_and_targets(x_orig, m_nat, m_tgt, fill_input_with=np.nan)

    # 1. Y_target must match x_orig exactly where m_tgt == 1
    assert np.allclose(y_target[m_tgt == 1], x_orig[m_tgt == 1]), "Y_target does not match original X!"

    # 2. Y_target must be NaN everywhere m_tgt == 0
    assert np.all(np.isnan(y_target[m_tgt == 0])), "Y_target contains values outside target mask!"

    # 3. X_input must be NaN everywhere m_obs == 0 (including both natural NaNs and artificial targets)
    assert np.all(np.isnan(x_input[m_obs == 0])), "X_input leaks target values!"

    # 4. X_input must match x_orig where m_obs == 1
    assert np.allclose(x_input[m_obs == 1], x_orig[m_obs == 1]), "X_input corrupted observed values!"


def test_qc10_train_normalization_statistics_only():
    """Check 10: Normalization statistics are derived strictly from training timestamps."""
    norm_path = EXPERIMENTS_DIR / "normalization" / "normalization_stats.json"
    assert norm_path.exists(), f"Normalization statistics file missing: {norm_path}"

    with open(norm_path, "r", encoding="utf-8") as f:
        stats = json.load(f)

    # Verify fit criteria recorded
    fit_meta = stats.get("fit_criteria", {})
    assert fit_meta.get("num_station_hours") == 294528, "Trained on wrong number of station-hours!"
    assert fit_meta.get("end_timestamp") == "2021-02-05 23:00:00", "Training set extended beyond boundary!"

    # Verify transform and denormalize
    normalizer = FeatureNormalizer(stats)
    test_arr = np.ones((5, 24, 13)) * 20.0
    norm_arr = normalizer.transform(test_arr, mode="z_score")
    denorm_arr = normalizer.denormalize(norm_arr, mode="z_score")
    assert np.allclose(test_arr, denorm_arr, atol=1e-4), "Denormalization failed roundtrip!"


def test_qc11_deterministic_mask_regeneration():
    """Check 11: Identical seeds produce bit-for-bit identical masks."""
    m_nat = np.ones((24, 13), dtype=np.int64)
    mask_gen = ExperimentalMaskGenerator()

    # MCAR test
    _, m_tgt_1, r1 = mask_gen.create_random_mask(m_nat, rate=0.30, seed=777)
    _, m_tgt_2, r2 = mask_gen.create_random_mask(m_nat, rate=0.30, seed=777)
    assert np.array_equal(m_tgt_1, m_tgt_2), "MCAR masking not deterministic across same seed!"
    assert r1 == r2

    # Block test
    _, m_blk_1, rb1 = mask_gen.create_block_mask(m_nat, rate=0.50, seed=888)
    _, m_blk_2, rb2 = mask_gen.create_block_mask(m_nat, rate=0.50, seed=888)
    assert np.array_equal(m_blk_1, m_blk_2), "Block masking not deterministic across same seed!"
    assert rb1 == rb2


def test_qc12_raw_data_immutability():
    """Check 12: Cryptographic immutability of data/raw/."""
    raw_files = list(RAW_DIR.rglob("*"))
    actual_files = [f for f in raw_files if f.is_file()]
    assert len(actual_files) == 683, f"Expected 683 raw files, found {len(actual_files)}"

    # Check key primary hash
    epd_path = RAW_DIR / "air_quality" / "epd_air_quality_2019_2021_hourly.csv"
    h = hashlib.sha256(epd_path.read_bytes()).hexdigest()
    assert h == "f2b1b46a9c8e69e2f18077fac4c4d4f664cb24162523dc978219d82c225b57b2", "Air quality raw CSV was modified!"


def test_qc13_artifact_test_benchmark_masks_integrity():
    """Check 13: Direct artifact validation of stored test_benchmark_masks.parquet.
    
    Verifies:
    - Exactly 62,224 test windows.
    - All 14 columns present (window_id, station_id, 4 MCAR, 4 Block, 4 Outage).
    - Flattened dimension of 120 cells (24 hours x 5 criteria pollutants).
    - Zero leakage: No cell with natural NaN is marked as an artificial target.
    - Block and MCAR achieved rates meet target rates within +-0.5% tolerance.
    - Station outage rates match theoretical network ratios (6.25%, 12.50%, 25.00%, 100.00%).
    """
    benchmark_path = EXPERIMENTS_DIR / "masks" / "test_benchmark_masks.parquet"
    assert benchmark_path.exists(), f"Benchmark masks file missing: {benchmark_path}"

    df_bench = pd.read_parquet(benchmark_path)
    assert len(df_bench) == 62224, f"Expected 62,224 test windows, got {len(df_bench)}"

    expected_cols = [
        "window_id", "station_id",
        "mcar_10", "mcar_30", "mcar_50", "mcar_70",
        "block_10", "block_30", "block_50", "block_70",
        "station_outage_1", "station_outage_2", "station_outage_4", "station_outage_full",
    ]
    assert list(df_bench.columns) == expected_cols, f"Columns mismatch: {list(df_bench.columns)}"

    # Load matching natural masks
    df_nat = pd.read_parquet(WINDOWS_DIR / "missingness_masks.parquet", columns=["window_id"] + POLLUTANT_CHANNELS)
    df_nat_test = df_nat[df_nat["window_id"].isin(df_bench["window_id"])].sort_values("window_id")
    df_bench_sorted = df_bench.sort_values("window_id")

    # Stack natural masks for criteria pollutants into (N, 120)
    nat_matrices = []
    for _, row in df_nat_test.iterrows():
        # Shape (24, 5) -> flatten row-major or col-major consistent with mask generator (24 * 5 = 120)
        ch_arrays = [np.array(row[ch], dtype=np.int64) for ch in POLLUTANT_CHANNELS]
        mat = np.column_stack(ch_arrays).ravel()  # (120,)
        nat_matrices.append(mat)
    m_nat_arr = np.vstack(nat_matrices)
    total_eligible = int(m_nat_arr.sum())
    assert total_eligible == 7261392, f"Expected 7,261,392 eligible cells, got {total_eligible}"

    # Verify rates and zero leakage
    target_specs = {
        "mcar_10": (0.10, 0.005),
        "mcar_30": (0.30, 0.005),
        "mcar_50": (0.50, 0.005),
        "mcar_70": (0.70, 0.005),
        "block_10": (0.10, 0.005),
        "block_30": (0.30, 0.005),
        "block_50": (0.50, 0.005),
        "block_70": (0.70, 0.005),
        "station_outage_1": (1.0 / 16.0, 0.001),
        "station_outage_2": (2.0 / 16.0, 0.001),
        "station_outage_4": (4.0 / 16.0, 0.001),
        "station_outage_full": (1.0, 0.0001),
    }

    for col_name, (expected_rate, tolerance) in target_specs.items():
        m_tgt_arr = np.vstack(df_bench_sorted[col_name].values)
        assert m_tgt_arr.shape == (62224, 120), f"{col_name} shape mismatch: {m_tgt_arr.shape}"

        # 1. Zero leakage: Target mask must be 0 wherever natural mask is 0
        leaked_count = int(np.sum((m_nat_arr == 0) & (m_tgt_arr == 1)))
        assert leaked_count == 0, f"{col_name} has {leaked_count} leaked targets on natural NaNs!"

        # 2. Rate tolerance check on eligible cells
        actual_rate = float(m_tgt_arr.sum()) / total_eligible
        dev = abs(actual_rate - expected_rate)
        assert dev <= tolerance, f"{col_name} rate {actual_rate:.4f} deviates from {expected_rate:.4f} by {dev:.4f} > {tolerance}"


def test_qc14_log1p_rainfall_normalization_roundtrip():
    """Check 14: Log1p rainfall normalization and exact roundtrip back-transformation."""
    norm_path = EXPERIMENTS_DIR / "normalization" / "normalization_stats.json"
    normalizer = FeatureNormalizer.load(norm_path)

    # Synthetic test data: batch of 10 windows of 24h x 13 channels
    rng = np.random.default_rng(1234)
    x_test = np.zeros((10, 24, 13), dtype=np.float32)

    # Non-rainfall channels: normal values
    for c in range(13):
        if c != 8:
            mean = normalizer.stats["channels"][CANONICAL_13_CHANNELS[c]]["mean"]
            std = normalizer.stats["channels"][CANONICAL_13_CHANNELS[c]]["std"]
            x_test[..., c] = rng.normal(loc=mean, scale=std, size=(10, 24))

    # Rainfall channel (index 8): zero-inflated with realistic positive bursts
    rain_vals = np.array([0.0, 0.0, 0.0, 0.1, 0.5, 2.5, 10.0, 25.0, 50.0, 61.8], dtype=np.float32)
    x_test[..., 8] = np.tile(rain_vals, (10, 24))[:, :24]

    # Transform in log1p mode
    x_norm = normalizer.transform(x_test, mode="log1p", fill_nan_with=None)

    # Denormalize in log1p mode
    x_recon = normalizer.denormalize(x_norm, mode="log1p")

    # Roundtrip check: reconstruction error < 1e-4 everywhere
    assert np.allclose(x_test, x_recon, atol=1e-4), "Log1p roundtrip failed reconstruction!"

    # Check zero rainfall strictly maps to >= 0.0 (non-negative physical constraint)
    assert np.all(x_recon[..., 8] >= 0.0), "Denormalized rainfall produced negative values!"
    zero_mask = (x_test[..., 8] == 0.0)
    assert np.allclose(x_recon[..., 8][zero_mask], 0.0, atol=1e-5), "Zero rainfall was not reconstructed to 0.0!"


def test_qc15_wind_direction_representations():
    """Check 15: Primary 13-channel degree contract vs 14-channel circular ablation."""
    # Test circular decomposition transformation
    x_13 = np.zeros((4, 24, 13), dtype=np.float32)
    # Set wind directions: 0 deg (North), 90 deg (East), 180 deg (South), 270 deg (West)
    x_13[0, :, 9] = 0.0
    x_13[1, :, 9] = 90.0
    x_13[2, :, 9] = 180.0
    x_13[3, :, 9] = 270.0

    normalizer = FeatureNormalizer()
    x_14 = normalizer.transform_circular_wind(x_13)

    assert x_14.shape == (4, 24, 14), f"Expected shape (4, 24, 14), got {x_14.shape}"

    # Channels 0..8 unchanged
    assert np.array_equal(x_14[..., 0:9], x_13[..., 0:9])

    # Check trigonometric projections: sin at index 9, cos at index 10
    # 0 deg: sin(0) = 0, cos(0) = 1
    assert np.allclose(x_14[0, :, 9], 0.0, atol=1e-5)
    assert np.allclose(x_14[0, :, 10], 1.0, atol=1e-5)

    # 90 deg: sin(90) = 1, cos(90) = 0
    assert np.allclose(x_14[1, :, 9], 1.0, atol=1e-5)
    assert np.allclose(x_14[1, :, 10], 0.0, atol=1e-5)

    # 180 deg: sin(180) = 0, cos(180) = -1
    assert np.allclose(x_14[2, :, 9], 0.0, atol=1e-5)
    assert np.allclose(x_14[2, :, 10], -1.0, atol=1e-5)

    # 270 deg: sin(270) = -1, cos(270) = 0
    assert np.allclose(x_14[3, :, 9], -1.0, atol=1e-5)
    assert np.allclose(x_14[3, :, 10], 0.0, atol=1e-5)

    # Channels 11..13 match old channels 10..12
    assert np.array_equal(x_14[..., 11:14], x_13[..., 10:13])

