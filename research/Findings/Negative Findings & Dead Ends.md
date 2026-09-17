# Negative Findings & Rejected Dead Ends

Documenting unsuccessful investigations, refuted hypotheses, and flawed source assumptions is essential to prevent current and future researchers from wasting weeks rediscovering the same dead ends.

---

## Negative Finding N01: Annual Traffic Census (ATC) Cannot Provide Continuous Hourly Series

- **What was tested**: Attempted to use the Transport Department Annual Traffic Census archive (`ATC_TRAFFIC_DATA.zip`) to construct 26,304 hourly traffic values for the 16 stations.
- **What was found**: Detailed parsing of `ATC_TRAFFIC_DATA/` revealed that ATC provides only annual average daily traffic (AADT), monthly index tables, and 24-hour diurnal fractional percentages. Continuous hourly time-series are completely absent. Furthermore, vehicular speed is not monitored by the census.
- **Why rejected**: Generating continuous hourly observations by multiplying annual AADT by static diurnal curves produces synthetic data, violating strict research integrity rules.
- **What should NOT be repeated**: **DO NOT ATTEMPT TO CONSTRUCT CONTINUOUS HOURLY TRAFFIC FROM THE ANNUAL TRAFFIC CENSUS (ATC)**.

---

## Negative Finding N02: `traffic_volume` is NOT a Channel in CTDI

- **What was tested**: Investigated how to integrate vehicular count / volume ($\text{veh/h}$) as Channel 13.
- **What was found**: Exhaustive search of Yu et al. (2025) proved `traffic_volume` is never mentioned in Table I or experimental feature sections. Table I specifies `Traffic congestion` (`ROAD_SATURATION_LEVEL`).
- **Why rejected**: Adding `traffic_volume` contradicts published benchmark ground truth.
- **What should NOT be repeated**: **DO NOT ADD `traffic_volume` AS A BENCHMARK CHANNEL**.

---

## Negative Finding N03: City Dashboard CSV Historical Archive Has an Unrecoverable 2019 Gap

- **What was tested**: Audited the DATA.GOV.HK historical archive for the City Dashboard traffic endpoint (`dashboard.data.gov.hk/api/traffic-speed?format=csv`).
- **What was found**: Historical snapshots on DATA.GOV.HK only began on December 24, 2019 at 08:34 HKT. Consequently, $8,577$ out of $8,760$ hours in 2019 ($97.9\%$) are completely missing from this archive. Furthermore, it exposes only 6 road links.
- **Why rejected**: A source missing 98% of its first year cannot support a 3-year continuous study period.
- **What should NOT be repeated**: **DO NOT ATTEMPT TO COMPILE 2019 HOURLY TRAFFIC TIME-SERIES FROM THE CITY DASHBOARD ENDPOINT**. Target the parent `speedmap.xml` system instead.

---

## Negative Finding N04: `rainfall` is NOT the CTDI Fourth Meteorological Channel

- **What was tested**: Evaluated maintaining `rainfall` ($\text{mm}$) as Channel 9.
- **What was found**: CTDI Table I explicitly specifies **`Visibility` ($\text{km}$)**. Rainfall is zero for $>90\%$ of hours in Hong Kong and does not reflect continuous aerosol loading.
- **Why rejected**: Fails source fidelity with the published paper.
- **What should NOT be repeated**: **DO NOT SUBSTITUTE `rainfall` FOR `visibility` WITHOUT EXPLICIT DIVERGENCE LABELING**.

---

## Negative Finding N05: Synthetic Traffic Data Injection is Strictly Prohibited

- **What was tested**: Evaluated filling traffic gaps using spline interpolation, KNN heuristics, or diurnal profiles.
- **What was found**: Injecting synthetic features into a benchmark dataset corrupts scientific comparison with published baselines and produces invalid evaluation metrics.
- **Why rejected**: Fundamental violation of scientific integrity.
- **What should NOT be repeated**: **NEVER INJECT SYNTHETIC OR INTERPOLATED SENSOR OBSERVATIONS INTO BENCHMARK CHANNELS**. If real data is missing, the pipeline must cleanly halt.
