# Research Status Dashboard

**Project**: Context-Aware Generative Imputation of Air Pollution Using SLM-Conditioned Diffusion  
**Benchmark Reference**: Yu et al., *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, IEEE Transactions on Big Data, 2025.  
**Last Updated**: 2026-09-17  
**Raw Data Acquisition Status**: **`COMPLETE`**  
**Phase 1 Status (Source-Specific Cleaning & Full Extraction)**: **`COMPLETE`**  
- `TRAFFIC SOURCE ACQUISITION`: **`COMPLETE`**  
- `TRAFFIC SOURCE VALIDATION`: **`COMPLETE`**  
- `TRAFFIC FULL EXTRACTION`: **`COMPLETE`** ($774,686$ snapshots, $466,829,497$ records across $36$ months)  
**Phase 2 Status (Temporal & Spatial Alignment)**: **`COMPLETE`**  
- `TEMPORAL & SPATIAL ALIGNMENT`: **`COMPLETE`** ($420,864$ station-hours, $16$ stations $\times$ $26,304$ hours, $13$ canonical channels)  
- `NATURAL AQ MISSINGNESS CONSERVATION`: **`COMPLETE`** ($55,876$ NaNs preserved bit-for-bit)  
- `METEOROLOGY COMPLETENESS`: **`COMPLETE`** ($0$ NaNs, physical bounds verified)  
- `TRAFFIC SPATIAL RESOLUTION`: **`COMPLETE`** (IDW $p=2$ on verified links, $0$ synthetic coordinates fabricated, $0$ artificial 0 km/h fills)  
- `3D TENSOR RESHAPEABILITY`: **`VERIFIED`** ($(420864, 13) \to (16, 26304, 13)$)  
**Current Operational Status**: **`PHASE_2_ALIGNED_DATASET_READY`**  
**Next Phase**: **`PHASE 3 — 24-HOUR SLIDING WINDOW SEGMENTATION & MISSINGNESS MASK GENERATION`** (Awaiting user authorization; NOT started)

---

## 1. Phase Status Summary

### COMPLETED:
- **PHASE 1 — SOURCE-SPECIFIC CLEANING & FULL EXTRACTION**: **`COMPLETE`**
  - Clean Air Quality (`data/interim/air_quality/clean_air_quality.parquet`): 420,864 rows, 16 stations, 26,304 hours, 55,876 natural missing values preserved without imputation, 0 duplicates.
  - Clean Meteorology (`data/interim/meteorology/clean_meteorology.parquet`): 420,864 rows, 16 stations, 26,304 hours, 0 missing, 0 duplicates, physical ranges verified, `rainfall` strictly preserved as rainfall (NEVER visibility).
  - Complete Traffic Extraction (`data/interim/traffic/clean_traffic_speedmap_complete.parquet`): Complete 3-year historical archive extraction: **774,686 snapshots** processed across all 36 months, **466,829,497 records** extracted, 0 missing dates ($1,096/1,096$ calendar days present), 632 unique links in union, speeds in $[0, 111]\text{ km/h}$ (mean $57.66\text{ km/h}$), raw saturation categories preserved, documented ordinal mapping specification established (GOOD=0.0, AVERAGE=0.5, BAD=1.0). Zero spatial IDW or station aggregation applied.
- **PHASE 2 — TEMPORAL & SPATIAL ALIGNMENT**: **`COMPLETE`**
  - Aligned 13-Channel Dataset (`data/interim/aligned/aligned_hourly_station_data.parquet`): 420,864 rows $\times$ 19 columns ($6.42\text{ MB}$), exact primary grid preservation.
  - Intermediate AQ + Met (`data/interim/aligned/aligned_air_met_hourly.parquet`): 420,864 rows, 14 columns ($5.2\text{ MB}$).
  - Link-Level Traffic Aggregation (`data/interim/aligned/traffic_hourly_link_data.parquet`): 15,725,618 records across 632 links and 26,154 unique hours ($76.78\text{ MB}$).
  - Station Traffic Projection (`data/interim/aligned/traffic_station_hourly.parquet`): 418,448 rows ($2.1\text{ MB}$), 99.43% coverage, 2,416 natural archive missing hours preserved as NaN (zero 0 km/h filling).
  - Spatial Distance Matrix (`data/interim/aligned/spatial_distance_matrix.npy`): $16 \times 16$ symmetric Haversine matrix, zero diagonal.
  - Automated Validation Suite: 9/9 checks passed with 0 errors (`data/interim/aligned/alignment_validation.json`).
  - Cryptographic Raw Immutability: 100% verified across 683 files in `data/raw/` (0 modified, 0 added, 0 deleted).
- **CTDI Reference Specification**: Fully audited from IEEE paper PDF ([`CTDIDataset Specifications.md`](Dataset/CTDIDataset%20Specifications.md)).
- **Air-Quality Dataset**: Acquired, validated, 100% complete ($16 \times 26,304 = 420,864$ rows, 55,876 missing values matching CTDI).
- **Meteorological Source**: Acquired (ECMWF ERA5 continuous surface reanalysis at the 16 air station coordinates).
- **Visibility Recovery Investigation**: Completed and closed ([`Visibility Data Recovery & Provenance Report.md`](Reports/Visibility%20Data%20Recovery%20&%20Provenance%20Report.md)).
- **Rainfall Substitution Decision**: Formally adopted (`[DECISION]`) for Channel 9 of `ctdi_aligned_reconstructed`.
- **Traffic Source Investigation**: Completed (Parent 1st Gen Speedmap system verified with 607 baseline links).
- **Traffic Temporal Coverage Audit**: Completed and passed (774,686 snapshots across 36/36 months, 100% coverage of 2019–2021).

### PENDING:
- None for Phase 1, Phase 1.1, or Phase 2.

### NEXT PHASE:
- **Phase 3 — 24-Hour Sliding Window Segmentation & Missingness Mask Generation**:
  1. Slice continuous 3D tensor $(16, 26304, 13)$ into 24-hour sliding windows ($K = 26,304 - 24 + 1 = 26,281$ windows) with shape $(24, 16, 13)$.
  2. Implement simulated missingness mask generators (Random, Spatial-Block, Temporal-Block) matching CTDI Table II evaluation protocol.
  3. Feature scaling (zero-data-leakage fitted on Train split only).
  *(Note: Model training, VAE, diffusion, and evaluation have NOT yet started).*

---

## 2. Project Component Status Dashboard

| Research Area | Status | Direct Empirical Evidence | Remaining Work |
| :--- | :---: | :--- | :--- |
| **Literature** | **`VERIFIED`** | Exhaustive textual/tabular audit of Yu et al. (IEEE TBD 2025). Authoritative specification documented in [`CTDIDataset Specifications.md`](Dataset/CTDIDataset%20Specifications.md). | Ongoing literature tracking of foundation time-series models. |
| **CTDI Reconstruction** | **`VERIFIED`** | Full consistency matrix ([`CTDI Dataset Consistency Matrix.md`](Dataset/CTDI%20Dataset%20Consistency%20Matrix.md)) and source fidelity report ([`ctdi source fidelity report.md`](Reports/ctdi%20source%20fidelity%20report.md)) published. 13-channel structure verified ($16 \times 26,304 \times 13 = 5,471,232$). | Proceed to Phase 3 window segmentation and masking. |
| **Air-Quality Dataset** | **`VERIFIED`** | EPD 2019–2021 continuous hourly dataset: 420,864 rows, 16 stations, 0 duplicates, 0 negative values. Total missing values: 55,876 ($99.99995\%$ match to paper's 55,875). Classified as `EXACT SOURCE MATCH`. | None. Air quality raw data is fully validated and immutable. |
| **Meteorology Dataset** | **`VERIFIED_DIFFERENCE`** | ERA5 surface reanalysis (420,864 rows, 16 stations). Exhaustive audit proved retrospective 10-min AWS series for 47 stations and visibility is `[IRRECOVERABLE]` from public open data (Page 2454: offline dataset from Dr. Yang Han at HKU). Documented in [`Visibility Data Recovery & Provenance Report.md`](Reports/Visibility%20Data%20Recovery%20&%20Provenance%20Report.md). Classified as `SOURCE DIFFERENCE WITH SCIENTIFIC JUSTIFICATION` (rainfall vs visibility). | Account for reanalysis rainfall vs visibility during feature preprocessing. |
| **Traffic Dataset** | **`VERIFIED`** | Parent 1st Gen Speedmap system verified and **100% extracted** (774,686 snapshots, 466,829,497 records, 632 unique links union, 590 common core links). Congestion mapped ordinally `[ASSUMPTION]`. `TRAFFIC_FULL_EXTRACTION = COMPLETE`. | Hourly link aggregation and station projection completed in Phase 2. |
| **Raw Data Integrity** | **`VERIFIED`** | 100% cryptographic immutability verified before and after Phase 2 (683 raw files identical bit-for-bit). Documented in [`Raw Data Integrity Manifest.md`](Dataset/Raw%20Data%20Integrity%20Manifest.md). | Maintain absolute raw immutability throughout all project phases. |
| **13-Channel Alignment** | **`VERIFIED`** | `src/preprocessing/build_aligned_dataset.py` executed successfully. Canonical 13-channel dataset saved at `data/interim/aligned/aligned_hourly_station_data.parquet` ($420,864 \times 13$). Shape $(16, 26304, 13)$ validated. | Ready for Phase 3 window segmentation. |
| **Spatial Alignment** | **`VERIFIED`** | Pairwise Haversine distance matrix computed and verified symmetric with zero diagonal (`data/interim/aligned/spatial_distance_matrix.npy`). IDW formula ($p=2$) computed on georeferenced links without coordinate fabrication. Audited in [`Phase 2 - Spatio-Temporal Alignment Report.md`](Reports/Phase%202%20-%20Spatio-Temporal%20Alignment%20Report.md). | Complete for Phase 2. |
| **Missingness & EDA** | **`VERIFIED`** | CTDI Section IV-B empirical missingness analysis fully reproduced in `notebooks/01_ctdi_style_missingness_analysis.ipynb`. Figures 6–10 published to `research/Figures/`. 1-hour temporal offset between EPD 1-indexed interval-end hours and ISO interval-start timestamps resolved ($\text{hour} = (\text{dt.hour}+1)\%24$). Bit-for-bit parity with published CTDI curves confirmed. Research report updated ([`CTDI Missingness Pattern Analysis.md`](Reports/CTDI%20Missingness%20Pattern%20Analysis.md)). | Finalize DataLoader integration once canonical tensor exists. |
| **Normalization** | **`READY`** | Mathematical specifications for zero-data-leakage scaling (fit on Train split ONLY) and cyclical temporal embeddings documented in [`Normalization & Zero-Leakage Protocol.md`](Preprocessing/Normalization%20&%20Zero-Leakage%20Protocol.md). | Execute scaling transformation on completed canonical tensor. |
| **Context Construction** | **`IN_PROGRESS`** | Deterministic Environmental Context Builder prototype drafted in `src/context/builder.py` and documented in [`reports/Data Processing - Hong Kong.md`](Reports/Data%20Processing%20-%20Hong%20Kong.md). | Update prompt templates with rainfall/visibility and traffic saturation features; test batch rendering. |
| **SLM Integration** | **`IN_PROGRESS`** | Architecture specified for frozen/LoRA SLM (Phi-3 / Gemma / Llama) context encoder $\mathbf{z}_C$ in [`SLM Context Encoder.md`](Architecture/SLM%20Context%20Encoder.md). | Benchmark lightweight SLM token inference latency and linear projection layer. |
| **Diffusion Denoiser** | **`IN_PROGRESS`** | Math formulated: DDPM with cross-attention / AdaLN conditioning on $\mathbf{z}_C$, spatial graph layers, temporal transformer blocks ([`Conditional Diffusion Model.md`](Architecture/Conditional%20Diffusion%20Model.md)). | Implement PyTorch module for conditional denoising backbone. |
| **Training Pipeline** | **`NOT_STARTED`** | Chronological 70/15/15 train/val/test split and composite loss function ($\mathcal{L}_{\text{diff}} + \mathcal{L}_{\text{chem}}$) formulated in [`Loss Functions & Objectives.md`](Architecture/Loss%20Functions%20&%20Objectives.md). | Implement training loop, optimizer, checkpointing, and WandB/TensorBoard logging. |
| **Evaluation Suite** | **`READY`** | Metric implementations for MAE, RMSE, MAPE, CRPS, and PICP formulated in `src/evaluation/metrics.py` and [`Evaluation Metrics.md`](Experiments/Evaluation%20Metrics.md). | Benchmark suite execution on trained model checkpoints. |
| **Baselines** | **`IN_PROGRESS`** | Baseline suite defined (Mean, Spline, KNN, BRITS, VAE, CSDI, CTDI) in [`Baseline Imputation Models.md`](Experiments/Baseline%20Imputation%20Models.md). | Implement benchmark test harness for comparative evaluation. |
| **Ablation Studies** | **`NOT_STARTED`** | 7-part ablation matrix designed in [`Ablation Study Plan.md`](Experiments/Ablation%20Study%20Plan.md) to evaluate SLM impact, graph structure, and physical loss. | Run ablations after baseline training. |
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
