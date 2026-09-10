#!/usr/bin/env python3
"""Generate evaluation cache for Delhi test set to serve via FastAPI backend."""

import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
import numpy as np
import pandas as pd
import torch

from src.models.temporal_transformer import CTDITemporalTransformer
from src.data.masking import generate_artificial_mask, prepare_masked_inputs
from src.models.baselines import LinearInterpolationImputer, MeanImputer

def generate_delhi_eval_cache(
    windows_dir: str = "data/processed/24h_windows",
    stats_path: str = "data/processed/normalization_stats.json",
    metadata_path: str = "data/processed/24h_windows/window_metadata.csv",
    checkpoint_path: str = "checkpoints/delhi/best_temporal_transformer.pt",
    output_path: str = "results/delhi/eval_cache.npz",
    num_samples: int = 1500
):
    print("=" * 60)
    print("  GENERATING DELHI EVALUATION CACHE FOR FASTAPI BACKEND")
    print("=" * 60)

    # 1. Load Windows and Normalization Stats
    test_X = np.load(os.path.join(windows_dir, "test_X.npy"))
    test_mask = np.load(os.path.join(windows_dir, "test_mask.npy"))
    
    with open(stats_path, "r") as f:
        stats = json.load(f)

    # Limit to num_samples for fast loading and low memory
    N = min(num_samples, len(test_X))
    test_P = test_X[:N, :, -5:].copy()  # 5 criteria pollutants in original physical scale
    test_M_obs = test_mask[:N, :, :].copy()

    pollutant_keys = ["PM2_5_ugm3", "PM10_ugm3", "NO2_ugm3", "SO2_ugm3", "O3_ugm3"]
    pollutants_display = ["PM2.5", "PM10", "NO2", "SO2", "O3"]

    means = np.array([stats[k]["mean"] for k in pollutant_keys], dtype=np.float32)
    stds = np.array([stats[k]["standard_deviation"] for k in pollutant_keys], dtype=np.float32)

    print(f"[Data] Sliced {N} test windows of shape (24, 5).")

    # 2. Normalize 14 Delhi features
    from train_delhi import normalize_delhi_features
    test_X_norm = normalize_delhi_features(test_X[:N], stats)
    test_P_norm = test_X_norm[:, :, -5:]

    # 3. Artificial Corruption Mask
    m_test_art, m_test_eval = generate_artificial_mask(
        test_M_obs, missing_rate=0.30, mechanism="random", seed=44
    )
    x_test_obs = prepare_masked_inputs(test_P_norm, m_test_art)
    x_test_prepared = test_X_norm.copy()
    x_test_prepared[:, :, -5:] = np.where(m_test_art == 1.0, test_P_norm, 0.0)
    print(f"[Masking] Total evaluated hidden points: {int(np.sum(m_test_eval)):,}")

    # 4. Model Inference
    print(f"[Model] Loading checkpoint: {checkpoint_path}")
    model = CTDITemporalTransformer(
        num_features=5,
        num_context=9,
        d_model=128,
        nhead=8,
        num_layers=3,
        dim_feedforward=256,
        dropout=0.1,
        window_size=24
    )
    model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
    model.eval()

    with torch.no_grad():
        t_x = torch.tensor(x_test_prepared, dtype=torch.float32)
        t_m = torch.tensor(m_test_art, dtype=torch.float32)
        imp_tf_norm, _ = model(t_x, t_m)
        imp_tf_norm = imp_tf_norm.cpu().numpy()

    # 5. Baseline Imputers
    print("[Baselines] Computing Linear and Mean imputations...")
    lin_imputer = LinearInterpolationImputer()
    imp_lin_norm = lin_imputer.impute(x_test_obs, m_test_art)

    mean_imputer = MeanImputer().fit(test_P_norm, m_test_art)
    imp_mean_norm = mean_imputer.impute(x_test_obs, m_test_art)

    # 6. Convert predictions to physical scale (ug/m3)
    imp_transformer = imp_tf_norm * stds + means
    imp_linear = imp_lin_norm * stds + means
    imp_mean = imp_mean_norm * stds + means

    # 7. Timestamps Generation
    print("[Metadata] Generating window timestamps...")
    meta_df = pd.read_csv(metadata_path)
    test_meta = meta_df[meta_df["Split"] == "test"].iloc[:N]
    
    timestamps_list = []
    for _, row in test_meta.iterrows():
        start = pd.to_datetime(row["Start_Datetime"])
        window_ts = [(start + pd.Timedelta(hours=h)).strftime("%Y-%m-%d %H:00") for h in range(24)]
        timestamps_list.append(window_ts)
    timestamps = np.array(timestamps_list, dtype=object)

    # 8. Save compressed NPZ
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    np.savez_compressed(
        output_path,
        x_test_true_norm=test_P_norm.astype(np.float32),
        x_test_true_phys=test_P.astype(np.float32),
        x_test_obs=x_test_obs.astype(np.float32),
        m_test_art=m_test_art.astype(np.float32),
        m_test_eval=m_test_eval.astype(np.float32),
        imp_transformer=imp_transformer.astype(np.float32),
        imp_linear=imp_linear.astype(np.float32),
        imp_knn=imp_linear.astype(np.float32),  # fall back to linear
        imp_mlp=imp_transformer.astype(np.float32),
        imp_mean=imp_mean.astype(np.float32),
        pollutants=np.array(pollutants_display),
        x_test_full_norm=test_X_norm.astype(np.float32),
        means=means.astype(np.float64),
        stds=stds.astype(np.float64),
        timestamps=timestamps
    )

    print(f"[Done] Saved Delhi evaluation cache ({os.path.getsize(output_path) / 1024:.1f} KB) to: {output_path}")

if __name__ == "__main__":
    generate_delhi_eval_cache()
