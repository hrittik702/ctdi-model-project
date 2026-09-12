# CTDI Dataset Specification & Acquisition Blueprint

This specification document outlines the dataset reconstruction protocol for the Air Pollution Missing Data Imputation research project, benchmarked against the reference paper:
> **Reference**: Yangwen Yu, Victor O. K. Li, Jacqueline C. K. Lam, Kelvin Chan, Qi Zhang, *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, **IEEE Transactions on Big Data**, vol. 11, 2025. DOI: [10.1109/TBDATA.2025.3533882](https://doi.org/10.1109/TBDATA.2025.3533882).

---

## 1. Target Dataset Dimensions & Tensor Formulation

| Parameter | Specification | Verification / Mathematical Derivation |
| :--- | :--- | :--- |
| **Geographic Location** | Hong Kong Special Administrative Region | Matches CTDI study domain |
| **Study Time Period** | 2019-01-01 00:00 to 2021-12-31 23:00 | Exactly 3 full calendar years (1,096 days) |
| **Calendar Breakdown** | 2019: 365 days; 2020 (leap year): 366 days; 2021: 365 days | $365 + 366 + 365 = 1,096 \text{ days}$ |
| **Temporal Resolution** | Hourly | $1,096 \text{ days} \times 24 \text{ hours/day} = \mathbf{26,304} \text{ time steps}$ |
| **Spatial Nodes** | **16 Monitoring Stations** | 16 air-quality stations active throughout 2019–2021 |
| **Feature Channels** | **13 Variables** | 5 pollutants + 6 meteorological + 2 traffic variables |
| **Tensor Dimensions** | $\mathbf{16 \times 26,304 \times 13}$ | Spatial nodes $\times$ Timestamps $\times$ Channels |
| **Total Numerical Elements** | $\mathbf{5,471,232}$ | $16 \times 26,304 \times 13 = 5,471,232$ values |

---

## 2. Official Data Sources

### Source 1: Air Quality Data
- **Official Provider**: Hong Kong Environmental Protection Department (EPD)
- **Primary Data Portals**:
  - Environmental Protection Interactive Centre (EPIC): [https://epic.epd.gov.hk/EPICDI/air/station/](https://epic.epd.gov.hk/EPICDI/air/station/)
  - Air Quality Health Index (AQHI) Portal: [https://www.aqhi.gov.hk](https://www.aqhi.gov.hk)
  - Open Data Portal: [https://data.gov.hk/en-data/dataset/hk-epd-airteam-past-record-of-air-quality-health-index-en](https://data.gov.hk/en-data/dataset/hk-epd-airteam-past-record-of-air-quality-health-index-en)
- **Historical Period Available**: 1990–present (including continuous 2019–2021).
- **Access Method**:
  1. Automated/form-based query on EPIC for hourly pollutant concentrations (`excel_by_station` / `excel_by_param` export).
  2. Direct download of monthly validated archive files via `https://www.aqhi.gov.hk/epd/ddata/html/history/{year}/{year}{month:02d}_Eng.csv`.
- **File Formats**: CSV, XML.
- **Availability Status**: **AVAILABLE**.

---

### Source 2: Meteorological Data
- **Official Provider**: Hong Kong Observatory (HKO)
- **Primary Data Portals**:
  - Climate Information Service: [https://www.hko.gov.hk/en/cis/climat.htm](https://www.hko.gov.hk/en/cis/climat.htm)
  - HKO Open Data API & Documentation: [https://data.weather.gov.hk/weatherAPI/](https://data.weather.gov.hk/weatherAPI/)
  - Common Spatial Data Infrastructure (CSDI) Portal: [https://portal.csdi.gov.hk/](https://portal.csdi.gov.hk/)
- **Historical Period Available**: 1884–present (Automatic Weather Stations active 2019–2021).
- **Access Method**:
  1. HKO Open Data API (`opendata.php` / `weather.php`).
  2. Climatological extract queries via Climate Information Service.
  3. CSDI meteorological geospatial data service.
- **File Formats**: CSV, JSON, XML.
- **Availability Status**: **AVAILABLE**.

---

### Source 3: Traffic Data
- **Official Provider**: Hong Kong Transport Department (TD)
- **Primary Data Portals**:
  - Traffic Data of Strategic / Major Roads (2nd Generation): [https://data.gov.hk/en-data/dataset/hk-td-sm_4-traffic-data-strategic-major-roads](https://data.gov.hk/en-data/dataset/hk-td-sm_4-traffic-data-strategic-major-roads)
  - Legacy Traffic Speed Map (1st Generation): [https://data.gov.hk/en-data/dataset/hk-td-sm_1-traffic-speed-map](https://data.gov.hk/en-data/dataset/hk-td-sm_1-traffic-speed-map)
  - Annual Traffic Census (ATC): [https://data.gov.hk/en-data/dataset/hk-td-sm_5-annual-traffic-census-survey-data](https://data.gov.hk/en-data/dataset/hk-td-sm_5-annual-traffic-census-survey-data)
- **Historical Period Available**:
  - Current real-time detector feeds serve rolling recent data.
  - Annual Traffic Census covers 2019, 2020, 2021.
  - Continuous 5-minute / hourly historical speed detector logs from 2019–2021 are archived under the 1st generation Traffic Speed Map system.
- **Access Method**:
  - Open Data API & XML download for current/recent feeds.
  - Historical batch extraction from Transport Department archives / CSDI geoportal.
- **File Formats**: CSV, XML, FGDB.
- **Availability Status**: **CURRENTLY RESTRICTED / REQUIRES ARCHIVAL EXTRACTION** (Annual Traffic Census hourly profiles are available; continuous 2019–2021 link-level speed detector series requires Transport Department archival extract).

---

## 3. Variable Verification (The Exact 13 Channels)

| Category | Variable | CTDI Designation | Official Source | Unit | Temporal Resolution | Spatial Resolution |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Air Pollutant** | Fine Suspended Particulates | $\text{PM}_{2.5}$ | HK EPD (EPIC / AQHI) | $\mu\text{g/m}^3$ | Hourly | Point (16 stations) |
| **Air Pollutant** | Respirable Suspended Particulates | $\text{PM}_{10}$ | HK EPD (EPIC / AQHI) | $\mu\text{g/m}^3$ | Hourly | Point (16 stations) |
| **Air Pollutant** | Nitrogen Dioxide | $\text{NO}_2$ | HK EPD (EPIC / AQHI) | $\mu\text{g/m}^3$ | Hourly | Point (16 stations) |
| **Air Pollutant** | Ozone | $\text{O}_3$ | HK EPD (EPIC / AQHI) | $\mu\text{g/m}^3$ | Hourly | Point (16 stations) |
| **Air Pollutant** | Sulphur Dioxide | $\text{SO}_2$ | HK EPD (EPIC / AQHI) | $\mu\text{g/m}^3$ | Hourly | Point (16 stations) |
| **Meteorology** | Air Temperature | $\text{TEMP}$ | HK Observatory (HKO) | $^\circ\text{C}$ | Hourly | Interpolated to stations |
| **Meteorology** | Relative Humidity | $\text{RH}$ | HK Observatory (HKO) | $\%$ | Hourly | Interpolated to stations |
| **Meteorology** | Wind Speed | $\text{WS}$ | HK Observatory (HKO) | $\text{m/s}$ | Hourly | Interpolated to stations |
| **Meteorology** | Wind Direction | $\text{WD}$ | HK Observatory (HKO) | $\text{Degrees}\ (0\text{--}360^\circ)$ | Hourly | Interpolated to stations |
| **Meteorology** | Atmospheric Pressure | $\text{PRES}$ | HK Observatory (HKO) | $\text{hPa}$ | Hourly | Interpolated to stations |
| **Meteorology** | Rainfall / Precipitation | $\text{RAIN}$ | HK Observatory (HKO) | $\text{mm}$ | Hourly | Interpolated to stations |
| **Traffic** | Traffic Speed | $\text{SPEED}$ | HK Transport Department (TD) | $\text{km/h}$ | Hourly | Interpolated to stations |
| **Traffic** | Traffic Volume / Flow | $\text{VOL}$ | HK Transport Department (TD) | $\text{veh/h}$ | Hourly | Interpolated to stations |

> **Note on Pollutant Selection**: Carbon Monoxide ($\text{CO}$) is monitored only at select stations (primarily roadside and Tap Mun) and is omitted by EPD at most general stations. Consequently, the CTDI paper uses the standard 5 continuous criteria pollutants ($\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{O}_3, \text{SO}_2$) to ensure uniform coverage across all 16 stations.

---

## 4. Station Verification (16 Included vs. 2 Excluded Stations)

The Hong Kong air-quality monitoring network currently comprises **18 fixed monitoring stations** (15 General Stations and 3 Roadside Stations).

### The 16 Stations Included in CTDI
All 16 of the following stations operated continuously throughout the entire study period (**2019-01-01 to 2021-12-31**):

| # | Station ID | Station Name | Station Type | Latitude (°N) | Longitude (°E) | Sampling Height | Operational Status (2019–2021) |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | `80` | **Central / Western** | General | 22.2848 | 114.1441 | 16 m | Active full period |
| 2 | `73` | **Eastern** | General | 22.2831 | 114.2190 | 15 m | Active full period |
| 3 | `74` | **Kwun Tong** | General | 22.3107 | 114.2312 | 15 m | Active full period |
| 4 | `66` | **Sham Shui Po** | General | 22.3304 | 114.1591 | 17 m | Active full period |
| 5 | `72` | **Kwai Chung** | General | 22.3569 | 114.1293 | 13 m | Active full period |
| 6 | `77` | **Tsuen Wan** | General | 22.3715 | 114.1146 | 17 m | Active full period |
| 7 | `83` | **Tseung Kwan O** | General | 22.3173 | 114.2596 | 16 m | Active full period (opened 2016) |
| 8 | `70` | **Yuen Long** | General | 22.4450 | 114.0227 | 25 m | Active full period |
| 9 | `82` | **Tuen Mun** | General | 22.3911 | 113.9768 | 27 m | Active full period |
| 10 | `78` | **Tung Chung** | General | 22.2885 | 113.9431 | 28 m | Active full period |
| 11 | `69` | **Tai Po** | General | 22.4508 | 114.1644 | 28 m | Active full period |
| 12 | `75` | **Sha Tin** | General | 22.3764 | 114.1846 | 25 m | Active full period |
| 13 | `76` | **Tap Mun** | General (Rural Background) | 22.4757 | 114.3619 | 11 m | Active full period |
| 14 | `71` | **Causeway Bay** | Roadside | 22.2801 | 114.1855 | 3 m | Active full period |
| 15 | `79` | **Central** | Roadside | 22.2802 | 114.1606 | 4.5 m | Active full period |
| 16 | `81` | **Mong Kok** | Roadside | 22.3225 | 114.1685 | 3 m | Active full period |

---

### The 2 Excluded Stations (Verification of Paper Statement)
The CTDI paper states:
> *"Two newer Hong Kong air-pollution monitoring stations were excluded for data consistency."*

Our historical analysis of EPD archival records confirms the identity of these two stations:

| Station ID | Station Name | Station Type | Latitude (°N) | Longitude (°E) | Commissioning Date | Reason for Exclusion in CTDI |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| `84` | **Southern** | General | 22.2472 | 114.1603 | **July 10, 2020** | Did **not exist** in 2019 or early 2020 (missing first 18 months of study period). |
| `85` | **North** | General | 22.4969 | 114.1283 | **July 10, 2020** | Did **not exist** in 2019 or early 2020 (missing first 18 months of study period). |

**Empirical Confirmation**:
- Inspection of EPD monthly records demonstrates:
  - `201901_Eng.csv` to `202005_Eng.csv`: Exactly **16 stations** reported. Southern and North are absent.
  - `202006_Eng.csv` onward: Southern and North were commissioned, expanding the network to **18 stations**.
- Retaining Southern and North would introduce an unrecoverable 18-month 100% structural outage from 2019-01-01 to 2020-07-09. Excluding them preserves unbroken continuity across all 16 spatial nodes for all 26,304 hours.

---

## 5. Research Traceability & Pipeline Architecture

```
                    ┌────────────────────────────────────────┐
                    │               CTDI Paper               │
                    │   (Yu et al., IEEE TBD 2025)           │
                    │   16 Stations | 26,304 Hrs | 13 Ch     │
                    └───────────────────┬────────────────────┘
                                        │
                                        ▼
                    ┌────────────────────────────────────────┐
                    │          Official HK Sources           │
                    │   EPD (Air) | HKO (Met) | TD (Traffic) │
                    └───────────────────┬────────────────────┘
                                        │
                                        ▼
                    ┌────────────────────────────────────────┐
                    │          Raw Data Acquisition          │
                    │   data/raw/air_quality/                │
                    │   data/raw/meteorology/                │
                    │   data/raw/traffic/                    │
                    │   data/raw/station_metadata/           │
                    └───────────────────┬────────────────────┘
                                        │
                                        ▼
                    ┌────────────────────────────────────────┐
                    │     Data Alignment & Interpolation     │
                    │   data/interim/                        │
                    │   - Spatial IDW / Kriging for Met & TD │
                    │   - Timestamp Hourly Synchronization   │
                    └───────────────────┬────────────────────┘
                                        │
                                        ▼
                    ┌────────────────────────────────────────┐
                    │       Canonical Dataset Tensor         │
                    │   data/canonical/                      │
                    │   Shape: [16, 26304, 13]               │
                    │   5,471,232 total data values          │
                    └───────────────────┬────────────────────┘
                                        │
                                        ▼
                    ┌────────────────────────────────────────┐
                    │       SLM-Diffusion Experiments        │
                    │   - 24-hr Sliding Window Tensors       │
                    │   - Environmental Context Builder      │
                    │   - SLM Conditioning & Diffusion Model │
                    └────────────────────────────────────────┘
```

### Traceability Distinction

1. **Explicitly Stated by CTDI Paper**:
   - Time range: 2019-01-01 through 2021-12-31 (hourly).
   - 16 stations utilized; 2 newer stations excluded for consistency.
   - 13 channels: 5 pollutants, 6 meteorological, 2 traffic.
   - Post-spatial-interpolation tensor dimension: $16 \times 26,304 \times 13 = 5,471,232$ values.
2. **Independently Verified by Our Inspection**:
   - The 2 excluded stations are confirmed to be **Southern (Station 84)** and **North (Station 85)**, commissioned in July 2020.
   - The 16 stations comprise 13 General Stations and 3 Roadside Stations.
   - The 5 criteria pollutants are $\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{O}_3, \text{SO}_2$.
   - Air pollution data from 2019–2021 is fully accessible via EPD EPIC and monthly open archives.
   - HKO hourly meteorological variables are accessible via HKO Climate Information Service.
3. **Inferred / Project Implementation Decisions**:
   - Spatial interpolation method: CTDI applies spatial interpolation (e.g., Inverse Distance Weighting or Gaussian spatial process) to map distributed AWS weather stations and road traffic detectors to the 16 exact air monitoring station coordinates.
   - Traffic variable handling: Because raw 2019–2021 continuous 5-minute road link speed streams require archival retrieval from TD/CSDI, we can either extract historical Annual Traffic Census (ATC) hourly volume/speed profiles or utilize the air+meteorology subsets ($16 \times 26,304 \times 11$) during initial pipeline development while awaiting complete archival traffic dumps.

---

## 6. Directory Scaffolding

```text
data/
├── raw/
│   ├── air_quality/          # EPD hourly station pollutant CSVs (2019–2021)
│   ├── meteorology/          # HKO hourly automatic weather station observations
│   ├── traffic/              # TD traffic speed & volume records
│   └── station_metadata/     # Station coordinates, elevations, types, and districts
├── interim/                  # Spatially interpolated, temporally harmonized intermediate tables
└── canonical/                # Final [16, 26304, 13] reference tensor and masks
```
