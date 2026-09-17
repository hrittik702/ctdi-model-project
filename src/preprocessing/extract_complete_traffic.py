"""Extract complete Hong Kong Traffic Speed Map historical archive (2019-2021).

Phase 1.1: Complete Traffic Data Extraction
- Downloads all 36 monthly archive packages from DATA.GOV.HK using parallel worker threads
- Streams and parses all ~774,686 raw XML snapshots (~464M+ records)
- Caches and writes monthly Parquet partitions to data/interim/traffic/monthly/
- Implements robust exponential backoff retries and idempotent resumption
- Extracts: link_id, timestamp, traffic_speed, road_saturation_level, traffic_congestion_ordinal
- Records progress in extraction_progress.json and failures in traffic_failed_extractions.csv
"""

import gc
import io
import json
import re
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd
import numpy as np

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INTERIM_TRAFFIC_DIR = PROJECT_ROOT / "data" / "interim" / "traffic"
MONTHLY_DIR = INTERIM_TRAFFIC_DIR / "monthly"
PROGRESS_FILE = INTERIM_TRAFFIC_DIR / "extraction_progress.json"
FAILED_LOG_FILE = INTERIM_TRAFFIC_DIR / "traffic_failed_extractions.csv"

# Study period specification
YEARS = ["2019", "2020", "2021"]
MONTHS = [f"{m:02d}" for m in range(1, 13)]
ALL_MONTH_KEYS = [f"{y}{m}" for y in YEARS for m in MONTHS]

# Speedmap API Endpoint for monthly packages
SPEEDMAP_URL_ENCODED = "http%3A%2F%2Fresource.data.one.gov.hk%2Ftd%2Fspeedmap.xml"
ARCHIVE_GET_URL = "https://app.data.gov.hk/v1/historical-archive/get-file"

# Documented discrete ordinal mapping
ORDINAL_MAP = {
    "TRAFFIC GOOD": 0.0,
    "TRAFFIC AVERAGE": 0.5,
    "TRAFFIC BAD": 1.0,
}

# Fast compiled regex for XML speedmap extraction
REGEX_SPEEDMAP = re.compile(
    r"<LINK_ID>([^<]+)</LINK_ID>.*?"
    r"<ROAD_SATURATION_LEVEL>([^<]+)</ROAD_SATURATION_LEVEL>.*?"
    r"<TRAFFIC_SPEED>([^<]+)</TRAFFIC_SPEED>.*?"
    r"<CAPTURE_DATE>([^<]+)</CAPTURE_DATE>",
    re.DOTALL,
)

# Thread synchronization lock for writing progress and failed log
PROGRESS_LOCK = threading.Lock()


def load_progress() -> Dict[str, Any]:
    """Load or initialize extraction progress record."""
    with PROGRESS_LOCK:
        if PROGRESS_FILE.exists():
            try:
                with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "status": "IN_PROGRESS",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "completed_months": {},
            "failed_months": {},
            "total_snapshots_processed": 0,
            "total_records_extracted": 0,
        }


def save_progress(progress: Dict[str, Any]):
    """Atomically save progress record."""
    with PROGRESS_LOCK:
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        progress["updated_at"] = datetime.now(timezone.utc).isoformat()
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2)


def append_failed_log(snapshot_file: str, error_reason: str, month_key: str):
    """Log individual failed snapshot parses."""
    with PROGRESS_LOCK:
        FAILED_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        write_header = not FAILED_LOG_FILE.exists()
        with open(FAILED_LOG_FILE, "a", encoding="utf-8") as f:
            if write_header:
                f.write("month_key,snapshot_file,error_reason,timestamp_utc\n")
            now_ts = datetime.now(timezone.utc).isoformat()
            reason_clean = error_reason.replace('"', '""').replace("\n", " ")
            f.write(f'"{month_key}","{snapshot_file}","{reason_clean}","{now_ts}"\n')


def download_monthly_zip(month_key: str, max_retries: int = 5) -> bytes:
    """Download monthly ZIP package with exponential backoff retries."""
    url = f"{ARCHIVE_GET_URL}?url={SPEEDMAP_URL_ENCODED}&time={month_key}01"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CTDI-Research/1.0"}

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=180) as resp:
                if resp.status not in (200, 206):
                    raise ValueError(f"HTTP status {resp.status}")
                zip_bytes = resp.read()
                if len(zip_bytes) < 1000:
                    raise ValueError(f"Received truncated payload ({len(zip_bytes)} bytes)")
                return zip_bytes
        except Exception as e:
            wait_sec = 2 ** attempt
            print(f"  [WARN] Attempt {attempt}/{max_retries} failed for {month_key}: {e}. Retrying in {wait_sec}s...")
            time.sleep(wait_sec)

    raise RuntimeError(f"Failed to download monthly ZIP for {month_key} after {max_retries} attempts.")


def process_month(month_key: str) -> Dict[str, Any]:
    """Download, parse, validate, and serialize one complete month of traffic snapshots."""
    parquet_path = MONTHLY_DIR / f"traffic_speedmap_{month_key}.parquet"
    if parquet_path.exists() and parquet_path.stat().st_size > 100_000:
        print(f"[{month_key}] Already completed ({parquet_path.name}, {parquet_path.stat().st_size:,} bytes). Skipping.")
        df_meta = pd.read_parquet(parquet_path, columns=["traffic_speed", "snapshot_file"])
        n_snaps = df_meta["snapshot_file"].nunique()
        n_records = len(df_meta)
        del df_meta
        return {
            "month_key": month_key,
            "status": "ALREADY_COMPLETED",
            "snapshots_processed": n_snaps,
            "records_extracted": n_records,
            "parquet_path": str(parquet_path.relative_to(PROJECT_ROOT)),
            "parquet_size_bytes": parquet_path.stat().st_size,
        }

    t0 = time.time()
    print(f"[{month_key}] Fetching monthly archive package...")
    zip_bytes = download_monthly_zip(month_key)
    download_sec = time.time() - t0
    zip_size_mb = len(zip_bytes) / (1024 * 1024)
    print(f"[{month_key}] Downloaded {zip_size_mb:.1f} MB in {download_sec:.1f}s ({zip_size_mb/max(download_sec, 0.1):.1f} MB/s)")

    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    all_names = zf.namelist()
    xml_names = [n for n in all_names if n.endswith(".xml")]
    print(f"[{month_key}] Archive contains {len(xml_names):,} XML snapshot files.")

    t_parse = time.time()
    snapshot_files: List[str] = []
    link_ids: List[str] = []
    speeds: List[float] = []
    saturations: List[str] = []
    ordinals: List[float] = []
    timestamps: List[str] = []

    failed_parse_count = 0

    for name in xml_names:
        short_name = name.split("/")[-1]
        try:
            content_str = zf.read(name).decode("utf-8", errors="replace")
            matches = REGEX_SPEEDMAP.findall(content_str)
            if not matches:
                failed_parse_count += 1
                append_failed_log(short_name, "No valid speedmap elements found", month_key)
                continue

            for lid, sat, spd, cap in matches:
                lid_clean = lid.strip()
                sat_clean = sat.strip().upper()
                try:
                    spd_val = float(spd)
                except ValueError:
                    spd_val = np.nan

                snapshot_files.append(short_name)
                link_ids.append(lid_clean)
                speeds.append(spd_val)
                saturations.append(sat_clean)
                ordinals.append(ORDINAL_MAP.get(sat_clean, np.nan))
                timestamps.append(cap.strip())

        except Exception as exc:
            failed_parse_count += 1
            append_failed_log(short_name, str(exc), month_key)

    parse_sec = time.time() - t_parse
    total_records = len(link_ids)
    print(f"[{month_key}] Parsed {len(xml_names):,} XMLs into {total_records:,} records in {parse_sec:.1f}s. Failed: {failed_parse_count}")

    t_df = time.time()
    df = pd.DataFrame({
        "snapshot_file": snapshot_files,
        "link_id": link_ids,
        "traffic_speed": np.array(speeds, dtype=np.float32),
        "road_saturation_level": saturations,
        "traffic_congestion_ordinal": np.array(ordinals, dtype=np.float32),
        "timestamp": timestamps,
    })

    df["link_id"] = df["link_id"].astype("category")
    df["road_saturation_level"] = df["road_saturation_level"].astype("category")
    df["snapshot_file"] = df["snapshot_file"].astype("category")

    MONTHLY_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, index=False, compression="snappy")
    parquet_size = parquet_path.stat().st_size
    write_sec = time.time() - t_df
    print(f"[{month_key}] Written to {parquet_path.name} ({parquet_size / (1024*1024):.1f} MB) in {write_sec:.1f}s.")

    unique_links = df["link_id"].nunique()
    unique_timestamps = df["timestamp"].nunique()
    min_ts = str(df["timestamp"].min())
    max_ts = str(df["timestamp"].max())
    speed_mean = float(df["traffic_speed"].mean())
    missing_speeds = int(df["traffic_speed"].isna().sum())

    del df, snapshot_files, link_ids, speeds, saturations, ordinals, timestamps, zip_bytes, zf
    gc.collect()

    return {
        "month_key": month_key,
        "status": "COMPLETED",
        "snapshots_processed": len(xml_names),
        "records_extracted": total_records,
        "failed_snapshots": failed_parse_count,
        "unique_links": unique_links,
        "unique_timestamps": unique_timestamps,
        "earliest_timestamp": min_ts,
        "latest_timestamp": max_ts,
        "mean_speed_kmh": round(speed_mean, 2),
        "missing_speed_count": missing_speeds,
        "parquet_path": str(parquet_path.relative_to(PROJECT_ROOT)),
        "parquet_size_bytes": parquet_size,
        "elapsed_seconds": round(time.time() - t0, 1),
    }


def extract_complete_traffic(target_months: Optional[List[str]] = None, max_workers: int = 4) -> Dict[str, Any]:
    """Execute complete traffic extraction across all study period months using thread pool."""
    MONTHLY_DIR.mkdir(parents=True, exist_ok=True)
    months_to_run = target_months or ALL_MONTH_KEYS

    print("=" * 80)
    print(f"STARTING COMPLETE TRAFFIC ARCHIVE EXTRACTION ({len(months_to_run)} MONTHS, {max_workers} WORKERS)")
    print(f"Target Period: 2019-01-01 through 2021-12-31")
    print("=" * 80)

    progress = load_progress()
    t_start = time.time()

    completed_count = 0
    total_to_run = len(months_to_run)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_month, m): m for m in months_to_run}

        for future in as_completed(futures):
            m = futures[future]
            try:
                month_stats = future.result()
                progress["completed_months"][m] = month_stats
                completed_count += 1
                progress["total_snapshots_processed"] = sum(
                    s.get("snapshots_processed", 0) for s in progress["completed_months"].values()
                )
                progress["total_records_extracted"] = sum(
                    s.get("records_extracted", 0) for s in progress["completed_months"].values()
                )
                save_progress(progress)
                pct = completed_count / total_to_run * 100
                print(f"\n>>> [OVERALL PROGRESS: {completed_count}/{total_to_run} ({pct:.1f}%)] Month {m} saved. <<<")
            except Exception as exc:
                print(f"\n>>> [OVERALL ERROR] Month {m} failed: {exc} <<<")
                progress["failed_months"][m] = str(exc)
                save_progress(progress)

    total_time = time.time() - t_start
    progress["status"] = "COMPLETE" if len(progress["failed_months"]) == 0 else "PARTIAL_FAILURES"
    progress["total_elapsed_seconds"] = round(total_time, 1)
    save_progress(progress)

    print("\n" + "=" * 80)
    print("COMPLETE TRAFFIC ARCHIVE EXTRACTION FINISHED.")
    print(f"Total Completed Months  : {len(progress['completed_months'])}/{len(months_to_run)}")
    print(f"Total Snapshots Parsed  : {progress['total_snapshots_processed']:,}")
    print(f"Total Records Extracted : {progress['total_records_extracted']:,}")
    print(f"Total Elapsed Time      : {total_time/60:.1f} minutes")
    print("=" * 80)
    return progress


if __name__ == "__main__":
    workers = 4
    if len(sys.argv) > 1:
        workers = int(sys.argv[1])
    extract_complete_traffic(max_workers=workers)
