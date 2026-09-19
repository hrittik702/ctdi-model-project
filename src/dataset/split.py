"""Chronological dataset split management and validation.

Verifies and manages the strict chronological partitions:
- Train: 2019-01-01 00:00 to 2021-02-05 23:00 (294,160 windows, 69.96%)
- Buffer 1 (train/val purge): 24-hour purge calendar day 2021-02-06 (752 excluded windows, 0.18%)
- Val: 2021-02-07 00:00 to 2021-07-20 23:00 (62,608 windows, 14.89%)
- Buffer 2 (val/test purge): 24-hour purge calendar day 2021-07-21 (752 excluded windows, 0.18%)
- Test: 2021-07-22 00:00 to 2021-12-31 23:00 (62,224 windows, 14.80%)

Clarification on Purge Buffers:
- Purge duration: 24.0 hours (the entire calendar day 2021-02-06 for Buffer 1; 2021-07-21 for Buffer 2).
- Physical temporal separation: exactly 25.0 hours between last hour of preceding split and first hour of following split.
- Excluded sliding windows: exactly 47 windows per station (752 windows network-wide) whose 24-hour frame
  intersects the 24-hour purge calendar day.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union
import pandas as pd


SPLIT_NAMES = ["train", "buffer_train_val", "val", "buffer_val_test", "test"]


class ChronologicalSplitManager:
    """Manages and verifies chronological dataset splitting with purge buffers."""

    def __init__(self, metadata_df: pd.DataFrame):
        """Initialize split manager with window metadata.
        
        Args:
            metadata_df: DataFrame loaded from window_metadata.parquet.
        """
        required_cols = ["window_id", "station_id", "start_timestamp", "end_timestamp", "temporal_split"]
        for col in required_cols:
            if col not in metadata_df.columns:
                raise ValueError(f"Missing required column '{col}' in metadata_df")
        self.df = metadata_df

    def get_split_indices(self, split_name: str) -> List[int]:
        """Get window_ids belonging to a specific split."""
        if split_name not in SPLIT_NAMES:
            raise ValueError(f"Unknown split '{split_name}'. Expected one of {SPLIT_NAMES}")
        return self.df[self.df["temporal_split"] == split_name]["window_id"].tolist()

    def summarize_splits(self) -> Dict[str, Any]:
        """Compute exhaustive summary statistics for all splits."""
        total_windows = len(self.df)
        summary: Dict[str, Any] = {
            "total_windows": total_windows,
            "unique_stations": int(self.df["station_id"].nunique()),
            "splits": {},
            "buffer_architecture": {
                "buffer_train_val": {
                    "purge_calendar_date": "2021-02-06",
                    "purge_duration_hours": 24.0,
                    "temporal_separation_gap_hours": 25.0,
                    "train_last_timestamp": "2021-02-05 23:00:00",
                    "val_first_timestamp": "2021-02-07 00:00:00",
                    "excluded_windows_count": 752,
                    "excluded_windows_per_station": 47,
                    "explanation": "752 sliding windows (47/station) are purged because their 24h span intersects the 24h calendar day 2021-02-06.",
                },
                "buffer_val_test": {
                    "purge_calendar_date": "2021-07-21",
                    "purge_duration_hours": 24.0,
                    "temporal_separation_gap_hours": 25.0,
                    "val_last_timestamp": "2021-07-20 23:00:00",
                    "test_first_timestamp": "2021-07-22 00:00:00",
                    "excluded_windows_count": 752,
                    "excluded_windows_per_station": 47,
                    "explanation": "752 sliding windows (47/station) are purged because their 24h span intersects the 24h calendar day 2021-07-21.",
                },
            }
        }

        for split_name in SPLIT_NAMES:
            grp = self.df[self.df["temporal_split"] == split_name]
            n_win = len(grp)
            pct = (n_win / total_windows) * 100.0 if total_windows > 0 else 0.0

            miss_cells = int(grp["missing_pollutant_cells"].sum()) if "missing_pollutant_cells" in grp else 0
            tot_cells = n_win * 120  # 24 hours * 5 pollutants
            miss_pct = (miss_cells / tot_cells) * 100.0 if tot_cells > 0 else 0.0
            win_with_miss = int((grp["missing_pollutant_cells"] > 0).sum()) if "missing_pollutant_cells" in grp else 0

            summary["splits"][split_name] = {
                "window_count": n_win,
                "percentage": round(pct, 2),
                "start_min": str(grp["start_timestamp"].min()),
                "start_max": str(grp["start_timestamp"].max()),
                "end_min": str(grp["end_timestamp"].min()),
                "end_max": str(grp["end_timestamp"].max()),
                "station_count": int(grp["station_id"].nunique()),
                "missing_pollutant_cells": miss_cells,
                "missing_pollutant_pct": round(miss_pct, 2),
                "windows_with_missing": win_with_miss,
            }

        return summary

    def verify_no_overlap(self) -> bool:
        """Verify that training, validation, and test windows have zero temporal overlap.
        
        Returns:
            True if all checks pass. Raises AssertionError if overlap detected.
        """
        train_end = self.df[self.df["temporal_split"] == "train"]["end_timestamp"].max()
        val_start = self.df[self.df["temporal_split"] == "val"]["start_timestamp"].min()
        val_end = self.df[self.df["temporal_split"] == "val"]["end_timestamp"].max()
        test_start = self.df[self.df["temporal_split"] == "test"]["start_timestamp"].min()

        # Check train-val separation
        t_gap_1 = (pd.to_datetime(val_start) - pd.to_datetime(train_end)).total_seconds() / 3600.0
        if t_gap_1 < 24.0:
            raise AssertionError(f"Data leakage detected: train-val temporal gap is {t_gap_1}h (expected >= 24h)")

        # Check val-test separation
        t_gap_2 = (pd.to_datetime(test_start) - pd.to_datetime(val_end)).total_seconds() / 3600.0
        if t_gap_2 < 24.0:
            raise AssertionError(f"Data leakage detected: val-test temporal gap is {t_gap_2}h (expected >= 24h)")

        return True

    def export_manifest(self, output_path: Union[str, Path]):
        """Export split summary manifest to JSON."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        summary = self.summarize_splits()
        with open(p, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
