"""Canonical Prediction Data representation.

Acts as the Single Source of Truth across the entire comparison lab:
All metrics, ranking tables, charts, failure cases, and CSV exports derive strictly
from this exact data structure.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd


@dataclass
class PointRecord:
    """Canonical record for a single timestep and pollutant."""
    timestamp: str
    pollutant: str
    ground_truth: Optional[float]
    observed: Optional[float]
    mask: int  # 1=observed, 0=artificially or naturally missing
    is_eval: int  # 1=hidden ground-truth evaluation point, 0=otherwise
    predictions: Dict[str, Optional[float]] = field(default_factory=dict)
    errors: Dict[str, Optional[float]] = field(default_factory=dict)
    abs_errors: Dict[str, Optional[float]] = field(default_factory=dict)
    sq_errors: Dict[str, Optional[float]] = field(default_factory=dict)
    gap_length: int = 0
    is_peak: bool = False
    pollution_level: str = "Moderate"

class InvarianceResult(dict):
    """Dictionary that can also be unpacked as (is_valid, max_diff, violations)."""
    def __iter__(self):
        yield self["valid"]
        yield self["max_diff"]
        yield self["violations"]


class CanonicalPredictionData:
    """
    Container for unified comparison experiment predictions.
    Guarantees exact parity across all analytical views and data exports.
    """

    def __init__(self, pollutants: List[str], model_ids: List[str]):
        self.pollutants = pollutants
        self.model_ids = model_ids
        self.records: List[PointRecord] = []
        self._df: Optional[pd.DataFrame] = None

    def add_record(self, record: PointRecord):
        self.records.append(record)
        self._df = None

    def to_dataframe(self) -> pd.DataFrame:
        """Converts canonical records into a flat pandas DataFrame."""
        if self._df is not None:
            return self._df

        rows = []
        for r in self.records:
            row = {
                "timestamp": r.timestamp,
                "pollutant": r.pollutant,
                "ground_truth": r.ground_truth,
                "observed": r.observed,
                "mask": r.mask,
                "is_eval": r.is_eval,
                "gap_length": r.gap_length,
                "is_peak": r.is_peak,
                "pollution_level": r.pollution_level
            }
            for m_id in self.model_ids:
                pred = r.predictions.get(m_id)
                err = r.errors.get(m_id)
                abs_e = r.abs_errors.get(m_id)
                row[f"{m_id}_pred"] = pred
                row[f"{m_id}_err"] = err
                row[f"{m_id}_abs_err"] = abs_e

            rows.append(row)

        self._df = pd.DataFrame(rows)
        return self._df

    def to_chart_timeseries(self, pollutant: str) -> List[Dict[str, Any]]:
        """
        Extracts formatted time-series data for the selected pollutant.
        Derives directly from canonical records.
        """
        pts = [r for r in self.records if r.pollutant == pollutant]
        chart_data = []
        for p in pts:
            clock = p.timestamp.split(" ")[1] if " " in p.timestamp else p.timestamp
            entry = {
                "timestamp": p.timestamp,
                "time": clock,
                "hour": clock,
                "ground_truth": p.ground_truth,
                "observed": p.observed if p.mask == 1 else None,
                "mask": p.mask,
                "is_eval": p.is_eval,
                "is_peak": p.is_peak,
                "gap_length": p.gap_length
            }
            for m_id in self.model_ids:
                entry[m_id] = p.predictions.get(m_id)
            chart_data.append(entry)
        return chart_data

    def to_csv_string(self) -> str:
        """Generates comprehensive canonical CSV string for export."""
        df = self.to_dataframe()
        return df.to_csv(index=False)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "CanonicalPredictionData":
        """Reconstructs CanonicalPredictionData directly from a pandas DataFrame."""
        pred_cols = [c for c in df.columns if c.endswith("_pred")]
        model_ids = [c[:-5] for c in pred_cols]
        pollutants = list(df["pollutant"].unique()) if "pollutant" in df.columns else ["PM2.5", "PM10", "NO2", "SO2", "O3"]

        canonical = cls(pollutants=pollutants, model_ids=model_ids)

        for _, row in df.iterrows():
            preds = {}
            errs = {}
            abs_errs = {}
            sq_errs = {}
            for m_id in model_ids:
                p_val = row.get(f"{m_id}_pred")
                if pd.notna(p_val):
                    p_float = float(p_val)
                    preds[m_id] = p_float
                    gt_val = row.get("ground_truth")
                    if pd.notna(gt_val):
                        e_float = p_float - float(gt_val)
                        errs[m_id] = round(e_float, 2)
                        abs_errs[m_id] = round(abs(e_float), 2)
                        sq_errs[m_id] = round(e_float ** 2, 4)
                    else:
                        errs[m_id] = None
                        abs_errs[m_id] = None
                        sq_errs[m_id] = None
                else:
                    preds[m_id] = None
                    errs[m_id] = None
                    abs_errs[m_id] = None
                    sq_errs[m_id] = None

            is_eval_raw = row.get("is_eval", 0)
            is_eval = 1 if is_eval_raw in (1, "1", True, "True", "true") else 0
            mask_raw = row.get("mask", 1)
            mask = 1 if mask_raw in (1, "1", True, "True", "true") else 0
            is_peak_raw = row.get("is_peak", False)
            is_peak = True if is_peak_raw in (1, "1", True, "True", "true") else False

            rec = PointRecord(
                timestamp=str(row.get("timestamp", "")),
                pollutant=str(row.get("pollutant", "")),
                ground_truth=float(row["ground_truth"]) if pd.notna(row.get("ground_truth")) else None,
                observed=float(row["observed"]) if pd.notna(row.get("observed")) else None,
                mask=mask,
                is_eval=is_eval,
                predictions=preds,
                errors=errs,
                abs_errors=abs_errs,
                sq_errors=sq_errs,
                gap_length=int(row.get("gap_length", 0)) if pd.notna(row.get("gap_length")) else 0,
                is_peak=is_peak,
                pollution_level=str(row.get("pollution_level", "Moderate"))
            )
            canonical.add_record(rec)

        return canonical

    @classmethod
    def from_csv_file(cls, csv_path: str) -> "CanonicalPredictionData":
        """Loads canonical prediction dataset from a CSV file."""
        df = pd.read_csv(csv_path)
        return cls.from_dataframe(df)

    def validate_invariance(self, tolerance: float = 1e-3) -> InvarianceResult:
        """
        Validates:
        1. Observed Value Preservation: output[observed] == input[observed] within tolerance.
        2. Evaluated cell consistency across models.
        """
        violations = []
        max_diff = 0.0
        observed_pts = [r for r in self.records if r.mask == 1 and r.observed is not None]
        for r in observed_pts:
            obs = r.observed
            for m_id, pred in r.predictions.items():
                if pred is not None:
                    diff = abs(pred - obs)
                    if diff > max_diff:
                        max_diff = diff
                    if diff > tolerance:
                        violations.append({
                            "model_id": m_id,
                            "timestamp": r.timestamp,
                            "pollutant": r.pollutant,
                            "observed": obs,
                            "prediction": pred,
                            "diff": diff
                        })

        return InvarianceResult({
            "valid": len(violations) == 0,
            "max_diff": round(float(max_diff), 6),
            "total_observed_cells": len(observed_pts),
            "violation_count": len(violations),
            "violations": violations[:5]
        })


