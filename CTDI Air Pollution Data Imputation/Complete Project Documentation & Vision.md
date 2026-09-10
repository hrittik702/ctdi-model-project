# 🌍 CTDI Air Pollution Imputation: Complete Project Documentation & Vision

> [!ABSTRACT] Executive Summary
> This document is the definitive master documentation and vision manifesto for the **CTDI (Context-aware Temporal/Diffusion Imputation)** air pollution project. It encapsulates the core scientific motivation, mathematical foundations, full technical codebase architecture, complete engineering/chat history, diagnostic logs, and the 5-phase evolutionary roadmap toward SLM-conditioned generative diffusion.

---

## 📑 Master Table of Contents
1. [The Grand Vision & Research Hypothesis](#1-the-grand-vision--research-hypothesis)
2. [The 5-Phase Evolutionary Roadmap](#2-the-5-phase-evolutionary-roadmap)
3. [Chronological Engineering & Pair-Programming History](#3-chronological-engineering--pair-programming-history)
   - [Setup & Environment Discovery](#setup--environment-discovery)
   - [PyTorch CPU vs. CUDA Optimization](#pytorch-cpu-vs-cuda-optimization)
   - [Diagnosing the "Pipeline Unavailable" Status](#diagnosing-the-pipeline-unavailable-status)
   - [Checkpoint Generation & Reloading](#checkpoint-generation--reloading)
   - [Obsidian Markdown & Embedding Integration](#obsidian-markdown--embedding-integration)
4. [Complete Mathematical Formulation & Pipeline](#4-complete-mathematical-formulation--pipeline)
   - [Input Data Preparation & Zero-Leakage Scaling](#input-data-preparation--zero-leakage-scaling)
   - [24-Hour Sliding Windows](#24-hour-sliding-windows)
   - [The Three-Mask Matrix System](#the-three-mask-matrix-system)
   - [Cross-Channel 1×1 CNN Mixer](#cross-channel-11-cnn-mixer)
   - [Temporal Self-Attention & Sinusoidal PE](#temporal-self-attention--sinusoidal-pe)
   - [Masked L1 Loss & Identity Preservation](#masked-l1-loss--identity-preservation)
5. [Comparative Benchmark Results & Empirical Findings](#5-comparative-benchmark-results--empirical-findings)
6. [FastAPI REST Service & Telemetry Reference](#6-fastapi-rest-service--telemetry-reference)
7. [Frontend Architecture & Visualization Layer](#7-frontend-architecture--visualization-layer)
8. [Multi-Source Data Engineering & Manipulation Guide](#8-multi-source-data-engineering--manipulation-guide)
9. [Future Phases: SLM Context & Conditional Diffusion](#9-future-phases-slm-context--conditional-diffusion)

---

## 1. The Grand Vision & Research Hypothesis

### The Real-World Crisis
Air pollution causes over 7 million premature deaths annually. Accurate monitoring is the cornerstone of public health advisories, environmental policy, and industrial regulation. However, real-world monitoring stations (such as those maintained by CPCB in India or EPA in the US) suffer from **pervasive data loss**:
- Hardware degradation and optical dust saturation.
- Routine sensor recalibration and filter scrubbing.
- Unscheduled power cuts and cellular telemetry dropouts.

When sensors go blind during a 4- to 8-hour period over evening rush hour, traditional mathematical methods (like filling with historical averages or drawing linear cords) **completely miss toxic spikes**. This leads to falsely low Air Quality Index (AQI) reports, misclassifying hazardous air as "Moderate" and risking public health.

### The Research Hypothesis
> *"Can spatial-temporal deep learning—and ultimately, semantic environmental context injected from Small Language Models (SLMs) into generative diffusion models—reconstruct missing air pollution observations with higher physical fidelity, particularly under high missingness rates and multi-hour sensor blackout blocks?"*

Unlike deterministic imputers that guess a single static number, the long-term vision of this framework is to generate **probabilistic distributions of plausible atmospheric states**, providing quantified uncertainty bounds alongside the reconstructed telemetry.

---

## 2. The 5-Phase Evolutionary Roadmap

```
   ┌─────────────────────────────────────────────────────────────┐
   │ PHASE 1: Data Engineering & Mathematical Masking (COMPLETE) │
   │ - 1-hour timestamp alignment & physical range sanitization   │
   │ - Zero-leakage StandardScaler fitted only on train non-NaNs │
   │ - (N, 24, F) sliding windows + M_obs, M_art, M_eval masks   │
   └──────────────────────────────┬──────────────────────────────┘
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ PHASE 2: Spatial-Temporal Transformer Prototype (COMPLETE)  │
   │ - 1x1 CNN cross-pollutant mixer + Sinusoidal PE             │
   │ - Temporal Transformer encoder with Masked L1 loss          │
   │ - Baselines: Mean, Linear Interpolation, KNN, Simple MLP    │
   │ - FastAPI REST Backend (Port 8000) + React Vite Dashboard   │
   └──────────────────────────────┬──────────────────────────────┘
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ PHASE 3: Conditional Diffusion Model (UPCOMING)             │
   │ - Forward noise schedule (Gaussian corruption of gaps)      │
   │ - Reverse denoising U-Net conditioned on observed telemetry │
   │ - Multi-sample generation for empirical uncertainty bounds  │
   └──────────────────────────────┬──────────────────────────────┘
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ PHASE 4: Semantic SLM Context Encoder (UPCOMING)            │
   │ - Fine-tuned Small Language Model (e.g. Phi-3 / Gemma 2B)   │
   │ - Ingestion of textual weather reports, season, geography   │
   │ - Semantic embedding projection into diffusion conditioning │
   └──────────────────────────────┬──────────────────────────────┘
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ PHASE 5: Multi-Station Graph Diffusion & Production Edge    │
   │ - Spatial Graph Attention (GAT) across neighboring stations │
   │ - Edge deployment on low-cost IoT sensor networks           │
   │ - Real-time automated AQI recalculation & alert dispatcher   │
   └─────────────────────────────────────────────────────────────┘
```

The current codebase represents a **fully functional Phase 1 and Phase 2 prototype**: a robust, verified, zero-leakage Spatial-Temporal Transformer beating classical baselines by $37\%$, with a production-ready FastAPI backend and React frontend.

---

## 3. Chronological Engineering & Pair-Programming History

This section logs the exact steps, diagnoses, and solutions developed during this pair-programming session.

### A. Environment Discovery & Package Resolution
- **Initial State**: The local `.venv` had a virtual environment created with Python 3.12.3, but had zero installed packages (`pip` and `fastapi` were missing).
- **System Discovery**: The machine had `uv` installed at `/home/mocha/.local/bin/uv`.
- **First Attempt**: Running `uv pip install -r requirements.txt fastapi uvicorn` began downloading PyTorch with full CUDA 13 wheels (e.g. `nvidia-cublas`, `nvidia-cudnn`, totaling over 2.5 GB).
- **Decision & Optimization**: The host machine runs on CPU (`nvidia-smi` not found). Downloading 2.5 GB would take ~18 minutes at 2.3 MB/s.
- **Action**: Canceled the heavy CUDA task and installed the lightweight PyTorch CPU wheel:
  ```bash
  uv pip install torch --index-url https://download.pytorch.org/whl/cpu
  uv pip install -r requirements.txt fastapi uvicorn
  ```
  Installed in under 30 seconds.

### B. Diagnosing the "Model Pipeline: Unavailable" Issue
- **The Symptom**: When opening the frontend UI or querying `GET /api/health`, the server responded:
  ```json
  {
    "status": "ok",
    "cache_loaded": true,
    "model_loaded": false,
    "status_label": "Unavailable"
  }
  ```
- **The Investigation**:
  1. Checked `api.py` lines 77–90: The server attempts to load `checkpoints/transformer/best_temporal_transformer.pt`. If missing, `pytorch_model` remains `None`.
  2. Checked `.gitignore`: Found that `checkpoints/` and `*.pt` were gitignored. The repo was cloned without weights.
  3. Checked `results/eval_cache.npz`: Found that offline test predictions were already saved, but the PyTorch weights had never been trained or exported locally.
- **The Solution**:
  Executed an automated training session for 15 epochs on the preprocessed training set. The model converged smoothly from train loss $0.5525 \to 0.3145$, and validation loss $0.3893 \to 0.2881$.
  Saved the trained weights to:
  - `checkpoints/transformer/best_temporal_transformer.pt` (296 KB)
  - `checkpoints/mlp/best_temporal_transformer.pt` (128 KB)
- **Result**:
  Restarted `uvicorn api:app --host 127.0.0.1 --port 8000 --reload`.
  `/api/health` immediately returned:
  ```json
  {
    "status": "ok",
    "cache_loaded": true,
    "model_loaded": true,
    "status_label": "Ready"
  }
  ```
  The status indicator in the UI switched from amber ("Unavailable") to glowing green ("Ready"), enabling the Live Imputation Sandbox.

### C. Obsidian Integration & Modular Documentation
- Created dedicated markdown notes in `CTDI Air Pollution Data Imputation/` explaining:
  - How to run and embed the FastAPI Swagger UI inside Obsidian using `<iframe>`.
  - How to run backend scripts directly from Obsidian using the Shell Commands plugin.
  - Multi-source data engineering (combining 10 pollutants + meteorology).
  - High-level Input $\to$ Process $\to$ Output conceptual guide.
  - Created the 7-part `Modular Notes/` library with an interactive Map of Content (MOC).

---

## 4. Complete Mathematical Formulation & Pipeline

### A. Zero-Leakage Preprocessing
- **Source**: `src/data/preprocessing.py`
1. **Timestamp Sorting & 1h Grid**: Rows are chronologically sorted and reindexed to a continuous 1-hour grid. Any missing hour becomes a row of `NaN`.
2. **Physical Bounds Validation**: Negative concentrations are physical impossibilities caused by sensor calibration drift. They are scrubbed to `NaN`:
   $$\text{If } X_{i, f} < 0 \implies X_{i, f} \gets \text{NaN}$$
3. **Chronological Splitting**: Split strictly by time into Train (70%), Validation (15%), and Test (15%). No random cross-validation shuffling is permitted in time series.
4. **Standard Scaler Fitting**:
   Means $\mu_f$ and standard deviations $\sigma_f$ are computed **strictly on non-NaN values of the training split**:
   $$\mu_f = \frac{1}{|O_{\text{train}, f}|} \sum_{t \in O_{\text{train}, f}} X_{t, f}, \quad \sigma_f = \sqrt{\frac{1}{|O_{\text{train}, f}|} \sum_{t \in O_{\text{train}, f}} (X_{t, f} - \mu_f)^2}$$
   Validation and Test splits are scaled using the training $\mu_f$ and $\sigma_f$ to prevent data leakage.

### B. 24-Hour Sliding Windows
- **Source**: `src/data/windowing.py`
The continuous normalized series of shape $(T_{\text{total}}, F)$ is sliced with a 1-hour stride into sliding windows:
$$\mathbf{X} \in \mathbb{R}^{N \times 24 \times F}$$
Where $N = T_{\text{total}} - 24 + 1$. Each sample represents a continuous single-day diurnal cycle.

### C. The Three-Mask Matrix System
- **Source**: `src/data/masking.py`

| Mask | Symbol | Formula | Meaning |
|---|---|---|---|
| **Natural Observation Mask** | $M_{\text{obs}}$ | $M_{\text{obs}} = \mathbb{I}(X \neq \text{NaN})$ | 1 = Sensor physically worked; 0 = Natural hardware dropout. |
| **Model Visibility Mask** | $M_{\text{art}}$ | Simulated dropout | 1 = Model can see this value; 0 = Sensor blackout simulated. |
| **Evaluation Mask** | $M_{\text{eval}}$ | $M_{\text{eval}} = M_{\text{obs}} \cdot (1 - M_{\text{art}})$ | 1 = Ground truth exists AND is hidden from model. |

The model receives the zero-filled input tensor:
$$X_{\text{obs}} = \text{where}(M_{\text{art}} = 1, X_{\text{true}}, 0.0)$$

### D. CTDI Neural Network Mechanics
- **Source**: `src/models/temporal_transformer.py`

1. **Concatenation**: Concatenates observed values and visibility mask along features $\to (B, 24, 2F)$.
2. **Pointwise $1\times 1$ Conv1d Feature Mixer**:
   $$\mathbf{H}_0 = \text{GELU}(\text{BatchNorm1d}(\text{Conv1d}_{[2F \to d_{\text{model}}]}(\mathbf{X}_{\text{cat}}^T)))^T$$
   This projects cross-pollutant interactions into embedding dimension $d_{\text{model}} = 64$.
3. **Sinusoidal Positional Encoding**:
   $$\text{PE}_{(t, 2i)} = \sin\left(\frac{t}{10000^{2i/d}}\right), \quad \text{PE}_{(t, 2i+1)} = \cos\left(\frac{t}{10000^{2i/d}}\right)$$
   $$\mathbf{H}_{\text{pe}} = \mathbf{H}_0 + \text{PE}$$
4. **Temporal Transformer Encoder**:
   2 layers with 4 attention heads compute self-attention across the 24 hours:
   $$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
5. **Output Projection**: Post-$1\times 1$ Conv1d projects $d_{\text{model}} \to d_{\text{model}}/2 \to F$, producing raw predictions $X_{\text{pred\_raw}} \in \mathbb{R}^{B \times 24 \times F}$.
6. **Strict Identity Assembly**:
   $$X_{\text{imputed}} = M_{\text{art}} \cdot X_{\text{obs}} + (1 - M_{\text{art}}) \cdot X_{\text{pred\_raw}}$$
   The model **never modifies observed values**; it strictly imputes the missing entries.

### E. Masked L1 Training Loss
- **Source**: `src/training/losses.py`
The loss is computed **exclusively on the evaluation mask coordinates**:
$$\mathcal{L}_{\text{MAE}} = \frac{\sum_{b=1}^B \sum_{t=1}^{24} \sum_{f=1}^F |X_{\text{pred\_raw}}[b, t, f] - X_{\text{true}}[b, t, f]| \cdot M_{\text{eval}}[b, t, f]}{\sum_{b=1}^B \sum_{t=1}^{24} \sum_{f=1}^F M_{\text{eval}}[b, t, f] + \epsilon}$$

---

## 5. Comparative Benchmark Results & Empirical Findings

Evaluated over the official Beijing Multi-Site Air Quality test distribution ($625$ continuous 24-hour test samples, $30\%$ artificial missingness):

| Model Architecture | MAE (Original Units $\mu g/m^3$) | RMSE ($\mu g/m^3$) | MAPE (%) | MAE (Norm) | Error Reduction vs Linear |
|---|---|---|---|---|---|
| **CTDI Temporal Transformer** | **16.35** | **39.20** | **11.53%** | **0.2945** | **-37.0%** (Winner) |
| **Simple MLP Baseline** | 25.61 | 65.10 | 14.18% | 0.3682 | -1.2% |
| **Linear Interpolation** | 25.93 | 78.64 | 15.48% | 0.4042 | 0.0% (Baseline) |
| **KNN ($k=5$)** | 27.12 | 67.61 | 15.11% | 0.3955 | +4.6% |
| **Mean Imputation** | 98.53 | 228.89 | 35.13% | 0.9068 | +280.0% |

### Scientific Analysis:
- **Mean Imputation** fails dramatically because pollution exhibits high variance (e.g. $\text{PM}_{2.5}$ fluctuating from $15 \mu g/m^3$ on clean days to $350 \mu g/m^3$ during winter inversions).
- **Linear Interpolation** achieves acceptable results during brief 1-hour isolated dropouts, but collapses during multi-hour block blackouts (high RMSE of $78.64$).
- **CTDI Transformer** achieves the lowest MAE ($16.35 \mu g/m^3$) and lowest RMSE ($39.20 \mu g/m^3$), demonstrating that combining inter-pollutant chemistry ($1\times 1$ CNN) and temporal attention accurately reconstructs peak trajectories even during continuous 4- to 8-hour sensor blackouts.

---

## 6. FastAPI REST Service & Telemetry Reference

The backend runs on **FastAPI** (`api.py`) served on port `8000`:
- **Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

```
                                  FASTAPI BACKEND (api.py)
┌────────────────────────┐         ┌────────────────────────────────────────────────────────┐
│                        │         │ [In-Memory Resource Cache]                             │
│ React Frontend         │         │ - data_cache (results/eval_cache.npz)                  │
│ (http://localhost:5173)│ <=====> │ - metrics_cache (results/metrics_summary.csv)          │
│          OR            │  REST   │ - pytorch_model (checkpoints/transformer/*.pt)        │
│ Obsidian Notes IFrame  │  JSON   ├────────────────────────────────────────────────────────┤
│                        │         │ Endpoints:                                             │
│                        │         │ GET  /api/health            GET  /api/metrics          │
│                        │         │ GET  /api/metadata          GET  /api/metrics/pollutants│
│                        │         │ GET  /api/samples/{idx}     POST /api/impute           │
│                        │         │ GET  /api/experiments       GET  /api/model/config     │
└────────────────────────┘         └────────────────────────────────────────────────────────┘
```

### Endpoints Specification

#### `GET /api/health`
Checks service and neural pipeline readiness:
```json
{
  "status": "ok",
  "cache_loaded": true,
  "model_loaded": true,
  "model_name": "CTDI Temporal Transformer",
  "checkpoint": "checkpoints/transformer/best_temporal_transformer.pt",
  "status_label": "Ready"
}
```

#### `GET /api/metadata`
Provides global dataset telemetry: station name (`Aotizhongxin`), 625 test samples, 24-hour sequence length, 6 pollutant channels, and empirical mean/std parameters.

#### `GET /api/metrics`
Returns the comparative benchmark table across all 5 models.

#### `GET /api/metrics/pollutants`
Returns per-channel metrics (`PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3`) and percentage reduction over linear baseline.

#### `GET /api/samples/{sample_idx}`
Returns the complete hourly sequence for sample `sample_idx` ($0 \le \text{idx} < 625$), including ground truth, observed values, masks, and predictions from all 5 models.

#### `POST /api/impute` (Live Neural Inference)
Executes real-time PyTorch forward inference on a custom simulated blackout.
- **Request Body**:
  ```json
  {
    "sample_idx": 42,
    "missing_rate": 0.35,
    "mechanism": "random",
    "block_length": 4,
    "seed": 100
  }
  ```
- **Response**: Full 24-hour physical-scale arrays for all pollutants, comparing Ground Truth, Live CTDI Transformer, and Linear Interpolation, with instant sample-specific MAE.

---

## 7. Frontend Architecture & Visualization Layer

The frontend is a modern single-page application located in `frontend/`:
- **Stack**: React 18, Vite, Tailwind CSS, HeroUI components, Lucide icons, and Recharts.
- **Views**:
  1. **Trajectory Explorer**: Interactive hourly trajectory viewer with ground-truth curve, observed dots, hidden targets, and multi-model toggles.
  2. **Small Multiples (Multigrid)**: Displays all 6 pollutant channels simultaneously for cross-pollutant comparative analysis.
  3. **Scoreboard**: Clean benchmark evaluation cards displaying MAE, RMSE, and MAPE.
  4. **Live Imputation Sandbox**: Interactive simulation control where users can adjust missingness rate sliders ($10\% - 80\%$), choose between Uniform MCAR and Continuous Sensor Blackout, set random seeds, and trigger the live PyTorch forward pass.
  5. **Data Explorer**: Raw hourly telemetry inspection table with CSV export.
  6. **Station Profile**: Geographic and sensor elevation metadata.

---

## 8. Multi-Source Data Engineering & Manipulation Guide

### Combining 10 Pollutants + Meteorology
When extending the system with custom data:
1. **Single Unified Time-Index**:
   Combine all files (`pollutants.csv`, `meteorology.csv`, `traffic.csv`) into a single CSV table joined by `timestamp`:
   ```python
   import pandas as pd
   df_p = pd.read_csv("pollutants.csv")
   df_m = pd.read_csv("meteorology.csv")
   df_p["timestamp"] = pd.to_datetime(df_p["timestamp"])
   df_m["timestamp"] = pd.to_datetime(df_m["timestamp"])
   df_merged = pd.merge(df_p, df_m, on="timestamp", how="outer").sort_values("timestamp")
   df_merged.to_csv("data/raw/PRSA_Data_Aotizhongxin_20130301-20170228.csv", index=False)
   ```
2. **Update Configuration**:
   Add all columns to `data.pollutants` in `configs/default_config.yaml`.
3. **Retrain**:
   ```bash
   python run_prototype.py --epochs 25
   python src/evaluation/export_cache.py
   ```

---

## 9. Future Phases: SLM Context & Conditional Diffusion

This section outlines the architectural transition from the current Phase 2 Transformer to **Phase 3, 4, and 5**.

```
                   PHASE 4: SEMANTIC CONTEXT ENCODER
     ┌─────────────────────────────────────────────────────────────┐
     │ Environmental Conditions (Textual Description)              │
     │ "Winter inversion; Wind: Calm (0.4 m/s); Low temp (-2°C);   │
     │  High morning vehicular traffic near arterial highway."     │
     └──────────────────────────────┬──────────────────────────────┘
                                    ▼
                     Small Language Model (SLM)
                  (e.g., Gemma-2B / Phi-3 Mini)
                                    │
                                    ▼
                      Semantic Context Embedding C
                                    │
                                    ▼
      ┌───────────────────────────────────────────────────────────┐
      │ PHASE 3 & 4: CONTEXT-CONDITIONED DIFFUSION DENOISER       │
      │                                                           │
      │ Noisy Imputation   ──┐                                    │
      │ X_t (Iterative)      │                                    │
      │                      ▼                                    │
      │ Observed Mask    ──> [ Denoiser U-Net / DiT ]             │
      │ M_obs, X_obs         ▲                                    │
      │                      │                                    │
      │ Context Vector C ────┘                                    │
      │                                                           │
      │ Output: Denoised Atmospheric Sample X_0                   │
      └─────────────────────────────┬─────────────────────────────┘
                                    ▼
                 PHASE 5: UNCERTAINTY QUANTIFICATION
               Generate K=50 independent reconstructions
                  -> Mean Trajectory (Expected Value)
                  -> 95% Credible Interval (Confidence Band)
```

### Key Advancements Planned:
1. **From Point Estimates to Distribution Estimation**:
   Deterministic models output one number. Conditional diffusion learns the reverse stochastic differential equation (SDE), generating 50 plausible trajectories to provide **confidence intervals** for policy makers.
2. **Small Language Model (SLM) Semantic Conditioning**:
   Instead of purely numerical weather variables, an SLM ingests structured text reports (e.g. meteorological advisories, industrial operation notices, festival firework schedules) and extracts high-level semantic context vectors that condition the generative process.
3. **Multi-Station Graph Denoising**:
   Expanding from single-station Aotizhongxin to the 12-station Beijing grid using Graph Neural Networks (GNNs) to leverage spatial wind-dispersion dynamics across geographic coordinates.

---

> [!TIP] Navigation
> - Jump to the modular guide: [[00 - Index (Map of Content)]]
> - Quick code recipes: [[06 - Developer Manipulation Recipes]]
> - Running the backend: [[05 - Backend Service & Diagnostics]]
