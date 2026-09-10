"""Preprocessing adapter for CTDI Temporal Model inference.

Constructs:
1. Exact 9-channel environmental context (4 calendar + 5 meteorological)
2. Exact 5-channel observation mask (1=observed, 0=missing)
3. Normalized 5-channel observed pollutant tensor (0 where missing)
4. Linear temporal interpolation prior via existing baseline
5. Saved training normalization and denormalization routines
"""

import os
import json
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import pandas as pd

from src.models.baselines import LinearInterpolationImputer


STATS_PATH = "data/processed/normalization_stats.json"

POLLUTANT_STAT_KEYS = {
    "PM2.5": "PM2_5_ugm3",
    "PM10": "PM10_ugm3",
    "NO2": "NO2_ugm3",
    "SO2": "SO2_ugm3",
    "O3": "O3_ugm3"
}

WEATHER_STAT_KEYS = [
    "Temp_2m_C",
    "Humidity_Percent",
    "Wind_Speed_10m_kmh",
    "Wind_Dir_10m",
    "Precipitation_mm"
]


class PreprocessingAdapter:
    """Manages feature construction and normalization using saved training statistics."""

    def __init__(self, stats_path: str = STATS_PATH):
        if not os.path.exists(stats_path):
            raise FileNotFoundError(f"Normalization statistics file not found: {stats_path}")
        with open(stats_path, "r") as f:
            self.norm_stats = json.load(f)

        self.linear_imputer = LinearInterpolationImputer(fallback_mean=0.0)

        # Pre-extract means and stds for 5 pollutants
        self.pollutant_means = np.array([
            self.norm_stats[POLLUTANT_STAT_KEYS[p]]["mean"] for p in ["PM2.5", "PM10", "NO2", "SO2", "O3"]
        ], dtype=np.float32)

        self.pollutant_stds = np.array([
            self.norm_stats[POLLUTANT_STAT_KEYS[p]]["standard_deviation"] for p in ["PM2.5", "PM10", "NO2", "SO2", "O3"]
        ], dtype=np.float32)
        self.pollutant_stds = np.where(self.pollutant_stds == 0, 1.0, self.pollutant_stds)

    def derive_calendar_features(self, timestamps: pd.Series) -> np.ndarray:
        """
        Derives and standardizes 4 calendar channels from timestamps:
        0. Hour (0..23): (Hour - 11.5) / 6.928
        1. Day of Week (0..6): (Day - 3.0) / 2.0
        2. Month (1..12): (Month - 6.5) / 3.452
        3. Season_Code (0..3): (Season - 1.5) / 1.118
           Where Winter=0, Summer=1, Monsoon=2, Post_Monsoon=3
        """
        T = len(timestamps)
        cal = np.zeros((T, 4), dtype=np.float32)

        ts = pd.to_datetime(timestamps)
        hours = ts.dt.hour.to_numpy(dtype=np.float32)
        days = ts.dt.dayofweek.to_numpy(dtype=np.float32)
        months = ts.dt.month.to_numpy(dtype=np.float32)

        # Map month to season
        # Dec, Jan, Feb -> Winter (0)
        # Mar, Apr, May -> Summer (1)
        # Jun, Jul, Aug, Sep -> Monsoon (2)
        # Oct, Nov -> Post_Monsoon (3)
        season_codes = np.zeros(T, dtype=np.float32)
        for i, m in enumerate(months):
            if m in [12, 1, 2]:
                season_codes[i] = 0.0
            elif m in [3, 4, 5]:
                season_codes[i] = 1.0
            elif m in [6, 7, 8, 9]:
                season_codes[i] = 2.0
            else:
                season_codes[i] = 3.0

        cal[:, 0] = (hours - 11.5) / 6.928
        cal[:, 1] = (days - 3.0) / 2.0
        cal[:, 2] = (months - 6.5) / 3.452
        cal[:, 3] = (season_codes - 1.5) / 1.118

        return cal

    def derive_meteorological_features(
        self,
        df: pd.DataFrame
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Standardizes 5 meteorological channels using training statistics.
        If a weather column is missing or all-NaN, uses training mean (z = 0.0).
        """
        T = len(df)
        meteo = np.zeros((T, 5), dtype=np.float32)
        fallback_cols = []

        for idx, col in enumerate(WEATHER_STAT_KEYS):
            mean = float(self.norm_stats[col]["mean"])
            std = float(self.norm_stats[col]["standard_deviation"])
            std = std if std > 0 else 1.0

            if col in df.columns and not df[col].isna().all():
                raw_vals = df[col].to_numpy(dtype=np.float32)
                # Fill any isolated NaNs with column mean or training mean
                col_mean = np.nanmean(raw_vals) if not np.isnan(np.nanmean(raw_vals)) else mean
                raw_vals = np.where(np.isnan(raw_vals), col_mean, raw_vals)
                meteo[:, idx] = (raw_vals - mean) / std
            else:
                # Fallback to training distribution center: z = 0.0
                meteo[:, idx] = 0.0
                fallback_cols.append(col)

        return meteo, fallback_cols

    def prepare_window_tensors(
        self,
        window_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Converts a 24-row DataFrame into model tensors:
        - raw_observed_phys: (1, 24, 5) float32 in physical units (with NaNs where missing)
        - mask: (1, 24, 5) float32 (1=observed, 0=missing)
        - x_norm_obs: (1, 24, 5) float32 normalized observed (0 where missing)
        - x_prior_norm: (1, 24, 5) float32 linear temporal interpolation prior
        - context: (1, 24, 9) float32 calendar + weather features
        """
        if len(window_df) != 24:
            raise ValueError(f"Window must contain exactly 24 rows, got {len(window_df)}")

        # 1. Extract raw physical pollutant values
        phys_vals = window_df[["PM2.5", "PM10", "NO2", "SO2", "O3"]].to_numpy(dtype=np.float32)
        
        # 2. Binary mask: 1 where observed (not NaN), 0 where missing
        mask = (~np.isnan(phys_vals)).astype(np.float32)

        # 3. Normalize observed values using saved training distribution
        norm_vals = (phys_vals - self.pollutant_means) / self.pollutant_stds
        # Set missing entries to 0.0 in model input
        x_norm_obs = np.where(mask == 1.0, norm_vals, 0.0)

        # 4. Construct continuous linear temporal interpolation prior
        # Using the existing LinearInterpolationImputer
        x_prior_norm = self.linear_imputer.impute(
            np.expand_dims(x_norm_obs, axis=0),
            np.expand_dims(mask, axis=0)
        )[0].astype(np.float32)

        # 5. Construct 9 context features
        cal_features = self.derive_calendar_features(window_df["timestamp"])
        meteo_features, fallback_weather = self.derive_meteorological_features(window_df)
        context = np.concatenate([cal_features, meteo_features], axis=-1)  # (24, 9)

        return {
            "phys_vals": np.expand_dims(phys_vals, axis=0),
            "mask": np.expand_dims(mask, axis=0),
            "x_norm_obs": np.expand_dims(x_norm_obs, axis=0),
            "x_prior_norm": np.expand_dims(x_prior_norm, axis=0),
            "context": np.expand_dims(context, axis=0),
            "fallback_weather": fallback_weather,
            "timestamps": window_df["timestamp"].tolist()
        }

    def denormalize_pollutants(self, norm_arr: np.ndarray) -> np.ndarray:
        """
        Denormalizes an array of shape (..., 5) back to physical units (ug/m3).
        y = norm * std + mean
        """
        return norm_arr * self.pollutant_stds + self.pollutant_means
