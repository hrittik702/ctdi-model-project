# 08 - Canonical Data Storage & File Layout

> **Previous**: [[07 - Environmental Context Builder for SLM]] | **Next**: [[09 - Quality Assurance & Verification Playbook]] | **Index**: [[00 - Overview & Pipeline Architecture]]

---

## 1. Directory Tree Overview

The data storage hierarchy cleanly separates immutable raw downloads, intermediate aligned tables, canonical master tensors, and model-ready windowed caches:

```text
ctdi-model-project/
├── configs/
│   └── config.yaml                          # Configuration parameters
├── data/
│   ├── raw/                                 # 1. IMMUTABLE ORIGINAL SOURCES
│   │   ├── air_quality/
│   │   │   ├── epd_air_quality_2019_2021_hourly.csv    # 420,864 rows (16 stations x 26,304 hrs)
│   │   │   ├── air_quality_missingness_summary.csv     # Missingness breakdown per station
│   │   │   └── monthly_raw/                            # 36 original EPD monthly archives
│   │   ├── meteorology/
│   │   │   ├── hourly_meteorology_16stations_2019_2021.csv  # 420,864 rows (6 met variables)
│   │   │   ├── by_station/                             # 16 individual station series
│   │   │   └── hko_daily_reference/                    # 6 official HKO daily reference files
│   │   ├── traffic/
│   │   │   ├── atc_2019_2021/                          # 629 extracted ATC census files
│   │   │   ├── traffic_prop_vehicle_class_info.csv     # 76 detector points & coordinates
│   │   │   └── spatial/ATC_STATION_PT.kmz              # Road link GIS geometry
│   │   └── station_metadata/
│   │       ├── air_quality_stations.csv                # 16 target + 2 excluded stations
│   │       ├── weather_stations.csv                    # 52 HKO automatic weather stations
│   │       └── traffic_detectors.csv                   # 76 transport detector locations
│   ├── interim/                             # 2. ALIGNED INTERMEDIATE DATA
│   │   ├── aligned_hourly_features.parquet             # Merged air + met + traffic table
│   │   └── spatial_distance_matrix.npy                 # 16x16 station Euclidean distance matrix
│   ├── canonical/                           # 3. CANONICAL REFERENCED TENSORS
│   │   ├── tensor_features.npy                         # [16, 26304, 13] float32
│   │   ├── tensor_mask.npy                             # [16, 26304, 13] uint8
│   │   ├── timestamps.csv                              # 26,304 datetime index
│   │   └── channels.json                               # List of 13 channel identifiers
│   └── processed/                           # 4. PREPROCESSED & SCALED OUTPUTS
│       ├── scalers.json                                # Channel-wise mean, std, min, max
│       ├── train_windows.pt                            # [N_train, 16, 24, 13] PyTorch tensor
│       ├── val_windows.pt                              # [N_val, 16, 24, 13] PyTorch tensor
│       └── test_windows.pt                             # [N_test, 16, 24, 13] PyTorch tensor
```

---

## 2. File Specifications & Binary Formats

### 2.1 Canonical Tensors (`data/canonical/`)

| File Name | Data Type | Dimensions | Disk Size | Description |
| :--- | :---: | :---: | :---: | :--- |
| `tensor_features.npy` | `float32` | $[16, 26304, 13]$ | $\approx 21.9\text{ MB}$ | Continuous physical readings in original units. Missing entries stored as `np.nan`. |
| `tensor_mask.npy` | `uint8` | $[16, 26304, 13]$ | $\approx 5.5\text{ MB}$ | Binary observation mask ($1 = \text{observed}, 0 = \text{missing}$). |
| `timestamps.csv` | String | $26,304\text{ rows}$ | $\approx 514\text{ KB}$ | Full hourly ISO timestamps from `2019-01-01 00:00:00` to `2021-12-31 23:00:00`. |
| `channels.json` | JSON | $13\text{ keys}$ | $\approx 1\text{ KB}$ | Channel ordering list: `['pm25', 'pm10', 'no2', 'o3', 'so2', 'temperature', 'relative_humidity', 'wind_speed', 'wind_direction', 'pressure', 'rainfall', 'traffic_speed', 'traffic_volume']`. |

### 2.2 Why NumPy (`.npy`) and Parquet (`.parquet`)?
- **Fast I/O Memory Mapping**: `np.load('tensor_features.npy', mmap_mode='r')` allows instant random access to arbitrary 24-hour time slices without loading the entire 22 MB into RAM.
- **Columnar Efficiency**: `.parquet` stores intermediate multi-modal tables with Snappy compression and strict type enforcement, saving 70% disk space compared to raw CSV.

---

## 3. Metadata Files (`data/raw/station_metadata/`)

### 3.1 `air_quality_stations.csv`
Contains the complete spatial and operational schema for all 18 Hong Kong monitoring stations:
```text
station_id,station_code,station_name,display_name,station_type,latitude,longitude,sampling_height_m,district,in_ctdi_study,reason_if_excluded
80,CW,CENTRAL/WESTERN,Central / Western,General,22.2848,114.1441,16.0,Central and Western,True,
73,E,EASTERN,Eastern,General,22.2831,114.2190,15.0,Eastern,True,
...
84,S,SOUTHERN,Southern,General,22.2472,114.1603,16.0,Southern,False,Commissioned 2020-07-10; missing 2019 to mid-2020
85,N,NORTH,North,General,22.4969,114.1283,16.0,North,False,Commissioned 2020-07-10; missing 2019 to mid-2020
```

### 3.2 `weather_stations.csv`
Contains the coordinates, elevations, and sensor capabilities of all 52 Automatic Weather Stations operated by the Hong Kong Observatory.

### 3.3 `traffic_detectors.csv`
Contains geographic locations (Easting, Northing, Latitude, Longitude) for 76 continuous traffic monitoring detectors installed across major road links.
