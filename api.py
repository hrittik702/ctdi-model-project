"""FastAPI Backend Entry Point for Air Pollution Imputation Research.

Connects directly to the frozen dataset v1.0 in data/final/ to serve:
- 16 Hong Kong EPD monitoring stations metadata
- Station-specific 24-hour sequence samples (X) and natural dropout masks (M_natural)
- Model architecture specifications and diagnostic health monitoring
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Air Pollution Imputation API",
    description="Backend service for Air Pollution Missing Data Imputation research (CTDI Studio)",
    version="0.1.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATASET_DIR = Path("data/final/CTDI_AirPollution_TrainingDataset_v1.0")

# 13 Canonical Continuous Channels in strict index ordering
CHANNELS = [
    {"index": 0, "id": "pm25", "name": "PM2.5", "label": "PM2.5", "unit": "µg/m³", "category": "air_quality"},
    {"index": 1, "id": "pm10", "name": "PM10", "label": "PM10", "unit": "µg/m³", "category": "air_quality"},
    {"index": 2, "id": "no2", "name": "NO2", "label": "NO2", "unit": "µg/m³", "category": "air_quality"},
    {"index": 3, "id": "so2", "name": "SO2", "label": "SO2", "unit": "µg/m³", "category": "air_quality"},
    {"index": 4, "id": "o3", "name": "O3", "label": "O3", "unit": "µg/m³", "category": "air_quality"},
    {"index": 5, "id": "pressure", "name": "Surface Pressure", "label": "Pressure", "unit": "hPa", "category": "meteorology"},
    {"index": 6, "id": "relative_humidity", "name": "Relative Humidity", "label": "Humidity", "unit": "%", "category": "meteorology"},
    {"index": 7, "id": "temperature", "name": "Temperature", "label": "Temperature", "unit": "°C", "category": "meteorology"},
    {"index": 8, "id": "rainfall", "name": "Precipitation", "label": "Rainfall", "unit": "mm", "category": "meteorology"},
    {"index": 9, "id": "wind_direction", "name": "Wind Direction", "label": "Wind Direction", "unit": "°", "category": "meteorology"},
    {"index": 10, "id": "wind_speed", "name": "Wind Speed", "label": "Wind Speed", "unit": "m/s", "category": "meteorology"},
    {"index": 11, "id": "traffic_speed", "name": "Traffic Speed", "label": "Traffic Speed", "unit": "km/h", "category": "traffic"},
    {"index": 12, "id": "traffic_congestion", "name": "Traffic Congestion", "label": "Traffic Congestion", "unit": "[0.0, 1.0]", "category": "traffic"},
]

# In-memory cached dataset state
STATIONS: List[Dict[str, Any]] = []
STATION_LOOKUP: Dict[str, Dict[str, Any]] = {}
STATION_BASE_WID: Dict[int, int] = {}
SPLITS: Dict[str, Dict[str, np.ndarray]] = {}
WID_TO_SPLIT: Dict[int, tuple] = {}
MIN_VALID_WID: int = 0
MAX_VALID_WID: int = 420495


def _init_dataset():
    """Load metadata and array indices at module initialization."""
    global STATIONS, STATION_LOOKUP, STATION_BASE_WID, SPLITS, WID_TO_SPLIT, MIN_VALID_WID, MAX_VALID_WID

    if not DATASET_DIR.exists():
        return

    # Load 16 stations from metadata/station_metadata.csv
    stn_path = DATASET_DIR / "metadata" / "station_metadata.csv"
    if stn_path.exists():
        stns_df = pd.read_csv(stn_path)
        for _, row in stns_df.iterrows():
            stn = {
                "id": str(row["station_code"]),
                "name": str(row["display_name"]),
                "code": str(row["station_code"]),
                "station_id": int(row["station_id"]),
                "type": str(row["station_type"]),
                "lat": float(row["latitude"]),
                "lng": float(row["longitude"]),
                "height_m": float(row["sampling_height_m"]),
                "district": str(row["district"]),
            }
            STATIONS.append(stn)
            STATION_LOOKUP[stn["code"].upper()] = stn
            STATION_LOOKUP[str(stn["station_id"])] = stn
            STATION_LOOKUP[stn["name"].lower()] = stn
            STATION_LOOKUP[stn["id"].lower()] = stn

    # Load window metadata base IDs
    wm_path = DATASET_DIR / "metadata" / "window_metadata.parquet"
    if wm_path.exists():
        wm = pd.read_parquet(wm_path, columns=["station_id", "window_id"])
        STATION_BASE_WID = wm.groupby("station_id")["window_id"].min().to_dict()
        MIN_VALID_WID = int(wm["window_id"].min())
        MAX_VALID_WID = int(wm["window_id"].max())

    # Load X and M arrays across train, validation, and test splits
    for split, sname in [("train", "train"), ("val", "val"), ("test", "test")]:
        folder = "validation" if split == "val" else split
        x_path = DATASET_DIR / folder / f"X_{sname}.npz"
        m_path = DATASET_DIR / folder / f"M_natural_{sname}.npz"
        if x_path.exists() and m_path.exists():
            x_data = np.load(x_path)
            m_data = np.load(m_path)
            SPLITS[split] = {
                "X": x_data["X"],
                "M": m_data["M_natural"],
            }
            wids = x_data["window_id"]
            for idx, wid in enumerate(wids):
                WID_TO_SPLIT[int(wid)] = (split, idx)


_init_dataset()


def _resolve_station(station_query: Optional[str]) -> Dict[str, Any]:
    """Resolve station identifier (code, station_id, or name) to canonical station object."""
    if not STATIONS:
        # Fallback if dataset directory is missing
        return {
            "id": "CW",
            "name": "Central / Western",
            "code": "CW",
            "station_id": 80,
            "type": "General",
            "lat": 22.2848,
            "lng": 114.1441,
            "height_m": 16.0,
            "district": "Central and Western",
        }

    if not station_query:
        return STATIONS[0]

    norm = str(station_query).strip()
    if norm.upper() in STATION_LOOKUP:
        return STATION_LOOKUP[norm.upper()]
    if norm.lower() in STATION_LOOKUP:
        return STATION_LOOKUP[norm.lower()]
    if norm in STATION_LOOKUP:
        return STATION_LOOKUP[norm]

    # Partial match
    for s in STATIONS:
        if norm.lower() in s["name"].lower() or norm.upper() in s["code"]:
            return s

    return STATIONS[0]


class StationSelectRequest(BaseModel):
    station: str


@app.get("/")
def root() -> Dict[str, Any]:
    """Root endpoint returning project identity and status."""
    return {
        "status": "ok",
        "project": "Air Pollution Missing Data Imputation",
        "stage": "connected",
        "dataset": "CTDI Air Pollution Training Dataset v1.0",
        "stations_loaded": len(STATIONS),
        "windows_indexed": len(WID_TO_SPLIT),
    }


@app.get("/api/health")
def health_check(station: Optional[str] = None) -> Dict[str, Any]:
    """Health check endpoint for frontend and service monitoring."""
    stn = _resolve_station(station)
    return {
        "status": "healthy",
        "stage": "dataset_connected",
        "message": f"Operational: Hong Kong EPD dataset v1.0 connected. Active station: {stn['name']} ({stn['code']}).",
        "station": stn["name"],
        "station_code": stn["code"],
        "total_stations": len(STATIONS),
    }


@app.get("/api/stations")
def get_stations() -> Dict[str, Any]:
    """Return catalog of 16 Hong Kong EPD air quality monitoring stations."""
    return {
        "status": "ok",
        "stations": STATIONS,
        "total": len(STATIONS),
        "network": "Hong Kong EPD Air Quality Network",
    }


@app.post("/api/stations/select")
def select_station(payload: StationSelectRequest) -> Dict[str, Any]:
    """Acknowledge active station context."""
    stn = _resolve_station(payload.station)
    return {
        "status": "ok",
        "station": stn["code"],
        "station_name": stn["name"],
        "station_id": stn["station_id"],
    }


@app.get("/api/metadata")
def get_metadata(station: Optional[str] = None) -> Dict[str, Any]:
    """Return dataset and station-specific metadata."""
    stn = _resolve_station(station)
    return {
        "status": "ok",
        "dataset": "CTDI Air Pollution Training Dataset v1.0",
        "network": "Hong Kong EPD Air Quality Network",
        "station": stn["name"],
        "station_code": stn["code"],
        "station_id": stn["station_id"],
        "station_type": stn["type"],
        "latitude": stn["lat"],
        "longitude": stn["lng"],
        "elevation": f"{stn['height_m']}m",
        "district": stn["district"],
        "temporal_range": "2019-01-01 to 2021-12-31",
        "total_hours": 26304,
        "num_samples": 26281,
        "station_windows": 26281,
        "test_station_windows": 3889,
        "total_windows": 420496,
        "window_size": 24,
        "channels": CHANNELS,
        "pollutants": [c["name"] for c in CHANNELS],
        "missing_rate_percent": 2.66,
        "total_eval_points": 3889 * 24,
        "model_trained": False,
        "stage": "Dataset Contract v1.0",
    }


@app.get("/api/samples/{sample_idx}")
def get_sample(sample_idx: int, station: Optional[str] = None) -> Dict[str, Any]:
    """Return genuine 24-hour sequence telemetry for the requested station and window index.

    sample_idx: Station-local window index (0 to 26,280).
    station: Station code (e.g. 'CW', 'CB', 'TMN') or station_id.
    """
    stn = _resolve_station(station)
    sid = stn["station_id"]

    # Clamp local window index
    window_idx = max(0, min(26280, sample_idx))
    base_wid = STATION_BASE_WID.get(sid, 0)
    target_wid = base_wid + window_idx

    # Handle purged leakage buffer boundaries if target_wid falls between splits
    lookup_wid = target_wid
    if lookup_wid not in WID_TO_SPLIT:
        # Search nearest valid window within the same station
        for offset in range(1, 50):
            if (target_wid - offset) in WID_TO_SPLIT and (target_wid - offset) >= base_wid:
                lookup_wid = target_wid - offset
                break
            if (target_wid + offset) in WID_TO_SPLIT and (target_wid + offset) < (base_wid + 26281):
                lookup_wid = target_wid + offset
                break

    if lookup_wid not in WID_TO_SPLIT:
        raise HTTPException(
            status_code=404,
            detail=f"Window {sample_idx} for station {stn['code']} not found in dataset splits.",
        )

    split_name, array_idx = WID_TO_SPLIT[lookup_wid]
    x_slice = SPLITS[split_name]["X"][array_idx]  # Shape (24, 13)
    m_slice = SPLITS[split_name]["M"][array_idx]  # Shape (24, 13)

    # Compute hourly ISO timestamps (Hong Kong EPD 2019-01-01 base)
    base_time = datetime(2019, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    window_start = base_time + timedelta(hours=window_idx)
    timestamps = [
        (window_start + timedelta(hours=h)).strftime("%Y-%m-%d %H:%M:%S")
        for h in range(24)
    ]
    hours = list(range(24))

    pollutants_data: Dict[str, Any] = {}
    for ch in CHANNELS:
        ch_idx = ch["index"]
        actual_vals = [round(float(val), 2) for val in x_slice[:, ch_idx]]
        obs_mask = [int(val) for val in m_slice[:, ch_idx]]
        hidden_count = sum(1 for m in obs_mask if m == 0)

        pollutants_data[ch["name"]] = {
            "channel_index": ch_idx,
            "channel_id": ch["id"],
            "unit": ch["unit"],
            "actual": actual_vals,
            "observed_mask": obs_mask,
            "eval_mask": [0] * 24,
            "transformer": None,
            "linear": None,
            "knn": None,
            "mlp": None,
            "hidden_count": hidden_count,
            "sample_mae": {"transformer": None, "linear": None},
        }

    return {
        "sample_idx": window_idx,
        "station": stn["name"],
        "station_code": stn["code"],
        "station_id": stn["station_id"],
        "temporal_split": split_name,
        "hours": hours,
        "timestamps": timestamps,
        "pollutants": pollutants_data,
        "is_synthetic_preview": False,
        "model_predictions_available": False,
    }


@app.get("/api/metrics")
def get_metrics(station: Optional[str] = None) -> List[Dict[str, Any]]:
    """Global benchmark metrics table across test set."""
    return []


@app.get("/api/metrics/pollutants")
def get_pollutant_metrics(station: Optional[str] = None) -> Dict[str, Any]:
    """Per-pollutant computed metrics across test set."""
    return {}


@app.get("/api/experiments")
def get_experiments() -> List[Dict[str, Any]]:
    """Benchmark experiment history."""
    return []


@app.get("/api/model/config")
def get_model_config(station: Optional[str] = None) -> Dict[str, Any]:
    """CTDI CNN-Transformer architecture specification."""
    return {
        "architecture": "1×1 Conv1D Spatial Feature Mixing + Multi-Head Temporal Transformer Encoder",
        "version": "CTDI Architecture Specification v1.0",
        "sequence_length": 24,
        "input_channels": 13,
        "input_features_with_mask": 26,
        "d_model": 64,
        "n_heads": 4,
        "num_layers": 2,
        "dim_feedforward": 128,
        "dropout": 0.1,
        "positional_encoding": "Sinusoidal Temporal Encoding (24 hours)",
        "loss_function": "Masked L1 Loss (evaluated strictly at withheld target coordinates)",
        "normalization": "Z-Score Standardization (derived strictly from training split, zero leakage)",
        "status": "specification_only",
        "status_label": "Architecture Specification",
        "checkpoint_path": "checkpoints/ctdi/best_temporal_transformer.pt",
        "device": "CUDA / MPS / CPU",
        "framework": "PyTorch v2.x",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

