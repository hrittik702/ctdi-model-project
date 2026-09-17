# Data Source Inventory & Fidelity Audit

To maintain research-grade documentation, data sources are categorized into four distinct epistemic categories:
1. `ACTUAL SOURCE`: Official physical provider and validated system endpoints.
2. `REFERENCE SOURCE`: Benchmark data used for cross-checking or calibration.
3. `INFERRED SOURCE`: Deduced from published citations or portal documentation.
4. `IMPLEMENTATION ASSUMPTION`: Interim choices made in code before source verification.

---

## 1. Air Quality Domain

- **Classification**: **`ACTUAL SOURCE`**
- **Publishing Authority**: Environmental Protection Department, The Government of the Hong Kong SAR (HKEPD)
- **Official Portals**:
  - Environmental Protection Interactive Centre (EPIC): `https://epic.epd.gov.hk/EPICDI/air/station/`
  - AQHI Open Monthly Archive: `https://www.aqhi.gov.hk/epd/ddata/html/history/{year}/{year}{month:02d}_Eng.csv`
- **Variables Acquired**: $\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{SO}_2, \text{O}_3, \text{NO}_x, \text{CO}$
- **Temporal Resolution**: Hourly native records
- **Spatial Coverage**: 16 continuous stations (13 General, 3 Roadside)
- **Local Archive**: `data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv`
- **Verification Status**: **`VERIFIED_VALID`** (420,864 rows, exact 1:1 match with CTDI Table I criteria pollutants).

---

## 2. Meteorology Domain

- **Classification**: **`IMPLEMENTATION ASSUMPTION`** (Interim dataset) vs **`ACTUAL SOURCE`** (CTDI Benchmark)
- **CTDI Benchmark Actual Source**:
  - Provider: Hong Kong Observatory (HKO) Open Database [81]
  - Network: 47 Automatic Weather Stations (AWS)
  - Cadence: 10 minutes
  - Variables: Pressure ($\text{hPa}$), Relative humidity ($\%$), Temperature ($^\circ\text{C}$), Visibility ($\text{km}$), Wind direction ($\text{N/A}$), Wind speed ($\text{km/h}$).
- **Interim Dataset in Codebase**:
  - Provider: ECMWF ERA5 Reanalysis via Open-Meteo Historical Archive API
  - Coordinates: Interpolated to the 16 exact station coordinates
  - Variables: Temperature ($^\circ\text{C}$), Relative humidity ($\%$), Wind speed ($\text{m/s}$), Wind direction (degrees), Surface pressure ($\text{hPa}$), Rainfall ($\text{mm}$).
  - Local Archive: `data/raw/meteorology/hourly_meteorology_16stations_2019_2021.csv`
- **Reference Benchmark Source**:
  - HKO Daily Benchmark Observations (`data/raw/meteorology/hko_daily_reference/`).
- **Fidelity Divergence**:
  1. CTDI Table I explicitly uses **Visibility ($\text{km}$)**; the interim file contains **Rainfall ($\text{mm}$)**.
  2. CTDI Table I performs IDW from 47 surface weather stations; the interim file uses grid-reanalysis.
- **Verification Status**: **`PARTIALLY_VERIFIED (SOURCE FIDELITY DIVERGENCE)`**.

---

## 3. Traffic Domain

- **Classification**: **`INFERRED SOURCE`** (Parent Speedmap System) vs **`REJECTED SOURCE`** (Annual Traffic Census)
- **Rejected Source**:
  - Source: Annual Traffic Census (ATC) from Transport Department (`ATC_TRAFFIC_DATA.zip`).
  - Reason for Rejection: Contains only annual aggregates (AADT) and 24-hour diurnal percentages; lacks continuous 26,304-hour empirical time-series and vehicular speeds.
- **Cited Reference [82]**:
  - Title: Hong Kong Traffic Speed Map (City Dashboard Version) Database [82]
  - Portal URL: `https://data.gov.hk/en-data/dataset/hk-ogcio-da_div_02-citydashboard-traffic-speed`
  - Limitation: Exposes only 6 road links and historical archives only begin on 2019-12-24 (missing 97.9% of 2019).
- **Target Parent System**:
  - Provider: Transport Department, The Government of the Hong Kong SAR
  - System: 1st Generation Traffic Speed Map (`hk-td-sm_1-traffic-speed-map`)
  - Endpoint: `http://resource.data.one.gov.hk/td/speedmap.xml`
  - Spatial Coverage: **Exactly 607 road links**, matching CTDI Table I ($607$ roads, 5-minute update cadence).
  - Temporal Coverage: $774,686$ archived snapshots covering 100% of 2019, 2020, and 2021.
  - Variables: `TRAFFIC_SPEED` ($\text{km/h}$) and `ROAD_SATURATION_LEVEL` (`TRAFFIC GOOD`, `TRAFFIC AVERAGE`, `TRAFFIC BAD`).
- **Verification Status**: **`PARTIALLY_VERIFIED (BATCH INGESTION REQUIRED)`**. Schema, variables, and network are verified; batch ingestion of the 2019–2021 snapshots remains to be run.
