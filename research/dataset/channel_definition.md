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

## 2. Comparison with Prior Codebase Assumptions

| Domain | CTDI Ground Truth (Table I) | Prior Codebase Assumption | Match? | Impact & Resolution |
| :--- | :--- | :--- | :---: | :--- |
| **Pollutants** | $\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{SO}_2, \text{O}_3$ | Same 5 criteria pollutants | **YES** | Perfect 1:1 alignment. |
| **Meteorology** | **`Visibility` ($\text{km}$)** | `rainfall` ($\text{mm}$) | **NO** | Critical divergence. Prior pipeline assumed rainfall. Must acquire HKO visibility records. |
| **Traffic** | **`Traffic speed` & `Traffic congestion`** | `traffic_speed` & `traffic_volume` | **NO** | Critical divergence. `traffic_volume` from ATC is completely absent from CTDI; must use saturation level from 607-road Speedmap. |
