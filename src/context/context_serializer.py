"""Context serialization and prompt formatting engine.

Formats extracted environmental context dictionaries into standardized,
deterministic string representations for Small Language Model (SLM) tokenization.

Supports:
- Narrative Natural Language (Prompt Template)
- Structured Key-Value (High Token Efficiency)
- Pure JSON (Programmatic Inspection & Exact Reproducibility)
"""

import json
from typing import Any, Dict, List, Optional


def serialize_to_narrative(context: Dict[str, Any], include_observed_aq: bool = False) -> str:
    """Format structured context into a coherent, natural English atmospheric narrative.
    
    Args:
        context: Hierarchical dictionary produced by extract_window_features().
        include_observed_aq: Whether to append observed-only air quality statistics.
            Defaults to False to prevent subtle cross-pollutant target correlation leakage.
            
    Returns:
        Deterministic formatted string prompt.
    """
    temp = context["temporal"]
    spat = context["spatial"]
    met = context["meteorological"]
    traf = context["traffic"]
    miss = context["missingness"]

    # 1. Header & Spatial-Temporal identification
    lines = [
        f"[ENVIRONMENTAL CONTEXT: HONG KONG]",
        f"Station: {spat['station_name']} ({spat['station_type']} Air Quality Station, {spat['district']} District)",
        f"Temporal Window: {temp['start_timestamp']} (Season: {temp['season'].capitalize()}, Start Hour: {temp['start_hour']:02d}:00)",
    ]

    # 2. Meteorological narrative
    rain_str = (
        f"{met['rain_descriptor'].capitalize()} ({met['rain_total_mm']:.1f} mm total, max hourly {met['rain_max_hourly_mm']:.1f} mm/h)"
        if met['rain_total_mm'] > 0
        else "No measurable rainfall (0.0 mm)"
    )
    
    met_line = (
        f"Meteorology: {met['temp_descriptor'].capitalize()} temperature (mean {met['mean_temp_c']:.1f}°C, "
        f"min {met['min_temp_c']:.1f}°C, max {met['max_temp_c']:.1f}°C); "
        f"{met['rh_descriptor']} relative humidity (mean {met['mean_rh_pct']:.0f}%); "
        f"surface pressure {met['mean_pressure_hpa']:.1f} hPa. {rain_str}. "
        f"Wind: {met['wind_speed_descriptor']} ({met['mean_wind_speed_ms']:.1f} m/s) from {met['wind_direction_descriptor']} "
        f"({met['mean_wind_dir_deg']:.0f}°), consistent with {met['synoptic_regime']}."
    )
    lines.append(met_line)

    # 3. Traffic narrative
    if traf['mean_speed_kmh'] is not None:
        traf_line = (
            f"Urban Mobility: {traf['traffic_speed_descriptor'].capitalize()} "
            f"(corridor speed {traf['mean_speed_kmh']:.1f} km/h), "
            f"{traf['traffic_congestion_descriptor']} (saturation index {traf['mean_congestion_index']:.2f})."
        )
    else:
        traf_line = "Urban Mobility: Corridor traffic telemetry not available."
    lines.append(traf_line)

    # 4. Observational / Missingness status
    if miss['missing_cells'] == 0:
        miss_line = "Observational Status: Continuous 24-hour observation with 100% complete sensor data across all criteria pollutants."
    else:
        aff_list = [f"{ch} ({cnt}h missing)" for ch, cnt in miss['affected_pollutants']]
        aff_str = ", ".join(aff_list) if aff_list else "none"
        miss_line = (
            f"Observational Status: {miss['severity'].capitalize()} missingness ({miss['missing_cells']}/{miss['total_cells']} cells, "
            f"{miss['missing_pct']:.1f}% missing; pattern: {miss['pattern']}). Affected channels: {aff_str}."
        )
    lines.append(miss_line)

    # 5. Optional Observed Pollutants (LEAKAGE GUARD: Observed entries ONLY)
    if include_observed_aq and "observed_air_quality" in context:
        obs_items = []
        for pol, stats in context["observed_air_quality"].items():
            if stats.get("observed_hours", 0) > 0:
                obs_items.append(f"{pol.upper()} mean {stats['mean_observed']:.1f} ug/m3")
        if obs_items:
            lines.append(f"Observed Background Pollutants: {'; '.join(obs_items)}.")

    return "\n".join(lines)


def serialize_to_key_value(context: Dict[str, Any]) -> str:
    """Format structured context into a dense, token-efficient key-value representation.
    
    [DESIGN DECISION REQUIRED]:
    Evaluates whether compact token structures outperform verbose natural language
    when constrained by small SLM context windows (e.g. 512 tokens).
    """
    temp = context["temporal"]
    spat = context["spatial"]
    met = context["meteorological"]
    traf = context["traffic"]
    miss = context["missingness"]

    spd_str = f"{traf['mean_speed_kmh']:.1f} km/h" if traf['mean_speed_kmh'] is not None else "N/A"
    cng_str = f"{traf['mean_congestion_index']:.2f}" if traf['mean_congestion_index'] is not None else "N/A"

    parts = [
        f"STATION: {spat['station_name']} | TYPE: {spat['station_type']} | DISTRICT: {spat['district']}",
        f"TIME: {temp['start_timestamp']} | SEASON: {temp['season']} | HOUR: {temp['start_hour']:02d}",
        f"MET: Temp {met['mean_temp_c']:.1f}C ({met['temp_descriptor']}) | RH {met['mean_rh_pct']:.0f}% ({met['rh_descriptor']}) | "
        f"Rain {met['rain_total_mm']:.1f}mm ({met['rain_descriptor']}) | Wind {met['mean_wind_speed_ms']:.1f}m/s {met['wind_direction_descriptor']} ({met['synoptic_regime']})",
        f"TRAFFIC: Speed {spd_str} ({traf['traffic_speed_descriptor']}) | Congestion {cng_str} ({traf['traffic_congestion_descriptor']})",
        f"MISSINGNESS: {miss['missing_cells']}/{miss['total_cells']} ({miss['missing_pct']:.1f}%) | Pattern: {miss['pattern']}",
    ]
    return "\n".join(parts)


def serialize_to_json(context: Dict[str, Any]) -> str:
    """Serialize structured context directly to a deterministic JSON string."""
    return json.dumps(context, indent=2, sort_keys=True)


def serialize_context(
    context: Dict[str, Any],
    format_type: str = "narrative",
    include_observed_aq: bool = False,
) -> str:
    """Universal dispatcher for serializing context dictionaries.
    
    Args:
        context: Extracted feature dictionary.
        format_type: One of 'narrative', 'key_value', 'json'.
        include_observed_aq: Only used when format_type='narrative'.
        
    Returns:
        Serialized string prompt.
    """
    fmt = format_type.lower().strip()
    if fmt in ["narrative", "text", "prompt"]:
        return serialize_to_narrative(context, include_observed_aq=include_observed_aq)
    elif fmt in ["key_value", "kv", "dense"]:
        return serialize_to_key_value(context)
    elif fmt in ["json", "dict"]:
        return serialize_to_json(context)
    else:
        raise ValueError(f"Unknown serialization format '{format_type}'. Expected 'narrative', 'key_value', or 'json'.")
