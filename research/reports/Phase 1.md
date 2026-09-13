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