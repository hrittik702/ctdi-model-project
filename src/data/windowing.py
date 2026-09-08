"""24-Hour Sliding Window construction for Spatio-Temporal Imputation."""

import numpy as np
import pandas as pd
from typing import Tuple, List, Optional

def create_sliding_windows(
    df: pd.DataFrame,
    window_size: int = 24,
    stride: int = 1
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Constructs 24-hour sliding window samples from a continuous hourly time series.
    
    Args:
        df: Processed DataFrame indexed by continuous hourly timestamps.
        window_size: Number of hours per sample (default: 24).
        stride: Sliding stride in hours (default: 1).
        
    Returns:
        windows: Array of shape (N_samples, window_size, num_features).
        timestamps: Array of shape (N_samples, window_size) containing pd.Timestamp objects.
    """
    data_values = df.to_numpy(dtype=np.float32)
    time_indices = df.index.to_numpy()
    
    total_hours, num_features = data_values.shape
    if total_hours < window_size:
        raise ValueError(f"Total series length ({total_hours}) must be >= window_size ({window_size})")
        
    sample_starts = range(0, total_hours - window_size + 1, stride)
    num_samples = len(sample_starts)
    
    windows = np.zeros((num_samples, window_size, num_features), dtype=np.float32)
    sample_times = []
    
    for i, start in enumerate(sample_starts):
        end = start + window_size
        windows[i] = data_values[start:end]
        sample_times.append(time_indices[start:end])
        
    timestamps = np.array(sample_times)
    return windows, timestamps

def reconstruct_series_from_windows(
    windows: np.ndarray,
    total_length: int,
    window_size: int = 24,
    stride: int = 1
) -> np.ndarray:
    """
    Averages overlapping predictions back into a continuous 1D/2D series.
    Useful when generating a complete reconstructed time-series.
    """
    num_features = windows.shape[-1]
    reconstructed = np.zeros((total_length, num_features), dtype=np.float32)
    counts = np.zeros((total_length, num_features), dtype=np.float32)
    
    sample_starts = range(0, total_length - window_size + 1, stride)
    for i, start in enumerate(sample_starts):
        end = start + window_size
        reconstructed[start:end] += windows[i]
        counts[start:end] += 1.0
        
    # Avoid division by zero
    valid_mask = counts > 0
    reconstructed[valid_mask] /= counts[valid_mask]
    return reconstructed
