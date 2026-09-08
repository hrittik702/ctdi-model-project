"""Benchmark evaluation and comparative analysis across all imputation methods."""

import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple
from src.evaluation.metrics import compute_all_metrics
from src.models.baselines import MeanImputer, LinearInterpolationImputer, KNNPollutionImputer
from src.data.preprocessing import AirPollutionScaler

def evaluate_all_models(
    x_test_true: np.ndarray,
    x_test_obs: np.ndarray,
    m_test_art: np.ndarray,
    eval_mask: np.ndarray,
    feature_names: List[str],
    scaler: Optional[AirPollutionScaler] = None,
    mean_imputer: Optional[MeanImputer] = None,
    linear_imputer: Optional[LinearInterpolationImputer] = None,
    knn_imputer: Optional[KNNPollutionImputer] = None,
    mlp_model: Optional[nn.Module] = None,
    transformer_model: Optional[nn.Module] = None,
    device: str = "cpu"
) -> Tuple[pd.DataFrame, Dict[str, np.ndarray]]:
    """
    Evaluates all baseline and neural imputation models on the test set.
    
    Returns:
        summary_df: Formatted comparison table of MAE, RMSE, and MAPE.
        imputations: Dictionary of complete imputed 3D arrays for each model.
    """
    imputations: Dict[str, np.ndarray] = {}
    
    # 1. Mean Baseline
    if mean_imputer is not None:
        imputations["Mean"] = mean_imputer.impute(x_test_obs, m_test_art)
        
    # 2. Linear Interpolation Baseline
    if linear_imputer is not None:
        imputations["Linear_Interpolation"] = linear_imputer.impute(x_test_obs, m_test_art)
        
    # 3. KNN Baseline
    if knn_imputer is not None:
        imputations["KNN"] = knn_imputer.impute(x_test_obs, m_test_art)
        
    # 4. MLP Baseline
    if mlp_model is not None:
        mlp_model.eval()
        with torch.no_grad():
            t_obs = torch.tensor(x_test_obs, dtype=torch.float32).to(device)
            t_mask = torch.tensor(m_test_art, dtype=torch.float32).to(device)
            mlp_imp, _ = mlp_model(t_obs, t_mask)
            imputations["MLP"] = mlp_imp.cpu().numpy()
            
    # 5. CTDI Temporal Transformer
    if transformer_model is not None:
        transformer_model.eval()
        with torch.no_grad():
            t_obs = torch.tensor(x_test_obs, dtype=torch.float32).to(device)
            t_mask = torch.tensor(m_test_art, dtype=torch.float32).to(device)
            tf_imp, _ = transformer_model(t_obs, t_mask)
            imputations["Temporal_Transformer"] = tf_imp.cpu().numpy()
            
    rows = []
    for model_name, imp_arr in imputations.items():
        # Evaluation in normalized space
        norm_metrics = compute_all_metrics(imp_arr, x_test_true, eval_mask, feature_names)
        
        # Evaluation in original physical units (if scaler is provided)
        if scaler is not None:
            phys_imp = scaler.inverse_transform_array(imp_arr)
            phys_true = scaler.inverse_transform_array(x_test_true)
            phys_metrics = compute_all_metrics(phys_imp, phys_true, eval_mask, feature_names)
            
            rows.append({
                "Model": model_name,
                "MAE (Original Units)": round(phys_metrics["overall"]["MAE"], 3),
                "RMSE (Original Units)": round(phys_metrics["overall"]["RMSE"], 3),
                "MAPE (%)": round(phys_metrics["overall"]["MAPE"], 2),
                "MAE (Norm)": round(norm_metrics["overall"]["MAE"], 4),
                "RMSE (Norm)": round(norm_metrics["overall"]["RMSE"], 4),
            })
        else:
            rows.append({
                "Model": model_name,
                "MAE": round(norm_metrics["overall"]["MAE"], 4),
                "RMSE": round(norm_metrics["overall"]["RMSE"], 4),
                "MAPE (%)": round(norm_metrics["overall"]["MAPE"], 2),
            })
            
    summary_df = pd.DataFrame(rows).sort_values(by=list(rows[0].keys())[1])
    return summary_df, imputations
