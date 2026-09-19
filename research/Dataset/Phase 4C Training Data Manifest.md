# Phase 4C Training Data Manifest

**Dataset Identity**: CTDI Air Pollution Training Dataset v1.0  
**Version**: 1.0.0 (Frozen & Checksummed)  
**Creation Date**: 2026-09-19  
**Status**: Canonical Training Baseline for Phase 4C Model Development  
**Repository Branch Baseline**: `main` (commit `4e6a72d43198080a0cfeea1903d1dcde2ec8d4ca`)

---

## 1. Executive Summary & Purpose

This document provides the definitive specification, tensor contract, normalization protocol, and file inventory required for **Phase 4C: Model Development & Training (CTDI Architecture)**.

To maintain maximum computational efficiency and eliminate Git repository bloat, Phase 4C establishes a clear separation between:
1. **Required Training Data**: The minimal set of pre-shaped 3D tensors (`.npz`) and metadata necessary to train, validate, and test CTDI models (~20.5 MB).
2. **Evaluation-Only Artifacts**: Benchmark evaluation masks used exclusively for post-training test performance quantification.
3. **Local-Only Artifacts**: Redundant 2D columnar tabular representations (`.parquet`), inspection notebooks, raw sensor data, and intermediate pipeline stages that remain preserved locally but are excluded from minimal training distribution.

---

## 2. Dataset Identity & Spatial-Temporal Specifications

### 2.1 Spatial Topology
- **Network**: 16 air quality monitoring stations operated by the Hong Kong Environmental Protection Department (EPD).
- **Coverage**: 13 General Ambient Stations and 3 Roadside Urban Stations.
- **Station List**:
  1. Central/Western (`CW`) - General
  2. Eastern (`EA`) - General
  3. Kwun Tong (`KT`) - General
  4. Sham Shui Po (`SSP`) - General
  5. Kwai Chung (`KC`) - General
  6. Tsuen Wan (`TW`) - General
  7. Tseung Kwan O (`TKO`) - General
  8. Yuen Long (`YL`) - General
  9. Tuen Mun (`TM`) - General
  10. Tung Chung (`TC`) - General
  11. Tai Po (`TP`) - General
  12. Sha Tin (`ST`) - General
  13. North (`NT`) - General
  14. Causeway Bay (`CB`) - Roadside
  15. Central (`CL`) - Roadside
  16. Mong Kok (`MK`) - Roadside
- **Spatial Geometry**: Station coordinates, network adjacency matrix, and pairwise Euclidean distances are defined in `metadata/station_metadata.csv`.

### 2.2 Temporal Grid & Windowing
- **Temporal Horizon**: 2019-01-01 00:00:00 to 2021-12-31 23:00:00 (3 continuous calendar years; 26,304 consecutive hours per station).
- **Total Physical Station-Hours**: $26,304 \times 16 = 420,864$ station-hours.
- **Window Formulation**: Sliding 24-hour temporal windows ($T = 24$) sampled with a step stride of 1 hour ($S = 1$).
- **Total Windows Generated**: $420,864 - 16 \times (24 - 1) = 419,496$ windows across 16 stations.

### 2.3 Chronological Partitioning & Purged Buffers
To completely eliminate temporal data leakage between partitions, 24-hour physical calendar buffers (plus 1-hour physical gap, yielding 25.0h total gap) were purged between splits:

| Partition | Start Timestamp (UTC+8) | End Timestamp (UTC+8) | Window Count | Percentage | Missing Pollutant % | Role in Phase 4C |
|:---|:---|:---|---:|---:|---:|:---|
| **Train** | 2019-01-01 00:00:00 | 2021-02-05 23:00:00 | 294,160 | 69.96% | 2.57% | Model parameter optimization |
| *Purged Buffer 1* | 2021-02-05 01:00:00 | 2021-02-07 22:00:00 | 752 | 0.18% | 1.41% | *Discarded to prevent leakage* |
| **Validation** | 2021-02-07 00:00:00 | 2021-07-20 23:00:00 | 62,608 | 14.89% | 2.96% | Hyperparameter tuning & early stopping |
| *Purged Buffer 2* | 2021-07-20 01:00:00 | 2021-07-22 22:00:00 | 752 | 0.18% | 3.71% | *Discarded to prevent leakage* |
| **Test** | 2021-07-22 00:00:00 | 2021-12-31 23:00:00 | 62,224 | 14.80% | 2.75% | Final benchmark evaluation |
| **Total** | **2019-01-01 00:00:00** | **2021-12-31 23:00:00** | **419,496** | **100.00%** | **2.66%** | Complete Frozen Corpus |

---

## 3. Channel Schema & Tensor Ordering

The dataset models 13 aligned continuous spatiotemporal channels ($C = 13$). Every sample tensor preserves strict column ordering:

| Channel Index | Channel Name | Category | Physical Unit | Description | Primary Representation | Missingness Type |
|:---:|:---|:---|:---|:---|:---|:---|
| **0** | `pm25` | Air Quality | $\mu g/m^3$ | Fine Particulate Matter ($<2.5\mu m$) | Continuous | Natural sensor dropout |
| **1** | `pm10` | Air Quality | $\mu g/m^3$ | Respirable Suspended Particulates ($<10\mu m$) | Continuous | Natural sensor dropout |
| **2** | `no2` | Air Quality | $\mu g/m^3$ | Nitrogen Dioxide | Continuous | Natural sensor dropout |
| **3** | `so2` | Air Quality | $\mu g/m^3$ | Sulphur Dioxide | Continuous | Natural sensor dropout |
| **4** | `o3` | Air Quality | $\mu g/m^3$ | Ground-Level Ozone | Continuous | Natural sensor dropout |
| **5** | `pressure` | Meteorology | $hPa$ | Surface Atmospheric Pressure | Continuous | Complete (ERA5 reanalysis) |
| **6** | `relative_humidity` | Meteorology | $\%$ | Surface Relative Humidity | Continuous | Complete (ERA5 reanalysis) |
| **7** | `temperature` | Meteorology | $^\circ C$ | 2-Meter Dry-Bulb Air Temperature | Continuous | Complete (ERA5 reanalysis) |
| **8** | `rainfall` | Meteorology | $mm$ | Total Hourly Surface Precipitation | Continuous | Complete (ERA5 reanalysis) |
| **9** | `wind_direction` | Meteorology | $^\circ$ | 10-Meter Wind Bearing ($0^\circ-360^\circ$) | Continuous degrees | Complete (ERA5 reanalysis) |
| **10** | `wind_speed` | Meteorology | $m/s$ | 10-Meter Wind Speed | Continuous | Complete (ERA5 reanalysis) |
| **11** | `traffic_speed` | Traffic | $km/h$ | Spatial-IDW Vehicular Speed | Continuous | Sensor outage preserved |
| **12** | `traffic_congestion`| Traffic | $[0.0, 1.0]$ | Spatial-IDW Road Saturation Level | Continuous | Sensor outage preserved |

---

## 4. Tensor Contract & Data Representation

### 4.1 In-Memory Tensor Specification
During PyTorch / JAX data loading in Phase 4C, each split is represented as paired tensors:
- **Observation Tensor $X$**:
  - **Shape**: $(N, T, C) = (N, 24, 13)$
  - **Data Type**: `float32` (single precision IEEE 754)
  - **Native Values**: Physical unnormalized values as recorded or derived.
  - **Missing Values**: Represented strictly as IEEE 754 `np.nan` in raw storage; imputed with 0.0 or mean after applying mask in model pipeline.
- **Natural Observation Mask $M_{natural}$**:
  - **Shape**: $(N, T, C) = (N, 24, 13)$
  - **Data Type**: `uint8` (binary indicator: `1 = observed`, `0 = missing`)
  - **Semantics**: Indicates ground truth observation status. Loss functions and metric evaluators MUST mask unobserved entries using $M_{natural} \odot M_{eval}$.

### 4.2 Storage Format Comparison: NPZ vs Parquet

| Metric | Pre-shaped Tensor (`.npz`) | Tabular Columnar (`.parquet`) | Decision for Phase 4C |
|:---|:---|:---|:---|
| **Storage Layout** | 3D array `(N, 24, 13)` | 2D flattened table `(N*24, 13)` | **NPZ is Primary for Model Training** |
| **Train Split Size** | 10.59 MB (`X_train.npz`) | 44.72 MB (`X_train.parquet`) | **NPZ is 76.3% smaller** |
| **Load Overhead** | Zero-copy / direct memory map (`np.load`) | Requires columnar decompression + reshape | **NPZ loads ~8x faster** |
| **Git Tracking** | Fits comfortably under 50 MB threshold | Nears 50 MB warning limit (44.7 MB) | **NPZ requires no Git LFS** |
| **Loss of Precision** | None (`float32` exact bitwise) | None (Parquet snappy `float32`) | Identical numerical fidelity |

**Phase 4C Rule**: The PyTorch/ML data loaders (`Dataset`, `DataLoader`) MUST directly load the `.npz` files (`X_*.npz` and `M_natural_*.npz`). The `.parquet` files are retained locally for analytical queries and DuckDB/Pandas inspection.

---

## 5. Normalization Protocol & Leakage-Free Contract

### 5.1 Formulation
All channels are normalized via Z-score standard scaling:
$$z_{i,t,c} = \frac{x_{i,t,c} - \mu_c}{\sigma_c}$$

### 5.2 Training Set Parameter Guarantees
- **Isolation Guarantee**: All normalization parameters ($\mu_c, \sigma_c$) were computed **strictly and exclusively** from the training split ($N_{train} = 294,528$ station-hours from 2019-01-01 to 2021-02-05).
- **Validation and Test Isolation**: Exactly zero validation or test observations were accessed during parameter computation.
- **Parameter File**: `data/final/CTDI_AirPollution_TrainingDataset_v1.0/metadata/normalization_stats.json`

### 5.3 Canonical Scaling Parameters ($\mu_c, \sigma_c$)

| Channel | Variable | Mean ($\mu$) | Standard Deviation ($\sigma$) | Median | Min | Max |
|:---:|:---|---:|---:|---:|---:|---:|
| 0 | `pm25` | 18.4007 | 12.5468 | 16.0 | 0.0 | 167.0 |
| 1 | `pm10` | 31.1885 | 20.0397 | 27.0 | 0.0 | 241.0 |
| 2 | `no2` | 43.7296 | 32.0178 | 36.0 | 0.0 | 366.0 |
| 3 | `so2` | 4.8857 | 2.9916 | 4.0 | 0.0 | 81.0 |
| 4 | `o3` | 51.4587 | 39.3490 | 43.0 | 0.0 | 422.0 |
| 5 | `pressure` | 1010.9061 | 6.6221 | 1011.0 | 988.8 | 1029.4 |
| 6 | `relative_humidity` | 81.2846 | 15.0711 | 86.0 | 13.0 | 100.0 |
| 7 | `temperature` | 22.7707 | 5.0677 | 23.6 | 2.9 | 35.6 |
| 8 | `rainfall` | 0.2320 | 1.0006 | 0.0 | 0.0 | 61.8 |
| 9 | `wind_direction` | 116.8105 | 80.0363 | 94.0 | 1.0 | 360.0 |
| 10 | `wind_speed` | 3.5634 | 1.7061 | 3.4 | 0.0 | 17.35 |
| 11 | `traffic_speed` | 62.0280 | 5.7545 | 62.66 | 34.76 | 146.66 |
| 12 | `traffic_congestion`| 0.1196 | 0.0626 | 0.1076 | 0.0 | 0.7959 |

---

## 6. Complete Inventory & Classification of Files

The frozen package directory `data/final/CTDI_AirPollution_TrainingDataset_v1.0` contains 51 files totaling 122.1 MB:

### 6.1 Category A: Required Files for Model Training & Validation (Minimal Core: 20.47 MB)
These files are strictly required to run model training, validation, testing, and spatial feature encoding in Phase 4C:

| File Path | Format | Size (Bytes) | Size (MB) | Purpose in Phase 4C |
|:---|:---:|---:|---:|:---|
| `train/X_train.npz` | NPZ | 10,594,624 | 10.10 | Training observation tensor `(294160, 24, 13)` |
| `train/M_natural_train.npz` | NPZ | 885,680 | 0.84 | Training observation mask `(294160, 24, 13)` |
| `validation/X_val.npz` | NPZ | 2,265,458 | 2.16 | Validation observation tensor `(62608, 24, 13)` |
| `validation/M_natural_val.npz` | NPZ | 205,074 | 0.20 | Validation observation mask `(62608, 24, 13)` |
| `test/X_test.npz` | NPZ | 2,275,477 | 2.17 | Test ground-truth tensor `(62224, 24, 13)` |
| `test/M_natural_test.npz` | NPZ | 198,609 | 0.19 | Test observation mask `(62224, 24, 13)` |
| `metadata/channel_schema.csv` | CSV | 1,172 | <0.01 | Channel metadata, units, and ordering indices |
| `metadata/station_metadata.csv`| CSV | 1,336 | <0.01 | 16 station coordinates, types, and spatial network |
| `metadata/normalization_stats.json`| JSON | 3,594 | <0.01 | Z-score scaling parameters ($\mu, \sigma$) |
| `metadata/split_manifest.csv` | CSV | 1,191 | <0.01 | Partition boundaries, timestamps, and window counts |
| `metadata/masking_statistics.json` | JSON | 2,814 | <0.01 | Natural missingness statistics across channels |
| `metadata/window_metadata.parquet` | Parquet | 4,070,452 | 3.88 | Window index mapping (timestamp, station, split) |
| `DATASET_CARD.md` | MD | 7,570 | <0.01 | Formal dataset card documentation |
| `README.md` | MD | 5,951 | <0.01 | Dataset package overview and quickstart |
| `dataset_manifest.json` | JSON | 15,972 | 0.02 | Package inventory and SHA-256 manifest |
| `checksums/SHA256SUMS` | Text | 4,458 | <0.01 | Cryptographic SHA-256 verification sums |
| **Subtotal Category A** | | **20,533,432** | **~20.5 MB** | **Minimal Training Payload** |

### 6.2 Category B: Evaluation-Only Mask Files (Post-Training Benchmarks: 17.03 MB)
These files represent synthetic experimental masks (MCAR, Station Outage, Temporal Block). They are **never** used during model training or validation. They are strictly loaded during the Phase 4C post-training benchmark evaluation suite:

| File Path | Format | Size (Bytes) | Evaluation Protocol |
|:---|:---:|---:|:---|
| `masks/mcar/mcar_10.npz` | NPZ | 1,697,083 | 10% random missingness benchmark |
| `masks/mcar/mcar_30.npz` | NPZ | 2,834,148 | 30% random missingness benchmark |
| `masks/mcar/mcar_50.npz` | NPZ | 3,108,804 | 50% random missingness benchmark |
| `masks/mcar/mcar_70.npz` | NPZ | 2,970,006 | 70% random missingness benchmark |
| `masks/station_outage/station_outage_1.npz` | NPZ | 172,077 | 1-station complete spatial blackout |
| `masks/station_outage/station_outage_2.npz` | NPZ | 204,151 | 2-station complete spatial blackout |
| `masks/station_outage/station_outage_4.npz` | NPZ | 256,612 | 4-station complete spatial blackout |
| `masks/station_outage/station_outage_full.npz` | NPZ | 289,410 | Full spatial blackout benchmark |
| `masks/temporal_block/block_10.npz` | NPZ | 828,107 | 10% temporal block dropout |
| `masks/temporal_block/block_30.npz` | NPZ | 1,606,377 | 30% temporal block dropout |
| `masks/temporal_block/block_50.npz` | NPZ | 1,974,222 | 50% temporal block dropout |
| `masks/temporal_block/block_70.npz` | NPZ | 1,972,775 | 70% temporal block dropout |
| **Subtotal Category B (NPZ)** | | **17,913,772** | **~17.1 MB** |

### 6.3 Category C: Local-Only / Redundant Parquet Tables & Notebooks (84.5 MB)
These files remain preserved locally in `data/final/` but are redundant for model execution:
- Parquet counterparts: `train/X_train.parquet` (44.72 MB), `train/M_natural_train.parquet` (2.45 MB), `validation/*.parquet` (9.28 MB), `test/*.parquet` (9.88 MB), and `masks/*/*.parquet` (14.24 MB).
- Notebooks: `overview.ipynb` (4.2 MB across root and subfolders).
- Raw and interim data: `data/raw/` (114 MB), `data/interim/`, `data/processed/`, `data/canonical/`.

---

## 7. Repository Tracking & Git Policy for Phase 4C

1. **Git Tracking Strategy**:
   - The minimal NPZ tensors and metadata in Category A (~20.5 MB) fit comfortably within standard Git object storage without triggering GitHub warnings (threshold: 50 MB) or blocks (hard limit: 100 MB).
   - Largest single file: `train/X_train.npz` (10.59 MB), which is well below GitHub's 50 MB recommendation.
   - Therefore, **Git LFS is not required** if tracking only the minimal NPZ training payload.
   - If Parquet files were tracked, Git LFS would be mandatory for `train/X_train.parquet` (44.72 MB).
2. **Local Data Preservation**:
   - Zero files will be deleted. The full 122.1 MB dataset package, all raw files, and interim outputs remain intact locally.
   - `.gitignore` explicitly protects `data/raw/`, `data/interim/`, `data/processed/`, `data/canonical/`, and large parquet caches from accidental Git staging.

---

## 8. Verification & Integrity Checklist

- [x] All 46 cryptographic checksums verified bit-for-bit OK via `sha256sum -c checksums/SHA256SUMS`.
- [x] Complete test suite verified: 23/23 tests passing (`tests/test_dataset_v1.py`, `tests/test_missingness.py`, `tests/test_overview_notebook.py`).
- [x] Tensor dimensions verified: Train `(294160, 24, 13)`, Val `(62608, 24, 13)`, Test `(62224, 24, 13)`.
- [x] Z-score normalization parameters strictly confined to training period; zero validation or test leakage.
- [x] Evaluation benchmark masks verified as test-partition only (`N = 62,224`) and strictly isolated from model training.
- [x] Git branch baseline verified: `main` aligned with `base/slm` (`4e6a72d`).
