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

## Decision D03: Investigation of `visibility` vs `rainfall` for CTDI Source Alignment

- **Date**: 2026-09-13 (Updated 2026-09-17)
- **Status**: **`SUPERSEDED_BY_D07`**

### Context
Interim reanalysis datasets downloaded from Open-Meteo included `rainfall` ($\text{mm}$) as the fourth weather channel. Initial audit required attempting to recover HKO visibility to match CTDI Table I.

### Evidence
Table I of Yu et al. (2025) explicitly specifies `Visibility` ($\text{km}$) from the Hong Kong Observatory Open Database [81] across 47 weather stations. Rainfall is not present in Table I.
However, subsequent exhaustive empirical investigation of DATA.GOV.HK, the HKO Open Data API, and archival endpoints revealed that retrospective 10-minute historical visibility across 47 stations does not exist in open public data. Furthermore, the CTDI paper's acknowledgments (Page 2454) disclose that the authors obtained an offline dataset from Dr. Yang Han at HKU. Public HKO AWS visibility was formally proven **`[IRRECOVERABLE]`** from open sources (see [Visibility Data Recovery & Provenance Report.md](../Reports/Visibility%20Data%20Recovery%20&%20Provenance%20Report.md)).

### Decision
Acknowledge the public irrecoverability of HKO 10-minute AWS historical visibility. Formally superseded by **Decision D07**, which establishes the documented adoption of ERA5 surface rainfall for Channel 9 with explicit scientific justification.

### Alternatives Considered
1. Continuing to search public open data endpoints: Proven exhausted and fruitless.
2. Fabricating synthetic visibility from airport or humidity records: Strictly prohibited under research integrity protocol.

### Why Alternatives Were Rejected
Scientific integrity requires reporting genuine empirical data and documented differences rather than fabricating ungrounded proxies.

### Consequences
Channel 9 is formally designated as `rainfall` in our reconstructed dataset (`ctdi_aligned_reconstructed`), while documenting the exact source difference against CTDI Table I.

### Revisit Conditions
Only if the CTDI authors release their private raw weather cache or HKO publishes historical 10-minute AWS archives.

---

## Decision D04: Absolute Prohibition Against Synthetic Traffic Injection & Phase 1.1 Resolution

- **Date**: 2026-09-13 (Updated 2026-09-17)
- **Status**: **`ACCEPTED_AND_SATISFIED`**

### Context
Because historical hourly traffic CSVs were not yet compiled, there was temptation to interpolate or synthesize missing 2019 traffic values to unblock pipeline execution.

### Evidence
Injecting synthetic data into a benchmark dataset corrupts scientific comparison with published baselines and produces invalid evaluation metrics.

### Decision
Enforce a programmatic safety halt in `src/preprocessing/alignment.py`. If real traffic data is unavailable, the pipeline must raise `FileNotFoundError` and halt immediately.

### Empirical Resolution (Phase 1.1 & Phase 2)
In Phase 1.1, the full 3-year historical traffic archive was extracted from the parent Transport Department 1st Generation Traffic Speed Map (`speedmap.xml`):
- **774,686 snapshots** parsed across all 36 months ($1,096/1,096$ continuous days, 0 missing days).
- **466,829,497 link records** extracted across 632 unique links in network union ($590$ core links).
- Speeds in $[0, 111]\text{ km/h}$ (mean $57.66\text{ km/h}$).

In Phase 2, sub-hourly records were aggregated to hourly link means and spatially projected via IDW ($p=2$) to the 16 air quality stations. In strict compliance with D04:
- **Zero synthetic traffic coordinates or values were fabricated**.
- $2,416$ station-hours of natural archive missingness were preserved as genuine `NaN`s ($99.43\%$ empirical coverage), strictly avoiding artificial $0\text{ km/h}$ standstill filling.
- The programmatic safety assertion passed cleanly with 100% real empirical data.

### Alternatives Considered
Synthesize 2019 traffic from diurnal curves or spline interpolation.

### Why Alternatives Were Rejected
Violates core scientific integrity principles. Benchmarks evaluated on synthetic data are invalid.

### Consequences
Tensor assembly was safely gated until real empirical traffic extraction was fully accomplished.

### Revisit Conditions
Permanent policy. Never inject synthetic data into ground truth benchmark datasets.

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

---

## Decision D07: Formal Adoption of ERA5 Rainfall Substitution for Channel 9

- **Date**: 2026-09-17
- **Status**: **`ACCEPTED`**

### Context
Following the conclusion of the visibility irrecoverability audit (proving that retrospective 10-minute HKO AWS visibility is unavailable from public open data and was acquired privately by the CTDI authors), the project required a scientifically grounded, continuous, and complete replacement channel to maintain the 13-channel multimodal tensor formulation ($\mathbf{X} \in \mathbb{R}^{16 \times 26,304 \times 13}$).

### Evidence
1. **Physical & Atmospheric Scavenging Justification**: In atmospheric physics and environmental chemistry, precipitation / rainfall is the primary driver of wet deposition (aerosol scavenging and washout of $\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{SO}_2$, and $\text{NO}_2$). It provides a powerful physically coupled conditioning signal for generative diffusion models.
2. **Completeness & Continuity**: ECMWF ERA5 atmospheric reanalysis provides continuous hourly surface precipitation at the 16 air quality station coordinates with exactly zero missing values ($420,864$ observations) across the entire 2019–2021 study period.
3. **Empirical Distribution**: Audited in `research/Reports/Rainfall Feature Investigation.md`: $134,101$ non-zero station-hours ($31.86\%$), range $[0.0, 61.8]\text{ mm}$, mean $0.24\text{ mm}$.
4. **Architectural Compatibility**: Preserves the exact 13-channel rank and shape required for downstream spatial graph and temporal attention layers without structural modification.

### Decision
Formally adopt ERA5 hourly rainfall ($\text{mm}$) as Channel 9 of our reconstructed benchmark dataset (`ctdi_aligned_reconstructed`). Maintain strict naming integrity (`rainfall`, NEVER disguised or mislabeled as `visibility`). Explicitly document the source difference in all publications, consistency matrices, and reports per Decision D06.

### Alternatives Considered
1. *Synthesize pseudo-visibility from relative humidity and aerosol extinction formulas*: Rejected under Decision D04 (violates Zero-Fabrication Protocol).
2. *Drop Channel 9 to create a 12-channel tensor*: Rejected because it breaks architectural tensor parity with published 13-channel CTDI configurations.
3. *Use daily airport visibility summaries*: Rejected because a single daily scalar cannot capture diurnal hourly variations across 16 stations.

### Why Alternatives Were Rejected
Fabrication and ungrounded approximations compromise scientific validity. Dropping channels breaks model tensor geometry.

### Consequences
Channel 9 is labeled `rainfall` throughout the pipeline and datasets (`data/interim/aligned/aligned_hourly_station_data.parquet`). Datasets are explicitly designated as `ctdi_aligned_reconstructed` with documented source divergence.

### Revisit Conditions
Only if the CTDI authors' unreleased HKO AWS visibility dataset is officially published or provided.
