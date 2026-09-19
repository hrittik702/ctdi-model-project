with open("research/Reports/Data Processing - Hong Kong.md") as f:
    text = f.read()

# 1. Pipeline diagram
old_box = """│  - HKO & Open-Meteo: Hourly meteorology (TEMP, RH, WS, WD, PRES, RAIN) at 16 coordinates       │
│  - Transport Dept: Annual Traffic Census (ATC) survey files (2019-2021), detectors, KMZ        │
│  - Spatial Metadata: 18 Air Stations (16 included + 2 excluded), 52 Weather, 76 Detectors      │"""

new_box = """│  - ECMWF ERA5: Hourly surface reanalysis (TEMP, RH, WS, WD, PRES, RAIN) at 16 coordinates     │
│  - Transport Dept: 1st Gen SpeedMap XML archives (2019–2021), 607/632 road links, 5-min cadence │
│  - Spatial Metadata: 18 Air Stations (16 included + 2 excluded), 16 ERA5 Coords, 632 Road Links│"""

text = text.replace(old_box, new_box)

# 2. Table I channels
old_channels = """|  **10**   | Rainfall                    |   $\text{RAIN}$   | Open-Meteo / HKO |    $\text{mm}$    |   $0.0 - 61.8$    | Hourly total precipitation           |
|  **11**   | Traffic Speed               |  $\text{SPEED}$   |   HK TD (ATC)    |   $\text{km/h}$   |  $10.0 - 100.0$   | Spatially interpolated traffic speed |
|  **12**   | Traffic Volume              |   $\text{VOL}$    |   HK TD (ATC)    |  $\text{veh/h}$   |  $50.0 - 6500.0$  | Spatially interpolated hourly flow   |"""

new_channels = """|  **10**   | Rainfall                    |   $\text{RAIN}$   |    ECMWF ERA5    |    $\text{mm}$    |   $0.0 - 61.8$    | Total hourly precipitation (Channel 9 substitution) |
|  **11**   | Traffic Speed               |  $\text{SPEED}$   | HK TD (SpeedMap) |   $\text{km/h}$   |   $0.0 - 111.0$   | Spatially interpolated vehicular speed (IDW $p=2$)  |
|  **12**   | Traffic Congestion          | $\text{CONGEST}$  | HK TD (SpeedMap) |   $\text{N/A}$    |    $0.0 - 1.0$    | Road saturation level (Good=0.0, Average=0.5, Bad=1.0) |"""

text = text.replace(old_channels, new_channels)

# 3. Spatial alignment text
old_spatial = """```
[HKO Weather Stations] ──(Spatial IDW / Co-located Coordinates)──┐
                                                                 ├──> [16 Air Stations Grid]
[Traffic Detectors / ATC] ──(Nearest Arterial Link / IDW)────────┘
```

1. **Meteorology Mapping**:
   - We query the high-resolution grid at the exact coordinates $(\text{Lat}_i, \text{Lon}_i)$ of each of the 16 air stations. This eliminates spatial discrepancy between meteorological inputs and air quality stations.
2. **Traffic Mapping**:
   - For Roadside Stations (Causeway Bay, Central, Mong Kok), traffic detectors are matched to the immediate road links (Hennessy Road, Des Voeux Road, Nathan Road).
   - For General Stations, Inverse Distance Weighting (IDW) or district-level Annual Traffic Census (ATC) flow profiles are mapped to each station radius."""

new_spatial = """```
[ECMWF ERA5 Surface Grid] ──(Co-located Station Coordinates)──────┐
                                                                 ├──> [16 Air Stations Grid]
[TD SpeedMap (632 Links)] ──(Spatial IDW p=2 Link Centroids)────┘
```

1. **Meteorology Mapping**:
   - Continuous surface reanalysis is sampled at the exact latitude/longitude coordinates of each of the 16 air quality monitoring stations, ensuring 100% temporal completeness and zero spatial displacement.
2. **Traffic Mapping**:
   - Road link centroids from 632 georeferenced Transport Department SpeedMap segments are spatially projected to each of the 16 station coordinates via Inverse Distance Weighting ($w_{ij} = 1/d_{ij}^2$). Natural archive missing hours (2,416 hours across the 3-year period) are strictly preserved as NaN floats with zero synthetic 0 km/h filling."""

text = text.replace(old_spatial, new_spatial)

# 4. Directory tree
old_tree = """│   ├── raw/                                 # 1. IMMUTABLE RAW SOURCES
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
│   │   └── spatial_distance_matrix.npy                 # 16x16 station Euclidean distance matrix"""

new_tree = """│   ├── raw/                                 # 1. IMMUTABLE RAW SOURCES (683 files)
│   │   ├── air_quality/                            # 36 original EPD monthly exports
│   │   ├── meteorology/                            # Hourly ERA5 surface reanalysis series
│   │   ├── traffic/monthly/                        # 36 monthly SpeedMap XML archives (774,686 snapshots)
│   │   └── station_metadata/                       # 16 included stations + 2 excluded stations
│   ├── interim/                             # 2. STANDARDIZED & ALIGNED DATA
│   │   ├── air_quality/clean_air_quality.parquet   # 420,864 rows, 55,876 natural NaNs preserved
│   │   ├── meteorology/clean_meteorology.parquet   # 420,864 rows, 0 NaNs, physical bounds verified
│   │   ├── traffic/clean_traffic_speedmap_complete.parquet # 774k snapshots, 466.8M records
│   │   └── aligned/                                # Phase 2 Spatio-Temporal Alignment Layer
│   │       ├── aligned_hourly_station_data.parquet # Unified 420,864 station-hour 13-channel grid
│   │       ├── traffic_hourly_link_data.parquet    # 15.7M records across 632 links
│   │       ├── traffic_station_hourly.parquet      # 418,448 rows (99.43% coverage, IDW p=2)
│   │       └── spatial_distance_matrix.npy         # 16x16 symmetric Haversine distance matrix"""

text = text.replace(old_tree, new_tree)

# 5. Table in Step 10
old_stage = """| **Stage 3A** | **Traffic Interpolation & Feature Merge** | ATC census files + Station coordinates | `data/interim/aligned_hourly_features.parquet` | Check that all 13 columns are non-empty and temporally aligned for 26,304 hours. |"""
new_stage = """| **Stage 3A** | **Traffic Interpolation & Feature Merge** | SpeedMap XML 632 links + Station coords | `data/interim/aligned/aligned_hourly_station_data.parquet` | Check that all 13 channels are temporally aligned for 26,304 hours (420,864 rows). |"""

text = text.replace(old_stage, new_stage)

with open("research/Reports/Data Processing - Hong Kong.md", "w") as f:
    f.write(text)

print("Updated research/Reports/Data Processing - Hong Kong.md successfully.")
