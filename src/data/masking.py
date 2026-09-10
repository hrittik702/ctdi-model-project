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

def compute_missingness_structure_features(mask: np.ndarray) -> np.ndarray:
    """
    Computes structural temporal missingness features strictly from the observation mask:
    1. dt_prev: Normalized steps since last observed point (or window edge).
    2. dt_next: Normalized steps until next observed point (or window edge).
    3. gap_len: Normalized total length of contiguous missing outage.
    4. is_boundary: Binary flag (1 if missing position is adjacent to observed value).

    Args:
        mask: Binary array of shape (..., T, F) where 1=observed, 0=missing.
    Returns:
        features: Array of shape (..., T, 4*F) normalized to [0, 1].
    """
    orig_shape = mask.shape
    if len(orig_shape) == 2:
        # (T, F) -> (1, T, F)
        m = mask[np.newaxis, ...]
    else:
        m = mask
        
    B, T, F = m.shape
    dt_prev = np.zeros_like(m, dtype=np.float32)
    curr = np.zeros((B, 1, F), dtype=np.float32)
    for t in range(T):
        m_t = m[:, t:t+1, :]
        curr = np.where(m_t == 1.0, 0.0, curr + 1.0)
        dt_prev[:, t:t+1, :] = curr
        
    dt_next = np.zeros_like(m, dtype=np.float32)
    curr = np.zeros((B, 1, F), dtype=np.float32)
    for t in range(T - 1, -1, -1):
        m_t = m[:, t:t+1, :]
        curr = np.where(m_t == 1.0, 0.0, curr + 1.0)
        dt_next[:, t:t+1, :] = curr
        
    norm_T = float(T)
    dt_prev = dt_prev * (1.0 - m) / norm_T
    dt_next = dt_next * (1.0 - m) / norm_T
    
    gap_len = np.maximum(0.0, dt_prev * norm_T + dt_next * norm_T - 1.0) / norm_T * (1.0 - m)
    
    prev_obs = np.concatenate([np.ones((B, 1, F), dtype=np.float32), m[:, :-1, :]], axis=1) == 1.0
    next_obs = np.concatenate([m[:, 1:, :], np.ones((B, 1, F), dtype=np.float32)], axis=1) == 1.0
    is_boundary = ((1.0 - m) * ((prev_obs.astype(np.float32) + next_obs.astype(np.float32)) > 0).astype(np.float32))
    
    out = np.concatenate([dt_prev, dt_next, gap_len, is_boundary], axis=-1)
    if len(orig_shape) == 2:
        return out[0]
    return out

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

def generate_curriculum_mask(
    m_obs: np.ndarray,
    epoch: int = 1,
    total_epochs: int = 40,
    seed: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates dynamic masking with curriculum scheduling across training epochs:
    - Early epochs (1-10): Easier random missingness (10-25%) + short blocks (2-4h).
    - Mid epochs (11-25): Moderate missingness (20-40%) + medium blocks (4-8h) + co-pollutant outages.
    - Late epochs (26+): Hard stress conditions (30-60%) + long blocks (8-16h) + multi-pollutant outages.
    """
    if seed is not None:
        np.random.seed(seed)
        
    N, T, F = m_obs.shape
    progress = min(1.0, epoch / max(1, total_epochs))
    
    min_rate = 0.10 + 0.15 * progress
    max_rate = 0.25 + 0.30 * progress
    rates = np.random.uniform(min_rate, max_rate, size=(N, 1, 1)).astype(np.float32)
    
    rand_draw = np.random.rand(N, T, F).astype(np.float32)
    m_art = m_obs.copy()
    m_art[(rand_draw < rates) & (m_obs == 1.0)] = 0.0
    
    # Add contiguous missing blocks (varying from 2h up to 16h as training progresses)
    max_block = int(4 + 12 * progress)
    block_prob = 0.35 + 0.25 * progress
    block_mask = np.random.rand(N, 1, F) < block_prob
    lens = np.random.randint(2, max(3, max_block + 1), size=(N, 1, F))
    starts = np.random.randint(0, np.maximum(1, T - lens + 1), size=(N, 1, F))
    time_indices = np.arange(T).reshape(1, T, 1)
    in_block = (time_indices >= starts) & (time_indices < (starts + lens)) & block_mask
    m_art[in_block & (m_obs == 1.0)] = 0.0
    
    # Multi-pollutant correlated outage for 15-30% of samples (e.g. PM2.5 and PM10 simultaneous outage)
    co_outage = np.random.rand(N, 1, 1) < (0.15 + 0.15 * progress)
    co_start = np.random.randint(0, T - 4, size=(N, 1, 1))
    co_len = np.random.randint(3, 10, size=(N, 1, 1))
    in_co = (time_indices >= co_start) & (time_indices < (co_start + co_len)) & co_outage
    # Apply to PM2.5 (idx 0) and PM10 (idx 1) simultaneously
    m_art[:, :, :2][in_co.squeeze(-1)[:, :, np.newaxis] & (m_obs[:, :, :2] == 1.0)] = 0.0

    
    eval_mask = ((m_obs == 1.0) & (m_art == 0.0)).astype(np.float32)
    return m_art.astype(np.float32), eval_mask

