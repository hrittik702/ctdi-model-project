# Dataset Card: CTDI_AirPollution_TrainingDataset_v1.0

## 1. Dataset Overview
- **Name**: `CTDI_AirPollution_TrainingDataset_v1.0`
- **Version**: `1.0.0`
- **Benchmark Paper**: Yangwen Yu, Victor O. K. Li, Jacqueline C. K. Lam, Kelvin Chan, Qi Zhang, *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, **IEEE Transactions on Big Data**, vol. 11, no. 5, pp. 2442–2455, Sept.–Oct. 2025. [DOI: 10.1109/TBDATA.2025.3533882](https://doi.org/10.1109/TBDATA.2025.3533882)
- **Domain**: Hong Kong Special Administrative Region (16 air quality monitoring stations, 2019-01-01 to 2021-12-31).
- **Core Contract**: 13 multi-modal channels $\times$ 24 hourly timesteps ($T=24$) per sliding window sample.
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
| **0** | `pm25` | Air Quality | $\mu\text{g/m}^3$ | Fine Particulate Matter ($<2.5\mu\text{m}$) | 10,657 NaNs ($2.53\%$) |
| **1** | `pm10` | Air Quality | $\mu\text{g/m}^3$ | Respirable Suspended Particulates ($<10\mu\text{m}$) | 11,395 NaNs ($2.71\%$) |
| **2** | `no2` | Air Quality | $\mu\text{g/m}^3$ | Nitrogen Dioxide | 11,651 NaNs ($2.77\%$) |
| **3** | `so2` | Air Quality | $\mu\text{g/m}^3$ | Sulphur Dioxide | 11,056 NaNs ($2.63\%$) |
| **4** | `o3` | Air Quality | $\mu\text{g/m}^3$ | Ground-Level Ozone | 11,117 NaNs ($2.64\%$) |
| **5** | `pressure` | Meteorology | $\text{hPa}$ | Barometric Atmospheric Surface Pressure | 0 NaNs ($100\%$ complete) |
| **6** | `relative_humidity` | Meteorology | $\%$ | Ambient Relative Humidity | 0 NaNs ($100\%$ complete) |
| **7** | `temperature` | Meteorology | $^\circ\text{C}$ | Ambient 2-Meter Dry-Bulb Air Temperature | 0 NaNs ($100\%$ complete) |
| **8** | `rainfall` | Meteorology | $\text{mm}$ | Total Hourly Precipitation (Aerosol wet scavenging proxy) | 0 NaNs ($100\%$ complete) |
| **9** | `wind_direction` | Meteorology | Degrees ($^\circ$) | 10-Meter Wind Direction Compass Azimuth ($0\text{--}360^\circ$) | 0 NaNs ($100\%$ complete) |
| **10** | `wind_speed` | Meteorology | $\text{m/s}$ | 10-Meter Surface Wind Velocity | 0 NaNs ($100\%$ complete) |
| **11** | `traffic_speed` | Traffic | $\text{km/h}$ | Spatial-IDW ($p=2$) Arterial Road Speed | 2,416 NaNs ($0.57\%$, archive outages) |
| **12** | `traffic_congestion` | Traffic | $[0.0, 1.0]$ | Spatial-IDW ($p=2$) Road Saturation Level (GOOD=0, AVG=0.5, BAD=1.0) | 2,416 NaNs ($0.57\%$, archive outages) |

> [!IMPORTANT]
> **Rainfall Adoption (Channel 8)**: Table I of Yu et al. (2025) specifies horizontal optical visibility (km) from HKO Automatic Weather Stations (AWS). However, extensive empirical audit proved that retrospective 10-minute HKO AWS historical visibility is publicly **irrecoverable** from open data (the CTDI paper authors received an unreleased private offline dataset from Dr. Yang Han at HKU; Page 2454). Per Decision D07, ECMWF ERA5 continuous hourly surface precipitation (mm) was formally adopted as Channel 8 due to its physical coupling with aerosol wet deposition and criteria pollutant scavenging.

---

## 4. Natural Missingness & Target Firewall
- **Natural Missingness Conservation**: Exactly $55,876$ natural pollutant NaNs in the primary air quality table ($2.66\%$) are preserved bit-for-bit with the raw sensor archives.
- **No Natural Imputation**: Natural NaNs are **never** filled with zero, mean, or interpolated values in the ground-truth arrays.
- **Target Firewall Invariant**: In all evaluation masking protocols, cells with natural sensor dropouts ($M_{\text{natural}} = 0$) are **never** treated as evaluation targets:
  $$M_{\text{target}} \le M_{\text{natural}}, \quad M_{\text{observed}} = M_{\text{natural}} \odot (1 - M_{\text{target}}), \quad M_{\text{natural}} = M_{\text{observed}} + M_{\text{target}}$$

---

## 5. Chronological Partitioning & Purge Buffers
To prevent autoregressive data leakage across sliding window horizons, chronological partitions are separated by 24-hour temporal purge buffers:

| Partition | Time Horizon | Windows | Percentage | Role |
| :--- | :--- | :---: | :---: | :--- |
| **Train** | `2019-01-01 00:00` to `2021-02-05 23:00` | $294,160$ | $69.96\%$ | Training model parameters |
| **Buffer 1** | Purge day `2021-02-06` ($25.0\text{h}$ physical gap) | $752$ | $0.18\%$ | **Purged** (47 windows/station excluded) |
| **Validation** | `2021-02-07 00:00` to `2021-07-20 23:00` | $62,608$ | $14.89\%$ | Hyperparameter tuning & model selection |
| **Buffer 2** | Purge day `2021-07-21` ($25.0\text{h}$ physical gap) | $752$ | $0.18\%$ | **Purged** (47 windows/station excluded) |
| **Test** | `2021-07-22 00:00` to `2021-12-31 23:00` | $62,224$ | $14.80\%$ | Final benchmark evaluation |

---

## 6. Normalization Protocol
- **Primary Method**: Standard z-score standardization ($x' = (x - \mu) / \sigma$).
- **Strict Isolation**: Parameters $\mu, \sigma$ are fitted **strictly on the 294,528 station-hours of the training partition** (observations $\le$ `2021-02-05 23:00:00`). Zero validation or test data leakage.
- **Stored Format**: Pre-computed statistics are provided in `metadata/normalization_stats.json`. Raw tensors $X$ in `train/`, `validation/`, and `test/` remain unnormalized on disk so that researchers can inspect native physical units ($\mu\text{g/m}^3$, $^\circ\text{C}$, $\text{km/h}$) or apply alternative scalings (min-max, robust, log1p).

---

## 7. Artificial Missingness Benchmarks
The test partition ($62,224$ windows) includes pre-computed deterministic benchmark evaluation masks for 12 experimental scenarios:
1. **Random Point MCAR**: 10%, 30%, 50%, 70% missingness rates across criteria pollutants.
2. **Continuous Temporal Block MAR**: 10%, 30%, 50%, 70% missingness rates (burst outages of 3–12 hours, trimmed to exact rate within $\pm 0.07\%$).
3. **Spatial Station Outage**: S1 (1 station / 6.25%), S2 (2 stations / 12.50%), S4 (4 stations / 25.00%), S_full (16 stations / 100.00%).

---

## 8. Intended & Non-Intended Use
- **Intended Use**: Benchmarking spatio-temporal missing data imputation algorithms, conditional generative diffusion models, small language model (SLM) environmental context conditioning, and urban air quality forecasting.
- **Non-Intended Use**: Operational real-time dispatching without real-time sensor calibration; safety-critical atmospheric emergency control without secondary domain validation.
