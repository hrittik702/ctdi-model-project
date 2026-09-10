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
    eps: float = 1e-3,
    min_threshold: float = 1.0
) -> float:
    """
    Mean Absolute Percentage Error over artificially hidden entries.
    Filters out near-zero values (abs_true < min_threshold) to prevent division-by-zero explosions.
    """
    valid = (eval_mask == 1.0) & (~np.isnan(y_true)) & (~np.isnan(y_pred)) & (np.abs(y_true) >= min_threshold)
    if not np.any(valid):
        return 0.0
    abs_true = np.abs(y_true[valid])
    diff = np.abs(y_pred[valid] - y_true[valid])
    pct = (diff / (abs_true + eps)) * 100.0
    return float(np.mean(pct))

def compute_masked_bias(
    y_pred: np.ndarray,
    y_true: np.ndarray,
    eval_mask: np.ndarray
) -> float:
    """Mean Bias Error over artificially hidden entries: mean(pred - true)."""
    valid = (eval_mask == 1.0) & (~np.isnan(y_true)) & (~np.isnan(y_pred))
    if not np.any(valid):
        return 0.0
    return float(np.mean(y_pred[valid] - y_true[valid]))

def compute_masked_correlation(
    y_pred: np.ndarray,
    y_true: np.ndarray,
    eval_mask: np.ndarray
) -> float:
    """Pearson correlation coefficient over artificially hidden entries."""
    valid = (eval_mask == 1.0) & (~np.isnan(y_true)) & (~np.isnan(y_pred))
    if np.sum(valid) < 2:
        return 0.0
    p = y_pred[valid]
    t = y_true[valid]
    p_std = np.std(p)
    t_std = np.std(t)
    if p_std < 1e-8 or t_std < 1e-8:
        return 0.0
    corr = np.corrcoef(p, t)[0, 1]
    return float(corr) if not np.isnan(corr) else 0.0

def compute_peak_metrics(
    y_pred: np.ndarray,
    y_true: np.ndarray,
    eval_mask: np.ndarray,
    percentiles: Optional[List[float]] = None
) -> Dict[str, Dict[str, float]]:
    """
    Computes MAE and RMSE on the top percentiles of ground-truth values (e.g. top 5%, 10%, 20%).
    """
    if percentiles is None:
        percentiles = [5.0, 10.0, 20.0]
        
    valid = (eval_mask == 1.0) & (~np.isnan(y_true)) & (~np.isnan(y_pred))
    if not np.any(valid):
        return {}
        
    results = {}
    vals = y_true[valid]
    for pct in percentiles:
        thr = float(np.percentile(vals, 100.0 - pct))
        peak_mask = valid & (y_true >= thr)
        cnt = int(np.sum(peak_mask))
        if cnt == 0:
            mae = 0.0
            rmse = 0.0
        else:
            mae = float(np.mean(np.abs(y_pred[peak_mask] - y_true[peak_mask])))
            rmse = float(np.sqrt(np.mean(np.square(y_pred[peak_mask] - y_true[peak_mask]))))
        results[f"top_{int(pct)}pct"] = {
            "threshold": round(thr, 2),
            "count": cnt,
            "MAE": round(mae, 3),
            "RMSE": round(rmse, 3)
        }
    return results

def compute_gap_length_tensor(m_art: np.ndarray) -> np.ndarray:
    """
    Computes the contiguous missing run length for each position in (N, T, F).
    """
    N, T, F = m_art.shape
    gap_len = np.zeros_like(m_art, dtype=np.int32)
    for n in range(N):
        for f in range(F):
            start = None
            for t in range(T):
                if m_art[n, t, f] == 0.0:
                    if start is None:
                        start = t
                else:
                    if start is not None:
                        length = t - start
                        gap_len[n, start:t, f] = length
                        start = None
            if start is not None:
                gap_len[n, start:T, f] = T - start
    return gap_len

def compute_gap_metrics(
    y_pred: np.ndarray,
    y_true: np.ndarray,
    eval_mask: np.ndarray,
    m_art: np.ndarray,
    gap_bins: Optional[List[tuple]] = None
) -> Dict[str, Dict[str, float]]:
    """
    Computes MAE and RMSE binned by missing run length (e.g. short 1-2h, medium 3-6h, long 7-24h).
    """
    if gap_bins is None:
        gap_bins = [(1, 2, "short_1_2h"), (3, 6, "medium_3_6h"), (7, 24, "long_7_24h")]
        
    gap_len = compute_gap_length_tensor(m_art)
    results = {}
    for g_min, g_max, label in gap_bins:
        bin_mask = eval_mask * ((gap_len >= g_min) & (gap_len <= g_max)).astype(float)
        valid = (bin_mask == 1.0) & (~np.isnan(y_true)) & (~np.isnan(y_pred))
        cnt = int(np.sum(valid))
        if cnt == 0:
            mae = 0.0
            rmse = 0.0
        else:
            mae = float(np.mean(np.abs(y_pred[valid] - y_true[valid])))
            rmse = float(np.sqrt(np.mean(np.square(y_pred[valid] - y_true[valid]))))
        results[label] = {
            "range": f"{g_min}-{g_max}h",
            "count": cnt,
            "MAE": round(mae, 3),
            "RMSE": round(rmse, 3)
        }
    return results

def compute_all_metrics(
    y_pred: np.ndarray,
    y_true: np.ndarray,
    eval_mask: np.ndarray,
    feature_names: Optional[List[str]] = None,
    m_art: Optional[np.ndarray] = None
) -> Dict[str, Dict[str, float]]:
    """
    Computes MAE, RMSE, MAPE, Bias, and Correlation across all features and per individual feature.
    Optionally computes peak and gap length breakdowns if m_art is supplied.
    
    Args:
        y_pred: Imputed values (N, T, F)
        y_true: Original values (N, T, F)
        eval_mask: Binary evaluation mask (N, T, F)
        feature_names: Optional feature label list
        m_art: Optional artificial missingness mask (N, T, F) for gap metrics
        
    Returns:
        results: Dict mapping 'overall' and each feature name to metric scores.
    """
    results = {}
    
    # Overall metrics
    overall_mae = compute_masked_mae(y_pred, y_true, eval_mask)
    overall_rmse = compute_masked_rmse(y_pred, y_true, eval_mask)
    overall_mape = compute_masked_mape(y_pred, y_true, eval_mask)
    overall_bias = compute_masked_bias(y_pred, y_true, eval_mask)
    overall_corr = compute_masked_correlation(y_pred, y_true, eval_mask)
    
    results["overall"] = {
        "MAE": round(overall_mae, 3),
        "RMSE": round(overall_rmse, 3),
        "MAPE": round(overall_mape, 2),
        "Bias": round(overall_bias, 3),
        "Correlation": round(overall_corr, 3),
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
            "MAE": round(compute_masked_mae(f_pred, f_true, f_mask), 3),
            "RMSE": round(compute_masked_rmse(f_pred, f_true, f_mask), 3),
            "MAPE": round(compute_masked_mape(f_pred, f_true, f_mask), 2),
            "Bias": round(compute_masked_bias(f_pred, f_true, f_mask), 3),
            "Correlation": round(compute_masked_correlation(f_pred, f_true, f_mask), 3),
            "eval_count": int(np.sum(f_mask))
        }
        
        # Add peak metrics per pollutant
        peak_res = compute_peak_metrics(f_pred, f_true, f_mask, [5.0, 10.0, 20.0])
        for pk_key, pk_val in peak_res.items():
            results[feat_name][f"Peak_{pk_key}_MAE"] = pk_val["MAE"]
            
    if m_art is not None:
        gap_res = compute_gap_metrics(y_pred, y_true, eval_mask, m_art)
        results["gap_breakdown"] = gap_res
        
    return results

