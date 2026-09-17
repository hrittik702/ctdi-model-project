# Living Unresolved Questions

This document maintains active open questions, scientific dilemmas, and next investigative actions.

---

## Unresolved Questions Registry

### Q01: How to Efficiently Batch-Ingest 774,686 Historical `speedmap.xml` Snapshots?
- **Why It Matters**: Constructing the real 2019–2021 continuous hourly traffic speed and congestion series across 607 links requires downloading and parsing XML snapshots from the DATA.GOV.HK archive.
- **Current Evidence**: DATA.GOV.HK archive endpoint (`http://resource.data.one.gov.hk/td/speedmap.xml`, dataset ID `hk-td-sm_1-traffic-speed-map`) contains 774,686 snapshots covering 100% of 2019–2021.
- **Next Investigation**: Develop a Python script (`scripts/download_historical_speedmap.py`) that queries snapshots at 1-hour intervals (target: $26,304$ snapshots rather than all $774\text{k}$), parses `<TRAFFIC_SPEED>` and `<ROAD_SATURATION_LEVEL>` for all 607 links, and stores them in Parquet.
- **Status**: **`OPEN`**

---

### Q02: Acquisition of HKO 47-Station AWS Visibility Records vs. Interim Reanalysis
- **Why It Matters**: CTDI Table I explicitly cites the Hong Kong Observatory Open Database [81] across 47 Automatic Weather Stations and specifies `Visibility` ($\text{km}$). Our interim file uses Open-Meteo ERA5 reanalysis and contains `rainfall`.
- **Current Evidence**: Interim reanalysis table has 420,864 complete rows across all 16 station coordinates. HKO daily benchmark records are downloaded in `data/raw/meteorology/hko_daily_reference/`.
- **Next Investigation**: Query HKO CSDI portal for 2019–2021 hourly visibility records from AWS stations, or determine if ERA5 surface visibility can serve as an interim proxy with explicit divergence labeling.
- **Status**: **`OPEN`**

---

### Q03: Optimal Numerical Encoding for Categorical `traffic_congestion`
- **Why It Matters**: Diffusion models operate on continuous real-valued variables. `ROAD_SATURATION_LEVEL` in `speedmap.xml` takes three categorical values: `TRAFFIC GOOD`, `TRAFFIC AVERAGE`, `TRAFFIC BAD`.
- **Current Evidence**: CTDI Table I lists unit as `N/A`. Section III-A states IDW is applied to both traffic speed and congestion.
- **Next Investigation**: Compare ordinal scalar mapping (`0.0 = GOOD, 0.5 = AVERAGE, 1.0 = BAD`) against one-hot continuous embedding vectors in downstream diffusion stability.
- **Status**: **`OPEN`**

---

### Q04: Feasibility of 11-Channel Baseline (Pollutants + Weather) Development
- **Why It Matters**: The 11-channel subset (5 criteria pollutants + 6 meteorological features) is 100% validated across all 420,864 rows. Proceeding with 11-channel model development would allow prototyping the SLM context encoder and diffusion denoiser while traffic batch downloading runs asynchronously.
- **Current Evidence**: CTDI Section V-C evaluates sub-datasets (Dataset A vs Dataset AU).
- **Next Investigation**: Review whether 11-channel ablation provides a clean comparative baseline in literature.
- **Status**: **`OPEN`**
