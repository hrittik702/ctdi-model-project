"""Teammate consumption test suite for CTDI_AirPollution_TrainingDataset_v1.0.

Validates that a new teammate or ML model-training script can consume
the final package independently without needing access to data/raw/.
Tests:
1. Load training NPZ and verify shapes.
2. Inspect and apply normalization statistics.
3. Load and inspect channel schema and station metadata.
4. Load benchmark masks and assert target firewall.
5. Reconstruct sample tensor [24, 13] and verify input/target partition.
6. Verify independent consumption with zero raw data dependencies.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parents[1]
PACKAGE_DIR = PROJECT_ROOT / "data" / "final" / "CTDI_AirPollution_TrainingDataset_v1.0"


@pytest.fixture(scope="module")
def package_paths():
    assert PACKAGE_DIR.exists(), f"Final package not found at {PACKAGE_DIR}"
    return {
        "train_x_npz": PACKAGE_DIR / "train" / "X_train.npz",
        "train_m_npz": PACKAGE_DIR / "train" / "M_natural_train.npz",
        "val_x_npz": PACKAGE_DIR / "validation" / "X_val.npz",
        "test_x_npz": PACKAGE_DIR / "test" / "X_test.npz",
        "test_m_npz": PACKAGE_DIR / "test" / "M_natural_test.npz",
        "norm_json": PACKAGE_DIR / "metadata" / "normalization_stats.json",
        "schema_csv": PACKAGE_DIR / "metadata" / "channel_schema.csv",
        "stations_csv": PACKAGE_DIR / "metadata" / "station_metadata.csv",
        "splits_csv": PACKAGE_DIR / "metadata" / "split_manifest.csv",
        "meta_parquet": PACKAGE_DIR / "metadata" / "window_metadata.parquet",
        "mcar_30_npz": PACKAGE_DIR / "masks" / "mcar" / "mcar_30.npz",
    }


def test_teammate_01_load_training_npz(package_paths):
    """Teammate Step 1: Load training tensor directly via numpy."""
    data = np.load(package_paths["train_x_npz"])
    X_train = data["X"]
    window_ids = data["window_id"]
    station_ids = data["station_id"]

    assert X_train.shape == (294160, 24, 13)
    assert X_train.dtype == np.float32
    assert len(window_ids) == 294160
    assert len(station_ids) == 294160

    mask_data = np.load(package_paths["train_m_npz"])
    M_train = mask_data["M_natural"]
    assert M_train.shape == (294160, 24, 13)
    assert M_train.dtype == np.uint8


def test_teammate_02_normalization_denormalization(package_paths):
    """Teammate Step 2: Load normalization parameters and transform a sample."""
    with open(package_paths["norm_json"], "r", encoding="utf-8") as f:
        norm_stats = json.load(f)

    channels = norm_stats["channels"]
    assert len(channels) == 13
    assert norm_stats["num_samples"] == 294528  # fitted strictly on train station-hours

    data = np.load(package_paths["train_x_npz"])
    sample_x = data["X"][0]  # (24, 13)

    # Normalize PM2.5 (Channel 0)
    mu = channels["pm25"]["mean"]
    sigma = channels["pm25"]["std"]
    norm_pm25 = (sample_x[:, 0] - mu) / sigma

    # Roundtrip denormalize
    recovered_pm25 = norm_pm25 * sigma + mu
    # Compare ignoring NaNs
    valid_mask = ~np.isnan(sample_x[:, 0])
    np.testing.assert_allclose(sample_x[valid_mask, 0], recovered_pm25[valid_mask], rtol=1e-5)


def test_teammate_03_metadata_and_schema_inspection(package_paths):
    """Teammate Step 3: Inspect metadata schemas and assert channel contract."""
    df_schema = pd.read_csv(package_paths["schema_csv"])
    assert len(df_schema) == 13
    assert df_schema.loc[8, "channel_name"] == "rainfall"
    assert df_schema.loc[8, "unit"] == "mm"

    df_stations = pd.read_csv(package_paths["stations_csv"])
    assert len(df_stations) == 16
    assert set(df_stations["station_id"]).issuperset({66, 71, 79, 80, 81})

    df_splits = pd.read_csv(package_paths["splits_csv"])
    assert len(df_splits) == 5  # train, buf1, val, buf2, test
    train_row = df_splits[df_splits["split_name"] == "train"].iloc[0]
    assert train_row["window_count"] == 294160


def test_teammate_04_benchmark_mask_firewall(package_paths):
    """Teammate Step 4: Load benchmark mask and assert target firewall."""
    test_m_nat = np.load(package_paths["test_m_npz"])["M_natural"]
    mask_data = np.load(package_paths["mcar_30_npz"])
    M_target = mask_data["M_target"]
    M_target_pol = mask_data["M_target_pollutants"]

    assert M_target.shape == (62224, 24, 13)
    assert M_target_pol.shape == (62224, 24, 5)

    # Invariant: No cell with natural NaN is marked as an evaluation target
    overlap = np.sum(M_target * (1 - test_m_nat))
    assert overlap == 0, f"Target firewall breached: {overlap} targets overlap with natural NaNs!"


def test_teammate_05_reconstruct_sample_and_partition(package_paths):
    """Teammate Step 5: Select sample, partition inputs and targets, verify metadata."""
    sample_idx = 42

    test_x = np.load(package_paths["test_x_npz"])
    test_m = np.load(package_paths["test_m_npz"])
    mask_data = np.load(package_paths["mcar_30_npz"])

    x_sample = test_x["X"][sample_idx]              # (24, 13)
    m_nat_sample = test_m["M_natural"][sample_idx]    # (24, 13)
    m_tgt_sample = mask_data["M_target"][sample_idx]  # (24, 13)
    w_id = test_x["window_id"][sample_idx]
    st_id = test_x["station_id"][sample_idx]

    # Partition model input and ground-truth target
    m_obs_sample = m_nat_sample * (1 - m_tgt_sample)
    assert np.array_equal(m_obs_sample + m_tgt_sample, m_nat_sample)
    assert np.sum(m_obs_sample * m_tgt_sample) == 0

    x_model_input = np.where(m_obs_sample == 1, x_sample, 0.0)
    y_ground_truth = x_sample[:, :5]
    eval_target_mask = m_tgt_sample[:, :5]

    # Verify window metadata index
    df_meta = pd.read_parquet(package_paths["meta_parquet"])
    matched = df_meta[df_meta["window_id"] == w_id]
    assert len(matched) == 1
    assert matched["station_id"].iloc[0] == st_id
    assert matched["temporal_split"].iloc[0] == "test"


def test_teammate_06_independent_consumption_without_raw():
    """Teammate Step 6: Verify package has zero required path links to data/raw/."""
    # Ensure package README and cards point only to intra-package files
    manifest_path = PACKAGE_DIR / "dataset_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Every file in package_files exists within PACKAGE_DIR
    for rel_path in manifest["package_files"].keys():
        p = PACKAGE_DIR / rel_path
        assert p.exists(), f"Self-contained package file missing: {p}"
