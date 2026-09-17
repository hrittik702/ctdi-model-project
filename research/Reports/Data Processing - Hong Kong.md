<img src="https://cd.epic.epd.gov.hk/EPICDI/air/station/images/air_station_map.jpg">
# Complete Data Processing Guide: From Raw Acquisition to Model-Ready Tensors

> **Project**: Context-Aware Generative Imputation of Air Pollution Using SLM-Conditioned Diffusion  
> **Benchmark Reference**: Yangwen Yu, Victor O. K. Li, Jacqueline C. K. Lam, Kelvin Chan, Qi Zhang, *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, **IEEE Transactions on Big Data**, vol. 11, 2025.  
> **Target Domain**: Hong Kong Special Administrative Region (2019-01-01 to 2021-12-31, 1,096 days = 26,304 continuous hours)

---

## Table of Contents
1. [End-to-End Pipeline Architecture](#1-end-to-end-pipeline-architecture)
2. [Phase 1: Raw Data Sources & Acquisition](#2-phase-1-raw-data-sources--acquisition)
3. [Phase 2: Cleaning, Translating & Format Harmonization](#3-phase-2-cleaning-translating--format-harmonization)
4. [Phase 3: Handling Natural Missingness vs. Simulated Missingness](#4-phase-3-handling-natural-missingness-vs-simulated-missingness)
5. [Phase 4: Spatio-Temporal Alignment & Canonical Tensor Formulation](#5-phase-4-spatio-temporal-alignment--canonical-tensor-formulation)
6. [Phase 5: Feature Engineering & Normalization](#6-phase-5-feature-engineering--normalization)
7. [Phase 6: 24-Hour Sliding Window Segmentation](#7-phase-6-24-hour-sliding-window-segmentation)
8. [Phase 7: Environmental Context Generation for SLM Conditioning](#8-phase-7-environmental-context-generation-for-slm-conditioning)
9. [Phase 8: Directory Layout & File Catalog](#9-phase-8-directory-layout--file-catalog)
10. [Phase 9: Step-by-Step Practical Execution Plan](#10-phase-9-step-by-step-practical-execution-plan)

---

## 1. End-to-End Pipeline Architecture

The entire data workflow transforms heterogeneous, bilingual government archives into synchronized, normalized 4D tensors ready for PyTorch diffusion and transformer models.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. RAW DATA INGESTION                                                                          │
│  - HK EPD: 36 monthly pollutant archives (PM2.5, PM10, NO2, O3, SO2, NOx, CO)                  │
│  - HKO & Open-Meteo: Hourly meteorology (TEMP, RH, WS, WD, PRES, RAIN) at 16 coordinates       │
│  - Transport Dept: Annual Traffic Census (ATC) survey files (2019-2021), detectors, KMZ        │
│  - Spatial Metadata: 18 Air Stations (16 included + 2 excluded), 52 Weather, 76 Detectors      │ 
└───────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. CLEANING & HARMONIZATION                                                                    │
│  - Strip Chinese characters & bilingual headers -> Standard snake_case English identifiers     │
│  - Harmonize Hour 1..24 -> Continuous ISO Datetime (2019-01-01 00:00 to 2021-12-31 23:00)      │
│  - Sanitize string flags ('N.A.', blanks) -> IEEE 754 NaN floats                               │
│  - Filter exactly the 16 continuous stations (exclude Southern #84 and North #85)              │
└───────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. CANONICAL MULTI-MODAL MATRIX & OBSERVATION MASKS                                            │
│  - Feature Tensor: X_canonical in R^(16 stations x 26,304 hours x 13 channels)                 │
│  - Natural Observation Mask: M_obs in {0, 1}^(16 x 26,304 x 13)                                │
│    (1 = true sensor reading, 0 = natural missingness ~2.5%)                                    │
│  - Station Metadata Matrix: Coordinates (lat, lon), sampling heights, station types            │
└───────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. PREPROCESSING & NORMALIZATION                                                               │
│  - Temporal Split: Train (70%, 2019-01 to 2021-02), Val (15%), Test (15%, 2021-07 to 2021-12)  │
│  - Fit Scalers (Min-Max or Z-score) on Train set ONLY (zero data leakage into Test)            │
│  - Cyclic time encodings (Hour sin/cos, Day-of-week sin/cos, Month sin/cos)                    │
└───────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. WINDOWING & BENCHMARK MISSINGNESS SIMULATION                                                │
│  - 24-Hour Sliding Windows: [B, 16 stations, 24 hours, 13 channels]                            │
│  - Simulated Missingness Masks (M_eval): 10%, 30%, 50%, 70% missingness rates                  │
│    * Pattern A: Random Point Missing (MCAR)                                                    │
│    * Pattern B: Continuous / Block Missing (temporal outages)                                  │
│    * Pattern C: Spatial Station Outage (entire station offline)                                │
│  - Environmental Context Builder: Structured English text prompts for SLM conditioning         │
└───────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                │
                                                ▼
                                    READY FOR MODEL TRAINING
                   [Data: (B, 16, 24, 13), Mask: (B, 16, 24, 13), Context: List[str]]
```

---

## 2. Phase 1: Raw Data Sources & Acquisition

### 2.1 The 13 Required Channels (Yu et al., CTDI 2025)

The CTDI paper defines a 13-channel spatio-temporal feature space:

| Channel # | Feature Name                |      Symbol       |      Source      |       Units       | Range in Raw Data | Description                          |
| :-------: | :-------------------------- | :---------------: | :--------------: | :---------------: | :---------------: | :----------------------------------- |
|   **0**   | Fine Suspended Particulates | $\text{PM}_{2.5}$ |      HK EPD      | $\mu\text{g/m}^3$ |   $0.0 - 167.0$   | Primary target criteria pollutant    |
|   **1**   | Respirable Particulates     | $\text{PM}_{10}$  |      HK EPD      | $\mu\text{g/m}^3$ |   $0.0 - 241.0$   | Coarse particulate matter            |
|   **2**   | Nitrogen Dioxide            |   $\text{NO}_2$   |      HK EPD      | $\mu\text{g/m}^3$ |   $0.0 - 366.0$   | Key combustion pollutant             |
|   **3**   | Ozone                       |   $\text{O}_3$    |      HK EPD      | $\mu\text{g/m}^3$ |   $0.0 - 422.0$   | Photochemical secondary pollutant    |
|   **4**   | Sulphur Dioxide             |   $\text{SO}_2$   |      HK EPD      | $\mu\text{g/m}^3$ |   $0.0 - 81.0$    | Industrial & marine fuel tracer      |
|   **5**   | Air Temperature             |   $\text{TEMP}$   | Open-Meteo / HKO | $^\circ\text{C}$  |   $2.9 - 35.6$    | Hourly 2-meter air temperature       |
|   **6**   | Relative Humidity           |    $\text{RH}$    | Open-Meteo / HKO |       $\%$        |  $13.0 - 100.0$   | Hourly relative humidity             |
|   **7**   | Wind Speed                  |    $\text{WS}$    | Open-Meteo / HKO |   $\text{m/s}$    |   $0.0 - 17.4$    | Hourly 10-meter wind velocity        |
|   **8**   | Wind Direction              |    $\text{WD}$    | Open-Meteo / HKO |      Degrees      |   $0.0 - 360.0$   | Compass angle ($0^\circ$ = North)    |
|   **9**   | Surface Pressure            |   $\text{PRES}$   | Open-Meteo / HKO |   $\text{hPa}$    | $986.5 - 1029.9$  | Atmospheric barometric pressure      |
|  **10**   | Rainfall                    |   $\text{RAIN}$   | Open-Meteo / HKO |    $\text{mm}$    |   $0.0 - 61.8$    | Hourly total precipitation           |
|  **11**   | Traffic Speed               |  $\text{SPEED}$   |   HK TD (ATC)    |   $\text{km/h}$   |  $10.0 - 100.0$   | Spatially interpolated traffic speed |
|  **12**   | Traffic Volume              |   $\text{VOL}$    |   HK TD (ATC)    |  $\text{veh/h}$   |  $50.0 - 6500.0$  | Spatially interpolated hourly flow   |

### 2.2 The 16 Air Quality Stations vs. 2 Excluded Stations

Hong Kong currently operates 18 fixed monitoring stations. The CTDI benchmark uses **exactly 16 stations** and excludes 2 newer stations.

```
                    HONG KONG AIR MONITORING NETWORK (16 STATIONS)
                    
                             [Tai Po]           [Tap Mun] (Rural Background)
                                │                    │
         [Yuen Long]      [Sha Tin]                  │
              │                 │                    │
   [Tuen Mun] │        [Tsuen Wan]                   │
        │     │             │                        │
        │     │      [Kwai Chung]  [Sham Shui Po]    │
        │     │             │             │          │
        │     │             └──[Mong Kok]*│          └──[Tseung Kwan O]
        │     │                       │   │                   │
  [Tung Chung]│              [Central]*   └──[Kwun Tong]      │
              │                  │               │            │
              └──────────[Central/Western]   [Eastern]────────┘
                                 │
                         [Causeway Bay]*
                         
              * Denotes Roadside Station (near heavy vehicular corridors)
```

#### Complete Station Catalog (`data/raw/station_metadata/air_quality_stations.csv`):
1. **Central/Western** (General, ID 80, Lat 22.2848, Lon 114.1441, Height 16m)
2. **Eastern** (General, ID 73, Lat 22.2831, Lon 114.2190, Height 15m)
3. **Kwun Tong** (General, ID 74, Lat 22.3107, Lon 114.2312, Height 15m)
4. **Sham Shui Po** (General, ID 66, Lat 22.3304, Lon 114.1591, Height 17m)
5. **Kwai Chung** (General, ID 72, Lat 22.3569, Lon 114.1293, Height 13m)
6. **Tsuen Wan** (General, ID 77, Lat 22.3715, Lon 114.1146, Height 17m)
7. **Tseung Kwan O** (General, ID 83, Lat 22.3173, Lon 114.2596, Height 16m)
8. **Yuen Long** (General, ID 70, Lat 22.4450, Lon 114.0227, Height 25m)
9. **Tuen Mun** (General, ID 82, Lat 22.3911, Lon 113.9768, Height 27m)
10. **Tung Chung** (General, ID 78, Lat 22.2885, Lon 113.9431, Height 28m)
11. **Tai Po** (General, ID 69, Lat 22.4508, Lon 114.1644, Height 28m)
12. **Sha Tin** (General, ID 75, Lat 22.3764, Lon 114.1846, Height 25m)
13. **Tap Mun** (General/Rural, ID 76, Lat 22.4757, Lon 114.3619, Height 11m)
14. **Causeway Bay** (Roadside, ID 71, Lat 22.2801, Lon 114.1855, Height 3m)
15. **Central** (Roadside, ID 79, Lat 22.2802, Lon 114.1606, Height 4.5m)
16. **Mong Kok** (Roadside, ID 81, Lat 22.3225, Lon 114.1685, Height 3m)

#### The 2 Excluded Stations (and Why):
- **Southern (ID 84)** and **North (ID 85)**: Both commissioned on **July 10, 2020**. They did not exist in 2019 or early 2020. Including them would create an 18-month structural gap (50% missingness) that would distort real temporal learning. They are documented in metadata but excluded from the tensor.

---

## 3. Phase 2: Cleaning, Translating & Format Harmonization

### 3.1 Resolving Chinese Characters and Bilingual Artifacts

Government datasets from Hong Kong are published bilingually:
- EPD file header remarks: `備註：空氣質素健康指數時報紀錄...`
- Table column headers: `日期,時間,中西區,東區...`
- Weather variables: `日平均氣溫(攝氏度) - 天文台`
- Road links: `黃泥涌峽天橋`, `獅子山隧道公路`

#### How our pipeline strips all foreign text:
1. **Explicit Column Normalization**: We never pass raw text columns into our numerical matrices. Instead, an explicit schema dictionary maps raw names to standard English identifiers:
   ```python
   COL_MAP = {
       "PM2.5": "pm25",
       "PM10": "pm10",
       "NO2": "no2",
       "O3": "o3",
       "SO2": "so2",
       "temperature_2m": "temperature",
       "relative_humidity_2m": "relative_humidity",
       "wind_speed_10m": "wind_speed",
       "wind_direction_10m": "wind_direction",
       "surface_pressure": "pressure",
       "precipitation": "rainfall"
   }
   ```
2. **Pure Float Tensors**: When PyTorch loads the processed dataset, it loads a tensor of `torch.float32` values. No text or language tokens exist inside the numeric feature tensor.
3. **English Context for SLM**: Where text *is* needed (for the Small Language Model text conditioning in our diffusion framework), our context builder writes purely in English (e.g. `"Station: Causeway Bay, Type: Roadside, District: Wan Chai, Wind: 3.5 m/s East-Southeast"`).

### 3.2 Date & Hour Alignment (The 26,304-Hour Continuous Grid)

In raw EPD CSVs:
- `DATE` is formatted as `D/M/YYYY` (e.g. `1/1/2019` to `31/12/2021`).
- `HOUR` runs from `01` to `24`.

#### The Mapping Rule:
In Hong Kong EPD conventions, `HOUR=01` represents the 1-hour average from 00:00 to 01:00 (hour ending 01:00), and `HOUR=24` represents the hour ending 24:00 (23:00 to 00:00).
We convert this to standard 0-indexed ISO datetime timestamps:
$$\text{timestamp} = \text{pd.to\_datetime}(\text{DATE}, \text{format}='\%d/\%m/\%Y') + (\text{HOUR} - 1) \times \text{1 hour}$$

- `1/1/2019, HOUR=01` $\rightarrow$ `2019-01-01 00:00:00`
- `1/1/2019, HOUR=24` $\rightarrow$ `2019-01-01 23:00:00`
- `31/12/2021, HOUR=24` $\rightarrow$ `2021-12-31 23:00:00`

#### Verification Math:
- 2019 (standard year): 365 days
- 2020 (leap year): 366 days
- 2021 (standard year): 365 days
- Total days = $365 + 366 + 365 = \mathbf{1,096}\text{ days}$
- Total hours per station = $1,096 \times 24 = \mathbf{26,304}\text{ hours}$
- Total entries across 16 stations = $16 \times 26,304 = \mathbf{420,864}\text{ rows}$

### 3.3 Numeric Sanitization
- Raw string missingness flags (`"N.A."`, `"***"`, `"# data incomplete"`, empty strings `""`) are coerced into `np.nan` (IEEE 754 floating-point Not-a-Number).
- Valid pollutant concentrations are parsed as standard `float32`.

---

## 4. Phase 3: Handling Natural Missingness vs. Simulated Missingness

This is the most critical conceptual distinction in air pollution imputation research.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE TWO FORMS OF MISSINGNESS                           │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│ 1. NATURAL MISSINGNESS (~2.5%)            │ 2. SIMULATED BENCHMARK MISSINGNESS         │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ • Cause: Sensor calibration, power dips   │ • Cause: Artificially injected by code     │
│ • True value is UNKNOWN to everyone       │ • True value is SECRETLY KNOWN             │
│ • Masked out during loss calculation:     │ • Used to evaluate accuracy (RMSE, MAE):   │
│   Loss = || M_obs ⊙ (X - X_pred) ||       │   RMSE = sqrt( mean( (X_true - X_pred)^2 ) │
│   (Never penalize on unknown labels)      │   (Evaluated strictly on held-out points)  │
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

### 4.1 Natural Missingness Rates in Hong Kong EPD (Raw Ground Truth)

Our inspection of the 420,864 hourly records reveals the real-world operational health of the Hong Kong network:

| Pollutant | Observed Valid Hours | Missing Hours (`N.A.`) | Natural Missingness Rate | Min ($\mu\text{g/m}^3$) | Max ($\mu\text{g/m}^3$) | Mean ($\mu\text{g/m}^3$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $\text{PM}_{2.5}$ | 410,207 | 10,657 | **2.53%** | 0.0 | 167.0 | 17.5 |
| $\text{PM}_{10}$ | 409,469 | 11,395 | **2.71%** | 0.0 | 241.0 | 29.7 |
| $\text{NO}_2$ | 409,213 | 11,651 | **2.77%** | 0.0 | 366.0 | 42.8 |
| $\text{O}_3$ | 409,747 | 11,117 | **2.64%** | 0.0 | 422.0 | 50.8 |
| $\text{SO}_2$ | 409,808 | 11,056 | **2.63%** | 0.0 | 81.0 | 4.9 |

> [!NOTE]
> This ~2.5% natural missingness is realistic and high quality for a 3-year government environmental monitoring network (>97.3% operational uptime).

### 4.2 The Natural Observation Mask ($\mathbf{M}_{\text{obs}}$)

We define a binary mask tensor $\mathbf{M}_{\text{obs}} \in \{0, 1\}^{16 \times 26,304 \times 13}$:
$$\mathbf{M}_{\text{obs}}[s, t, c] = \begin{cases} 1 & \text{if station } s \text{ at hour } t \text{ had a valid observed value for channel } c \\ 0 & \text{if station } s \text{ at hour } t \text{ was naturally missing (NaN)} \end{cases}$$

For meteorology channels (Channels 5–10), the Open-Meteo ERA5-Land series is 100% complete, so $\mathbf{M}_{\text{obs}}[s, t, 5..10] = 1$ everywhere.

### 4.3 Simulated Benchmark Missingness Patterns (CTDI Protocol)

To reproduce the benchmark evaluations from the CTDI paper, we implement 3 standard synthetic missingness mechanisms across 4 missing rates ($10\%, 30\%, 50\%, 70\%$):

1. **Random Point Missing (MCAR - Missing Completely at Random)**:
   - Individual cells $(s, t, c)$ are dropped independently with probability $p \in \{0.1, 0.3, 0.5, 0.7\}$.
   - Simulates sporadic transmission loss or transient sensor jitter.
2. **Continuous Block Missing (Temporal Outage)**:
   - Contiguous chunks of time (e.g. 4, 8, 12, or 24 consecutive hours) are knocked out simultaneously at a station.
   - Simulates physical hardware malfunction, power loss, or sensor maintenance.
3. **Spatial Station Outage**:
   - An entire station's observations across all 5 pollutants are knocked out for a given day.
   - Tests whether the spatial attention mechanism in the model can reconstruct the station's readings solely from neighboring stations and meteorology.

#### The Evaluation Mask ($\mathbf{M}_{\text{eval}}$) and Loss Masking:
Let $\mathbf{M}_{\text{sim}}$ be the binary mask indicating which values were artificially removed ($0 = \text{removed}, 1 = \text{kept}$).
The evaluation mask is:
$$\mathbf{M}_{\text{eval}} = \mathbf{M}_{\text{obs}} \odot (1 - \mathbf{M}_{\text{sim}})$$
- $\mathbf{M}_{\text{eval}} = 1$ **only** where a genuine ground-truth value existed *and* was intentionally hidden.
- Test metrics (RMSE, MAE, MRE) are computed strictly over the coordinates where $\mathbf{M}_{\text{eval}} = 1$:
  $$\text{RMSE} = \sqrt{\frac{\sum_{s,t,c} \mathbf{M}_{\text{eval}} \odot (\mathbf{X} - \hat{\mathbf{X}})^2}{\sum_{s,t,c} \mathbf{M}_{\text{eval}}}}$$

---

## 5. Phase 4: Spatio-Temporal Alignment & Canonical Tensor Formulation

### 5.1 Spatial Alignment (Anchoring to the 16 Stations)

In urban environmental physics, pollutants are monitored at fixed ground locations. Meteorological weather stations and traffic sensors, however, are distributed at different physical coordinates.
To combine them into a single tensor, all channels must be mapped onto the **16 air monitoring station locations**:

```
[HKO Weather Stations] ──(Spatial IDW / Co-located Coordinates)──┐
                                                                 ├──> [16 Air Stations Grid]
[Traffic Detectors / ATC] ──(Nearest Arterial Link / IDW)────────┘
```

1. **Meteorology Mapping**:
   - We query the high-resolution grid at the exact coordinates $(\text{Lat}_i, \text{Lon}_i)$ of each of the 16 air stations. This eliminates spatial discrepancy between meteorological inputs and air quality stations.
2. **Traffic Mapping**:
   - For Roadside Stations (Causeway Bay, Central, Mong Kok), traffic detectors are matched to the immediate road links (Hennessy Road, Des Voeux Road, Nathan Road).
   - For General Stations, Inverse Distance Weighting (IDW) or district-level Annual Traffic Census (ATC) flow profiles are mapped to each station radius.

### 5.2 The Canonical Tensor Dimensions

The primary numerical asset produced by the data pipeline is saved to `data/canonical/`:

$$\mathbf{X} \in \mathbb{R}^{16 \times 26,304 \times 13}$$
$$\mathbf{M} \in \{0, 1\}^{16 \times 26,304 \times 13}$$

$$\text{Total Elements} = 16 \times 26,304 \times 13 = \mathbf{5,471,232}\text{ numerical values}$$

- Axis 0 ($S = 16$): Spatial monitoring station index ($0..15$).
- Axis 1 ($T = 26,304$): Continuous hourly timestamps ($0..26,303$).
- Axis 2 ($C = 13$): Feature channels ($0..12$).

---

## 6. Phase 5: Feature Engineering & Normalization

### 6.1 Train / Validation / Test Temporal Splits

To prevent look-ahead bias in time series, we perform **chronological splitting** (never random splitting):
- **Train Set**: $70\%$ (2019-01-01 00:00 to 2021-02-05 06:00, $\approx 18,412\text{ hours}$)
- **Validation Set**: $15\%$ (2021-02-05 07:00 to 2021-07-19 16:00, $\approx 3,946\text{ hours}$)
- **Test Set**: $15\%$ (2021-07-19 17:00 to 2021-12-31 23:00, $\approx 3,946\text{ hours}$)

### 6.2 Data Normalization (Zero-Leakage Rule)

```
[Raw Train Data] ──> Compute (Mean, Std) OR (Min, Max) ──> Fitted Scaler
                                                               │
      ┌────────────────────────────────────────────────────────┴──────────────────────────┐
      ▼                                                        ▼                          ▼
Scale Train Data                                         Scale Val Data            Scale Test Data
```

> [!CRITICAL]
> The normalization parameters ($\mu, \sigma$ or $x_{\min}, x_{\max}$) are computed **strictly on the Train split**, using only observed values where $\mathbf{M}_{\text{obs}} = 1$.
> They are stored in `data/processed/scalers.json` and reused to transform Validation and Test data. This guarantees zero data leakage from the future into the past.

### 6.3 Cyclical Time Embeddings

To allow neural attention layers to learn diurnal (day/night) and seasonal (summer/winter) rhythms without discontinuity at midnight or year-end, we encode cyclical timestamps:
$$\text{Hour}_{\sin} = \sin\left(\frac{2\pi \cdot \text{hour}}{24}\right), \quad \text{Hour}_{\cos} = \cos\left(\frac{2\pi \cdot \text{hour}}{24}\right)$$
$$\text{Day}_{\sin} = \sin\left(\frac{2\pi \cdot \text{dayofweek}}{7}\right), \quad \text{Day}_{\cos} = \cos\left(\frac{2\pi \cdot \text{dayofweek}}{7}\right)$$
$$\text{Month}_{\sin} = \sin\left(\frac{2\pi \cdot \text{month}}{12}\right), \quad \text{Month}_{\cos} = \cos\left(\frac{2\pi \cdot \text{month}}{12}\right)$$

---
·
## 7. Phase 6: 24-Hour Sliding Window Segmentation

### 7.1 Why 24 Hours?
The CTDI paper specifies input samples as **24-hour periods** ($T_{\text{window}} = 24$).
In atmospheric science, 24 hours captures one complete diurnal atmospheric cycle:
- Morning rush hour traffic peak (07:00 - 09:00): elevated $\text{NO}_2$, $\text{PM}_{2.5}$, $\text{CO}$.
- Solar noon photochemical peak (12:00 - 15:00): elevated temperature, UV, and secondary $\text{O}_3$ production.
- Evening traffic peak (18:00 - 20:00).
- Nighttime boundary layer collapse & surface inversion (00:00 - 06:00).

### 7.2 Sliding Window Formulation

```
Hour 0 ──────────── Hour 23   ──> Window 0  [16, 24, 13]
   Hour 1 ──────────── Hour 24   ──> Window 1  [16, 24, 13]
      Hour 2 ──────────── Hour 25   ──> Window 2  [16, 24, 13]
         ...
```

- **Window Length ($L$)**: 24 hours
- **Stride ($S_{\text{stride}}$)**:
  - In Training: $S_{\text{stride}} = 1\text{ hour}$ (overlapping windows to create $\approx 18,389$ training samples).
  - In Evaluation/Testing: $S_{\text{stride}} = 24\text{ hours}$ (non-overlapping contiguous days for unbiased reporting).
- **Single Window Tensor Shape**:
  $$\mathbf{X}_{\text{win}} \in \mathbb{R}^{16 \times 24 \times 13} \quad (16 \text{ stations}, 24 \text{ hours}, 13 \text{ channels})$$
- **PyTorch Batched Tensor**:
  $$\mathbf{X}_{\text{batch}} \in \mathbb{R}^{B \times 16 \times 24 \times 13}$$
  where $B$ is the batch size (e.g. 32 or 64).

---

## 8. Phase 7: Environmental Context Generation for SLM Conditioning

A distinctive advantage of our research pipeline over standard CTDI is **context-aware generative diffusion**: conditioning the diffusion model with a Small Language Model (SLM).

For each 24-hour sample window, our context builder (`src/context/builder.py`) generates a structured English environmental context prompt:

```text
[SAMPLE SLM CONTEXT PROMPT]
"Time: 2019-11-15, Season: Autumn.
Weather: Mean temperature 21.4°C, Relative Humidity 68%, Surface Pressure 1018 hPa.
Prevailing Wind: Moderate 4.2 m/s from North-East (inflow of regional air mass).
Precipitation: 0.0 mm (dry conditions favor particulate accumulation).
Spatial Domain: 16 stations across Hong Kong (13 General urban/rural, 3 Roadside corridors).
Traffic Activity: Normal weekday commuter profile, high volume along Causeway Bay & Central roadside."
```

- **Encoding**: The prompt is processed through a lightweight Small Language Model (e.g. Phi-2, Qwen-1.5, or TinyLlama) to produce a dense conditioning vector $\mathbf{c}_{\text{text}} \in \mathbb{R}^{D}$.
- **Conditioning**: The vector $\mathbf{c}_{\text{text}}$ is injected into the diffusion reverse process via cross-attention or adaptive layer norm (AdaLN), providing global atmospheric context that guides the imputation of missing values.

---

## 9. Phase 8: Directory Layout & File Catalog

```text
ctdi-model-project/
├── configs/
│   └── config.yaml                          # Global settings, window size (24), seed (42)
├── data/
│   ├── raw/                                 # 1. IMMUTABLE RAW SOURCES
│   │   ├── air_quality/
│   │   │   ├── epd_air_quality_2019_2021_hourly.csv    # 420,864 rows (16 stations x 26,304 hrs)
│   │   │   ├── air_quality_missingness_summary.csv     # Missingness breakdown per station
│   │   │   └── monthly_raw/                            # 36 original EPD monthly exports
│   │   ├── meteorology/
│   │   │   ├── hourly_meteorology_16stations_2019_2021.csv  # 420,864 rows (6 met variables)
│   │   │   ├── by_station/                             # 16 individual station series
│   │   │   └── hko_daily_reference/                    # HKO official daily validation files
│   │   ├── traffic/
│   │   │   ├── atc_2019_2021/                          # 629 extracted ATC survey files
│   │   │   ├── traffic_prop_vehicle_class_info.csv     # 76 detector points & coordinates
│   │   │   └── spatial/ATC_STATION_PT.kmz              # Road link GIS geometry
│   │   └── station_metadata/
│   │       ├── air_quality_stations.csv                # 16 target + 2 excluded stations
│   │       ├── weather_stations.csv                    # 52 HKO automatic weather stations
│   │       └── traffic_detectors.csv                   # 76 transport detector locations
│   ├── interim/                             # 2. ALIGNED INTERMEDIATE DATA
│   │   ├── aligned_hourly_features.parquet             # Merged air + met + traffic table
│   │   └── spatial_distance_matrix.npy                 # 16x16 station Euclidean distance matrix
│   └── canonical/                           # 3. CANONICAL REFERENCED TENSORS
│       ├── tensor_features.npy                         # [16, 26304, 13] float32
│       ├── tensor_mask.npy                             # [16, 26304, 13] bool/uint8
│       ├── timestamps.csv                              # 26,304 datetime index
│       └── channels.json                               # Metadata list of 13 feature names
├── Reports/
│   ├── Phase 1 - Source-Specific Cleaning Report.md # Source cleaning & traffic extraction
│   └── Data Processing - Hong Kong.md       # THIS PRACTICAL GUIDE
├── scripts/
│   ├── build_station_metadata.py            # Generates metadata catalogs
│   ├── process_air_quality.py               # Standardizes raw EPD hourly records
│   ├── download_meteorology.py              # Fetches Open-Meteo & HKO archives
│   ├── download_traffic.py                  # Downloads & extracts ATC traffic archives
│   └── verify_raw_datasets.py               # 4-stage integrity test suite
└── src/
    ├── Preprocessing/                       # Pipeline, scalers, normalizers
    ├── Dataset/                             # Windowing, missingness simulators, PyTorch Dataset
    └── context/                             # Environmental text prompt builder
```

---

## 10. Phase 9: Step-by-Step Practical Execution Plan

Once you review and approve this guide, the exact execution will proceed in 4 modular stages:

| Stage | Task | Input | Output | Verification Test |
| :---: | :--- | :--- | :--- | :--- |
| **Stage 3A** | **Traffic Interpolation & Feature Merge** | ATC census files + Station coordinates | `data/interim/aligned_hourly_features.parquet` | Check that all 13 columns are non-empty and temporally aligned for 26,304 hours. |
| **Stage 3B** | **Canonical Tensor Construction** | Merged parquet table | `data/canonical/tensor_features.npy`<br>`data/canonical/tensor_mask.npy` | Assert shape is exactly $[16, 26304, 13]$; assert `tensor_mask` matches natural missingness ($~2.5\%$). |
| **Stage 3C** | **Preprocessing & Normalization Engine** | Canonical tensors + `configs/config.yaml` | `src/preprocessing/pipeline.py`<br>`data/processed/scalers.json` | Assert scalers fit on Train split only; assert scaled outputs are zero-mean unit-variance or $[0, 1]$. |
| **Stage 3D** | **24-Hour Windowing & Missingness Simulation** | Normalized tensors | `src/dataset/windowing.py`<br>`src/dataset/missingness.py`<br>`src/dataset/torch_dataset.py` | Run unit test asserting batch shapes $[B, 16, 24, 13]$ and verify simulated missingness masks at 10%, 30%, 50%, 70%. |

This completes the entire data foundation, leaving the dataset fully processed, mathematically verified, and ready for model training.
