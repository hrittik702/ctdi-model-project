# Station Inventory & Spatial Network Analysis

---

## 1. The 16 Stations Included in CTDI

All 16 of the following air quality monitoring stations operated continuously throughout the study period (**2019-01-01 00:00 to 2021-12-31 23:00**):

| # | Station ID | Station Name | Type | Latitude (°N) | Longitude (°E) | Sampling Height | Topography & Exposure |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | `80` | **Central / Western** | General | 22.2848 | 114.1441 | 16 m | High-density urban commercial/residential |
| **2** | `73` | **Eastern** | General | 22.2831 | 114.2190 | 15 m | Coastal residential, Victoria Harbour corridor |
| **3** | `74` | **Kwun Tong** | General | 22.3107 | 114.2312 | 15 m | Industrial / high-density mixed urban |
| **4** | `66` | **Sham Shui Po** | General | 22.3304 | 114.1591 | 17 m | Dense older urban street canyon network |
| **5** | `72` | **Kwai Chung** | General | 22.3569 | 114.1293 | 13 m | Container port, industrial logistics corridor |
| **6** | `77` | **Tsuen Wan** | General | 22.3715 | 114.1146 | 17 m | High-density new town basin, coastal |
| **7** | `83` | **Tseung Kwan O** | General | 22.3173 | 114.2596 | 16 m | Coastal planned residential valley (opened 2016) |
| **8** | `70` | **Yuen Long** | General | 22.4450 | 114.0227 | 25 m | Inland northwestern basin, regional transport |
| **9** | `82` | **Tuen Mun** | General | 22.3911 | 113.9768 | 27 m | Western maritime / industrial channel |
| **10** | `78` | **Tung Chung** | General | 22.2885 | 113.9431 | 28 m | Lantau Island, near HKIA, regional ozone trap |
| **11** | `69` | **Tai Po** | General | 22.4508 | 114.1644 | 28 m | Northeastern valley residential new town |
| **12** | `75` | **Sha Tin** | General | 22.3764 | 114.1846 | 25 m | Mountain-bounded valley corridor |
| **13** | `76` | **Tap Mun** | General (Rural) | 22.4757 | 114.3619 | 11 m | Isolated northeastern island, regional background |
| **14** | `71` | **Causeway Bay** | Roadside | 22.2801 | 114.1855 | 3 m | Heavy commercial canyon, direct vehicular exhaust |
| **15** | `79` | **Central** | Roadside | 22.2802 | 114.1606 | 4.5 m | Financial district corridor, extreme bus/taxi flow |
| **16** | `81` | **Mong Kok** | Roadside | 22.3225 | 114.1685 | 3 m | Extreme street canyon, severe pedestrian exposure |

---

## 2. Empirical Verification of the 2 Excluded Stations

Footnote 1 of Yu et al. (2025, Page 2447) states:  
> *"Air pollution data from two new air pollution monitoring stations in Hong Kong are not included for data consistency."*

Our audit of EPD historical station commissioning records confirms:

| Station ID | Station Name | Type | Latitude (°N) | Longitude (°E) | Commission Date | Reason for Exclusion |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| `84` | **Southern** | General | 22.2472 | 114.1603 | **July 10, 2020** | Did not exist during 2019 or early 2020 (missing first 18 months). |
| `85` | **North** | General | 22.4969 | 114.1283 | **July 10, 2020** | Did not exist during 2019 or early 2020 (missing first 18 months). |

### Archival Evidence
- Inspection of EPD monthly CSV files (`data/raw/air_quality/monthly_raw/`):
  - `201901_Eng.csv` to `202005_Eng.csv`: Exactly 16 stations are present.
  - `202006_Eng.csv` onward: Southern and North appear, expanding the network to 18 stations.
- Retaining Southern and North would inject a 100% missingness block of $18 \times 24 \times 30 \approx 13,000$ consecutive hours per station, violating the temporal continuity required for fair benchmarking.
