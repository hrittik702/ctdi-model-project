readme_content = """# Research Knowledge Base & Documentation Hub

**Project**: Context-Aware Generative Imputation of Air Pollution Using SLM-Conditioned Diffusion  
**Core Benchmark**: Yu et al., *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, **IEEE Transactions on Big Data**, vol. 11, no. 5, pp. 2442–2455, Sept.–Oct. 2025.  
**Target Domain**: Hong Kong SAR (16 stations × 26,304 hours × 13 channels; 2019-01-01 00:00 to 2021-12-31 23:00)  
**Current Milestone**: Phase 2 Complete (Spatio-Temporal Alignment & 13-Channel Cartesian Grid Verified)  
**Epistemic Standard**: Curated Knowledge Base where **One Topic → One Primary Canonical Note → Complete Curated Information**.

---

## 1. Quick Start: Where to Begin

If you are joining or resuming this project, follow this curated entry sequence:

1. **[Master Research Document](MASTER_RESEARCH_DOCUMENT.md)**: The comprehensive thesis document uniting dataset design, literature foundation, diffusion architecture, and empirical findings.
2. **[Research Status Dashboard](research_status.md)**: High-level operational readiness, active blockers, and progress across all phases.
3. **[Research Timeline](research_timeline.md)**: Chronological history of scientific discoveries, data audits, and architectural shifts.
4. **[Latest Daily Checkpoints](checkpoints/README.md)**: Immutable daily session logs ([2026-09-17 Phase 2](checkpoints/2026-09-17_phase_2.md), [2026-09-17 Phase 1.1](checkpoints/2026-09-17_phase_1_1.md), [2026-09-13](checkpoints/2026-09-13.md)).
5. **[Confirmed Findings](findings/Confirmed%20Research%20Findings.md)** & **[Negative Findings](findings/Negative%20Findings%20&%20Dead%20Ends.md)**: What was empirically proven true, and critical dead ends that must not be repeated.
6. **[Methodological Decisions](decisions/README.md)**: Formal decision records (ADRs) explaining key scientific and architectural choices.

---

## 2. Topic Navigation Map (One Topic → One Primary Note)

To eliminate information duplication and fragmentation, the research knowledge base is organized around **15 Core Research Topics**. Every topic is anchored by **one primary canonical note** that contains complete, self-contained knowledge. Supporting empirical investigation reports and historical logs are hyperlinked as secondary evidence.

| # | Research Topic | Primary Canonical Document | Key Focus & Scope | Supporting Evidence & Reports | Historical Checkpoints |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **1** | **CTDI Benchmark & Paper Specification** | **[CTDIDataset Specifications.md](dataset/CTDIDataset%20Specifications.md)** | Verbatim Table I, 13 channels, 607 road links, 47 AWS stations, side-by-side figures | [ctdi table I reconstruction.md](reports/ctdi%20table%20I%20reconstruction.md)<br>[ctdi traffic variable verification.md](reports/ctdi%20traffic%20variable%20verification.md)<br>[ctdi channel reconstruction.md](reports/ctdi%20channel%20reconstruction.md) | [2026-09-13.md](checkpoints/2026-09-13.md) |
| **2** | **Reconstructed Hong Kong Dataset & Provenance** | **[Dataset Provenance & Specifications.md](dataset/Dataset%20Provenance%20&%20Specifications.md)** | End-to-end chain of custody, 16 stations, ERA5 surface meteorology, TD traffic extraction | [Phase 1 - Source-Specific Cleaning Report.md](reports/Phase%201%20-%20Source-Specific%20Cleaning%20Report.md)<br>[Raw Data Availability & Verification.md](reports/Raw%20Data%20Availability%20&%20Verification.md)<br>[Raw Data Integrity Manifest.md](dataset/Raw%20Data%20Integrity%20Manifest.md) | [2026-09-13.md](checkpoints/2026-09-13.md)<br>[2026-09-17_phase_1_1.md](checkpoints/2026-09-17_phase_1_1.md) |
| **3** | **CTDI vs. Our Reconstruction Divergence** | **[CTDI Consistency & Divergence Matrix](dataset/CTDI%20Dataset%20Consistency%20Matrix.md)** | Variable-by-variable comparison, visibility vs rainfall rationale, traffic speed & congestion | [Visibility Data Recovery & Provenance Report.md](reports/Visibility%20Data%20Recovery%20&%20Provenance%20Report.md)<br>[ctdi source fidelity report.md](reports/ctdi%20source%20fidelity%20report.md) | [2026-09-13.md](checkpoints/2026-09-13.md)<br>[Dataset Decisions.md](decisions/Dataset%20Decisions.md) |
| **4** | **Air Quality Monitoring Network** | **[Station Inventory & Spatial Network.md](dataset/Station%20Inventory%20&%20SpatialNetwork.md)** | 16 EPD monitoring stations (13 ambient, 3 roadside), GPS coordinates, sensor heights | [CTDI Dataset Description.md](reports/CTDI%20Dataset%20Description.md)<br>[Cleaning, Translation & Validation Rules.md](preprocessing/Cleaning,%20Translation%20&%20Validation%20Rules.md) | [2026-09-13.md](checkpoints/2026-09-13.md) |
| **5** | **Temporal Coverage & Calendar Accounting** | **[Temporal Coverage & Calendar Accounting.md](dataset/Temporal%20Coverage%20&%20Calendar%20Accounting.md)** | 3-year continuous timeline (2019–2021), 2020 leap year accounting, 26,304 hourly timestamps | [Raw Data Availability & Verification.md](reports/Raw%20Data%20Availability%20&%20Verification.md)<br>[Temporal Alignment & Grid Assembly.md](preprocessing/Temporal%20Alignment%20&%20Grid%20Assembly.md) | [2026-09-13.md](checkpoints/2026-09-13.md) |
| **6** | **Missingness Architecture & Empirical Distribution** | **[Missingness Architecture & Empirical Distribution.md](dataset/Missingness%20Architecture%20&%20Empirical%20Distribution.md)** | Natural missingness (55,876 missing entries; 2.6553%), diurnal calibration spikes, Figures 6–9 | [CTDI Missingness Pattern Analysis.md](reports/CTDI%20Missingness%20Pattern%20Analysis.md)<br>[figures/](figures/) | [2026-09-17.md](checkpoints/2026-09-17.md) |
| **7** | **Meteorological Reconstruction & Visibility** | **[Visibility Data Recovery & Provenance Report.md](reports/Visibility%20Data%20Recovery%20&%20Provenance%20Report.md)** | HKO 10-min visibility irrecoverability audit, physical justification for ERA5 rainfall substitution | [Data Source Inventory & Fidelity Audit.md](dataset/Data%20Source%20Inventory%20&%20Fidelity%20Audit.md)<br>[Dataset Decisions.md](decisions/Dataset%20Decisions.md) | [2026-09-13.md](checkpoints/2026-09-13.md) |
| **8** | **Traffic Dataset Extraction & Verification** | **[ctdi traffic variable verification.md](reports/ctdi%20traffic%20variable%20verification.md)** | Transport Department parent SpeedMap XML (607 links, 774k snapshots) vs rejected ATC/Dashboard | [Phase 1 - Source-Specific Cleaning Report.md](reports/Phase%201%20-%20Source-Specific%20Cleaning%20Report.md)<br>[checkpoints/2026-09-17_phase_1_1.md](checkpoints/2026-09-17_phase_1_1.md) | [2026-09-13.md](checkpoints/2026-09-13.md)<br>[2026-09-17_phase_1_1.md](checkpoints/2026-09-17_phase_1_1.md) |
| **9** | **Spatial Alignment & Network Geometry** | **[Spatial Alignment & Network Geometry.md](dataset/Spatial%20Alignment%20&%20Network%20Geometry.md)** | 16×16 Haversine distance matrix, Inverse Distance Weighting ($p=2$), link-to-station assignment | [Alignment - PY.md](reports/Alignment%20-%20PY.md)<br>[Spatial Alignment Implementation.md](preprocessing/Spatial%20Alignment%20Implementation.md) | [2026-09-13.md](checkpoints/2026-09-13.md) |
| **10** | **Spatio-Temporal Alignment (Phase 2)** | **[Phase 2 - Spatio-Temporal Alignment Report.md](reports/Phase%202%20-%20Spatio-Temporal%20Alignment%20Report.md)** | Construction of the unified Cartesian grid $\mathcal{S} \times \mathcal{T} = 420,864$ observations across 13 channels | [Phase 1 - Source-Specific Cleaning Report.md](reports/Phase%201%20-%20Source-Specific%20Cleaning%20Report.md)<br>[Temporal Alignment & Grid Assembly.md](preprocessing/Temporal%20Alignment%20&%20Grid%20Assembly.md) | [2026-09-17_phase_2.md](checkpoints/2026-09-17_phase_2.md) |
| **11** | **Data Preprocessing Engineering** | **[Data Processing - Hong Kong.md](reports/Data%20Processing%20-%20Hong%20Kong.md)** | Monolithic 454-line end-to-end data processing guide from raw archives to tensor structures | [Data Preprocessing/](reports/Data%20Preprocessing/) (10 modular chapters)<br>[preprocessing/README.md](preprocessing/README.md) | [Phase 1.md](reports/Phase%201.md)<br>[Phase 2.md](reports/Phase%202.md) |
| **12** | **Generative Model Architecture** | **[System Architecture.md](architecture/System%20Architecture.md)** | End-to-end architecture: SLM context encoder, conditional diffusion backbone, temporal/spatial prior | [SLM Context Encoder.md](architecture/SLM%20Context%20Encoder.md)<br>[Conditional Diffusion Model.md](architecture/Conditional%20Diffusion%20Model.md)<br>[Temporal Denoising Model.md](architecture/Temporal%20Denoising%20Model.md) | [MASTER_RESEARCH_DOCUMENT.md](MASTER_RESEARCH_DOCUMENT.md) |
| **13** | **Experimental Protocols & Benchmarks** | **[Experimental Training Protocol.md](experiments/Experimental%20Training%20Protocol.md)** | Train/Val/Test splits (2019-2020 train, 2021 test), MCAR & block missingness masks, baselines | [Baseline Imputation Models.md](experiments/Baseline%20Imputation%20Models.md)<br>[Missingness Scenarios & Benchmark Masks.md](experiments/Missingness%20Scenarios%20&%20Benchmark%20Masks.md)<br>[Evaluation Metrics.md](experiments/Evaluation%20Metrics.md) | [Ablation Study Plan.md](experiments/Ablation%20Study%20Plan.md) |
| **14** | **Methodological Decisions (ADRs)** | **[decisions/README.md](decisions/README.md)** | Master Architectural and Methodological Decision Register tracking status of all scientific choices | [Dataset Decisions.md](decisions/Dataset%20Decisions.md)<br>[Architecture Decisions.md](decisions/Architecture%20Decisions.md)<br>[Preprocessing Decisions.md](decisions/Preprocessing%20Decisions.md) | Checkpoints |
| **15** | **Scientific Findings & Limitations** | **[Confirmed Research Findings.md](findings/Confirmed%20Research%20Findings.md)** | Empirically verified findings with exact citations, known physical boundaries, and negative findings | [Negative Findings & Dead Ends.md](findings/Negative%20Findings%20&%20Dead%20Ends.md)<br>[Living Unresolved Questions.md](findings/Living%20Unresolved%20Questions.md)<br>[Research Boundaries & Limitations.md](findings/Research%20Boundaries%20&%20Limitations.md) | Checkpoints |

---

## 3. Fast Navigation: The 15 Core Questions

Need an immediate answer? Open **exactly one document** listed below:

| # | Question | Single Document to Open | Section / Key Finding |
| :-: | :--- | :--- | :--- |
| **1** | **What exactly did CTDI use as its dataset?** | [CTDIDataset Specifications.md](dataset/CTDIDataset%20Specifications.md) | §1–4: Summary Table, 16 AQ stations, 47 HKO stations, 607 roads |
| **2** | **What are CTDI's 13 channels?** | [CTDIDataset Specifications.md](dataset/CTDIDataset%20Specifications.md) | §4: 13 Channels Decomposition Table (5 AQ, 6 Met, 2 Traffic) |
| **3** | **What did CTDI use for traffic?** | [CTDIDataset Specifications.md](dataset/CTDIDataset%20Specifications.md) | §3: 607 road links from Transport Department `speedmap.xml` |
| **4** | **What did CTDI use for meteorology?** | [CTDIDataset Specifications.md](dataset/CTDIDataset%20Specifications.md) | §2: 47 HKO automatic weather stations (10-min), including visibility |
| **5** | **What is known about CTDI visibility?** | [Dataset Provenance & Specifications.md](dataset/Dataset%20Provenance%20&%20Specifications.md) | §4: Irrecoverability audit & ERA5 rainfall substitution rationale |
| **6** | **What data did we actually recover?** | [Dataset Provenance & Specifications.md](dataset/Dataset%20Provenance%20&%20Specifications.md) | §2–5: 16 AQ stations, ERA5 surface met, 36-mo SpeedMap XML |
| **7** | **What are the differences between CTDI and our reconstruction?** | [CTDIDataset Specifications.md](dataset/CTDIDataset%20Specifications.md) | §5: Explicit Comparative Divergence Table |
| **8** | **What are our 16 stations?** | [Station Inventory & Spatial Network.md](dataset/Station%20Inventory%20&%20Spatial%20Network.md) | §1–2: 13 ambient + 3 roadside stations, lat/lon, heights |
| **9** | **What is our temporal coverage?** | [Temporal Coverage & Calendar Accounting.md](dataset/Temporal%20Coverage%20&%20Calendar%20Accounting.md) | §1: 2019-01-01 to 2021-12-31 (1,096 days, 26,304 continuous hours) |
| **10** | **What is our natural missingness?** | [Missingness Architecture & Empirical Distribution.md](dataset/Missingness%20Architecture%20&%20Empirical%20Distribution.md) | §2: 55,876 entries (2.6553%), diurnal peaks at 01:00, 20% parity |
| **11** | **What preprocessing has been completed?** | [Data Processing - Hong Kong.md](reports/Data%20Processing%20-%20Hong%20Kong.md) | §1: Full end-to-end data pipeline from raw to tensors |
| **12** | **What traffic processing has been completed?** | [Phase 1 - Source-Specific Cleaning Report.md](reports/Phase%201%20-%20Source-Specific%20Cleaning%20Report.md) | §3: 36 monthly partitions, 774,686 snapshots, 466M records |
| **13** | **What decisions have been made?** | [decisions/README.md](decisions/README.md) | Comprehensive ADR Register with status badges |
| **14** | **Why are we using rainfall instead of visibility?** | [Dataset Provenance & Specifications.md](dataset/Dataset%20Provenance%20&%20Specifications.md) | §4: Physical justification & meteorological wet-deposition coupling |
| **15** | **What is the current project status?** | [research_status.md](research_status.md) | Operational status, Phase 2 completion, and next starting point |

---

## 4. Curated Directory Architecture

The `research/` directory is organized into 10 intentional categories. All files feature human-readable titles:

```text
research/
├── MASTER_RESEARCH_DOCUMENT.md             # Living comprehensive thesis/research specification
├── Obsidian Figure Template.md             # Standard Obsidian template for multi-figure visual layouts
├── README.md                               # This file: navigation, topic maps, and documentation protocol
├── research_status.md                      # High-level operational status dashboard
├── research_timeline.md                    # Chronological record of milestones and shifts
│
├── architecture/                           # Deep generative and language model design
│   ├── README.md                           # Architecture index and component interaction map
│   ├── Conditional Diffusion Model.md      # DDPM backbone, noise schedules, reverse diffusion
│   ├── Conditioning Mechanism.md           # Cross-attention / AdaLN integration of SLM context
│   ├── Loss Functions & Objectives.md      # Denoising MSE, context consistency, physics regularizers
│   ├── SLM Context Encoder.md              # Atmospheric prompt generation and language model encoding
│   ├── Spatial Model Prior.md              # GCN / spatial attention over 16-station distance graph
│   ├── System Architecture.md              # End-to-end architecture unifying SLM, spatial, and temporal layers
│   └── Temporal Denoising Model.md         # Transformer / temporal attention denoising architecture
│
├── checkpoints/                            # Immutable chronological daily research logs
│   ├── README.md                           # Checkpoint rules, protocol, and daily template
│   ├── 2026-09-13.md                       # Initial benchmark audit, Table I discovery, traffic audit
│   ├── 2026-09-14.md                       # Phase 1 planning and data verification
│   ├── 2026-09-17.md                       # Empirical missingness pattern analysis replication
│   ├── 2026-09-17_phase_1_1.md             # Phase 1.1 Complete Traffic Data Extraction (774k snapshots)
│   └── 2026-09-17_phase_2.md               # Phase 2 Spatio-Temporal Alignment & 13-Channel Dataset
│
├── dataset/                                # Dataset specifications, ground truth, and provenance
│   ├── README.md                           # Dataset documentation index and topic map
│   ├── CTDIDataset Specifications.md       # PRIMARY: CTDI paper benchmark, Table I, 13 channels, figures
│   ├── Dataset Provenance & Specifications.md # PRIMARY: Reconstructed HK dataset, custody chain, SHA-256
│   ├── Missingness Architecture & Empirical Distribution.md # PRIMARY: Theory and empirical analysis
│   ├── Station Inventory & Spatial Network.md # PRIMARY: 16 monitoring stations, GPS coords, metadata
│   ├── Temporal Coverage & Calendar Accounting.md # PRIMARY: 26,304 hours, leap year, grid continuity
│   ├── Spatial Alignment & Network Geometry.md # PRIMARY: 16x16 distance matrix, IDW spatial mapping
│   ├── Canonical Dataset Definition.md     # Mathematical tensor formulation [16, 26304, 13]
│   ├── CTDI 13-Channel Specification.md    # Detailed specification of the 13 feature channels
│   ├── CTDI Dataset Consistency Matrix.md  # Detailed feature-by-feature divergence comparison
│   ├── Data Source Inventory & Fidelity Audit.md # Source-by-source availability, endpoints, licenses
│   ├── Raw Data Integrity Manifest.md      # File listings, row counts, and checksum verification
│   ├── air - missing by hour year.png      # CTDI Paper Fig 6 reference screenshot
│   ├── air - pollutant by missing.png      # CTDI Paper Fig 8 reference screenshot
│   ├── air - pollution hour vs missing.png # CTDI Paper Fig 7 reference screenshot
│   └── air - station vs missing.png        # CTDI Paper Fig 9 reference screenshot
│
├── decisions/                              # Formal Architectural and Methodological Decision Records
│   ├── README.md                           # Master ADR register and decision matrix
│   ├── Architecture Decisions.md           # SLM conditioning, AdaLN, diffusion backbone choices
│   ├── Dataset Decisions.md                # 13 channels, zero synthetic data, rainfall substitution
│   ├── Experimental Decisions.md           # Missingness scenarios, evaluation metrics, baselines
│   └── Preprocessing Decisions.md          # Spatial IDW (p=2), coordinate anchoring, zero leakage
│
├── experiments/                            # Experimental protocols, evaluations, and benchmarks
│   ├── README.md                           # Experiments overview and testing roadmap
│   ├── Ablation Study Plan.md              # Systematic ablation matrix (SLM prompt, loss terms)
│   ├── Baseline Imputation Models.md       # Traditional, deep autoregressive, and generative baselines
│   ├── Cross-Dataset Evaluation.md         # Generalization evaluation protocol on external benchmarks
│   ├── Evaluation Metrics.md               # MAE, RMSE, MAPE, CRPS, Prediction Interval Coverage
│   ├── Experimental Training Protocol.md   # Train/val/test splits, optimization schedule, random seeds
│   └── Missingness Scenarios & Benchmark Masks.md # MCAR, block temporal, and spatial outage masks
│
├── figures/                                # High-resolution programmatically generated figures
│   ├── fig_06_missing_by_hour_year.png     # Empirical missingness by hour across 2019-2021
│   ├── fig_07_missing_proportion_by_hour_pie.png # Diurnal missingness distribution (Hour 1 peak)
│   ├── fig_08_missing_proportion_by_pollutant_pie.png # Pollutant missingness parity (~20% each)
│   └── fig_09_missing_proportion_by_station_pie.png # Station missingness distribution across 16 stations
│
├── findings/                               # Evidence-backed research results and boundaries
│   ├── README.md                           # Index of scientific findings and evidence classification
│   ├── Confirmed Research Findings.md      # Empirically verified findings with exact citations
│   ├── Living Unresolved Questions.md      # Active open research questions and investigation steps
│   ├── Negative Findings & Dead Ends.md    # Formally documented approaches that failed and why
│   └── Research Boundaries & Limitations.md # Physical, computational, and archival boundary constraints
│
├── literature/                             # Literature reviews and theoretical foundation
│   ├── README.md                           # Overview of literature corpus and taxonomies
│   ├── CTDI Paper Exhaustive Analysis.md   # Line-by-line critical breakdown of Yu et al. (IEEE TBD 2025)
│   ├── Related Imputation Methods.md       # Survey of CSDI, SAITS, BRITS, PriSTI, NAOMI, VAE models
│   └── SLM-Conditioned Diffusion Research.md # Small Language Model conditioning in physical domains
│
├── preprocessing/                          # Implementation details of the preprocessing pipeline
│   ├── README.md                           # Preprocessing pipeline guide and execution order
│   ├── Cleaning, Translation & Validation Rules.md # Header standardization, bilingual sanitization
│   ├── Data Quality Assurance Playbook.md  # Numerical assertion suites and sanity test protocols
│   ├── Feature Engineering & Encodings.md  # Cyclical time encodings (sin/cos hour, day, month)
│   ├── Normalization & Zero-Leakage Protocol.md # MinMax scaling fit strictly on Train split (2019-2020)
│   ├── Raw Data Ingestion Protocol.md      # Parsing schemas and raw archive extraction methods
│   ├── Spatial Alignment Implementation.md # Nearest neighbor and IDW spatial mapping algorithms
│   └── Temporal Alignment & Grid Assembly.md # Cartesian grid generation and chronological sorting
│
└── reports/                                # Empirical investigation reports, execution logs & handbooks
    ├── README.md                           # Index of reports, execution logs, and archival analyses
    ├── Alignment - PY.md                   # Execution log of alignment pipeline and safety halt
    ├── CTDI Dataset Description.md         # Comprehensive background dataset documentation (2026-09-12)
    ├── CTDI Missingness Pattern Analysis.md # Detailed empirical analysis replicating Figures 6–9
    ├── Data Processing - Hong Kong.md      # 454-line comprehensive data engineering handbook
    ├── Phase 1.md                          # Phase 1 raw data verification execution log
    ├── Phase 1 - Source-Specific Cleaning Report.md # Source-specific cleaning & Phase 1.1 traffic extraction
    ├── Phase 2.md                          # Early Phase 2 spatial alignment and tensor plan (historical)
    ├── Phase 2 - Spatio-Temporal Alignment Report.md # Phase 2 completion report: 420k row Cartesian grid
    ├── Raw Data Availability & Verification.md # Initial raw download availability and physical checks
    ├── Visibility Data Recovery & Provenance Report.md # HKO AWS visibility irrecoverability audit
    ├── ctdi channel reconstruction.md      # 13-channel specification and code divergence analysis
    ├── ctdi source fidelity report.md      # Source data fidelity compared against published citations
    ├── ctdi table I reconstruction.md      # Exact reproduction and analytical breakdown of CTDI Table I
    ├── ctdi traffic variable verification.md # Candidate traffic variable evidence matrix & 607-link proof
    └── Data Preprocessing/                 # 10-chapter modular data engineering guides (Chapters 00–09)
```

---

## 5. Documentation Philosophy & Evidence Discipline

To guarantee scientific rigor, every research document strictly adheres to four foundational rules:

1. **Explicit Epistemic Status**: Every assertion is tagged with an epistemic label:
   - `[VERIFIED]`: Directly proven by paper text, official dataset, or empirical test.
   - `[OBSERVED]`: Measured empirically from raw files or execution output.
   - `[IMPLEMENTED]`: Code exists, executes, and produces validated output.
   - `[PROPOSED]`: Planned methodology not yet implemented.
   - `[ASSUMPTION]`: Working hypothesis required for progress, pending confirmation.
   - `[FAILED]`: Tested and proven unviable or incorrect.
   - `[BLOCKED]`: Cannot proceed due to missing external data or unresolved prerequisite.
   - `[SUPERSEDED]`: Previously held assumption overturned by newer evidence.
2. **Zero Fabrication & Immutability**: No synthetic data may ever be injected into real benchmark channels. All transformations are mathematically transparent, deterministic, and logged.
3. **Preservation of Failures**: Negative findings and dead ends are primary research assets. They are preserved in `findings/Negative Findings & Dead Ends.md` so that flawed hypotheses are never repeated.
4. **Separation of Living Truth vs. Historical Logs**:
   - Primary topic notes in `dataset/`, `architecture/`, and `MASTER_RESEARCH_DOCUMENT.md` record current consolidated knowledge.
   - `checkpoints/` and execution logs in `reports/` remain immutable chronological records of each session.
"""

with open("research/README.md", "w") as f:
    f.write(readme_content)
print("Updated research/README.md successfully.")
