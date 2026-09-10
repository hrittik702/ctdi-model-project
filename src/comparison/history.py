"""Experiment history management and persistence."""

import os
import json
import time
from typing import Dict, List, Any, Optional

HISTORY_FILE = "results/experiments/comparison_history.json"


class ExperimentHistoryManager:
    """Manages storage and retrieval of comparative benchmarking runs."""

    def __init__(self, history_path: str = HISTORY_FILE):
        self.history_path = history_path
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        if not os.path.exists(self.history_path):
            with open(self.history_path, "w") as f:
                json.dump([], f)

    def list_experiments(self) -> List[Dict[str, Any]]:
        """Returns list of past experiment summaries."""
        try:
            with open(self.history_path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Fetches full record for a specific experiment ID."""
        experiments = self.list_experiments()
        return next((e for e in experiments if e["experiment_id"] == experiment_id), None)

    def save_experiment(self, experiment_record: Dict[str, Any]) -> str:
        """Appends a new experiment record and returns its experiment ID."""
        experiments = self.list_experiments()
        exp_id = experiment_record.get(
            "experiment_id",
            f"EXP-LAB-{len(experiments) + 1:03d}"
        )
        experiment_record["experiment_id"] = exp_id
        experiment_record["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

        # Keep history capped at 100 experiments
        experiments.insert(0, experiment_record)
        experiments = experiments[:100]

        with open(self.history_path, "w") as f:
            json.dump(experiments, f, indent=2)

        return exp_id

    def compare_experiments(self, id_a: str, id_b: str) -> Dict[str, Any]:
        """Compares two historical experiments side-by-side."""
        exp_a = self.get_experiment(id_a)
        exp_b = self.get_experiment(id_b)

        if not exp_a or not exp_b:
            raise ValueError(f"One or both experiments not found ({id_a}, {id_b})")

        ds_a = exp_a.get("dataset_id") or exp_a.get("dataset")
        ds_b = exp_b.get("dataset_id") or exp_b.get("dataset")
        seed_a = exp_a.get("missingness", {}).get("random_seed") if isinstance(exp_a.get("missingness"), dict) else exp_a.get("random_seed")
        seed_b = exp_b.get("missingness", {}).get("random_seed") if isinstance(exp_b.get("missingness"), dict) else exp_b.get("random_seed")

        return {
            "experiment_a": exp_a,
            "experiment_b": exp_b,
            "dataset_match": ds_a == ds_b,
            "seed_match": seed_a == seed_b
        }
