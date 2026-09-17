"""Phase 2.3: Traffic Road-Link -> AQ Station Spatial Mapping.

Computes the spatial projection from georeferenced road links to the 16 air quality monitoring
stations using the CTDI Inverse Distance Weighting (IDW, p=2) formulation:
    w_ij = 1 / d(i, j)^2
where d(i, j) is the great-circle Haversine distance between station i and link midpoint j.

Spatial Coverage Audit Findings:
1. In data/raw/traffic/traffic-speed-info.csv, exactly 6 links possess verified geographic
   coordinates (start/end node coordinates on the 3 Cross-Harbour Tunnels).
2. The remaining 626 links from speedmap.xml lack georeferenced coordinates in available sources
   (1st Gen system decommissioned by TD; no public coordinate tables published in CTDI literature).
3. Urban core stations (Causeway Bay, Eastern, Central, Central/Western, Kwun Tong, Mong Kok,
   Sham Shui Po, Tseung Kwan O) possess near-proximity coverage (1.3 km - 4.6 km).
4. Remote stations (Tai Po: 17.2 km, Tuen Mun: 20.9 km, Yuen Long: 21.2 km, Tung Chung: 21.5 km,
   Tap Mun: 24.7 km) have no local highway links. Tap Mun is a remote island with zero traffic.
5. In accordance with strict project stop conditions and scientific integrity, spatial diagnostics
   are explicitly maintained:
   - nearest_link_distance_km
   - contributing_links_count
   - spatial_confidence_flag (HIGH <= 5km, MODERATE 5-10km, REMOTE > 10km)

Outputs:
- data/interim/aligned/station_traffic_mapping.parquet (spatial weight matrix)
- data/interim/aligned/traffic_station_hourly.parquet (hourly station-projected traffic)
- data/interim/aligned/spatial_mapping_report.json (spatial audit report)
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATION_METADATA_PATH = PROJECT_ROOT / "data" / "raw" / "station_metadata" / "air_quality_stations.csv"
TRAFFIC_SPEED_INFO_PATH = PROJECT_ROOT / "data" / "raw" / "traffic" / "traffic-speed-info.csv"
TRAFFIC_HOURLY_PATH = PROJECT_ROOT / "data" / "interim" / "aligned" / "traffic_hourly_link_data.parquet"
ALIGNED_DIR = PROJECT_ROOT / "data" / "interim" / "aligned"

OUTPUT_STATION_MAPPING_PARQUET = ALIGNED_DIR / "station_traffic_mapping.parquet"
OUTPUT_STATION_HOURLY_PARQUET = ALIGNED_DIR / "traffic_station_hourly.parquet"
OUTPUT_SPATIAL_REPORT_JSON = ALIGNED_DIR / "spatial_mapping_report.json"

EARTH_RADIUS_KM = 6371.0
LOCAL_RADIUS_KM = 10.0  # Plausible maximum influence threshold for local traffic


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great-Circle Haversine distance in kilometers."""
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return float(EARTH_RADIUS_KM * c)


def compute_spatial_weights() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Compute pairwise distances and IDW (p=2) spatial weights between 16 AQ stations and 6 links."""
    # 1. Load target 16 AQ stations
    df_stations = pd.read_csv(STATION_METADATA_PATH)
    df_stations["in_ctdi_study"] = df_stations["in_ctdi_study"].astype(str).str.strip().str.lower() == "true"
    df_stations = df_stations[df_stations["in_ctdi_study"]].sort_values("station_id").reset_index(drop=True)

    # 2. Load georeferenced links
    df_links = pd.read_csv(TRAFFIC_SPEED_INFO_PATH)
    # Compute midpoint centroid coordinates as documented in research assumptions
    df_links["midpoint_latitude"] = (df_links["start_node_latitude"] + df_links["end_node_latitude"]) / 2.0
    df_links["midpoint_longitude"] = (df_links["start_node_longitude"] + df_links["end_node_longitude"]) / 2.0

    print(f"Loaded {len(df_stations)} target AQ stations and {len(df_links)} georeferenced road links.")

    # 3. Compute pairwise distances
    weight_rows = []
    station_summary_rows = []

    for _, s in df_stations.iterrows():
        s_id = int(s["station_id"])
        s_name = s["station_name"]
        s_lat = float(s["latitude"])
        s_lon = float(s["longitude"])

        link_dists = []
        for _, l in df_links.iterrows():
            l_id = str(l["link_id"])
            l_name = l["link_name_en"]
            l_lat = float(l["midpoint_latitude"])
            l_lon = float(l["midpoint_longitude"])

            d = haversine_distance_km(s_lat, s_lon, l_lat, l_lon)
            link_dists.append((l_id, l_name, d))

        # Handle zero distance explicitly if any
        # Compute raw IDW weights: w_ij = 1 / d^2
        distances = np.array([item[2] for item in link_dists], dtype=np.float64)
        min_dist = float(np.min(distances))

        if min_dist == 0.0:
            raw_weights = np.where(distances == 0.0, 1.0, 0.0)
        else:
            raw_weights = 1.0 / (distances ** 2)

        # Global IDW normalized weights across all 6 links
        norm_weights_global = raw_weights / np.sum(raw_weights)

        # Local IDW normalized weights (links within LOCAL_RADIUS_KM)
        local_mask = distances <= LOCAL_RADIUS_KM
        num_local = int(np.sum(local_mask))
        if num_local > 0:
            local_weights = np.where(local_mask, raw_weights, 0.0)
            norm_weights_local = local_weights / np.sum(local_weights)
        else:
            norm_weights_local = np.zeros_like(raw_weights)

        # Classification
        if min_dist <= 5.0:
            confidence = "HIGH_URBAN"
        elif min_dist <= LOCAL_RADIUS_KM:
            confidence = "MODERATE_SUBURBAN"
        else:
            confidence = "REMOTE_BACKGROUND"

        station_summary_rows.append({
            "station_id": s_id,
            "station_name": s_name,
            "station_type": s["station_type"],
            "nearest_link_km": round(min_dist, 2),
            "nearest_link_id": link_dists[int(np.argmin(distances))][0],
            "links_within_5km": int(np.sum(distances <= 5.0)),
            "links_within_10km": num_local,
            "spatial_confidence_flag": confidence,
        })

        for idx, (l_id, l_name, d) in enumerate(link_dists):
            weight_rows.append({
                "station_id": s_id,
                "station_name": s_name,
                "link_id": l_id,
                "link_name_en": l_name,
                "distance_km": round(d, 4),
                "idw_weight_global": float(round(norm_weights_global[idx], 6)),
                "idw_weight_local": float(round(norm_weights_local[idx], 6)),
                "is_within_10km": bool(local_mask[idx]),
            })

    df_weights = pd.DataFrame(weight_rows)
    df_station_summary = pd.DataFrame(station_summary_rows).sort_values("nearest_link_km").reset_index(drop=True)

    return df_weights, df_station_summary


def project_traffic_to_stations(df_weights: pd.DataFrame) -> pd.DataFrame:
    """Project hourly traffic speeds and congestion from links to stations using IDW weights."""
    print(f"\nLoading hourly link traffic data from: {TRAFFIC_HOURLY_PATH}")
    # We only need the 6 georeferenced links for spatial IDW projection
    georef_link_ids = df_weights["link_id"].unique().tolist()
    print(f"Filtering to the {len(georef_link_ids)} georeferenced links: {georef_link_ids}")

    df_hourly = pd.read_parquet(
        TRAFFIC_HOURLY_PATH,
        filters=[("link_id", "in", georef_link_ids)]
    )
    print(f"Loaded {len(df_hourly):,} hourly link records for georeferenced links.")

    # Merge weights with hourly data
    # Key: link_id
    df_merged = pd.merge(
        df_hourly,
        df_weights[["station_id", "station_name", "link_id", "distance_km", "idw_weight_global", "idw_weight_local", "is_within_10km"]],
        on="link_id",
        how="inner"
    )

    # Compute weighted speed and congestion for every station and hourly_timestamp
    df_merged["weighted_speed_global"] = df_merged["traffic_speed_hourly"] * df_merged["idw_weight_global"]
    df_merged["weighted_congestion_global"] = df_merged["traffic_congestion_hourly"] * df_merged["idw_weight_global"]

    df_station_hourly = df_merged.groupby(["station_id", "hourly_timestamp"]).agg(
        traffic_speed_station_hourly=("weighted_speed_global", "sum"),
        traffic_congestion_station_hourly=("weighted_congestion_global", "sum"),
        contributing_links_count=("link_id", "count"),
        nearest_link_distance_km=("distance_km", "min")
    ).reset_index()

    df_station_hourly["traffic_speed_station_hourly"] = df_station_hourly["traffic_speed_station_hourly"].round(2).astype("float32")
    df_station_hourly["traffic_congestion_station_hourly"] = df_station_hourly["traffic_congestion_station_hourly"].round(4).astype("float32")
    df_station_hourly["nearest_link_distance_km"] = df_station_hourly["nearest_link_distance_km"].round(2).astype("float32")
    df_station_hourly["contributing_links_count"] = df_station_hourly["contributing_links_count"].astype("int16")

    # Add spatial confidence flag
    conditions = [
        df_station_hourly["nearest_link_distance_km"] <= 5.0,
        df_station_hourly["nearest_link_distance_km"] <= LOCAL_RADIUS_KM,
    ]
    choices = ["HIGH_URBAN", "MODERATE_SUBURBAN"]
    df_station_hourly["spatial_confidence_flag"] = np.select(conditions, choices, default="REMOTE_BACKGROUND")

    # Rename hourly_timestamp to timestamp for consistency
    df_station_hourly.rename(columns={"hourly_timestamp": "timestamp"}, inplace=True)

    return df_station_hourly


def run_traffic_spatial_mapping() -> Dict[str, Any]:
    """Execute complete Phase 2.3 traffic spatial mapping and generate reports."""
    print("=" * 80)
    print("PHASE 2.3: TRAFFIC ROAD-LINK -> AQ STATION SPATIAL MAPPING (IDW p=2)")
    print("=" * 80)

    ALIGNED_DIR.mkdir(parents=True, exist_ok=True)

    df_weights, df_station_summary = compute_spatial_weights()

    print("\nStation-to-Traffic Proximity Summary:")
    print(df_station_summary.to_string(index=False))

    # Save spatial mapping weights
    df_weights.to_parquet(OUTPUT_STATION_MAPPING_PARQUET, index=False, engine="pyarrow")
    print(f"\nSaved spatial weight matrix to: {OUTPUT_STATION_MAPPING_PARQUET}")

    # Project to hourly station data
    df_station_hourly = project_traffic_to_stations(df_weights)
    df_station_hourly.to_parquet(OUTPUT_STATION_HOURLY_PARQUET, index=False, engine="pyarrow", compression="snappy")
    print(f"Saved station-projected hourly traffic to: {OUTPUT_STATION_HOURLY_PARQUET}")
    print(f"  Shape: {df_station_hourly.shape}")
    print(f"  Rows: {len(df_station_hourly):,}")
    print(f"  Unique stations: {df_station_hourly['station_id'].nunique()}")
    print(f"  Unique timestamps: {df_station_hourly['timestamp'].nunique():,}")

    # Compile audit report
    spatial_report = {
        "report_title": "Phase 2.3: Traffic Road-Link to Station Spatial Mapping Audit",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "methodology": "Inverse Distance Weighting (IDW, p=2) on Great-Circle Haversine distances",
        "station_coordinates_source": "data/raw/station_metadata/air_quality_stations.csv",
        "road_coordinates_source": "data/raw/traffic/traffic-speed-info.csv (Harbour Crossing links)",
        "unresolved_links_count": 626,
        "resolved_links_count": 6,
        "georeferenced_links": [
            {"link_id": "4651-4631", "name": "Cross-Harbour Tunnel towards Kowloon"},
            {"link_id": "46319-46512", "name": "Cross-Harbour Tunnel towards HK Island"},
            {"link_id": "4650-3651", "name": "Eastern Harbour Crossing towards Kowloon"},
            {"link_id": "36511-46502", "name": "Eastern Harbour Crossing towards HK Island"},
            {"link_id": "4652-4633", "name": "Western Harbour Crossing towards Kowloon"},
            {"link_id": "46332-46522", "name": "Western Harbour Crossing towards HK Island"}
        ],
        "distance_statistics": {
            "min_distance_km": float(df_weights["distance_km"].min()),
            "max_distance_km": float(df_weights["distance_km"].max()),
            "mean_nearest_link_km": float(round(df_station_summary["nearest_link_km"].mean(), 2)),
        },
        "station_proximity_table": df_station_summary.to_dict(orient="records"),
        "tap_mun_audit": {
            "station_name": "TAP MUN",
            "station_type": "General (Rural Background)",
            "nearest_link_distance_km": float(df_station_summary[df_station_summary["station_name"] == "TAP MUN"]["nearest_link_km"].iloc[0]),
            "nearest_link_id": str(df_station_summary[df_station_summary["station_name"] == "TAP MUN"]["nearest_link_id"].iloc[0]),
            "spatial_confidence": "REMOTE_BACKGROUND",
            "scientific_note": (
                "Tap Mun is a remote rural island without vehicular roads. Projected traffic features "
                "represent distant cross-territory harbour traffic and are explicitly flagged as REMOTE_BACKGROUND."
            )
        }
    }

    with open(OUTPUT_SPATIAL_REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(spatial_report, f, indent=2)
    print(f"Saved spatial report to: {OUTPUT_SPATIAL_REPORT_JSON}")

    return spatial_report


if __name__ == "__main__":
    run_traffic_spatial_mapping()
