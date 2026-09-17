# Raw Data Ingestion Protocol

---

## 1. Automated Scripts Inventory

The following ingestion scripts in `scripts/` govern raw public data acquisition:

| Script Path | Target Domain | Source Authority | Outputs Created |
| :--- | :--- | :--- | :--- |
| `scripts/download_epd_air_quality.py` | Air Pollutants | HKEPD AQHI Monthly Archives | 36 raw monthly CSVs in `data/raw/air_quality/monthly_raw/` |
| `scripts/process_air_quality.py` | Air Pollutants | Cleaned EPD Monthly Files | Unified `data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv` |
| `scripts/download_meteorology.py` | Meteorology | Open-Meteo API / HKO Reference | `hourly_meteorology_16stations_2019_2021.csv` + HKO daily reference files |
| `scripts/download_traffic.py` | Traffic | Transport Department Portals | Downloads ATC zip and city dashboard samples |
| `scripts/build_station_metadata.py` | Topography | EPD & HKO Station Catalogs | `data/raw/station_metadata/air_quality_stations.csv` |

---

## 2. Strict Research Integrity Ingestion Rules

1. **Immutable Raw Caches**: Files stored under `data/raw/` are treated as write-once, read-only artifacts. Raw files must never be manually edited or modified in place.
2. **Deterministic Logging**: Every download operation records the source URL, timestamp, HTTP status, and resulting file hash in `data/raw/source_manifest.json`.
3. **No Synthetic Fallbacks**: If an endpoint fails, times out, or contains an unrecoverable gap, the script must report an error rather than generating fallback synthetic numbers.
