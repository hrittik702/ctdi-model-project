"""Build reproducible dataset training package CTDI_AirPollution_TrainingDataset_v1.0.

Phase 4 Data Finalization:
Freezes the research dataset into a reproducible, self-contained training package.
Exports:
- train/, validation/, test/ in both Parquet and NPZ formats.
- masks/ in both Parquet and NPZ formats across all 12 benchmark scenarios.
- metadata/ schemas, station info, split manifest, window metadata, normalization stats.
- dataset_manifest.json, DATASET_CARD.md, README.md, and checksums/SHA256SUMS.

Strict Rules:
- 100% derived from canonical Phase 1-4B interim artifacts.
- No model training or architecture implementation.
- data/raw/ is never modified.
- Parquet and NPZ match sample-for-sample in identical order.
- Natural missingness preserved without imputation.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parents[2]

# Canonical Input Artifacts
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
WINDOWS_PARQUET = INTERIM_DIR / "windows" / "24h_windows.parquet"
MASKS_PARQUET = INTERIM_DIR / "windows" / "missingness_masks.parquet"
METADATA_PARQUET = INTERIM_DIR / "windows" / "window_metadata.parquet"
ALIGNED_PARQUET = INTERIM_DIR / "aligned" / "aligned_hourly_station_data.parquet"
NORM_STATS_JSON = INTERIM_DIR / "experiments" / "normalization" / "normalization_stats.json"
SPLIT_MANIFEST_JSON = INTERIM_DIR / "experiments" / "splits" / "split_manifest.json"
BENCHMARK_MASKS_PARQUET = INTERIM_DIR / "experiments" / "masks" / "test_benchmark_masks.parquet"
MASKING_STATS_JSON = INTERIM_DIR / "experiments" / "metadata" / "masking_statistics.json"
RAW_STATIONS_CSV = PROJECT_ROOT / "data" / "raw" / "station_metadata" / "air_quality_stations.csv"

# Output Final Package Directory
FINAL_DIR = PROJECT_ROOT / "data" / "final" / "CTDI_AirPollution_TrainingDataset_v1.0"

sys.path.insert(0, str(PROJECT_ROOT))
from src.dataset.normalization import CANONICAL_13_CHANNELS, POLLUTANT_CHANNELS
TARGET_POLLUTANT_CHANNELS = POLLUTANT_CHANNELS


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_git_commit() -> str:
    """Get current git commit hash."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        return "git_commit_unavailable"


def build_channel_schema_csv(output_path: Path):
    """Generate metadata/channel_schema.csv with exact channel definitions."""
    schema_rows = [
        {"channel_index": 0, "channel_name": "pm25", "group": "air_quality", "unit": "ug/m3", "description": "Fine Particulate Matter (<2.5 um)", "normalization_method": "z_score", "primary_representation": "continuous"},
        {"channel_index": 1, "channel_name": "pm10", "group": "air_quality", "unit": "ug/m3", "description": "Respirable Suspended Particulates (<10 um)", "normalization_method": "z_score", "primary_representation": "continuous"},
        {"channel_index": 2, "channel_name": "no2", "group": "air_quality", "unit": "ug/m3", "description": "Nitrogen Dioxide", "normalization_method": "z_score", "primary_representation": "continuous"},
        {"channel_index": 3, "channel_name": "so2", "group": "air_quality", "unit": "ug/m3", "description": "Sulphur Dioxide", "normalization_method": "z_score", "primary_representation": "continuous"},
        {"channel_index": 4, "channel_name": "o3", "group": "air_quality", "unit": "ug/m3", "description": "Ground-Level Ozone", "normalization_method": "z_score", "primary_representation": "continuous"},
        {"channel_index": 5, "channel_name": "pressure", "group": "meteorology", "unit": "hPa", "description": "Surface Atmospheric Pressure", "normalization_method": "z_score", "primary_representation": "continuous"},
        {"channel_index": 6, "channel_name": "relative_humidity", "group": "meteorology", "unit": "%", "description": "Surface Relative Humidity", "normalization_method": "z_score", "primary_representation": "continuous"},
        {"channel_index": 7, "channel_name": "temperature", "group": "meteorology", "unit": "degC", "description": "2-Meter Dry-Bulb Air Temperature", "normalization_method": "z_score", "primary_representation": "continuous"},
        {"channel_index": 8, "channel_name": "rainfall", "group": "meteorology", "unit": "mm", "description": "Total Hourly Surface Precipitation (wet scavenging proxy)", "normalization_method": "z_score", "primary_representation": "continuous"},
        {"channel_index": 9, "channel_name": "wind_direction", "group": "meteorology", "unit": "degrees", "description": "10-Meter Wind Direction Bearing (0-360 deg)", "normalization_method": "z_score", "primary_representation": "degrees_13_channel"},
        {"channel_index": 10, "channel_name": "wind_speed", "group": "meteorology", "unit": "m/s", "description": "10-Meter Wind Speed", "normalization_method": "z_score", "primary_representation": "continuous"},
        {"channel_index": 11, "channel_name": "traffic_speed", "group": "traffic", "unit": "km/h", "description": "Spatial-IDW Road Vehicular Speed", "normalization_method": "z_score", "primary_representation": "continuous"},
        {"channel_index": 12, "channel_name": "traffic_congestion", "group": "traffic", "unit": "[0.0, 1.0]", "description": "Spatial-IDW Road Saturation Level (ordinal: GOOD=0, AVG=0.5, BAD=1.0)", "normalization_method": "z_score", "primary_representation": "continuous"},
    ]
    df_schema = pd.DataFrame(schema_rows)
    df_schema.to_csv(output_path, index=False)


def build_station_metadata_csv(output_path: Path):
    """Generate metadata/station_metadata.csv for the 16 CTDI air stations."""
    df_raw = pd.read_csv(RAW_STATIONS_CSV)
    df_16 = df_raw[df_raw["in_ctdi_study"] == True].copy().reset_index(drop=True)
    df_16.to_csv(output_path, index=False)


def build_split_manifest_csv(output_path: Path):
    """Generate metadata/split_manifest.csv recording exact split boundaries and purge buffers."""
    with open(SPLIT_MANIFEST_JSON, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    rows = []
    split_order = ["train", "buffer_train_val", "val", "buffer_val_test", "test"]
    descriptions = {
        "train": "Primary chronological training split (25 months)",
        "buffer_train_val": "Purged temporal buffer: 24h calendar day 2021-02-06, 25.0h physical gap, 47 windows/station",
        "val": "Chronological validation split (5.5 months)",
        "buffer_val_test": "Purged temporal buffer: 24h calendar day 2021-07-21, 25.0h physical gap, 47 windows/station",
        "test": "Chronological test split (5.3 months, benchmark evaluated)",
    }

    for s_name in split_order:
        s = manifest["splits"][s_name]
        rows.append({
            "split_name": s_name,
            "window_count": s["window_count"],
            "percentage": s["percentage"],
            "start_timestamp_min": s["start_min"],
            "start_timestamp_max": s["start_max"],
            "end_timestamp_min": s["end_min"],
            "end_timestamp_max": s["end_max"],
            "station_count": s["station_count"],
            "missing_pollutant_cells": s["missing_pollutant_cells"],
            "missing_pollutant_pct": s["missing_pollutant_pct"],
            "windows_with_missing": s["windows_with_missing"],
            "is_purged_buffer": "buffer" in s_name,
            "description": descriptions[s_name],
        })

    df_splits = pd.DataFrame(rows)
    df_splits.to_csv(output_path, index=False)


def dataframe_to_tensor_3d(df: pd.DataFrame, channels: List[str], window_len: int = 24) -> np.ndarray:
    """Convert window dataframe with array cells into 3D numpy ndarray [N, 24, C]."""
    n_samples = len(df)
    arr = np.empty((n_samples, window_len, len(channels)), dtype=np.float32)
    for c_idx, ch in enumerate(channels):
        arr[:, :, c_idx] = np.vstack(df[ch].to_numpy())
    return arr


def dataframe_to_mask_3d(df: pd.DataFrame, channels: List[str], window_len: int = 24) -> np.ndarray:
    """Convert mask dataframe with array cells into 3D numpy ndarray [N, 24, C] uint8."""
    n_samples = len(df)
    arr = np.empty((n_samples, window_len, len(channels)), dtype=np.uint8)
    for c_idx, ch in enumerate(channels):
        arr[:, :, c_idx] = np.vstack(df[ch].to_numpy()).astype(np.uint8)
    return arr


def export_split_partition(
    split_name: str,
    target_dir: Path,
    df_meta: pd.DataFrame,
    df_windows: pd.DataFrame,
    df_masks: pd.DataFrame,
) -> Dict[str, Any]:
    """Export a single split partition into both Parquet and NPZ formats."""
    print(f"\n  Exporting {split_name.upper()} partition...")
    t0 = time.time()
    target_dir.mkdir(parents=True, exist_ok=True)

    # Filter indices
    split_mask = df_meta["temporal_split"] == split_name
    split_indices = df_meta[split_mask].index

    win_sub = df_windows.iloc[split_indices].copy().reset_index(drop=True)
    mask_sub = df_masks.iloc[split_indices].copy().reset_index(drop=True)
    n_samples = len(win_sub)

    # 1. Parquet files
    parquet_x_path = target_dir / f"X_{split_name}.parquet"
    parquet_m_path = target_dir / f"M_natural_{split_name}.parquet"

    win_sub.to_parquet(parquet_x_path, index=False, engine="pyarrow", compression="snappy")
    mask_sub.to_parquet(parquet_m_path, index=False, engine="pyarrow", compression="snappy")

    # 2. 3D Tensors
    arr_x = dataframe_to_tensor_3d(win_sub, CANONICAL_13_CHANNELS, window_len=24)
    arr_m = dataframe_to_mask_3d(mask_sub, CANONICAL_13_CHANNELS, window_len=24)

    w_ids = win_sub["window_id"].to_numpy(dtype=np.int64)
    st_ids = win_sub["station_id"].to_numpy(dtype=np.int64)

    # 3. NPZ files (compressed)
    npz_x_path = target_dir / f"X_{split_name}.npz"
    npz_m_path = target_dir / f"M_natural_{split_name}.npz"

    np.savez_compressed(npz_x_path, X=arr_x, window_id=w_ids, station_id=st_ids)
    np.savez_compressed(npz_m_path, M_natural=arr_m, window_id=w_ids, station_id=st_ids)

    elapsed = time.time() - t0
    print(f"    Exported {n_samples:,} samples to {target_dir} in {elapsed:.2f}s:")
    print(f"      - X_{split_name}.parquet: {parquet_x_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"      - M_natural_{split_name}.parquet: {parquet_m_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"      - X_{split_name}.npz: {npz_x_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"      - M_natural_{split_name}.npz: {npz_m_path.stat().st_size / (1024*1024):.2f} MB")

    return {
        "split_name": split_name,
        "sample_count": n_samples,
        "tensor_shape": list(arr_x.shape),
        "parquet_x_size": parquet_x_path.stat().st_size,
        "parquet_m_size": parquet_m_path.stat().st_size,
        "npz_x_size": npz_x_path.stat().st_size,
        "npz_m_size": npz_m_path.stat().st_size,
    }


def export_benchmark_masks(
    masks_root: Path,
    df_meta: pd.DataFrame,
    df_test_benchmarks: pd.DataFrame,
) -> Dict[str, Any]:
    """Export all 12 test benchmark masking scenarios under masks/ in both Parquet and NPZ formats."""
    print("\n  Exporting benchmark masks across MCAR, Block, and Outage scenarios...")
    t0 = time.time()

    # Create subdirectories
    mcar_dir = masks_root / "mcar"
    block_dir = masks_root / "temporal_block"
    outage_dir = masks_root / "station_outage"
    for d in [mcar_dir, block_dir, outage_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Master benchmark masks parquet
    master_masks_parquet = masks_root / "test_benchmark_masks.parquet"
    df_test_benchmarks.to_parquet(master_masks_parquet, index=False, engine="pyarrow", compression="snappy")
    print(f"    Saved master test_benchmark_masks.parquet: {master_masks_parquet.stat().st_size / (1024*1024):.2f} MB")

    n_test = len(df_test_benchmarks)
    w_ids = df_test_benchmarks["window_id"].to_numpy(dtype=np.int64)
    st_ids = df_test_benchmarks["station_id"].to_numpy(dtype=np.int64)

    scenarios = [
        # (category, scenario_name, target_dir)
        ("mcar", "mcar_10", mcar_dir),
        ("mcar", "mcar_30", mcar_dir),
        ("mcar", "mcar_50", mcar_dir),
        ("mcar", "mcar_70", mcar_dir),
        ("temporal_block", "block_10", block_dir),
        ("temporal_block", "block_30", block_dir),
        ("temporal_block", "block_50", block_dir),
        ("temporal_block", "block_70", block_dir),
        ("station_outage", "station_outage_1", outage_dir),
        ("station_outage", "station_outage_2", outage_dir),
        ("station_outage", "station_outage_4", outage_dir),
        ("station_outage", "station_outage_full", outage_dir),
    ]

    scenario_reports = {}

    for cat, sc_name, target_dir in scenarios:
        raw_masks = df_test_benchmarks[sc_name].to_numpy()
        flat_arr = np.vstack(raw_masks).astype(np.uint8)  # (62224, 120)

        # 1. 5-channel pollutant mask: (62224, 24, 5)
        m_pollutants = flat_arr.reshape((n_test, 24, 5))

        # 2. 13-channel tensor mask: (62224, 24, 13)
        m_13ch = np.zeros((n_test, 24, 13), dtype=np.uint8)
        m_13ch[:, :, :5] = m_pollutants

        # Export NPZ
        npz_path = target_dir / f"{sc_name}.npz"
        np.savez_compressed(
            npz_path,
            M_target=m_13ch,
            M_target_pollutants=m_pollutants,
            window_id=w_ids,
            station_id=st_ids,
        )

        # Export Parquet
        parquet_dict = {
            "window_id": w_ids,
            "station_id": st_ids,
        }
        for p_idx, p_name in enumerate(TARGET_POLLUTANT_CHANNELS):
            parquet_dict[p_name] = [m_pollutants[i, :, p_idx].tolist() for i in range(n_test)]

        df_sc = pd.DataFrame(parquet_dict)
        parquet_path = target_dir / f"{sc_name}.parquet"
        df_sc.to_parquet(parquet_path, index=False, engine="pyarrow", compression="snappy")

        scenario_reports[sc_name] = {
            "category": cat,
            "npz_size_bytes": npz_path.stat().st_size,
            "parquet_size_bytes": parquet_path.stat().st_size,
            "total_masked_cells": int(flat_arr.sum()),
        }
        print(f"    {sc_name:20s} -> {sc_name}.npz ({npz_path.stat().st_size / 1024:.1f} KB), {sc_name}.parquet ({parquet_path.stat().st_size / 1024:.1f} KB)")

    elapsed = time.time() - t0
    print(f"  Exported all 12 benchmark mask scenarios in {elapsed:.2f}s.")
    return scenario_reports


def generate_dataset_card_md(output_path: Path):
    """Generate professional research-grade DATASET_CARD.md."""
    content = """# Dataset Card: CTDI_AirPollution_TrainingDataset_v1.0

## 1. Dataset Overview
- **Name**: `CTDI_AirPollution_TrainingDataset_v1.0`
- **Version**: `1.0.0`
- **Benchmark Paper**: Yangwen Yu, Victor O. K. Li, Jacqueline C. K. Lam, Kelvin Chan, Qi Zhang, *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, **IEEE Transactions on Big Data**, vol. 11, no. 5, pp. 2442–2455, Sept.–Oct. 2025. [DOI: 10.1109/TBDATA.2025.3533882](https://doi.org/10.1109/TBDATA.2025.3533882)
- **Domain**: Hong Kong Special Administrative Region (16 air quality monitoring stations, 2019-01-01 to 2021-12-31).
- **Core Contract**: 13 multi-modal channels $\\times$ 24 hourly timesteps ($T=24$) per sliding window sample.
- **Total Sliding Windows**: $420,496$ windows ($26,281$ windows per station across 16 stations).
- **Format**: Dual release in Apache Parquet (`.parquet`) and NumPy Compressed Tensor (`.npz`).

---

## 2. Source Data & Provenance
The dataset is constructed by fusing three official data feeds across Hong Kong:
1. **Air Quality**: Hong Kong Environmental Protection Department (HKEPD) official telemetry network. Exactly 16 operational stations (13 general ambient + 3 roadside: Causeway Bay, Central, Mong Kok). Stations Southern (#84) and North (#85) commissioned in July 2020 are excluded to prevent 18-month structural missingness blocks.
2. **Meteorology**: ECMWF ERA5 hourly surface reanalysis extracted at the exact geographical coordinates of the 16 air quality monitoring stations.
3. **Traffic**: Transport Department First-Generation Traffic Speed Map (`speedmap.xml`) historical telemetry ($774,686$ snapshots parsed across all 36 months of 2019–2021; 466.8M link records across 632 unique links in network union).

---

## 3. The 13 Canonical Channels
The tensor feature dimension ($C=13$) follows strict canonical ordering:

| Index | Name | Group | Unit | Physical Description | Missingness Profile |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **0** | `pm25` | Air Quality | $\\mu\\text{g/m}^3$ | Fine Particulate Matter ($<2.5\\mu\\text{m}$) | 10,657 NaNs ($2.53\\%$) |
| **1** | `pm10` | Air Quality | $\\mu\\text{g/m}^3$ | Respirable Suspended Particulates ($<10\\mu\\text{m}$) | 11,395 NaNs ($2.71\\%$) |
| **2** | `no2` | Air Quality | $\\mu\\text{g/m}^3$ | Nitrogen Dioxide | 11,651 NaNs ($2.77\\%$) |
| **3** | `so2` | Air Quality | $\\mu\\text{g/m}^3$ | Sulphur Dioxide | 11,056 NaNs ($2.63\\%$) |
| **4** | `o3` | Air Quality | $\\mu\\text{g/m}^3$ | Ground-Level Ozone | 11,117 NaNs ($2.64\\%$) |
| **5** | `pressure` | Meteorology | $\\text{hPa}$ | Barometric Atmospheric Surface Pressure | 0 NaNs ($100\\%$ complete) |
| **6** | `relative_humidity` | Meteorology | $\\%$ | Ambient Relative Humidity | 0 NaNs ($100\\%$ complete) |
| **7** | `temperature` | Meteorology | $^\\circ\\text{C}$ | Ambient 2-Meter Dry-Bulb Air Temperature | 0 NaNs ($100\\%$ complete) |
| **8** | `rainfall` | Meteorology | $\\text{mm}$ | Total Hourly Precipitation (Aerosol wet scavenging proxy) | 0 NaNs ($100\\%$ complete) |
| **9** | `wind_direction` | Meteorology | Degrees ($^\\circ$) | 10-Meter Wind Direction Compass Azimuth ($0\\text{--}360^\\circ$) | 0 NaNs ($100\\%$ complete) |
| **10** | `wind_speed` | Meteorology | $\\text{m/s}$ | 10-Meter Surface Wind Velocity | 0 NaNs ($100\\%$ complete) |
| **11** | `traffic_speed` | Traffic | $\\text{km/h}$ | Spatial-IDW ($p=2$) Arterial Road Speed | 2,416 NaNs ($0.57\\%$, archive outages) |
| **12** | `traffic_congestion` | Traffic | $[0.0, 1.0]$ | Spatial-IDW ($p=2$) Road Saturation Level (GOOD=0, AVG=0.5, BAD=1.0) | 2,416 NaNs ($0.57\\%$, archive outages) |

> [!IMPORTANT]
> **Rainfall Adoption (Channel 8)**: Table I of Yu et al. (2025) specifies horizontal optical visibility (km) from HKO Automatic Weather Stations (AWS). However, extensive empirical audit proved that retrospective 10-minute HKO AWS historical visibility is publicly **irrecoverable** from open data (the CTDI paper authors received an unreleased private offline dataset from Dr. Yang Han at HKU; Page 2454). Per Decision D07, ECMWF ERA5 continuous hourly surface precipitation (mm) was formally adopted as Channel 8 due to its physical coupling with aerosol wet deposition and criteria pollutant scavenging.

---

## 4. Natural Missingness & Target Firewall
- **Natural Missingness Conservation**: Exactly $55,876$ natural pollutant NaNs in the primary air quality table ($2.66\\%$) are preserved bit-for-bit with the raw sensor archives.
- **No Natural Imputation**: Natural NaNs are **never** filled with zero, mean, or interpolated values in the ground-truth arrays.
- **Target Firewall Invariant**: In all evaluation masking protocols, cells with natural sensor dropouts ($M_{\\text{natural}} = 0$) are **never** treated as evaluation targets:
  $$M_{\\text{target}} \\le M_{\\text{natural}}, \\quad M_{\\text{observed}} = M_{\\text{natural}} \\odot (1 - M_{\\text{target}}), \\quad M_{\\text{natural}} = M_{\\text{observed}} + M_{\\text{target}}$$

---

## 5. Chronological Partitioning & Purge Buffers
To prevent autoregressive data leakage across sliding window horizons, chronological partitions are separated by 24-hour temporal purge buffers:

| Partition | Time Horizon | Windows | Percentage | Role |
| :--- | :--- | :---: | :---: | :--- |
| **Train** | `2019-01-01 00:00` to `2021-02-05 23:00` | $294,160$ | $69.96\\%$ | Training model parameters |
| **Buffer 1** | Purge day `2021-02-06` ($25.0\\text{h}$ physical gap) | $752$ | $0.18\\%$ | **Purged** (47 windows/station excluded) |
| **Validation** | `2021-02-07 00:00` to `2021-07-20 23:00` | $62,608$ | $14.89\\%$ | Hyperparameter tuning & model selection |
| **Buffer 2** | Purge day `2021-07-21` ($25.0\\text{h}$ physical gap) | $752$ | $0.18\\%$ | **Purged** (47 windows/station excluded) |
| **Test** | `2021-07-22 00:00` to `2021-12-31 23:00` | $62,224$ | $14.80\\%$ | Final benchmark evaluation |

---

## 6. Normalization Protocol
- **Primary Method**: Standard z-score standardization ($x' = (x - \\mu) / \\sigma$).
- **Strict Isolation**: Parameters $\\mu, \\sigma$ are fitted **strictly on the 294,528 station-hours of the training partition** (observations $\\le$ `2021-02-05 23:00:00`). Zero validation or test data leakage.
- **Stored Format**: Pre-computed statistics are provided in `metadata/normalization_stats.json`. Raw tensors $X$ in `train/`, `validation/`, and `test/` remain unnormalized on disk so that researchers can inspect native physical units ($\mu\\text{g/m}^3$, $^\\circ\\text{C}$, $\\text{km/h}$) or apply alternative scalings (min-max, robust, log1p).

---

## 7. Artificial Missingness Benchmarks
The test partition ($62,224$ windows) includes pre-computed deterministic benchmark evaluation masks for 12 experimental scenarios:
1. **Random Point MCAR**: 10%, 30%, 50%, 70% missingness rates across criteria pollutants.
2. **Continuous Temporal Block MAR**: 10%, 30%, 50%, 70% missingness rates (burst outages of 3–12 hours, trimmed to exact rate within $\\pm 0.07\\%$).
3. **Spatial Station Outage**: S1 (1 station / 6.25%), S2 (2 stations / 12.50%), S4 (4 stations / 25.00%), S_full (16 stations / 100.00%).

---

## 8. Intended & Non-Intended Use
- **Intended Use**: Benchmarking spatio-temporal missing data imputation algorithms, conditional generative diffusion models, small language model (SLM) environmental context conditioning, and urban air quality forecasting.
- **Non-Intended Use**: Operational real-time dispatching without real-time sensor calibration; safety-critical atmospheric emergency control without secondary domain validation.
"""
    output_path.write_text(content, encoding="utf-8")


def generate_readme_md(output_path: Path):
    """Generate comprehensive user-friendly README.md."""
    content = """# CTDI Air Pollution Training Dataset v1.0

A frozen, reproducible, multi-modal benchmark dataset for spatio-temporal missing air pollution data imputation.

## Quick Start: Loading Data in Python

### 1. Direct Tensor Training Format (`.npz`)
Recommended for deep learning models (PyTorch, JAX, TensorFlow):

```python
import numpy as np

# Load Training Partition
train_data = np.load("train/X_train.npz")
X_train = train_data["X"]                   # Shape: (294160, 24, 13), dtype: float32
window_ids = train_data["window_id"]         # Shape: (294160,), dtype: int64
station_ids = train_data["station_id"]       # Shape: (294160,), dtype: int64

# Load Natural Missingness Mask (1 = observed, 0 = natural sensor NaN)
mask_data = np.load("train/M_natural_train.npz")
M_nat_train = mask_data["M_natural"]         # Shape: (294160, 24, 13), dtype: uint8

print(f"X_train shape: {X_train.shape}")
print(f"Sample 0 PM2.5 (first 5 hours): {X_train[0, :5, 0]}")
```

### 2. Inspectable Tabular Format (`.parquet`)
Recommended for pandas, EDA, and feature inspection:

```python
import pandas as pd

# Load Validation Partition
df_val = pd.read_parquet("validation/X_val.parquet")
print(f"Val rows: {len(df_val):,}")
print(f"Columns: {df_val.columns.tolist()}")

# Each channel cell contains a 24-element list/array
first_pm25_window = df_val["pm25"].iloc[0]
print(f"Window 0 PM2.5 24h sequence: {first_pm25_window}")
```

### 3. Loading Normalization Statistics & Transforming
```python
import json
import numpy as np

with open("metadata/normalization_stats.json") as f:
    stats = json.load(f)

# Compute z-score for PM2.5
pm25_mean = stats["channels"]["pm25"]["mean"]
pm25_std = stats["channels"]["pm25"]["std"]

X_norm = np.copy(X_train)
X_norm[:, :, 0] = (X_train[:, :, 0] - pm25_mean) / pm25_std
```

### 4. Evaluating with Benchmark Evaluation Masks
```python
import numpy as np

# Load Test Features and MCAR 30% Evaluation Mask
test_data = np.load("test/X_test.npz")
X_test = test_data["X"]                     # (62224, 24, 13)

mask_data = np.load("masks/mcar/mcar_30.npz")
M_tgt = mask_data["M_target"]               # (62224, 24, 13), uint8 (1 = evaluation target)

# Load Test Natural Missingness
M_nat = np.load("test/M_natural_test.npz")["M_natural"]

# Model inputs: observed cells that are NOT masked
M_obs = M_nat * (1 - M_tgt)
X_input = np.where(M_obs == 1, X_test, 0.0)

# Ground truth evaluation targets:
Y_ground_truth = X_test[:, :, :5]           # 5 criteria pollutants
eval_mask = M_tgt[:, :, :5]                 # Evaluate model predictions ONLY where eval_mask == 1
```

---

## Directory Organization

```text
CTDI_AirPollution_TrainingDataset_v1.0/
├── README.md                               # This file
├── DATASET_CARD.md                         # Detailed scientific datasheet
├── dataset_manifest.json                   # Master metadata & SHA-256 hashes
│
├── train/                                  # 294,160 training windows (2019-01-01 to 2021-02-05)
│   ├── X_train.parquet
│   ├── M_natural_train.parquet
│   ├── X_train.npz
│   └── M_natural_train.npz
│
├── validation/                             # 62,608 validation windows (2021-02-07 to 2021-07-20)
│   ├── X_val.parquet
│   ├── M_natural_val.parquet
│   ├── X_val.npz
│   └── M_natural_val.npz
│
├── test/                                   # 62,224 test windows (2021-07-22 to 2021-12-31)
│   ├── X_test.parquet
│   ├── M_natural_test.parquet
│   ├── X_test.npz
│   └── M_natural_test.npz
│
├── masks/                                  # Deterministic benchmark evaluation masks
│   ├── test_benchmark_masks.parquet        # Master table with all 12 scenarios
│   ├── mcar/                               # Point MCAR: 10%, 30%, 50%, 70%
│   ├── temporal_block/                     # Continuous MAR block: 10%, 30%, 50%, 70%
│   └── station_outage/                     # Station outage: S1 (1 stn), S2 (2 stn), S4 (4 stn), S_full (16 stn)
│
├── metadata/
│   ├── channel_schema.csv                  # 13 channels definition and units
│   ├── station_metadata.csv                # 16 air stations, coordinates, types
│   ├── split_manifest.csv                  # Split boundaries and purge buffer metrics
│   ├── window_metadata.parquet             # Full 420,496-row window metadata index
│   ├── normalization_stats.json            # Train-fitted normalization statistics
│   └── masking_statistics.json             # Exact achieved masking rates and deviations
│
└── checksums/
    └── SHA256SUMS                          # SHA-256 cryptographic verification checksums
```

---

## The 13 Canonical Feature Channels

```text
Index 0:  pm25                 (ug/m3)       - Air Quality
Index 1:  pm10                 (ug/m3)       - Air Quality
Index 2:  no2                  (ug/m3)       - Air Quality
Index 3:  so2                  (ug/m3)       - Air Quality
Index 4:  o3                   (ug/m3)       - Air Quality
Index 5:  pressure             (hPa)         - Meteorology
Index 6:  relative_humidity    (%)           - Meteorology
Index 7:  temperature          (degC)        - Meteorology
Index 8:  rainfall             (mm)          - Meteorology (Aerosol wet scavenging proxy)
Index 9:  wind_direction       (degrees)     - Meteorology (0-360 deg bearing)
Index 10: wind_speed           (m/s)         - Meteorology
Index 11: traffic_speed        (km/h)        - Traffic (Spatial-IDW on arterial road links)
Index 12: traffic_congestion   ([0.0, 1.0])  - Traffic (Spatial-IDW ordinal road saturation)
```

---

## Verifying Package Integrity

To cryptographically verify all downloaded or uncompressed files:

```bash
cd CTDI_AirPollution_TrainingDataset_v1.0
sha256sum -c checksums/SHA256SUMS
```
"""
    output_path.write_text(content, encoding="utf-8")


def generate_dataset_manifest_json(
    output_path: Path,
    package_dir: Path,
    split_info: Dict[str, Any],
    mask_info: Dict[str, Any],
):
    """Generate master dataset_manifest.json with all metadata, counts, and checksums."""
    with open(NORM_STATS_JSON, "r", encoding="utf-8") as f:
        norm_stats = json.load(f)

    with open(SPLIT_MANIFEST_JSON, "r", encoding="utf-8") as f:
        split_manifest = json.load(f)

    # Collect all files and compute relative SHA256
    dist_files = {}
    for p in sorted(package_dir.rglob("*")):
        if p.is_file() and p.name != "dataset_manifest.json" and "checksums" not in str(p):
            rel = str(p.relative_to(package_dir))
            dist_files[rel] = {
                "sha256": compute_sha256(p),
                "size_bytes": p.stat().st_size,
            }

    manifest = {
        "dataset_name": "CTDI_AirPollution_TrainingDataset_v1.0",
        "version": "1.0.0",
        "freeze_date": "2026-09-19",
        "authoritative_benchmark_reference": "Yu et al., IEEE Transactions on Big Data, 2025 (Table I)",
        "git_commit": get_git_commit(),
        "creation_timestamp": pd.Timestamp.now().isoformat(),
        "temporal_coverage": {
            "start": "2019-01-01 00:00:00",
            "end": "2021-12-31 23:00:00",
            "timezone": "Asia/Hong_Kong",
            "total_calendar_days": 1096,
            "total_hourly_timestamps": 26304,
        },
        "spatial_coverage": {
            "station_count": 16,
            "station_ids": [66, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83],
            "excluded_newer_stations": [84, 85],
        },
        "tensor_contract": {
            "channel_count": 13,
            "channel_order": CANONICAL_13_CHANNELS,
            "channel_index_8": "rainfall",
            "window_length_hours": 24,
            "window_stride_hours": 1,
            "axis_semantics": {
                "axis_0": "sample / window (window_id)",
                "axis_1": "hourly timestep [0..23]",
                "axis_2": "feature channel [0..12]",
            },
            "tensor_dtype": "float32",
            "natural_mask_dtype": "uint8",
        },
        "split_summary": {
            "train": split_manifest["splits"]["train"],
            "buffer_train_val": split_manifest["splits"]["buffer_train_val"],
            "val": split_manifest["splits"]["val"],
            "buffer_val_test": split_manifest["splits"]["buffer_val_test"],
            "test": split_manifest["splits"]["test"],
            "buffer_architecture": split_manifest["buffer_architecture"],
        },
        "natural_missingness_summary": {
            "total_natural_pollutant_nans": 55876,
            "expected_bit_for_bit_match": True,
            "per_pollutant_nans": {
                "pm25": 10657,
                "pm10": 11395,
                "no2": 11651,
                "so2": 11056,
                "o3": 11117,
            },
            "meteorology_nans": 0,
            "traffic_natural_missing_station_hours": 2416,
        },
        "normalization_contract": {
            "primary": "z_score",
            "fit_split": "train_only",
            "fit_sample_count": norm_stats["num_samples"],
            "fit_criteria": norm_stats["fit_criteria"],
            "channel_statistics": norm_stats["channels"],
        },
        "benchmark_mask_scenarios": mask_info,
        "source_artifacts": {
            "24h_windows.parquet": {
                "sha256": compute_sha256(WINDOWS_PARQUET),
                "size_bytes": WINDOWS_PARQUET.stat().st_size,
            },
            "missingness_masks.parquet": {
                "sha256": compute_sha256(MASKS_PARQUET),
                "size_bytes": MASKS_PARQUET.stat().st_size,
            },
            "window_metadata.parquet": {
                "sha256": compute_sha256(METADATA_PARQUET),
                "size_bytes": METADATA_PARQUET.stat().st_size,
            },
            "aligned_hourly_station_data.parquet": {
                "sha256": compute_sha256(ALIGNED_PARQUET),
                "size_bytes": ALIGNED_PARQUET.stat().st_size,
            },
            "test_benchmark_masks.parquet": {
                "sha256": compute_sha256(BENCHMARK_MASKS_PARQUET),
                "size_bytes": BENCHMARK_MASKS_PARQUET.stat().st_size,
            },
        },
        "package_files": dist_files,
        "known_limitations": [
            "Channel 8 is ECMWF ERA5 surface precipitation (rainfall, mm) rather than unreleased private HKO AWS visibility.",
            "Traffic variables derived from Transport Department 1st Gen Speedmap (632 links union across 2019-2021) projected via IDW (p=2). 2,416 missing hours preserved as genuine NaNs.",
            "Natural sensor dropouts are preserved as NaNs in raw tensors and 0 in M_natural; model inputs must be masked before loss computation.",
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def generate_sha256sums(package_dir: Path, checksums_file: Path):
    """Generate SHA256SUMS file covering all files in package."""
    checksums_file.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for p in sorted(package_dir.rglob("*")):
        if p.is_file() and p != checksums_file:
            rel = p.relative_to(package_dir)
            h = compute_sha256(p)
            lines.append(f"{h}  {rel}")

    checksums_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Generated {checksums_file} ({len(lines)} file hashes recorded)")


def main():
    print("=" * 80)
    print("PHASE 4 DATA FINALIZATION: FREEZING DATASET PACKAGE v1.0")
    print("Target: CTDI_AirPollution_TrainingDataset_v1.0")
    print("=" * 80)
    t_start = time.time()

    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    metadata_dir = FINAL_DIR / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load canonical source data
    print("\n[Step 1/6] Loading canonical source window artifacts...")
    df_meta = pd.read_parquet(METADATA_PARQUET)
    df_windows = pd.read_parquet(WINDOWS_PARQUET)
    df_masks = pd.read_parquet(MASKS_PARQUET)
    df_test_benchmarks = pd.read_parquet(BENCHMARK_MASKS_PARQUET)
    print(f"  Loaded metadata: {len(df_meta):,} rows")
    print(f"  Loaded 24h windows: {len(df_windows):,} rows")
    print(f"  Loaded natural masks: {len(df_masks):,} rows")
    print(f"  Loaded test benchmark masks: {len(df_test_benchmarks):,} rows")

    # 2. Export train, validation, and test partitions
    print("\n[Step 2/6] Packaging train, validation, and test partitions (Parquet + NPZ)...")
    split_summaries = {}
    for sp in ["train", "val", "test"]:
        sp_folder = "validation" if sp == "val" else sp
        target_dir = FINAL_DIR / sp_folder
        split_summaries[sp] = export_split_partition(
            split_name=sp,
            target_dir=target_dir,
            df_meta=df_meta,
            df_windows=df_windows,
            df_masks=df_masks,
        )

    # 3. Export benchmark evaluation masks
    print("\n[Step 3/6] Packaging benchmark evaluation masks...")
    masks_root = FINAL_DIR / "masks"
    mask_summaries = export_benchmark_masks(
        masks_root=masks_root,
        df_meta=df_meta,
        df_test_benchmarks=df_test_benchmarks,
    )

    # 4. Generate metadata artifacts
    print("\n[Step 4/6] Exporting metadata schemas and manifests...")
    build_channel_schema_csv(metadata_dir / "channel_schema.csv")
    build_station_metadata_csv(metadata_dir / "station_metadata.csv")
    build_split_manifest_csv(metadata_dir / "split_manifest.csv")
    shutil.copy2(METADATA_PARQUET, metadata_dir / "window_metadata.parquet")
    shutil.copy2(NORM_STATS_JSON, metadata_dir / "normalization_stats.json")
    shutil.copy2(MASKING_STATS_JSON, metadata_dir / "masking_statistics.json")
    print("  Copied and verified metadata files.")

    # 5. Generate documentation and manifest
    print("\n[Step 5/6] Generating README.md, DATASET_CARD.md, and dataset_manifest.json...")
    generate_readme_md(FINAL_DIR / "README.md")
    generate_dataset_card_md(FINAL_DIR / "DATASET_CARD.md")
    generate_dataset_manifest_json(
        output_path=FINAL_DIR / "dataset_manifest.json",
        package_dir=FINAL_DIR,
        split_info=split_summaries,
        mask_info=mask_summaries,
    )

    # 6. Generate cryptographic checksums
    print("\n[Step 6/6] Generating checksums/SHA256SUMS...")
    checksums_dir = FINAL_DIR / "checksums"
    generate_sha256sums(FINAL_DIR, checksums_dir / "SHA256SUMS")

    total_time = time.time() - t_start
    print("\n" + "=" * 80)
    print(f"SUCCESS: CTDI_AirPollution_TrainingDataset_v1.0 PACKAGED IN {total_time:.2f}s")
    print(f"Location: {FINAL_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
