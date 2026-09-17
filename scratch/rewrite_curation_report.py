report_content = """# Research Information Curation & Knowledge Consolidation Report

**Project**: Context-Aware Generative Imputation of Air Pollution Using SLM-Conditioned Diffusion  
**Subsystem**: Research Knowledge Base Curation & Cognitive Architecture  
**Execution Timestamp**: 2026-09-17  
**Benchmark Reference**: Yu et al., *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, **IEEE Transactions on Big Data**, vol. 11, no. 5, pp. 2442–2455, Sept.–Oct. 2025.  
**Curation Principle**: **One Topic → One Primary Canonical Note → Complete Curated Information**, supported by immutable empirical evidence and chronological checkpoints.

---

## 1. Executive Summary & Curation Mandate

Over the course of initial data discovery, empirical validation, and data pipeline construction, the `research/` directory expanded organically to 96 files. While this organic development ensured thorough logging of scientific evidence, it introduced acute **cognitive fragmentation and information duplication**:
- A researcher seeking to understand the CTDI baseline had to consult up to 6 distinct Markdown files (`CTDI Dataset Specifications.md`, `ctdi_table_i_reconstruction.md`, `ctdi_channel_reconstruction.md`, `ctdi_traffic_variable_verification.md`, `ctdi_source_fidelity_report.md`, and `ctdi_consistency_matrix.md`).
- Provenance and custody details were split across `provenance.md`, an unformatted draft export `Hello.md`, `source_inventory.md`, and `raw_data_availability_and_verification.md`.
- Preprocessing documentation was duplicated three times: in `research/preprocessing/` (7 files), in a monolithic handbook `reports/Data Processing - Hong Kong.md`, and in a 10-file subfolder `reports/Data Preprocessing/` (chapters 00 to 09).
- Scratch terminal logs (`Phase 1.md`, `Phase 2.md`, `Alignment - PY.md`) and superseded early drafts (`CTDI Dataset Description.md`) cluttered the `reports/` directory.
- Theoretical missingness ($M_{\\text{obs}}$ vs $M_{\\text{eval}}$) was severed from empirical missingness findings (diurnal curves, calibration windows, pollutant parity, and Figures 6–9).
- Broken relative image links and obscure screenshot filenames (`Screenshot_2026-09-16_15-02-33.png`) impaired visual navigation in Obsidian.

In strict adherence to project directives and user clarification:
1. **Top-Level Structure Preserved**: The 10 intentional top-level categories (`architecture/`, `checkpoints/`, `dataset/`, `decisions/`, `experiments/`, `figures/`, `findings/`, `literature/`, `preprocessing/`, `reports/`) were 100% preserved. No artificial directory hierarchies were created.
2. **Subfolder Redundancy Eradicated**: The redundant subfolder `reports/Data Preprocessing/` (all 10 chapters) was completely removed, as its content is fully contained within the monolithic handbook `reports/Data Processing - Hong Kong.md` and the modular implementation specifications in `preprocessing/`.
3. **Scratch & Superseded Reports Pruned**: Removed redundant scratch logs (`Phase 1.md`, `Phase 2.md`, `Alignment - PY.md`) and the superseded preliminary draft `CTDI Dataset Description.md`.
4. **Human-Readable Research Naming**: Standardized all notes with intuitive research titles (e.g. `CTDIDataset Specifications.md`, `Station Inventory & Spatial Network.md`, `Missingness Architecture & Empirical Distribution.md`). Generic snake_case names were strictly rejected.
5. **Topic Consolidation**: Every core research topic is now anchored by **exactly one primary canonical document** containing complete, self-contained, and up-to-date knowledge.
6. **Zero Broken Links**: Verified **0 broken markdown links and 0 broken `<img>` tags** across the entire repository.
7. **Raw Data Immutability**: Absolute immutability of `data/raw/` (683 files) and all Phase 1.1 / Phase 2 artifacts verified.

---

## 2. Complete Inventory of Files Inspected & Final Structure

A recursive audit of the `research/` directory was conducted across all 10 intentional categories. Following the removal of 16 redundant/scratch files and draft exports, the curated repository contains **80 authoritative files**:

| Category / Directory | Curated File Count | Description & Focus |
| :--- | :---: | :--- |
| **Root (`research/`)** | 6 | `MASTER_RESEARCH_DOCUMENT.md`, `README.md`, `research_status.md`, `research_timeline.md`, `Obsidian Figure Template.md`, and the published CTDI paper PDF. |
| **`architecture/`** | 8 | Deep generative diffusion backbone, SLM context encoder, AdaLN conditioning, loss objectives, spatial priors, and system architecture. |
| **`checkpoints/`** | 6 | Immutable dated daily research logs (`2026-09-13.md`, `2026-09-14.md`, `2026-09-17.md`, `2026-09-17_phase_1_1.md`, `2026-09-17_phase_2.md`, `README.md`). |
| **`dataset/`** | 16 | Ground truth specifications, provenance, channel definitions, consistency matrices, station coordinates, temporal accounting, and the 4 CTDI paper reference screenshots. |
| **`decisions/`** | 5 | Formal Architectural Decision Records (ADRs) covering Dataset, Architecture, Preprocessing, Experimental decisions, and the ADR Index. |
| **`experiments/`** | 7 | Training protocols, baseline model definitions, ablation study plans, missingness masks, evaluation metrics, and cross-dataset benchmarks. |
| **`figures/`** | 4 | High-resolution empirical replication figures (`fig_06_...` to `fig_09_...`) generated programmatically. |
| **`findings/`** | 5 | Confirmed research findings, negative findings / dead ends, living unresolved questions, research boundaries, and findings index. |
| **`literature/`** | 4 | Line-by-line CTDI paper analysis, SLM conditioning literature, related time-series imputation surveys, and literature index. |
| **`preprocessing/`** | 8 | Implementation specifications for ingestion, cleaning, temporal grid assembly, spatial IDW, feature engineering, normalization, quality assurance, and preprocessing README. |
| **`reports/`** | 12 | 11 substantive empirical investigation reports/handbooks plus `README.md` (scratch logs, obsolete drafts, and the redundant `Data Preprocessing/` subfolder removed). |
| **Total** | **80** | **100% curated, self-contained, and non-redundant.** |

---

## 3. Core Research Topics Identified

The repository's knowledge space is organized into **15 Core Research Topics**:

1. **CTDI Reference Dataset & Published Benchmark**: What Yu et al. (IEEE TBD 2025) actually used, Table I, 13 channels, 607 road links, 47 AWS stations, and reference figures.
2. **Reconstructed Hong Kong Dataset & Provenance**: Our real reconstructed dataset, custody chain, official URLs, download parameters, row counts, and cryptographic hashes.
3. **CTDI vs. Our Reconstruction Divergence**: Feature-by-feature comparative matrix, visibility vs. rainfall justification, traffic speed and congestion fidelity.
4. **Air Quality Monitoring Network**: 16 EPD monitoring stations (13 ambient, 3 roadside), geographic distribution, GPS coordinates, and historical commissioning constraints.
5. **Temporal Coverage & Calendar Accounting**: 3 full calendar years (2019–2021), 2020 leap year accounting, 26,304 continuous hours, and Cartesian grid completeness.
6. **Missingness Architecture & Empirical Distribution**: Theoretical missingness formulation ($M_{\\text{obs}}$ vs $M_{\\text{eval}}$), empirical findings, diurnal 01:00 calibration spike, and 20% pollutant parity.
7. **Meteorology & Visibility Recovery**: HKO AWS 10-minute visibility irrecoverability audit, public API limitations, and physical justification for ERA5 rainfall substitution.
8. **Traffic Extraction & Verification**: Transport Department 1st Generation Traffic Speed Map XML parent system (607 links, 774,686 snapshots, 466.8M records) vs rejected ATC/Dashboard sources.
9. **Spatial Alignment & Network Geometry**: Pairwise 16×16 Haversine distance matrix, Inverse Distance Weighting ($p=2$) mathematics, and link-to-station assignment.
10. **Spatio-Temporal Alignment (Phase 2)**: Construction and validation of the unified Cartesian grid $\\mathcal{S} \\times \\mathcal{T} = 420,864$ station-hours across 13 canonical channels.
11. **Data Preprocessing Engineering**: Ingestion schemas, bilingual cleaning, 24-hour interval convention, MinMax scaling on train-only split, and quality assurance playbooks.
12. **Generative Model Architecture**: SLM context encoder (atmospheric prompt builder + lightweight LLM), conditional diffusion backbone (DDPM + AdaLN), and spatial/temporal denoising layers.
13. **Experimental Protocols & Benchmarks**: 70/15/15 chronological split, evaluation metrics (MAE, RMSE, MAPE, CRPS, PICP), missingness scenarios (MCAR, block, outage), and baselines.
14. **Methodological Decisions (ADRs)**: Master Architectural Decision Records establishing immutable scientific choices.
15. **Scientific Findings & Limitations**: Confirmed empirical discoveries, documented negative findings (dead ends to avoid), and living unresolved questions.

---

## 4. Duplicate Information Identified & Resolved

| Information Domain | Duplicate Locations Prior to Curation | Consolidation Action & Resolution |
| :--- | :--- | :--- |
| **Data Preprocessing Documentation** | Split across 3 places: `reports/Data Preprocessing/` (10 files), `reports/Data Processing - Hong Kong.md` (monolithic handbook), and `preprocessing/` (7 modular specs). | **Purged `reports/Data Preprocessing/` subfolder entirely (10 files deleted).** Retained `reports/Data Processing - Hong Kong.md` as the monolithic reference manual and `preprocessing/` as implementation specs. |
| **Phase 1 Execution Logs** | `reports/Phase 1.md` (unformatted console output) duplicated `reports/Phase 1 - Source-Specific Cleaning Report.md`. | **Deleted `reports/Phase 1.md`.** All empirical cleaning metrics, schemas, and Phase 1.1 traffic extraction are authoritative in `Phase 1 - Source-Specific Cleaning Report.md`. |
| **Phase 2 & Alignment Scratch Files** | `reports/Phase 2.md` (early broken LaTeX plan) and `reports/Alignment - PY.md` (early terminal output) duplicated `Phase 2 - Spatio-Temporal Alignment Report.md`. | **Deleted `reports/Phase 2.md` and `reports/Alignment - PY.md`.** The complete 420,864-row Cartesian grid validation is authoritative in `Phase 2 - Spatio-Temporal Alignment Report.md`. |
| **Superseded Dataset Draft** | `reports/CTDI Dataset Description.md` (authored 2026-09-12 with outdated assumptions like rainfall and traffic volume) duplicated and contradicted `dataset/CTDIDataset Specifications.md`. | **Deleted `reports/CTDI Dataset Description.md`.** All station metadata was verified in `dataset/Station Inventory & Spatial Network.md` and Table I specs in `dataset/CTDIDataset Specifications.md`. |
| **CTDI Table I & Channels** | Repeated across `CTDI Dataset Specifications.md`, `ctdi_table_i_reconstruction.md`, `ctdi_channel_reconstruction.md`, and `MASTER_RESEARCH_DOCUMENT.md`. | Consolidated full Table I reproduction, 13-channel definitions, units, and cadences directly into primary document `dataset/CTDIDataset Specifications.md`. |
| **Dataset Provenance & Hashes** | Fragmented across `provenance.md`, draft export `Hello.md`, `source_inventory.md`, and `raw_data_integrity_manifest.md`. | Consolidated unbroken chain of custody, official download links, row counts, and cryptographic hashes into primary document `dataset/Dataset Provenance & Specifications.md`. `Hello.md` deleted. |
| **Missingness Distribution & Figures** | Theoretical mask math in `missingness_analysis.md`; empirical diurnal peaks, pollutant parity, and Figures 6–9 in `ctdi_missingness_pattern_analysis.md`. | Unified theory and empirical analysis into `dataset/Missingness Architecture & Empirical Distribution.md`, with embedded side-by-side figures and explicit diurnal peak statistics. |

---

## 5. Primary Documents Selected & Justification

To realize the **One Topic → One Primary Canonical Note** model, 15 primary documents were designated and enriched:

| # | Topic | Primary Canonical Document | Justification |
| :-: | :--- | :--- | :--- |
| 1 | **CTDI Benchmark** | `research/dataset/CTDIDataset Specifications.md` | Authoritative reference containing verbatim Table I, exact channel specifications, sensor counts, and side-by-side paper figure comparisons. |
| 2 | **Reconstructed HK Dataset** | `research/dataset/Dataset Provenance & Specifications.md` | Master provenance note tracking official URLs, file hashes, acquisition methods, and validated row counts across all modalities. |
| 3 | **CTDI vs Reconstruction** | `research/dataset/CTDI Dataset Consistency Matrix.md` | Exhaustive variable-by-variable matrix auditing exact matches, justified substitutions, and operational assumptions. |
| 4 | **Air Quality Network** | `research/dataset/Station Inventory & Spatial Network.md` | Primary spatial registry defining all 16 stations, latitudes, longitudes, base elevations, and intake heights. |
| 5 | **Temporal Accounting** | `research/dataset/Temporal Coverage & Calendar Accounting.md` | Master temporal ledger detailing continuous hourly coverage, leap year handling, and Cartesian row accounting. |
| 6 | **Missingness Architecture** | `research/dataset/Missingness Architecture & Empirical Distribution.md` | Synthesizes theoretical mask mechanics ($M_{\\text{obs}}$ vs $M_{\\text{eval}}$) with empirical multi-year diurnal distributions and pollutant parity. |
| 7 | **Meteorology & Visibility** | `research/reports/Visibility Data Recovery & Provenance Report.md` | Authoritative investigation proving HKO AWS visibility irrecoverability and establishing the scientific validity of ERA5 rainfall substitution. |
| 8 | **Traffic Extraction** | `research/reports/ctdi traffic variable verification.md` | Rigorous empirical proof demonstrating why TD 1st Gen `speedmap.xml` matches CTDI's 607 road links and refuting flawed alternatives. |
| 9 | **Spatial Alignment & IDW** | `research/dataset/Spatial Alignment & Network Geometry.md` | Authoritative mathematical specification of pairwise Haversine geometry and inverse distance weighting ($p=2$). |
| 10 | **Spatio-Temporal Alignment** | `research/reports/Phase 2 - Spatio-Temporal Alignment Report.md` | Primary engineering and validation report detailing the unified 420,864-row Cartesian grid across all 13 channels. |
| 11 | **Preprocessing Engineering** | `research/reports/Data Processing - Hong Kong.md` | Comprehensive 454-line technical manual guiding data transformations from raw ingest to model tensors. |
| 12 | **Model Architecture** | `research/architecture/System Architecture.md` | High-level architectural blueprint uniting the SLM context encoder, conditional diffusion denoiser, and spatio-temporal layers. |
| 13 | **Experimental Protocols** | `research/experiments/Experimental Training Protocol.md` | Complete specification of training regimes, 70/15/15 splits, optimization parameters, and validation cadences. |
| 14 | **Methodological Decisions** | `research/decisions/README.md` | Master ADR registry detailing all architectural and dataset decisions with their active epistemic statuses. |
| 15 | **Scientific Findings** | `research/findings/Confirmed Research Findings.md` | Living catalogue of empirically proven facts, accompanied by negative results in `findings/Negative Findings & Dead Ends.md`. |

---

## 6. Information Consolidated

### A. Primary Document: `dataset/CTDIDataset Specifications.md`
- **Integrated**:
  - Verbatim Table I reproduction with exact English names, symbols, sampling intervals, and units.
  - 13-channel decomposition: Criteria Air Pollutants (5), Surface Meteorology (6), Urban Traffic (2).
  - Explicit documentation of the 607 road links from Transport Department `speedmap.xml`.
  - Documentation of 47 HKO Automatic Weather Stations (AWS) with 10-minute native cadence.
  - CTDI published natural missingness: 55,875 missing entries ($2.46\\%$ rate).
  - Side-by-side visual comparison tables pairing CTDI published Figures 6, 7, 8, 9 with our empirical figures.
  - Hyperlinks to deep empirical proofs in `reports/`.

### B. Primary Document: `dataset/Dataset Provenance & Specifications.md`
- **Integrated**:
  - Full unbroken chain of custody: $\\text{Data Source} \\to \\text{Official Link} \\to \\text{Local Raw File & SHA-256} \\to \\text{Audit Findings} \\to \\text{Decision} \\to \\text{Data Used}$.
  - Air Quality: EPD 16 stations, 26,304 hours, 420,864 rows, 55,876 missing entries ($99.99995\\%$ parity).
  - Surface Meteorology: ECMWF ERA5 reanalysis at the 16 station coordinates, 100% complete, zero missing.
  - Urban Traffic: Full Phase 1.1 extraction metrics incorporated (**774,686 snapshots**, **466,829,497 records**, 632 unique links union, 590 common core links, 0 failed snapshots across 36 monthly archives).
  - Spatial Network: Pairwise Haversine distance matrix ($16 \\times 16$).
  - Complete cryptographic raw manifest with SHA-256 hashes and row counts.

### C. Primary Document: `dataset/Missingness Architecture & Empirical Distribution.md`
- **Integrated**:
  - Theoretical framework: Natural Missingness Mask ($M_{\\text{obs}}$) vs Simulated Evaluation Mask ($M_{\\text{eval}}$).
  - Multi-year invariance: 2019 (17,629), 2020 (18,025), 2021 (20,222) totaling 55,876 entries.
  - Diurnal profile analysis: Hour 1 peak ($16.0\\%$ calibration spike) and Hour 4 secondary peak ($10.3\\%$).
  - Pollutant parity: $\\text{PM}_{2.5}$ ($19.1\\%$), $\\text{PM}_{10}$ ($20.4\\%$), $\\text{NO}_2$ ($20.9\\%$), $\\text{SO}_2$ ($19.8\\%$), $\\text{O}_3$ ($19.9\\%$).
  - Station reliability: Roadside monitors exhibit $>96.3\\%$ completeness, matching ambient stations.
  - High-resolution figures embedded with corrected relative paths.

---

## 7. Documents Merged

- **`research/Hello.md` $\\to$ `research/dataset/Dataset Provenance & Specifications.md`**:
  - Audit revealed `Hello.md` was an unformatted draft export of `provenance.md`.
  - All text, markdown tables, SHA-256 hashes, and pipeline notes from `Hello.md` were verified as 100% present in `Dataset Provenance & Specifications.md`.
  - `Hello.md` was safely removed.

---

## 8. Documents Preserved as Supporting Evidence

Detailed empirical reports and execution logs were preserved intact under `research/reports/` to maintain an immutable scientific audit trail:

1. **`reports/Phase 1 - Source-Specific Cleaning Report.md`**: Preserved as the active engineering report documenting Phase 1 cleaning and Phase 1.1 full traffic extraction.
2. **`reports/Phase 2 - Spatio-Temporal Alignment Report.md`**: Preserved as the active engineering report documenting Phase 2 alignment and Cartesian grid validation.
3. **`reports/Visibility Data Recovery & Provenance Report.md`**: Preserved as the formal audit proving HKO 10-minute visibility is irrecoverable from open data.
4. **`reports/CTDI Missingness Pattern Analysis.md`**: Preserved as the deep statistical report explaining the 1-hour temporal offset between EPD 1-indexed interval-end hours and ISO interval-start timestamps.
5. **`reports/Data Processing - Hong Kong.md`**: Preserved as the comprehensive, monolithic 454-line data engineering manual.
6. **`reports/ctdi table I reconstruction.md`**: Preserved as the gold-standard verbatim transcription of Table I discovered on 2026-09-13.
7. **`reports/ctdi traffic variable verification.md`**: Preserved as the empirical proof validating `speedmap.xml` (607 links) and refuting ATC / City Dashboard.
8. **`reports/ctdi channel reconstruction.md`**: Preserved as the audit documenting the divergence between published CTDI variables and early interim code.
9. **`reports/ctdi source fidelity report.md`**: Preserved as the source-by-source fidelity audit matching raw data characteristics to paper citations.
10. **`reports/Raw Data Availability & Verification.md`**: Preserved as the baseline physical verification log of initial raw downloads.
11. **`reports/Research Information Curation Report.md`**: Preserved as the authoritative curation report.

---

## 9. Documents Archived / Removed

A total of 16 redundant, duplicate, or draft files were removed from the repository:

1. **`research/reports/Data Preprocessing/` (10 files deleted)**:
   - `00 - Overview & Pipeline Architecture.md`
   - `01 - Raw Data Sources & Ingestion.md`
   - `02 - Cleaning, Translation & Formatting.md`
   - `03 - Missingness Architecture (Natural vs Simulated).md`
   - `04 - Spatial Alignment & 13-Channel Formulation.md`
   - `05 - Feature Engineering & Normalization.md`
   - `06 - 24-Hour Sliding Window Segmentation.md`
   - `07 - Environmental Context Builder for SLM.md`
   - `08 - Canonical Data Storage & File Layout.md`
   - `09 - Quality Assurance & Verification Playbook.md`
   *(All 10 chapters 100% duplicated in `reports/Data Processing - Hong Kong.md` and `preprocessing/`)*.
2. **`research/reports/Phase 1.md` (Deleted)**: Scratch console output, fully superseded by `Phase 1 - Source-Specific Cleaning Report.md`.
3. **`research/reports/Phase 2.md` (Deleted)**: Obsolete scratch plan with corrupted math formatting, fully superseded by `Phase 2 - Spatio-Temporal Alignment Report.md`.
4. **`research/reports/Alignment - PY.md` (Deleted)**: Scratch console log of dry run, fully superseded by `Phase 2 - Spatio-Temporal Alignment Report.md`.
5. **`research/reports/CTDI Dataset Description.md` (Deleted)**: Superseded early draft from 2026-09-12 containing outdated assumptions; canonical knowledge consolidated into `dataset/CTDIDataset Specifications.md`.
6. **`research/Hello.md` (Deleted)**: Unformatted draft export of `provenance.md`.
7. **`research/reports/Untitled.base` (Deleted)**: Empty 4-line Obsidian interface artifact.

---

## 10. Information Moved Between Documents

1. **Phase 1.1 Traffic Extraction Results**:
   - Moved from temporary session logs into `dataset/Dataset Provenance & Specifications.md` (§3.3) and `dataset/CTDIDataset Specifications.md` (§3).
2. **Side-by-Side Figure Layouts**:
   - Transferred structured layout syntax from `Obsidian Figure Template.md` into `dataset/CTDIDataset Specifications.md` to format Figures 6–9.
3. **Diurnal Peak Breakdown & Station Parity**:
   - Synthesized key numerical tables from `reports/CTDI Missingness Pattern Analysis.md` into `dataset/Missingness Architecture & Empirical Distribution.md`.
4. **Rainfall Scavenging Physics**:
   - Lifted environmental aerosol physics justification from `decisions/Dataset Decisions.md` into `dataset/Dataset Provenance & Specifications.md` (§4).

---

## 11. Link, Image, and Syntax Repairs

All broken relative links and image references were systematically repaired:

1. **Image Filename Standardization**:
   - `research/dataset/Screenshot_2026-09-16_15-02-33.png` $\\to$ `research/dataset/air - missing by hour year.png` (matches sibling figures `air - station vs missing.png`, `air - pollutant by missing.png`, `air - pollution hour vs missing.png`).
2. **Image Path Normalization in `dataset/CTDIDataset Specifications.md`**:
   - Repaired broken `../` relative paths for local CTDI reference screenshots.
   - Pointed generated empirical figures to `../figures/fig_06_...` to `../figures/fig_09_...`.
3. **Pie Chart vs Bar Chart Alignment in `reports/CTDI Missingness Pattern Analysis.md`**:
   - Updated broken bar chart paths (`fig_07_missing_proportion_by_hour.png`) to point to actual generated pie chart assets (`fig_07_missing_proportion_by_hour_pie.png`, etc.).
4. **Cross-Document Hyperlinks**:
   - Updated `research/README.md`, `research/MASTER_RESEARCH_DOCUMENT.md`, `research/research_status.md`, `research/research_timeline.md`, root `README.md`, and all 10 folder `README.md` files to point only to active, non-deleted files.
5. **Automated Verification**:
   - **Repository-wide broken markdown links: 0**
   - **Repository-wide broken `<img>` tags: 0**

---

## 12. Current Source-of-Truth Map

The complete, authoritative source-of-truth mapping across the entire research knowledge base:

```text
========================================================================================================
TOPIC                              PRIMARY CANONICAL NOTE               SUPPORTING EVIDENCE (REPORTS)
========================================================================================================
CTDI Published Benchmark           dataset/CTDIDataset Specifications   reports/ctdi table I reconstruction
                                                                        reports/ctdi channel reconstruction
                                                                        reports/ctdi traffic variable verification
                                                                        reports/ctdi source fidelity report
--------------------------------------------------------------------------------------------------------
Reconstructed HK Dataset           dataset/Dataset Provenance & Specs   reports/Phase 1 - Cleaning Report
                                                                        reports/Raw Data Availability
                                                                        dataset/Raw Data Integrity Manifest
--------------------------------------------------------------------------------------------------------
CTDI vs Reconstruction Divergence  dataset/CTDI Consistency Matrix      reports/Visibility Recovery Report
                                                                        decisions/Dataset Decisions
--------------------------------------------------------------------------------------------------------
Air Quality Monitoring Network     dataset/Station Inventory            dataset/Canonical Dataset Definition
                                                                        preprocessing/Cleaning Rules
--------------------------------------------------------------------------------------------------------
Temporal Coverage & Accounting     dataset/Temporal Coverage            reports/Raw Data Availability
                                                                        preprocessing/Temporal Alignment
--------------------------------------------------------------------------------------------------------
Missingness Theory & Distribution  dataset/Missingness Architecture     reports/CTDI Missingness Analysis
                                                                        figures/fig_06 to fig_09
--------------------------------------------------------------------------------------------------------
Meteorology & Visibility Recovery  reports/Visibility Recovery Report   dataset/Data Source Inventory
                                                                        decisions/Dataset Decisions
--------------------------------------------------------------------------------------------------------
Traffic Extraction & Proof         reports/ctdi traffic variable verif  reports/Phase 1 - Cleaning Report
                                                                        checkpoints/2026-09-17_phase_1_1
--------------------------------------------------------------------------------------------------------
Spatial Alignment & Geometry       dataset/Spatial Alignment            preprocessing/Spatial Alignment
                                                                        reports/Phase 2 - Alignment Report
--------------------------------------------------------------------------------------------------------
Spatio-Temporal Alignment (Ph. 2)  reports/Phase 2 - Alignment Report   reports/Phase 1 - Cleaning Report
                                                                        preprocessing/Temporal Alignment
--------------------------------------------------------------------------------------------------------
Preprocessing Engineering          reports/Data Processing - Hong Kong  preprocessing/README
                                                                        preprocessing/Data Quality Assurance
--------------------------------------------------------------------------------------------------------
Generative Model Architecture      architecture/System Architecture     architecture/Conditional Diffusion Model
                                                                        architecture/SLM Context Encoder
                                                                        architecture/Temporal Denoising Model
--------------------------------------------------------------------------------------------------------
Experimental Protocols             experiments/Experimental Protocol    experiments/Baseline Imputation Models
                                                                        experiments/Missingness Scenarios
                                                                        experiments/Evaluation Metrics
--------------------------------------------------------------------------------------------------------
Methodological Decisions           decisions/README (ADR Register)      decisions/Dataset Decisions
                                                                        decisions/Architecture Decisions
                                                                        decisions/Preprocessing Decisions
--------------------------------------------------------------------------------------------------------
Scientific Findings & Boundaries   findings/Confirmed Findings          findings/Negative Findings & Dead Ends
                                                                        findings/Living Unresolved Questions
                                                                        findings/Research Boundaries
========================================================================================================
```

---

## 13. Living Unresolved Ambiguities & Open Questions

While the knowledge base is now fully curated and consolidated, two minor technical questions remain documented in `findings/Living Unresolved Questions.md`:
1. **Traffic Congestion Ordinal Scale**: CTDI Table I denotes congestion levels as an unscaled categorical variable without giving explicit float cutoffs. We have adopted an equidistant ordinal scale (`GOOD` = 0.0, `AVERAGE` = 0.5, `BAD` = 1.0) with documented assumption status `[ASSUMPTION]`.
2. **HKO Rain Gauge Network vs. ERA5 Total Precipitation**: While ERA5 surface reanalysis provides complete, zero-leakage, hourly rainfall across all 16 station coordinates, future ablations may benchmark ERA5 against HKO automatic tipping-bucket rain gauges if local convective spikes require higher fidelity.

---

## 14. Fast Navigation: The 15-Question Validation Test

To verify that cognitive friction has been eradicated, the 15-Question Fast Navigation Test was executed. Any researcher can answer each question by opening **exactly one document**:

| # | Core Research Question | Single Document to Open | Section & Immediate Answer |
| :-: | :--- | :--- | :--- |
| **1** | **What exactly did CTDI use as its dataset?** | `dataset/CTDIDataset Specifications.md` | §1–4: 16 EPD air quality stations, 47 HKO AWS stations (10-min), 607 road links (5-min `speedmap.xml`), 3 years (2019–2021). |
| **2** | **What are CTDI's 13 channels?** | `dataset/CTDIDataset Specifications.md` | §4: 5 Criteria Pollutants ($\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{NO}_2$, $\text{SO}_2$, $\text{O}_3$), 6 Weather (Pressure, RH, Temp, Visibility, Wind Dir, Wind Speed), 2 Traffic (Speed, Congestion). |
| **3** | **What did CTDI use for traffic?** | `dataset/CTDIDataset Specifications.md` | §3: 607 road links from Transport Department `speedmap.xml` recorded at 5-minute intervals. |
| **4** | **What did CTDI use for meteorology?** | `dataset/CTDIDataset Specifications.md` | §2: 47 Hong Kong Observatory Automatic Weather Stations (AWS) with 10-minute native sampling, including visibility. |
| **5** | **What is known about CTDI visibility?** | `dataset/Dataset Provenance & Specifications.md` | §4: Retrospective 10-min HKO visibility is irrecoverable from public archives (offline data from HKU). Scientifically substituted by ERA5 rainfall. |
| **6** | **What data did we actually recover?** | `dataset/Dataset Provenance & Specifications.md` | §2–5: 16 EPD air stations (420,864 rows, 55,876 missing entries), 16 ERA5 surface weather series (100% complete), 36 monthly SpeedMap archives (774k snapshots, 466M records). |
| **7** | **What are the differences between CTDI and our reconstruction?** | `dataset/CTDIDataset Specifications.md` | §5: Explicit Comparative Divergence Table (Air Quality: Exact Match; Traffic: System Match; Weather: ERA5 substitution; Channel 9: Rainfall vs Visibility). |
| **8** | **What are our 16 stations?** | `dataset/Station Inventory & Spatial Network.md` | §1–2: 13 ambient stations + 3 roadside stations (Causeway Bay, Central, Mong Kok) with GPS coordinates and sensor heights. Southern and North excluded. |
| **9** | **What is our temporal coverage?** | `dataset/Temporal Coverage & Calendar Accounting.md` | §1: 2019-01-01 00:00:00 to 2021-12-31 23:00:00 (1,096 continuous calendar days, 2020 leap year accounted, 26,304 hourly timestamps). |
| **10** | **What is our natural missingness?** | `dataset/Missingness Architecture & Empirical Distribution.md` | §2: 55,876 entries ($2.6553\\%$ rate), diurnal peak at 01:00 ($16.0\\%$ calibration window), near-equal pollutant parity ($\sim 20\\%$ each). |
| **11** | **What preprocessing has been completed?** | `reports/Data Processing - Hong Kong.md` | §1: Full end-to-end data pipeline from raw ingestion, bilingual cleaning, 24-hour interval conversion, spatial IDW, and tensor formulation. |
| **12** | **What traffic processing has been completed?** | `reports/Phase 1 - Source-Specific Cleaning Report.md` | §3: 36 monthly partitions, 774,686 snapshots, 466,829,497 records, 632 unique links union, 590 common core links, zero failed snapshots. |
| **13** | **What decisions have been made?** | `decisions/README.md` | Master ADR Register: 13 channels, zero synthetic data, rainfall substitution, IDW $p=2$, train-only normalization, and conditional diffusion backbone. |
| **14** | **Why are we using rainfall instead of visibility?** | `dataset/Dataset Provenance & Specifications.md` | §4: Physical rationale of wet scavenging / precipitation washout on PM and gases, coupled with open-data irrecoverability of HKO AWS visibility. |
| **15** | **What is the current project status?** | `research/research_status.md` | Phase 1, Phase 1.1, and Phase 2 are 100% complete. 420,864-row Cartesian grid validated. Phase 3 (sliding windows) is awaiting user authorization. |

---

## 15. Conclusion & Verification Summary

The curation and consolidation of the `research/` directory is complete. Redundancies and scratch logs have been permanently eliminated:
- **Structure**: 10 intentional top-level categories preserved. Redundant subfolder `reports/Data Preprocessing/` eliminated.
- **Cognitive Clarity**: Zero duplicate files; 15 self-contained primary topic notes.
- **Link Integrity**: 0 broken markdown links; 0 broken image tags across the entire repository.
- **Data Safety**: `data/raw/` untouched; Phase 1.1 / Phase 2 artifacts preserved.
- **Operational Freeze**: Ready for Phase 3 whenever authorized.
"""

with open("research/reports/Research Information Curation Report.md", "w") as f:
    f.write(report_content)

print("Updated research/reports/Research Information Curation Report.md successfully.")
