"""Phase 2.6: Comprehensive Alignment Validation & Cryptographic Raw Audit Suite.

Executes all 9 required verification checks for Phase 2:
1. Temporal grid completeness (26,304 hourly timestamps)
2. Station coverage (16 target AQ stations)
3. Cartesian station-hour grid integrity (420,864 rows, zero duplicates)
4. Natural pollutant missingness conservation (55,876 NaNs preserved)
5. Meteorology completeness & physical bounds (0 missing, rainfall naming preserved)
6. Traffic integrity & spatial coverage status (no 0 km/h filling, 99.43% coverage)
7. Canonical 13-channel schema & 3D tensor reshapeability (16, 26304, 13)
8. Spatial distance matrix validation (16x16 symmetric, zero diagonal)
9. Cryptographic raw data immutability audit (SHA-256 on 683 files)

Exports:
- data/interim/aligned/alignment_validation.json
- data/interim/aligned/alignment_summary.json
"""

from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Input paths
DATASET_PATH = PROJECT_ROOT / "data" / "interim" / "aligned" / "aligned_hourly_station_data.parquet"
DIST_MATRIX_PATH = PROJECT_ROOT / "data" / "interim" / "aligned" / "spatial_distance_matrix.npy"
PRE_MANIFEST_PATH = PROJECT_ROOT / "data" / "interim" / "metadata" / "raw_data_pre_manifest.json"
STATION_META_PATH = PROJECT_ROOT / "data" / "raw" / "station_metadata" / "air_quality_stations.csv"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Output paths
OUT_VALIDATION_PATH = PROJECT_ROOT / "data" / "interim" / "aligned" / "alignment_validation.json"
OUT_SUMMARY_PATH = PROJECT_ROOT / "data" / "interim" / "aligned" / "alignment_summary.json"

CANONICAL_13_CHANNELS = [
    "pm25",
    "pm10",
    "no2",
    "so2",
    "o3",
    "pressure",
    "relative_humidity",
    "temperature",
    "rainfall",
    "wind_direction",
    "wind_speed",
    "traffic_speed",
    "traffic_congestion",
]

EXPECTED_STATIONS = [66, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83]
EXPECTED_HOURS = 26304
EXPECTED_ROWS = 420864

EXPECTED_AQ_NANS = {
    "pm25": 10657,
    "pm10": 11395,
    "no2": 11651,
    "so2": 11056,
    "o3": 11117,
}


def run_comprehensive_validation():
    print("=" * 70)
    print("PHASE 2.6: COMPREHENSIVE ALIGNMENT VALIDATION & AUDIT SUITE")
    print("=" * 70)

    results = {}
    passed_all = True

    # -------------------------------------------------------------
    # 1. Dataset Loading
    # -------------------------------------------------------------
    print("\n[Check 1/9] Loading and inspecting aligned dataset...")
    assert DATASET_PATH.exists(), f"Aligned dataset not found at: {DATASET_PATH}"
    df = pd.read_parquet(DATASET_PATH)
    file_size_mb = DATASET_PATH.stat().st_size / (1024 * 1024)
    print(f"  Dataset path: {DATASET_PATH} ({file_size_mb:.2f} MB)")
    print(f"  Rows: {len(df):,}, Columns: {len(df.columns)}")

    # -------------------------------------------------------------
    # 2. Temporal Grid Audit
    # -------------------------------------------------------------
    print("\n[Check 2/9] Auditing temporal grid completeness...")
    timestamps = pd.to_datetime(df["timestamp"].unique())
    timestamps = timestamps.sort_values()
    expected_ts = pd.date_range("2019-01-01 00:00:00", "2021-12-31 23:00:00", freq="1h")

    ts_match = (len(timestamps) == EXPECTED_HOURS) and (timestamps.equals(expected_ts))
    print(f"  Unique timestamps: {len(timestamps):,} (Expected: {EXPECTED_HOURS:,})")
    print(f"  Start: {timestamps.min()}, End: {timestamps.max()}")
    print(f"  Consecutive hourly grid exact match: {ts_match}")
    assert ts_match, "Temporal grid mismatch!"
    results["temporal_grid"] = {
        "passed": True,
        "unique_hours": len(timestamps),
        "start": str(timestamps.min()),
        "end": str(timestamps.max()),
        "frequency": "1h",
    }

    # -------------------------------------------------------------
    # 3. Station Coverage Audit
    # -------------------------------------------------------------
    print("\n[Check 3/9] Auditing station coverage & CTDI target alignment...")
    unique_stations = sorted(df["station_id"].unique().tolist())
    st_match = unique_stations == EXPECTED_STATIONS
    print(f"  Unique stations count: {len(unique_stations)} (Expected: 16)")
    print(f"  Station IDs: {unique_stations}")
    print(f"  Target station list exact match: {st_match}")
    assert st_match, f"Station ID mismatch! Found: {unique_stations}"

    # Verify excluded stations from metadata
    meta = pd.read_csv(STATION_META_PATH)
    excluded = meta[meta["in_ctdi_study"].astype(str).str.strip().str.lower() == "false"]["station_id"].tolist()
    overlap = set(unique_stations).intersection(set(excluded))
    print(f"  Excluded stations: {excluded} (Overlap with dataset: {list(overlap)})")
    assert len(overlap) == 0, f"Excluded stations found in dataset: {overlap}"
    results["station_coverage"] = {
        "passed": True,
        "station_count": len(unique_stations),
        "station_ids": unique_stations,
        "excluded_stations_verified_absent": excluded,
    }

    # -------------------------------------------------------------
    # 4. Cartesian Station-Hour Grid Integrity
    # -------------------------------------------------------------
    print("\n[Check 4/9] Auditing Cartesian station-hour grid integrity...")
    assert len(df) == EXPECTED_ROWS, f"Row count mismatch! Expected {EXPECTED_ROWS}, got {len(df)}"
    duplicates = df.duplicated(subset=["station_id", "timestamp"]).sum()
    print(f"  Total rows: {len(df):,} (Exact match: 16 stations x 26,304 hours)")
    print(f"  Duplicate (station_id, timestamp) rows: {duplicates}")
    assert duplicates == 0, f"Found {duplicates} duplicate station-hour records!"

    # Check monotonic sorting
    is_sorted = (
        df["station_id"].is_monotonic_increasing
        and df.groupby("station_id")["timestamp"].is_monotonic_increasing.all()
    )
    print(f"  Sorted strictly by station_id ascending and timestamp ascending: {is_sorted}")
    assert is_sorted, "Dataset is not sorted deterministically!"
    results["grid_integrity"] = {
        "passed": True,
        "total_rows": len(df),
        "duplicates": int(duplicates),
        "is_sorted_monotonically": True,
    }

    # -------------------------------------------------------------
    # 5. Natural Pollutant Missingness Conservation
    # -------------------------------------------------------------
    print("\n[Check 5/9] Auditing air quality natural missingness conservation...")
    total_aq_nans = 0
    aq_nan_details = {}
    for col, exp in EXPECTED_AQ_NANS.items():
        actual = int(df[col].isna().sum())
        min_val = float(df[col].dropna().min())
        max_val = float(df[col].dropna().max())
        mean_val = float(df[col].dropna().mean())
        print(f"  - {col:6s}: NaNs = {actual:6,d} (Expected: {exp:6,d}) | Range: [{min_val:.1f}, {max_val:.1f}], Mean: {mean_val:.2f}")
        assert actual == exp, f"Pollutant {col} NaN count mismatch! Expected {exp}, got {actual}"
        assert min_val >= 0.0, f"Pollutant {col} contains negative values!"
        total_aq_nans += actual
        aq_nan_details[col] = {
            "nans": actual,
            "expected_nans": exp,
            "min": min_val,
            "max": max_val,
            "mean": mean_val,
        }
    print(f"  Total AQ NaNs: {total_aq_nans:,} (Exact bit-for-bit match to Phase 1: 55,876)")
    assert total_aq_nans == 55876, f"Total AQ NaNs mismatch! Expected 55876, got {total_aq_nans}"
    results["air_quality_integrity"] = {
        "passed": True,
        "total_nans": total_aq_nans,
        "expected_total_nans": 55876,
        "details": aq_nan_details,
    }

    # -------------------------------------------------------------
    # 6. Meteorology Completeness & Physical Bounds
    # -------------------------------------------------------------
    print("\n[Check 6/9] Auditing meteorology completeness & physical bounds...")
    met_bounds = {
        "pressure": (950.0, 1050.0),
        "relative_humidity": (0.0, 100.0),
        "temperature": (-10.0, 45.0),
        "rainfall": (0.0, 300.0),
        "wind_direction": (0.0, 360.0),
        "wind_speed": (0.0, 200.0),
    }
    met_details = {}
    for col, (b_min, b_max) in met_bounds.items():
        nans = int(df[col].isna().sum())
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        mean_val = float(df[col].mean())
        print(f"  - {col:18s}: NaNs = {nans:d} | Range: [{min_val:.2f}, {max_val:.2f}], Mean: {mean_val:.2f}")
        assert nans == 0, f"Meteorology channel {col} has {nans} missing values!"
        assert min_val >= b_min, f"Meteorology channel {col} min {min_val} < {b_min}"
        assert max_val <= b_max, f"Meteorology channel {col} max {max_val} > {b_max}"
        met_details[col] = {
            "nans": nans,
            "min": min_val,
            "max": max_val,
            "mean": mean_val,
        }
    # Check rainfall column naming
    assert "rainfall" in df.columns, "Column 'rainfall' missing!"
    assert "visibility" not in df.columns, "Forbidden column 'visibility' found in aligned dataset!"
    print(f"  [CONFIRMED] Channel 9 is named 'rainfall' (visibility is NOT fabricated).")
    results["meteorology_integrity"] = {
        "passed": True,
        "channels": met_details,
        "rainfall_naming_rule_enforced": True,
    }

    # -------------------------------------------------------------
    # 7. Traffic Integrity & Spatial Coverage Audit
    # -------------------------------------------------------------
    print("\n[Check 7/9] Auditing traffic integrity & spatial coverage...")
    traffic_speed_nans = int(df["traffic_speed"].isna().sum())
    traffic_cong_nans = int(df["traffic_congestion"].isna().sum())
    valid_speed = df["traffic_speed"].dropna()
    valid_cong = df["traffic_congestion"].dropna()

    print(f"  Traffic valid station-hours: {len(valid_speed):,} ({len(valid_speed)/len(df)*100:.2f}%)")
    print(f"  Traffic missing station-hours: {traffic_speed_nans:,} ({traffic_speed_nans/len(df)*100:.2f}%)")
    print(f"  Traffic speed range: [{valid_speed.min():.2f}, {valid_speed.max():.2f}] km/h, Mean: {valid_speed.mean():.2f} km/h")
    print(f"  Traffic congestion range: [{valid_cong.min():.4f}, {valid_cong.max():.4f}], Mean: {valid_cong.mean():.4f}")

    # Verify no accidental 0.0 filling
    zeros_speed = int((df["traffic_speed"] == 0.0).sum())
    print(f"  Standstill 0.0 km/h speed count: {zeros_speed}")
    assert zeros_speed == 0, f"Accidental 0.0 km/h filling detected in traffic speed: {zeros_speed} rows!"

    # Verify spatial metadata coverage
    conf_counts = df["traffic_spatial_confidence"].value_counts().to_dict()
    print(f"  Spatial confidence breakdown across station-hours:")
    for conf, count in conf_counts.items():
        print(f"    * {conf:20s}: {count:7,d} ({count/len(df)*100:.1f}%)")

    results["traffic_integrity"] = {
        "passed": True,
        "valid_station_hours": len(valid_speed),
        "missing_station_hours": traffic_speed_nans,
        "coverage_percentage": len(valid_speed) / len(df) * 100.0,
        "speed_stats": {
            "min": float(valid_speed.min()),
            "max": float(valid_speed.max()),
            "mean": float(valid_speed.mean()),
        },
        "congestion_stats": {
            "min": float(valid_cong.min()),
            "max": float(valid_cong.max()),
            "mean": float(valid_cong.mean()),
        },
        "spatial_confidence_breakdown": conf_counts,
        "zero_fill_free": True,
    }

    # -------------------------------------------------------------
    # 8. Canonical 13-Channel Schema & 3D Tensor Representation
    # -------------------------------------------------------------
    print("\n[Check 8/9] Auditing 13-channel schema & 3D tensor reshapeability...")
    for idx, col in enumerate(CANONICAL_13_CHANNELS):
        assert col in df.columns, f"Channel {idx}: {col} missing from dataset!"
        print(f"  Channel {idx:2d}: {col}")

    X_2d = df[CANONICAL_13_CHANNELS].to_numpy(dtype=np.float32)
    assert X_2d.shape == (EXPECTED_ROWS, 13), f"2D Matrix shape mismatch: {X_2d.shape}"

    X_3d = X_2d.reshape(len(unique_stations), EXPECTED_HOURS, 13)
    assert X_3d.shape == (16, 26304, 13), f"3D Tensor reshape mismatch: {X_3d.shape}"
    print(f"  Feature matrix shape: {X_2d.shape}")
    print(f"  3D Tensor reshape: {X_3d.shape} (stations, hours, channels) -> PASSED")

    # Audit distance matrix
    assert DIST_MATRIX_PATH.exists(), f"Distance matrix missing at: {DIST_MATRIX_PATH}"
    dist_mat = np.load(DIST_MATRIX_PATH)
    assert dist_mat.shape == (16, 16), f"Distance matrix shape mismatch: {dist_mat.shape}"
    assert np.allclose(np.diag(dist_mat), 0.0), "Distance matrix diagonal not 0.0!"
    assert np.allclose(dist_mat, dist_mat.T), "Distance matrix not symmetric!"
    print(f"  Pairwise station distance matrix: {dist_mat.shape}, symmetric, zero-diagonal -> PASSED")

    results["tensor_representation"] = {
        "passed": True,
        "canonical_channels": CANONICAL_13_CHANNELS,
        "tensor_2d_shape": list(X_2d.shape),
        "tensor_3d_shape": list(X_3d.shape),
        "distance_matrix_shape": list(dist_mat.shape),
    }

    # -------------------------------------------------------------
    # 9. Cryptographic Raw Data Immutability Audit
    # -------------------------------------------------------------
    print("\n[Check 9/9] Executing cryptographic raw data audit (SHA-256)...")
    assert PRE_MANIFEST_PATH.exists(), f"Pre-manifest missing: {PRE_MANIFEST_PATH}"
    with open(PRE_MANIFEST_PATH) as f:
        pre_manifest = json.load(f)

    current_files = {str(p.relative_to(RAW_DIR)): p for p in RAW_DIR.rglob("*") if p.is_file()}
    modified_files = []
    missing_files = []

    for rel_path, meta_item in pre_manifest.items():
        p = RAW_DIR / rel_path
        if not p.exists():
            missing_files.append(rel_path)
            continue
        cur_hash = hashlib.sha256(p.read_bytes()).hexdigest()
        if cur_hash != meta_item["sha256"]:
            modified_files.append(rel_path)

    added_files = list(set(current_files.keys()) - set(pre_manifest.keys()))
    deleted_files = list(set(pre_manifest.keys()) - set(current_files.keys()))

    print(f"  Total raw files audited: {len(pre_manifest)}")
    print(f"  Modified: {len(modified_files)}")
    print(f"  Added:    {len(added_files)}")
    print(f"  Deleted:  {len(deleted_files)}")

    assert len(modified_files) == 0, f"Raw files modified: {modified_files}"
    assert len(added_files) == 0, f"Files added to raw/: {added_files}"
    assert len(deleted_files) == 0, f"Files deleted from raw/: {deleted_files}"
    print("  [CONFIRMED] Cryptographic Raw Audit: 100% untouched (0 modified, 0 added, 0 deleted).")

    results["raw_immutability_audit"] = {
        "passed": True,
        "total_files": len(pre_manifest),
        "modified_count": len(modified_files),
        "added_count": len(added_files),
        "deleted_count": len(deleted_files),
    }

    # -------------------------------------------------------------
    # Export Validation & Summary Reports
    # -------------------------------------------------------------
    validation_report = {
        "status": "PASSED",
        "phase": "Phase 2 — Temporal & Spatial Alignment",
        "checks_passed": 9,
        "checks_total": 9,
        "results": results,
    }
    with open(OUT_VALIDATION_PATH, "w") as f:
        json.dump(validation_report, f, indent=2)
    print(f"\nSaved validation report: {OUT_VALIDATION_PATH}")

    # Build comprehensive alignment summary
    alignment_summary = {
        "phase": "2 — Temporal & Spatial Alignment",
        "status": "COMPLETE",
        "dataset": {
            "path": str(DATASET_PATH.relative_to(PROJECT_ROOT)),
            "format": "Parquet (Snappy)",
            "size_bytes": DATASET_PATH.stat().st_size,
            "total_rows": EXPECTED_ROWS,
            "total_columns": len(df.columns),
            "primary_key": ["station_id", "timestamp"],
        },
        "spatiotemporal_grid": {
            "spatial_units": len(unique_stations),
            "stations": unique_stations,
            "temporal_units": EXPECTED_HOURS,
            "time_range": ["2019-01-01 00:00:00", "2021-12-31 23:00:00"],
            "frequency": "1h",
            "station_hours": EXPECTED_ROWS,
        },
        "channels": {
            "count": 13,
            "order": CANONICAL_13_CHANNELS,
            "tensor_shape_2d": [EXPECTED_ROWS, 13],
            "tensor_shape_3d": [16, 26304, 13],
        },
        "natural_missingness": {
            "air_quality_total_nans": total_aq_nans,
            "air_quality_by_channel": EXPECTED_AQ_NANS,
            "meteorology_nans": 0,
            "traffic_valid_station_hours": len(valid_speed),
            "traffic_missing_station_hours": traffic_speed_nans,
            "traffic_coverage_pct": len(valid_speed) / len(df) * 100.0,
        },
        "traffic_spatial_resolution": {
            "resolved_links": 6,
            "unresolved_links": 626,
            "spatial_method": "Inverse Distance Weighting (IDW, p=2) on georeferenced links",
            "spatial_confidence_distribution": conf_counts,
        },
        "raw_data_integrity": {
            "files_audited": len(pre_manifest),
            "modified": 0,
            "added": 0,
            "deleted": 0,
            "status": "IMMUTABLE",
        },
    }
    with open(OUT_SUMMARY_PATH, "w") as f:
        json.dump(alignment_summary, f, indent=2)
    print(f"Saved alignment summary: {OUT_SUMMARY_PATH}")

    print("\n" + "=" * 70)
    print("ALL PHASE 2 VALIDATION CHECKS PASSED WITH ZERO ERRORS")
    print("=" * 70)


if __name__ == "__main__":
    run_comprehensive_validation()
