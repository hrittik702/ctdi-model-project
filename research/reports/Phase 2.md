# Phase 2 & 3: Spatial Alignment & Canonical Tensor Construction Plan

## Goal Description

Transform the verified raw datasets (EPD air pollutants, Open-Meteo meteorology, TD traffic dynamics) into the unified canonical multi-modal tensor: Xcanonical∈R16×26,304×13Xcanonical​∈R16×26,304×13 along with its corresponding binary observation mask: Mcanonical∈{0,1}16×26,304×13Mcanonical​∈{0,1}16×26,304×13 Total numerical volume: 16 stations×26,304 hours×13 channels=5,471,232 values16 stations×26,304 hours×13 channels=5,471,232 values.

---
**Pyarrow is using** 
## User Review Required

IMPORTANT

- **Spatial Anchor**: The 16 continuous air quality monitoring stations are used as the spatial coordinate anchors.
- **Zero Synthetic Data Injection**: No values are fabricated. Natural missing values (~2.5% in pollutants) remain as `np.nan` in `tensor_features.npy`, with exact positions recorded as `0` in `tensor_mask.npy`.
- **Traffic Fusion**: Traffic speed and volume profiles from co-located Transport Department detectors and the Annual Traffic Census are aligned to the 16 station coordinates.
- **Frontend & API Unchanged**: Frontend and FastAPI entry point will not be touched during this tensor assembly.

---

## Proposed Changes

### Data Pipeline & Preprocessing Layer

#### [NEW] alignment.py

Implements spatio-temporal alignment:

- Merges the 5 pollutant features (`pm25`, `pm10`, `no2`, `o3`, `so2`) from EPD.
- Merges the 6 meteorological variables (`temperature`, `relative_humidity`, `wind_speed`, `wind_direction`, `pressure`, `rainfall`) from Open-Meteo.
- Computes and merges the 2 traffic features (`traffic_speed`, `traffic_volume`) from Transport Department detector and ATC census hourly diurnal curves.
- Computes the 16×1616×16 pairwise Haversine geographic distance matrix between all monitoring stations.
- Saves the intermediate table as `data/interim/aligned_hourly_features.parquet` and distance matrix as `data/interim/spatial_distance_matrix.npy`.

#### [NEW] canonical_builder.py

Constructs canonical tensors:

- Reshapes the aligned table into 3D tensors: [S,T,C]=[16,26304,13][S,T,C]=[16,26304,13].
- Builds binary observation mask MobsMobs​ (1=valid observation,0=missing1=valid observation,0=missing).
- Exports:
    - `data/canonical/tensor_features.npy` (`float32`)
    - `data/canonical/tensor_mask.npy` (`uint8`)
    - `data/canonical/timestamps.csv` (26,30426,304 timestamps)
    - `data/canonical/channels.json` (List of 13 channel names)
    - `data/canonical/stations.json` (List of 16 station names & coordinates)
    - `data/canonical/spatial_distance_matrix.npy` (16×1616×16)

#### [NEW] build_canonical_dataset.py

User-executable command line entry point to run the alignment and canonical tensor building pipeline end-to-end.

### Testing & Verification Layer

#### [NEW] test_canonical_tensor.py

Pytest test suite asserting:

- `tensor_features.shape == (16, 26304, 13)`.
- `tensor_mask.shape == (16, 26304, 13)`.
- `tensor_mask` contains only values in {0,1}{0,1} with zero NaNs.
- Natural missingness in mask matches ~2.5% to 2.8% for pollutant channels and 0.0% for meteorology.
- Timestamps are strictly monotonic and span exactly 2019-01-01 00:00 to 2021-12-31 23:00.

---

## Verification Plan

### Automated Tests

bash

# 1. Run canonical tensor builder

.venv/bin/python scripts/build_canonical_dataset.py

# 2. Run pytest verification suite

.venv/bin/pytest tests/test_canonical_tensor.py -v

### Manual Inspection

- Confirm generated file sizes in `data/canonical/`:
    - `tensor_features.npy`: ≈21.9 MB≈21.9 MB
    - `tensor_mask.npy`: ≈5.5 MB≈5.5 MB
- Check memory-mapping (`mmap_mode='r'`) performance for fast random access.