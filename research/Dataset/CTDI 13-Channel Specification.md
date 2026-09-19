# 13-Channel Multimodal Specification

---

## 1. Ground Truth Channel Enumeration (CTDI Table I)

The 13 multi-modal channels of the canonical tensor $\mathbf{X} \in \mathbb{R}^{16 \times 26,304 \times 13}$ are defined as follows:

| Index | Identifier | Domain | Variable Description | Native Unit | CTDI Source | Spatial Mapping Method |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **0** | `pm25` | Air Pollutant | Fine Particulate Matter ($<2.5\mu\text{m}$) | $\mu\text{g/m}^3$ | HKEPD Database [80] | Direct physical measurement at 16 stations |
| **1** | `pm10` | Air Pollutant | Respirable Particulates ($<10\mu\text{m}$) | $\mu\text{g/m}^3$ | HKEPD Database [80] | Direct physical measurement at 16 stations |
| **2** | `no2` | Air Pollutant | Nitrogen Dioxide | $\mu\text{g/m}^3$ | HKEPD Database [80] | Direct physical measurement at 16 stations |
| **3** | `so2` | Air Pollutant | Sulphur Dioxide | $\mu\text{g/m}^3$ | HKEPD Database [80] | Direct physical measurement at 16 stations |
| **4** | `o3` | Air Pollutant | Ground-Level Ozone | $\mu\text{g/m}^3$ | HKEPD Database [80] | Direct physical measurement at 16 stations |
| **5** | `pressure` | Meteorology | Barometric Atmospheric Pressure | $\text{hPa}$ | HKO Open Database [81] | Spatially interpolated via IDW ($p=2$) from 47 AWS |
| **6** | `relative_humidity` | Meteorology | Ambient Relative Humidity | $\%$ | HKO Open Database [81] | Spatially interpolated via IDW ($p=2$) from 47 AWS |
| **7** | `temperature` | Meteorology | Ambient Dry-Bulb Air Temperature | $^\circ\text{C}$ | HKO Open Database [81] | Spatially interpolated via IDW ($p=2$) from 47 AWS |
| **8** | `visibility` | Meteorology | Horizontal Atmospheric Visibility | $\text{km}$ | HKO Open Database [81] | Spatially interpolated via IDW ($p=2$) from 47 AWS |
| **9** | `wind_direction` | Meteorology | Surface Wind Direction Bearing | Degrees / N/A | HKO Open Database [81] | Spatially interpolated via IDW ($p=2$) from 47 AWS |
| **10** | `wind_speed` | Meteorology | Surface Wind Velocity | $\text{km/h}$ | HKO Open Database [81] | Spatially interpolated via IDW ($p=2$) from 47 AWS |
| **11** | `traffic_speed` | Traffic | Road Segment Vehicular Speed | $\text{km/h}$ | HK Speedmap [82] | Spatially interpolated via IDW ($p=2$) from 607 links |
| **12** | `traffic_congestion`| Traffic | Congestion Index / Saturation Level | N/A | HK Speedmap [82] | Spatially interpolated via IDW ($p=2$) from 607 links |

---

## 2. Comparison with Prior Codebase Assumptions & Empirical Resolution

| Domain | CTDI Ground Truth (Table I) | Prior Codebase Assumption | Match? | Empirical Resolution & Current Status |
| :--- | :--- | :--- | :---: | :--- |
| **Pollutants** | $\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{SO}_2, \text{O}_3$ | Same 5 criteria pollutants | **YES** | **`[EXACT_MATCH]`**: Verified against official HKEPD records. 55,876 natural missing values preserved bit-for-bit across $420,864$ station-hours. Zero negative values. |
| **Meteorology** | **`Visibility` ($\text{km}$)** | `rainfall` ($\text{mm}$) | **NO** | **`[VERIFIED_SUBSTITUTION]`**: HKO AWS 10-minute historical visibility is publicly **`[IRRECOVERABLE]`** (paper authors acquired offline data from Dr. Yang Han at HKU). Formally resolved via **Decision D07**: adopted ECMWF ERA5 continuous hourly surface precipitation ($\text{mm}$) with documented wet-scavenging justification and zero missingness. |
| **Traffic** | **`Traffic speed` & `Traffic congestion`** | `traffic_speed` & `traffic_volume` | **NO** | **`[SOURCE_MATCH & RESOLVED]`**: `traffic_volume` completely refuted. Resolved in Phase 1.1 via full extraction of HKTD 1st Gen Speedmap (774,686 snapshots, 466.8M records across 632 links). In Phase 2, aggregated to hourly link means and spatially projected via IDW ($p=2$). Zero synthetic data injected; natural missing hours preserved as `NaN`. |

---

## 3. Reconstructed Aligned 13-Channel Specification (`ctdi_aligned_reconstructed`)

The operational dataset generated in Phase 2 (`data/interim/aligned/aligned_hourly_station_data.parquet`) implements the following 13-channel schema:

| Channel Index | Channel Key | Physical Domain | Units | Source & Processing | Missingness Profile |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **0** | `pm25` | Air Quality | $\mu\text{g/m}^3$ | HKEPD 16 stations (in-situ monitor) | 10,657 NaNs (2.53%) |
| **1** | `pm10` | Air Quality | $\mu\text{g/m}^3$ | HKEPD 16 stations (in-situ monitor) | 11,395 NaNs (2.71%) |
| **2** | `no2` | Air Quality | $\mu\text{g/m}^3$ | HKEPD 16 stations (in-situ monitor) | 11,651 NaNs (2.77%) |
| **3** | `so2` | Air Quality | $\mu\text{g/m}^3$ | HKEPD 16 stations (in-situ monitor) | 11,056 NaNs (2.63%) |
| **4** | `o3` | Air Quality | $\mu\text{g/m}^3$ | HKEPD 16 stations (in-situ monitor) | 11,117 NaNs (2.64%) |
| **5** | `pressure` | Meteorology | $\text{hPa}$ | ERA5 surface reanalysis at station coordinates | 0 NaNs (100% complete) |
| **6** | `relative_humidity` | Meteorology | $\%$ | ERA5 surface reanalysis at station coordinates | 0 NaNs (100% complete) |
| **7** | `temperature` | Meteorology | $^\circ\text{C}$ | ERA5 surface reanalysis at station coordinates | 0 NaNs (100% complete) |
| **8** | `rainfall` | Meteorology | $\text{mm}$ | ERA5 hourly total precipitation (wet scavenging proxy) | 0 NaNs (100% complete) |
| **9** | `wind_direction` | Meteorology | Degrees ($^\circ$) | ERA5 10m surface wind bearing ($0\text{--}360^\circ$) | 0 NaNs (100% complete) |
| **10** | `wind_speed` | Meteorology | $\text{m/s}$ | ERA5 10m surface wind velocity | 0 NaNs (100% complete) |
| **11** | `traffic_speed` | Traffic | $\text{km/h}$ | HKTD Speedmap: hourly mean link speed projected via IDW ($p=2$) | 2,416 NaNs (0.57%, archive outages) |
| **12** | `traffic_congestion` | Traffic | $[0.0, 1.0]$ | HKTD Speedmap: ordinal saturation projected via IDW ($p=2$) | 2,416 NaNs (0.57%, archive outages) |

**Tensor Geometry**: Monotonically ordered by `(station_id, timestamp)` across $16 \text{ stations} \times 26,304 \text{ hours} = 420,864$ rows, reshaped to $\mathbf{X} \in \mathbb{R}^{16 \times 26,304 \times 13}$ ($5,471,232$ total values). Validated with 9/9 automated assertions (`alignment_validation.json`).
