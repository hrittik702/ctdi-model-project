# Research Status Dashboard

**Project**: Context-Aware Generative Imputation of Air Pollution Using SLM-Conditioned Diffusion  
**Benchmark Reference**: Yu et al., *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, IEEE Transactions on Big Data, 2025.  
**Last Updated**: 2026-09-13  
**Current Operational Status**: **PAUSED FOR TODAY (CHECKPOINT FREEZE)**

---

## 1. Project Component Status Dashboard

| Research Area | Status | Direct Empirical Evidence | Remaining Work |
| :--- | :---: | :--- | :--- |
| **Literature** | **`VERIFIED`** | Exhaustive textual/tabular audit of Yu et al. (IEEE TBD 2025), CSDI (NeurIPS 2021), PriSTI (KDD 2023). Table I, Section III-A, IV-A, V-C documented in `research/literature/ctdi_paper_analysis.md`. | Ongoing literature tracking of emerging diffusion/foundation time-series models. |
| **CTDI Reconstruction** | **`VERIFIED`** | Table I reproduction published (`research/reports/ctdi_table_i_reconstruction.md`). All 13 channels verified; 607 road links proven in parent speedmap; IDW ($p=2$) verified. | Complete physical batch extraction of 2019–2021 traffic snapshots. |
| **Air-Quality Dataset** | **`READY`** | EPD 2019–2021 continuous hourly dataset loaded: 420,864 rows, 16 stations, 0 duplicates, 0 negative values. Natural NaNs: PM2.5 (2.53%), PM10 (2.71%), NO2 (2.77%), O3 (2.64%), SO2 (2.63%). SHA-256 verified. | None. Air quality is fully validated and ready. |
| **Meteorology Dataset** | **`PARTIALLY_VERIFIED`** | Reanalysis dataset exists (420,864 rows, Temp, RH, WS, WD, Pres, Rain). HKO daily benchmark verified. Divergence: CTDI Table I uses Visibility ($\text{km}$), interim uses Rainfall. | Acquire HKO 47-station AWS visibility series to achieve exact CTDI source-fidelity. |
| **Traffic Dataset** | **`BLOCKED`** | Parent 1st Gen Speedmap system verified (607 links, 774k snapshots covering 100% of 2019–2021). City Dashboard rejected (missing 97.9% of 2019). ATC rejected (annual averages, no speed). Real traffic file does not yet exist. | Build parallel batch snapshot scraper/parser for `speedmap.xml` to construct continuous hourly CSV. |
| **13-Channel Alignment** | **`BLOCKED`** | `src/preprocessing/alignment.py` implemented with Cartesian grid (420,864 rows) and strict safety halt preventing synthetic data injection. Aligns air + met, halts cleanly on traffic. | Update channel schema to visibility + congestion, then assemble canonical tensor once traffic is ingested. |
| **Spatial Alignment** | **`VERIFIED`** | Pairwise Haversine distance matrix computed and verified symmetric with zero diagonal (`data/interim/spatial_distance_matrix.npy`). IDW formula ($p=2$) mathematically formulated. | Apply IDW mapping across 607 road links once hourly traffic table is compiled. |
| **Missingness** | **`READY`** | Natural missingness verified in air quality. Simulated missingness masks (MCAR, continuous block, spatial station outage) formulated in `src/dataset/missingness.py` and `research/dataset/missingness_analysis.md`. | Finalize DataLoader integration once canonical tensor exists. |
| **Normalization** | **`READY`** | Mathematical specifications for zero-data-leakage scaling (fit on Train split ONLY) and cyclical temporal embeddings documented in `research/preprocessing/normalization.md`. | Execute scaling transformation on completed canonical tensor. |
| **Context Construction** | **`IN_PROGRESS`** | Deterministic Environmental Context Builder prototype drafted in `src/context/builder.py` and documented in `reports/Data Preprocessing/07`. | Update prompt templates with visibility and traffic saturation features; test batch rendering. |
| **SLM Integration** | **`IN_PROGRESS`** | Architecture specified for frozen/LoRA SLM (Phi-3 / Gemma / Llama) context encoder $\mathbf{z}_C$ in `research/architecture/context_encoder.md`. | Benchmark lightweight SLM token inference latency and linear projection layer. |
| **Diffusion Denoiser** | **`IN_PROGRESS`** | Math formulated: DDPM with cross-attention / AdaLN conditioning on $\mathbf{z}_C$, spatial graph layers, temporal transformer blocks (`research/architecture/diffusion_model.md`). | Implement PyTorch module for conditional denoising backbone. |
| **Training Pipeline** | **`NOT_STARTED`** | Chronological 70/15/15 train/val/test split and composite loss function ($\mathcal{L}_{\text{diff}} + \mathcal{L}_{\text{chem}}$) formulated in `research/architecture/loss_functions.md`. | Implement training loop, optimizer, checkpointing, and WandB/TensorBoard logging. |
| **Evaluation Suite** | **`READY`** | Metric implementations for MAE, RMSE, MAPE, CRPS, and PICP formulated in `src/evaluation/metrics.py` and `research/experiments/evaluation_metrics.md`. | Benchmark suite execution on trained model checkpoints. |
| **Baselines** | **`IN_PROGRESS`** | Baseline suite defined (Mean, Spline, KNN, BRITS, VAE, CSDI, CTDI) in `research/experiments/baselines.md`. | Implement benchmark test harness for comparative evaluation. |
| **Ablation Studies** | **`NOT_STARTED`** | 7-part ablation matrix designed in `research/experiments/ablation_plan.md` to evaluate SLM impact, graph structure, and physical loss. | Run ablations after baseline training. |
| **Documentation** | **`READY`** | Complete modular research architecture, master research document, decision records, daily checkpoints, and evidence logs established in `research/`. | Maintain continuously under Automatic Documentation Protocol. |

---

## 2. Allowed Status Definitions

- **`NOT_STARTED`**: Architectural or experimental design exists conceptually, but no code or data has been implemented.
- **`IN_PROGRESS`**: Active design, coding, or preliminary testing is underway.
- **`VERIFIED`**: Directly inspected, tested, and validated with empirical evidence and mathematical proof.
- **`PARTIALLY_VERIFIED`**: Certain aspects verified (e.g., schemas/coordinates), but subcomponents require correction or source alignment.
- **`BLOCKED`**: Cannot proceed to execution due to missing external data, unresolved prerequisites, or safety assertions.
- **`FAILED`**: Attempted approach proven scientifically or operationally unviable and officially rejected.
- **`READY`**: Component code/specifications are fully validated and awaiting upstream dependencies before execution.
- **`SUPERSEDED`**: Prior assumption or intermediate result overturned and replaced by newer evidence.
