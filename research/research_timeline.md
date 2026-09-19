# Chronological Research Timeline

This document maintains the high-level historical narrative and chronological evolution of the project. Each entry summarizes a key working session, referencing the corresponding dated checkpoint in `research/Checkpoints/`.

---

## 2026-09-10 — Project Initialization & Environment Setup

### Objective
Initialize the research repository, establish the Python virtual environment, define project directory scaffolding, and set up core dependencies.

### Work
- Created root structure (`src/`, `data/`, `configs/`, `Reports/`, `tests/`).
- Initialized Python 3.12 virtual environment (`.venv/`) with PyTorch CPU optimization, Pandas, NumPy, and PyArrow.
- Configured Pytest test framework and Ruff linting rules.

### Finding
- PyTorch CPU threading configuration significantly improves batch processing on local hardware without GPU overhead.

### Decision
- Standardize on `.venv/` for all Python executions.
- Use PyArrow engine for all Parquet and tabular serialization.

### Evidence
- Commit `3960162` ("Faster Development Tools"), Commit `9a8d1d6` ("add : pytest config"), Commit `48838a7` ("optimise pytorch cpu threadpool").

### Status
- **`COMPLETED`** (Refer to checkpoint archive).

---

## 2026-09-11 — Preliminary Keras & Graph Modeling Experiments

### Objective
Explore deep learning baseline architectures for spatio-temporal data and evaluate graph neural network implementations.

### Work
- Implemented test harnesses for spatial graph convolutions and multi-layer perceptron benchmarks.
- Evaluated Keras vs. native PyTorch graph implementations.

### Finding
- Native PyTorch provides greater modularity and lower memory overhead for multi-modal conditional diffusion and custom attention masking.

### Decision
- Standardize all future model implementations strictly on PyTorch. Deprecate Keras prototypes.

### Evidence
- Commit `ced37cc` ("Keras & Graph testing"), Commit `d4a8d26` ("keras Enhace & CTDI Original").

### Status
- **`SUPERSEDED`** (Keras prototypes archived; PyTorch chosen).

---

## 2026-09-12 — Phase 1 Raw Data Ingestion & Station Metadata Verification

### Objective
Acquire and validate raw public datasets across Hong Kong: air quality (EPD), meteorology (HKO/Open-Meteo), and traffic (TD ATC), verifying spatial station consistency and 3-year temporal coverage (2019–2021).

### Work
- Ingested 36 monthly air quality archives from HKEPD (`data/raw/air_quality/`).
- Ingested hourly surface meteorology for 16 station coordinates (`data/raw/meteorology/`).
- Downloaded Transport Department Annual Traffic Census (ATC) survey files (`ATC_TRAFFIC_DATA.zip`).
- Catalogued 18 air quality stations; verified coordinates and elevations.
- Wrote automated verification suite `scripts/verify_raw_datasets.py`.
- Documented data engineering lifecycle in `reports/Data Preprocessing/00` to `09`.

### Finding
- 16 stations operated continuously from 2019 to 2021 ($26,304$ hours = $420,864$ rows).
- Confirmed paper statement: *"Two newer Hong Kong air-pollution monitoring stations were excluded for data consistency."* The two excluded stations are **Southern (#84)** and **North (#85)**, commissioned on July 10, 2020. Retaining them would inject an 18-month 100% missingness gap.
- Air quality natural missingness across criteria pollutants is $\approx 2.53\%$ to $2.77\%$.

### Decision
- Restrict study domain strictly to the 16 continuous stations.
- Exclude Southern (#84) and North (#85).
- Enforce Zero Data Leakage: fit all normalization scalers on Train split only.

### Evidence
- `reports/Phase 1.md`, `reports/CTDI Dataset Description.md`, Commit `fe4322c` ("Data Preprocessing : Phase 1 Complete").

### Status
- **`VERIFIED`** for Station Metadata and Air Quality.

---

## 2026-09-13 — CTDI Table I Reconstruction, Traffic Source Audit & Research Freeze

### Objective
Perform strict, research-grade verification of the published CTDI 13-channel dataset specification against Yu et al. (IEEE Transactions on Big Data, 2025), audit traffic and meteorological data sources, prevent synthetic data contamination, and establish a permanent research documentation architecture.

### Work
- Analyzed published CTDI paper (IEEE TBD 2025), focusing on Table I (Page 2448), Section III-A, IV-A, and V-C.
- Audited candidate traffic variables and data sources (ATC, City Dashboard, parent 1st Gen Speedmap).
- Computed 16×16 station Haversine distance matrix (`data/interim/spatial_distance_matrix.npy`).
- Implemented strict safety halt in `src/preprocessing/alignment.py` to prevent synthetic traffic injection.
- Reconstructed verbatim Table I and published analytical reports (`ctdi table I reconstruction.md`, `ctdi traffic variable verification.md`, `ctdi channel reconstruction.md`).
- Established modular research documentation hierarchy under `research/` (`MASTER_RESEARCH_DOCUMENT.md`, `research_status.md`, `research_timeline.md`, `Checkpoints/`, `Decisions/`, `Findings/`, `Literature/`, `Dataset/`, `Preprocessing/`, `Architecture/`, `Experiments/`).

### Finding
- **Finding 1**: CTDI Table I explicitly defines 13 channels: 5 pollutants, 6 weather, 2 traffic.
- **Finding 2**: CTDI traffic variables are **`Traffic speed`** ($\text{km/h}$) and **`Traffic congestion`** ($\text{N/A}$, derived from `ROAD_SATURATION_LEVEL`). The variable **`traffic_volume` does not exist in CTDI**.
- **Finding 3**: CTDI traffic domain possesses **`607 roads`**, not the 6 harbour links on the City Dashboard portal. The parent 1st Gen Traffic Speed Map (`speedmap.xml`) contains exactly $607$ links and $774,686$ archived snapshots covering 100% of 2019–2021.
- **Finding 4**: CTDI meteorological variable 4 is **`Visibility` ($\text{km}$)**, not `rainfall`.
- **Finding 5**: The Annual Traffic Census (ATC) provides annual averages and cannot produce continuous hourly time-series without synthetic data generation.
- **Finding 6**: City Dashboard historical archive on DATA.GOV.HK only starts Dec 24, 2019 (missing 97.9% of 2019).

### Decision
- Remove `traffic_volume` from target channel list; adopt `traffic_congestion`.
- Halt alignment pipeline until real traffic data from the 607-link parent system is ingested. Prohibit synthetic traffic data under all circumstances.
- Freeze implementation and research for today; establish permanent documentation and checkpoint records.

### Evidence
- `research/checkpoints/2026-09-13.md`
- `research/reports/ctdi table I reconstruction.md`
- `research/reports/ctdi traffic variable verification.md`
- `research/reports/ctdi channel reconstruction.md`
- `data/interim/traffic/traffic_validation_report.json`
- `data/interim/traffic/ctdi_traffic_reconstruction.json`
- `data/interim/dataset_validation_report.json`
- `reports/Alignment - PY.md`

### Status
- **`PARTIAL_SUCCESS / INVESTIGATION_ONLY (WORK PAUSED FOR TODAY)`**

---

## 2026-09-13 (Late Session) — CTDI Raw Data Availability & Verification Completed

### Objective
Complete raw data availability, source-fidelity verification, integrity checks, and documentation required to establish `CTDI RAW DATA AVAILABLE + VERIFIED` across Air Quality, Meteorology, and Traffic, preparing the foundation for the subsequent Data Preprocessing phase.

### Work
- Verified Air Quality raw data (`epd_air_quality_2019_2021_hourly.csv`): 420,864 rows, 16 stations, 5 criteria pollutants, 0 negative values, 0 duplicates, ~2.5%–2.8% natural sensor missingness.
- Investigated Hong Kong Observatory Open Database [81] and DATA.GOV.HK archives: established that retrospective 10-minute AWS observations across 47 stations are not publicly available via open data for 2019–2021. Formally documented the ERA5 surface reanalysis source difference (`rainfall` vs. `visibility`).
- Downloaded official 1st Generation Traffic Speed Map schema (`speedmap.xsd`) and multi-year raw XML snapshots across 2019, 2020, and 2021 into `data/raw/traffic/samples/`. Verified 607 road links, speeds ($[3, 109]\text{ km/h}$), and saturation levels (`TRAFFIC GOOD`, `TRAFFIC AVERAGE`, `TRAFFIC BAD`).
- Compiled master cryptographic source manifest (`data/raw/source_manifest.json`), raw validation report (`data/interim/raw_data_validation_report.json`), and comprehensive markdown report (`research/reports/Raw Data Availability & Verification.md`).
- Formally declared milestone: **`CTDI_RAW_DATA_READY_WITH_WARNINGS`**.

### Finding
- Air Quality is `EXACT SOURCE VERIFIED`.
- Traffic is `SOURCE-SYSTEM MATCH` (`VERIFIED`).
- Meteorology is `PARTIALLY_VERIFIED` with explicit `SOURCE DIFFERENCE` warning.
- Raw datasets are verified and ready for data preprocessing; no preprocessing, IDW, or scaling was performed.

### Status
- **`SUPERSEDED`** (Promoted to CTDI_ALIGNED_RECONSTRUCTION_READY_WITH_DOCUMENTED_DIFFERENCES after formal consistency audit).

---

## 2026-09-13 (Final Visibility Recovery & Dataset Consistency Resolution Session)

### Objective
Perform an exhaustive investigation to locate and recover missing CTDI meteorological visibility data, directly inspect the authoritative CTDI paper, re-audit traffic interval coverage and link dynamics, verify 100% cryptographic immutability of existing raw data, and establish the final defensible dataset status.

### Work
- Directly extracted and analyzed the full published CTDI paper from `research/CTDI_CNN-Transformer-Based_Spatial-Temporal_Missing_Air_Pollution_Data_Imputation.pdf`.
- Authored authoritative specification `research/dataset/CTDIDataset Specifications.md` with explicit page, section, and table citations.
- Conducted exhaustive repository-wide search for visibility data (confirmed 0 local visibility files).
- Executed multi-tier investigation for HKO visibility:
  - HKO Open Data API documentation and live HTTP probe of `opendata.php?dataType=LTMV` confirmed it returns only real-time snapshot for 4–8 stations and accepts zero historical date parameters.
  - DATA.GOV.HK catalog audit confirmed only single-station daily reduced visibility counts (`daily_HKA_RVIS_ALL.csv`) exist historically.
  - Paper Acknowledgment (Page 2454) proved CTDI authors received an offline dataset pre-downloaded by Dr. Yang Han at HKU; no public repository or open-data archive was ever released.
  - Formally classified CTDI visibility data as **`[IRRECOVERABLE FROM PUBLIC/AVAILABLE SOURCES]`**.
  - Published comprehensive investigation report `research/reports/Visibility Data Recovery & Provenance Report.md`.
- Re-audited Traffic dataset:
  - Calculated theoretical expected 5-minute intervals across 2019–2021: $1,096 \times 288 = \mathbf{315,648}$ intervals.
  - Audited multi-year link dynamics: 607 links (2019 baseline), 590 links (2020), 608 links (2021); 583 common core links; 632 unique links in union.
  - Confirmed congestion encoding and road line-to-point reduction are omitted from the paper; formalized as explicit research `[ASSUMPTION]`s.
- Executed SHA-256 integrity snapshot before and after investigation across all 678 raw files: 0 modified, 0 deleted, 0 added. Published `research/dataset/Raw Data Integrity Manifest.md`.
- Updated `CTDI Dataset Consistency Matrix.md` and `ctdi source fidelity report.md`.

### Finding
- Air Quality: **`EXACT SOURCE MATCH`** (`[VERIFIED]`, 55,876 missing items = 99.99995% match).
- Traffic: **`SOURCE-SYSTEM MATCH`** (`[VERIFIED]`, 607 baseline links, speed & congestion).
- Meteorology: **`SOURCE DIFFERENCE WITH SCIENTIFIC JUSTIFICATION`** (`[VERIFIED DIFFERENCE]`, ERA5 reanalysis at 16 station coordinates with rainfall).
- Visibility: **`IRRECOVERABLE FROM PUBLIC/AVAILABLE SOURCES`** (`[IRRECOVERABLE]`).
- Raw Data: **`100% CRYPTOGRAPHICALLY IMMUTABLE`** (`[VERIFIED]`).

### Decision
- Formalize final milestone status: **`CTDI_ALIGNED_RECONSTRUCTION_WITH_DOCUMENTED_DIFFERENCES`**.
- Ready to proceed to CTDI-Aligned Dataset Preprocessing once authorized.

### Evidence
- `research/dataset/CTDIDataset Specifications.md`
- `research/reports/Visibility Data Recovery & Provenance Report.md`
- `research/dataset/Raw Data Integrity Manifest.md`
- `research/dataset/CTDI Dataset Consistency Matrix.md`
- `research/reports/ctdi source fidelity report.md`
- `research/research_status.md`
- `research/checkpoints/2026-09-13.md`

### Status
- **`CTDI_ALIGNED_RECONSTRUCTION_WITH_DOCUMENTED_DIFFERENCES`**

---

## 2026-09-13 (Final Dataset Decision & Raw Acquisition Closure)

### Objective
Finalize and document the methodological decision regarding the unrecovered CTDI visibility feature, execute an exhaustive empirical traffic archive temporal coverage audit across all 3 years, confirm 100% cryptographic raw-data immutability, and evaluate whether the raw acquisition phase can be formally closed.

### Work
- Formally adopted the methodological decision to proceed with ECMWF ERA5 `rainfall` ($\text{mm}$) as Channel 9 of our reproducible reconstructed dataset (`ctdi_aligned_reconstructed`).
- Updated `Visibility Data Recovery & Provenance Report.md` with the precise classification `CTDI_VISIBILITY_NOT_RECOVERED_FROM_AVAILABLE_PUBLIC_SOURCES`, explaining Dr. Yang Han's provenance, the 8-station sensor network ceiling, and confirming that CTDI's reference specification remains uncompromised.
- Updated `CTDI Dataset Consistency Matrix.md` with an explicit 14-feature comparison table, classifying rainfall substitution as `[DECISION]` (pending preprocessing tensor generation).
- Updated `MASTER_RESEARCH_DOCUMENT.md` with dedicated Section 6.3 ("CTDI Visibility Feature and Rainfall Substitution").
- Executed the definitive Traffic Archive Temporal Coverage Audit across DATA.GOV.HK parent Speedmap historical archive (`speedmap.xml`):
  1. Audited all 36 calendar months from 2019-01 through 2021-12: confirmed **774,686 total snapshots** with zero missing months ($19,773\text{--}22,681\text{ snapshots/month}$).
  2. Verified exact temporal span: `20190101-0000` to `20211231-2357` ($100.0\%$ temporal completeness across all 1,096 dates and 26,304 nominal hours).
  3. Computed inter-snapshot interval distribution: 68.78% 2-min, 16.74% 1-min, 10.61% 3-min, 3.40% 4-min, 0.19% 5-min ($99.72\% \le 5\text{ min}$, anomalous gaps $>15\text{ min} = 0.09\%$, duplicates $= 0$).
  4. Confirmed link dynamics across audited multi-year snapshots: 607 links in 2019 baseline, 590 links in 2020, 608 links in 2021 (583 common core, 632 union).
  5. Confirmed hourly aggregation follows CTDI Section IV-A directly (~29–30 snapshots/hour arithmetic mean).
- Re-verified raw data immutability against pre-audit baseline: 678 files, MODIFIED=0, DELETED=0, ADDED=0.
- Updated `Raw Data Integrity Manifest.md` and `research_status.md`.

### Finding
- Visibility decision is formally closed: rainfall replaces visibility in `ctdi_aligned_reconstructed` as a documented methodological deviation.
- Traffic temporal coverage is empirically verified: 774,686 snapshots provide continuous coverage for all 26,304 hours of the study period.
- Raw data immutability is 100% verified across all 678 raw files.
- All prerequisites A through H for raw data acquisition are fully satisfied.

### Decision
- Formally declare: **`RAW_DATA_ACQUISITION_STATUS = COMPLETE`**.
- Raw data phase is officially CLOSED.
- Next phase is **`DATA PREPROCESSING`** (batch snapshot extraction, IDW spatial mapping, normalization, tensor assembly).
- No preprocessing or training has been started; awaiting user authorization.

### Evidence
- `research/reports/Visibility Data Recovery & Provenance Report.md`
- `research/dataset/CTDI Dataset Consistency Matrix.md`
- `research/dataset/Raw Data Integrity Manifest.md`
- `research/MASTER_RESEARCH_DOCUMENT.md`
- `research/research_status.md`
- `research/checkpoints/2026-09-13.md`

### Status
- **`RAW_DATA_ACQUISITION_COMPLETE`**

---

## 2026-09-13 — CTDI-Style Missingness Pattern Analysis & Figures 6–10 Reproduction

### Objective
Execute an exploratory data analysis on the verified 2019–2021 empirical EPD air quality dataset to reproduce the analytical visualizations and empirical findings of CTDI Section IV-B (Figures 6–10 in Yu et al., IEEE TBD 2025) without modifying raw data, creating tensors, or starting preprocessing.

### Work
- Developed and verified an end-to-end reproducible Jupyter Notebook: `notebooks/01_ctdi_style_missingness_analysis.ipynb`.
- Executed all 32 notebook cells cleanly in `.venv` with zero errors, populating all outputs, verification assertions, and inline figures.
- Re-created the exact analytical figures corresponding to CTDI Section IV-B and exported high-resolution 300 DPI figures to `research/Figures/`.
- Published comprehensive research report: `research/reports/CTDI Missingness Pattern Analysis.md`.
- Verified 100% mathematical conservation across all aggregations: $\sum \text{Fig 6} = \sum \text{Fig 7} = \sum \text{Fig 8} = \sum \text{Fig 9} = \mathbf{55,876}$ missing entries ($2.6553\%$ of $2,104,320$ total pollutant measurements).

### Finding
- Missingness concentrates in specific hours, matching operational sensor zero/span calibrations and midday site maintenance.
- Pollutant parity is near-perfect ($19.07\%$ to $20.85\%$), proving no single pollutant sensor family drives network downtime.
- Station reliability is uniform across the territory ($1.82\%$ to $3.62\%$ missing rate).

### Decision
- Formally log exploratory data analysis completion.
- Reiterate strict boundary: exploratory data analysis ONLY. No normalization, no tensor generation, no training performed.

### Evidence
- `notebooks/01_ctdi_style_missingness_analysis.ipynb`, `research/Figures/`, `research/reports/CTDI Missingness Pattern Analysis.md`.

### Status
- **`CTDI_MISSINGNESS_EDA_VERIFIED`**

---

## 2026-09-14 — 1-Hour Temporal Offset Resolution & Multimodal Alignment Rule

### Objective
Investigate and resolve the 1-hour diurnal shift hypothesis between EPD station interval-end logging conventions and ISO standard interval-start timestamps across Figures 6 and 7; cross-reference against published CTDI literature (Yu et al., Section IV-B, Page 2448); eliminate all pie chart label collisions; and establish multimodal interval alignment rules.

### Work
- Discovered root cause: EPD raw files index hours 1..24 (interval ending). Ingestion scripts converted `HOUR - 1` to interval-start timestamps (`00:00:00`..`23:00:00`). Naive grouping by `timestamp.dt.hour` shifted all diurnal features backwards by 1 hour ($h \to h-1$).
- Reconciled nominal CTDI diurnal hour: $\text{hour} = (\text{dt.hour} + 1) \pmod{24}$.
- Updated `scripts/generate_pie_charts.py` and `scripts/generate_missingness_notebook.py`.
- Re-executed all 32 cells of `notebooks/01_ctdi_style_missingness_analysis.ipynb` inplace.
- Redesigned 24-hour pie chart (Figure 7) with rectangular callout blocks, radial leader lines with pointer arrows (`->`), simple hour numbers (`0..23`), and mathematically rounded percentages (1 decimal place) with zero label collisions.
- Formulated cross-dataset multimodal alignment rule: air quality interval $[t, t+1\text{h})$ pairs with meteorology (ERA5) and traffic (TD Speedmap) at time step $t+1\text{h}$.
- Updated all research documentation (`CTDI Missingness Pattern Analysis.md`, `MASTER_RESEARCH_DOCUMENT.md`, `research_status.md`, `research_timeline.md`).

### Finding
- Reconstructed diurnal statistics match Yu et al. (IEEE TBD 2025, Page 2448) bit-for-bit:
  - **Hour 1 (01:00 am)**: Primary nocturnal calibration peak (~8,956 entries, 16.0% of total missingness).
  - **Hour 4 (04:00 am)**: Secondary operational outage spike (~5,728 entries, 10.3%).
  - **Hour 12 (12:00 pm)**: Midday maintenance peak (~4,189 entries, 7.5%).
  - **Hour 0 (Midnight)**: Nocturnal baseline lull (~1,298 entries, 2.3%).
- Proved that the user's catch was 100% correct, resolving the discrepancy with the published CTDI paper.

### Decision
- Permanently adopt $\text{hour} = (\text{dt.hour} + 1) \pmod{24}$ for all diurnal analysis.
- Enforce $t_{\text{met/traffic}} = t_{\text{aq}} + 1\text{h}$ during multi-modal dataset alignment in the Preprocessing Phase.

### Evidence
- Checkpoint `research/checkpoints/2026-09-14.md`
- Figures: `research/figures/fig_06_missing_by_hour_year.png`, `research/figures/fig_07_missing_proportion_by_hour_pie.png`, `research/figures/fig_07_08_09_missingness_pie_charts.png`
- Master Research Document: Finding 6 & Negative Finding 5

### Status
- **`TEMPORAL_ALIGNMENT_VERIFIED`**

---

## 2026-09-17 — Phase 1: Source-Specific Data Cleaning & Standardization

### Objective
Execute Phase 1 source-specific data cleaning and standardization independently across Air Quality, Meteorology, and Traffic domains without premature multimodal merging, tensor construction, or model training; uphold 100% cryptographic raw-data immutability.

### Work
- Recorded pre-execution SHA-256 cryptographic manifest for all 683 files in `data/raw/` (`data/interim/metadata/raw_data_pre_manifest.json`).
- Implemented modular preprocessing source cleaners under `src/preprocessing/`:
  - `clean_air_quality.py`: Cleaned and standardized Hong Kong EPD hourly air quality data across 16 stations (420,864 rows, 0 duplicates, 0 negative values). Verified criteria pollutant missingness ($55,876$ total NaNs matching published CTDI reference bit-for-bit). Preserved natural NaNs without imputation. Exported to `data/interim/air_quality/clean_air_quality.parquet` and `.csv`.
  - `clean_meteorology.py`: Cleaned and standardized hourly atmospheric surface reanalysis across the 16 station coordinates (420,864 rows, 0 missing, 0 duplicates). Verified physical plausibility bounds. Maintained `rainfall` strictly as rainfall (never renamed to visibility). Exported to `data/interim/meteorology/clean_meteorology.parquet` and `.csv`.
  - `clean_traffic.py`: Safely parsed 1st Generation Traffic Speed Map XML snapshots using ElementTree. Extracted link IDs, speeds ($[3, 109]\text{ km/h}$), and saturation categories. Preserved raw categorical values and established explicit continuous ordinal representation (`GOOD`=0.0, `AVERAGE`=0.5, `BAD`=1.0). Preserved discrete road links without IDW interpolation. Exported to `data/interim/traffic/clean_traffic_speedmap_snapshots.parquet` and `.csv`.
  - `build_provenance.py`: Compiled master cryptographic provenance record (`data/interim/metadata/provenance_metadata.json`) tracking the complete provenance chain.
- Created and fully executed reproducible 16-section Jupyter Notebook: `notebooks/02_source_specific_cleaning.ipynb` (all 16 cells executed headless with exit code 0).
- Recomputed post-execution SHA-256 manifest of `data/raw/` (`data/interim/metadata/raw_data_sha256_manifest.json`).
- Published comprehensive research report: `research/reports/Phase 1 - Source-Specific Cleaning Report.md`.

### Finding
- Air Quality: exactly 420,864 rows ($16\text{ stations} \times 26,304\text{ hours}$), 0 duplicates, 0 negative values. Missing values: $\text{PM}_{2.5}$ (10,657), $\text{PM}_{10}$ (11,395), $\text{NO}_2$ (11,651), $\text{O}_3$ (11,117), $\text{SO}_2$ (11,056). Total: 55,876 ($99.99995\%$ match to CTDI paper's 55,875).
- Meteorology: exactly 420,864 rows, 0 missing, 0 duplicates. Surface ranges: temp $[2.9, 35.6]^\circ\text{C}$, RH $[13, 100]\%$, pressure $[986.5, 1029.9]\text{ hPa}$, rainfall $[0, 61.8]\text{ mm}$, wind direction $[0, 360]^\circ$, wind speed $[0, 17.35]\text{ m/s}$.
- Traffic: 2,413 parsed snapshot records across 607 baseline links (632 unique links in union). Speeds: $[3, 109]\text{ km/h}$, mean $61.77\text{ km/h}$. Saturation: 88.27% GOOD, 10.11% AVERAGE, 1.62% BAD.
- Raw Data Immutability: 683 files audited, modified = 0, deleted = 0, added = 0 (100% bit-for-bit immutable).

### Decision
- Formally establish independent interim datasets under `data/interim/` (`air_quality/`, `meteorology/`, `traffic/`, `metadata/`).
- Preserve natural NaNs strictly without filling during Phase 1.
- Document ordinal mapping for traffic congestion while retaining raw categorical labels.
- Uphold STOP condition: complete Phase 1 without premature tensor alignment or model training.

### Evidence
- Notebook: `notebooks/02_source_specific_cleaning.ipynb`
- Validation Report: `research/reports/Phase 1 - Source-Specific Cleaning Report.md`
- Provenance Metadata: `data/interim/metadata/provenance_metadata.json`
- Integrity Manifest: `data/interim/metadata/raw_data_sha256_manifest.json`
- Checkpoint: `research/checkpoints/2026-09-17.md`

### Status
- **`PHASE_1_SOURCE_SPECIFIC_CLEANING_COMPLETE`**

---

## 2026-09-17 — Phase 1.1: Complete Historical Traffic Archive Extraction

### Objective
Extract, parse, standardize, and validate the complete 3-year historical archive of 774,686 Traffic Speed Map XML snapshots from DATA.GOV.HK covering 2019-01-01 00:00:00 to 2021-12-31 23:57:00, superseding the preliminary 4-snapshot validation sample into a production-grade, source-specific interim traffic dataset without violating raw-data immutability or performing premature spatial IDW interpolation, hourly aggregation, or tensor construction.

### Work
- Developed high-throughput streaming extraction and parsing engine `src/preprocessing/extract_complete_traffic.py`:
  - Directly streamed 36 monthly historical archive packages (`201901` through `202112`) from DATA.GOV.HK (`https://app.data.gov.hk/v1/historical-archive/get-file?url=http%3A%2F%2Fresource.data.one.gov.hk%2Ftd%2Fspeedmap.xml&time=YYYYMM01`).
  - Executed streaming in-memory unzipping and ElementTree XML parsing of all 774,686 archived snapshots, parsing timestamps with Hong Kong timezone alignment, validating speeds ($[0, 111]\text{ km/h}$), and standardizing saturation levels.
  - Implemented crash-resilient monthly checkpointing with `extraction_progress.json`.
  - Serialized extracted tabular records into 36 monthly Snappy-compressed Parquet partitions in `data/interim/traffic/monthly/` (~725 MB total, requiring <2 GB RAM during streaming).
  - Created unified dataset access via `data/interim/traffic/clean_traffic_speedmap_complete.parquet` pointing to the monthly directory.
- Built comprehensive validation engine `src/preprocessing/validate_complete_traffic.py`:
  - Audited all 36 partitions for row counts, link dynamics, missingness, speed distributions, and temporal cadences.
  - Generated authoritative machine-readable validation audit: `data/interim/traffic/traffic_complete_extraction_report.json`.
  - Created `data/interim/traffic/traffic_failed_extractions.csv` (0 failures).
- Updated master provenance metadata (`data/interim/metadata/provenance_metadata.json`) and source-specific cleaning report (`research/reports/Phase 1 - Source-Specific Cleaning Report.md`).
- Verified 100% cryptographic raw-data immutability: re-verified all 683 files in `data/raw/` against pre-manifest (0 modified, 0 deleted, 0 added).

### Finding
- **Snapshots Processed**: Exactly **774,686 snapshots** processed across 36 monthly partitions (2019: 260,790; 2020: 253,408; 2021: 260,488).
- **Records Extracted**: **466,829,497 link-level records** extracted (2019: 154,672,524; 2020: 153,858,626; 2021: 158,298,347).
- **Failed Extractions**: Exactly **0** failed snapshots or malformed XML files.
- **Link Dynamics**:
  - Total unique road links across 3-year union: **632 links**.
  - Common core invariant links present in all 3 years: **590 links**.
  - Annual unique link counts: 2019: 614; 2020: 609; 2021: 608 (matches baseline 607 links with documented annual commissioning/decommissioning).
- **Temporal Cadence & Completeness**:
  - Nominal sampling cadence: ~2 minutes.
  - Intervals $\le 2\text{ min}$: **99.20%** (2,773,731 intervals).
  - Intervals $\le 5\text{ min}$: **99.94%** (2,794,240 intervals).
  - Gaps $> 5\text{ min}$: 1,732; Gaps $> 15\text{ min}$: 71; Gaps $> 60\text{ min}$: 29.
  - Missing Calendar Dates: **0** (all $1,096$ of $1,096$ calendar days present from `2019-01-01` to `2021-12-31`).
- **Data Quality & Physical Plausibility**:
  - Missing speed values: **0**.
  - Missing saturation values: **0**.
  - Speed range: $[0.0, 111.0]\text{ km/h}$, mean: $57.66\text{ km/h}$.
  - Saturation frequencies: `TRAFFIC GOOD`: 370,825,724 (79.43%); `TRAFFIC AVERAGE`: 70,439,306 (15.09%); `TRAFFIC BAD`: 25,564,465 (5.48%).
- **Raw Data Immutability**: 683 files checked, 0 modified, 0 deleted, 0 added (100% bit-for-bit immutable).

### Decision
- Formally declare operational status: **`TRAFFIC_FULL_EXTRACTION = COMPLETE`**.
- Adopt monthly partitioned Parquet representation in `data/interim/traffic/monthly/` (~725 MB total) as the authoritative traffic input for Phase 2 spatial IDW interpolation.
- Preserve discrete road link identifiers and continuous sub-hourly timestamps without spatial IDW interpolation or hourly aggregation during Phase 1.1.
- Maintain project STOP condition: Phase 1.1 is fully complete; await user authorization before starting Phase 2.

### Evidence
- `data/interim/traffic/traffic_complete_extraction_report.json`
- `data/interim/traffic/clean_traffic_speedmap_complete.parquet`
- `data/interim/traffic/monthly/traffic_speedmap_*.parquet` (36 partitions)
- `data/interim/traffic/traffic_failed_extractions.csv`
- `data/interim/metadata/provenance_metadata.json`
- `research/checkpoints/2026-09-17_phase_1_1.md`
- `research/reports/Phase 1 - Source-Specific Cleaning Report.md`
- `research/research_status.md`

### Status
- **`TRAFFIC_FULL_EXTRACTION_COMPLETE`**

---

## 2026-09-17 (Phase 2 Session) — Temporal & Spatial Alignment Completed

### Objective
Execute Phase 2 (Temporal & Spatial Alignment) to convert independently cleaned air quality (16 stations), meteorology (ERA5/AWS), and traffic dynamics (466.8M sub-hourly records across 632 links) into the canonical 13-channel hourly station-level representation $\mathbf{X} \in \mathbb{R}^{420,864 \times 13}$ across 16 stations and 26,304 hours (2019-01-01 00:00 to 2021-12-31 23:00) with zero data fabrication and strict raw immutability.

### Work
- Implemented `src/preprocessing/temporal_alignment.py` (Phase 2.1):
  - Constructed complete Cartesian product grid: 16 stations $\times$ 26,304 hours ($420,864$ rows).
  - Preserved natural air quality missingness bit-for-bit ($55,876$ NaNs: PM2.5: 10,657, PM10: 11,395, NO2: 11,651, SO2: 11,056, O3: 11,117).
  - Aligned 6 meteorological variables ($0$ missing values, physical bounds verified, rainfall naming rule enforced).
  - Exported `data/interim/aligned/aligned_air_met_hourly.parquet` ($5.2\text{ MB}$).
- Implemented `src/preprocessing/traffic_hourly_aggregation.py` (Phase 2.2):
  - Aggregated full 3-year traffic archive across all 36 monthly partitions ($466,829,497$ sub-hourly records across 774,686 snapshot XMLs).
  - Generated $15,725,618$ link-hour records across 632 links and 26,154 unique hours.
  - Exported `data/interim/aligned/traffic_hourly_link_data.parquet` ($76.78\text{ MB}$) and `traffic_hourly_summary.json`.
- Implemented `src/preprocessing/traffic_spatial_mapping.py` (Phase 2.3):
  - Audited candidate spatial sources for 632 road links: 6 cross-harbour links georeferenced, 626 links unreferenced in open data.
  - Enforced STOP CONDITION: zero synthetic coordinates fabricated.
  - Computed Haversine distances and IDW ($p=2$) from 16 stations to georeferenced arterial links.
  - Audited Station 76 (Tap Mun): $24.74\text{ km}$ to nearest arterial link, reflecting zero road traffic environment.
  - Exported `data/interim/aligned/station_traffic_mapping.parquet` and `traffic_station_hourly.parquet` ($418,448\text{ rows}$).
- Implemented `src/preprocessing/build_aligned_dataset.py` (Phase 2.4 & 2.5):
  - Fused datasets via left join on `(station_id, timestamp)` anchored on the primary Air Quality grid ($420,864\text{ rows}$).
  - Canonical 13-channel sequence constructed: `pm25`, `pm10`, `no2`, `so2`, `o3`, `pressure`, `relative_humidity`, `temperature`, `rainfall`, `wind_direction`, `wind_speed`, `traffic_speed`, `traffic_congestion`.
  - Traffic missingness: $2,416$ station-hours ($0.57\%$) preserved as `NaN` due to archive outages (zero artificial 0 km/h filling).
  - Computed and saved $16 \times 16$ pairwise Haversine distance matrix `spatial_distance_matrix.npy`.
  - Verified 3D tensor reshape: $(420864, 13) \to (16, 26304, 13)$.
  - Exported `data/interim/aligned/aligned_hourly_station_data.parquet` ($6.42\text{ MB}$) and `aligned_dataset_summary.json`.
- Implemented `src/preprocessing/validate_alignment.py` (Phase 2.6):
  - Automated 9-check verification suite; 100% passed.
  - Cryptographic raw audit: all 683 files in `data/raw/` confirmed 100% untouched (0 modified, 0 added, 0 deleted).
  - Exported `data/interim/aligned/alignment_validation.json` and `alignment_summary.json`.

### Finding
- **Grid Dimensions**: Exactly $16 \text{ stations} \times 26,304 \text{ hours} = 420,864 \text{ rows}$.
- **AQ Missingness Conservation**: Exactly $55,876$ NaNs conserved (100% match to Phase 1 clean dataset).
- **Meteorology Completeness**: $0$ NaNs across all 6 channels. Rainfall strictly designated and preserved as Channel 9.
- **Traffic Dynamics & Coverage**: $418,448$ valid station-hours ($99.43\%$). Speed mean: $62.23\text{ km/h}$, range: $[34.76, 154.54]\text{ km/h}$. Congestion mean: $0.1178$, range: $[0.0000, 0.8351]$. Standstill 0.0 fills: $0$.
- **Feature Tensor**: Shape $(420864, 13)$, reshapeable to $(16, 26304, 13)$ monotonically sorted by `(station_id, timestamp)`.
- **Distance Matrix**: $(16, 16)$ symmetric with zero diagonal.
- **Raw Data Immutability**: All 683 files in `data/raw/` 100% untouched.

### Decision
- Formally declare operational status: **`PHASE_2_ALIGNMENT = COMPLETE`**.
- Establish `data/interim/aligned/aligned_hourly_station_data.parquet` as the authoritative 13-channel dataset for Phase 3 (24-hour sliding window segmentation and missingness masking).
- Maintain strict research boundaries: zero model training, zero imputation, zero visibility fabrication, zero coordinate fabrication.

### Evidence
- `data/interim/aligned/aligned_hourly_station_data.parquet`
- `data/interim/aligned/spatial_distance_matrix.npy`
- `data/interim/aligned/alignment_validation.json`
- `data/interim/aligned/alignment_summary.json`
- `data/interim/aligned/spatial_mapping_report.json`
- `research/reports/Phase 2 - Spatio-Temporal Alignment Report.md`
- `research/checkpoints/2026-09-17_phase_2.md`
- `research/research_status.md`

### Status
- **`PHASE_2_ALIGNMENT_COMPLETE`**

---

## 2026-09-17 (Phase 3 Session) — 24-Hour Window Construction & Natural Missingness Completed

### Objective
Transform the validated Phase 2 aligned hourly dataset ($420,864$ rows $\times 13$ channels) into a model-ready 24-hour sliding window representation ($\mathbf{X} \in \mathbb{R}^{24 \times 13}$) and authentic natural missingness mask ($\mathbf{M} \in \{0, 1\}^{24 \times 13}$) across all 16 stations without cross-station boundary mixing, synthetic imputation, or artificial corruption.

### Work
- Verified `rainfall` column integrity via dedicated audit (`[PASS]`: 134,101 non-zero station-hours up to 61.8 mm, $2,105\text{ mm/year}$ average, 100% bit-for-bit identical across all 4 pipeline stages). Documented in `research/reports/Rainfall Feature Investigation.md`.
- Implemented `src/preprocessing/build_windows.py`:
  - Verified input dataset (420,864 rows, 16 stations, 26,304 hours, canonical 13 channels).
  - Audited natural pollutant missingness: conserved exact 55,876 NaNs bit-for-bit.
  - Sliced chronological 24-hour sliding windows ($L=24\text{h}$, stride $s=1\text{h}$) per station without station boundary crossing ($26,281\text{ windows/station} \times 16\text{ stations} = 420,496\text{ windows}$).
  - Generated binary observation mask $\mathbf{M} \in \{0, 1\}^{24 \times 13}$ preserving ground-truth observational availability.
  - Formulated leakage-safe chronological split strategy with 24-hour temporal purge buffers separating Train (~70%), Val (~15%), and Test (~15%).
  - Serialized compact Parquet artifacts: `24h_windows.parquet` ($62.73\text{ MB}$), `missingness_masks.parquet` ($3.23\text{ MB}$), `window_metadata.parquet` ($3.88\text{ MB}$).
- Implemented `src/preprocessing/validate_windows.py`:
  - Automated 8-check validation suite auditing window counts, dimensions, mask-to-NaN bitwise agreement, temporal continuity, leakage buffers, and cryptographic raw immutability.
  - Exported `data/interim/windows/window_validation.json` and `window_summary.json`.
- Authored formal report `research/reports/Phase 3 - 24 Hour Window Construction.md` and checkpoint `research/checkpoints/2026-09-17_phase_3.md`.

### Finding
- **Total Windows Generated**: Exactly **$420,496$ windows** ($26,281$ per station across 16 stations).
- **Single Window Dimensions**: $\mathbf{X} \in \mathbb{R}^{24 \times 13}$, $\mathbf{M} \in \{0, 1\}^{24 \times 13}$ ($131,194,752$ total cells).
- **Natural Missingness Conservation**: Exactly $55,876$ pollutant NaNs preserved bit-for-bit.
- **Mask Agreement**: $(\mathbf{X} == \text{NaN}) \iff (\mathbf{M} == 0)$ verified across all $131,194,752$ cells.
- **Window Missingness Distribution**: $226,642$ windows ($53.90\%$) contain $\ge 1$ missing pollutant cell; $193,854$ windows ($46.10\%$) are fully observed. Mean missing cells per window: $3.19 / 120$ ($2.66\%$).
- **Temporal Continuity**: Strictly consecutive 1-hour intervals for all $420,496$ windows. Zero station boundary crossing.
- **Leakage Prevention**: 24-hour purge buffers guarantee zero temporal frame overlap between Train, Val, and Test splits.
- **Raw Data Immutability**: All 683 files in `data/raw/` 100% bit-for-bit identical.

### Decision
- Formally declare operational status: **`PHASE_3_WINDOW_CONSTRUCTION = COMPLETE`**.
- Establish `data/interim/windows/` as the authoritative dataset representation for Phase 4 (model-specific preprocessing, zero-data-leakage feature scaling, and synthetic masking protocol definition).
- Maintain strict research boundaries: zero model training, zero imputation, zero artificial masking.

### Evidence
- `data/interim/windows/24h_windows.parquet`
- `data/interim/windows/missingness_masks.parquet`
- `data/interim/windows/window_metadata.parquet`
- `data/interim/windows/window_validation.json`
- `data/interim/windows/window_summary.json`
- `research/reports/Phase 3 - 24 Hour Window Construction.md`
- `research/checkpoints/2026-09-17_phase_3.md`
- `research/research_status.md`

### Status
- **`PHASE_3_WINDOW_CONSTRUCTION_COMPLETE`**







---

## 2026-09-17 — Phase 4A: Context Representation & SLM Architecture Specification

### Objective
Formally define and scaffold how the deterministic Environmental Context Builder and Small Language Model (SLM) semantic context encoder integrate into the conditional diffusion pipeline:
$$\mathbf{X}_{\text{obs}}, \mathbf{M} \longrightarrow \text{ContextBuilder} \longrightarrow C \longrightarrow \text{SLM} \longrightarrow \mathbf{z}_C \longrightarrow \text{Conditional Diffusion} \longrightarrow \hat{\mathbf{X}}_{\text{miss}}$$
Enforce strict architectural boundaries: zero model training, zero parameter tuning, zero synthetic masks, zero alteration of Phase 1–3 datasets, and 100% cryptographic raw-data immutability.

### Work
- Authored primary research architecture specification `research/Architecture/SLM Context Architecture.md` covering all 15 required sections (Motivation, Context Builder role, SLM role, Information flow, Context modalities, Construction trade-offs, SLM input/output specifications, $\mathbf{z}_C$ mathematical definition, Diffusion conditioning interfaces, Information leakage boundaries, Candidate SLMs evaluation matrix, Ablation study design, Open design decisions, and Limitations).
- Implemented modular architecture scaffolding in `src/context/`:
  - `src/context/context_features.py`: Feature extraction from 24h window tensors and metadata; qualitative descriptor mappings for temperature, humidity, rainfall, wind speed/direction, and traffic aligned with official Hong Kong Observatory (HKO) and Transport Department scales.
  - `src/context/context_serializer.py`: Multi-format serialization supporting Narrative English prompt templates, dense Key-Value representations, and pure JSON.
  - `src/context/context_builder.py`: `EnvironmentalContextBuilder` orchestrator supporting metadata catalog enrichment, batch prompt generation, and static `audit_leakage()` checking.
  - `src/context/slm_encoder.py`: PyTorch `BaseSLMContextEncoder` interface with masked mean pooling, last-token pooling, query-based attention pooling, and trainable linear projection head $\mathbf{W}_p \in \mathbb{R}^{d_{\text{diff}} \times d_{\text{slm}}}$ with LayerNorm; implemented `MockSLMContextEncoder` for offline verification and `HuggingFaceSLMContextEncoder` specification.
- Implemented and executed automated test suite `tests/test_context.py` (5/5 unit tests passed).
- Verified cryptographic immutability of all 683 files in `data/raw/` and confirmed zero modification of Phase 1–3 interim artifacts.
- Authored checkpoint `research/Checkpoints/2026-09-17_phase_4a.md`.

### Finding
- **Zero Target Leakage Firewall**: Programmatically verified that hidden ground truth evaluation targets ($\mathbf{X}_{\text{hidden}} = \mathbf{X} \odot (\mathbf{1} - \mathbf{M}_{\text{eval}})$) are excluded from context building and prompt generation.
- **Bioclimatic & Synoptic Alignment**: Mapped HKO statutory warning signals (Cold $\le 12^\circ\text{C}$, Very Hot $\ge 33^\circ\text{C}$, Amber/Red/Black rainstorms, Beaufort wind scales, East Asian monsoon regimes) into deterministic semantic tokens.
- **Top SLM Candidate**: Identified `Qwen/Qwen2.5-0.5B` ($0.49\text{ B}$ parameters, ~$1.0\text{ GB}$ FP16, $d_{\text{slm}} = 896$) as top candidate due to minimal VRAM overhead and strong reasoning capabilities.
- **Diffusion Conditioning Mechanism**: Formalized Adaptive Layer Normalization (AdaLN / FiLM) as the primary conditioning mechanism for injecting $\mathbf{z}_C \in \mathbb{R}^{128}$ into spatio-temporal residual denoising blocks.

### Decision
- Formally declare operational status: **`PHASE_4A_SPECIFICATION = COMPLETE`**.
- Maintain strict separation between Phase 4A (Architecture Specification) and Phase 4B (Dataset Preprocessing, Feature Scaling & Artificial Masking Design).
- Retain open design decisions (`[DESIGN DECISION REQUIRED]` D01–D06) for experimental resolution in Phase 5 ablation studies.

### Evidence
- `research/Architecture/SLM Context Architecture.md`
- `src/context/context_features.py`
- `src/context/context_serializer.py`
- `src/context/context_builder.py`
- `src/context/slm_encoder.py`
- `tests/test_context.py`
- `research/Checkpoints/2026-09-17_phase_4a.md`

### Status
- **`PHASE_4A_SPECIFICATION_COMPLETE`**

---

## 2026-09-17 — Phase 4B: Experimental Dataset Construction & Masking Protocol

### Objective
Construct the experimental dataset layer required to evaluate the proposed SLM-conditioned diffusion imputation framework:
1. Feature normalization fit strictly on training observations without validation or test data leakage.
2. Leakage-safe chronological train/validation/test partitions with 24-hour temporal purge buffers.
3. Deterministic controlled missingness masking engine for MCAR ($10\%, 30\%, 50\%, 70\%$), Continuous Block MAR ($10\%, 30\%, 50\%, 70\%$), and Spatial Station Outage.
4. Structurally partitioned model inputs $\mathbf{X}_{\text{input}}$ and evaluation ground truth targets $\mathbf{Y}_{\text{target}}$ such that natural NaNs are never treated as targets.
5. Lightweight artifact design under `data/interim/experiments/` without raw tensor duplication.

### Work
- Authored primary research document `research/Experiments/Experimental Dataset Construction & Masking Protocol.md` covering all 18 mandatory sections.
- Implemented `src/dataset/normalization.py`:
  - `FeatureNormalizer`: Primary canonical contract `z_score` across all 13 canonical channels, ablation contract `log1p` for zero-inflated rainfall ($68.8\%$ zeros) with exact reversible roundtrip and non-negative guarantee, dynamic circular $(\sin \theta, \cos \theta)$ wind direction expansion (`transform_circular_wind()`), min-max, and robust scaling.
  - Fitted parameters strictly on $294,528$ training station-hours ($294,160$ training windows, 2019-01-01 to 2021-02-05).
  - Saved `data/interim/experiments/normalization/normalization_stats.json`.
- Implemented `src/dataset/missingness.py`:
  - `ExperimentalMaskGenerator`: Random MCAR, contiguous temporal block MAR with precision candidate trimming ($3\text{--}12\text{h}$), and deterministic rotating station outage scenarios (S1, S2, S4, S_full).
  - Enforced strict invariants: $M_{\text{art}} \le M_{\text{nat}}$, $M_{\text{nat}} = M_{\text{obs}} + M_{\text{tgt}}$, and $M_{\text{obs}} \odot M_{\text{tgt}} = 0$.
  - Partitioning method `partition_inputs_and_targets()`.
- Implemented `src/dataset/split.py`:
  - `ChronologicalSplitManager`: Verified reconciled purge buffers (24h calendar day duration, 25.0h physical gap between split endpoints, and 752 excluded sliding windows per buffer across all 16 stations).
  - Saved `data/interim/experiments/splits/split_indices.parquet` ($3.68\text{ MB}$) and `split_manifest.json`.
- Implemented and executed `src/dataset/build_experimental_datasets.py`:
  - Generated pre-computed benchmark evaluation masks for all $62,224$ test windows across 12 evaluation scenarios ($7,261,392$ eligible cells):
    - `mcar_10`: $10.07\%$ ($731,326$ cells) [Dev: $+0.07\%$]
    - `mcar_30`: $29.95\%$ ($2,174,824$ cells) [Dev: $-0.05\%$]
    - `mcar_50`: $49.96\%$ ($3,627,817$ cells) [Dev: $-0.04\%$]
    - `mcar_70`: $70.03\%$ ($5,085,285$ cells) [Dev: $+0.03\%$]
    - `block_10`: $10.07\%$ ($731,326$ cells) [Dev: $+0.07\%$] (trimmed)
    - `block_30`: $29.95\%$ ($2,174,824$ cells) [Dev: $-0.05\%$] (trimmed)
    - `block_50`: $49.96\%$ ($3,627,817$ cells) [Dev: $-0.04\%$] (trimmed)
    - `block_70`: $70.03\%$ ($5,085,285$ cells) [Dev: $+0.03\%$] (trimmed)
    - `station_outage_1`: $6.25\%$ ($453,636$ cells, $1/16$ stations)
    - `station_outage_2`: $12.50\%$ ($907,691$ cells, $2/16$ stations)
    - `station_outage_4`: $25.00\%$ ($1,815,340$ cells, $4/16$ stations)
    - `station_outage_full`: $100.00\%$ ($7,261,392$ cells, $16/16$ stations)
  - Saved `data/interim/experiments/masks/test_benchmark_masks.parquet` ($7.39\text{ MB}$).
  - Saved `data/interim/experiments/metadata/reproducibility_manifest.json` with SHA-256 hashes.
- Implemented automated quality control suite `tests/test_experimental_dataset.py`:
  - 15 automated checks covering window uniqueness, temporal separation, channel order, natural NaN preservation, target invariant, train-only stats, deterministic seeds, raw data immutability, artifact test mask validation, reversible log1p roundtrip, and circular wind decomposition.
  - 17/17 tests in the combined project test suite passed cleanly in $8.70\text{ seconds}$.
- Authored checkpoints `research/Checkpoints/2026-09-17_phase_4b.md` and `research/checkpoints/2026-09-17_phase_4b.md`.

### Finding
- **Zero-Leakage Guarantee**: Temporal separation is mathematically complete; training set ends 25 hours before validation set begins, and validation set ends 25 hours before test set begins.
- **Natural Missingness Conservation**: Exactly $55,876$ natural air quality NaNs preserved bit-for-bit. In all masking operations across 62,224 test windows, $0$ natural NaNs were converted into artificial targets.
- **Target Partition Invariant**: Verified $\mathbf{M}_{\text{nat}} \equiv \mathbf{M}_{\text{obs}} + \mathbf{M}_{\text{tgt}}$ across all $7,261,392$ candidate evaluation cells.
- **Precision Block Masking**: Continuous candidate block trimming achieved exact target missing rates within $\pm 0.07\%$ deviation.
- **Deterministic Station Outages**: Rotating station selection models network degradation across 1, 2, 4, and 16 stations without spatial bias.
- **Lightweight Storage Efficiency**: Stored only normalization statistics, split manifests, and benchmark masks ($<12\text{ MB}$ total), saving over $2\text{ GB}$ of redundant array copies.
- **Raw Data Immutability**: All 683 files in `data/raw/` 100% untouched.

### Decision
- Formally declare operational status: **`PHASE_4B_EXPERIMENTAL_DATASET = COMPLETE & AUDIT-VERIFIED`**.
- Establish `data/interim/experiments/` as the authoritative dataset representation for model construction and benchmarking.
- Maintain strict research boundaries: zero model training, zero imputation, zero claims of performance numbers.

### Evidence
- `research/Experiments/Experimental Dataset Construction & Masking Protocol.md`
- `data/interim/experiments/normalization/normalization_stats.json`
- `data/interim/experiments/splits/split_manifest.json`
- `data/interim/experiments/splits/split_indices.parquet`
- `data/interim/experiments/masks/test_benchmark_masks.parquet`
- `data/interim/experiments/metadata/reproducibility_manifest.json`
- `tests/test_experimental_dataset.py`
- `research/Checkpoints/2026-09-17_phase_4b.md`

### Status
- **`PHASE_4B_EXPERIMENTAL_DATASET_COMPLETE_AND_AUDIT_VERIFIED`**

---

## 2026-09-19 — Phase 4 Data Finalization: Frozen Training Package v1.0

### Objective
Freeze and package the validated Phase 1–4B data artifacts into a self-contained, reproducible training package (`CTDI_AirPollution_TrainingDataset_v1.0`) directly consumable by ML pipelines and teammate developers:
1. Export dual Parquet and dense NumPy NPZ representations for Train, Validation, and Test partitions.
2. Pre-compute and package all 12 benchmark evaluation masks (MCAR 10/30/50/70%, Contiguous Temporal Block 10/30/50/70%, and Station Outages S1, S2, S4, S_full).
3. Standardize schemas and metadata manifests (`channel_schema.csv`, `station_metadata.csv`, `split_manifest.csv`, `window_metadata.parquet`, `normalization_stats.json`, `masking_statistics.json`).
4. Generate self-contained documentation: `README.md`, `DATASET_CARD.md`, `dataset_manifest.json`, and `checksums/SHA256SUMS`.
5. Execute a 15-point automated validation engine, deterministic reproducibility verification, cryptographic checksum audit, and teammate consumption test suite.
6. Verify 100% cryptographic raw data immutability across all 683 files.
7. Maintain strict research boundary: zero model architecture implementation or model training (Phase 4C NOT started).

### Work
- Implemented packaging pipeline `src/dataset/build_final_package.py` and generated release directory `data/final/CTDI_AirPollution_TrainingDataset_v1.0/` (~121 MB across 46 files):
  - Train: `X_train.parquet` ($42.65\text{ MB}$), `M_natural_train.parquet` ($2.34\text{ MB}$), `X_train.npz` ($10.10\text{ MB}$, shape `(294160, 24, 13)`), `M_natural_train.npz` ($0.84\text{ MB}$).
  - Validation: `X_val.parquet` ($8.28\text{ MB}$), `M_natural_val.parquet` ($0.57\text{ MB}$), `X_val.npz` ($2.16\text{ MB}$, shape `(62608, 24, 13)`), `M_natural_val.npz` ($0.20\text{ MB}$).
  - Test: `X_test.parquet` ($8.86\text{ MB}$), `M_natural_test.parquet` ($0.57\text{ MB}$), `X_test.npz` ($2.17\text{ MB}$, shape `(62224, 24, 13)`), `M_natural_test.npz` ($0.19\text{ MB}$).
  - Benchmark Masks: `test_benchmark_masks.parquet` ($7.39\text{ MB}$) plus 12 modular `.npz` and `.parquet` scenario files under `masks/mcar/`, `masks/temporal_block/`, and `masks/station_outage/`.
  - Standardized Metadata: `channel_schema.csv`, `station_metadata.csv`, `split_manifest.csv`, `window_metadata.parquet`, `normalization_stats.json`, `masking_statistics.json`.
  - Package Documentation: `README.md`, `DATASET_CARD.md`, `dataset_manifest.json`, and `checksums/SHA256SUMS`.
- Implemented and executed 15-point automated validation suite `src/dataset/validate_final_dataset.py`: 15/15 checks passed with 100% success.
- Executed deterministic reproducibility check: 0 bitwise hash mismatches across independent export runs.
- Verified cryptographic SHA-256 manifest: all 46 package files reported `OK` via `sha256sum -c checksums/SHA256SUMS`.
- Implemented teammate consumption test suite `tests/test_teammate_consumption.py`: verified PyTorch `Dataset`/`DataLoader` batching, Pandas/Parquet reshaping, target firewall invariant on live batches, denormalization roundtrip, and dynamic mask loading. All 23 tests in project suite passed in 12.51s.
- Audited raw data: confirmed 683/683 raw files 100% bitwise identical against `raw_data_sha256_manifest.json`.
- Authored canonical research documentation: `research/Dataset/Final Training Dataset v1.0.md` and checkpoint `research/Checkpoints/2026-09-19_dataset_v1_finalization.md`.

### Finding
- **Self-Contained Portability**: Teammates can immediately consume the dataset via PyTorch `Dataset` or Pandas without running upstream preprocessing scripts.
- **Storage Efficiency**: Total package footprint is ~$121\text{ MB}$ ($56\text{ MB}$ train, $37\text{ MB}$ masks, $12\text{ MB}$ val, $12\text{ MB}$ test, $4\text{ MB}$ metadata).
- **Dual Representation Fidelity**: Dense NumPy arrays and Parquet tables contain identical values with zero precision loss.
- **Target Firewall Guarantee**: Target invariant $M_{\text{target}} \le M_{\text{natural}}$ holds across all $7,261,392$ candidate evaluation cells; zero natural sensor NaNs are treated as evaluation targets.
- **Raw Data Immutability**: All 683 raw files in `data/raw/` remain bit-for-bit identical to the baseline manifest.

### Decision
- Declare operational status: **`DATASET_V1_FROZEN_AND_PACKAGED = COMPLETE & VERIFIED`**.
- Freeze `data/final/CTDI_AirPollution_TrainingDataset_v1.0/` as the immutable dataset contract for model training.
- Any future scientific changes or additional sensor modalities require releasing an explicitly incremented dataset version (e.g., `v1.1`).
- Proceed to Phase 4C (Model Architecture Scaffolding) only upon user authorization; Phase 4C is currently **`NOT_STARTED`**.

### Evidence
- `data/final/CTDI_AirPollution_TrainingDataset_v1.0/`
- `src/dataset/build_final_package.py`
- `src/dataset/validate_final_dataset.py`
- `tests/test_teammate_consumption.py`
- `research/Dataset/Final Training Dataset v1.0.md`
- `research/Checkpoints/2026-09-19_dataset_v1_finalization.md`

### Status
- **`DATASET_V1_FROZEN_AND_PACKAGED`**
