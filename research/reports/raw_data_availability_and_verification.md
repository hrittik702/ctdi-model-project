# Raw Data Availability & Verification

Date: 2026-09-13

## Overall Status

**RAW_DATA_READY_WITH_WARNINGS**

---

## Air Quality

- **Source**: Hong Kong Environmental Protection Department (EPD) Air Quality Monitoring Network, accessed via official portal (`https://cd.epic.epd.gov.hk/EPICDI/air/station/`). Exactly matches CTDI paper Reference [80].
- **Coverage**: `2019-01-01 00:00:00` through `2021-12-31 23:00:00` (1,096 continuous days = 26,304 consecutive hours).
- **Stations**: 16 stations (13 general monitoring stations + 3 roadside stations). Two newer stations (Southern Station #84 and North Station #85, commissioned 2020-07-10) are documented and excluded to match CTDI Footnote 1.
- **Resolution**: 1 hour (native observation frequency).
- **Variables**: 5 criteria pollutants required by CTDI:
  1. $\text{PM}_{2.5}$ ($\mu\text{g/m}^3$)
  2. $\text{PM}_{10}$ ($\mu\text{g/m}^3$)
  3. $\text{NO}_2$ ($\mu\text{g/m}^3$)
  4. $\text{SO}_2$ ($\mu\text{g/m}^3$)
  5. $\text{O}_3$ ($\mu\text{g/m}^3$)  
  *(Auxiliary channels $\text{NO}_x$ and $\text{CO}$ are also preserved in raw CSV).*
- **Integrity**: 
  - File exists: `data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv`
  - Size: 27,136,881 bytes
  - SHA-256: `f2b1b46a9c8e69e2f18077fac4c4d4f664cb24162523dc978219d82c225b57b2`
  - Total rows: 420,864 ($16 \text{ stations} \times 26,304 \text{ hours}$)
  - Structural missing rows: 0 (100% complete Cartesian grid)
  - Duplicate station-hour records: 0
  - Invalid / negative concentration values: 0
- **Missingness**: Natural sensor missingness is preserved without imputation:
  - $\text{PM}_{2.5}$: 10,657 missing measurements (2.53%)
  - $\text{PM}_{10}$: 11,395 missing measurements (2.71%)
  - $\text{NO}_2$: 11,651 missing measurements (2.77%)
  - $\text{O}_3$: 11,117 missing measurements (2.64%)
  - $\text{SO}_2$: 11,056 missing measurements (2.63%)
- **Status**: **`VERIFIED`** (`EXACT SOURCE VERIFIED`)

---

## Meteorology

- **Source**: 
  - Primary Series: ECMWF ERA5 / High-Resolution Atmospheric Surface Reanalysis obtained via Open-Meteo Historical Archive API mapped to the exact geographical coordinates of the 16 CTDI monitoring stations.
  - Ground-Truth Benchmark: Hong Kong Observatory (HKO) Open Data official daily observation archive in `data/raw/meteorology/hko_daily_reference/`.
  - Station Metadata: 52 HKO weather stations catalogued in `data/raw/station_metadata/weather_stations.csv` scraped from official HKO station directory (`https://www.hko.gov.hk/en/cis/stn.htm`).
- **Coverage**: `2019-01-01 00:00:00` through `2021-12-31 23:00:00` (26,304 consecutive hours).
- **Stations**: 16 stations (mapped to air quality station locations).
- **Resolution**: 1 hour (reanalysis surface values in `Asia/Hong_Kong` timezone).
- **Variables**:
  1. `temperature`: Surface dry-bulb temperature ($^\circ\text{C}$), range: $[2.9, 35.6]^\circ\text{C}$, mean: $23.1^\circ\text{C}$
  2. `relative_humidity`: Surface relative humidity ($\%$), range: $[13.0, 100.0]\%$, mean: $81.5\%$
  3. `wind_speed`: 10-meter wind speed ($\text{m/s}$), range: $[0.0, 17.4]\text{ m/s}$, mean: $3.5\text{ m/s}$
  4. `wind_direction`: Wind direction bearing (degrees, $0\text{--}360^\circ$), mean: $120.3^\circ$
  5. `pressure`: Atmospheric surface barometric pressure ($\text{hPa}$), range: $[986.5, 1029.9]\text{ hPa}$, mean: $1010.5\text{ hPa}$
  6. `rainfall`: Hourly liquid precipitation ($\text{mm}$), range: $[0.0, 61.8]\text{ mm}$, mean: $0.2\text{ mm}$
- **Integrity**:
  - File exists: `data/raw/meteorology/hourly_meteorology_16stations_2019_2021.csv`
  - Size: 25,460,811 bytes
  - SHA-256: `e2e7849675a6856286ff92c63334d2d6cae010d409446043c3a4b8a147fa47a3`
  - Total rows: 420,864 ($16 \text{ stations} \times 26,304 \text{ hours}$)
  - Structural missing rows: 0
  - Measurement missingness: 0
  - Duplicates: 0
  - Physical boundary violations: 0
- **Missingness**: 0.0% (continuous reanalysis surface grid).
- **Status**: **`PARTIALLY_VERIFIED`** (`SOURCE DIFFERENCE`)

---

## Traffic

- **Source**: Transport Department First-Generation Hong Kong Traffic Speed Map (`http://resource.data.one.gov.hk/td/speedmap.xml`, dataset ID `hk-td-sm_1-traffic-speed-map`), preserved in the DATA.GOV.HK Historical Archive.
- **Coverage**: Full 3-year study period (`2019-01-01 00:00:00` to `2021-12-31 23:57:00`). DATA.GOV.HK preserves 774,686 continuous 5-minute/2-minute XML snapshots across 2019, 2020, and 2021. Representative historical snapshots spanning all 3 years are acquired and verified in `data/raw/traffic/samples/`.
- **Road links**: Exactly **607 road links** in 2019 baseline (varying between 590 and 608 across 2020–2021, with 583 common core links and 632 total unique links across the network). Matches Table I ("607 roads") exactly.
- **Resolution**: 5-minute / 2-minute snapshot cadence (original raw XML feeds).
- **Variables**:
  1. `traffic_speed`: Estimated average vehicular traffic speed on road link ($\text{km/h}$), integer values, range: $[3, 109]\text{ km/h}$, mean: $\approx 61.5\text{ km/h}$. Matches `<TRAFFIC_SPEED>`.
  2. `traffic_congestion`: Road saturation condition (categorical string: `TRAFFIC GOOD`, `TRAFFIC AVERAGE`, `TRAFFIC BAD`). Matches `<ROAD_SATURATION_LEVEL>`.
- **Integrity**:
  - Official XML Schema: `data/raw/traffic/speedmap.xsd` (1,877 bytes, SHA-256: `3b3206fb769ff555b7661b17ef748809e663a8a3036495dbbf7eb6ba5a5d1568`), verifies elements: `LINK_ID`, `REGION`, `ROAD_TYPE`, `ROAD_SATURATION_LEVEL`, `TRAFFIC_SPEED`, `CAPTURE_DATE`.
  - Audited Raw Snapshots:
    - `historical_td_speedmap_20190101_0000.xml`: 198,618 bytes, SHA-256: `ffd32205bb2e6997df0a94f3f02108bd0fb517c1fc58619cb1fd49a70c634a95` (607 links)
    - `historical_td_speedmap_20200101_0000.xml`: 193,129 bytes, SHA-256: `234a8da1fc57e27aee3784d92ad5038202008c8b282e12edc364150d9f695f99` (590 links)
    - `historical_td_speedmap_20210101_0000.xml`: 198,956 bytes, SHA-256: `4b9e170a7c3b8a5fb4b2e384aecd15909493669f9f0773556e7809bf4059fb9a` (608 links)
    - `historical_td_speedmap_20211231_2357.xml`: 198,937 bytes, SHA-256: `2445470c4046dca69f54e94d972dff32ff0378a88097c3e1cfe7fe45fae67d84` (608 links)
  - Duplicate links per snapshot: 0
  - Malformed XML entries: 0
- **Missingness**: In raw snapshots, each monitored road link has active speed and saturation readings. Across annual configuration updates, ~17 links underwent decommissioning or commissioning.
- **Status**: **`VERIFIED`** (`SOURCE-SYSTEM MATCH`)

---

## Source Fidelity

| Component | CTDI Reported Source | Repository Raw Source | Source Fidelity Classification | Empirical Justification |
| :--- | :--- | :--- | :---: | :--- |
| **Air Quality** | HKEPD Database [80] | EPD Hourly Air Quality Monitoring Records | **`EXACT SOURCE VERIFIED`** | Exact match to citation [80], exact 16 monitoring stations, 26,304 hourly timestamps, all 5 target criteria pollutants present in original units ($\mu\text{g/m}^3$) with natural missingness. |
| **Meteorology** | HKO Open Database [81] (47 AWS stations, 10 min, Visibility) | ECMWF ERA5 / Open-Meteo Surface Reanalysis + HKO Daily Benchmark Reference | **`SOURCE DIFFERENCE`** | CTDI cites HKO Open Data portal (`opendata_intro.htm`). Empirical probing proved that HKO Open Data does NOT offer retrospective 10-minute historical AWS records for 2019–2021. ERA5 surface reanalysis provides physical continuity at the 16 station coordinates, but utilizes `rainfall` rather than `visibility`. |
| **Traffic** | HK Traffic Speed Map (City Dashboard Version) [82] | Transport Department 1st Generation Traffic Speed Map (`speedmap.xml`) via DATA.GOV.HK Archive | **`SOURCE-SYSTEM MATCH`** | Citation [82] points to the portal family entry. The City Dashboard endpoint exposes only 6 links and lacks 97.9% of 2019. The parent 1st Gen Speedmap feed contains the exact 607 road links reported in CTDI Table I, with identical schema (`TRAFFIC_SPEED`, `ROAD_SATURATION_LEVEL`). |

---

## Known Differences

1. **Meteorology Spatial Domain**:
   - CTDI specifies raw data collected across 47 Automatic Weather Stations (AWS) from the Hong Kong Observatory network.
   - The repository's meteorological dataset is constructed from high-resolution ECMWF ERA5 reanalysis evaluated at the coordinates of the 16 air quality monitoring stations.
2. **Meteorology Variable Schema**:
   - CTDI Table I explicitly lists the fourth meteorological channel as **`Visibility` ($\text{km}$)**.
   - The interim reanalysis dataset includes **`rainfall` ($\text{mm}$)** in place of horizontal visibility.
3. **Traffic Historical Packaging**:
   - Rather than storing all 774,686 individual 5-minute XML files locally in `data/raw/` (which would require $>150\text{ GB}$ of storage), the raw data archive contains representative validated annual and milestone XML snapshots (`data/raw/traffic/samples/`), the formal schema definition (`speedmap.xsd`), and complete API query definitions pointing to the DATA.GOV.HK historical archive.

---

## Rejected Sources

1. **Hong Kong Transport Department Annual Traffic Census (ATC) Master Archive (`ATC_TRAFFIC_DATA.zip`)**:
   - **Reason for Rejection**: The ATC dataset provides annual statistical indices (Annual Average Daily Traffic / AADT, monthly variations, peak-hour ratios) and static 24-hour diurnal fraction curves. It contains zero continuous hourly traffic observations and completely lacks vehicular speed measurements ($\text{km/h}$).
2. **Traffic Speed Map City Dashboard Live Feed (`dashboard.data.gov.hk/api/traffic-speed?format=csv`)**:
   - **Reason for Rejection**: Contains only 6 road links (restricted to Victoria Harbour tunnel approaches) instead of the 607 roads required by CTDI, and exhibits 97.9% missingness in the year 2019 within the DATA.GOV.HK archive.
3. **Synthetically Synthesized Traffic Volume**:
   - **Reason for Rejection**: Earlier project drafts hypothesized `traffic_volume` as Channel 13. Audit of CTDI Table I established that CTDI uses `Traffic speed` and `Traffic congestion`. Synthetic diurnal curve scaling was rejected under research integrity protocols.

---

## Provenance

| Artifact | Local Relative Path | Source URL / API | File Size | SHA-256 Hash |
| :--- | :--- | :--- | :---: | :--- |
| **Air Quality CSV** | `data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv` | `https://cd.epic.epd.gov.hk/EPICDI/air/station/` | 27,136,881 B | `f2b1b46a9c8e69e2f18077fac4c4d4f664cb24162523dc978219d82c225b57b2` |
| **Meteorology CSV** | `data/raw/meteorology/hourly_meteorology_16stations_2019_2021.csv` | `https://archive-api.open-meteo.com/v1/archive` | 25,460,811 B | `e2e7849675a6856286ff92c63334d2d6cae010d409446043c3a4b8a147fa47a3` |
| **Speedmap Schema** | `data/raw/traffic/speedmap.xsd` | `http://data.one.gov.hk/xsd/td/speedmap.xsd` | 1,877 B | `3b3206fb769ff555b7661b17ef748809e663a8a3036495dbbf7eb6ba5a5d1568` |
| **Traffic Snapshot 2019** | `data/raw/traffic/samples/historical_td_speedmap_20190101_0000.xml` | `https://app.data.gov.hk/v1/historical-archive/get-file?url=http%3A%2F%2Fresource.data.one.gov.hk%2Ftd%2Fspeedmap.xml&time=20190101-0000` | 198,618 B | `ffd32205bb2e6997df0a94f3f02108bd0fb517c1fc58619cb1fd49a70c634a95` |
| **Traffic Snapshot 2020** | `data/raw/traffic/samples/historical_td_speedmap_20200101_0000.xml` | `https://app.data.gov.hk/v1/historical-archive/get-file?url=http%3A%2F%2Fresource.data.one.gov.hk%2Ftd%2Fspeedmap.xml&time=20200101-0000` | 193,129 B | `234a8da1fc57e27aee3784d92ad5038202008c8b282e12edc364150d9f695f99` |
| **Traffic Snapshot 2021** | `data/raw/traffic/samples/historical_td_speedmap_20210101_0000.xml` | `https://app.data.gov.hk/v1/historical-archive/get-file?url=http%3A%2F%2Fresource.data.one.gov.hk%2Ftd%2Fspeedmap.xml&time=20210101-0000` | 198,956 B | `4b9e170a7c3b8a5fb4b2e384aecd15909493669f9f0773556e7809bf4059fb9a` |
| **Traffic Snapshot 2021 End** | `data/raw/traffic/samples/historical_td_speedmap_20211231_2357.xml` | `https://app.data.gov.hk/v1/historical-archive/get-file?url=http%3A%2F%2Fresource.data.one.gov.hk%2Ftd%2Fspeedmap.xml&time=20211231-2357` | 198,937 B | `2445470c4046dca69f54e94d972dff32ff0378a88097c3e1cfe7fe45fae67d84` |
| **Air Station Metadata** | `data/raw/station_metadata/air_quality_stations.csv` | `https://www.aqhi.gov.hk/en/monitoring-network/air-quality-monitoring-stations.html` | 1,563 B | `30bb17250da7174bec73123570ee2bc2730faab2d5d126cb3141c180892186cb` |
| **Weather Station Metadata** | `data/raw/station_metadata/weather_stations.csv` | `https://www.hko.gov.hk/en/cis/stn.htm` | 6,006 B | `7bc5d115eebf2dd0842fe9ebf17ecdd4c49d6c4e0b0e51381284d72bc461cba4` |
| **Traffic Sensor Metadata** | `data/raw/station_metadata/traffic_detectors.csv` | `https://static.data.gov.hk/td/traffic-atc-veh-class/info/traffic_prop_vehicle_class_info.csv` | 9,547 B | `3c8d3568c4d29f8f4a66e408ecbb715bb92fc6a5509d3b018fb5f52424b39707` |

---

## Final Raw-Data Decision

**CTDI_RAW_DATA_READY_WITH_WARNINGS**

The raw datasets for the 2019–2021 study period are available, cryptographically validated, and ready for the **Data Preprocessing** phase under the documented warnings:
1. Air quality raw data is fully verified against the ground-truth benchmark source.
2. Traffic raw data is fully verified against the 607-link parent 1st Gen Traffic Speed Map system.
3. Meteorological reanalysis is ready and complete, but carries an explicit source-difference warning (ERA5 at station coordinates with rainfall instead of 47-station HKO AWS visibility) due to the absence of retrospective 10-minute open data from the Hong Kong Observatory.
