"""Missingness robustness and multi-rate degradation analysis."""

from typing import Dict, List, Any
import numpy as np


def compute_robustness_curve(
    models: List[Any],
    x_true_phys: np.ndarray,
    x_true_norm: np.ndarray,
    context: np.ndarray,
    rates: List[float] = [0.10, 0.20, 0.30, 0.50, 0.70],
    seed: int = 42
) -> Dict[str, Any]:
    """
    Evaluates selected models across escalating corruption rates (e.g. 10% to 70%)
    to quantify degradation resilience under identical masking per rate.
    """
    from src.data.masking import generate_artificial_mask

    N, T, F = x_true_phys.shape
    curve_data = []

    for rate in rates:
        np.random.seed(seed)
        m_obs = np.ones((N, T, F), dtype=np.float32)
        m_art, m_eval = generate_artificial_mask(m_obs, missing_rate=rate, mechanism="random", seed=seed)
        x_obs_norm = np.where(m_art == 1.0, x_true_norm, 0.0)

        entry = {
            "missing_rate": int(rate * 100),
            "rate_label": f"{int(rate * 100)}%",
            "eval_points": int(np.sum(m_eval))
        }

        for model_runner in models:
            try:
                imp_norm, _ = model_runner.predict(x_obs_norm, m_art, context)
                # Denormalize
                means = np.array([67.6, 119.2, 46.2, 41.2, 81.1], dtype=np.float32)
                stds = np.array([42.9, 70.7, 35.0, 34.1, 61.9], dtype=np.float32)
                imp_phys = imp_norm * stds + means
                valid = (m_eval == 1.0) & (~np.isnan(x_true_phys))
                if np.any(valid):
                    mae = float(np.mean(np.abs(imp_phys[valid] - x_true_phys[valid])))
                    entry[model_runner.id] = round(mae, 2)
                else:
                    entry[model_runner.id] = None
            except Exception:
                entry[model_runner.id] = None

        curve_data.append(entry)

    return {
        "rates": [int(r * 100) for r in rates],
        "curve": curve_data
    }
