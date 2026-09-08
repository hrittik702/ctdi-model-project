"""Master Execution Script for Phase 1 & Phase 2 Air Pollution Imputation Prototype.

Executes:
1. Dataset acquisition (Beijing Air Quality or user CSV)
2. Preprocessing & leak-free normalization
3. 24-hour sliding window extraction
4. Observation & artificial missingness masking
5. Baseline evaluations (Mean, Linear Interpolation, KNN, MLP)
6. CTDI 1x1 CNN + Temporal Transformer training
7. Rigorous MAE/RMSE/MAPE metric comparison on hidden values
8. Actual vs. Imputed 24-hour sequence visualization
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import sys
import argparse
import yaml
import numpy as np
import pandas as pd
import torch

from src.data.downloader import download_beijing_air_quality
from src.data.preprocessing import (
    preprocess_air_quality_data,
    split_time_series,
    normalize_datasets
)
from src.data.windowing import create_sliding_windows
from src.data.masking import (
    create_observation_mask,
    generate_artificial_mask,
    prepare_masked_inputs
)
from src.models.baselines import (
    MeanImputer,
    LinearInterpolationImputer,
    KNNPollutionImputer
)
from src.models.temporal_transformer import (
    CTDITemporalTransformer,
    SimpleMLPImputer
)
from src.training.trainer import (
    PollutionImputationDataset,
    train_imputation_model
)
from src.evaluation.evaluate import evaluate_all_models
from src.utils.visualization import (
    plot_24h_imputation_comparison,
    plot_multichannel_comparison
)

def run_pipeline(
    config_path: str = "configs/default_config.yaml",
    epochs_override: int = None,
    smoke_test: bool = False,
    sample_idx: int = 0
):
    print("=" * 70)
    print("  AIR POLLUTION IMPUTATION PROTOTYPE (PHASE 1 & 2)")
    print("=" * 70)
    
    # 1. Load Config
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
        
    pollutants = cfg["data"]["pollutants"]
    station = cfg["data"]["station_name"]
    window_size = cfg["data"]["window_size"]
    stride = cfg["data"]["stride"]
    missing_rate = cfg["masking"]["missing_rate"]
    mechanism = cfg["masking"]["mechanism"]
    epochs = epochs_override if epochs_override is not None else cfg["training"]["epochs"]
    batch_size = cfg["training"]["batch_size"]
    lr = cfg["training"]["learning_rate"]
    patience = cfg["training"]["patience"]
    
    if smoke_test:
        print("[Mode] Running in FAST SMOKE-TEST mode (truncated epochs and dataset).")
        epochs = min(epochs, 2)
        batch_size = 32
        
    print(f"[Config] Target Pollutants: {pollutants}")
    print(f"[Config] Window Size: {window_size} hours | Missing Rate: {missing_rate * 100:.0f}%")
    
    # 2. Acquire Dataset
    raw_csv = download_beijing_air_quality(
        raw_dir=cfg["data"]["raw_data_dir"],
        station=station
    )
    
    # 3. Clean and Align
    df_clean = preprocess_air_quality_data(raw_csv, feature_cols=pollutants, station=station)
    print(f"[Data] Preprocessed continuous hourly records: {len(df_clean)} rows.")
    
    if smoke_test and len(df_clean) > 3000:
        df_clean = df_clean.iloc[:3000].copy()
        
    # Chronological Split
    train_df, val_df, test_df = split_time_series(
        df_clean,
        train_ratio=cfg["data"]["train_ratio"],
        val_ratio=cfg["data"]["val_ratio"]
    )
    print(f"[Split] Train: {len(train_df)}h | Val: {len(val_df)}h | Test: {len(test_df)}h")
    
    # Normalization (Train stats only, zero leakage)
    train_norm, val_norm, test_norm, scaler = normalize_datasets(
        train_df, val_df, test_df, feature_cols=pollutants
    )
    
    # 4. 24-Hour Sliding Windows
    win_train, ts_train = create_sliding_windows(train_norm, window_size=window_size, stride=stride)
    win_val, ts_val = create_sliding_windows(val_norm, window_size=window_size, stride=stride)
    win_test, ts_test = create_sliding_windows(test_norm, window_size=window_size, stride=stride)
    print(f"[Windowing] 24-Hour Window Samples -> Train: {win_train.shape}, Val: {win_val.shape}, Test: {win_test.shape}")
    
    # 5. Masking
    m_train_obs = create_observation_mask(win_train)
    m_train_art, m_train_eval = generate_artificial_mask(m_train_obs, missing_rate=missing_rate, mechanism=mechanism, seed=42)
    x_train_obs = prepare_masked_inputs(win_train, m_train_art)
    
    m_val_obs = create_observation_mask(win_val)
    m_val_art, m_val_eval = generate_artificial_mask(m_val_obs, missing_rate=missing_rate, mechanism=mechanism, seed=43)
    x_val_obs = prepare_masked_inputs(win_val, m_val_art)
    
    m_test_obs = create_observation_mask(win_test)
    m_test_art, m_test_eval = generate_artificial_mask(m_test_obs, missing_rate=missing_rate, mechanism=mechanism, seed=44)
    x_test_obs = prepare_masked_inputs(win_test, m_test_art)
    
    print(f"[Masking] Artificially masked evaluation points in Test Set: {int(np.sum(m_test_eval))} values.")
    
    # 6. Fit Classical Baselines
    print("\n" + "-" * 50)
    print("  EVALUATING CLASSICAL BASELINES")
    print("-" * 50)
    
    print("[Baseline 1] Fitting Mean Imputer...")
    mean_imp = MeanImputer().fit(win_train, m_train_obs)
    
    print("[Baseline 2] Initializing Linear Interpolation Imputer...")
    linear_imp = LinearInterpolationImputer()
    
    print("[Baseline 3] Fitting KNN Imputer...")
    knn_imp = KNNPollutionImputer(n_neighbors=5).fit(win_train, m_train_art)
    
    # 7. Train Simple MLP Autoencoder Baseline
    print("\n" + "-" * 50)
    print("  TRAINING NEURAL BASELINE: MLP AUTOENCODER")
    print("-" * 50)
    num_feats = len(pollutants)
    mlp_model = SimpleMLPImputer(num_features=num_feats, window_size=window_size, hidden_dim=128)
    train_ds = PollutionImputationDataset(x_train_obs, m_train_art, win_train, m_train_eval)
    val_ds = PollutionImputationDataset(x_val_obs, m_val_art, win_val, m_val_eval)
    
    mlp_model, _ = train_imputation_model(
        model=mlp_model,
        train_dataset=train_ds,
        val_dataset=val_ds,
        epochs=min(epochs, 8 if not smoke_test else 2),
        batch_size=batch_size,
        learning_rate=0.002,
        patience=3,
        checkpoint_dir="checkpoints/mlp"
    )
    
    # 8. Train CTDI 1x1 CNN + Temporal Transformer Imputer
    print("\n" + "-" * 50)
    print("  TRAINING CTDI TEMPORAL TRANSFORMER")
    print("-" * 50)
    tf_model = CTDITemporalTransformer(
        num_features=num_feats,
        d_model=cfg["model"]["d_model"],
        nhead=cfg["model"]["nhead"],
        num_layers=cfg["model"]["num_layers"],
        dim_feedforward=cfg["model"]["dim_feedforward"],
        dropout=cfg["model"]["dropout"],
        window_size=window_size
    )
    
    tf_model, history = train_imputation_model(
        model=tf_model,
        train_dataset=train_ds,
        val_dataset=val_ds,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=lr,
        patience=patience,
        checkpoint_dir="checkpoints/transformer"
    )
    
    # 9. Comparative Evaluation on Test Set
    print("\n" + "=" * 70)
    print("  FINAL COMPARATIVE EVALUATION ON TEST SET (HIDDEN POSITIONS ONLY)")
    print("=" * 70)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    summary_df, imputations = evaluate_all_models(
        x_test_true=win_test,
        x_test_obs=x_test_obs,
        m_test_art=m_test_art,
        eval_mask=m_test_eval,
        feature_names=pollutants,
        scaler=scaler,
        mean_imputer=mean_imp,
        linear_imputer=linear_imp,
        knn_imputer=knn_imp,
        mlp_model=mlp_model,
        transformer_model=tf_model,
        device=device
    )
    
    print("\n" + summary_df.to_string(index=False))
    
    # Save metrics summary
    os.makedirs(cfg["evaluation"]["results_dir"], exist_ok=True)
    summary_csv = os.path.join(cfg["evaluation"]["results_dir"], "metrics_summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"\n[Results] Saved benchmark summary to {summary_csv}")
    
    # 10. Generate Actual vs Imputed Plots
    print("\n" + "-" * 50)
    print("  GENERATING ACTUAL VS. IMPUTED VISUALIZATIONS")
    print("-" * 50)
    
    plots_dir = cfg["evaluation"]["plots_dir"]
    sample_to_plot = min(sample_idx, len(win_test) - 1)
    
    plot_single = os.path.join(plots_dir, f"actual_vs_imputed_sample_{sample_to_plot}.png")
    plot_24h_imputation_comparison(
        sample_idx=sample_to_plot,
        x_test_true=win_test,
        m_test_art=m_test_art,
        eval_mask=m_test_eval,
        imputations=imputations,
        feature_names=pollutants,
        timestamps=ts_test,
        scaler=scaler,
        target_pollutant="PM2.5",
        save_path=plot_single
    )
    
    plot_multi = os.path.join(plots_dir, f"multichannel_comparison_sample_{sample_to_plot}.png")
    plot_multichannel_comparison(
        sample_idx=sample_to_plot,
        x_test_true=win_test,
        eval_mask=m_test_eval,
        imputations=imputations,
        feature_names=pollutants,
        scaler=scaler,
        save_path=plot_multi
    )
    
    print("\n" + "=" * 70)
    print("  PHASE 1 & 2 PROTOTYPE COMPLETE")
    print("=" * 70)
    return summary_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Air Pollution Imputation Prototype")
    parser.add_argument("--config", type=str, default="configs/default_config.yaml", help="Path to config file")
    parser.add_argument("--epochs", type=int, default=None, help="Override training epochs")
    parser.add_argument("--smoke-test", action="store_true", help="Run fast test")
    parser.add_argument("--sample-idx", type=int, default=0, help="Test sample index to visualize")
    args = parser.parse_args()
    
    run_pipeline(
        config_path=args.config,
        epochs_override=args.epochs,
        smoke_test=args.smoke_test,
        sample_idx=args.sample_idx
    )
