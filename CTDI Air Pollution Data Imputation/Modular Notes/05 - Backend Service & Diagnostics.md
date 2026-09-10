# 05 - Backend Service & Diagnostics

> [!INFO] Module Context
> - **Parent**: [[00 - Index (Map of Content)]]
> - **Previous**: [[04 - Neural Model & Masked Training]]
> - **Next**: [[06 - Developer Manipulation Recipes]]
> - **Tags**: `#fastapi` `#backend` `#troubleshooting` `#obsidian` `#api`

---

## 1. Backend Service Overview

The backend is built with **FastAPI** (`api.py`) and served via **Uvicorn** on port `8000`.

- **Entrypoint**: `api.py`
- **Default Port**: `8000`
- **Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 2. In-Memory Caching & Startup Lifecycle

Air quality datasets contain hundreds of thousands of hourly numbers. Evaluating models on the fly for every web request would make dashboards sluggish.

### How `load_resources()` works:
When the server starts (`@app.on_event("startup")`):
1. **Pre-computed Test Cache**: Reads `results/eval_cache.npz` into memory. This contains test sequences, ground truth, masks, and baseline predictions for instant $O(1)$ lookup.
2. **Benchmark Summary**: Loads `results/metrics_summary.csv`.
3. **Per-Pollutant Error Cache**: Computes channel-by-channel percentage reductions.
4. **PyTorch Weight Loading**: Checks for `checkpoints/transformer/best_temporal_transformer.pt`. If found, loads the model into CPU memory and sets it to evaluation mode (`.eval()`).

---

## 3. Complete REST API Reference

| Method | Route | Description | Output / Example |
|---|---|---|---|
| `GET` | `/api/health` | System health check and model pipeline status. | `{"status": "ok", "model_loaded": true, "status_label": "Ready"}` |
| `GET` | `/api/metadata` | Station metadata, sample count, feature channels, mean/std ranges. | Station name, 625 samples, 24h window. |
| `GET` | `/api/metrics` | Overall benchmark scoreboard across all 5 models. | Table with MAE, RMSE, and MAPE. |
| `GET` | `/api/metrics/pollutants` | Error breakdown per individual gas (PM2.5, PM10, etc.). | Channel MAE and % gain of CTDI vs Linear. |
| `GET` | `/api/samples/{idx}` | Hourly telemetry curves for a specific 24h sample. | Actual ground truth, observed, and 5 imputed curves. |
| `POST` | `/api/impute` | **Live Neural Inference**: Takes a sample and simulates a custom blackout. | Returns real-time PyTorch forward pass reconstruction. |
| `GET` | `/api/model/config` | Hyperparameters, attention heads, layers, checkpoint path. | Architecture configuration details. |

---

## 4. Diagnostics: Fixing "Model Pipeline Status: Unavailable"

### What Caused It:
When inspecting the backend health, you may see:
```json
{
  "model_loaded": false,
  "status_label": "Unavailable"
}
```
And on the frontend UI:
**"Model Pipeline: Unavailable"** (amber indicator).

### Root Cause:
`api.py` requires the model weights file:
`checkpoints/transformer/best_temporal_transformer.pt`

Because `.gitignore` ignores `checkpoints/` and `*.pt` files by default, git does not commit trained neural weights. If the weights are missing, the server falls back to "Unavailable" mode (disabling the live simulation sandbox).

### How to Fix It:
Run the quick training script in your virtual environment:

```bash
# 1. Activate venv
source .venv/bin/activate

# 2. Train transformer and export checkpoint
python -c "
import yaml
from src.data.preprocessing import preprocess_air_quality_data, split_time_series, normalize_datasets
from src.data.windowing import create_sliding_windows
from src.data.masking import create_observation_mask, generate_artificial_mask, prepare_masked_inputs
from src.models.temporal_transformer import CTDITemporalTransformer
from src.training.trainer import PollutionImputationDataset, train_imputation_model

with open('configs/default_config.yaml') as f: cfg = yaml.safe_load(f)
pollutants = cfg['data']['pollutants']
df = preprocess_air_quality_data('data/raw/PRSA_Data_Aotizhongxin_20130301-20170228.csv', pollutants)
tr, val, te = split_time_series(df, 0.7, 0.15)
tr_n, v_n, te_n, sc = normalize_datasets(tr, val, te, pollutants)

w_tr, _ = create_sliding_windows(tr_n, 24, 1)
w_val, _ = create_sliding_windows(v_n, 24, 1)

m_tr_obs = create_observation_mask(w_tr)
m_tr_art, m_tr_eval = generate_artificial_mask(m_tr_obs, 0.3, 'random', seed=42)
x_tr_obs = prepare_masked_inputs(w_tr, m_tr_art)

m_val_obs = create_observation_mask(w_val)
m_val_art, m_val_eval = generate_artificial_mask(m_val_obs, 0.3, 'random', seed=43)
x_val_obs = prepare_masked_inputs(w_val, m_val_art)

train_ds = PollutionImputationDataset(x_tr_obs, m_tr_art, w_tr, m_tr_eval)
val_ds = PollutionImputationDataset(x_val_obs, m_val_art, w_val, m_val_eval)

model = CTDITemporalTransformer(num_features=len(pollutants), d_model=64, nhead=4, num_layers=2, dim_feedforward=128, window_size=24)
train_imputation_model(model, train_ds, val_ds, epochs=15, batch_size=64, checkpoint_dir='checkpoints/transformer')
print('Done!')
"
```

Once `best_temporal_transformer.pt` is created, restart or reload Uvicorn:
```bash
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```
`/api/health` will immediately report `"model_loaded": true` and `"status_label": "Ready"`.

---

## 5. Live Swagger Docs Inside Obsidian

You can embed the live interactive API documentation directly inside your Obsidian notes:

<iframe 
  src="http://127.0.0.1:8000/docs" 
  width="100%" 
  height="700px" 
  style="border-radius: 8px; border: 1px solid var(--background-modifier-border);">
</iframe>

---

👉 **Next Step**: Read [[06 - Developer Manipulation Recipes]] for practical code recipes to modify and extend the codebase.
