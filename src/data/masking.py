"""Observation and Artificial Missingness Mask generation."""

import numpy as np
from typing import Tuple, Optional

def create_observation_mask(data: np.ndarray) -> np.ndarray:
    """
    Creates binary observation mask:
    1 where value is observed (not NaN), 0 where value is naturally missing (NaN).
    
    Args:
        data: Array of shape (..., num_features) with potential NaNs.
    Returns:
        mask: Binary float32 array of shape (..., num_features).
    """
    return (~np.isnan(data)).astype(np.float32)

def generate_artificial_mask(
    m_obs: np.ndarray,
    missing_rate: float = 0.30,
    mechanism: str = "random",
    block_length: int = 4,
    seed: Optional[int] = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates artificial missingness masks for controlled training & evaluation.
    
    Args:
        m_obs: Natural observation mask (1=observed, 0=naturally missing).
        missing_rate: Target fraction of observed entries to hide (e.g. 0.30).
        mechanism: "random" (MCAR) or "block" (consecutive hours missing).
        block_length: Duration of missing block in hours if mechanism=="block".
        seed: Random seed for reproducibility.
        
    Returns:
        m_art: Model visibility mask (1=model can see, 0=hidden or naturally missing).
        eval_mask: Target evaluation mask (1=artificially hidden ground-truth, 0=otherwise).
                   eval_mask = m_obs * (1 - m_art).
    """
    if seed is not None:
        np.random.seed(seed)
        
    shape = m_obs.shape
    m_art = m_obs.copy()
    
    if mechanism == "random":
        # Uniform random missingness across observed coordinates
        rand_draw = np.random.rand(*shape)
        # Only hide where naturally observed
        art_hidden = (rand_draw < missing_rate) & (m_obs == 1.0)
        m_art[art_hidden] = 0.0
        
    elif mechanism == "block":
        # Consecutive hours missing per sample/channel
        # m_obs shape: (N, T=24, F)
        if len(shape) == 3:
            N, T, F = shape
            for i in range(N):
                for f in range(F):
                    if np.random.rand() < missing_rate:
                        # Pick random start hour
                        max_start = max(0, T - block_length)
                        start_h = np.random.randint(0, max_start + 1)
                        end_h = min(T, start_h + block_length)
                        m_art[i, start_h:end_h, f] = 0.0
        else:
            rand_draw = np.random.rand(*shape)
            art_hidden = (rand_draw < missing_rate) & (m_obs == 1.0)
            m_art[art_hidden] = 0.0
    else:
        raise ValueError(f"Unknown missingness mechanism: {mechanism}")
        
    # eval_mask: 1 where original ground truth was observed AND we artificially hid it
    eval_mask = (m_obs == 1.0) & (m_art == 0.0)
    return m_art.astype(np.float32), eval_mask.astype(np.float32)

def prepare_masked_inputs(
    x_true: np.ndarray,
    m_art: np.ndarray,
    fill_value: float = 0.0
) -> np.ndarray:
    """
    Zeros or fills values where m_art == 0 to provide input to models.
    """
    x_obs = np.where(m_art == 1.0, x_true, fill_value)
    # Ensure any remaining NaNs are replaced by fill_value
    x_obs = np.nan_to_num(x_obs, nan=fill_value)
    return x_obs.astype(np.float32)
