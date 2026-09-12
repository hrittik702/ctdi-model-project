# 01 - Raw Data Sources & Ingestion

> **Next**: [[02 - Cleaning, Translation & Formatting]] | **Index**: [[00 - Overview & Pipeline Architecture]]

---

## 1. Overview of Multi-Modal Data Sources

To reconstruct the CTDI paper benchmark, our pipeline acquires four distinct raw data assets:

1. **Air Quality Criteria Pollutants**: Hong Kong Environmental Protection Department (EPD).
2. **Hourly Gridded Meteorology**: Open-Meteo Historical Archive (assimilated ERA5-Land reanalysis).
3. **Daily Ground-Truth Climatology**: Hong Kong Observatory (HKO) Climate Information Service.
4. **Traffic Census & Flow**: Hong Kong Transport Department (TD) Annual Traffic Census (ATC).
5. **Spatial Metadata & Network Coordinates**: Government Open Data & Geoportals.

---

## 2. Air Quality Data (Hong Kong EPD)

### 2.1 The Provider & Portal
- **Authority**: Environmental Protection Department, The Government of the Hong Kong SAR.
- **Primary Portal**: Environmental Protection Interactive Centre (EPIC)  
  URL: `https://cd.epic.epd.gov.hk/EPICDI/air/station/`
- **Acquisition Protocol**: HTTP POST queries against Apache MyFaces JSF form using session cookies and `ViewState`.

### 2.2 Raw Characteristics
- **Date Range**: 2019-01-01 01:00 to 2021-12-31 24:00 (3 full calendar years = 36 monthly files).
- **Network Extent**: 18 active stations reported.
- **Temporal Resolution**: Hourly.
- **Reported Pollutants**: `SO2`, `NOX`, `NO2`, `CO`, `PM10`, `O3`, `PM2.5`.
- **Missing Value Representation**: The string `"N.A."`.

### 2.3 Station Selection (16 Included vs 2 Excluded)
Hong Kong operates 18 monitoring stations. The CTDI benchmark uses **exactly 16 stations**:

```text
16 Included Stations (Continuous across 2019-01-01 to 2021-12-31):
- General (13): Central/Western, Eastern, Kwun Tong, Sham Shui Po, Kwai Chung, 
                Tsuen Wan, Tseung Kwan O, Yuen Long, Tuen Mun, Tung Chung, 
                Tai Po, Sha Tin, Tap Mun.
- Roadside (3): Causeway Bay, Central, Mong Kok.

2 Excluded Stations:
- Southern (Station ID 84): Commissioned July 10, 2020.
- North (Station ID 85): Commissioned July 10, 2020.
* Reason: Both stations were non-existent for the entire year of 2019 and early 2020. 
  Retaining them would introduce an 18-month structural outage (50% missingness).
```

- **Output File**: `data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv` (420,864 rows).
- **Automation Script**: `scripts/process_air_quality.py` / `scripts/download_epd_air_quality.py`.

---

## 3. Meteorological Data (Open-Meteo & HKO)

### 3.1 The 6 Required Meteorological Variables
In accordance with atmospheric physics and the CTDI paper:
1. **Air Temperature ($\text{TEMP}$)**: Units: $^\circ\text{C}$.
2. **Relative Humidity ($\text{RH}$)**: Units: $\%$.
3. **Wind Speed ($\text{WS}$)**: Units: $\text{m/s}$.
4. **Wind Direction ($\text{WD}$)**: Units: Degrees ($0^\circ\text{--}360^\circ$).
5. **Surface Pressure ($\text{PRES}$)**: Units: $\text{hPa}$.
6. **Rainfall ($\text{RAIN}$)**: Units: $\text{mm}$.

### 3.2 Primary Hourly Series (Open-Meteo)
- **Source**: Open-Meteo Historical Weather Archive API.
- **Model Backbone**: ECMWF ERA5-Land reanalysis combined with surface station observation assimilation.
- **Spatial Method**: Queried directly at the exact latitude/longitude coordinates of each of the 16 air stations.
- **Volume**: 26,304 continuous hourly timestamps per station $\times 16 = \mathbf{420,864}$ rows.
- **Completeness**: **100.00%** (zero missing values).
- **Master File**: `data/raw/meteorology/hourly_meteorology_16stations_2019_2021.csv`.
- **Automation Script**: `scripts/download_meteorology.py`.

### 3.3 HKO Official Daily Reference Series (Validation Benchmark)
- **Source**: Hong Kong Observatory (HKO) Climate Information Service (`data.weather.gov.hk`).
- **Stations**: HKO Headquarters (temperature, humidity, pressure, rain) and Waglan Island (`WGL`, standard official marine anemometer since 1989 for wind speed and prevailing wind direction).
- **Period**: 2019-01-01 to 2021-12-31 ($1,096$ continuous days per file).
- **Role**: Never fed into the model; used strictly to verify that the hourly meteorological data is physically calibrated to official government records.
- **Directory**: `data/raw/meteorology/hko_daily_reference/` (6 CSV files).

---

## 4. Traffic Data (Hong Kong Transport Department)

### 4.1 Annual Traffic Census (ATC) Archives
- **Source**: Hong Kong Transport Department Open Data Portal (`data.gov.hk`).
- **Archive File**: `ATC_TRAFFIC_DATA.zip` ($33.7\text{ MB}$).
- **Years Acquired**: 2019 ($226$ survey files), 2020 ($200$ survey files), 2021 ($203$ survey files).
- **Extracted Location**: `data/raw/traffic/atc_2019_2021/`.

### 4.2 Spatial Geometry & Vehicle Classification
- **Station Line/Point KMZ**: `data/raw/traffic/spatial/ATC_STATION_PT.kmz` (GIS coordinates of core and coverage census stations).
- **Detector Information**: `data/raw/traffic/traffic_prop_vehicle_class_info.csv` ($76$ continuous detector points across arterial road corridors).
- **Automation Script**: `scripts/download_traffic.py`.

---

## 5. Summary of Raw Acquisition Commands

All data acquisition scripts are fully automated and stored in `scripts/`:

```bash
# 1. Generate station metadata catalogs
.venv/bin/python scripts/build_station_metadata.py

# 2. Standardize raw EPD air quality records
.venv/bin/python scripts/process_air_quality.py

# 3. Fetch hourly meteorology and daily HKO reference series
.venv/bin/python scripts/download_meteorology.py

# 4. Download and extract Transport Department traffic archives
.venv/bin/python scripts/download_traffic.py

# 5. Run full 4-stage integrity verification test
.venv/bin/python scripts/verify_raw_datasets.py
```
