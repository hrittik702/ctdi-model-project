#!/usr/bin/env python3
"""Training script for CTDI Spatial-Temporal Transformer in Keras 3 on Delhi Dataset."""

import os
import sys

# Ensure Keras 3 uses PyTorch execution backend
os.environ.setdefault("KERAS_BACKEND", "torch")
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import yaml
import time
import argparse
import numpy as np
import pandas as pd
import torch

# Optimize PyTorch CPU threading for Intel Core i5-13500H (12 physical cores)
torch.set_num_threads(min(12, os.cpu_count() or 8))

import keras
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from models.model_config import TemporalModelConfig
from models.keras_temporal_model import build_keras_temporal_model
from src.models.baselines import MeanImputer, LinearInterpolationImputer
from src.models.temporal_transformer import torch_linear_interpolate_24h
from src.training.losses import MaskedImputationLoss
from src.training.trainer import PollutionImputationDataset
from src.evaluation.metrics import compute_masked_mae, compute_masked_rmse, compute_masked_mape
from train_delhi import normalize_delhi_features


def train_keras_delhi_model(
    config_path: str = "configs/delhi_config.yaml",
    epochs_override: int = None
):
    print("=" * 70)
    print("  TRAINING CTDI SPATIAL-TEMPORAL TRANSFORMER (KERAS 3 - DELHI)")
    print("=" * 70)
    print(f"[Framework] Keras Version: {keras.__version__} | Backend: {keras.backend.backend()}")

    # 1. Load Configuration
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    # 2. Load Normalization Statistics
    stats_path = os.path.join(cfg["data"]["data_dir"], "normalization_stats.json")
    with open(stats_path, "r") as f:
        norm_stats = json.load(f)

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
            raise KeyError(f"Pollutant '{p}' not found in stats.")

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

    train_X_raw = np.load(os.path.join(windows_dir, "train_X.npy"))
    train_M_obs = np.load(os.path.join(windows_dir, "train_mask.npy"))
    val_X_raw = np.load(os.path.join(windows_dir, "validation_X.npy"))
    val_M_obs = np.load(os.path.join(windows_dir, "validation_mask.npy"))
    test_X_raw = np.load(os.path.join(windows_dir, "test_X.npy"))
    test_M_obs = np.load(os.path.join(windows_dir, "test_mask.npy"))

    print(f"[Tensors] Train: {train_X_raw.shape} | Val: {val_X_raw.shape} | Test: {test_X_raw.shape}")
    print(f"[Target Pollutants] ({num_pollutants} channels): {pollutants}")

    means = np.array([norm_stats[p]["mean"] for p in pollutants], dtype=np.float32)
    stds = np.array([norm_stats[p]["standard_deviation"] for p in pollutants], dtype=np.float32)
    stds = np.where(stds == 0, 1.0, stds)

    train_X_norm = normalize_delhi_features(train_X_raw, norm_stats)
    val_X_norm = normalize_delhi_features(val_X_raw, norm_stats)
    test_X_norm = normalize_delhi_features(test_X_raw, norm_stats)
    test_P_phys = test_X_raw[:, :, -num_pollutants:]

    # 4. Generate Validation and Test Corruption Masks
    from src.data.masking import generate_artificial_mask
    m_val_art, m_val_eval = generate_artificial_mask(
        val_M_obs, missing_rate=missing_rate, mechanism=mechanism, block_length=block_length, seed=43
    )
    m_test_art, m_test_eval = generate_artificial_mask(
        test_M_obs, missing_rate=missing_rate, mechanism=mechanism, block_length=block_length, seed=44
    )

    # 5. Build Datasets
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

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=False, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    # 6. Instantiate Keras 3 Model
    print("\n" + "-" * 50)
    print("  BUILDING KERAS 3 SPATIAL-TEMPORAL TRANSFORMER")
    print("-" * 50)
    model_cfg = TemporalModelConfig(
        num_features=num_pollutants,
        num_context=num_context,
        window_size=window_size,
        d_model=cfg["model"]["d_model"],
        num_heads=cfg["model"]["nhead"],
        num_transformer_layers=cfg["model"]["num_layers"],
        feed_forward_dim=cfg["model"]["dim_feedforward"],
        dropout=cfg["model"]["dropout"]
    )
    model = build_keras_temporal_model(model_cfg, name="CTDI_Keras_Temporal_Transformer_Delhi")
    print(f"[Model] Total parameters: {model.count_params():,}")

    # 7. Optimizer, LR Scheduler & Loss
    best_keras_ckpt = os.path.join(checkpoint_dir, "best_temporal_transformer.keras")
    criterion = MaskedImputationLoss(loss_type=loss_type)
    eval_criterion = MaskedImputationLoss(loss_type="l1")  # MAE for validation metric

    trainable_params = [w.value for w in model.trainable_weights]
    optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    tb_logdir = os.path.join("runs", "keras_delhi")
    tb_writer = SummaryWriter(log_dir=tb_logdir)

    print(f"[Training] Optimizer: AdamW (lr={lr}) | Loss: {loss_type} | Epochs: {epochs}")
    print(f"[TensorBoard] Logging to: {tb_logdir}")

    best_val_loss = float("inf")
    patience_counter = 0

    # 8. Training Loop
    for epoch in range(1, epochs + 1):
        t0 = time.time()
        train_ds.regenerate_epoch_masks()

        train_losses = []
        for x_obs, m_art, x_true, eval_m in train_loader:
            ctx = x_obs[:, :, :num_context]
            p_obs = x_obs[:, :, num_context:]
            prior = torch_linear_interpolate_24h(p_obs, m_art)

            optimizer.zero_grad()
            out = model([p_obs, m_art, prior, ctx], training=True)
            x_pred_raw = out[1]

            loss = criterion(x_pred_raw, x_true, eval_m)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=1.0)
            optimizer.step()

            train_losses.append(loss.item())

        scheduler.step()
        avg_train_loss = float(np.mean(train_losses))

        # Validation pass
        val_losses = []
        with torch.no_grad():
            for x_obs, m_art, x_true, eval_m in val_loader:
                ctx = x_obs[:, :, :num_context]
                p_obs = x_obs[:, :, num_context:]
                prior = torch_linear_interpolate_24h(p_obs, m_art)

                out = model([p_obs, m_art, prior, ctx], training=False)
                x_pred_raw = out[1]
                v_loss = eval_criterion(x_pred_raw, x_true, eval_m)
                val_losses.append(v_loss.item())

        avg_val_loss = float(np.mean(val_losses))
        current_lr = scheduler.get_last_lr()[0]
        duration = time.time() - t0

        tb_writer.add_scalar("Loss/train", avg_train_loss, epoch)
        tb_writer.add_scalar("Loss/val_mae", avg_val_loss, epoch)
        tb_writer.add_scalar("Learning_Rate", current_lr, epoch)
        tb_writer.add_scalar("Time/epoch_seconds", duration, epoch)

        is_best = avg_val_loss < best_val_loss
        if is_best:
            best_val_loss = avg_val_loss
            patience_counter = 0
            model.save(best_keras_ckpt)
            mark = "★ BEST"
        else:
            patience_counter += 1
            mark = f"(patience {patience_counter}/{patience})"

        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {avg_train_loss:.4f} | Val MAE: {avg_val_loss:.4f} | LR: {current_lr:.1e} | Time: {duration:.2f}s {mark}")

        if patience_counter >= patience:
            print(f"[Early Stopping] Triggered at epoch {epoch}. Best Val MAE: {best_val_loss:.4f}")
            break

    tb_writer.close()

    # 9. Reload Best Model Checkpoint
    if os.path.exists(best_keras_ckpt):
        model = keras.models.load_model(best_keras_ckpt)
        print(f"\n[Checkpoint] Restored best model from {best_keras_ckpt} (Val MAE: {best_val_loss:.4f})")

    # 10. Test Evaluation
    print("\n" + "=" * 70)
    print("  EVALUATION ON TEST SET (HIDDEN POSITIONS ONLY)")
    print("=" * 70)

    # Prepare masked test input
    x_test_prep = test_X_norm.copy()
    test_P_norm = test_X_norm[:, :, -num_pollutants:]
    x_test_prep[:, :, -num_pollutants:] = np.where(m_test_art == 1.0, test_P_norm, 0.0)

    t_ctx = torch.tensor(x_test_prep[:, :, :num_context], dtype=torch.float32)
    t_p_obs = torch.tensor(x_test_prep[:, :, num_context:], dtype=torch.float32)
    t_m_art = torch.tensor(m_test_art, dtype=torch.float32)
    t_prior = torch_linear_interpolate_24h(t_p_obs, t_m_art)

    with torch.no_grad():
        out_test = model([t_p_obs, t_m_art, t_prior, t_ctx], training=False)
        imp_tf_norm = out_test[0].detach().cpu().numpy()

    # Baselines
    x_test_pollutants_obs = np.where(m_test_art == 1.0, test_P_norm, 0.0)
    lin_imputer = LinearInterpolationImputer()
    imp_lin_norm = lin_imputer.impute(x_test_pollutants_obs, m_test_art)

    train_P_norm = train_X_norm[:, :, -num_pollutants:]
    mean_imputer = MeanImputer().fit(train_P_norm, train_M_obs)
    imp_mean_norm = mean_imputer.impute(x_test_pollutants_obs, m_test_art)

    # Physical scaling
    imp_tf_phys = imp_tf_norm * stds + means
    imp_lin_phys = imp_lin_norm * stds + means
    imp_mean_phys = imp_mean_norm * stds + means
    y_test_phys = test_P_phys

    models_dict = {
        "Keras3_Temporal_Transformer": imp_tf_phys,
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
    tf_mae = summary_df.loc[summary_df["Model"] == "Keras3_Temporal_Transformer", "MAE (ug/m3)"].values[0]
    reduction = round(((lin_mae - tf_mae) / lin_mae) * 100, 1)

    gains = []
    for m in summary_df["Model"]:
        if m == "Keras3_Temporal_Transformer":
            gains.append(f"+{reduction:.1f}%" if reduction > 0 else f"{reduction:.1f}%")
        elif m == "Linear_Interpolation":
            gains.append("0.0% (Baseline)")
        else:
            m_mae = summary_df.loc[summary_df["Model"] == m, "MAE (ug/m3)"].values[0]
            m_red = round(((lin_mae - m_mae) / lin_mae) * 100, 1) if lin_mae > 0 else 0.0
            gains.append(f"+{m_red:.1f}%" if m_red > 0 else f"{m_red:.1f}%")
    summary_df["Gain vs Linear (%)"] = gains

    print("\n" + summary_df.to_string(index=False))

    summary_csv = os.path.join(results_dir, "delhi_keras_benchmark_summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"\n[Results] Saved benchmark summary to: {summary_csv}")
    print(f"[Checkpoint] Best weights saved to: {best_keras_ckpt}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train CTDI Keras 3 Model on Processed Delhi Data")
    parser.add_argument("--config", type=str, default="configs/delhi_config.yaml", help="Path to config")
    parser.add_argument("--epochs", type=int, default=None, help="Epoch override")
    args = parser.parse_args()

    train_keras_delhi_model(config_path=args.config, epochs_override=args.epochs)
