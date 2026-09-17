# Dataset Decision Records

---

## Decision D01: Strict Adoption of CTDI Table I 13-Channel Formulation

- **Date**: 2026-09-13
- **Status**: **`ACCEPTED`**

### Context
To rigorously benchmark our proposed generative diffusion model against the published state-of-the-art (Yu et al., *IEEE Transactions on Big Data*, vol. 11, no. 5, 2025), we must determine the exact feature channels required for fair and valid comparison.

### Evidence
Page 2448 (PDF Page 6), Table I of Yu et al. (2025) explicitly enumerates the Hong Kong dataset collected from 2019-01-01 to 2021-12-31:
- 5 air pollutants: $\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{SO}_2, \text{O}_3$.
- 6 meteorological variables: Pressure, Relative humidity, Temperature, Visibility, Wind direction, Wind speed.
- 2 traffic variables: Traffic speed, Traffic congestion.
Total channels: $5 + 6 + 2 = 13$.

### Decision
Construct the canonical benchmark tensor with exactly $C = 13$ feature channels:
`['pm25', 'pm10', 'no2', 'so2', 'o3', 'pressure', 'relative_humidity', 'temperature', 'visibility', 'wind_direction', 'wind_speed', 'traffic_speed', 'traffic_congestion']`.

### Alternatives Considered
1. *Evaluate only on the 5 criteria pollutants*: Simplifies data collection, but ignores traffic and meteorology, preventing comparison with CTDI's primary multi-modal model (Dataset AU in Section V-C).
2. *Arbitrary multi-modal feature expansion (e.g., adding rainfall, CO, solar radiation)*: Prevents direct comparison with published CTDI figures.

### Why Alternatives Were Rejected
Direct comparison against the published CTDI baseline requires matching their exact multi-modal input tensor geometry.

### Consequences
Requires collecting and aligning all 13 channels across the 3-year study period.

### Revisit Conditions
Only if the CTDI authors formally release an erratum altering their published feature space.

---

## Decision D02: Rejection of `traffic_volume` & Adoption of `traffic_congestion`

- **Date**: 2026-09-13
- **Status**: **`ACCEPTED`**

### Context
Earlier informal project documents and scripts assumed Channel 13 was `traffic_volume` (veh/h) derived from the Annual Traffic Census (ATC).

### Evidence
1. Table I of Yu et al. (2025) explicitly specifies:
   - Variable: `Traffic congestion`
   - Unit: `N/A`
   - Update Frequency: `5min`
   - Nodes: `607 roads`
2. The word "volume" appears zero times in Table I and zero times in reference to traffic features in the CTDI text.
3. The Traffic Speed Map XML feed (`speedmap.xml`) contains `<ROAD_SATURATION_LEVEL>` (`TRAFFIC GOOD`, `TRAFFIC AVERAGE`, `TRAFFIC BAD`) matching Table I's description.

### Decision
Definitively reject `traffic_volume`. Define Channel 13 as `traffic_congestion` mapped from `ROAD_SATURATION_LEVEL`.

### Alternatives Considered
Retaining `traffic_volume` via ATC census files.

### Why Alternatives Were Rejected
ATC census data provides only annual aggregates, completely lacks speed, and does not match the published CTDI paper.

### Consequences
Eliminates reliance on ATC census files. Requires parsing `<ROAD_SATURATION_LEVEL>` from historical `speedmap.xml` snapshots.

### Revisit Conditions
Never; published evidence is conclusive.

---

## Decision D03: Replacement of `rainfall` with `visibility` for CTDI Source Alignment

- **Date**: 2026-09-13
- **Status**: **`ACCEPTED`**

### Context
Interim reanalysis datasets downloaded from Open-Meteo included `rainfall` ($\text{mm}$) as the fourth weather channel.

### Evidence
Table I of Yu et al. (2025) explicitly specifies `Visibility` ($\text{km}$) from the Hong Kong Observatory Open Database [81] across 47 weather stations. Rainfall is not present in Table I.

### Decision
Replace `rainfall` with `visibility` as Channel 9. In the interim reanalysis table, explicitly flag rainfall as a source-fidelity divergence until HKO visibility records are ingested.

### Alternatives Considered
Continuing to use rainfall as a proxy.

### Why Alternatives Were Rejected
Rainfall in Hong Kong is zero for $>90\%$ of hours (extreme zero-inflation), whereas visibility is a continuous indicator of atmospheric aerosol loading and photochemical haze.

### Consequences
Requires acquiring HKO historical visibility records.

### Revisit Conditions
Never; Table I explicitly specifies Visibility.

---

## Decision D04: Absolute Prohibition Against Synthetic Traffic Injection

- **Date**: 2026-09-13
- **Status**: **`ACCEPTED`**

### Context
Because historical hourly traffic CSVs were not yet compiled, there was temptation to interpolate or synthesize missing 2019 traffic values to unblock pipeline execution.

### Evidence
Injecting synthetic data into a benchmark dataset corrupts scientific comparison with published baselines and produces invalid evaluation metrics.

### Decision
Enforce a programmatic safety halt in `src/preprocessing/alignment.py`. If real traffic data is unavailable, the pipeline must raise `FileNotFoundError` and halt immediately.

### Alternatives Considered
Synthesize 2019 traffic from diurnal diurnal curves or spline interpolation.

### Why Alternatives Were Rejected
Violates core scientific integrity principles. Benchmarks evaluated on synthetic data are invalid.

### Consequences
Dataset tensor assembly is blocked until real historical traffic snapshots are parsed.

### Revisit Conditions
Never. Real data only.

---

## Decision D05: Exclusion of Southern (#84) & North (#85) Stations

- **Date**: 2026-09-12
- **Status**: **`ACCEPTED`**

### Context
Hong Kong EPD currently operates 18 stations. CTDI states: *"Two newer Hong Kong air-pollution monitoring stations were excluded for data consistency."*

### Evidence
EPD monthly records prove that Southern (Station 84) and North (Station 85) were commissioned on July 10, 2020. They did not exist in 2019 or early 2020. Retaining them would introduce an 18-month 100% structural missingness block.

### Decision
Exclude Southern (#84) and North (#85), restricting the spatial domain strictly to the 16 continuous stations.

### Alternatives Considered
Retain all 18 stations.

### Why Alternatives Were Rejected
Would introduce massive unrecoverable missingness and violate CTDI benchmark specifications.

### Consequences
Preserves a balanced Cartesian grid of $16 \times 26,304 = 420,864$ station-hour rows.

### Revisit Conditions
Only if expanding study period to post-2021 where all 18 stations are operational.

---

## Decision D06: Distinguishing Source-System Reconstruction from Exact Raw Dataset Reproduction

- **Date**: 2026-09-13
- **Status**: **`ACCEPTED`**

### Context
When reconstructing a published research dataset, researchers often confuse matching the source system with having the identical raw files.

### Evidence
While we have proven that the CTDI authors used the 607-road 1st Gen Speedmap, HKEPD air quality, and HKO weather, we do not possess their exact private download cache or unreleased intermediate scripts.

### Decision
Strictly distinguish between:
1. **Source-System Reconstruction**: Verified schemas, endpoints, formulas, and link counts.
2. **Exact Raw Dataset Reproduction**: Byte-for-byte identical numbers.
Never describe our reconstructed dataset as "identically reproduced" unless empirically proven by tensor cross-correlation.

### Alternatives Considered
Claiming full dataset reproduction based on matching Table I.

### Why Alternatives Were Rejected
Scientifically dishonest; minor differences in scraper timestamps, IDW distance rounding, or boundary clipping can yield numerical discrepancies.

### Consequences
Maintains absolute intellectual honesty in all publications and reports.

### Revisit Conditions
Permanent policy.
