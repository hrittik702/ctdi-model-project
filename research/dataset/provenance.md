# Data Provenance & Cryptographic Hashes

All raw and interim data files are tracked with cryptographic SHA-256 hashes to guarantee data immutability and reproducibility.

---

## 1. Cryptographic Checksum Registry

| Description | Relative File Path | Size (Bytes) | SHA-256 Cryptographic Checksum | Status |
| :--- | :--- | :---: | :--- | :---: |
| Air Quality Stations Catalog | `data/raw/station_metadata/air_quality_stations.csv` | 1,563 | `30bb17250da7174bec73123570ee2bc2730faab2d5d126cb3141c180892186cb` | **`VERIFIED`** |
| Weather Stations Catalog | `data/raw/station_metadata/weather_stations.csv` | 4,210 | `748e8946e01a89f81a7a03079983424699fa48ff1140224d081f9a2ceebbc76b` | **`VERIFIED`** |
| EPD Hourly Air Quality (2019–2021) | `data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv` | 27,136,881 | `f2b1b46a9c8e69e2f18077fac4c4d4f664cb24162523dc978219d82c225b57b2` | **`VERIFIED`** |
| Hourly Meteorology (16 Stations) | `data/raw/meteorology/hourly_meteorology_16stations_2019_2021.csv` | 25,460,811 | `e2e7849675a6856286ff92c63334d2d6cae010d409446043c3a4b8a147fa47a3` | **`INTERIM`** |
| Annual Traffic Census Archive | `data/raw/traffic/ATC_TRAFFIC_DATA.zip` | 33,710,902 | `b2738720b17f47946cdebae2291bcb56eb0078a2603f412de13b328accfd84f7` | **`REJECTED`** |
| ATC Spatial KMZ Points | `data/raw/traffic/spatial/ATC_STATION_PT.kmz` | 67,197 | `a6ee2b2d0f21286bab5930925df557311a289654d86df40cfa1a972b83fa1ac0` | **`REFERENCE`** |
| Pairwise Spatial Distance Matrix | `data/interim/spatial_distance_matrix.npy` | 1,152 | Validated symmetric float32 matrix | **`VERIFIED`** |

---

## 2. Integrity Verification Command

To verify that local files match the registered checksums, run:
```bash
sha256sum data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv \
          data/raw/station_metadata/air_quality_stations.csv \
          data/raw/meteorology/hourly_meteorology_16stations_2019_2021.csv
```
