"""Data preprocessing, timestamp alignment, and normalization for air pollution time-series."""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Optional
from sklearn.preprocessing import StandardScaler

def clean_and_align_timestamps(df: pd.DataFrame, station: Optional[str] = None) -> pd.DataFrame:
    """
    Constructs a continuous hourly time series from raw records.
    Filters by station if multi-station, checks impossible negative values.
    """
    df = df.copy()
    
    # If station specified and exists in columns
    if station and "station" in df.columns:
        df = df[df["station"] == station].copy()
        
    # Construct timestamp if separate year/month/day/hour columns exist
    if "timestamp" not in df.columns:
        if all(col in df.columns for col in ["year", "month", "day", "hour"]):
            df["timestamp"] = pd.to_datetime(
                df["year"].astype(str) + "-" +
                df["month"].astype(str).str.zfill(2) + "-" +
                df["day"].astype(str).str.zfill(2) + " " +
                df["hour"].astype(str).str.zfill(2) + ":00:00"
            )
        else:
            raise ValueError("Dataframe must contain 'timestamp' or ['year', 'month', 'day', 'hour']")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
    # Sort chronologically
    df = df.sort_values("timestamp").drop_duplicates(subset=["timestamp"])
    df = df.set_index("timestamp")
    
    # Resample to strict 1-hour frequency
    full_idx = pd.date_range(start=df.index.min(), end=df.index.max(), freq="1h")
    df = df.reindex(full_idx)
    df.index.name = "timestamp"
    
    return df

def clean_physical_ranges(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    """
    Replaces physically impossible values (e.g. negative pollutant concentrations) with NaN.
    """
    df = df.copy()
    for col in feature_cols:
        if col in df.columns:
            # Pollutant concentrations and precipitation cannot be negative
            if col in ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "RAIN", "WSPM"]:
                invalid_mask = df[col] < 0
                if invalid_mask.any():
                    df.loc[invalid_mask, col] = np.nan
    return df

def preprocess_air_quality_data(
    file_path: str,
    feature_cols: List[str],
    station: Optional[str] = None
) -> pd.DataFrame:
    """
    Loads raw CSV, aligns timestamps, cleans physical ranges, and returns cleaned dataframe.
    """
    df_raw = pd.read_csv(file_path)
    df_clean = clean_and_align_timestamps(df_raw, station=station)
    df_clean = clean_physical_ranges(df_clean, feature_cols=feature_cols)
    
    # Keep only selected feature columns
    available_features = [c for c in feature_cols if c in df_clean.columns]
    return df_clean[available_features]

def split_time_series(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Chronological train/val/test split to prevent temporal leakage.
    """
    n = len(df)
    n_train = int(n * train_ratio)
    n_val = int(n * (train_ratio + val_ratio))
    
    train_df = df.iloc[:n_train].copy()
    val_df = df.iloc[n_train:n_val].copy()
    test_df = df.iloc[n_val:].copy()
    
    return train_df, val_df, test_df

class AirPollutionScaler:
    """
    StandardScaler wrapper that fits ONLY on observed (non-NaN) values in the training set
    and avoids data leakage.
    """
    def __init__(self, feature_names: List[str]):
        self.feature_names = feature_names
        self.means: Dict[str, float] = {}
        self.stds: Dict[str, float] = {}
        
    def fit(self, train_df: pd.DataFrame) -> "AirPollutionScaler":
        for col in self.feature_names:
            valid_vals = train_df[col].dropna().values
            if len(valid_vals) == 0:
                mean_val = 0.0
                std_val = 1.0
            else:
                mean_val = float(np.mean(valid_vals))
                std_val = float(np.std(valid_vals))
                if std_val < 1e-6:
                    std_val = 1.0
            self.means[col] = mean_val
            self.stds[col] = std_val
        return self
        
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        norm_df = df.copy()
        for col in self.feature_names:
            if col in norm_df.columns:
                norm_df[col] = (norm_df[col] - self.means[col]) / self.stds[col]
        return norm_df
        
    def inverse_transform_array(self, arr: np.ndarray) -> np.ndarray:
        """
        arr shape: (..., num_features)
        """
        out = arr.copy()
        for i, col in enumerate(self.feature_names):
            out[..., i] = out[..., i] * self.stds[col] + self.means[col]
        return out

def normalize_datasets(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: List[str]
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, AirPollutionScaler]:
    """
    Fits scaler exclusively on train_df, transforms train, val, test splits.
    """
    scaler = AirPollutionScaler(feature_cols)
    scaler.fit(train_df)
    
    train_norm = scaler.transform(train_df)
    val_norm = scaler.transform(val_df)
    test_norm = scaler.transform(test_df)
    
    return train_norm, val_norm, test_norm, scaler
