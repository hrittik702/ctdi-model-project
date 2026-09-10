"""Postprocessing, observation preservation enforcement, denormalization, and integrity verification."""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd


class InferenceIntegrityError(Exception):
    """Raised if observed values were modified or corrupted during inference."""
    pass


def sanitize_val(v: Any) -> Optional[float]:
    """Ensures JSON-compliant float output, converting NaN/Inf to None."""
    if v is None or np.isnan(v) or np.isinf(v):
        return None
    return round(float(v), 2)


def process_and_verify_imputation_window(
    phys_observed: np.ndarray,      # (1, 24, 5) with NaNs at missing positions
    mask: np.ndarray,               # (1, 24, 5) binary mask
    raw_pred_norm: np.ndarray,      # (1, 24, 5) raw predictions in normalized space
    imputed_norm: np.ndarray,       # (1, 24, 5) model imputed in normalized space
    pollutant_means: np.ndarray,    # (5,)
    pollutant_stds: np.ndarray,     # (5,)
    pollutant_names: List[str] = ["PM2.5", "PM10", "NO2", "SO2", "O3"]
) -> Dict[str, Any]:
    """
    Denormalizes predictions, strictly locks observed values, and verifies numerical integrity.
    """
    # 1. Denormalize raw predictions and model imputed to physical scale
    pred_phys = raw_pred_norm * pollutant_stds + pollutant_means
    
    # Non-negativity constraint for physical pollution concentrations
    pred_phys = np.clip(pred_phys, a_min=0.0, a_max=None)

    # 2. Strict observation merge: preserve original physical observations exactly
    # final_phys = mask * phys_observed + (1 - mask) * pred_phys
    final_phys = np.where(mask == 1.0, phys_observed, pred_phys)

    # 3. Observation Integrity Test
    obs_indices = mask == 1.0
    if np.any(obs_indices):
        max_diff = float(np.max(np.abs(final_phys[obs_indices] - phys_observed[obs_indices])))
        if max_diff > 1e-4:
            raise InferenceIntegrityError(
                f"Observed value integrity violation! Observed data altered by {max_diff:.6f} µg/m³"
            )
    else:
        max_diff = 0.0

    # 4. Check for NaNs/Infs in the final imputed output
    if np.isnan(final_phys).any() or np.isinf(final_phys).any():
        raise ValueError("Model output contains NaN or Infinite values at imputed positions.")

    return {
        "final_phys": final_phys,
        "pred_phys": pred_phys,
        "max_observed_deviation": max_diff
    }


def assemble_complete_dataset(
    window_results: List[Dict[str, Any]],
    original_df: pd.DataFrame,
    pollutants: List[str] = ["PM2.5", "PM10", "NO2", "SO2", "O3"]
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Assembles multiple processed 24-hour windows into a continuous imputed DataFrame
    and prepares serialized time-series data for frontend rendering.
    """
    total_rows = len(window_results) * 24
    timestamps = []
    
    obs_dict = {p: [] for p in pollutants}
    imp_dict = {p: [] for p in pollutants}
    pred_dict = {p: [] for p in pollutants}
    mask_dict = {p: [] for p in pollutants}

    imputed_df = pd.DataFrame()
    
    # Collect all timestamps
    all_ts = []
    for w in window_results:
        all_ts.extend([str(t) for t in w["timestamps"]])
    imputed_df["timestamp"] = all_ts[:total_rows]

    # Collect pollutant values
    for f_idx, p in enumerate(pollutants):
        p_obs_list = []
        p_imp_list = []
        p_pred_list = []
        p_mask_list = []

        for w in window_results:
            phys_obs = w["phys_observed"][0, :, f_idx]
            final_imp = w["final_phys"][0, :, f_idx]
            pred = w["pred_phys"][0, :, f_idx]
            m = w["mask"][0, :, f_idx]

            for t in range(24):
                is_observed = (m[t] == 1.0)
                obs_val = sanitize_val(phys_obs[t]) if is_observed else None
                imp_val = sanitize_val(final_imp[t])
                pred_val = sanitize_val(pred[t])

                p_obs_list.append(obs_val)
                p_imp_list.append(imp_val)
                p_pred_list.append(pred_val)
                p_mask_list.append(int(m[t]))

        obs_dict[p] = p_obs_list
        imp_dict[p] = p_imp_list
        pred_dict[p] = p_pred_list
        mask_dict[p] = p_mask_list

        imputed_df[f"{p}_observed"] = p_obs_list
        imputed_df[f"{p}_imputed"] = p_imp_list
        imputed_df[f"{p}_mask"] = p_mask_list

    hours = [f"{i % 24:02d}:00" for i in range(total_rows)]

    serialized_data = {
        "timestamps": all_ts[:total_rows],
        "hours": hours,
        "observed": obs_dict,
        "imputed": imp_dict,
        "predictions": pred_dict,
        "mask": mask_dict
    }

    return imputed_df, serialized_data
