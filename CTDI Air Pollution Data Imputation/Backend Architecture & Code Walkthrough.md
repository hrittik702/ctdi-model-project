# 📘 CTDI Air Pollution Imputation: Backend Architecture & Code Walkthrough

> [!INFO] Document Purpose
> This document provides an exhaustive, end-to-end architectural breakdown of the **CTDI Air Pollution Data Imputation** Python backend and machine learning pipeline. Use this guide to understand how data flows through the system, how the neural model operates, and how to safely manipulate and extend the codebase.


## 📑 Table of Contents
1. [System High-Level Architecture](#1-system-high-level-architecture)
2. [Project File Tree & Responsibilities](#2-project-file-tree--responsibilities)
3. [End-to-End Data Pipeline & Mathematics](#3-end-to-end-data-pipeline--mathematics)
   - [Data Acquisition (`src/data/downloader.py`)](#data-acquisition)
   - [Preprocessing & Zero-Leakage Normalization (`src/data/preprocessing.py`)](#preprocessing--normalization)
   - [24-Hour Sliding Windows (`src/data/windowing.py`)](#24-hour-sliding-windows)
   - [Observation & Artificial Masking (`src/data/masking.py`)](#masking-logic)
4. [Neural Network Architecture (`CTDITemporalTransformer`)](#4-neural-network-architecture)
   - [Cross-Channel 1×1 CNN Mixer](#cross-channel-11-cnn-mixer)
   - [Sinusoidal Positional Encoding](#sinusoidal-positional-encoding)
   - [Multi-Head Temporal Attention](#multi-head-temporal-attention)
   - [Reconstruction & Identity Preservation](#reconstruction--identity-preservation)
5. [Training & Masked Loss Function](#5-training--masked-loss-function)
6. [Benchmark Baselines Suite](#6-benchmark-baselines-suite)
7. [FastAPI Backend Service (`api.py`)](#7-fastapi-backend-service-apipy)
   - [Resource Caching & Startup Lifecycle](#startup-lifecycle)
   - [Complete REST API Endpoint Reference](#rest-api-endpoint-reference)
8. [Step-by-Step Developer Manipulation Recipes](#8-step-by-step-developer-manipulation-recipes)
   - [Recipe A: Add New Pollutants or Meteorological Sensors](#recipe-a-add-new-pollutants)
   - [Recipe B: Change Sequence Window Length (e.g., 24h → 48h)](#recipe-b-change-window-length)
   - [Recipe C: Modify Model Hyperparameters & Architecture](#recipe-c-modify-model-hyperparameters)
   - [Recipe D: Retrain Models & Regenerate Evaluation Caches](#recipe-d-retrain-and-cache)
   - [Recipe E: Integrate a Custom Imputation Algorithm](#recipe-e-integrate-custom-model)
   - [Recipe F: Add a New Backend REST Endpoint](#recipe-f-add-new-endpoint)

---

## 1. System High-Level Architecture

```
Raw CSV Telemetry (Beijing PRSA / Synthetic Fallback)
  │
  ▼
[src/data/preprocessing.py] ── Chronological Train/Val/Test Split (70/15/15)
  │                          ── Fit StandardScaler ONLY on Training Non-NaNs
  ▼
[src/data/windowing.py]     ── Sliding Windows: (N, 24 hours, 6 pollutants)
  │
  ▼
[src/data/masking.py]       ── Natural Mask M_obs (1=valid, 0=sensor NaN)
                            ── Artificial Mask M_art (simulates 30% loss)
                            ── Evaluation Mask M_eval = M_obs * (1 - M_art)
  │
  ├───────────────────────────────┬───────────────────────────────┐
  ▼                               ▼                               ▼
[Baselines]                 [CTDI Transformer]              [Simple MLP]
- Mean Imputer               - 1x1 CNN Feature Mixer         - Flattened 24x6
- Linear Interpolation       - Sinusoidal PE                 - Linear layers
- KNN (k=5)                  - Temporal Multi-Head Attn
  │                          - Output Projection
  └───────────────────────────────┼───────────────────────────────┘
                                  ▼
                    [src/training/losses.py]
                    Masked L1 Loss on M_eval ONLY
                                  │
                                  ▼
               Checkpoints: `checkpoints/transformer/best_temporal_transformer.pt`
               Results:     `results/eval_cache.npz`, `results/metrics_summary.csv`
                                  │
                                  ▼
                    [api.py] FastAPI REST Service (Port 8000)
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
          React Vite Dashboard        Obsidian Embedded Studio
          (http://localhost:5173)     (Live Swagger Docs / IFrames)
```

---

## 2. Project File Tree & Responsibilities

```text
ctdi-model-project/
├── configs/
│   └── default_config.yaml         # Master YAML configuration (data, model, training, paths)
├── src/
│   ├── data/
│   │   ├── downloader.py          # Downloads PRSA dataset; generates synthetic fallback if offline
│   │   ├── preprocessing.py       # Timestamp sorting, 1h resampling, physical range check, zero-leakage scaler
│   │   ├── windowing.py           # Extracts (N, 24, F) sliding windows and timestamp coordinates
│   │   └── masking.py             # Generates M_obs, M_art, and M_eval for MCAR random and block missingness
│   ├── models/
│   │   ├── baselines.py           # Mean, Linear Interpolation, and KNN imputers
│   │   └── temporal_transformer.py# CTDITemporalTransformer (1x1 CNN + Transformer) & SimpleMLPImputer
│   ├── training/
│   │   ├── losses.py              # MaskedImputationLoss (L1 / MSE computed strictly on M_eval)
│   │   └── trainer.py             # PyTorch training loop with early stopping, scheduler, checkpoint saving
│   ├── evaluation/
│   │   ├── metrics.py             # Masked MAE, RMSE, MAPE calculation functions
│   │   ├── evaluate.py            # Comparative evaluation runner across all baselines & neural models
│   │   └── export_cache.py        # Compiles test set predictions into results/eval_cache.npz
│   └── utils/
│       └── visualization.py       # Matplotlib trajectory and multi-channel comparison plotters
├── checkpoints/
│   ├── transformer/
│   │   └── best_temporal_transformer.pt  # Trained PyTorch weights for CTDITemporalTransformer
│   └── mlp/
│       └── best_temporal_transformer.pt  # Trained PyTorch weights for SimpleMLP baseline
├── results/
│   ├── eval_cache.npz             # Compressed numpy cache for sub-millisecond API responses
│   ├── metrics_summary.csv        # Benchmark metrics table comparing all models
│   └── plots/                     # Static evaluation figures
├── api.py                         # FastAPI REST API exposing metrics, samples, and live imputation
├── run_prototype.py               # Master CLI script running data prep, training, eval, and plot export
└── frontend/                      # React + Vite + Tailwind CSS + HeroUI single-page app
```

---

## 3. End-to-End Data Pipeline & Mathematics

### Data Acquisition
- **File**: `src/data/downloader.py`
- **Function**: `download_beijing_air_quality(raw_dir, station)`
- **Behavior**: Checks if `data/raw/PRSA_Data_{station}_20130301-20170228.csv` exists. If not, attempts to fetch from GitHub mirror or UCI repository. If remote servers are unreachable, calls `generate_synthetic_air_quality_csv()` which creates a mathematically correlated 4,320-hour multi-pollutant dataset exhibiting diurnal cycles and meteorological correlations.

### Preprocessing & Normalization
- **File**: `src/data/preprocessing.py`
1. **Timestamp Alignment (`clean_and_align_timestamps`)**:
   - Parses `year`, `month`, `day`, `hour` into UTC timestamps.
   - Reindexes to strict **1-hour frequency** (`freq="1h"`). Any omitted hours become rows of `NaN`.
2. **Physical Range Validation (`clean_physical_ranges`)**:
   - Pollutant concentrations cannot be negative:
   $$\text{If } X_{i, f} < 0 \implies X_{i, f} \gets \text{NaN}$$
3. **Chronological Splitting (`split_time_series`)**:
   - **No random shuffling** across time. Split chronologically into Train (70%), Validation (15%), and Test (15%) to mirror production forecasting and prevent data leakage.
4. **Zero-Leakage Standard Scaler (`AirPollutionScaler`)**:
   - Mean $\mu_f$ and standard deviation $\sigma_f$ are computed **exclusively from observed non-NaN values in the training split**:
   $$\mu_f = \frac{1}{|O_{\text{train}, f}|} \sum_{t \in O_{\text{train}, f}} X_{t, f}, \quad \sigma_f = \sqrt{\frac{1}{|O_{\text{train}, f}|} \sum_{t \in O_{\text{train}, f}} (X_{t, f} - \mu_f)^2}$$
   - Both Validation and Test sets are normalized using the training set's $\mu_f$ and $\sigma_f$.

### 24-Hour Sliding Windows
- **File**: `src/data/windowing.py`
- **Function**: `create_sliding_windows(df, window_size=24, stride=1)`
- Transforms continuous series $T_{\text{total}} \times F$ into batches of 24-hour continuous windows:
  $$\mathbf{X} \in \mathbb{R}^{N \times 24 \times F}$$
  where $N = \lfloor \frac{T_{\text{total}} - 24}{\text{stride}} \rfloor + 1$.
  For $F=6$ pollutants (`PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3`), each sample is a $(24 \times 6)$ matrix.

### Masking Logic
- **File**: `src/data/masking.py`
To train and evaluate an imputer objectively without ground-truth corruption, the framework defines three separate binary masks:

| Mask Name | Variable | Definition |
|---|---|---|
| **Natural Observation Mask** | $M_{\text{obs}} \in \{0, 1\}$ | $1$ if telemetry was physically recorded; $0$ if natural sensor dropout ($\text{NaN}$). |
| **Model Visibility Mask** | $M_{\text{art}} \in \{0, 1\}$ | $1$ if visible to model; $0$ if artificially hidden or natural $\text{NaN}$. |
| **Evaluation Mask** | $M_{\text{eval}} \in \{0, 1\}$ | $M_{\text{eval}} = M_{\text{obs}} \cdot (1 - M_{\text{art}})$. Equals $1$ **only** at coordinates where ground truth is known but hidden from the model. |

**Missingness Mechanisms**:
1. **Random MCAR (Missing Completely at Random)**:
   - Each observed cell has independent probability $p_{\text{missing}}$ of being hidden.
2. **Block Missingness (Sensor Blackout)**:
   - Consecutive hours (e.g. $L=4$ continuous hours) are dropped simultaneously across channels to simulate hardware failure.

The model input tensor is zero-filled at missing positions:
$$X_{\text{obs}} = \text{where}(M_{\text{art}} = 1, X_{\text{true}}, 0.0)$$

---

## 4. Neural Network Architecture

- **File**: `src/models/temporal_transformer.py`
- **Class**: `CTDITemporalTransformer`

```text
Input Tensor: X_obs (B, 24, F)   Mask Tensor: M_art (B, 24, F)
                   │                       │
                   └───────────┬───────────┘
                               ▼
            Concatenation: [X_obs, M_art] (B, 24, 2*F)
                               │
                               ▼
        1x1 Conv1d + BatchNorm1d + GELU (Cross-Pollutant Mixer)
                               │
                               ▼  (B, 24, d_model=64)
              Add Sinusoidal Positional Encoding
                               │
                               ▼
        Temporal Transformer Encoder (2 Layers, 4 Heads)
                               │
                               ▼  (B, 24, d_model=64)
         Post 1x1 Conv1d: (d_model -> d_model/2 -> F)
                               │
                               ▼
               Raw Prediction: X_pred_raw (B, 24, F)
                               │
                               ▼
      Output Assembly: X_imputed = M_art * X_obs + (1 - M_art) * X_pred_raw
```

### Key Mathematical Steps:
1. **Feature Mixing**:
   Instead of feeding raw sequence values directly into self-attention, a $1 \times 1$ convolution mixes the $2 \times F = 12$ channels ($6$ measurements $+ 6$ masks) into an embedding space $d_{\text{model}} = 64$. This allows the model to learn chemical correlations (e.g., $\text{PM}_{2.5} \leftrightarrow \text{PM}_{10}$, $\text{NO}_2 \leftrightarrow \text{O}_3$).
2. **Positional Encoding**:
   Sinusoidal positional encoding is added to inject the hour-of-the-day index $t \in [0, 23]$:
   $$\text{PE}_{(t, 2i)} = \sin\left(\frac{t}{10000^{2i/d}}\right), \quad \text{PE}_{(t, 2i+1)} = \cos\left(\frac{t}{10000^{2i/d}}\right)$$
3. **Temporal Attention**:
   Standard scaled dot-product multi-head attention models temporal transitions across the 24 hours:
   $$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
4. **Strict Identity Preservation**:
   The network **never alters observed values**. The final returned sequence enforces:
   $$X_{\text{imputed}}[t, f] = \begin{cases} X_{\text{obs}}[t, f], & \text{if } M_{\text{art}}[t, f] = 1 \\ X_{\text{pred\_raw}}[t, f], & \text{if } M_{\text{art}}[t, f] = 0 \end{cases}$$

---

## 5. Training & Masked Loss Function

- **File**: `src/training/losses.py`
- **Class**: `MaskedImputationLoss`

### Loss Formula
The loss is computed **exclusively on the evaluation mask coordinates** ($M_{\text{eval}}$). Unobserved cells and observed conditioning cells are excluded:
$$\mathcal{L}_{\text{MAE}} = \frac{\sum_{b=1}^B \sum_{t=1}^{24} \sum_{f=1}^F |X_{\text{pred\_raw}}[b, t, f] - X_{\text{true}}[b, t, f]| \cdot M_{\text{eval}}[b, t, f]}{\sum_{b=1}^B \sum_{t=1}^{24} \sum_{f=1}^F M_{\text{eval}}[b, t, f] + \epsilon}$$

### Training Loop Specifics (`src/training/trainer.py`):
- **Optimizer**: AdamW (`lr=0.001`, `weight_decay=1e-4`)
- **Gradient Clipping**: `max_norm=1.0` to stabilize attention gradients.
- **LR Scheduler**: `ReduceLROnPlateau(factor=0.5, patience=2)`.
- **Early Stopping**: Tracks validation loss on artificially masked validation windows; saves weights to `checkpoints/transformer/best_temporal_transformer.pt`.

---

## 6. Benchmark Baselines Suite

- **File**: `src/models/baselines.py`

| Baseline | Implementation Detail | Strengths / Weaknesses |
|---|---|---|
| **Mean Imputer** | Fits $\mu_f$ on training set. Fills missing cells with $\mu_f$. | Fast baseline. Completely destroys temporal dynamics and spikes. |
| **Linear Interpolation** | 1D Pandas linear interpolation along time axis $t \in [0, 23]$; nearest fill at sequence edges. | Strong for short 1-hour gaps. Fails completely during multi-hour block blackouts. |
| **KNN Imputer** | $k=5$ distance-weighted KNN over flattened $(24 \times F)$ vectors. | Captures similar day patterns; computationally expensive at inference time. |
| **MLP Autoencoder** | Multi-Layer Perceptron ($24 \times F \times 2 \to 128 \to 24 \times F$). | Learns non-linear mappings but lacks inductive bias for temporal sequentiality. |

---

## 7. FastAPI Backend Service (`api.py`)

### Startup Lifecycle
When `api.py` launches, the `@app.on_event("startup")` trigger runs `load_resources()`:
1. Loads `results/eval_cache.npz` into memory as a global dictionary `data_cache`.
2. Loads `results/metrics_summary.csv` into `metrics_cache`.
3. Precomputes per-pollutant error breakdowns in `compute_pollutant_metrics()`.
4. Checks if `checkpoints/transformer/best_temporal_transformer.pt` exists. If found, instantiates `CTDITemporalTransformer`, loads the state dict, calls `.eval()`, and sets `status_label = "Ready"`.

### REST API Endpoint Reference

#### 1. System Health
- **Endpoint**: `GET /api/health`
- **Purpose**: System monitoring, cache check, and model readiness status.
- **Sample Output**:
  ```json
  {
    "status": "ok",
    "cache_loaded": true,
    "model_loaded": true,
    "model_name": "CTDI Temporal Transformer",
    "version": "v0.1 Prototype",
    "checkpoint": "checkpoints/transformer/best_temporal_transformer.pt",
    "device": "cpu",
    "status_label": "Ready",
    "evaluation_scope": "hidden_values_only"
  }
  ```

#### 2. Dataset Metadata
- **Endpoint**: `GET /api/metadata`
- **Purpose**: Supplies the frontend with station names, sample counts, feature ranges, and units.

#### 3. Overall Benchmark Metrics
- **Endpoint**: `GET /api/metrics`
- **Purpose**: Returns the comparative evaluation scoreboard (MAE, RMSE, MAPE) across all 5 models.

#### 4. Per-Pollutant Breakdown
- **Endpoint**: `GET /api/metrics/pollutants`
- **Purpose**: Returns individual channel metrics and percentage improvements of CTDI over Linear Interpolation:
  $$\text{reduction\_mae\_pct} = \frac{\text{MAE}_{\text{linear}} - \text{MAE}_{\text{ctdi}}}{\text{MAE}_{\text{linear}}} \times 100$$

#### 5. Sample Sequence Telemetry
- **Endpoint**: `GET /api/samples/{sample_idx}`
- **Parameters**: `sample_idx` (integer from $0$ to $N-1$).
- **Purpose**: Returns the full 24-hour trajectory for all 6 pollutants, comparing ground truth, observed values, and reconstructions from all models.

#### 6. Live Interactive Imputation
- **Endpoint**: `POST /api/impute`
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
- **Execution Flow**:
  1. Grabs the ground-truth normalized sample from `data_cache["x_test_true_norm"][sample_idx]`.
  2. Synthesizes a new artificial mask based on requested `missing_rate` and `mechanism`.
  3. Executes `pytorch_model(t_obs, t_mask)` in real time.
  4. Runs linear interpolation on the exact same masked coordinates.
  5. Scales all outputs back to physical units ($\mu g/m^3$) using `scaler.means` and `scaler.stds`.
  6. Computes sample-specific MAE and returns full comparative series.

#### 7. Architecture Configuration
- **Endpoint**: `GET /api/model/config`
- **Purpose**: Returns hyperparameter specifications, layer counts, attention heads, and checkpoint file paths.

---

## 8. Step-by-Step Developer Manipulation Recipes

### Recipe A: Add New Pollutants or Meteorological Sensors
To add features (e.g., `TEMP`, `PRES`, or new gases like `CO2`):
1. Open `configs/default_config.yaml`.
2. Add the column names to `data.pollutants`:
   ```yaml
   pollutants:
     - "PM2.5"
     - "PM10"
     - "SO2"
     - "NO2"
     - "CO"
     - "O3"
     - "TEMP"  # <-- New feature
   ```
3. The dataset cleaner in `src/data/preprocessing.py` will automatically retain this column if it exists in the CSV.
4. Retrain the model using Recipe D.

---

### Recipe B: Change Sequence Window Length (e.g., 24h → 48h)
1. In `configs/default_config.yaml`:
   ```yaml
   data:
     window_size: 48   # <-- Changed from 24
   ```
2. In `src/models/temporal_transformer.py`, `CTDITemporalTransformer` accepts `window_size` in `__init__`:
   - It automatically adjusts `PositionalEncoding(max_len=window_size + 4)`.
3. In `api.py`, update `hours = [f"{h:02d}:00" for h in range(window_size)]` if you adjust the sequence length.
4. Retrain using Recipe D.

---

### Recipe C: Modify Model Hyperparameters & Architecture
To make the model deeper or wider:
1. In `configs/default_config.yaml`:
   ```yaml
   model:
     d_model: 128         # Increase channel embedding (default 64)
     nhead: 8             # Must divide d_model (128 / 8 = 16)
     num_layers: 4        # Deeper transformer (default 2)
     dim_feedforward: 256 # Default 128
     dropout: 0.15
   ```
2. In `src/models/temporal_transformer.py`, the network reads these arguments dynamically upon instantiation.

---

### Recipe D: Retrain Models & Regenerate Evaluation Caches
To retrain the neural model and update all cached predictions for the UI in one step:

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run master prototype pipeline (trains models, exports plots, updates metrics)
python run_prototype.py --epochs 20

# 3. Regenerate results/eval_cache.npz for the FastAPI backend
python src/evaluation/export_cache.py
```

After running this, the new weights will be in `checkpoints/transformer/best_temporal_transformer.pt` and the API will serve the newly trained model immediately upon reload.

---

### Recipe E: Integrate a Custom Imputation Algorithm
To add a new baseline or model (e.g., BiLSTM, Diffusion, Mamba):
1. Create your class in `src/models/`:
   ```python
   # src/models/bilstm.py
   import torch
   import torch.nn as nn

   class BiLSTMImputer(nn.Module):
       def __init__(self, in_features, hidden_dim=64):
           super().__init__()
           self.lstm = nn.LSTM(in_features * 2, hidden_dim, batch_first=True, bidirectional=True)
           self.fc = nn.Linear(hidden_dim * 2, in_features)
           
       def forward(self, x_obs, mask):
           x_cat = torch.cat([x_obs, mask], dim=-1)
           h, _ = self.lstm(x_cat)
           x_pred_raw = self.fc(h)
           x_imputed = mask * x_obs + (1.0 - mask) * x_pred_raw
           return x_imputed, x_pred_raw
   ```
2. In `src/evaluation/evaluate.py`, add your model to the comparison loop.
3. In `src/evaluation/export_cache.py`, add the predictions dictionary key to `phys_imputations`.

---

### Recipe F: Add a New Backend REST Endpoint
To expose a new analytical metric or function via FastAPI:
1. Open `api.py`.
2. Define your endpoint:
   ```python
   @app.get("/api/analysis/correlation")
   def get_pollutant_correlation():
       if data_cache is None:
           raise HTTPException(status_code=500, detail="Data cache not loaded.")
           
       # Reshape (N, 24, F) -> (N*24, F)
       flat_data = data_cache["x_test_true_phys"].reshape(-1, len(data_cache["pollutants"]))
       df = pd.DataFrame(flat_data, columns=data_cache["pollutants"])
       corr_matrix = df.corr().round(3).to_dict()
       return {"correlation": corr_matrix}
   ```
3. Because Uvicorn is running with `--reload`, the endpoint will be instantly available at `http://127.0.0.1:8000/api/analysis/correlation` and appear in the Swagger docs at `/docs`.
