# Reconstructed CTDI 13-Channel Dataset Specification

**Document Purpose**: Define the exact 13 multi-modal channels of the CTDI Hong Kong dataset ($X \in \mathbb{R}^{16 \times 26,304 \times 13}$), established directly from Table I, Section III-A, Section IV-A, and Section V-C of the published paper (*IEEE Transactions on Big Data*, 2025).

---

## 1. Channel Definitions (Channels 1 to 13)

### Channel 1
- **Variable**: `pm25` (Fine Suspended Particulates)
- **Source**: Hong Kong Environmental Protection Department (HKEPD) Database [80]
- **Unit**: $\mu\text{g/m}^3$
- **CTDI Evidence**: Table I explicitly specifies "$\text{PM}_{2.5}$", Unit $\mu\text{g/m}^3$, 16 stations, 1 hour update frequency.
- **Spatial Mapping**: Direct physical measurement at the 16 air quality monitoring stations.
- **Temporal Resolution**: Hourly native resolution ($26,304\text{ hours}$).
- **Confidence**: **`HIGH`**

### Channel 2
- **Variable**: `pm10` (Respirable Suspended Particulates)
- **Source**: HKEPD Database [80]
- **Unit**: $\mu\text{g/m}^3$
- **CTDI Evidence**: Table I explicitly specifies "$\text{PM}_{10}$", Unit $\mu\text{g/m}^3$, 16 stations, 1 hour update frequency.
- **Spatial Mapping**: Direct physical measurement at the 16 air quality monitoring stations.
- **Temporal Resolution**: Hourly native resolution ($26,304\text{ hours}$).
- **Confidence**: **`HIGH`**

### Channel 3
- **Variable**: `no2` (Nitrogen Dioxide)
- **Source**: HKEPD Database [80]
- **Unit**: $\mu\text{g/m}^3$
- **CTDI Evidence**: Table I explicitly specifies "$\text{NO}_2$", Unit $\mu\text{g/m}^3$, 16 stations, 1 hour update frequency.
- **Spatial Mapping**: Direct physical measurement at the 16 air quality monitoring stations.
- **Temporal Resolution**: Hourly native resolution ($26,304\text{ hours}$).
- **Confidence**: **`HIGH`**

### Channel 4
- **Variable**: `so2` (Sulphur Dioxide)
- **Source**: HKEPD Database [80]
- **Unit**: $\mu\text{g/m}^3$
- **CTDI Evidence**: Table I explicitly specifies "$\text{SO}_2$", Unit $\mu\text{g/m}^3$, 16 stations, 1 hour update frequency.
- **Spatial Mapping**: Direct physical measurement at the 16 air quality monitoring stations.
- **Temporal Resolution**: Hourly native resolution ($26,304\text{ hours}$).
- **Confidence**: **`HIGH`**

### Channel 5
- **Variable**: `o3` (Ozone)
- **Source**: HKEPD Database [80]
- **Unit**: $\mu\text{g/m}^3$
- **CTDI Evidence**: Table I explicitly specifies "$\text{O}_3$", Unit $\mu\text{g/m}^3$, 16 stations, 1 hour update frequency.
- **Spatial Mapping**: Direct physical measurement at the 16 air quality monitoring stations.
- **Temporal Resolution**: Hourly native resolution ($26,304\text{ hours}$).
- **Confidence**: **`HIGH`**

### Channel 6
- **Variable**: `pressure` (Atmospheric Pressure)
- **Source**: Hong Kong Observatory Open Database [81]
- **Unit**: $\text{hPa}$
- **CTDI Evidence**: Table I explicitly specifies "Pressure", Unit $\text{hPa}$, 47 stations, 10 min update frequency.
- **Spatial Mapping**: Spatially mapped from 47 HKO Automatic Weather Stations to 16 air stations via IDW ($p=2$).
- **Temporal Resolution**: 10-minute records averaged over each hour.
- **Confidence**: **`HIGH`**

### Channel 7
- **Variable**: `relative_humidity` (Relative Humidity)
- **Source**: HKO Open Database [81]
- **Unit**: $\%$
- **CTDI Evidence**: Table I explicitly specifies "Relative humidity", Unit $\%$, 47 stations, 10 min update frequency.
- **Spatial Mapping**: Spatially mapped from 47 HKO AWS stations to 16 air stations via IDW ($p=2$).
- **Temporal Resolution**: 10-minute records averaged over each hour.
- **Confidence**: **`HIGH`**

### Channel 8
- **Variable**: `temperature` (Air Temperature)
- **Source**: HKO Open Database [81]
- **Unit**: $^\circ\text{C}$
- **CTDI Evidence**: Table I explicitly specifies "Temperature", Unit $^\circ\text{C}$, 47 stations, 10 min update frequency.
- **Spatial Mapping**: Spatially mapped from 47 HKO AWS stations to 16 air stations via IDW ($p=2$).
- **Temporal Resolution**: 10-minute records averaged over each hour.
- **Confidence**: **`HIGH`**

### Channel 9
- **Variable**: `visibility` (Horizontal Visibility)
- **Source**: HKO Open Database [81]
- **Unit**: $\text{km}$
- **CTDI Evidence**: Table I explicitly specifies "Visibility", Unit $\text{km}$, 47 stations, 10 min update frequency.
- **Spatial Mapping**: Spatially mapped from HKO monitoring network to 16 air stations via IDW ($p=2$).
- **Temporal Resolution**: 10-minute records averaged over each hour.
- **Confidence**: **`HIGH`**  
*(Note: Replaces previous informal project substitution of "rainfall".)*

### Channel 10
- **Variable**: `wind_direction` (Wind Direction)
- **Source**: HKO Open Database [81]
- **Unit**: $\text{N/A}$ (Compass degree azimuth $0\text{--}360^\circ$ or vector decomposed components)
- **CTDI Evidence**: Table I explicitly specifies "Wind direction", Unit $\text{N/A}$, 47 stations, 10 min update frequency.
- **Spatial Mapping**: Spatially mapped from 47 HKO AWS stations to 16 air stations via IDW ($p=2$).
- **Temporal Resolution**: 10-minute records averaged over each hour.
- **Confidence**: **`HIGH`**

### Channel 11
- **Variable**: `wind_speed` (Wind Speed)
- **Source**: HKO Open Database [81]
- **Unit**: $\text{km/h}$
- **CTDI Evidence**: Table I explicitly specifies "Wind speed", Unit $\text{km/h}$, 47 stations, 10 min update frequency.
- **Spatial Mapping**: Spatially mapped from 47 HKO AWS stations to 16 air stations via IDW ($p=2$).
- **Temporal Resolution**: 10-minute records averaged over each hour.
- **Confidence**: **`HIGH`**

### Channel 12
- **Variable**: `traffic_speed` (Road Vehicular Speed)
- **Source**: Hong Kong Traffic Speed Map [82] (`http://resource.data.one.gov.hk/td/speedmap.xml`)
- **Unit**: $\text{km/h}$
- **CTDI Evidence**: Table I explicitly specifies "Traffic speed", Unit $\text{km/h}$, 607 roads, 5min update frequency. Section III-A explicitly cites traffic speed as a primary urban factor.
- **Spatial Mapping**: Spatially mapped from 607 road link centroids to 16 air stations via IDW ($p=2$).
- **Temporal Resolution**: 5-minute link observations averaged over each hour.
- **Confidence**: **`HIGH`**

### Channel 13
- **Variable**: `traffic_congestion` / `road_saturation_level` (Traffic Congestion / Saturation Level)
- **Source**: Hong Kong Traffic Speed Map [82] (`http://resource.data.one.gov.hk/td/speedmap.xml`)
- **Unit**: $\text{N/A}$ (Categorical saturation level: `TRAFFIC GOOD` [0], `TRAFFIC AVERAGE` [1], `TRAFFIC BAD` [2])
- **CTDI Evidence**: Table I explicitly specifies "Traffic congestion", Unit $\text{N/A}$, 607 roads, 5min update frequency. Section V-C discusses "traffic conditions".
- **Spatial Mapping**: Spatially mapped from 607 road link centroids to 16 air stations via IDW ($p=2$).
- **Temporal Resolution**: 5-minute link observations averaged over each hour.
- **Confidence**: **`HIGH`**

---

## 2. Comparison of Meteorological Variables: CTDI vs Current Implementation

| CTDI Variable (Table I) | Current Codebase Variable | Exact Match? | Unit in CTDI | Unit in Current | Source Alignment & Difference |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Pressure** | `pressure` | **YES** | $\text{hPa}$ | $\text{hPa}$ | Exact match. Measured by HKO Automatic Weather Stations. |
| **Relative humidity** | `relative_humidity` | **YES** | $\%$ | $\%$ | Exact match. Measured by HKO Automatic Weather Stations. |
| **Temperature** | `temperature` | **YES** | $^\circ\text{C}$ | $^\circ\text{C}$ | Exact match. Measured by HKO Automatic Weather Stations. |
| **Visibility** | `rainfall` | **NO** | $\text{km}$ | $\text{mm}$ | **Critical divergence**: CTDI Table I explicitly uses **Visibility** ($\text{km}$), whereas the interim codebase had substituted `rainfall`. |
| **Wind direction** | `wind_direction` | **YES** | N/A | Degrees ($0\text{--}360^\circ$) | Exact semantic match. CTDI marks unit as N/A in Table I. |
| **Wind speed** | `wind_speed` | **YES** | $\text{km/h}$ | $\text{m/s}$ | Semantic match. Unit in CTDI is $\text{km/h}$ ($1\text{ m/s} = 3.6\text{ km/h}$). |

---

## 3. Comparison of Traffic Variables: CTDI vs Prior Pipeline Assumptions

| CTDI Variable (Table I) | Prior Codebase Assumption | Exact Match? | Unit in CTDI | Prior Unit | Evidence & Impact |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Traffic speed** | `traffic_speed` | **YES** | $\text{km/h}$ | $\text{km/h}$ | Exact match. Verified across 607 roads. |
| **Traffic congestion** | `traffic_volume` | **NO** | N/A | $\text{veh/h}$ | **Severe misconception in prior code**: Prior code assumed `traffic_volume` from Annual Traffic Census (ATC). CTDI Table I explicitly uses **`Traffic congestion`** ($\text{N/A}$) from the Traffic Speed Map. |
