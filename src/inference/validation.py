"""Data validation and parsing for air pollution imputation inference."""

import io
from typing import Tuple, List, Dict, Any, Optional, Union
import numpy as np
import pandas as pd


class ValidationError(Exception):
    """Raised when uploaded CSV or input data fails schema or continuity validation."""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


POLLUTANT_ALIASES: Dict[str, List[str]] = {
    "PM2.5": [
        "pm2.5", "pm2_5", "pm25", "pm2_5_ugm3", "pm2.5_ugm3", "pm2_5 (ug/m3)", "pm2.5 (ug/m3)",
        "pm2.5_observed", "pm2_5_observed", "pm25_observed", "pm2.5 observed",
        "pm2.5_imputed", "pm2_5_imputed", "pm25_imputed", "pm2.5 imputed",
        "pm2.5_pred", "pm2_5_pred", "pm25_pred"
    ],
    "PM10": [
        "pm10", "pm10_ugm3", "pm10 (ug/m3)", "pm10_observed", "pm10 observed",
        "pm10_imputed", "pm10 imputed", "pm10_pred"
    ],
    "NO2": [
        "no2", "no2_ugm3", "no2 (ug/m3)", "no2_observed", "no2 observed",
        "no2_imputed", "no2 imputed", "no2_pred"
    ],
    "SO2": [
        "so2", "so2_ugm3", "so2 (ug/m3)", "so2_observed", "so2 observed",
        "so2_imputed", "so2 imputed", "so2_pred"
    ],
    "O3": [
        "o3", "o3_ugm3", "o3 (ug/m3)", "ozone", "o3_observed", "o3 observed",
        "o3_imputed", "o3 imputed", "o3_pred"
    ],
}

CONTEXT_ALIASES: Dict[str, List[str]] = {
    "Temp_2m_C": ["temp_2m_c", "temperature", "temp", "temp_c"],
    "Humidity_Percent": ["humidity_percent", "humidity", "rh", "rh_percent"],
    "Wind_Speed_10m_kmh": ["wind_speed_10m_kmh", "wind_speed", "wspm", "wind_speed_kmh"],
    "Wind_Dir_10m": ["wind_dir_10m", "wind_dir", "wind_direction", "wd"],
    "Precipitation_mm": ["precipitation_mm", "precipitation", "rain", "rain_mm"],
}

TARGET_POLLUTANTS: List[str] = ["PM2.5", "PM10", "NO2", "SO2", "O3"]
TARGET_CONTEXT_METEO: List[str] = [
    "Temp_2m_C", "Humidity_Percent", "Wind_Speed_10m_kmh", "Wind_Dir_10m", "Precipitation_mm"
]


def resolve_columns(df_columns: List[str], alias_map: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Maps user column names to standardized canonical column names.
    Returns dict mapping canonical_name -> user_column_name.
    """
    col_lookup = {c.strip().lower(): c for c in df_columns}
    resolved = {}
    
    for canonical, aliases in alias_map.items():
        canon_lower = canonical.lower()
        # 1. Exact canonical name match (e.g. 'PM2.5')
        if canon_lower in col_lookup:
            resolved[canonical] = col_lookup[canon_lower]
            continue
            
        # 2. Prioritize '_observed' column if present
        obs_cand = f"{canon_lower}_observed"
        if obs_cand in col_lookup:
            resolved[canonical] = col_lookup[obs_cand]
            continue
            
        # 3. Check alias list
        found = False
        for a in aliases:
            a_clean = a.lower().replace(" ", "_")
            if a.lower() in col_lookup:
                resolved[canonical] = col_lookup[a.lower()]
                found = True
                break
            elif a_clean in col_lookup:
                resolved[canonical] = col_lookup[a_clean]
                found = True
                break
        if found:
            continue
            
        # 4. Fallback: column name starts with canonical name followed by '_' or ' ' (excluding mask)
        for cl, orig_col in col_lookup.items():
            if "mask" in cl:
                continue
            if (cl.startswith(canon_lower + "_") or cl.startswith(canon_lower + " ") or 
                cl.startswith(canon_lower.replace(".", "_") + "_") or cl.startswith(canon_lower.replace(".", "") + "_")):
                resolved[canonical] = orig_col
                break

    return resolved


def load_and_validate_csv(
    file_or_path: Union[str, bytes, io.BytesIO, pd.DataFrame]
) -> pd.DataFrame:
    """
    Reads CSV and validates fundamental schema:
    1. Timestamp column presence and parsing
    2. Chronological sorting
    3. Duplicate detection
    4. Required pollutant columns presence
    """
    if isinstance(file_or_path, pd.DataFrame):
        df = file_or_path.copy()
    elif isinstance(file_or_path, bytes):
        df = pd.read_csv(io.BytesIO(file_or_path))
    else:
        df = pd.read_csv(file_or_path)

    if df.empty:
        raise ValidationError("Uploaded dataset is completely empty.")

    # 1. Identify and parse timestamp
    timestamp_col = None
    candidate_time_cols = [
        "timestamp", "datetime", "date_time", "date", "time", 
        "Timestamp", "Datetime", "Date_Time", "Date", "Time"
    ]
    for c in df.columns:
        if c.strip().lower() in [cand.lower() for cand in candidate_time_cols]:
            timestamp_col = c
            break

    if timestamp_col is None:
        if all(c in df.columns for c in ["year", "month", "day", "hour"]):
            df["timestamp"] = pd.to_datetime(
                df["year"].astype(str) + "-" +
                df["month"].astype(str).str.zfill(2) + "-" +
                df["day"].astype(str).str.zfill(2) + " " +
                df["hour"].astype(str).str.zfill(2) + ":00:00"
            )
            timestamp_col = "timestamp"
        else:
            raise ValidationError(
                "Missing timestamp column. Dataset must contain 'Datetime' / 'Timestamp' "
                "or separate ['year', 'month', 'day', 'hour'] columns."
            )

    try:
        df["parsed_timestamp"] = pd.to_datetime(df[timestamp_col])
    except Exception as e:
        raise ValidationError(f"Could not parse timestamp column '{timestamp_col}': {str(e)}")

    # 2. Check for duplicate timestamps
    dup_count = int(df["parsed_timestamp"].duplicated().sum())
    if dup_count > 0:
        # Keep first occurrence
        df = df.drop_duplicates(subset=["parsed_timestamp"], keep="first")

    # 3. Sort chronologically
    df = df.sort_values("parsed_timestamp").reset_index(drop=True)

    # 4. Resolve required pollutant columns
    pollutant_map = resolve_columns(list(df.columns), POLLUTANT_ALIASES)
    missing_pollutants = [p for p in TARGET_POLLUTANTS if p not in pollutant_map]
    if missing_pollutants:
        raise ValidationError(
            f"Missing required pollutant column(s): {missing_pollutants}. "
            f"Required 5 pollutants: {TARGET_POLLUTANTS}. "
            f"Found columns: {list(df.columns)}"
        )

    # 5. Resolve optional meteorological context columns
    meteo_map = resolve_columns(list(df.columns), CONTEXT_ALIASES)

    # Standardize column naming in dataframe
    std_df = pd.DataFrame()
    std_df["timestamp"] = df["parsed_timestamp"]

    for canon, user_col in pollutant_map.items():
        # Clean numeric conversion: treat empty strings, 'NaN', 'null' as np.nan
        vals = pd.to_numeric(df[user_col], errors="coerce").astype(float)
        # Physical sanity: negative pollutant concentrations are physically impossible -> convert to NaN
        vals = np.where(vals < 0.0, np.nan, vals)
        # Note: 0.0 is legitimate observed value (NOT NaN)
        std_df[canon] = vals

    for canon, user_col in meteo_map.items():
        vals = pd.to_numeric(df[user_col], errors="coerce").astype(float)
        std_df[canon] = vals

    # Preserve any station column if present
    if "station" in df.columns:
        std_df["station"] = df["station"]

    return std_df


def extract_24h_windows(
    df: pd.DataFrame,
    window_size: int = 24
) -> Tuple[List[pd.DataFrame], List[Dict[str, Any]]]:
    """
    Extracts non-overlapping 24-hour continuous windows from cleaned DataFrame.
    Validates hourly continuity within each window.
    
    Returns:
        windows: List of 24-row DataFrames.
        window_metadata: List of metadata dicts describing each window.
    """
    if len(df) < window_size:
        raise ValidationError(
            f"Model requires at least {window_size} hourly observations for inference, "
            f"but only {len(df)} rows were provided."
        )

    windows = []
    metadata = []
    
    total_rows = len(df)
    # Stride of 24 for non-overlapping multi-day blocks
    num_full_windows = total_rows // window_size
    
    for w_idx in range(num_full_windows):
        start_idx = w_idx * window_size
        end_idx = start_idx + window_size
        sub_df = df.iloc[start_idx:end_idx].copy().reset_index(drop=True)
        
        # Verify hourly continuity: time difference between consecutive rows should be ~1 hour
        timestamps = sub_df["timestamp"]
        time_diffs = timestamps.diff().dropna()
        irregular_gap = any(abs(d.total_seconds() - 3600) > 300 for d in time_diffs)
        
        meta = {
            "window_idx": w_idx,
            "start_time": str(timestamps.iloc[0]),
            "end_time": str(timestamps.iloc[-1]),
            "row_count": len(sub_df),
            "is_continuous_hourly": not irregular_gap
        }
        
        windows.append(sub_df)
        metadata.append(meta)

    return windows, metadata


def compute_missingness_summary(
    df: pd.DataFrame,
    pollutant_cols: List[str] = TARGET_POLLUTANTS
) -> Dict[str, Any]:
    """
    Calculates exact missing value counts and rates per pollutant.
    Zero (0.0) is strictly observed, only NaN is missing.
    """
    total_cells = len(df) * len(pollutant_cols)
    pollutant_stats = {}
    total_missing = 0

    for p in pollutant_cols:
        col_vals = df[p]
        missing_count = int(col_vals.isna().sum())
        observed_count = len(col_vals) - missing_count
        total_missing += missing_count
        pollutant_stats[p] = {
            "missing_count": missing_count,
            "observed_count": observed_count,
            "missing_pct": round((missing_count / len(col_vals)) * 100, 2) if len(col_vals) > 0 else 0.0
        }

    return {
        "total_rows": len(df),
        "total_values": total_cells,
        "total_missing": total_missing,
        "missing_percentage": round((total_missing / total_cells) * 100, 2) if total_cells > 0 else 0.0,
        "per_pollutant": pollutant_stats,
        "time_start": str(df["timestamp"].iloc[0]) if not df.empty else None,
        "time_end": str(df["timestamp"].iloc[-1]) if not df.empty else None
    }
