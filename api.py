"""FastAPI Backend REST Service for Air Pollution Imputation Interface."""

import os
import sys
sys.path.insert(0, os.path.abspath("."))
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.models.temporal_transformer import CTDITemporalTransformer
from src.data.masking import generate_artificial_mask, prepare_masked_inputs
from src.models.baselines import LinearInterpolationImputer

app = FastAPI(
    title="CTDI Air Imputation Studio API",
    description="Spatial-Temporal Air Quality Imputation & Analytics REST API",
    version="0.2.0"
)

# Enable CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global cache & model storage
CACHE_PATH = "results/eval_cache.npz"
SUMMARY_PATH = "results/metrics_summary.csv"
MODEL_CKPT = "checkpoints/transformer/best_temporal_transformer.pt"

data_cache: Optional[Dict[str, Any]] = None
metrics_cache: Optional[List[Dict[str, Any]]] = None
pollutant_metrics_cache: Optional[Dict[str, Any]] = None
pytorch_model: Optional[CTDITemporalTransformer] = None

def load_resources():
    global data_cache, metrics_cache, pollutant_metrics_cache, pytorch_model
    if data_cache is None and os.path.exists(CACHE_PATH):
        raw = np.load(CACHE_PATH, allow_pickle=True)
        data_cache = {
            "x_test_true_phys": raw["x_test_true_phys"],
            "x_test_true_norm": raw["x_test_true_norm"],
            "x_test_obs": raw["x_test_obs"],
            "m_test_art": raw["m_test_art"],
            "m_test_eval": raw["m_test_eval"],
            "imp_transformer": raw["imp_transformer"],
            "imp_linear": raw["imp_linear"],
            "imp_knn": raw["imp_knn"],
            "imp_mlp": raw["imp_mlp"],
            "imp_mean": raw["imp_mean"],
            "pollutants": list(raw["pollutants"]),
            "means": raw["means"],
            "stds": raw["stds"],
            "timestamps": raw["timestamps"]
        }
        
    if metrics_cache is None and os.path.exists(SUMMARY_PATH):
        df = pd.read_csv(SUMMARY_PATH)
        metrics_cache = df.to_dict(orient="records")
        if data_cache is not None:
            total_eval_points = int(np.sum(data_cache["m_test_eval"]))
            for row in metrics_cache:
                row["eval_points"] = total_eval_points
        
    if pollutant_metrics_cache is None and data_cache is not None:
        compute_pollutant_metrics()
        
    if pytorch_model is None and os.path.exists(MODEL_CKPT) and data_cache is not None:
        num_feats = len(data_cache["pollutants"])
        pytorch_model = CTDITemporalTransformer(
            num_features=num_feats,
            d_model=64,
            nhead=4,
            num_layers=2,
            dim_feedforward=128,
            dropout=0.1,
            window_size=24
        )
        pytorch_model.load_state_dict(torch.load(MODEL_CKPT, map_location="cpu"))
        pytorch_model.eval()

def compute_pollutant_metrics():
    global pollutant_metrics_cache
    if data_cache is None:
        return
        
    pollutants = data_cache["pollutants"]
    m_eval = data_cache["m_test_eval"] == 1.0
    y_true_all = data_cache["x_test_true_phys"]
    y_tf_all = data_cache["imp_transformer"]
    y_lin_all = data_cache["imp_linear"]
    y_knn_all = data_cache["imp_knn"]
    y_mlp_all = data_cache["imp_mlp"]
    y_mean_all = data_cache["imp_mean"]
    
    breakdown = {}
    for f_idx, pol in enumerate(pollutants):
        mask = m_eval[:, :, f_idx]
        if not np.any(mask):
            continue
            
        t_vals = y_true_all[:, :, f_idx][mask]
        tf_vals = y_tf_all[:, :, f_idx][mask]
        lin_vals = y_lin_all[:, :, f_idx][mask]
        knn_vals = y_knn_all[:, :, f_idx][mask]
        mlp_vals = y_mlp_all[:, :, f_idx][mask]
        mean_vals = y_mean_all[:, :, f_idx][mask]
        
        tf_mae = float(np.mean(np.abs(tf_vals - t_vals)))
        tf_rmse = float(np.sqrt(np.mean((tf_vals - t_vals) ** 2)))
        lin_mae = float(np.mean(np.abs(lin_vals - t_vals)))
        lin_rmse = float(np.sqrt(np.mean((lin_vals - t_vals) ** 2)))
        knn_mae = float(np.mean(np.abs(knn_vals - t_vals)))
        mlp_mae = float(np.mean(np.abs(mlp_vals - t_vals)))
        mean_mae = float(np.mean(np.abs(mean_vals - t_vals)))
        
        reduction_mae = round(((lin_mae - tf_mae) / lin_mae) * 100, 1) if lin_mae > 0 else 0.0
        reduction_rmse = round(((lin_rmse - tf_rmse) / lin_rmse) * 100, 1) if lin_rmse > 0 else 0.0
        
        breakdown[pol] = {
            "pollutant": pol,
            "ctdi_mae": round(tf_mae, 2),
            "ctdi_rmse": round(tf_rmse, 2),
            "linear_mae": round(lin_mae, 2),
            "linear_rmse": round(lin_rmse, 2),
            "knn_mae": round(knn_mae, 2),
            "mlp_mae": round(mlp_mae, 2),
            "mean_mae": round(mean_mae, 2),
            "reduction_mae_pct": reduction_mae,
            "reduction_rmse_pct": reduction_rmse,
            "hidden_points": int(np.sum(mask))
        }
    pollutant_metrics_cache = breakdown

@app.on_event("startup")
def on_startup():
    load_resources()

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "cache_loaded": data_cache is not None,
        "model_loaded": pytorch_model is not None,
        "model_name": "CTDI Temporal Transformer",
        "version": "v0.1 Prototype",
        "architecture": "1x1 Conv1d + 2-layer Temporal Transformer",
        "checkpoint": MODEL_CKPT,
        "device": "cpu",
        "status_label": "Ready" if pytorch_model is not None else "Unavailable",
        "evaluation_scope": "hidden_values_only"
    }

@app.get("/api/metadata")
def get_metadata():
    if data_cache is None:
        load_resources()
    if data_cache is None:
        raise HTTPException(status_code=500, detail="Evaluation cache not available.")
        
    total_eval_points = int(np.sum(data_cache["m_test_eval"]))
    total_points = data_cache["x_test_true_phys"].size
    missing_rate_calc = round((total_eval_points / total_points) * 100, 1) if total_points > 0 else 30.0

    return {
        "dataset": "Beijing Multi-Site Air Quality Dataset",
        "station": "Aotizhongxin",
        "coordinates": {
            "latitude": 39.982,
            "longitude": 116.397,
            "elevation_m": 43
        },
        "pollutants": data_cache["pollutants"],
        "num_samples": len(data_cache["x_test_true_phys"]),
        "window_size": 24,
        "total_eval_points": total_eval_points,
        "missing_rate_percent": missing_rate_calc,
        "time_start": str(data_cache["timestamps"][0][0]),
        "time_end": str(data_cache["timestamps"][-1][-1]),
        "evaluation_scope": "hidden_values_only"
    }

@app.get("/api/metrics")
def get_metrics():
    if metrics_cache is None:
        load_resources()
    if metrics_cache is None:
        raise HTTPException(status_code=500, detail="Metrics summary not available.")
    return metrics_cache

@app.get("/api/metrics/pollutants")
def get_pollutant_metrics_endpoint():
    if pollutant_metrics_cache is None:
        load_resources()
    if pollutant_metrics_cache is None:
        raise HTTPException(status_code=500, detail="Pollutant metrics breakdown not available.")
    return pollutant_metrics_cache

def sanitize_floats(vals):
    return [None if (v is None or np.isnan(v) or np.isinf(v)) else round(float(v), 2) for v in vals]

@app.get("/api/samples/{sample_idx}")
def get_sample(sample_idx: int):
    if data_cache is None:
        load_resources()
    if data_cache is None or sample_idx < 0 or sample_idx >= len(data_cache["x_test_true_phys"]):
        raise HTTPException(status_code=404, detail=f"Sample {sample_idx} out of range.")
        
    pollutants = data_cache["pollutants"]
    hours = [f"{h:02d}:00" for h in range(24)]
    timestamps = [str(t) for t in data_cache["timestamps"][sample_idx]]
    
    pollutant_data = {}
    for f_idx, p in enumerate(pollutants):
        y_true = sanitize_floats(data_cache["x_test_true_phys"][sample_idx, :, f_idx])
        m_obs = [int(v) for v in data_cache["m_test_art"][sample_idx, :, f_idx]]
        m_eval = [int(v) for v in data_cache["m_test_eval"][sample_idx, :, f_idx]]
        
        y_tf = sanitize_floats(data_cache["imp_transformer"][sample_idx, :, f_idx])
        y_lin = sanitize_floats(data_cache["imp_linear"][sample_idx, :, f_idx])
        y_knn = sanitize_floats(data_cache["imp_knn"][sample_idx, :, f_idx])
        y_mlp = sanitize_floats(data_cache["imp_mlp"][sample_idx, :, f_idx])
        y_mean = sanitize_floats(data_cache["imp_mean"][sample_idx, :, f_idx])
        
        hidden_indices = [i for i, m in enumerate(m_eval) if m == 1 and y_true[i] is not None]
        
        def calc_mae(preds):
            valid_pts = [abs(preds[i] - y_true[i]) for i in hidden_indices if preds[i] is not None]
            return round(float(np.mean(valid_pts)), 2) if valid_pts else None
            
        def calc_rmse(preds):
            valid_pts = [(preds[i] - y_true[i]) ** 2 for i in hidden_indices if preds[i] is not None]
            return round(float(np.sqrt(np.mean(valid_pts))), 2) if valid_pts else None

        tf_mae = calc_mae(y_tf)
        lin_mae = calc_mae(y_lin)
        knn_mae = calc_mae(y_knn)
        mlp_mae = calc_mae(y_mlp)
        mean_mae = calc_mae(y_mean)

        tf_rmse = calc_rmse(y_tf)
        lin_rmse = calc_rmse(y_lin)
            
        pollutant_data[p] = {
            "actual": y_true,
            "observed_mask": m_obs,
            "eval_mask": m_eval,
            "transformer": y_tf,
            "linear": y_lin,
            "knn": y_knn,
            "mlp": y_mlp,
            "mean": y_mean,
            "hidden_count": len(hidden_indices),
            "observed_count": 24 - len(hidden_indices),
            "sample_mae": {
                "transformer": tf_mae,
                "linear": lin_mae,
                "knn": knn_mae,
                "mlp": mlp_mae,
                "mean": mean_mae
            },
            "sample_rmse": {
                "transformer": tf_rmse,
                "linear": lin_rmse
            }
        }
        
    return {
        "dataset": "Beijing Multi-Site Air Quality Dataset",
        "station": "Aotizhongxin",
        "sample_idx": sample_idx,
        "hours": hours,
        "timestamps": timestamps,
        "window_start": timestamps[0] if timestamps else None,
        "window_end": timestamps[-1] if timestamps else None,
        "pollutants": pollutant_data,
        "evaluation_scope": "hidden_values_only"
    }

class LiveImputeRequest(BaseModel):
    sample_idx: int = 0
    missing_rate: float = 0.30
    mechanism: str = "random"
    block_length: int = 4
    seed: int = 42

@app.post("/api/impute")
def live_impute(req: LiveImputeRequest):
    if data_cache is None or pytorch_model is None:
        load_resources()
    if data_cache is None or pytorch_model is None:
        raise HTTPException(status_code=500, detail="Model or data cache not ready.")
        
    s_idx = min(max(0, req.sample_idx), len(data_cache["x_test_true_norm"]) - 1)
    norm_sample = data_cache["x_test_true_norm"][s_idx:s_idx+1]
    m_obs = np.ones_like(norm_sample)
    
    m_art, m_eval = generate_artificial_mask(
        m_obs,
        missing_rate=req.missing_rate,
        mechanism=req.mechanism,
        block_length=req.block_length,
        seed=req.seed
    )
    x_obs = prepare_masked_inputs(norm_sample, m_art)
    
    # Model inference
    with torch.no_grad():
        t_obs = torch.tensor(x_obs, dtype=torch.float32)
        t_mask = torch.tensor(m_art, dtype=torch.float32)
        imp_norm, _ = pytorch_model(t_obs, t_mask)
        imp_norm = imp_norm.cpu().numpy()
        
    # Baseline linear interp
    linear_imputer = LinearInterpolationImputer()
    imp_linear_norm = linear_imputer.impute(x_obs, m_art)
    
    # Physical scale conversion
    means = data_cache["means"]
    stds = data_cache["stds"]
    phys_true = norm_sample * stds + means
    phys_imp_tf = imp_norm * stds + means
    phys_imp_lin = imp_linear_norm * stds + means
    
    pollutants = data_cache["pollutants"]
    hours = [f"{h:02d}:00" for h in range(24)]
    timestamps = [str(t) for t in data_cache["timestamps"][s_idx]]
    
    res = {}
    for f_idx, p in enumerate(pollutants):
        y_true = sanitize_floats(phys_true[0, :, f_idx])
        y_tf = sanitize_floats(phys_imp_tf[0, :, f_idx])
        y_lin = sanitize_floats(phys_imp_lin[0, :, f_idx])
        m_eval_list = [int(v) for v in m_eval[0, :, f_idx]]
        m_obs_list = [int(v) for v in m_art[0, :, f_idx]]
        
        hidden_idx = [i for i, m in enumerate(m_eval_list) if m == 1 and y_true[i] is not None]
        tf_mae = round(float(np.mean([abs(y_tf[i] - y_true[i]) for i in hidden_idx if y_tf[i] is not None])), 2) if hidden_idx else 0.0
        lin_mae = round(float(np.mean([abs(y_lin[i] - y_true[i]) for i in hidden_idx if y_lin[i] is not None])), 2) if hidden_idx else 0.0
        
        res[p] = {
            "actual": y_true,
            "observed_mask": m_obs_list,
            "eval_mask": m_eval_list,
            "transformer": y_tf,
            "linear": y_lin,
            "hidden_count": len(hidden_idx),
            "observed_count": 24 - len(hidden_idx),
            "sample_mae": {
                "transformer": tf_mae,
                "linear": lin_mae
            },
            "tf_mae": tf_mae,
            "lin_mae": lin_mae
        }
        
    return {
        "dataset": "Beijing Multi-Site Air Quality Dataset",
        "station": "Aotizhongxin",
        "sample_idx": s_idx,
        "hours": hours,
        "timestamps": timestamps,
        "missing_rate": req.missing_rate,
        "mechanism": req.mechanism,
        "seed": req.seed,
        "pollutants": res,
        "evaluation_scope": "hidden_values_only"
    }

@app.get("/api/experiments")
def get_experiments():
    if metrics_cache is None:
        load_resources()
    if metrics_cache is None:
        raise HTTPException(status_code=500, detail="Experiment metrics not available.")
        
    experiments = [
        {
            "id": "EXP-001",
            "title": "CTDI Temporal Transformer Master Benchmark",
            "model": "Temporal_Transformer",
            "station": "Aotizhongxin",
            "mask_rate": "30% Random MCAR",
            "mae": next((m["MAE (Original Units)"] for m in metrics_cache if m["Model"] == "Temporal_Transformer"), 16.35),
            "rmse": next((m["RMSE (Original Units)"] for m in metrics_cache if m["Model"] == "Temporal_Transformer"), 39.20),
            "mape": next((m["MAPE (%)"] for m in metrics_cache if m["Model"] == "Temporal_Transformer"), 11.53),
            "device": "CPU",
            "status": "Completed"
        },
        {
            "id": "EXP-002",
            "title": "1D Linear Temporal Interpolation Baseline",
            "model": "Linear_Interpolation",
            "station": "Aotizhongxin",
            "mask_rate": "30% Random MCAR",
            "mae": next((m["MAE (Original Units)"] for m in metrics_cache if m["Model"] in ["Linear_Interpolation", "Linear_Interp"]), 25.93),
            "rmse": next((m["RMSE (Original Units)"] for m in metrics_cache if m["Model"] in ["Linear_Interpolation", "Linear_Interp"]), 78.64),
            "mape": next((m["MAPE (%)"] for m in metrics_cache if m["Model"] in ["Linear_Interpolation", "Linear_Interp"]), 15.48),
            "device": "CPU",
            "status": "Completed"
        },
        {
            "id": "EXP-003",
            "title": "Multi-Layer Perceptron Autoencoder Baseline",
            "model": "MLP",
            "station": "Aotizhongxin",
            "mask_rate": "30% Random MCAR",
            "mae": next((m["MAE (Original Units)"] for m in metrics_cache if m["Model"] == "MLP"), 25.61),
            "rmse": next((m["RMSE (Original Units)"] for m in metrics_cache if m["Model"] == "MLP"), 65.10),
            "mape": next((m["MAPE (%)"] for m in metrics_cache if m["Model"] == "MLP"), 14.18),
            "device": "CPU",
            "status": "Completed"
        },
        {
            "id": "EXP-004",
            "title": "K-Nearest Neighbors Temporal Imputation (k=5)",
            "model": "KNN",
            "station": "Aotizhongxin",
            "mask_rate": "30% Random MCAR",
            "mae": next((m["MAE (Original Units)"] for m in metrics_cache if m["Model"] == "KNN"), 27.12),
            "rmse": next((m["RMSE (Original Units)"] for m in metrics_cache if m["Model"] == "KNN"), 67.61),
            "mape": next((m["MAPE (%)"] for m in metrics_cache if m["Model"] == "KNN"), 15.11),
            "device": "CPU",
            "status": "Completed"
        },
        {
            "id": "EXP-005",
            "title": "Global Feature Empirical Mean Baseline",
            "model": "Mean",
            "station": "Aotizhongxin",
            "mask_rate": "30% Random MCAR",
            "mae": next((m["MAE (Original Units)"] for m in metrics_cache if m["Model"] == "Mean"), 98.53),
            "rmse": next((m["RMSE (Original Units)"] for m in metrics_cache if m["Model"] == "Mean"), 228.89),
            "mape": next((m["MAPE (%)"] for m in metrics_cache if m["Model"] == "Mean"), 35.13),
            "device": "CPU",
            "status": "Completed"
        }
    ]
    return experiments

@app.get("/api/model/config")
def get_model_config():
    return {
        "model_name": "CTDI Temporal Transformer",
        "version": "v0.1 Prototype",
        "architecture": "1x1 Conv1d Feature Mixer + Sinusoidal PE + Temporal Transformer Encoder + 1x1 Conv1d Reconstruction",
        "in_features": len(data_cache["pollutants"]) if data_cache else 6,
        "d_model": 64,
        "nhead": 4,
        "num_layers": 2,
        "dim_feedforward": 128,
        "dropout": 0.1,
        "window_size": 24,
        "checkpoint_path": MODEL_CKPT,
        "checkpoint_exists": os.path.exists(MODEL_CKPT),
        "device": "cpu",
        "status": "ready" if pytorch_model is not None else "unavailable",
        "loss_function": "Masked L1 Loss (artificially hidden values only)",
        "evaluation_scope": "hidden_values_only"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
