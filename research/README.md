# Research Documentation & Checkpoint Repository

**Project**: Context-Aware Generative Imputation of Air Pollution Using SLM-Conditioned Diffusion  
**Core Benchmark**: Yu et al., *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, **IEEE Transactions on Big Data**, vol. 11, no. 5, pp. 2442–2455, Sept.–Oct. 2025.  
**Target Domain**: Hong Kong SAR (16 stations × 26,304 hours × 13 channels; 2019-01-01 00:00 to 2021-12-31 23:00)  
**Current Date**: 13 September 2026  
**Current Project Status**: Work intentionally paused for today; documentation, audit, and checkpoint freeze.

---

## 1. Start Here

If you are a researcher, engineer, or collaborator joining or resuming this project, review documents in the following order:

1. **[Master Research Document](MASTER_RESEARCH_DOCUMENT.md)**: The single living master document containing the complete, consolidated scientific understanding, dataset definition, architecture, literature foundation, findings, and current stopping point.
2. **[Research Status Dashboard](research_status.md)**: High-level table tracking the verified status, blockers, and remaining work for all project components.
3. **[Research Timeline](research_timeline.md)**: Chronological evolution of scientific milestones and decisions.
4. **[Latest Daily Checkpoint](checkpoints/2026-09-13.md)**: The exact work, findings, and next starting point from the most recent session (2026-09-13).
5. **[Confirmed Findings](findings/confirmed_findings.md)** & **[Negative Findings](findings/negative_findings.md)**: What was empirically proven true, and critical dead ends that must not be repeated.
6. **[Methodological Decisions](decisions/README.md)**: Formal decision records (ADRs) explaining key scientific and architectural choices.

---

## 2. Directory Architecture

The `research/` directory is structured modularly to ensure complete traceability, auditability, and reproducibility:

```text
research/
│
├── README.md                               # This file: navigation and documentation protocol
├── MASTER_RESEARCH_DOCUMENT.md             # Living comprehensive thesis/research specification
├── research_status.md                      # High-level operational status dashboard
├── research_timeline.md                    # Chronological record of milestones and shifts
│
├── decisions/                              # Formal Architectural and Methodological Decision Records
│   ├── README.md                           # Index of decisions and decision framework
│   ├── dataset_decisions.md                # 13 channels, zero synthetic data, train-only normalization
│   ├── architecture_decisions.md           # SLM conditioning, context vector z_C, diffusion backbone
│   ├── preprocessing_decisions.md          # Spatial IDW (p=2), coordinate anchoring, missingness
│   └── experimental_decisions.md           # Missingness scenarios, evaluation metrics, baselines
│
├── literature/                             # Literature reviews and theoretical foundation
│   ├── README.md                           # Overview of literature corpus
│   ├── ctdi_paper_analysis.md              # Exhaustive breakdown of Yu et al. (IEEE TBD 2025)
│   ├── slm_conditioned_diffusion_research.md # Small Language Model conditioning for generative models
│   └── related_methods.md                  # CSDI, SAITS, BRITS, PriSTI, NAOMI, VAE baselines
│
├── dataset/                                # Target and raw dataset specifications
│   ├── README.md                           # Dataset documentation index
│   ├── dataset_definition.md               # Canonical tensor [16, 26304, 13] formulation
│   ├── source_inventory.md                 # EPD, HKO, TD source fidelity and access endpoints
│   ├── station_inventory.md                # 16 included stations, 2 excluded stations (Southern, North)
│   ├── channel_definition.md               # Exact 13 channels (5 pollutants, 6 weather, 2 traffic)
│   ├── temporal_coverage.md                # 3 full calendar years, 2020 leap year, 26,304 hours
│   ├── spatial_alignment.md                # IDW spatial interpolation (w_ij = 1/d_ij^2)
│   ├── missingness_analysis.md             # Natural missingness (~2.5%) vs simulated evaluation masks
│   └── provenance.md                       # Cryptographic hashes, file sizes, and reproducibility logs
│
├── preprocessing/                          # Implementation details of the preprocessing pipeline
│   ├── README.md                           # Preprocessing pipeline guide
│   ├── ingestion.md                        # Raw data parsing and schema harmonization
│   ├── cleaning_and_validation.md          # Header standardization, 24h convention, NaN sanitization
│   ├── temporal_alignment.md               # Cartesian grid generation and chronological sorting
│   ├── spatial_alignment.md                # Spatial IDW mapping of meteorology and traffic to stations
│   ├── feature_engineering.md              # Cyclical time encodings (hour, day-of-week, month)
│   ├── normalization.md                    # Zero-data-leakage scaling (fit on Train split ONLY)
│   └── data_quality_assurance.md           # Verification playbook and numerical assertion suites
│
├── architecture/                           # Deep generative and language model design
│   ├── README.md                           # Architecture index
│   ├── system_architecture.md              # End-to-end SLM-Conditioned Diffusion pipeline
│   ├── context_encoder.md                  # Synoptic atmospheric prompt generation & SLM encoding
│   ├── diffusion_model.md                  # Conditional denoising diffusion probabilistic model (DDPM)
│   ├── temporal_model.md                   # Temporal attention / Transformer denoising layers
│   ├── spatial_model.md                    # Spatial graph / GCN / CNN spatial dependency layers
│   ├── conditioning_mechanism.md           # Cross-attention / adaptive layer norm (AdaLN) conditioning
│   └── loss_functions.md                   # Denoising MSE, context consistency, physics regularizers
│
├── experiments/                            # Experimental protocols, evaluations, and benchmarks
│   ├── README.md                           # Experiments overview
│   ├── experimental_protocol.md            # Train/val/test splits, random seeds, training schedules
│   ├── baselines.md                        # Mean, Linear/Spline, KNN, GRU/LSTM, BRITS, VAE, CSDI, CTDI
│   ├── missingness_scenarios.md            # MCAR, Continuous temporal block, Spatial station outages
│   ├── evaluation_metrics.md               # MAE, RMSE, MAPE, CRPS, Prediction Interval Coverage (PICP)
│   ├── ablation_plan.md                    # Ablation matrix: SLM impact, loss components, noise schedules
│   └── cross_dataset_evaluation.md         # External validation (e.g., Beijing / Air-Quality benchmarks)
│
├── findings/                               # Evidence-backed research results and boundaries
│   ├── README.md                           # Index of scientific findings
│   ├── confirmed_findings.md               # Empirically verified findings with direct citations
│   ├── negative_findings.md                # Tested approaches that failed or dead ends to avoid
│   ├── unresolved_questions.md             # Living open questions with next investigative steps
│   └── research_limitations.md             # Physical, computational, and archival boundary limitations
│
├── checkpoints/                            # Immutable chronological daily research logs
│   ├── README.md                           # Checkpoint rules and format specifications
│   ├── 2026-09-13.md                       # Today's checkpoint: Table I discovery, traffic audit, freeze
│   └── ...                                 # Future dated checkpoints (YYYY-MM-DD.md)
│
└── reports/                                # Raw investigation reports, execution logs, and reproductions
    ├── README.md                           # Reports catalog
    ├── ctdi_table_i_reconstruction.md      # Exact reproduction and analytical breakdown of CTDI Table I
    ├── ctdi_traffic_variable_verification.md # Candidate variable evidence matrix & 607-link proof
    ├── ctdi_channel_reconstruction.md      # 13-channel specification & divergence resolution
    ├── Alignment - PY.md                   # Alignment pipeline verification log & traffic safety halt
    ├── Phase 1.md                          # Phase 1 raw verification report (Air, Met, ATC)
    ├── Phase 2.md                          # Phase 2 spatial alignment & canonical tensor plan
    ├── CTDI Dataset Description.md         # Comprehensive background dataset documentation
    ├── Data Processing - Hong Kong.md      # 454-line complete data processing reference guide
    └── Data Preprocessing/                 # 10-part modular data engineering guides (00 to 09)
```

---

## 3. Documentation Philosophy & Evidence Discipline

To maintain research rigor, every document adheres to the following principles:

1. **Strict Evidence Labeling**: Every statement of fact must carry an explicit epistemic status:
   - `[VERIFIED]`: Directly proven by paper text, official dataset, or empirical test.
   - `[OBSERVED]`: Measured empirically from raw files or execution output.
   - `[IMPLEMENTED]`: Code exists, executes, and produces validated output.
   - `[PROPOSED]`: Planned methodology not yet implemented.
   - `[ASSUMPTION]`: Working hypothesis required for progress, pending external confirmation.
   - `[FAILED]`: Tested and proven unviable or incorrect.
   - `[BLOCKED]`: Cannot proceed due to missing external data or unresolved prerequisite.
   - `[SUPERSEDED]`: Previously held assumption overturned by newer evidence.
2. **Zero Fabrication / Zero Silent Changes**: No synthetic data may ever be injected into real benchmark channels. All imputations, scalings, and transformations must be logged with input, output, and physical rationale.
3. **Preservation of Failures**: Negative findings and dead ends are primary research results. Never delete or conceal an approach that failed.
4. **Separation of Living Truth vs. Historical Log**:
   - `MASTER_RESEARCH_DOCUMENT.md` records current consolidated knowledge.
   - `checkpoints/YYYY-MM-DD.md` records historical daily sessions and is immutable once written.

---

## 4. Automatic Documentation Protocol

**MANDATORY RULE**: Documentation must be updated **before** any research or implementation task is marked complete.

Whenever a meaningful event occurs:
- **Success** (dataset verified, parser implemented, assertion passed): Update the relevant module, update `research_status.md`, record in the daily checkpoint, and update the master document if scientific understanding shifts.
- **Failure** (schema mismatch, missing archive, validation error): Document in `findings/negative_findings.md`, note why it failed, whether it can be retried, and record in the daily checkpoint.
- **Discovery** (corrected channel, newly discovered paper table): Update `MASTER_RESEARCH_DOCUMENT.md`, `research_timeline.md`, and relevant module docs.
- **Decision** (source selected, channel altered, model layer chosen): Create or update a record in `decisions/`.
- **Blocker** (missing archive, hardware bottleneck): Update `research_status.md` and `findings/unresolved_questions.md`.
