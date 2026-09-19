"""Feature normalization engine for multi-modal air pollution imputation.

Fits normalization statistics strictly on the training partition (2019-01-01 to 2021-02-05)
to guarantee zero data leakage into validation or test partitions.

Supports:
- Standard Z-Score Normalization ((x - mean) / std) [PRIMARY CANONICAL CONTRACT]
- Min-Max Scaling to [0, 1] [ABLATION CONTRACT]
- Robust Scaling ((x - median) / IQR) [ABLATION CONTRACT]
- Log1p scaling for zero-inflated rainfall [ABLATION CONTRACT]
- Circular decomposition for wind direction: sin(theta), cos(theta) [ABLATION CONTRACT]
- Exact back-transformation (denormalization)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


CANONICAL_13_CHANNELS = [
    "pm25",                # 0: PM2.5 (ug/m3)
    "pm10",                # 1: PM10 (ug/m3)
    "no2",                 # 2: NO2 (ug/m3)
    "so2",                 # 3: SO2 (ug/m3)
    "o3",                  # 4: O3 (ug/m3)
    "pressure",            # 5: Surface atmospheric pressure (hPa)
    "relative_humidity",   # 6: Relative humidity (%)
    "temperature",         # 7: Ambient temperature (deg C)
    "rainfall",            # 8: Hourly rainfall accumulation (mm/h)
    "wind_direction",      # 9: Wind direction (compass degrees 1-360)
    "wind_speed",          # 10: Wind speed (m/s)
    "traffic_speed",       # 11: Corridor traffic speed (km/h)
    "traffic_congestion",  # 12: Speed saturation / congestion index [0, 1]
]

POLLUTANT_CHANNELS = ["pm25", "pm10", "no2", "so2", "o3"]
MET_CHANNELS = ["pressure", "relative_humidity", "temperature", "rainfall", "wind_direction", "wind_speed"]
TRAFFIC_CHANNELS = ["traffic_speed", "traffic_congestion"]


class FeatureNormalizer:
    """Computes, stores, and applies normalization statistics strictly on training data."""

    def __init__(self, stats: Optional[Dict[str, Any]] = None):
        """Initialize normalizer with existing statistics or empty dictionary."""
        self.stats: Dict[str, Any] = stats or {}
        self.is_fitted: bool = bool(stats and "channels" in stats)

    def fit_from_dataframe(self, train_df: pd.DataFrame) -> Dict[str, Any]:
        """Fit normalization parameters on training split dataframe.
        
        Args:
            train_df: DataFrame containing the 13 canonical channels for training timestamps only.
            
        Returns:
            Dictionary of computed statistics.
        """
        stats_dict: Dict[str, Any] = {
            "num_samples": int(len(train_df)),
            "channels": {},
        }

        for ch in CANONICAL_13_CHANNELS:
            s = train_df[ch].dropna()
            mean_val = float(s.mean())
            std_val = float(s.std())
            if std_val < 1e-6:
                std_val = 1.0

            q25 = float(s.quantile(0.25))
            median_val = float(s.median())
            q75 = float(s.quantile(0.75))
            iqr_val = float(q75 - q25)
            if iqr_val < 1e-6:
                iqr_val = 1.0

            min_val = float(s.min())
            max_val = float(s.max())
            if max_val - min_val < 1e-6:
                max_val = min_val + 1.0

            ch_stats: Dict[str, Any] = {
                "mean": mean_val,
                "std": std_val,
                "median": median_val,
                "iqr": iqr_val,
                "q25": q25,
                "q75": q75,
                "min": min_val,
                "max": max_val,
            }

            # Rainfall log1p parameters
            if ch == "rainfall":
                s_log = np.log1p(s.clip(lower=0))
                ch_stats["log1p_mean"] = float(s_log.mean())
                ch_stats["log1p_std"] = float(s_log.std()) if s_log.std() > 1e-6 else 1.0

            stats_dict["channels"][ch] = ch_stats

        self.stats = stats_dict
        self.is_fitted = True
        return self.stats

    def transform(
        self,
        data: np.ndarray,
        mode: str = "z_score",
        fill_nan_with: Optional[float] = 0.0,
    ) -> np.ndarray:
        """Normalize input array of shape (..., 13).
        
        Args:
            data: Array with last dimension equal to 13.
            mode: 'z_score' (PRIMARY), 'min_max', 'robust', or 'log1p'.
            fill_nan_with: Value to fill NaNs with (e.g. 0.0 for masked inputs), or None.
            
        Returns:
            Normalized array of identical shape.
        """
        if not self.is_fitted:
            raise RuntimeError("FeatureNormalizer is not fitted. Call fit() or load() first.")

        norm_data = np.copy(data).astype(np.float32)
        shape_13 = data.shape[-1]
        if shape_13 != 13:
            raise ValueError(f"Expected last dimension 13, got {shape_13}")

        for c, ch in enumerate(CANONICAL_13_CHANNELS):
            ch_s = self.stats["channels"][ch]
            col = norm_data[..., c]

            if mode == "z_score":
                col_norm = (col - ch_s["mean"]) / ch_s["std"]
            elif mode == "min_max":
                col_norm = (col - ch_s["min"]) / (ch_s["max"] - ch_s["min"])
            elif mode == "robust":
                col_norm = (col - ch_s["median"]) / ch_s["iqr"]
            elif mode == "log1p":
                if ch == "rainfall":
                    # Specialized log1p standardization for zero-inflated rainfall
                    col_safe = np.clip(col, 0.0, None)
                    col_log = np.log1p(col_safe)
                    col_norm = (col_log - ch_s["log1p_mean"]) / ch_s["log1p_std"]
                else:
                    col_norm = (col - ch_s["mean"]) / ch_s["std"]
            else:
                raise ValueError(f"Unknown normalization mode: {mode}. Expected 'z_score', 'min_max', 'robust', or 'log1p'.")

            if fill_nan_with is not None:
                col_norm = np.nan_to_num(col_norm, nan=fill_nan_with)

            norm_data[..., c] = col_norm

        return norm_data

    def denormalize(
        self,
        norm_data: np.ndarray,
        mode: str = "z_score",
        channels: Optional[List[Union[int, str]]] = None,
    ) -> np.ndarray:
        """Back-transform normalized data to original physical units.
        
        Args:
            norm_data: Array of shape (..., C).
            mode: Normalization mode used ('z_score', 'min_max', 'robust', or 'log1p').
            channels: If C < 13 (e.g., criteria pollutants C=5), list of channel names or indices.
                      If None, assumes all 13 canonical channels.
                      
        Returns:
            Denormalized array in original physical units.
        """
        if not self.is_fitted:
            raise RuntimeError("FeatureNormalizer is not fitted.")

        orig_data = np.copy(norm_data).astype(np.float32)
        c_dim = norm_data.shape[-1]

        if channels is None:
            if c_dim != 13:
                raise ValueError(f"channels is None but last dimension is {c_dim} (expected 13)")
            target_channels = CANONICAL_13_CHANNELS
        else:
            if len(channels) != c_dim:
                raise ValueError(f"Length of channels ({len(channels)}) != last dim ({c_dim})")
            target_channels = [CANONICAL_13_CHANNELS[ch] if isinstance(ch, int) else ch for ch in channels]

        for idx, ch in enumerate(target_channels):
            ch_s = self.stats["channels"][ch]
            col = orig_data[..., idx]

            if mode == "z_score":
                col_orig = col * ch_s["std"] + ch_s["mean"]
            elif mode == "min_max":
                col_orig = col * (ch_s["max"] - ch_s["min"]) + ch_s["min"]
            elif mode == "robust":
                col_orig = col * ch_s["iqr"] + ch_s["median"]
            elif mode == "log1p":
                if ch == "rainfall":
                    col_unnorm_log = col * ch_s["log1p_std"] + ch_s["log1p_mean"]
                    col_orig = np.expm1(col_unnorm_log)
                    col_orig = np.clip(col_orig, 0.0, None)
                else:
                    col_orig = col * ch_s["std"] + ch_s["mean"]
            else:
                raise ValueError(f"Unknown normalization mode: {mode}")

            orig_data[..., idx] = col_orig

        return orig_data

    def transform_circular_wind(self, data: np.ndarray) -> np.ndarray:
        """Expand 13-channel tensor to 14 channels by decomposing wind_direction into sin & cos.
        
        Preserves channels 0..8 unchanged.
        Channel 9 (wind_direction degrees) becomes:
            New Channel 9: sin(2 * pi * wd / 360)
            New Channel 10: cos(2 * pi * wd / 360)
        Channels 10..12 (wind_speed, traffic_speed, traffic_congestion) become channels 11..13.
        
        Args:
            data: Array of shape (..., 13).
            
        Returns:
            Array of shape (..., 14).
        """
        if data.shape[-1] != 13:
            raise ValueError(f"Expected last dimension 13, got {data.shape[-1]}")

        wd = data[..., 9]
        rad = np.radians(wd)
        sin_wd = np.sin(rad)
        cos_wd = np.cos(rad)

        parts = [
            data[..., 0:9],           # 0..8: pm25, pm10, no2, so2, o3, pres, rh, temp, rain
            sin_wd[..., np.newaxis],  # 9: sin(wd)
            cos_wd[..., np.newaxis],  # 10: cos(wd)
            data[..., 10:13],         # 11..13: wind_speed, traffic_speed, traffic_congestion
        ]
        return np.concatenate(parts, axis=-1)

    def save(self, filepath: Union[str, Path]):
        """Save fitted statistics to JSON file."""
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "FeatureNormalizer":
        """Load fitted statistics from JSON file."""
        p = Path(filepath)
        if not p.exists():
            raise FileNotFoundError(f"Statistics file not found: {p}")
        with open(p, "r", encoding="utf-8") as f:
            stats = json.load(f)
        return cls(stats=stats)
