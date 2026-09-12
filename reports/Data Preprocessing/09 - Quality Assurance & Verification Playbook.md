# 09 - Quality Assurance & Verification Playbook

> **Previous**: [[08 - Canonical Data Storage & File Layout]] | **Index**: [[00 - Overview & Pipeline Architecture]]

---

## 1. Overview

To ensure complete mathematical correctness and data integrity before initiating any model training, our pipeline enforces an automated 4-stage verification suite.

Every transformation must satisfy strict assertions regarding row counts, spatial coordinate validity, timestamp monotonicity, and physical numerical boundaries.

---

## 2. Automated Verification Suite (`scripts/verify_raw_datasets.py`)

Run the full verification suite using the active environment:

```bash
.venv/bin/python scripts/verify_raw_datasets.py
```

### 2.1 Test Stage 1: Station Metadata Verification
- **Target File**: `data/raw/station_metadata/air_quality_stations.csv`
- **Assertions**:
  - Exactly 18 total stations cataloged.
  - Exactly 16 stations marked `in_ctdi_study = True`.
  - Exactly 2 stations marked `in_ctdi_study = False` with verified exclusion rationale (`Southern` and `North`).
  - Spatial coordinates must fall strictly within Hong Kong territorial bounds:
    $$22.0^\circ\text{N} \le \text{Latitude} \le 23.0^\circ\text{N}, \quad 113.8^\circ\text{E} \le \text{Longitude} \le 114.5^\circ\text{E}$$

### 2.2 Test Stage 2: Air Quality Dataset Verification
- **Target File**: `data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv`
- **Assertions**:
  - Total rows must equal exactly $16 \times 26,304 = \mathbf{420,864}$.
  - Exactly 16 unique station names present.
  - Timestamps must form an unbroken hourly sequence from `2019-01-01 00:00:00` to `2021-12-31 23:00:00`.
  - Natural missingness rates for the 5 criteria pollutants ($\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{O}_3, \text{SO}_2$) must be below $5.0\%$ across the entire network.
  - Non-negative pollutant concentrations ($x \ge 0.0\ \mu\text{g/m}^3$).

### 2.3 Test Stage 3: Meteorological Dataset Verification
- **Target File**: `data/raw/meteorology/hourly_meteorology_16stations_2019_2021.csv`
- **Assertions**:
  - Total rows must equal exactly $16 \times 26,304 = \mathbf{420,864}$.
  - Zero missing values across all 6 meteorological variables (100% complete).
  - Physical boundary checks:
    - Temperature: $-5.0^\circ\text{C} \le T \le 45.0^\circ\text{C}$
    - Relative Humidity: $0.0\% \le \text{RH} \le 100.0\%$
    - Atmospheric Pressure: $900.0\text{ hPa} \le P \le 1050.0\text{ hPa}$
    - Wind Speed: $\text{WS} \ge 0.0\text{ m/s}$
    - Rainfall: $\text{RAIN} \ge 0.0\text{ mm}$

### 2.4 Test Stage 4: Traffic Census Archives Verification
- **Target Directory**: `data/raw/traffic/atc_2019_2021/`
- **Assertions**:
  - Annual archives for 2019, 2020, and 2021 extracted and verified.
  - More than 200 station survey files present per year.
  - Detector coordinates file `traffic_prop_vehicle_class_info.csv` populated with 76 detectors.
  - Spatial KMZ `ATC_STATION_PT.kmz` present.

---

## 3. Expected Verification Output

A successful run of `verify_raw_datasets.py` terminates with exit code 0 and logs:

```text
============================================================
1. VERIFYING STATION METADATA
============================================================
Total stations in metadata catalog: 18
  Stations included in CTDI: 16
  Stations excluded (historical consistency): 2
    - SOUTHERN (ID 84): Commissioned 2020-07-10; missing 2019 to mid-2020
    - NORTH (ID 85): Commissioned 2020-07-10; missing 2019 to mid-2020
  [PASS] Station metadata is complete, accurate, and spatially valid.

============================================================
2. VERIFYING AIR QUALITY DATASET (EPD 2019-2021)
============================================================
Rows loaded: 420,864
Columns: ['station_id', 'station_name', 'timestamp', 'pm25', 'pm10', 'no2', 'o3', 'so2', 'nox', 'co']
Missingness Rates Across 3 Full Years (1,096 days = 26,304 hours per station):
  PM25 : 410,207 valid, 10,657 missing ( 2.53%) | range: [0.0, 167.0] μg/m³, mean: 17.5
  PM10 : 409,469 valid, 11,395 missing ( 2.71%) | range: [0.0, 241.0] μg/m³, mean: 29.7
  NO2  : 409,213 valid, 11,651 missing ( 2.77%) | range: [0.0, 366.0] μg/m³, mean: 42.8
  O3   : 409,747 valid, 11,117 missing ( 2.64%) | range: [0.0, 422.0] μg/m³, mean: 50.8
  SO2  : 409,808 valid, 11,056 missing ( 2.63%) | range: [0.0, 81.0] μg/m³, mean: 4.9
  [PASS] Air quality dataset is continuous, monotonic, and fully validated.

============================================================
3. VERIFYING METEOROLOGICAL DATASET (16 STATIONS 2019-2021)
============================================================
Rows loaded: 420,864
Columns: ['station_id', 'station_name', 'timestamp', 'temperature', 'relative_humidity', 'wind_speed', 'wind_direction', 'pressure', 'rainfall']
  temperature       : 100% complete | range: [2.9, 35.6], mean: 23.1
  relative_humidity : 100% complete | range: [13.0, 100.0], mean: 81.5
  wind_speed        : 100% complete | range: [0.0, 17.4], mean: 3.5
  wind_direction    : 100% complete | range: [0.0, 360.0], mean: 120.3
  pressure          : 100% complete | range: [986.5, 1029.9], mean: 1010.5
  rainfall          : 100% complete | range: [0.0, 61.8], mean: 0.2
  [PASS] Meteorology dataset is complete, physically consistent, and fully aligned.

============================================================
4. VERIFYING TRAFFIC CENSUS ARCHIVES (TD 2019-2021)
============================================================
  Year 2019: 226 census survey / station files extracted.
  Year 2020: 200 census survey / station files extracted.
  Year 2021: 203 census survey / station files extracted.
  [PASS] Traffic census archives are verified and accessible.

============================================================
SUMMARY OF VERIFICATION
============================================================
  1. Station Metadata:    PASS
  2. Air Quality Dataset:  PASS
  3. Meteorology Dataset:  PASS
  4. Traffic Archives:     PASS

ALL VERIFICATION CHECKS PASSED SUCCESSFULLY.
Post-spatial tensor alignment: 16 stations × 26,304 hours = 420,864 aligned steps.
```

---

## 4. Failure Modes & Recovery Procedures

| Failure Scenario | Root Cause | Automated Resolution |
| :--- | :--- | :--- |
| `Row count mismatch in air quality` | Duplicate timestamps or omitted leap day (2020-02-29). | Rerun `process_air_quality.py`; verify calendar range generates exactly 1,096 days. |
| `Missing variable in meteorology` | Incomplete download stream or timeout from Open-Meteo. | Check `data/raw/meteorology/by_station/`; rerun `download_meteorology.py` (has automatic caching of completed stations). |
| `Name resolution error on HKO portal` | Intermittent DNS network jitter when querying `data.weather.gov.hk`. | The scripts include a 3-attempt exponential backoff retry loop (`fetch_with_retries`). |
| `Negative pollutant values` | Raw telemetry baseline drift before EPD QA zero-correction. | Coerced to `0.0` or clipped at physical minimum. |
