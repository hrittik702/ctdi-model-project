# 06 - Developer Manipulation Recipes

> [!INFO] Module Context
> - **Parent**: [[00 - Index (Map of Content)]]
> - **Previous**: [[05 - Backend Service & Diagnostics]]
> - **Tags**: `#developer-guide` `#customization` `#code-snippets` `#python`

---

## Overview
This document contains copy-pasteable recipes to safely customize, modify, and extend any component of the CTDI framework.

---

## 🍳 Recipe 1: Add New Pollutants or Weather Sensors

1. Open `configs/default_config.yaml`.
2. Add your feature names to `data.pollutants`:
   ```yaml
   data:
     pollutants:
       - "PM2.5"
       - "PM10"
       - "SO2"
       - "NO2"
       - "CO"
       - "O3"
       - "TEMP"       # <-- Weather feature
       - "HUMIDITY"   # <-- Weather feature
       - "WSPM"       # <-- Wind speed
   ```
3. Retrain the model and regenerate the evaluation cache:
   ```bash
   python run_prototype.py --epochs 20
   python src/evaluation/export_cache.py
   ```

---

## 🍳 Recipe 2: Change Sequence Length (e.g. 24h $\to$ 48h)

1. Open `configs/default_config.yaml` and set:
   ```yaml
   data:
     window_size: 48   # Default was 24
     stride: 1
   ```
2. The `CTDITemporalTransformer` in `src/models/temporal_transformer.py` dynamically adjusts its sinusoidal positional encodings up to `window_size + 4`.
3. In `api.py`, update line 219 and line 335 if you want the API hours array to reflect 48 hours:
   ```python
   hours = [f"{h:02d}:00" for h in range(48)]
   ```
4. Retrain using Recipe 4.

---

## 🍳 Recipe 3: Modify Transformer Hyperparameters

To experiment with a larger, deeper neural network:

1. Open `configs/default_config.yaml`:
   ```yaml
   model:
     d_model: 128         # Hidden channel dimension (default: 64)
     nhead: 8             # Multi-head attention heads (must divide d_model: 128 / 8 = 16)
     num_layers: 4        # Encoder layers (default: 2)
     dim_feedforward: 256 # Feedforward expansion (default: 128)
     dropout: 0.15        # Dropout regularization (default: 0.1)
   ```
2. `CTDITemporalTransformer` reads these parameters directly from `configs/default_config.yaml` during instantiation.

---

## 🍳 Recipe 4: Retrain and Update All Caches in One Go

Whenever you change datasets, columns, or model architecture, run this 2-step command to update all weights, benchmarks, and UI caches:

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Train baseline models and transformer; export comparison plots and metrics summary
python run_prototype.py --epochs 25

# 3. Compile predictions into results/eval_cache.npz for instant API serving
python src/evaluation/export_cache.py
```

---

## 🍳 Recipe 5: Add a Custom Imputation Model (e.g. BiLSTM)

Want to compare against a new architecture?

1. Create a new model file `src/models/bilstm.py`:
   ```python
   import torch
   import torch.nn as nn

   class BiLSTMPollutionImputer(nn.Module):
       def __init__(self, num_features, hidden_dim=64):
           super().__init__()
           self.lstm = nn.LSTM(
               input_size=num_features * 2, # Concatenated data + mask
               hidden_size=hidden_dim,
               num_layers=2,
               batch_first=True,
               bidirectional=True
           )
           self.fc = nn.Linear(hidden_dim * 2, num_features)

       def forward(self, x_obs, mask):
           x_cat = torch.cat([x_obs, mask], dim=-1)
           h, _ = self.lstm(x_cat)
           x_pred_raw = self.fc(h)
           # Identity preservation: keep observed, fill missing
           x_imputed = mask * x_obs + (1.0 - mask) * x_pred_raw
           return x_imputed, x_pred_raw
   ```
2. Import and instantiate your model in `src/evaluation/evaluate.py`.
3. It will automatically be evaluated against the baselines and saved in `results/metrics_summary.csv`.

---

## 🍳 Recipe 6: Add a New FastAPI Endpoint

To expose a new analytics function via the REST API:

1. Open `api.py`.
2. Add your endpoint function:
   ```python
   @app.get("/api/analytics/correlations")
   def get_feature_correlations():
       if data_cache is None:
           raise HTTPException(status_code=500, detail="Data cache not loaded.")
       
       # Flatten (N, 24, F) -> (N*24, F)
       raw_values = data_cache["x_test_true_phys"].reshape(-1, len(data_cache["pollutants"]))
       df = pd.DataFrame(raw_values, columns=data_cache["pollutants"])
       matrix = df.corr().round(3).to_dict()
       return {"correlation_matrix": matrix}
   ```
3. Because Uvicorn runs with `--reload`, the endpoint will be live immediately at:
   - `http://127.0.0.1:8000/api/analytics/correlations`
   - Visible in Swagger UI at `http://127.0.0.1:8000/docs`.
