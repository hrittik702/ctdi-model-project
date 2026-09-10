#!/usr/bin/env python3
"""Training script for CTDI Spatial-Temporal Transformer on Processed Delhi Data."""

import os
import sys

# Auto-redirect to .venv Python interpreter if launched with external/Conda Python missing dependencies
_venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "python")
if os.path.exists(_venv_python) and sys.executable != _venv_python:
    try:
        import torch
        import yaml
    except ImportError:
        os.execv(_venv_python, [_venv_python] + sys.argv)

import json
import yaml
import time
import argparse
import numpy as np
import pandas as pd
import torch

from src.data.masking import generate_artificial_mask, prepare_masked_inputs
from src.models.temporal_transformer import CTDITemporalTransformer
from src.models.baselines import MeanImputer, LinearInterpolationImputer
from src.training.losses import MaskedImputationLoss
from src.training.trainer import PollutionImputationDataset, train_imputation_model
from src.evaluation.metrics import compute_masked_mae, compute_masked_rmse, compute_masked_mape

def normalize_delhi_features(X_raw: np.ndarray, norm_stats: dict) -> np.ndarray:
    """
    Normalizes 14 Delhi features:
    0-3: Hour, Day_of_Week, Month, Season_Code
    4-8: Temp_2m_C, Humidity_Percent, Wind_Speed_10m_kmh, Wind_Dir_10m, Precipitation_mm
    9-13: PM2_5_ugm3, PM10_ugm3, NO2_ugm3, SO2_ugm3, O3_ugm3
    """
    X_norm = X_raw.copy()
    
    # 0. Hour (0..23)
    X_norm[:, :, 0] = (X_norm[:, :, 0] - 11.5) / 6.928
    # 1. Day of Week (0..6)
    X_norm[:, :, 1] = (X_norm[:, :, 1] - 3.0) / 2.0
    # 2. Month (1..12)
    X_norm[:, :, 2] = (X_norm[:, :, 2] - 6.5) / 3.452
    # 3. Season_Code (0..3)
    X_norm[:, :, 3] = (X_norm[:, :, 3] - 1.5) / 1.118
    
    # 4-8 Weather
    weather_keys = ["Temp_2m_C", "Humidity_Percent", "Wind_Speed_10m_kmh", "Wind_Dir_10m", "Precipitation_mm"]
    for idx, k in enumerate(weather_keys, start=4):
        m = norm_stats[k]["mean"]
        s = norm_stats[k]["standard_deviation"]
        s = s if s > 0 else 1.0
        X_norm[:, :, idx] = (X_norm[:, :, idx] - m) / s
        
    # 9-13 Pollutants
    pollutant_keys = ["PM2_5_ugm3", "PM10_ugm3", "NO2_ugm3", "SO2_ugm3", "O3_ugm3"]
    for idx, k in enumerate(pollutant_keys, start=9):
        m = norm_stats[k]["mean"]
        s = norm_stats[k]["standard_deviation"]
        s = s if s > 0 else 1.0
        X_norm[:, :, idx] = (X_norm[:, :, idx] - m) / s
        
    return X_norm

def train_delhi_model(
    config_path: str = "configs/delhi_config.yaml",
    epochs_override: int = None
):
    print("=" * 70)
    print("  TRAINING CTDI SPATIAL-TEMPORAL TRANSFORMER (DELHI DATASET)")
    print("=" * 70)

    # 1. Load Configuration
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    # 2. Load Normalization Statistics (Computed strictly on TRAIN non-NaNs)
    stats_path = os.path.join(cfg["data"]["data_dir"], "normalization_stats.json")
    with open(stats_path, "r") as f:
        norm_stats = json.load(f)

    # Resolve pollutant keys flexibly (e.g. "PM2_5" -> "PM2_5_ugm3")
    raw_pollutants = cfg["data"]["pollutants"]
    resolved_pollutants = []
    for p in raw_pollutants:
        if p in norm_stats:
            resolved_pollutants.append(p)
        elif f"{p}_ugm3" in norm_stats:
            resolved_pollutants.append(f"{p}_ugm3")
        elif p.replace("_ugm3", "") in norm_stats:
            resolved_pollutants.append(p.replace("_ugm3", ""))
        else:
            raise KeyError(f"Pollutant '{p}' not found in normalization stats: {list(norm_stats.keys())}")

    pollutants = resolved_pollutants
    num_pollutants = len(pollutants)
    num_context = 9
    window_size = cfg["data"]["window_size"]
    missing_rate = cfg["masking"]["missing_rate"]
    mechanism = cfg["masking"]["mechanism"]
    block_length = cfg["masking"]["block_length"]
    epochs = epochs_override if epochs_override is not None else cfg["training"]["epochs"]
    batch_size = cfg["training"]["batch_size"]
    lr = cfg["training"]["learning_rate"]
    patience = cfg["training"]["patience"]
    checkpoint_dir = cfg["training"]["checkpoint_dir"]
    results_dir = cfg["evaluation"]["results_dir"]
    loss_type = cfg["training"].get("loss_type", "smooth_l1")
    os.makedirs(checkpoint_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    # 3. Load Preprocessed 24h Window Tensors
    windows_dir = os.path.join(cfg["data"]["data_dir"], "24h_windows")
    print(f"[Data] Loading pre-generated 24h windows from: {windows_dir}")

    train_X_raw = np.load(os.path.join(windows_dir, "train_X.npy"))       # (N, 24, 14)
    train_M_obs = np.load(os.path.join(windows_dir, "train_mask.npy"))    # (N, 24, 5)
    val_X_raw = np.load(os.path.join(windows_dir, "validation_X.npy"))    # (N, 24, 14)
    val_M_obs = np.load(os.path.join(windows_dir, "validation_mask.npy")) # (N, 24, 5)
    test_X_raw = np.load(os.path.join(windows_dir, "test_X.npy"))         # (N, 24, 14)
    test_M_obs = np.load(os.path.join(windows_dir, "test_mask.npy"))      # (N, 24, 5)

    print(f"[Tensors] Train: {train_X_raw.shape} | Val: {val_X_raw.shape} | Test: {test_X_raw.shape}")
    print(f"[Target Pollutants] ({num_pollutants} channels): {pollutants}")
    print(f"[Context Features] ({num_context} channels): 4 calendar + 5 meteorological")

    means = np.array([norm_stats[p]["mean"] for p in pollutants], dtype=np.float32)
    stds = np.array([norm_stats[p]["standard_deviation"] for p in pollutants], dtype=np.float32)
    stds = np.where(stds == 0, 1.0, stds)

    # Standardize all 14 channels using train statistics
    train_X_norm = normalize_delhi_features(train_X_raw, norm_stats)
    val_X_norm = normalize_delhi_features(val_X_raw, norm_stats)
    test_X_norm = normalize_delhi_features(test_X_raw, norm_stats)

    # Physical pollutant ground truth for test evaluation
    test_P_phys = test_X_raw[:, :, -num_pollutants:]

    # 4. Generate Deterministic Validation & Test Missingness Masks
    print(f"[Masking] Generating validation/test corruption: {missing_rate * 100:.0f}% ({mechanism})...")
    m_val_art, m_val_eval = generate_artificial_mask(
        val_M_obs, missing_rate=missing_rate, mechanism=mechanism, block_length=block_length, seed=43
    )
    m_test_art, m_test_eval = generate_artificial_mask(
        test_M_obs, missing_rate=missing_rate, mechanism=mechanism, block_length=block_length, seed=44
    )

    print(f"[Masking] Artificially masked test evaluation points: {int(np.sum(m_test_eval)):,} values.")

    # 5. Build Datasets (Train with dynamic on-the-fly masking)
    train_ds = PollutionImputationDataset(
        x_all=train_X_norm,
        m_obs=train_M_obs,
        num_pollutants=num_pollutants,
        dynamic_masking=True,
        missing_rate=missing_rate
    )
    val_ds = PollutionImputationDataset(
        x_all=val_X_norm,
        m_obs=val_M_obs,
        num_pollutants=num_pollutants,
        dynamic_masking=False,
        fixed_m_art=m_val_art,
        fixed_eval_mask=m_val_eval
    )

    # 6. Instantiate Context-Aware CTDI Spatial-Temporal Transformer
    print("\n" + "-" * 50)
    print("  BUILDING CTDI SPATIAL-TEMPORAL TRANSFORMER")
    print("-" * 50)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CTDITemporalTransformer(
        num_features=num_pollutants,
        num_context=num_context,
        d_model=cfg["model"]["d_model"],
        nhead=cfg["model"]["nhead"],
        num_layers=cfg["model"]["num_layers"],
        dim_feedforward=cfg["model"]["dim_feedforward"],
        dropout=cfg["model"]["dropout"],
        window_size=window_size
    )
    print(f"[Model] Parameter count: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    print(f"[Hardware] Training on device: {device}")

    # 7. Train Model with Dynamic Masking, Huber Loss, and CosineAnnealingLR
    model, history = train_imputation_model(
        model=model,
        train_dataset=train_ds,
        val_dataset=val_ds,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=lr,
        patience=patience,
        checkpoint_dir=checkpoint_dir,
        device=device,
        loss_type=loss_type
    )

    # 8. Comparative Test Evaluation (Hidden Values Only)
    print("\n" + "=" * 70)
    print("  EVALUATION ON TEST SET (HIDDEN POSITIONS ONLY)")
    print("=" * 70)

    model.eval()
    # Prepare masked test input (14 features with pollutants masked by m_test_art)
    x_test_prepared = test_X_norm.copy()
    test_P_norm = test_X_norm[:, :, -num_pollutants:]
    x_test_prepared[:, :, -num_pollutants:] = np.where(m_test_art == 1.0, test_P_norm, 0.0)

    with torch.no_grad():
        t_x_test = torch.tensor(x_test_prepared, dtype=torch.float32).to(device)
        t_m_art = torch.tensor(m_test_art, dtype=torch.float32).to(device)
        imp_tf_norm, _ = model(t_x_test, t_m_art)
        imp_tf_norm = imp_tf_norm.cpu().numpy()

    # Baselines on normalized pollutants
    x_test_pollutants_obs = np.where(m_test_art == 1.0, test_P_norm, 0.0)
    lin_imputer = LinearInterpolationImputer()
    imp_lin_norm = lin_imputer.impute(x_test_pollutants_obs, m_test_art)

    train_P_norm = train_X_norm[:, :, -num_pollutants:]
    mean_imputer = MeanImputer().fit(train_P_norm, train_M_obs)
    imp_mean_norm = mean_imputer.impute(x_test_pollutants_obs, m_test_art)

    # Inverse transform to physical units (ug/m3)
    imp_tf_phys = imp_tf_norm * stds + means
    imp_lin_phys = imp_lin_norm * stds + means
    imp_mean_phys = imp_mean_norm * stds + means
    y_test_phys = test_P_phys

    # Compute Metrics on Hidden Evaluation Points
    models_dict = {
        "CTDI_Temporal_Transformer": imp_tf_phys,
        "Linear_Interpolation": imp_lin_phys,
        "Mean_Imputer": imp_mean_phys
    }

    results = []
    for m_name, preds in models_dict.items():
        mae = compute_masked_mae(preds, y_test_phys, m_test_eval)
        rmse = compute_masked_rmse(preds, y_test_phys, m_test_eval)
        mape = compute_masked_mape(preds, y_test_phys, m_test_eval, min_threshold=1.0)
        results.append({
            "Model": m_name,
            "MAE (ug/m3)": round(mae, 3),
            "RMSE (ug/m3)": round(rmse, 3),
            "MAPE (%)": round(mape, 2)
        })

    summary_df = pd.DataFrame(results)
    lin_mae = summary_df.loc[summary_df["Model"] == "Linear_Interpolation", "MAE (ug/m3)"].values[0]
    tf_mae = summary_df.loc[summary_df["Model"] == "CTDI_Temporal_Transformer", "MAE (ug/m3)"].values[0]
    reduction = round(((lin_mae - tf_mae) / lin_mae) * 100, 1)

    gains = []
    for m in summary_df["Model"]:
        if m == "CTDI_Temporal_Transformer":
            gains.append(f"+{reduction:.1f}%" if reduction > 0 else f"{reduction:.1f}%")
        elif m == "Linear_Interpolation":
            gains.append("0.0% (Baseline)")
        else:
            m_mae = summary_df.loc[summary_df["Model"] == m, "MAE (ug/m3)"].values[0]
            m_red = round(((lin_mae - m_mae) / lin_mae) * 100, 1) if lin_mae > 0 else 0.0
            gains.append(f"+{m_red:.1f}%" if m_red > 0 else f"{m_red:.1f}%")
    summary_df["Gain vs Linear (%)"] = gains
    print(summary_df.to_string(index=False))

    summary_csv = os.path.join(results_dir, "delhi_benchmark_summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"\n[Results] Saved benchmark summary to: {summary_csv}")
    print(f"[Checkpoint] Best weights saved to: {os.path.join(checkpoint_dir, 'best_temporal_transformer.pt')}")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train CTDI Model on Processed Delhi Data")
    parser.add_argument("--config", type=str, default="configs/delhi_config.yaml", help="Path to config")
    parser.add_argument("--epochs", type=int, default=None, help="Epoch override")
    args = parser.parse_args()

    train_delhi_model(config_path=args.config, epochs_override=args.epochs)
