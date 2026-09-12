# 04 - Spatial Alignment & 13-Channel Formulation

> **Previous**: [[03 - Missingness Architecture (Natural vs Simulated)]] | **Next**: [[05 - Feature Engineering & Normalization]] | **Index**: [[00 - Overview & Pipeline Architecture]]

---

## 1. Overview

In urban environmental physics, monitoring sensors are rarely co-located in the same room. Air pollution analyzers sit on building rooftops or roadside curbsides; weather sensors sit on hilltop masts or offshore buoys; traffic cameras sit over expressways.

To assemble a unified multi-modal tensor, the spatial coordinates of the **16 air monitoring stations** serve as the physical anchors. All other variables (weather, traffic) are aligned to these exact 16 spatial coordinates.

---

## 2. Spatial Grounding (The 16 Anchor Stations)

```
                            HONG KONG MONITORING TOPOGRAPHY
                            
                                   [Tai Po]             [Tap Mun] (Rural Baseline)
                                      │                      │
            [Yuen Long]         [Sha Tin]                    │
                 │                    │                      │
      [Tuen Mun] │          [Tsuen Wan]                      │
           │     │                │                          │
           │     │         [Kwai Chung]  [Sham Shui Po]      │
           │     │                │              │           │
           │     │                └──[Mong Kok]* │           └──[Tseung Kwan O]
           │     │                         │     │                    │
     [Tung Chung]│                 [Central]*    └──[Kwun Tong]       │
                 │                     │                │             │
                 └─────────────[Central/Western]    [Eastern]─────────┘
                                       │
                                [Causeway Bay]*
                                
                 * Denotes Roadside Corridors (street canyons with heavy traffic)
```

### 2.1 Spatial Typology Breakdown
The 16 stations span three critical environmental archetypes:
1. **Urban / Suburban General (12 stations)**: Central/Western, Eastern, Kwun Tong, Sham Shui Po, Kwai Chung, Tsuen Wan, Tseung Kwan O, Yuen Long, Tuen Mun, Tung Chung, Tai Po, Sha Tin.
   - Elevation: $13\text{m} - 28\text{m}$ above ground level (rooftops).
   - Measures general population exposure and ambient neighborhood air.
2. **Rural Background (1 station)**: Tap Mun.
   - Elevation: $11\text{m}$.
   - Located on an isolated northeastern island with virtually zero local emissions. Serves as regional baseline.
3. **Urban Roadside (3 stations)**: Causeway Bay, Central, Mong Kok.
   - Elevation: $3.0\text{m} - 4.5\text{m}$ (pedestrian breathing height).
   - Located within dense urban street canyons adjacent to major vehicular thoroughfares. Dominated by primary vehicle exhaust ($\text{NO}_2, \text{PM}_{2.5}$).

---

## 3. The 13 Channels Defined

The canonical dataset consists of exactly 13 channels per station-hour:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           THE 13-CHANNEL MULTI-MODAL MATRIX                             │
├───────────────┬─────────────────────────────────────────────────────────────────────────┤
│ Channels 0-4  │ AIR POLLUTANTS (EPD): PM2.5, PM10, NO2, O3, SO2                         │
│ Channels 5-10 │ METEOROLOGY (Open-Meteo & HKO): TEMP, RH, WS, WD, PRES, RAIN            │
│ Channels 11-12│ TRAFFIC DYNAMICS (TD ATC): SPEED, VOL                                   │
└───────────────┴─────────────────────────────────────────────────────────────────────────┘
```

| Index | Name | Column | Unit | Physical Role in Imputation |
| :---: | :--- | :--- | :---: | :--- |
| `0` | $\text{PM}_{2.5}$ | `pm25` | $\mu\text{g/m}^3$ | Fine combustion particulate matter; primary target. |
| `1` | $\text{PM}_{10}$ | `pm10` | $\mu\text{g/m}^3$ | Coarse dust and mechanical friction particulates. |
| `2` | $\text{NO}_2$ | `no2` | $\mu\text{g/m}^3$ | Vehicle combustion tracer; strongly inversely correlated with ozone. |
| `3` | $\text{O}_3$ | `o3` | $\mu\text{g/m}^3$ | Secondary photochemical oxidant; strongly driven by solar radiation. |
| `4` | $\text{SO}_2$ | `so2` | $\mu\text{g/m}^3$ | Industrial and marine shipping fuel tracer. |
| `5` | Air Temperature | `temperature` | $^\circ\text{C}$ | Drives chemical reaction rates and atmospheric boundary layer height. |
| `6` | Relative Humidity | `relative_humidity` | $\%$ | Influences particulate hygroscopic growth and secondary aerosol formation. |
| `7` | Wind Speed | `wind_speed` | $\text{m/s}$ | Controls horizontal pollutant dispersion and ventilation. |
| `8` | Wind Direction | `wind_direction` | Degrees | Indicates source trajectory (oceanic sea breeze vs continental plume). |
| `9` | Surface Pressure | `pressure` | $\text{hPa}$ | Tracks synoptic weather systems (anticyclones trap pollutants). |
| `10` | Rainfall | `rainfall` | $\text{mm}$ | Wet deposition / scavenging of suspended particulates. |
| `11` | Traffic Speed | `traffic_speed` | $\text{km/h}$ | Congestion indicator; low speed implies stop-and-go emission spikes. |
| `12` | Traffic Volume | `traffic_volume` | $\text{veh/h}$ | Direct emission source proxy near roadside stations. |

---

## 4. Spatio-Temporal Alignment Protocol

### 4.1 Meteorological Coordinate Matching
Because the Open-Meteo reanalysis archive can be queried at arbitrary geographic coordinates, we query each weather variable at the exact coordinates $(\text{Lat}_i, \text{Lon}_i)$ of station $i$. This eliminates spatial interpolation error for meteorological features.

### 4.2 Traffic Link Matching & Spatial IDW
1. For **Roadside Stations** (Causeway Bay, Central, Mong Kok): Traffic flow and speed are extracted directly from the co-located Transport Department detectors on Hennessy Road, Des Voeux Road, and Nathan Road.
2. For **General Stations**: Inverse Distance Weighting (IDW) interpolates traffic census indices based on neighboring arterial road links:
   $$\text{Traffic}(s) = \sum_{k=1}^K \frac{w_k}{\sum_j w_j} \text{Traffic}(d_k), \quad w_k = \frac{1}{\text{dist}(s, d_k)^2}$$

---

## 5. Master Canonical Tensor Dimensions

The primary numerical asset produced by the pipeline is stored in `data/canonical/`:

$$\mathbf{X} \in \mathbb{R}^{16 \times 26,304 \times 13}$$
$$\mathbf{M}_{\text{obs}} \in \{0, 1\}^{16 \times 26,304 \times 13}$$

### Total Tensor Magnitude
$$\text{Total Elements} = 16 \times 26,304 \times 13 = \mathbf{5,471,232}\text{ numerical values}$$

- **File**: `data/canonical/tensor_features.npy` (Data matrix, `float32`, $\approx 21.9\text{ MB}$)
- **File**: `data/canonical/tensor_mask.npy` (Observation mask, `uint8`, $\approx 5.5\text{ MB}$)
- **Index**: `data/canonical/timestamps.csv` ($26,304$ datetime strings)
- **Metadata**: `data/canonical/channels.json` (List of 13 channel identifiers)
