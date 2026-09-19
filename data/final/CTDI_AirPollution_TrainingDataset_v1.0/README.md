# CTDI Air Pollution Training Dataset v1.0

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
