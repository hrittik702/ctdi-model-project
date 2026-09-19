# Final Training Dataset v1.0 Specification

**Dataset Name**: `CTDI_AirPollution_TrainingDataset_v1.0`  
**Package Path**: `data/final/CTDI_AirPollution_TrainingDataset_v1.0/`  
**Version**: `1.0` (Frozen & Released)  
**Date**: `2026-09-19`  
**Status**: **`FROZEN_FOR_MODEL_TRAINING`**  
**Benchmark Reference**: Yu et al., *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, IEEE Transactions on Big Data, 2025.

---

## 1. Executive Summary & Frozen Scope

`CTDI_AirPollution_TrainingDataset_v1.0` is the frozen, self-contained, and cryptographically verified training and benchmark package for generative and spatio-temporal air pollution imputation models. It encapsulates the full 3-year study horizon (2019–2021) across 16 continuous monitoring stations in Hong Kong, partitioned into leakage-safe chronological splits with pre-computed evaluation masks and train-only normalization statistics.

### What is Frozen:
1. **Temporal Horizon**: Exactly 3 calendar years ($1,096$ days, $26,304$ continuous hourly timestamps from `2019-01-01 00:00:00` to `2021-12-31 23:00:00` UTC+8).
2. **Spatial Domain**: Exactly 16 continuous air quality monitoring stations in Hong Kong ([`Station Inventory & Spatial Network.md`](Station%20Inventory%20&%20Spatial%20Network.md)). Stations Southern (#84) and North (#85) are excluded in strict accordance with the published CTDI paper benchmark protocol.
3. **Canonical Channels**: Exactly 13 continuous channels ordered deterministically ([`CTDI 13-Channel Specification.md`](CTDI%2013-Channel%20Specification.md)). Channel index 8 is ERA5 continuous total rainfall (mm), formally substituted for unrecoverable HKO visibility per Decision D07.
4. **Window Geometry**: 24-hour sliding temporal windows with a 1-hour step size, yielding $26,281$ windows per station and $420,496$ total windows across the network ($S=16$).
5. **Partitioning**: Chronological split into Train ($294,160$ windows, $69.96\%$), Validation ($62,608$ windows, $14.89\%$), and Test ($62,224$ windows, $14.80\%$), separated by two 24-hour calendar-day purge buffers ($752$ excluded windows each; $25.0\text{h}$ physical gap).
6. **Normalization Statistics**: Fit strictly on training station-hours ($294,528$ records), providing zero-leakage z-score standardization.
7. **Benchmark Evaluation Masks**: 12 deterministic pre-computed scenarios across all $62,224$ test windows ($7,261,392$ eligible evaluation cells), strictly partitioned by the target firewall invariant.

---

## 2. Dataset Contract & Tensor Geometry

### 2.1 Spatial-Temporal-Channel Geometry
Every sliding window represents a 2D matrix per station-window or a 3D batch element:
$$\mathbf{X} \in \mathbb{R}^{24 \times 13}$$
$$\mathbf{M}_{\text{natural}} \in \{0, 1\}^{24 \times 13}$$

When loaded in batches across stations or time:
- **Individual Window**: Shape `(24, 13)`
- **Full Partition Tensor** (Station-Window Batch):
  - Train: `(294160, 24, 13)`
  - Validation: `(62608, 24, 13)`
  - Test: `(62224, 24, 13)`
  - Buffer (Purged): `(1504, 24, 13)`

### 2.2 Canonical Channel Schema
The channel ordering is immutable. Any permutation invalidates model weights and pre-computed evaluation masks:

| Channel Index | Channel Name | Physical Unit | Domain / Category | Source Provider | Missingness Policy |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **0** | `PM2.5` | $\mu\text{g}/\text{m}^3$ | Air Pollutant (Target) | HKEPD | Natural NaNs preserved ($M_{\text{nat}}=0$) |
| **1** | `PM10` | $\mu\text{g}/\text{m}^3$ | Air Pollutant (Target) | HKEPD | Natural NaNs preserved ($M_{\text{nat}}=0$) |
| **2** | `SO2` | $\mu\text{g}/\text{m}^3$ | Air Pollutant (Target) | HKEPD | Natural NaNs preserved ($M_{\text{nat}}=0$) |
| **3** | `NO2` | $\mu\text{g}/\text{m}^3$ | Air Pollutant (Target) | HKEPD | Natural NaNs preserved ($M_{\text{nat}}=0$) |
| **4** | `CO` | $\mu\text{g}/\text{m}^3$ | Air Pollutant (Target) | HKEPD | Natural NaNs preserved ($M_{\text{nat}}=0$) |
| **5** | `temperature` | $^\circ\text{C}$ | Meteorology (Exogenous) | ECMWF ERA5 | Complete ($100\%$ observed) |
| **6** | `pressure` | $\text{hPa}$ | Meteorology (Exogenous) | ECMWF ERA5 | Complete ($100\%$ observed) |
| **7** | `humidity` | $\%$ | Meteorology (Exogenous) | ECMWF ERA5 | Complete ($100\%$ observed) |
| **8** | `rainfall` | $\text{mm}$ | Meteorology (Exogenous) | ECMWF ERA5 | Complete ($100\%$ observed) |
| **9** | `wind_speed` | $\text{m}/\text{s}$ | Meteorology (Exogenous) | ECMWF ERA5 | Complete ($100\%$ observed) |
| **10** | `wind_direction`| $\text{degrees}$ | Meteorology (Exogenous) | ECMWF ERA5 | Complete ($100\%$ observed, $[0, 360)$) |
| **11** | `traffic_speed`| $\text{km}/\text{h}$ | Urban Mobility (Exogenous) | Transport Dept Speedmap | IDW $p=2$; Archive NaNs preserved |
| **12** | `traffic_flow` | Ordinal $[0, 1]$ | Urban Mobility (Exogenous) | Transport Dept Speedmap | Congestion saturation score |

---

## 3. Package File Hierarchy & Storage Footprint

The package resides at `data/final/CTDI_AirPollution_TrainingDataset_v1.0/` with a total disk footprint of approximately $121\text{ MB}$ across 46 files:

```text
data/final/CTDI_AirPollution_TrainingDataset_v1.0/
├── README.md                              # High-level overview and onboarding instructions
├── DATASET_CARD.md                        # Formal ML dataset card and provenance disclosure
├── dataset_manifest.json                  # Machine-readable structural metadata and manifest
├── checksums/
│   └── SHA256SUMS                         # Cryptographic SHA-256 hashes for all 46 package files
├── train/
│   ├── X_train.parquet                    # Normalized feature windows (42.65 MB)
│   ├── M_natural_train.parquet            # Natural missingness masks (2.34 MB)
│   ├── X_train.npz                        # Dense NumPy tensor (10.10 MB, shape (294160, 24, 13))
│   └── M_natural_train.npz                # Dense NumPy mask (0.84 MB, shape (294160, 24, 13))
├── validation/
│   ├── X_val.parquet                      # Normalized feature windows (8.28 MB)
│   ├── M_natural_val.parquet              # Natural missingness masks (0.57 MB)
│   ├── X_val.npz                          # Dense NumPy tensor (2.16 MB, shape (62608, 24, 13))
│   └── M_natural_val.npz                  # Dense NumPy mask (0.20 MB, shape (62608, 24, 13))
├── test/
│   ├── X_test.parquet                     # Normalized feature windows (8.86 MB)
│   ├── M_natural_test.parquet             # Natural missingness masks (0.57 MB)
│   ├── X_test.npz                         # Dense NumPy tensor (2.17 MB, shape (62224, 24, 13))
│   └── M_natural_test.npz                 # Dense NumPy mask (0.19 MB, shape (62224, 24, 13))
├── masks/
│   ├── test_benchmark_masks.parquet       # Master test benchmark mask table (7.39 MB)
│   ├── mcar/
│   │   ├── mcar_10.npz / .parquet         # Point MCAR 10% (0.19 MB / 1.70 MB)
│   │   ├── mcar_30.npz / .parquet         # Point MCAR 30% (0.23 MB / 2.05 MB)
│   │   ├── mcar_50.npz / .parquet         # Point MCAR 50% (0.26 MB / 2.37 MB)
│   │   └── mcar_70.npz / .parquet         # Point MCAR 70% (0.29 MB / 2.65 MB)
│   ├── temporal_block/
│   │   ├── block_10.npz / .parquet        # Contiguous Block 10% (0.19 MB / 1.69 MB)
│   │   ├── block_30.npz / .parquet        # Contiguous Block 30% (0.23 MB / 2.05 MB)
│   │   ├── block_50.npz / .parquet        # Contiguous Block 50% (0.26 MB / 2.37 MB)
│   │   └── block_70.npz / .parquet        # Contiguous Block 70% (0.29 MB / 2.65 MB)
│   └── station_outage/
│       ├── station_outage_1.npz / .parquet    # Spatial Outage S1 (1 station)
│       ├── station_outage_2.npz / .parquet    # Spatial Outage S2 (2 stations)
│       ├── station_outage_4.npz / .parquet    # Spatial Outage S4 (4 stations)
│       └── station_outage_full.npz / .parquet # Spatial Outage S_full (16 stations)
└── metadata/
    ├── channel_schema.csv                 # 13-channel index, name, unit, and role definition
    ├── station_metadata.csv               # 16 station IDs, names, coords, types, elevations
    ├── split_manifest.csv                 # Window counts, date ranges, and buffer reconciliation
    ├── window_metadata.parquet            # Temporal index, station ID, slice timestamps (3.88 MB)
    ├── normalization_stats.json           # Train-fitted mean, std, min, max, median, IQR
    └── masking_statistics.json            # Target missingness rates and empirical deviations
```

---

## 4. Train-Only Normalization Policy

To enforce mathematical zero-data-leakage, all normalization statistics were fit strictly on the training partition ($294,528$ station-hours from `2019-01-01 00:00` to `2021-02-05 23:00`):

$$z_{s, t, c} = \frac{x_{s, t, c} - \mu_c}{\sigma_c}$$

### Normalization Parameters (`metadata/normalization_stats.json`):
- **PM2.5**: $\mu = 15.6888\,\mu\text{g}/\text{m}^3$, $\sigma = 10.9702\,\mu\text{g}/\text{m}^3$
- **PM10**: $\mu = 28.5303\,\mu\text{g}/\text{m}^3$, $\sigma = 17.5855\,\mu\text{g}/\text{m}^3$
- **SO2**: $\mu = 5.2536\,\mu\text{g}/\text{m}^3$, $\sigma = 3.6669\,\mu\text{g}/\text{m}^3$
- **NO2**: $\mu = 38.3846\,\mu\text{g}/\text{m}^3$, $\sigma = 26.6800\,\mu\text{g}/\text{m}^3$
- **CO**: $\mu = 566.2719\,\mu\text{g}/\text{m}^3$, $\sigma = 277.5847\,\mu\text{g}/\text{m}^3$
- **Temperature**: $\mu = 24.3643^\circ\text{C}$, $\sigma = 5.1636^\circ\text{C}$
- **Pressure**: $\mu = 1012.8711\,\text{hPa}$, $\sigma = 6.2713\,\text{hPa}$
- **Humidity**: $\mu = 77.8932\%$, $\sigma = 12.9839\%$
- **Rainfall**: $\mu = 0.2312\,\text{mm}$, $\sigma = 1.6980\,\text{mm}$
- **Wind Speed**: $\mu = 3.6121\,\text{m}/\text{s}$, $\sigma = 2.0520\,\text{m}/\text{s}$
- **Wind Direction**: $\mu = 117.8427^\circ$, $\sigma = 89.3789^\circ$
- **Traffic Speed**: $\mu = 50.8122\,\text{km}/\text{h}$, $\sigma = 10.7410\,\text{km}/\text{h}$
- **Traffic Flow**: $\mu = 0.3541$, $\sigma = 0.2215$

Validation and test tensors are scaled using these exact training parameters. During denormalization, the inverse transformation restores the physical scale: $\hat{x} = \hat{z} \cdot \sigma_c + \mu_c$.

---

## 5. Natural Missingness & The Target Firewall Invariant

### 5.1 Natural Missingness
Natural sensor dropouts ($55,876$ values across the 3-year air quality archive, matching CTDI Section IV-B) are encoded in $\mathbf{M}_{\text{natural}}$:
$$M_{\text{natural}}(t, c) = \begin{cases} 1 & \text{if observation exists and is physically valid} \\ 0 & \text{if observation is missing in raw source (NaN)} \end{cases}$$

### 5.2 Target Firewall Invariant
In evaluation benchmarking, models must never be evaluated against natural NaNs. The target firewall strictly partitions every cell into three mutually exclusive states:
1. **Observed Conditioning Input**: $M_{\text{observed}} = M_{\text{natural}} \odot (1 - M_{\text{artificial}})$
2. **Evaluation Target**: $M_{\text{target}} = M_{\text{natural}} \odot M_{\text{artificial}}$
3. **Unobserved Natural Dropout**: $1 - M_{\text{natural}}$

$$\mathbf{M}_{\text{natural}} \equiv \mathbf{M}_{\text{observed}} + \mathbf{M}_{\text{target}}$$
$$\mathbf{M}_{\text{observed}} \odot \mathbf{M}_{\text{target}} = \mathbf{0}$$
$$M_{\text{target}} \le M_{\text{natural}}$$

---

## 6. Pre-Computed Benchmark Mask Scenarios

All 12 evaluation scenarios are pre-computed across the $62,224$ test windows ($7,261,392$ eligible criteria pollutant cells, channels 0–4):

| Scenario Key | Description | Masked Cells | Empirical Rate | Target Rate | Empirical Deviation |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `mcar_10` | Point MCAR 10% | $731,326$ | $10.07\%$ | $10.00\%$ | $+0.07\%$ |
| `mcar_30` | Point MCAR 30% | $2,174,824$ | $29.95\%$ | $30.00\%$ | $-0.05\%$ |
| `mcar_50` | Point MCAR 50% | $3,627,817$ | $49.96\%$ | $50.00\%$ | $-0.04\%$ |
| `mcar_70` | Point MCAR 70% | $5,085,285$ | $70.03\%$ | $70.00\%$ | $+0.03\%$ |
| `block_10` | Temporal Block MAR 10% | $731,326$ | $10.07\%$ | $10.00\%$ | $+0.07\%$ |
| `block_30` | Temporal Block MAR 30% | $2,174,824$ | $29.95\%$ | $30.00\%$ | $-0.05\%$ |
| `block_50` | Temporal Block MAR 50% | $3,627,817$ | $49.96\%$ | $50.00\%$ | $-0.04\%$ |
| `block_70` | Temporal Block MAR 70% | $5,085,285$ | $70.03\%$ | $70.00\%$ | $+0.03\%$ |
| `station_outage_1` | Spatial Outage S1 (1 station) | $453,636$ | $6.25\%$ | $6.25\%$ | $0.00\%$ |
| `station_outage_2` | Spatial Outage S2 (2 stations) | $907,691$ | $12.50\%$ | $12.50\%$ | $0.00\%$ |
| `station_outage_4` | Spatial Outage S4 (4 stations) | $1,815,340$ | $25.00\%$ | $25.00\%$ | $0.00\%$ |
| `station_outage_full` | Spatial Outage S_full (16 stations) | $7,261,392$ | $100.00\%$ | $100.00\%$ | $0.00\%$ |

---

## 7. Teammate Consumption Interface

Teammates can consume the dataset immediately using either PyTorch or Pandas.

### 7.1 PyTorch Dataset Example (`.npz` format)
```python
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

class CTDIDataset(Dataset):
    def __init__(self, data_dir: str, split: str = "train"):
        npz_x = np.load(f"{data_dir}/{split}/X_{split}.npz")
        npz_m = np.load(f"{data_dir}/{split}/M_natural_{split}.npz")
        self.X = torch.from_numpy(npz_x["data"]).float()      # Shape: (N, 24, 13)
        self.M = torch.from_numpy(npz_m["data"]).float()      # Shape: (N, 24, 13)

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, idx):
        return {"features": self.X[idx], "natural_mask": self.M[idx]}

# Usage:
dataset = CTDIDataset("data/final/CTDI_AirPollution_TrainingDataset_v1.0", split="train")
loader = DataLoader(dataset, batch_size=64, shuffle=True)
for batch in loader:
    x = batch["features"]      # (64, 24, 13)
    m = batch["natural_mask"]  # (64, 24, 13)
    break
```

### 7.2 Pandas / Polars Example (`.parquet` format)
```python
import pandas as pd

# Load test partition features and metadata
X_test = pd.read_parquet("data/final/CTDI_AirPollution_TrainingDataset_v1.0/test/X_test.parquet")
meta = pd.read_parquet("data/final/CTDI_AirPollution_TrainingDataset_v1.0/metadata/window_metadata.parquet")

# Reshape window to 24x13
sample_row = X_test.iloc[0]
window_matrix = sample_row.drop("window_id").to_numpy().reshape(24, 13)
```

---

## 8. Cryptographic Checksums & Deterministic Reproducibility

All 46 files in the package have been validated with zero mismatches against `checksums/SHA256SUMS`.
To verify package integrity on any Linux/macOS terminal:

```bash
cd data/final/CTDI_AirPollution_TrainingDataset_v1.0/
sha256sum -c checksums/SHA256SUMS
```

All 46 files will report `OK`.

---

## 9. Known Limitations

1. **ERA5 Rainfall Substitution**: Channel index 8 contains total rainfall from ECMWF ERA5 continuous hourly surface reanalysis. The original CTDI paper used unrecoverable 10-minute visibility series from Dr. Yang Han at HKU ([`Visibility Data Recovery & Provenance Report.md`](../Reports/Visibility%20Data%20Recovery%20&%20Provenance%20Report.md)).
2. **Traffic Spatial Resolution**: Traffic speeds and saturation flows are projected onto the 16 air stations via inverse distance weighting ($p=2$) across 632 georeferenced road links. Sub-link traffic congestion is spatialized to station coordinates.
3. **Hourly Temporal Resolution**: Sub-hourly phenomena (e.g., 5-minute traffic surges) are aggregated into 1-hour intervals.

---

## 10. Important Scientific Boundary

`CTDI_AirPollution_TrainingDataset_v1.0` is permanently **FROZEN**.
- **DO NOT** modify channel ordering.
- **DO NOT** alter raw data or intermediate alignment files.
- **DO NOT** recalculate normalization statistics with validation or test observations.
- **DO NOT** convert natural NaNs to evaluation targets.
- Any future scientific changes or additional sensor modalities require releasing an explicitly incremented dataset version (e.g., `v1.1`).
