"""Feature extraction and thresholding logic for environmental context synthesis.

Transforms 24-hour numerical window slices, observation masks, and window metadata
into structured environmental, meteorological, urban, and missingness descriptors.

Thresholds are aligned with official Hong Kong Observatory (HKO) and Transport
Department standards, with all non-standard decisions explicitly marked with
[DESIGN DECISION REQUIRED].
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


# Canonical channel definitions matching CTDI 13-channel specification
CHANNEL_NAMES = [
    "pm25",                # 0: PM2.5 (ug/m3)
    "pm10",                # 1: PM10 (ug/m3)
    "no2",                 # 2: NO2 (ug/m3)
    "so2",                 # 3: SO2 (ug/m3)
    "o3",                  # 4: O3 (ug/m3)
    "pressure",            # 5: Surface atmospheric pressure (hPa)
    "relative_humidity",   # 6: Relative humidity (%)
    "temperature",         # 7: Ambient temperature (deg C)
    "rainfall",            # 8: Hourly rainfall accumulation (mm/h)
    "wind_direction",      # 9: Wind direction (compass degrees 0-360)
    "wind_speed",          # 10: Wind speed (m/s)
    "traffic_speed",       # 11: Corridor traffic speed (km/h)
    "traffic_congestion",  # 12: Speed saturation / congestion index [0, 1]
]

POLLUTANT_INDICES = [0, 1, 2, 3, 4]
MET_INDICES = [5, 6, 7, 8, 9, 10]
TRAFFIC_INDICES = [11, 12]


# ==============================================================================
# 1. DESCRIPTOR THRESHOLDING FUNCTIONS
# ==============================================================================

def describe_temperature(temp_c: float) -> str:
    """Categorize ambient temperature in Celsius.
    
    Threshold References:
    - Hong Kong Observatory (HKO) Cold Weather Warning threshold: <= 12.0 deg C.
    - HKO Very Hot Weather Warning threshold: >= 33.0 deg C.
    - Intermediate bins (Cool, Mild, Warm, Hot) follow sub-tropical bioclimatic standards.
    
    [DESIGN DECISION REQUIRED]:
    Intermediate thresholds (12-18, 18-24, 24-28, 28-33) are chosen based on HK seasonal
    comfort indices. Future ablation may test continuous numerical injection vs these bins.
    """
    if np.isnan(temp_c):
        return "unknown temperature"
    if temp_c < 8.0:
        return "intensely cold"
    if temp_c <= 12.0:
        return "cold"
    if temp_c < 18.0:
        return "cool"
    if temp_c < 24.0:
        return "mild"
    if temp_c < 28.0:
        return "warm"
    if temp_c < 33.0:
        return "hot"
    return "very hot"


def describe_humidity(rh_pct: float) -> str:
    """Categorize relative humidity percentage.
    
    Threshold References:
    - HKO Fire Danger Warning often triggers when RH drops below 40-50% with dry monsoon.
    - Coastal marine fog and condensation occur when RH >= 90%.
    
    [DESIGN DECISION REQUIRED]:
    Bins: Very Dry (<40%), Dry (40-59%), Comfortable (60-79%), Humid (80-89%), Very Humid (>=90%).
    """
    if np.isnan(rh_pct):
        return "unknown humidity"
    if rh_pct < 40.0:
        return "very dry"
    if rh_pct < 60.0:
        return "dry"
    if rh_pct < 80.0:
        return "comfortable"
    if rh_pct < 90.0:
        return "humid"
    return "very humid"


def describe_rainfall(rain_total_mm: float, rain_max_hourly: float) -> str:
    """Categorize rainfall based on 24-hour accumulation and peak hourly intensity.
    
    Threshold References:
    - HKO Rainstorm Warning System:
      * Amber: Heavy rain exceeding 30 mm/h.
      * Red: Heavy rain exceeding 50 mm/h.
      * Black: Very heavy rain exceeding 70 mm/h.
    - Measurable rainfall threshold: >= 0.1 mm.
    
    [DESIGN DECISION REQUIRED]:
    Categorization evaluates both 24h cumulative total and hourly burst intensity.
    """
    if np.isnan(rain_total_mm) or rain_total_mm < 0.1:
        return "no rain"
    if rain_max_hourly >= 30.0 or rain_total_mm >= 70.0:
        return "torrential downpour"
    if rain_max_hourly >= 15.0 or rain_total_mm >= 30.0:
        return "heavy rain"
    if rain_max_hourly >= 5.0 or rain_total_mm >= 10.0:
        return "moderate rain"
    return "light rain"


def describe_wind(speed_ms: float, direction_deg: float) -> Tuple[str, str, str]:
    """Categorize wind speed, compass direction, and synoptic monsoon regime.
    
    Threshold References:
    - Hong Kong data stores wind speed in m/s (mean ~3.5 m/s, max ~17.4 m/s).
    - International Beaufort Scale & HKO wind scale:
      * Light: < 3.4 m/s (< 12 km/h, Beaufort 0-2)
      * Moderate: 3.4 - 7.9 m/s (12 - 28 km/h, Beaufort 3-4)
      * Fresh: 8.0 - 10.7 m/s (29 - 38 km/h, Beaufort 5)
      * Strong: 10.8 - 13.8 m/s (39 - 49 km/h, Beaufort 6, HKO Signal No. 3)
      * Gale / Storm: >= 13.9 m/s (>= 50 km/h, Beaufort 7+, HKO Signal No. 8)
      
    Synoptic Regimes in Hong Kong:
    - N/NE/E (0-90 deg, 315-360 deg): Continental Winter Monsoon / Inland advection.
      Transports regional pollutants from Pearl River Delta.
    - S/SW/SE (90-270 deg): Maritime Summer Monsoon / Marine advection.
      Brings clean oceanic air masses and convective moisture.
    - Calm (< 1.5 m/s): Weak dispersion, high stagnation potential.
    
    [DESIGN DECISION REQUIRED]:
    Synoptic regime mapping partitions compass angles into continental vs maritime flows.
    """
    # 1. Wind speed description
    if np.isnan(speed_ms):
        speed_desc = "unknown wind speed"
    elif speed_ms < 1.5:
        speed_desc = "calm"
    elif speed_ms < 3.4:
        speed_desc = "light breeze"
    elif speed_ms < 8.0:
        speed_desc = "moderate breeze"
    elif speed_ms < 10.8:
        speed_desc = "fresh wind"
    elif speed_ms < 13.9:
        speed_desc = "strong wind"
    else:
        speed_desc = "gale force wind"

    # 2. Compass direction
    if np.isnan(direction_deg) or (not np.isnan(speed_ms) and speed_ms < 0.5):
        dir_desc = "variable"
        sector = "calm"
    else:
        deg = direction_deg % 360.0
        if 22.5 <= deg < 67.5:
            dir_desc = "northeasterly"
            sector = "NE"
        elif 67.5 <= deg < 112.5:
            dir_desc = "easterly"
            sector = "E"
        elif 112.5 <= deg < 157.5:
            dir_desc = "southeasterly"
            sector = "SE"
        elif 157.5 <= deg < 202.5:
            dir_desc = "southerly"
            sector = "S"
        elif 202.5 <= deg < 247.5:
            dir_desc = "southwesterly"
            sector = "SW"
        elif 247.5 <= deg < 292.5:
            dir_desc = "westerly"
            sector = "W"
        elif 292.5 <= deg < 337.5:
            dir_desc = "northwesterly"
            sector = "NW"
        else:
            dir_desc = "northerly"
            sector = "N"

    # 3. Synoptic regime
    if not np.isnan(speed_ms) and speed_ms < 1.5:
        regime = "stagnant air mass with weak dispersion"
    elif sector in ["N", "NE", "E", "NW"]:
        regime = "continental outflow bringing regional inland air"
    elif sector in ["S", "SW", "SE"]:
        regime = "maritime inflow bringing clean oceanic air"
    else:
        regime = "transitional atmospheric flow"

    return speed_desc, dir_desc, regime


def describe_traffic(mean_speed: float, mean_congestion: float) -> Tuple[str, str]:
    """Categorize vehicular traffic speed and corridor congestion level.
    
    Threshold References:
    - SpeedMap traffic speed: Empirical mean is 62.2 km/h across strategic corridors.
    - Congestion index: Empirical mean is 0.12 (range 0.0 to 0.84).
    
    [DESIGN DECISION REQUIRED]:
    Speed bins: Heavy congestion (<40 km/h), Moderate traffic (40-60 km/h), Free flow (>60 km/h).
    Saturation bins: Light (<0.10), Moderate (0.10-0.25), Severe (>0.25).
    """
    if np.isnan(mean_speed):
        speed_cat = "unknown speed"
    elif mean_speed < 40.0:
        speed_cat = "heavy corridor congestion"
    elif mean_speed < 60.0:
        speed_cat = "moderate vehicular flow"
    else:
        speed_cat = "smooth free-flow traffic"

    if np.isnan(mean_congestion):
        cong_cat = "unknown saturation"
    elif mean_congestion < 0.10:
        cong_cat = "low saturation"
    elif mean_congestion < 0.25:
        cong_cat = "moderate saturation"
    else:
        cong_cat = "severe saturation"

    return speed_cat, cong_cat


def describe_missingness(
    mask_24h: np.ndarray,
    pollutant_indices: List[int] = POLLUTANT_INDICES
) -> Dict[str, Any]:
    """Analyze missingness pattern across pollutant channels for a 24h window.
    
    Args:
        mask_24h: Binary array of shape (24, 13) where 1=observed, 0=missing.
        pollutant_indices: Column indices for criteria pollutants (default 0..4).
        
    Returns:
        Structured dictionary detailing missingness rate, affected channels, and pattern.
    """
    pol_mask = mask_24h[:, pollutant_indices]  # shape (24, 5)
    total_cells = pol_mask.size  # 120
    observed_cells = int(np.sum(pol_mask))
    missing_cells = total_cells - observed_cells
    missing_pct = (missing_cells / total_cells) * 100.0

    affected_pollutants = []
    for idx in pollutant_indices:
        ch_name = CHANNEL_NAMES[idx]
        ch_missing = int(np.sum(1 - mask_24h[:, idx]))
        if ch_missing > 0:
            affected_pollutants.append((ch_name, ch_missing))

    # Determine pattern type
    if missing_cells == 0:
        pattern = "complete observation"
        severity = "none"
    elif missing_cells == total_cells:
        pattern = "total station outage"
        severity = "extreme"
    else:
        # Check if missingness is contiguous block or scattered
        is_block = False
        for idx in pollutant_indices:
            col = pol_mask[:, idx - pollutant_indices[0]]
            miss_idx = np.where(col == 0)[0]
            if len(miss_idx) > 1 and np.all(np.diff(miss_idx) == 1):
                is_block = True
                break
        
        if missing_pct < 10.0:
            severity = "minor"
            pattern = "intermittent sporadic dropouts" if not is_block else "short contiguous gap"
        elif missing_pct <= 50.0:
            severity = "moderate"
            pattern = "sustained block outage" if is_block else "frequent scattered dropouts"
        else:
            severity = "severe"
            pattern = "prolonged multi-channel blackout"

    return {
        "missing_cells": missing_cells,
        "total_cells": total_cells,
        "missing_pct": missing_pct,
        "severity": severity,
        "pattern": pattern,
        "affected_pollutants": affected_pollutants,
    }


# ==============================================================================
# 2. COMPREHENSIVE CONTEXT FEATURE EXTRACTION
# ==============================================================================

def extract_window_features(
    window_data: np.ndarray,
    mask_data: np.ndarray,
    metadata: Dict[str, Any],
    eval_mask: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """Extract structured environmental context features from a single 24h window.
    
    CRITICAL LEAKAGE GUARD:
    - Meteorology and traffic features are extracted from exogenous channels (5..12).
    - Missingness metrics are computed using eval_mask if provided (simulated missingness),
      otherwise using mask_data (natural missingness).
    - If pollutant summaries are computed, they strictly mask hidden cells:
      observed_pollutants = window_data[:, 0:5] * effective_mask[:, 0:5].
      Hidden values are NEVER accessed.
      
    Args:
        window_data: Array of shape (24, 13) containing numerical channel values.
        mask_data: Array of shape (24, 13) containing natural observation mask.
        metadata: Dictionary containing window metadata (station, timestamps, calendar).
        eval_mask: Optional array of shape (24, 13) for experimental missingness masking.
        
    Returns:
        Hierarchical dictionary containing extracted temporal, spatial, meteorological,
        traffic, and missingness features.
    """
    if window_data.shape != (24, 13):
        raise ValueError(f"Expected window_data shape (24, 13), got {window_data.shape}")
    if mask_data.shape != (24, 13):
        raise ValueError(f"Expected mask_data shape (24, 13), got {mask_data.shape}")

    effective_mask = eval_mask if eval_mask is not None else mask_data

    # 1. Temporal context
    start_ts = str(metadata.get("start_timestamp", ""))
    year = int(metadata.get("year", 0))
    month = int(metadata.get("month", 0))
    day = int(metadata.get("day", 0))
    start_hour = int(metadata.get("start_hour", 0))

    # Determine season in Hong Kong climatology
    # Winter: Dec-Feb, Spring: Mar-May, Summer: Jun-Aug, Autumn: Sep-Nov
    if month in [12, 1, 2]:
        season = "winter"
    elif month in [3, 4, 5]:
        season = "spring"
    elif month in [6, 7, 8]:
        season = "summer"
    else:
        season = "autumn"

    temporal_ctx = {
        "start_timestamp": start_ts,
        "year": year,
        "month": month,
        "day": day,
        "start_hour": start_hour,
        "season": season,
        "temporal_split": metadata.get("temporal_split", "train"),
    }

    # 2. Spatial context
    station_id = int(metadata.get("station_id", 0))
    station_name = str(metadata.get("station_name", "UNKNOWN"))
    station_type = str(metadata.get("station_type", "General"))
    district = str(metadata.get("district", "Hong Kong"))

    spatial_ctx = {
        "station_id": station_id,
        "station_name": station_name,
        "station_type": station_type,
        "district": district,
    }

    # 3. Meteorological context (Exogenous channels 5..10)
    pres = window_data[:, 5]
    rh = window_data[:, 6]
    temp = window_data[:, 7]
    rain = window_data[:, 8]
    wd = window_data[:, 9]
    ws = window_data[:, 10]

    mean_temp = float(np.nanmean(temp))
    min_temp = float(np.nanmin(temp))
    max_temp = float(np.nanmax(temp))

    mean_rh = float(np.nanmean(rh))
    min_rh = float(np.nanmin(rh))
    max_rh = float(np.nanmax(rh))

    mean_pres = float(np.nanmean(pres))
    rain_total = float(np.nansum(rain))
    rain_max = float(np.nanmax(rain))

    mean_ws = float(np.nanmean(ws))
    mean_wd = float(np.nanmean(wd))

    temp_desc = describe_temperature(mean_temp)
    rh_desc = describe_humidity(mean_rh)
    rain_desc = describe_rainfall(rain_total, rain_max)
    wind_speed_desc, wind_dir_desc, synoptic_regime = describe_wind(mean_ws, mean_wd)

    met_ctx = {
        "mean_temp_c": round(mean_temp, 1),
        "min_temp_c": round(min_temp, 1),
        "max_temp_c": round(max_temp, 1),
        "temp_descriptor": temp_desc,
        "mean_rh_pct": round(mean_rh, 1),
        "rh_descriptor": rh_desc,
        "mean_pressure_hpa": round(mean_pres, 1),
        "rain_total_mm": round(rain_total, 2),
        "rain_max_hourly_mm": round(rain_max, 2),
        "rain_descriptor": rain_desc,
        "mean_wind_speed_ms": round(mean_ws, 2),
        "mean_wind_speed_kmh": round(mean_ws * 3.6, 1),
        "mean_wind_dir_deg": round(mean_wd, 1),
        "wind_speed_descriptor": wind_speed_desc,
        "wind_direction_descriptor": wind_dir_desc,
        "synoptic_regime": synoptic_regime,
    }

    # 4. Traffic context (Exogenous channels 11..12)
    speed = window_data[:, 11]
    cong = window_data[:, 12]

    mean_spd = float(np.nanmean(speed)) if not np.all(np.isnan(speed)) else np.nan
    mean_cng = float(np.nanmean(cong)) if not np.all(np.isnan(cong)) else np.nan

    speed_cat, cong_cat = describe_traffic(mean_spd, mean_cng)

    traffic_ctx = {
        "mean_speed_kmh": round(mean_spd, 1) if not np.isnan(mean_spd) else None,
        "mean_congestion_index": round(mean_cng, 2) if not np.isnan(mean_cng) else None,
        "traffic_speed_descriptor": speed_cat,
        "traffic_congestion_descriptor": cong_cat,
    }

    # 5. Missingness context (Derived strictly from effective_mask)
    missingness_ctx = describe_missingness(effective_mask, POLLUTANT_INDICES)

    # 6. Observed air quality summary (STRICTLY OBSERVATION-ONLY)
    # Excludes any hidden/masked values
    pol_obs = window_data[:, POLLUTANT_INDICES] * effective_mask[:, POLLUTANT_INDICES]
    obs_counts = np.sum(effective_mask[:, POLLUTANT_INDICES], axis=0)

    obs_aq_summary = {}
    for i, idx in enumerate(POLLUTANT_INDICES):
        ch_name = CHANNEL_NAMES[idx]
        n_obs = int(obs_counts[i])
        if n_obs > 0:
            obs_vals = pol_obs[:, i][effective_mask[:, idx] == 1]
            obs_aq_summary[ch_name] = {
                "observed_hours": n_obs,
                "mean_observed": round(float(np.mean(obs_vals)), 1),
                "max_observed": round(float(np.max(obs_vals)), 1),
            }
        else:
            obs_aq_summary[ch_name] = {
                "observed_hours": 0,
                "status": "completely missing",
            }

    return {
        "temporal": temporal_ctx,
        "spatial": spatial_ctx,
        "meteorological": met_ctx,
        "traffic": traffic_ctx,
        "missingness": missingness_ctx,
        "observed_air_quality": obs_aq_summary,
    }
