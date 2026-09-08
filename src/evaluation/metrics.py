"""Evaluation metrics calculated strictly at artificially hidden positions."""

import numpy as np
from typing import Dict, List, Optional

def compute_masked_mae(
    y_pred: np.ndarray,
    y_true: np.ndarray,
    eval_mask: np.ndarray,
    eps: float = 1e-8
) -> float:
    """Mean Absolute Error over artificially hidden entries."""
    valid = (eval_mask == 1.0) & (~np.isnan(y_true)) & (~np.isnan(y_pred))
    if not np.any(valid):
        return 0.0
    return float(np.mean(np.abs(y_pred[valid] - y_true[valid])))

def compute_masked_rmse(
    y_pred: np.ndarray,
    y_true: np.ndarray,
    eval_mask: np.ndarray,
    eps: float = 1e-8
) -> float:
    """Root Mean Square Error over artificially hidden entries."""
    valid = (eval_mask == 1.0) & (~np.isnan(y_true)) & (~np.isnan(y_pred))
    if not np.any(valid):
        return 0.0
    return float(np.sqrt(np.mean(np.square(y_pred[valid] - y_true[valid]))))

def compute_masked_mape(
    y_pred: np.ndarray,
    y_true: np.ndarray,
    eval_mask: np.ndarray,
    eps: float = 1e-3
) -> float:
    """Mean Absolute Percentage Error over artificially hidden entries."""
    valid = (eval_mask == 1.0) & (~np.isnan(y_true)) & (~np.isnan(y_pred))
    if not np.any(valid):
        return 0.0
    abs_true = np.abs(y_true[valid])
    diff = np.abs(y_pred[valid] - y_true[valid])
    pct = (diff / (abs_true + eps)) * 100.0
    return float(np.mean(pct))

def compute_all_metrics(
    y_pred: np.ndarray,
    y_true: np.ndarray,
    eval_mask: np.ndarray,
    feature_names: Optional[List[str]] = None
) -> Dict[str, Dict[str, float]]:
    """
    Computes MAE, RMSE, and MAPE across all features and per individual feature.
    
    Args:
        y_pred: Imputed values (N, T, F)
        y_true: Original values (N, T, F)
        eval_mask: Binary evaluation mask (N, T, F)
        feature_names: Optional feature label list
        
    Returns:
        results: Dict mapping 'overall' and each feature name to metric scores.
    """
    results = {}
    
    # Overall metrics
    overall_mae = compute_masked_mae(y_pred, y_true, eval_mask)
    overall_rmse = compute_masked_rmse(y_pred, y_true, eval_mask)
    overall_mape = compute_masked_mape(y_pred, y_true, eval_mask)
    
    results["overall"] = {
        "MAE": overall_mae,
        "RMSE": overall_rmse,
        "MAPE": overall_mape,
        "eval_count": int(np.sum(eval_mask))
    }
    
    # Per-feature breakdown
    num_features = y_pred.shape[-1]
    for f in range(num_features):
        feat_name = feature_names[f] if (feature_names and f < len(feature_names)) else f"feature_{f}"
        
        f_pred = y_pred[..., f]
        f_true = y_true[..., f]
        f_mask = eval_mask[..., f]
        
        results[feat_name] = {
            "MAE": compute_masked_mae(f_pred, f_true, f_mask),
            "RMSE": compute_masked_rmse(f_pred, f_true, f_mask),
            "MAPE": compute_masked_mape(f_pred, f_true, f_mask),
            "eval_count": int(np.sum(f_mask))
        }
        
    return results
