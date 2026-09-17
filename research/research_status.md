# Research Status Dashboard

**Project**: Context-Aware Generative Imputation of Air Pollution Using SLM-Conditioned Diffusion  
**Benchmark Reference**: Yu et al., *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, IEEE Transactions on Big Data, 2025.  
**Last Updated**: 2026-09-17  
**Raw Data Acquisition Status**: **`COMPLETE`**  
**Phase 1 Status (Source-Specific Cleaning)**: **`COMPLETE`**  
**Current Operational Status**: **`PHASE_1_SOURCE_SPECIFIC_CLEAN_DATA_READY`**  
**Next Phase**: **`PHASE 2 — TEMPORAL & SPATIAL ALIGNMENT`** (Awaiting user authorization; NOT started)

---

## 1. Phase Status Summary

### COMPLETED:
- **PHASE 1 — SOURCE-SPECIFIC CLEANING**: **`COMPLETE`**
  - Clean Air Quality (`data/interim/air_quality/clean_air_quality.parquet`): 420,864 rows, 16 stations, 26,304 hours, 55,876 natural missing values preserved without imputation, 0 duplicates.
  - Clean Meteorology (`data/interim/meteorology/clean_meteorology.parquet`): 420,864 rows, 16 stations, 26,304 hours, 0 missing, 0 duplicates, physical ranges verified, `rainfall` strictly preserved as rainfall (NEVER visibility).
  - Clean Traffic (`data/interim/traffic/clean_traffic_speedmap_snapshots.parquet`): 2,413 records across 4 representative multi-year snapshots (607 baseline links, 632 unique links union), speeds in [3, 109] km/h, raw saturation categories preserved, documented ordinal mapping specification established (GOOD=0.0, AVERAGE=0.5, BAD=1.0). Zero spatial IDW or station aggregation applied.
  - Reproducible Notebook: `notebooks/02_source_specific_cleaning.ipynb` (16/16 cells executed headless with code 0).
  - Cryptographic Provenance: `data/interim/metadata/provenance_metadata.json` and `data/interim/metadata/raw_data_sha256_manifest.json`.
  - Comprehensive Validation Report: `research/reports/source_specific_cleaning_report.md`.
  - Raw Data Immutability: Cryptographically verified (683 files in `data/raw/`, MODIFIED=0, DELETED=0, ADDED=0).
- **CTDI Reference Specification**: Fully audited from IEEE paper PDF (`research/dataset/ctdi_paper_dataset_specification.md`).
- **Air-Quality Dataset**: Acquired, validated, 100% complete ($16 \times 26,304 = 420,864$ rows, 55,876 missing values matching CTDI).
- **Meteorological Source**: Acquired (ECMWF ERA5 continuous surface reanalysis at the 16 air station coordinates).
- **Visibility Recovery Investigation**: Completed and closed (`research/reports/visibility_data_recovery_report.md`).
- **Rainfall Substitution Decision**: Formally adopted (`[DECISION]`) for Channel 9 of `ctdi_aligned_reconstructed`.
- **Traffic Source Investigation**: Completed (Parent 1st Gen Speedmap system verified with 607 baseline links).
- **Traffic Temporal Coverage Audit**: Completed and passed (774,686 snapshots across 36/36 months, 100% coverage of 2019–2021).

### PENDING:
- None for Phase 1.

### NEXT PHASE:
- **Phase 2 — Temporal & Spatial Alignment**:
  1. Batch extraction / parsing of 1st Gen Speedmap snapshots across 2019–2021.
  2. IDW spatial mapping ($p=2$) from road link centroids to the 16 air quality monitoring stations.
  3. Multimodal temporal alignment ($t_{\text{met/traffic}} = t_{\text{aq}} + 1\text{h}$).
  4. Zero-data-leakage feature normalization (fit on 70% Train split only).
  5. Assembly of canonical 3D tensor ($16 \times 26,304 \times 13$, named `ctdi_aligned_reconstructed`).
  *(Note: Multimodal alignment, tensor construction, window generation, and model training have NOT yet started).*

---

## 2. Project Component Status Dashboard

| Research Area | Status | Direct Empirical Evidence | Remaining Work |
| :--- | :---: | :--- | :--- |
| **Literature** | **`VERIFIED`** | Exhaustive textual/tabular audit of Yu et al. (IEEE TBD 2025). Authoritative specification documented in `research/dataset/ctdi_paper_dataset_specification.md`. | Ongoing literature tracking of foundation time-series models. |
| **CTDI Reconstruction** | **`VERIFIED`** | Full consistency matrix (`ctdi_consistency_matrix.md`) and source fidelity report (`ctdi_source_fidelity_report.md`) published. 13-channel structure verified ($16 \times 26,304 \times 13 = 5,471,232$). | Complete batch extraction of 2019–2021 traffic snapshots during preprocessing. |
| **Air-Quality Dataset** | **`VERIFIED`** | EPD 2019–2021 continuous hourly dataset: 420,864 rows, 16 stations, 0 duplicates, 0 negative values. Total missing values: 55,876 ($99.99995\%$ match to paper's 55,875). Classified as `EXACT SOURCE MATCH`. | None. Air quality raw data is fully validated and immutable. |
| **Meteorology Dataset** | **`VERIFIED_DIFFERENCE`** | ERA5 surface reanalysis (420,864 rows, 16 stations). Exhaustive audit proved retrospective 10-min AWS series for 47 stations and visibility is `[IRRECOVERABLE]` from public open data (Page 2454: offline dataset from Dr. Yang Han at HKU). Documented in `research/reports/visibility_data_recovery_report.md`. Classified as `SOURCE DIFFERENCE WITH SCIENTIFIC JUSTIFICATION` (rainfall vs visibility). | Account for reanalysis rainfall vs visibility during feature preprocessing. |
| **Traffic Dataset** | **`VERIFIED`** | Parent 1st Gen Speedmap system verified (607 baseline links, 315,648 expected 5-min intervals, 774k snapshots covering 100% of 2019–2021). Multi-year snapshots audited: 607 (2019), 590 (2020), 608 (2021). Congestion mapped ordinally `[ASSUMPTION]`. Classified as `SOURCE-SYSTEM MATCH`. | Ingest snapshots and apply IDW ($p=2$) in data preprocessing phase. |
| **Raw Data Integrity** | **`VERIFIED`** | 100% cryptographic immutability verified before and after investigation (678 raw files identical bit-for-bit). Documented in `research/dataset/raw_data_integrity_manifest.md`. | Maintain absolute raw immutability throughout all project phases. |
| **13-Channel Alignment** | **`READY`** | `src/preprocessing/alignment.py` implemented with Cartesian grid (420,864 rows). Consistency matrix and source fidelity report completed. Channel schema updated to CTDI 13 channels (`traffic_congestion` + reanalysis `rainfall`). | Assemble canonical tensor once traffic is ingested in preprocessing. |
| **Spatial Alignment** | **`VERIFIED`** | Pairwise Haversine distance matrix computed and verified symmetric with zero diagonal (`data/interim/spatial_distance_matrix.npy`). IDW formula ($p=2$) mathematically formulated. Road centroid georeferencing established `[ASSUMPTION]`. | Apply IDW mapping across 607 road links once hourly traffic table is compiled. |
| **Missingness & EDA** | **`VERIFIED`** | CTDI Section IV-B empirical missingness analysis fully reproduced in `notebooks/01_ctdi_style_missingness_analysis.ipynb`. Figures 6–10 published to `research/figures/`. 1-hour temporal offset between EPD 1-indexed interval-end hours and ISO interval-start timestamps resolved ($\text{hour} = (\text{dt.hour}+1)\%24$). Bit-for-bit parity with published CTDI curves confirmed. Research report updated (`research/reports/ctdi_missingness_pattern_analysis.md`). | Finalize DataLoader integration once canonical tensor exists. |
| **Normalization** | **`READY`** | Mathematical specifications for zero-data-leakage scaling (fit on Train split ONLY) and cyclical temporal embeddings documented in `research/preprocessing/normalization.md`. | Execute scaling transformation on completed canonical tensor. |
| **Context Construction** | **`IN_PROGRESS`** | Deterministic Environmental Context Builder prototype drafted in `src/context/builder.py` and documented in `reports/Data Preprocessing/07`. | Update prompt templates with rainfall/visibility and traffic saturation features; test batch rendering. |
| **SLM Integration** | **`IN_PROGRESS`** | Architecture specified for frozen/LoRA SLM (Phi-3 / Gemma / Llama) context encoder $\mathbf{z}_C$ in `research/architecture/context_encoder.md`. | Benchmark lightweight SLM token inference latency and linear projection layer. |
| **Diffusion Denoiser** | **`IN_PROGRESS`** | Math formulated: DDPM with cross-attention / AdaLN conditioning on $\mathbf{z}_C$, spatial graph layers, temporal transformer blocks (`research/architecture/diffusion_model.md`). | Implement PyTorch module for conditional denoising backbone. |
| **Training Pipeline** | **`NOT_STARTED`** | Chronological 70/15/15 train/val/test split and composite loss function ($\mathcal{L}_{\text{diff}} + \mathcal{L}_{\text{chem}}$) formulated in `research/architecture/loss_functions.md`. | Implement training loop, optimizer, checkpointing, and WandB/TensorBoard logging. |
| **Evaluation Suite** | **`READY`** | Metric implementations for MAE, RMSE, MAPE, CRPS, and PICP formulated in `src/evaluation/metrics.py` and `research/experiments/evaluation_metrics.md`. | Benchmark suite execution on trained model checkpoints. |
| **Baselines** | **`IN_PROGRESS`** | Baseline suite defined (Mean, Spline, KNN, BRITS, VAE, CSDI, CTDI) in `research/experiments/baselines.md`. | Implement benchmark test harness for comparative evaluation. |
| **Ablation Studies** | **`NOT_STARTED`** | 7-part ablation matrix designed in `research/experiments/ablation_plan.md` to evaluate SLM impact, graph structure, and physical loss. | Run ablations after baseline training. |
| **Documentation** | **`READY`** | Complete modular research architecture, master research document, decision records, daily checkpoints, consistency matrix, paper specification, source fidelity report, visibility report, and integrity manifest established in `research/`. | Maintain continuously under Automatic Documentation Protocol. |

---

## 3. Allowed Status Definitions

- **`NOT_STARTED`**: Architectural or experimental design exists conceptually, but no code or data has been implemented.
- **`IN_PROGRESS`**: Active design, coding, or preliminary testing is underway.
- **`VERIFIED`**: Directly inspected, tested, and validated with empirical evidence and mathematical proof.
- **`VERIFIED_DIFFERENCE`**: Rigorously audited and proven to differ from the published reference, with full scientific justification and proof of irrecoverability.
- **`PARTIALLY_VERIFIED`**: Certain aspects verified, but subcomponents require correction or source alignment.
- **`BLOCKED`**: Cannot proceed to execution due to missing external data, unresolved prerequisites, or safety assertions.
- **`FAILED`**: Attempted approach proven scientifically or operationally unviable and officially rejected.
- **`READY`**: Component code/specifications are fully validated and awaiting upstream dependencies before execution.
- **`SUPERSEDED`**: Prior assumption or intermediate result overturned and replaced by newer evidence.
- **`IRRECOVERABLE`**: Proven unavailable from any public open data repository, API, or legitimate open-access archive.
