It takes raw data from the raw sources and do following operations on data 

```js
different timestamps
        ↓
align to same hourly timestamps

different station names
        ↓
map to common station IDs

different column names
        ↓
standardize names

different sources
        ↓
merge
```


and save it to : 
```js
data/interim/
```

RUNNING ALIGNMENT PIPELINE VALIDATION...

Beginning spatio-temporal alignment pipeline...
============================================================
1. CTDI TARGET STATIONS VALIDATION
============================================================
Number of CTDI target stations: 16
  - CAUSEWAY BAY (ID: 71, Type: Roadside)
  - CENTRAL (ID: 79, Type: Roadside)
  - CENTRAL/WESTERN (ID: 80, Type: General)
  - EASTERN (ID: 73, Type: General)
  - KWAI CHUNG (ID: 72, Type: General)
  - KWUN TONG (ID: 74, Type: General)
  - MONG KOK (ID: 81, Type: Roadside)
  - SHAM SHUI PO (ID: 66, Type: General)
  - SHATIN (ID: 75, Type: General)
  - TAI PO (ID: 69, Type: General)
  - TAP MUN (ID: 76, Type: General (Rural Background))
  - TSEUNG KWAN O (ID: 83, Type: General)
  - TSUEN WAN (ID: 77, Type: General)
  - TUEN MUN (ID: 82, Type: General)
  - TUNG CHUNG (ID: 78, Type: General)
  - YUEN LONG (ID: 70, Type: General)

Constructed expected Cartesian grid: 420,864 station-hour rows.

Computing spatial distance matrix for target stations...
Saved verified spatial distance matrix to data/interim/spatial_distance_matrix.npy (Shape: (16, 16)).

============================================================
VALIDATING SOURCE: AIR_QUALITY
============================================================
  Timestamp format: ISO datetime (Timezone-aware: False)
  Total records: 420,864
  Unique stations: 16
  Timestamp range: 2019-01-01 00:00:00 to 2021-12-31 23:00:00
  Duplicate records: 0
  Missing records relative to expected grid: 0
  Natural NaN counts per feature:
    - pm25                : 10,657 NaNs (2.53%)
    - pm10                : 11,395 NaNs (2.71%)
    - no2                 : 11,651 NaNs (2.77%)
    - o3                  : 11,117 NaNs (2.64%)
    - so2                 : 11,056 NaNs (2.63%)

============================================================
VALIDATING SOURCE: METEOROLOGY
============================================================
  Timestamp format: ISO datetime (Timezone-aware: False)
  Total records: 420,864
  Unique stations: 16
  Timestamp range: 2019-01-01 00:00:00 to 2021-12-31 23:00:00
  Duplicate records: 0
  Missing records relative to expected grid: 0
  Natural NaN counts per feature:
    - temperature         : 0 NaNs (0.00%)
    - relative_humidity   : 0 NaNs (0.00%)
    - wind_speed          : 0 NaNs (0.00%)
    - wind_direction      : 0 NaNs (0.00%)
    - pressure            : 0 NaNs (0.00%)
    - rainfall            : 0 NaNs (0.00%)

============================================================
VALIDATING SOURCE: TRAFFIC
============================================================

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ALIGNMENT CORRECTLY HALTED AS EXPECTED:
Real CTDI traffic dataset not found at 'data/raw/traffic/hourly_traffic_16stations_2019_2021.csv'.
The CTDI research paper specifies that traffic features ('traffic_speed' and 'traffic_volume') must come from real source traffic data (e.g. Hong Kong Traffic Speed Map / Transport Department detector streams).
Synthetic traffic generation has been completely removed. Please provide the real raw traffic dataset before 13-channel alignment can produce the interim dataset.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Result: No synthetic traffic was created. Alignment correctly stopped.