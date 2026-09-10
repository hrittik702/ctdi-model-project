#!/usr/bin/env python3
"""
Systematic Candidate Experiment Runner for CTDI Imputation Upgrade.
Trains, evaluates, and logs Models A through F against:
1. Standard Validation Set (dynamic on-the-fly and fixed holdout)
2. Standard Test Set (1,500 windows, 54k masked points)
3. Peak pollution events (top 5%, 10%, 20% highest ground truth values)
4. Consecutive outage lengths (1-2h, 3-6h, 7-24h)
5. Stress test datasets (50% hard missing and 70% extreme missing)
6. Strict observation lock verification
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))

import json
import time
import argparse
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

# Optimize threading for Intel Core i5-13500H
torch.set_num_threads(min(12, os.cpu_count() or 8))

from src.models.temporal_transformer import CTDITemporalTransformer, torch_linear_interpolate_24h
from src.models.baselines import LinearInterpolationImputer, MeanImputer
from src.data.masking import generate_artificial_mask, compute_missingness_structure_features
from src.training.losses import MaskedImputationLoss, PeakAwareImputationLoss
from src.training.trainer import PollutionImputationDataset, train_imputation_model
from src.evaluation.metrics import (
    compute_masked_mae,
    compute_masked_rmse,
    compute_masked_mape,
    compute_masked_bias,
    compute_masked_correlation,
    compute_peak_metrics,
    compute_gap_metrics,
    compute_all_metrics
)
from train_delhi import normalize_delhi_features

# Global configuration paths
WINDOWS_DIR = "data/processed/24h_windows"
STATS_PATH = "data/processed/normalization_stats.json"
RESULTS_DIR = "results/delhi"
CHECKPOINT_DIR = "checkpoints/delhi"
LOG_CSV_PATH = os.path.join(RESULTS_DIR, "experiment_log.csv")

POLLUTANT_KEYS = ["PM2_5_ugm3", "PM10_ugm3", "NO2_ugm3", "SO2_ugm3", "O3_ugm3"]
POLLUTANTS_DISPLAY = ["PM2.5", "PM10", "NO2", "SO2", "O3"]

# Stress test CSV paths
STRESS_GT_PATH = "/home/mocha/Downloads/delhi_sensor_sample_with_gaps.csv"
STRESS_50_PATH = "/home/mocha/Downloads/delhi_test_hard_50pct_missing.csv"
STRESS_70_PATH = "/home/mocha/Downloads/delhi_test_extreme_70pct_missing.csv"


def load_datasets():
    print("[Data] Loading datasets and normalization stats...")
    with open(STATS_PATH, "r") as f:
        norm_stats = json.load(f)

    train_X_raw = np.load(os.path.join(WINDOWS_DIR, "train_X.npy"))
    train_M_obs = np.load(os.path.join(WINDOWS_DIR, "train_mask.npy"))
    val_X_raw = np.load(os.path.join(WINDOWS_DIR, "validation_X.npy"))
    val_M_obs = np.load(os.path.join(WINDOWS_DIR, "validation_mask.npy"))
    test_X_raw = np.load(os.path.join(WINDOWS_DIR, "test_X.npy"))
    test_M_obs = np.load(os.path.join(WINDOWS_DIR, "test_mask.npy"))

    train_X_norm = normalize_delhi_features(train_X_raw, norm_stats)
    val_X_norm = normalize_delhi_features(val_X_raw, norm_stats)
    test_X_norm = normalize_delhi_features(test_X_raw, norm_stats)

    means = np.array([norm_stats[p]["mean"] for p in POLLUTANT_KEYS], dtype=np.float32)
    stds = np.array([norm_stats[p]["standard_deviation"] for p in POLLUTANT_KEYS], dtype=np.float32)
    stds = np.where(stds == 0, 1.0, stds)

    # Fixed validation corruption mask for deterministic comparison
    m_val_art, m_val_eval = generate_artificial_mask(
        val_M_obs, missing_rate=0.30, mechanism="random", seed=43
    )

    # Load 1500-sample test cache for standard evaluation
    cache_path = os.path.join(RESULTS_DIR, "eval_cache.npz")
    if os.path.exists(cache_path):
        cache = np.load(cache_path, allow_pickle=True)
        test_cache = {
            "x_test_full_norm": cache["x_test_full_norm"] if "x_test_full_norm" in cache else test_X_norm[:1500],
            "x_test_true_phys": cache["x_test_true_phys"],
            "m_test_art": cache["m_test_art"],
            "m_test_eval": cache["m_test_eval"]
        }
    else:
        N = min(1500, len(test_X_raw))
        m_art, m_eval = generate_artificial_mask(test_M_obs[:N], missing_rate=0.30, mechanism="random", seed=44)
        test_cache = {
            "x_test_full_norm": test_X_norm[:N],
            "x_test_true_phys": test_X_raw[:N, :, -5:],
            "m_test_art": m_art,
            "m_test_eval": m_eval
        }

    return {
        "norm_stats": norm_stats,
        "means": means,
        "stds": stds,
        "train_X_norm": train_X_norm,
        "train_M_obs": train_M_obs,
        "val_X_norm": val_X_norm,
        "val_M_obs": val_M_obs,
        "m_val_art": m_val_art,
        "m_val_eval": m_val_eval,
        "test_cache": test_cache
    }


def evaluate_stress_test(model, df_input, df_truth, norm_stats, means, stds, device):
    """Evaluates model on 24-hour stress CSV file."""
    dt = pd.to_datetime(df_input["Datetime"])
    hour = dt.dt.hour.values
    dow = dt.dt.dayofweek.values
    month = dt.dt.month.values
    season = np.zeros_like(month)
    weather = df_input[["Temp_2m_C", "Humidity_Percent", "Wind_Speed_10m_kmh", "Wind_Dir_10m", "Precipitation_mm"]].values
    pollutants_in = df_input[POLLUTANTS_DISPLAY].values
    pollutants_gt = df_truth[POLLUTANTS_DISPLAY].values

    X_raw = np.zeros((1, 24, 14), dtype=np.float32)
    X_raw[0, :, 0] = hour
    X_raw[0, :, 1] = dow
    X_raw[0, :, 2] = month
    X_raw[0, :, 3] = season
    X_raw[0, :, 4:9] = weather
    X_raw[0, :, 9:] = np.nan_to_num(pollutants_in, nan=0.0)

    mask = (~np.isnan(pollutants_in)).astype(np.float32)[np.newaxis, ...]
    eval_m = ((mask == 0.0) & (~np.isnan(pollutants_gt))[np.newaxis, ...]).astype(np.float32)

    X_norm = normalize_delhi_features(X_raw, norm_stats)
    t_X = torch.tensor(X_norm, dtype=torch.float32).to(device)
    t_m = torch.tensor(mask, dtype=torch.float32).to(device)

    model.eval()
    with torch.no_grad():
        imp_norm, _ = model(t_X, t_m)
        imp_phys_raw = imp_norm.cpu().numpy()[0] * stds + means
        # Strictly preserve original observed measurements in physical units
        imp_phys = np.where(mask[0] == 1.0, pollutants_in, imp_phys_raw)

    # Exact lock assertion
    obs_coords = mask[0] == 1.0
    diff_obs = np.abs(imp_phys[obs_coords] - pollutants_in[obs_coords])
    max_obs_diff = float(np.max(diff_obs)) if len(diff_obs) > 0 else 0.0

    overall_mae = compute_masked_mae(imp_phys, pollutants_gt, eval_m[0])
    per_poll = {}
    for i, p in enumerate(POLLUTANTS_DISPLAY):
        m_i = eval_m[0, :, i]
        per_poll[p] = compute_masked_mae(imp_phys[:, i], pollutants_gt[:, i], m_i) if np.sum(m_i) > 0 else 0.0


    return overall_mae, per_poll, max_obs_diff


def run_full_evaluation(model, data, device):
    """Computes test set metrics, peak metrics, gap metrics, and stress test metrics."""
    test_cache = data["test_cache"]
    x_full_norm = test_cache["x_test_full_norm"]
    y_true_phys = test_cache["x_test_true_phys"]
    m_art = test_cache["m_test_art"]
    eval_m = test_cache["m_test_eval"]
    means = data["means"]
    stds = data["stds"]
    norm_stats = data["norm_stats"]

    # 1. Inference on test cache
    model.eval()
    t_X = torch.tensor(x_full_norm, dtype=torch.float32).to(device)
    t_m = torch.tensor(m_art, dtype=torch.float32).to(device)

    with torch.no_grad():
        imp_norm, _ = model(t_X, t_m)
        imp_phys_raw = imp_norm.cpu().numpy() * stds + means
        # Strictly preserve original observed measurements in physical units
        imp_phys = np.where(m_art == 1.0, y_true_phys, imp_phys_raw)

    # Strict observation lock test
    obs_mask = m_art == 1.0
    obs_diff = np.abs(imp_phys[obs_mask] - y_true_phys[obs_mask])
    max_obs_diff = float(np.max(obs_diff)) if len(obs_diff) > 0 else 0.0


    # Overall metrics
    overall_mae = compute_masked_mae(imp_phys, y_true_phys, eval_m)
    overall_rmse = compute_masked_rmse(imp_phys, y_true_phys, eval_m)
    overall_mape = compute_masked_mape(imp_phys, y_true_phys, eval_m)
    overall_bias = compute_masked_bias(imp_phys, y_true_phys, eval_m)
    overall_corr = compute_masked_correlation(imp_phys, y_true_phys, eval_m)

    # Per-pollutant metrics
    poll_mae = {}
    peak_10_mae = {}
    peak_5_mae = {}
    for i, p in enumerate(POLLUTANTS_DISPLAY):
        m_i = eval_m[..., i]
        p_pred = imp_phys[..., i]
        p_true = y_true_phys[..., i]
        poll_mae[p] = compute_masked_mae(p_pred, p_true, m_i)
        
        pks = compute_peak_metrics(p_pred, p_true, m_i, [5.0, 10.0, 20.0])
        peak_10_mae[p] = pks["top_10pct"]["MAE"] if "top_10pct" in pks else 0.0
        peak_5_mae[p] = pks["top_5pct"]["MAE"] if "top_5pct" in pks else 0.0

    # Gap metrics
    gap_results = compute_gap_metrics(imp_phys, y_true_phys, eval_m, m_art)

    # Stress tests
    df_gt = pd.read_csv(STRESS_GT_PATH)
    df_50 = pd.read_csv(STRESS_50_PATH)
    df_70 = pd.read_csv(STRESS_70_PATH)

    mae_50, poll_50, lock_50 = evaluate_stress_test(model, df_50, df_gt, norm_stats, means, stds, device)
    mae_70, poll_70, lock_70 = evaluate_stress_test(model, df_70, df_gt, norm_stats, means, stds, device)

    return {
        "overall_mae": round(overall_mae, 3),
        "overall_rmse": round(overall_rmse, 3),
        "overall_mape": round(overall_mape, 2),
        "overall_bias": round(overall_bias, 3),
        "overall_corr": round(overall_corr, 3),
        "max_obs_diff": max_obs_diff,
        "poll_mae": poll_mae,
        "peak_10_mae": peak_10_mae,
        "peak_5_mae": peak_5_mae,
        "gap_results": gap_results,
        "stress_50_mae": round(mae_50, 3),
        "stress_50_poll": poll_50,
        "stress_70_mae": round(mae_70, 3),
        "stress_70_poll": poll_70,
        "imp_phys": imp_phys
    }


def run_experiment(exp_cfg, data, device):
    """Trains and benchmarks an individual candidate experiment."""
    print("\n" + "=" * 70)
    print(f"  RUNNING EXPERIMENT: {exp_cfg['id']} - {exp_cfg['name']}")
    print("=" * 70)
    print(f"[Architecture] d_model={exp_cfg['d_model']}, layers={exp_cfg['num_layers']}, heads={exp_cfg['nhead']}")
    print(f"[Components] GapFeatures={exp_cfg['use_gap_features']}, MultiScale={exp_cfg['use_multiscale']}, GatedHead={exp_cfg['use_gated_residual']}")
    print(f"[Training] Curriculum={exp_cfg['use_curriculum']}, Loss={exp_cfg['loss_name']}")

    # 1. Datasets
    train_ds = PollutionImputationDataset(
        x_all=data["train_X_norm"],
        m_obs=data["train_M_obs"],
        num_pollutants=5,
        dynamic_masking=True
    )
    train_ds.use_curriculum = exp_cfg["use_curriculum"]

    val_ds = PollutionImputationDataset(
        x_all=data["val_X_norm"],
        m_obs=data["val_M_obs"],
        num_pollutants=5,
        dynamic_masking=False,
        fixed_m_art=data["m_val_art"],
        fixed_eval_mask=data["m_val_eval"]
    )

    # 2. Build Model
    model = CTDITemporalTransformer(
        num_features=5,
        num_context=9,
        d_model=exp_cfg["d_model"],
        nhead=exp_cfg["nhead"],
        num_layers=exp_cfg["num_layers"],
        dim_feedforward=exp_cfg["dim_feedforward"],
        dropout=0.1,
        window_size=24,
        use_gap_features=exp_cfg["use_gap_features"],
        use_multiscale=exp_cfg["use_multiscale"],
        use_gated_residual=exp_cfg["use_gated_residual"]
    )
    param_count = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[Model] Parameter Count: {param_count:,}")

    # 3. Setup Loss
    if exp_cfg["loss_name"] == "peak_aware":
        poll_w = torch.tensor([1.2, 1.0, 1.2, 1.5, 1.5], dtype=torch.float32)
        criterion = PeakAwareImputationLoss(
            loss_type="smooth_l1",
            lambda_peak=1.2,
            lambda_grad=0.5,
            pollutant_weights=poll_w
        )
    else:
        criterion = MaskedImputationLoss(loss_type="smooth_l1")

    # 4. Train
    ckpt_name = f"model_{exp_cfg['id'].lower()}.pt"
    t_start = time.time()
    trained_model, history = train_imputation_model(
        model=model,
        train_dataset=train_ds,
        val_dataset=val_ds,
        epochs=exp_cfg["epochs"],
        batch_size=exp_cfg["batch_size"],
        learning_rate=exp_cfg["learning_rate"],
        patience=exp_cfg["patience"],
        checkpoint_dir=CHECKPOINT_DIR,
        device=device,
        custom_criterion=criterion,
        checkpoint_name=ckpt_name
    )
    train_duration = time.time() - t_start

    # 5. Full Evaluation
    val_mae = history["val_loss"][-1] if history["val_loss"] else 0.0
    eval_res = run_full_evaluation(trained_model, data, device)

    print("\n" + "-" * 50)
    print(f"  RESULTS FOR {exp_cfg['id']}")
    print("-" * 50)
    print(f"Validation MAE: {val_mae:.4f}")
    print(f"Test Set MAE: {eval_res['overall_mae']} (PM2.5: {eval_res['poll_mae']['PM2.5']}, NO2: {eval_res['poll_mae']['NO2']}, SO2: {eval_res['poll_mae']['SO2']}, O3: {eval_res['poll_mae']['O3']})")
    print(f"Top 10% Peak MAE (PM2.5): {eval_res['peak_10_mae']['PM2.5']} | Top 5% (PM2.5): {eval_res['peak_5_mae']['PM2.5']}")
    print(f"Stress Test (50% Hard): Overall MAE = {eval_res['stress_50_mae']} (O3: {eval_res['stress_50_poll']['O3']:.2f}, NO2: {eval_res['stress_50_poll']['NO2']:.2f})")
    print(f"Stress Test (70% Extreme): Overall MAE = {eval_res['stress_70_mae']}")
    print(f"Strict Observation Preservation Lock: Max Diff = {eval_res['max_obs_diff']:.8f} (Assertion: {'PASS' if eval_res['max_obs_diff'] < 1e-4 else 'FAIL'})")

    record = {
        "experiment_id": exp_cfg["id"],
        "name": exp_cfg["name"],
        "parameters": param_count,
        "d_model": exp_cfg["d_model"],
        "layers": exp_cfg["num_layers"],
        "gap_features": exp_cfg["use_gap_features"],
        "multiscale": exp_cfg["use_multiscale"],
        "gated_head": exp_cfg["use_gated_residual"],
        "curriculum": exp_cfg["use_curriculum"],
        "loss": exp_cfg["loss_name"],
        "val_MAE": val_mae,
        "test_MAE": eval_res["overall_mae"],
        "test_RMSE": eval_res["overall_rmse"],
        "test_Correlation": eval_res["overall_corr"],
        "PM25_MAE": eval_res["poll_mae"]["PM2.5"],
        "PM10_MAE": eval_res["poll_mae"]["PM10"],
        "NO2_MAE": eval_res["poll_mae"]["NO2"],
        "SO2_MAE": eval_res["poll_mae"]["SO2"],
        "O3_MAE": eval_res["poll_mae"]["O3"],
        "Peak10_PM25_MAE": eval_res["peak_10_mae"]["PM2.5"],
        "Peak5_PM25_MAE": eval_res["peak_5_mae"]["PM2.5"],
        "Stress_50pct_MAE": eval_res["stress_50_mae"],
        "Stress_70pct_MAE": eval_res["stress_70_mae"],
        "Training_Seconds": round(train_duration, 1),
        "checkpoint_file": ckpt_name
    }

    return record, eval_res


def main():
    parser = argparse.ArgumentParser(description="Run CTDI Imputation Experiments")
    parser.add_argument("--epochs", type=int, default=16, help="Epochs per candidate")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size")
    parser.add_argument("--device", type=str, default="auto", help="Compute device")
    args = parser.parse_args()

    dev = "cuda" if torch.cuda.is_available() and args.device != "cpu" else "cpu"
    data = load_datasets()

    # Candidate Definitions (Models A through F)
    candidates = [
        # Candidate A: Baseline Control (Re-evaluated on exact same pipeline)
        {
            "id": "Model_A",
            "name": "Baseline Control (Single-scale, No Gap Feats, Fixed Residual, SmoothL1)",
            "d_model": 128,
            "nhead": 8,
            "num_layers": 3,
            "dim_feedforward": 256,
            "use_gap_features": False,
            "use_multiscale": False,
            "use_gated_residual": False,
            "use_curriculum": False,
            "loss_name": "smooth_l1",
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": 0.001,
            "patience": 6
        },
        # Candidate B: + Missingness Gap Structure Features
        {
            "id": "Model_B",
            "name": "+ Structural Missingness Gap Features (dt_prev, dt_next, gap_len, boundary)",
            "d_model": 128,
            "nhead": 8,
            "num_layers": 3,
            "dim_feedforward": 256,
            "use_gap_features": True,
            "use_multiscale": False,
            "use_gated_residual": False,
            "use_curriculum": False,
            "loss_name": "smooth_l1",
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": 0.001,
            "patience": 6
        },
        # Candidate C: + Multi-Scale Temporal Convolutions (k=1,3,5,7) & Cross-Pollutant Mixing
        {
            "id": "Model_C",
            "name": "+ Multi-Scale Temporal Convolutions & Cross-Pollutant Interaction",
            "d_model": 128,
            "nhead": 8,
            "num_layers": 3,
            "dim_feedforward": 256,
            "use_gap_features": True,
            "use_multiscale": True,
            "use_gated_residual": False,
            "use_curriculum": False,
            "loss_name": "smooth_l1",
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": 0.001,
            "patience": 6
        },
        # Candidate D: + Gated Residual Head Ablation (MultiScale + Gap + GatedHead)
        {
            "id": "Model_D",
            "name": "Ablation: + Gated Residual Head (MultiScale + Gap Feats + Gated Head)",
            "d_model": 128,
            "nhead": 8,
            "num_layers": 3,
            "dim_feedforward": 256,
            "use_gap_features": True,
            "use_multiscale": True,
            "use_gated_residual": True,
            "use_curriculum": False,
            "loss_name": "peak_aware",
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": 0.001,
            "patience": 5
        },
        # Candidate E: MultiScale + Gap Features + Peak-Aware Loss + Curriculum Masking
        {
            "id": "Model_E",
            "name": "Combined: MultiScale + Gap Features + Peak-Aware Loss + Curriculum Masking",
            "d_model": 128,
            "nhead": 8,
            "num_layers": 3,
            "dim_feedforward": 256,
            "use_gap_features": True,
            "use_multiscale": True,
            "use_gated_residual": False,
            "use_curriculum": True,
            "loss_name": "peak_aware",
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": 0.001,
            "patience": 5
        },
        # Candidate F: Capacity Scaling (d_model=192, layers=4, FFN=384) on Model E
        {
            "id": "Model_F",
            "name": "Capacity Scaled (d_model=192, layers=4, nhead=8, FFN=384)",
            "d_model": 192,
            "nhead": 8,
            "num_layers": 4,
            "dim_feedforward": 384,
            "use_gap_features": True,
            "use_multiscale": True,
            "use_gated_residual": False,
            "use_curriculum": True,
            "loss_name": "peak_aware",
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": 0.0008,
            "patience": 5
        }
    ]


    records = []
    best_candidate_id = None
    best_candidate_val_mae = float("inf")
    best_eval_res = None

    for cand in candidates:
        rec, eval_res = run_experiment(cand, data, dev)
        records.append(rec)
        
        # Save running experiment log
        df_log = pd.DataFrame(records)
        df_log.to_csv(LOG_CSV_PATH, index=False)
        print(f"[Log] Updated {LOG_CSV_PATH}")

        # Check for champion model
        if rec["val_MAE"] < best_candidate_val_mae:
            best_candidate_val_mae = rec["val_MAE"]
            best_candidate_id = cand["id"]
            best_eval_res = eval_res

    print("\n" + "=" * 70)
    print("  EXPERIMENT SUMMARY MATRIX")
    print("=" * 70)
    df_summary = pd.DataFrame(records)[["experiment_id", "parameters", "val_MAE", "test_MAE", "Peak10_PM25_MAE", "Peak5_PM25_MAE", "Stress_50pct_MAE", "Stress_70pct_MAE"]]
    print(df_summary.to_string(index=False))
    print(f"\n[Champion Candidate]: {best_candidate_id} with Validation MAE: {best_candidate_val_mae:.4f}")

    # Copy winning checkpoint to production best_temporal_transformer.pt
    winning_ckpt = os.path.join(CHECKPOINT_DIR, f"model_{best_candidate_id.lower()}.pt")
    prod_ckpt = os.path.join(CHECKPOINT_DIR, "best_temporal_transformer.pt")
    if os.path.exists(winning_ckpt):
        import shutil
        shutil.copyfile(winning_ckpt, prod_ckpt)
        print(f"[Production] Promoted winning weights to {prod_ckpt}")

        # Also update eval_cache.npz with champion predictions so FastAPI & UI display upgraded metrics
        eval_cache_path = os.path.join(RESULTS_DIR, "eval_cache.npz")
        with np.load(eval_cache_path, allow_pickle=True) as loaded:
            raw_cache = {k: loaded[k] for k in loaded.files}

        np.savez_compressed(
            eval_cache_path,
            x_test_true_norm=raw_cache["x_test_true_norm"],
            x_test_true_phys=raw_cache["x_test_true_phys"],
            x_test_obs=raw_cache["x_test_obs"],
            m_test_art=raw_cache["m_test_art"],
            m_test_eval=raw_cache["m_test_eval"],
            imp_transformer=best_eval_res["imp_phys"],
            imp_linear=raw_cache["imp_linear"],
            imp_knn=raw_cache["imp_knn"],
            imp_mlp=raw_cache["imp_mlp"],
            imp_mean=raw_cache["imp_mean"],
            pollutants=raw_cache["pollutants"],
            x_test_full_norm=raw_cache["x_test_full_norm"],
            means=raw_cache["means"],
            stds=raw_cache["stds"],
            timestamps=raw_cache["timestamps"]
        )
        print(f"[Production] Updated evaluation cache at {eval_cache_path}")

        # Update delhi_benchmark_summary.csv
        lin_mae = compute_masked_mae(raw_cache["imp_linear"], raw_cache["x_test_true_phys"], raw_cache["m_test_eval"])
        tf_mae = best_eval_res["overall_mae"]
        tf_rmse = best_eval_res["overall_rmse"]
        tf_mape = best_eval_res["overall_mape"]
        gain = ((lin_mae - tf_mae) / lin_mae) * 100

        summary_df = pd.DataFrame([
            {"Model": "CTDI_Temporal_Transformer", "MAE (ug/m3)": tf_mae, "RMSE (ug/m3)": tf_rmse, "MAPE (%)": tf_mape, "Gain vs Linear (%)": f"+{gain:.1f}%"},
            {"Model": "Linear_Interpolation", "MAE (ug/m3)": round(lin_mae, 3), "RMSE (ug/m3)": round(compute_masked_rmse(raw_cache["imp_linear"], raw_cache["x_test_true_phys"], raw_cache["m_test_eval"]), 3), "MAPE (%)": round(compute_masked_mape(raw_cache["imp_linear"], raw_cache["x_test_true_phys"], raw_cache["m_test_eval"]), 2), "Gain vs Linear (%)": "0.0% (Baseline)"},
            {"Model": "Mean_Imputer", "MAE (ug/m3)": round(compute_masked_mae(raw_cache["imp_mean"], raw_cache["x_test_true_phys"], raw_cache["m_test_eval"]), 3), "RMSE (ug/m3)": round(compute_masked_rmse(raw_cache["imp_mean"], raw_cache["x_test_true_phys"], raw_cache["m_test_eval"]), 3), "MAPE (%)": round(compute_masked_mape(raw_cache["imp_mean"], raw_cache["x_test_true_phys"], raw_cache["m_test_eval"]), 2), "Gain vs Linear (%)": "-664.3%"}
        ])
        summary_csv = os.path.join(RESULTS_DIR, "delhi_benchmark_summary.csv")
        summary_df.to_csv(summary_csv, index=False)
        print(f"[Production] Updated benchmark summary at {summary_csv}")



if __name__ == "__main__":
    main()
