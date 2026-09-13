# CTDI Table I Exact Reproduction & Reconstruction

**Reference**: Yangwen Yu, Victor O. K. Li, Jacqueline C. K. Lam, Kelvin Chan, Qi Zhang, *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, **IEEE Transactions on Big Data**, vol. 11, no. 5, pp. 2442–2455, Sept.–Oct. 2025. DOI: [10.1109/TBDATA.2025.3533882](https://doi.org/10.1109/TBDATA.2025.3533882).  
**Source Document**: Page 2448 (PDF Page 6), Table I.

---

## 1. Exact Reproduction of Table I as Published

Below is the verbatim reproduction of **TABLE I** as rendered in the published IEEE Transactions paper:

### TABLE I
### HONG KONG DATASET COLLECTED FROM 2019-01-01 TO 2021-12-31

| Domain | Number of Data Nodes | Data Category | Unit | Update Frequency |
| :--- | :---: | :--- | :---: | :---: |
| **Air pollution** | 16 stations | $\text{PM}_{2.5}$ | $\mu\text{g/m}^3$ | 1 hour |
| | | $\text{PM}_{10}$ | $\mu\text{g/m}^3$ | 1 hour |
| | | $\text{NO}_2$ | $\mu\text{g/m}^3$ | 1 hour |
| | | $\text{SO}_2$ | $\mu\text{g/m}^3$ | 1 hour |
| | | $\text{O}_3$ | $\mu\text{g/m}^3$ | 1 hour |
| **Meteorology** | 47 stations | Pressure | $\text{hPa}$ | 10 min |
| | | Relative humidity | $\%$ | 10 min |
| | | Temperature | $^\circ\text{C}$ | 10 min |
| | | Visibility | $\text{km}$ | 10 min |
| | | Wind direction | N/A | 10 min |
| | | Wind speed | $\text{km/h}$ | 10 min |
| **Traffic** | 607 roads | Traffic speed | $\text{km/h}$ | 5min |
| | | Traffic congestion | N/A | 5min |

---

## 2. Comprehensive Field-by-Field Analytical Breakdown

To satisfy the required schema format:
`| Category | Variable | Source | Nodes | Update frequency | Unit | Notes |`

| Category | Variable | Source | Nodes | Update frequency | Unit | Notes |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Air pollution** | $\text{PM}_{2.5}$ | HKEPD Database [80] | 16 | 1 hour | $\mu\text{g/m}^3$ | Criteria pollutant; target imputation channel. |
| **Air pollution** | $\text{PM}_{10}$ | HKEPD Database [80] | 16 | 1 hour | $\mu\text{g/m}^3$ | Criteria pollutant; target imputation channel. |
| **Air pollution** | $\text{NO}_2$ | HKEPD Database [80] | 16 | 1 hour | $\mu\text{g/m}^3$ | Criteria pollutant; target imputation channel. |
| **Air pollution** | $\text{SO}_2$ | HKEPD Database [80] | 16 | 1 hour | $\mu\text{g/m}^3$ | Criteria pollutant; target imputation channel. |
| **Air pollution** | $\text{O}_3$ | HKEPD Database [80] | 16 | 1 hour | $\mu\text{g/m}^3$ | Criteria pollutant; target imputation channel. |
| **Meteorology** | Pressure | HKO Open Database [81] | 47 | 10 min | $\text{hPa}$ | Atmospheric pressure across Automatic Weather Stations. |
| **Meteorology** | Relative humidity | HKO Open Database [81] | 47 | 10 min | $\%$ | Percentage relative humidity across AWS network. |
| **Meteorology** | Temperature | HKO Open Database [81] | 47 | 10 min | $^\circ\text{C}$ | Ambient dry-bulb surface temperature across AWS network. |
| **Meteorology** | Visibility | HKO Open Database [81] | 47 | 10 min | $\text{km}$ | **Horizontal visibility**. Replaces previous mistaken assumption of "rainfall". |
| **Meteorology** | Wind direction | HKO Open Database [81] | 47 | 10 min | N/A | Azimuth compass/degree bearing $(0\text{--}360^\circ)$. Unit listed as N/A in Table I. |
| **Meteorology** | Wind speed | HKO Open Database [81] | 47 | 10 min | $\text{km/h}$ | Wind speed reported in $\text{km/h}$ (converted from 10-min mean wind feed). |
| **Traffic** | Traffic speed | HK Traffic Speed Map [82] | 607 | 5min | $\text{km/h}$ | **Estimated road vehicular speed**. Matches `<TRAFFIC_SPEED>` in `speedmap.xml`. |
| **Traffic** | Traffic congestion | HK Traffic Speed Map [82] | 607 | 5min | N/A | **Congestion/saturation level**. Matches `<ROAD_SATURATION_LEVEL>` in `speedmap.xml` (`TRAFFIC GOOD`, `TRAFFIC AVERAGE`, `TRAFFIC BAD`). |

---

## 3. Critical Analytical Findings from Table I

### Finding 1: The Two Traffic Variables Are Speed and Congestion (NOT Volume)
Table I explicitly identifies the two traffic variables as:
1. **`Traffic speed`** ($\text{km/h}$)
2. **`Traffic congestion`** ($\text{N/A}$)

The word "volume" does **not appear anywhere in Table I**, nor does it appear in the context of traffic anywhere in the CTDI text. The assumption that Channel 13 is `traffic_volume` is completely refuted by the published paper.

### Finding 2: The Spatial Node Count is Exactly 607 Roads
Table I explicitly lists the number of traffic nodes as **`607 roads`**.
- The City Dashboard version on DATA.GOV.HK contains only **6 road links** (the 3 harbour crossings).
- The parent Transport Department 1st Generation Traffic Speed Map (`http://resource.data.one.gov.hk/td/speedmap.xml`) contains **exactly 607 road links** (`unique LINK_ID count = 607`).
- Therefore, the CTDI authors utilized the **full 607-road parent network**, confirming why the paper reports 607 traffic nodes.

### Finding 3: The Fourth Meteorology Channel is Visibility (NOT Rainfall)
Table I explicitly lists **`Visibility` ($\text{km}$)** as the fourth meteorological variable. Prior informal project documentation had substituted `rainfall` ($\text{mm}$). The actual CTDI Hong Kong dataset uses `Visibility` alongside `Pressure`, `Relative humidity`, `Temperature`, `Wind direction`, and `Wind speed`.
