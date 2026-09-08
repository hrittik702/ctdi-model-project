"""Cache evaluation predictions and test samples for instant UI loading."""

import os
import sys
sys.path.insert(0, os.path.abspath("."))
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import yaml
import numpy as np
import pandas as pd
import torch
from src.data.downloader import download_beijing_air_quality
from src.data.preprocessing import preprocess_air_quality_data, split_time_series, normalize_datasets
from src.data.windowing import create_sliding_windows
from src.data.masking import create_observation_mask, generate_artificial_mask, prepare_masked_inputs
from src.models.baselines import MeanImputer, LinearInterpolationImputer, KNNPollutionImputer
from src.models.temporal_transformer import CTDITemporalTransformer, SimpleMLPImputer
from src.evaluation.evaluate import evaluate_all_models

def export_cache(config_path="configs/default_config.yaml", output_path="results/eval_cache.npz"):
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
        
    pollutants = cfg["data"]["pollutants"]
    station = cfg["data"]["station_name"]
    window_size = cfg["data"]["window_size"]
    stride = cfg["data"]["stride"]
    missing_rate = cfg["masking"]["missing_rate"]
    mechanism = cfg["masking"]["mechanism"]
    
    raw_csv = download_beijing_air_quality(raw_dir=cfg["data"]["raw_data_dir"], station=station)
    df_clean = preprocess_air_quality_data(raw_csv, feature_cols=pollutants, station=station)
    
    train_df, val_df, test_df = split_time_series(
        df_clean,
        train_ratio=cfg["data"]["train_ratio"],
        val_ratio=cfg["data"]["val_ratio"]
    )
    
    train_norm, val_norm, test_norm, scaler = normalize_datasets(
        train_df, val_df, test_df, feature_cols=pollutants
    )
    
    win_train, ts_train = create_sliding_windows(train_norm, window_size=window_size, stride=stride)
    win_test, ts_test = create_sliding_windows(test_norm, window_size=window_size, stride=stride)
    
    m_train_obs = create_observation_mask(win_train)
    m_test_obs = create_observation_mask(win_test)
    m_test_art, m_test_eval = generate_artificial_mask(m_test_obs, missing_rate=missing_rate, mechanism=mechanism, seed=44)
    x_test_obs = prepare_masked_inputs(win_test, m_test_art)
    
    # Baselines
    mean_imp = MeanImputer().fit(win_train, m_train_obs)
    linear_imp = LinearInterpolationImputer()
    knn_imp = KNNPollutionImputer(n_neighbors=5).fit(win_train, m_train_obs)
    
    # Load trained models
    num_feats = len(pollutants)
    mlp_model = SimpleMLPImputer(num_features=num_feats, window_size=window_size, hidden_dim=128)
    mlp_ckpt = "checkpoints/mlp/best_temporal_transformer.pt"
    if os.path.exists(mlp_ckpt):
        mlp_model.load_state_dict(torch.load(mlp_ckpt, map_location="cpu"))
        
    tf_model = CTDITemporalTransformer(
        num_features=num_feats,
        d_model=cfg["model"]["d_model"],
        nhead=cfg["model"]["nhead"],
        num_layers=cfg["model"]["num_layers"],
        dim_feedforward=cfg["model"]["dim_feedforward"],
        dropout=cfg["model"]["dropout"],
        window_size=window_size
    )
    tf_ckpt = "checkpoints/transformer/best_temporal_transformer.pt"
    if os.path.exists(tf_ckpt):
        tf_model.load_state_dict(torch.load(tf_ckpt, map_location="cpu"))
        
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
        device="cpu"
    )
    
    # Physical transforms
    phys_true = scaler.inverse_transform_array(win_test)
    phys_imputations = {
        m: scaler.inverse_transform_array(arr) for m, arr in imputations.items()
    }
    
    means_arr = np.array([scaler.means[c] for c in pollutants])
    stds_arr = np.array([scaler.stds[c] for c in pollutants])
    
    ts_flat = pd.to_datetime(ts_test.flatten())
    ts_strings = ts_flat.strftime("%Y-%m-%d %H:%M").to_numpy().reshape(ts_test.shape)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    np.savez_compressed(
        output_path,
        x_test_true_norm=win_test,
        x_test_true_phys=phys_true,
        x_test_obs=x_test_obs,
        m_test_art=m_test_art,
        m_test_eval=m_test_eval,
        imp_transformer=phys_imputations["Temporal_Transformer"],
        imp_linear=phys_imputations["Linear_Interpolation"],
        imp_knn=phys_imputations["KNN"],
        imp_mlp=phys_imputations["MLP"],
        imp_mean=phys_imputations["Mean"],
        pollutants=np.array(pollutants),
        means=means_arr,
        stds=stds_arr,
        timestamps=ts_strings
    )
    print(f"[Cache] Successfully saved UI cache to {output_path}")

if __name__ == "__main__":
    export_cache()
