# CTDI Traffic Variable Verification & Spatial Reconstruction Report

**Project**: Research-Grade CTDI Dataset Reconstruction  
**Focus**: Verification of Traffic Variables, Source Systems, IDW Formulation, and Spatial Network

---

## 1. Candidate Variable Evidence Matrix

We conducted an exhaustive textual and visual examination of the published CTDI paper (*IEEE Transactions on Big Data*, 2025). The results for every candidate traffic variable are summarized below:

| Candidate Variable | Status Classification | Direct Paper Evidence | Notes & Official System Mapping |
| :--- | :---: | :--- | :--- |
| **`traffic_speed`** | **`EXPLICITLY_USED`** | **Table I explicitly lists `Traffic speed`** (Domain: Traffic, Unit: $\text{km/h}$, Update Frequency: 5min, Nodes: 607 roads). Section III-A cites "traffic speed" as a key urban factor. | Corresponds to `<TRAFFIC_SPEED>` in `speedmap.xml` and `traffic_speed` in City Dashboard. |
| **`road_saturation_level` / `traffic_congestion`** | **`EXPLICITLY_USED`** | **Table I explicitly lists `Traffic congestion`** (Domain: Traffic, Unit: $\text{N/A}$, Update Frequency: 5min, Nodes: 607 roads). Section V-C discusses "traffic conditions". | Corresponds to `<ROAD_SATURATION_LEVEL>` in `speedmap.xml` and `road_saturation_level` in City Dashboard (`TRAFFIC GOOD`, `TRAFFIC AVERAGE`, `TRAFFIC BAD`). |
| **`traffic_volume`** | **`NOT_USED`** | **Zero occurrences in CTDI paper.** The word "volume" appears only in reference to tensor size ("input volume") and 3D medical segmentation [53]. | Not collected by the Traffic Speed Map system. Any volume variable in 13-channel CTDI is unevidenced. |
| **`traffic_flow`** | **`NOT_USED`** | Mentioned once in reference [60] title, never used as an experimental variable in CTDI. | Not present in Table I or official Speedmap feeds. |
| **`traffic_count`** | **`NOT_USED`** | Zero occurrences in CTDI paper text and tables. | Census concept, not part of continuous speedmap system. |
| **`vehicle_speed`** | **`STRONGLY_SUPPORTED`** | Direct semantic synonym for `traffic_speed`. Table I uses the exact phrase `Traffic speed`. | Standard transport nomenclature for speed along a link. |
| **`road occupancy`** | **`NOT_USED`** | Zero occurrences in CTDI paper. | Only introduced in 2nd-gen detectors (`sm_4`) in March 2021. |

---

## 2. Investigation of Reference [82] & The Six-Link vs 607-Link Resolution

### The Apparent Paradox
- In Section IV-A, the authors state:  
  *"The dataset used was obtained from three online Hong Kong databases, namely ... Hong Kong Traffic Speed Map (City Dashboard Version) Database [82]."*
- In Bibliography [82], the citation is:  
  *"Hong Kong Traffic Speed Map. Accessed: Aug. 31, 2022. [Online]. Available: https://data.gov.hk/en-data/dataset/hk-ogcio-da_div_02-citydashboard-traffic-speed"*
- However, the DATA.GOV.HK City Dashboard portal metadata (`traffic-speed-info.csv`) exposes **only 6 road links** (the 3 Victoria Harbour crossings).
- Meanwhile, in **Table I**, the authors explicitly document the traffic domain as possessing:  
  **`Number of Data Nodes = 607 roads`**

### Empirical Proof of Resolution
1. We queried the DATA.GOV.HK historical archive for the parent Transport Department 1st Generation Traffic Speed Map (`http://resource.data.one.gov.hk/td/speedmap.xml`, dataset ID `hk-td-sm_1-traffic-speed-map`).
2. We parsed an actual snapshot from `2019-01-01 00:00 HKT` (archived member `ffd32205bb2e...`).
3. The empirical link count in the parent system is:
   $$\text{Unique Links in Snapshot} = \mathbf{607}$$
4. The 6 harbour crossing links present in the City Dashboard feed are an **exact subset** of these 607 links (`4651-4631`, `46319-46512`, `4650-3651`, `36511-46502`, `4652-4633`, `46332-46522`).
5. **Conclusion**: The authors accessed the Transport Department's 1st Generation Traffic Speed Map which covers **607 road links** across Hong Kong Island, Kowloon, Sha Tin, and Tuen Mun, while citing the official DATA.GOV.HK portal entry for the Traffic Speed Map family.

---

## 3. Critical Reconstruction of CTDI's IDW Spatial Interpolation

Section III-A (Equation 1, Page 2445) specifies the exact mathematical formula used to map urban factors to air quality stations:

$$u'_j = \begin{cases} \frac{\sum_{i=1}^N w_{ij} u_i}{\sum_{i=1}^N w_{ij}} & \text{if } d(i, j) \neq 0 \\ u_i & \text{if } d(i, j) = 0 \end{cases}$$

where:
- $u_i$: Raw urban measurement (traffic speed or numeric congestion index) at the $i$-th source location ($i \in \{1, \dots, 607\}$).
- $u'_j$: Mapped urban value at the $j$-th air quality monitoring station ($j \in \{1, \dots, 16\}$).
- $w_{ij} = \frac{1}{d(i, j)^p}$ with power parameter $p = 2$ (squared inverse Euclidean / Haversine distance).
- $d(i, j)$: Spatial distance between road link centroid $i$ and air station $j$.

### Detailed Answers to the 10 IDW Operational Questions:

1. **Original Observation Locations**: Geographic centroids of the 607 road links in the Hong Kong Traffic Speed Map.
2. **Number of Source Locations ($N$)**: Exactly $N = 607$ road links.
3. **Coordinates**: WGS84 latitude and longitude computed as the midpoint between each road link's start node and end node:
   $$\phi_{\text{centroid}} = \frac{\phi_{\text{start}} + \phi_{\text{end}}}{2}, \quad \lambda_{\text{centroid}} = \frac{\lambda_{\text{start}} + \lambda_{\text{end}}}{2}$$
4. **Records Used**: 5-minute speed and saturation level observations aggregated to hourly arithmetic means:
   *"To standardize the frequency of each type of data to one hour ... data updated more than once per hour was averaged over the hour."* (Section IV-A).
5. **Timestamp Independence**: IDW is evaluated independently for each hour $t \in \{1, \dots, 26,304\}$ across all unmasked road links.
6. **Missing Source Observations**: If link $i$ is unobserved at timestamp $t$, it is excluded from the summation:
   $$u'_{j, t} = \frac{\sum_{i \in \mathcal{O}_t} w_{ij} u_{i, t}}{\sum_{i \in \mathcal{O}_t} w_{ij}}$$
7. **Zero Distance ($d(i, j) = 0$)**: The exact piecewise definition in Equation (1) assigns $u'_j = u_i$ directly, avoiding division by zero.
8. **Source Node Scope**: Global network summation across all available source links; no artificial distance boundary is imposed.
9. **Cutoff Threshold**: The squared distance decay ($w_{ij} = 1 / d(i, j)^2$) intrinsically downweights distant roads (e.g. roads $20\text{ km}$ away have weights $1/400$ relative to a road at $1\text{ km}$).
10. **Spatial Representation**: Road links are treated as spatial point observations located at their link centroids.

---

## 4. Temporal Coverage & Historical Archive Verification (2019–2021)

Target Study Duration: `2019-01-01 00:00` to `2021-12-31 23:00` ($1,096\text{ days} = \mathbf{26,304}\text{ hours}$).

### City Dashboard Endpoint (`dashboard.data.gov.hk/api/traffic-speed?format=csv`)
- **2019**: Archive contains $4,870$ versions spanning `2019-12-24 08:34` to `2019-12-31 23:59`.
  - Available hours: $\approx 183\text{ hours}$ ($2.1\%$ of 2019).
  - Missing hours: $8,577\text{ hours}$ ($97.9\%$ of 2019).
- **2020**: Fully archived ($10,000+$ snapshots, continuous $\approx 2\text{-min}$ cadence). $8,784\text{ hours}$ ($100.0\%$).
- **2021**: Fully archived ($10,000+$ snapshots, continuous $\approx 2\text{-min}$ cadence). $8,760\text{ hours}$ ($100.0\%$).
- **Total Temporal Completeness**: $17,727 / 26,304 = \mathbf{67.4\%}$.

### Parent 1st Gen Speedmap Endpoint (`resource.data.one.gov.hk/td/speedmap.xml`)
- **Total Archived Versions**: **$774,686\text{ snapshots}$** in DATA.GOV.HK historical archive.
- **2019**: Continuously available from `20190101-0000` to `20191231-2359` ($8,760\text{ hours}$, $100.0\%$).
- **2020**: Continuously available from `20200101-0000` to `20201231-2359` ($8,784\text{ hours}$, $100.0\%$).
- **2021**: Continuously available from `20210101-0000` to `20211231-2359` ($8,760\text{ hours}$, $100.0\%$).
- **Total Temporal Completeness**: $26,304 / 26,304 = \mathbf{100.0\%}$.
- **Nodes Monitored**: Exactly $607$ road links.
