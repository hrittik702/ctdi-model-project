"""Baseline imputation methods for air pollution time-series.

Includes:
1. Mean Imputation
2. Linear Temporal Interpolation
3. K-Nearest Neighbors (KNN) Imputation
4. Multi-Layer Perceptron (MLP) Imputer
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
from sklearn.impute import KNNImputer

class MeanImputer:
    """Imputes missing values with feature-wise mean computed from training observations."""
    def __init__(self):
        self.means: Optional[np.ndarray] = None
        
    def fit(self, x_train: np.ndarray, m_train: np.ndarray) -> "MeanImputer":
        # x_train: (N, T, F), m_train: (N, T, F)
        num_features = x_train.shape[-1]
        self.means = np.zeros(num_features, dtype=np.float32)
        for f in range(num_features):
            valid = (m_train[..., f] == 1.0) & (~np.isnan(x_train[..., f]))
            if np.any(valid):
                self.means[f] = np.mean(x_train[..., f][valid])
            else:
                self.means[f] = 0.0
        return self
        
    def impute(self, x_obs: np.ndarray, m_obs: np.ndarray) -> np.ndarray:
        out = x_obs.copy()
        for f in range(x_obs.shape[-1]):
            missing = (m_obs[..., f] == 0.0)
            out[..., f][missing] = self.means[f]
        return out

class LinearInterpolationImputer:
    """
    Interpolates missing values along the 24-hour temporal dimension.
    Uses linear interpolation for interior gaps and nearest/mean fill for boundaries.
    """
    def __init__(self, fallback_mean: float = 0.0):
        self.fallback_mean = fallback_mean
        
    def fit(self, *args, **kwargs) -> "LinearInterpolationImputer":
        return self
        
    def impute(self, x_obs: np.ndarray, m_obs: np.ndarray) -> np.ndarray:
        # x_obs shape: (N, T=24, F)
        N, T, F = x_obs.shape
        out = x_obs.copy()
        
        for i in range(N):
            for f in range(F):
                vals = out[i, :, f].copy()
                mask = m_obs[i, :, f]
                
                # Replace hidden positions with NaN for pandas interpolation
                vals[mask == 0.0] = np.nan
                s = pd.Series(vals)
                # Linear interpolation in time direction, then forward/backward fill
                s_interp = s.interpolate(method="linear", limit_direction="both")
                # Any remaining NaNs fill with fallback mean
                s_filled = s_interp.fillna(self.fallback_mean).to_numpy()
                
                # Retain observed values exactly, only fill missing
                out[i, :, f] = np.where(mask == 1.0, x_obs[i, :, f], s_filled)
                
        return out

class KNNPollutionImputer:
    """Imputes missing values using K-Nearest Neighbors across 24-hour windows."""
    def __init__(self, n_neighbors: int = 5):
        self.n_neighbors = n_neighbors
        self.imputer = KNNImputer(n_neighbors=n_neighbors, weights="distance")
        
    def fit(self, x_train: np.ndarray, m_train: np.ndarray) -> "KNNPollutionImputer":
        N, T, F = x_train.shape
        flat = x_train.reshape(N, T * F).copy()
        flat[m_train.reshape(N, T * F) == 0.0] = np.nan
        # Subsample for fit if training set is large
        if N > 2000:
            indices = np.random.choice(N, 2000, replace=False)
            flat = flat[indices]
        self.imputer.fit(flat)
        return self
        
    def impute(self, x_obs: np.ndarray, m_obs: np.ndarray) -> np.ndarray:
        N, T, F = x_obs.shape
        flat = x_obs.reshape(N, T * F).copy()
        flat[m_obs.reshape(N, T * F) == 0.0] = np.nan
        
        imputed_flat = self.imputer.transform(flat)
        imputed = imputed_flat.reshape(N, T, F)
        
        # Merge: keep observed values, replace only missing
        out = np.where(m_obs == 1.0, x_obs, imputed)
        return out
