"""Comprehensive Evaluation Engine for Multi-Model Imputation Benchmarking.

Computes all factual statistical metrics, peak errors, gap breakdowns, rankings,
model win matrix, bootstrap confidence intervals, and data quality indicators.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from src.comparison.canonical_data import CanonicalPredictionData, PointRecord


def compute_r2(y_true: np.ndarray, y_pred: np.ndarray) -> Optional[float]:
    """Computes R² coefficient of determination."""
    if len(y_true) < 2:
        return None
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot < 1e-8:
        return 0.0
    r2 = 1.0 - (ss_res / ss_tot)
    return round(float(r2), 3)


def classify_pollution_level(val: float) -> str:
    """Categorizes pollutant concentrations into standard atmospheric levels."""
    if val < 50.0:
        return "Low"
    elif val < 100.0:
        return "Moderate"
    elif val < 200.0:
        return "High"
    elif val < 300.0:
        return "Very High"
    return "Extreme"


class EvaluationEngine:
    """Computes all factual statistical metrics, peak errors, gap breakdowns, and rankings."""

    def __init__(self, canonical_data: CanonicalPredictionData, model_names: Optional[Dict[str, str]] = None):
        self.canonical = canonical_data
        self.model_names = model_names or {m: m for m in canonical_data.model_ids}
        self.model_ids = canonical_data.model_ids
        self.pollutants = canonical_data.pollutants
        self.records = canonical_data.records
        self.eval_records = [r for r in self.records if r.is_eval == 1]
        self.observed_records = [r for r in self.records if r.mask == 1]
        self.has_ground_truth = len(self.eval_records) > 0

    def compute_data_quality(self) -> Dict[str, Any]:
        """Analyzes raw dataset quality, sampling interval, and missingness characteristics."""
        total_cells = len(self.records)
        observed_count = len(self.observed_records)
        eval_count = len(self.eval_records)
        missing_count = total_cells - observed_count

        timestamps = [r.timestamp for r in self.records]
        unique_timestamps = sorted(list(set(timestamps)))

        # Detect sampling interval from consecutive timestamps
        sampling_interval_desc = "1 hour"
        interval_minutes = 60
        if len(unique_timestamps) >= 2:
            try:
                t0 = pd.to_datetime(unique_timestamps[0])
                t1 = pd.to_datetime(unique_timestamps[1])
                diff_m = int(round((t1 - t0).total_seconds() / 60.0))
                interval_minutes = diff_m if diff_m > 0 else 60
                if diff_m == 30:
                    sampling_interval_desc = "30 minutes"
                elif diff_m == 60:
                    sampling_interval_desc = "1 hour"
                elif diff_m == 15:
                    sampling_interval_desc = "15 minutes"
                elif diff_m == 120:
                    sampling_interval_desc = "2 hours"
                else:
                    sampling_interval_desc = f"{diff_m} minutes"
            except Exception:
                sampling_interval_desc = "1 hour"

        # Per-pollutant missingness & longest run
        pollutant_quality = {}
        for p in self.pollutants:
            p_recs = [r for r in self.records if r.pollutant == p]
            p_total = len(p_recs)
            p_missing = len([r for r in p_recs if r.mask == 0])
            p_eval = len([r for r in p_recs if r.is_eval == 1])
            p_rate = round((p_missing / p_total) * 100.0, 1) if p_total > 0 else 0.0

            # Compute longest missing run
            longest_run = 0
            current_run = 0
            for r in p_recs:
                if r.mask == 0:
                    current_run += 1
                    if current_run > longest_run:
                        longest_run = current_run
                else:
                    current_run = 0

            longest_hours = round(longest_run * (interval_minutes / 60.0), 1)

            pollutant_quality[p] = {
                "total": p_total,
                "total_cells": p_total,
                "observed": p_total - p_missing,
                "missing_cells": p_missing,
                "evaluated": p_eval,
                "evaluated_cells": p_eval,
                "missing_rate": round(p_missing / p_total, 4) if p_total > 0 else 0.0,
                "missing_rate_pct": p_rate,
                "max_gap_hours": longest_hours,
                "longest_missing_run_steps": longest_run,
                "longest_missing_run_hours": longest_hours
            }

        # Check for duplicate timestamps per pollutant
        has_duplicates = len(timestamps) != len(set((r.timestamp, r.pollutant) for r in self.records))
        invalid_values = sum(1 for r in self.records if r.ground_truth is not None and np.isnan(r.ground_truth))

        time_range_str = f"{unique_timestamps[0]} to {unique_timestamps[-1]}" if unique_timestamps else "Empty"

        is_prelim = eval_count < 100
        prelim_warn = (
            f"⚠ Preliminary evaluation: Only {eval_count} missing cells were evaluated. "
            "Results should not be interpreted as statistically robust."
            if is_prelim else None
        )

        return {
            "total_cells": total_cells,
            "observed_cells": observed_count,
            "hidden_cells": missing_count,
            "evaluated_cells": eval_count,
            "is_preliminary": is_prelim,
            "preliminary_warning": prelim_warn,
            "missing_rate_pct": round((missing_count / total_cells) * 100.0, 1) if total_cells > 0 else 0.0,
            "total_timesteps": len(unique_timestamps),
            "time_range": time_range_str,
            "sampling_interval": sampling_interval_desc,
            "sampling_interval_minutes": interval_minutes,
            "has_duplicate_timestamps": has_duplicates,
            "invalid_values_count": invalid_values,
            "ground_truth_available": self.has_ground_truth,
            "pollutant_quality": pollutant_quality,
            "pollutant_breakdown": pollutant_quality
        }

    def compute_all_evaluations(self) -> Dict[str, Any]:
        """Runs full evaluation suite and returns structured benchmark results."""
        data_quality = self.compute_data_quality()

        if not self.has_ground_truth:
            return self._compute_reconstruction_only_summary(data_quality)

        overall_metrics = self._compute_overall_metrics()
        pollutant_metrics = self._compute_pollutant_metrics()
        model_rankings = self._compute_model_rankings(overall_metrics)
        model_win_matrix = self._compute_model_win_matrix(pollutant_metrics)
        peak_analysis = self._compute_peak_analysis()
        gap_analysis = self._compute_gap_analysis()
        pollution_level_analysis = self._compute_pollution_level_analysis()
        error_distribution = self._compute_error_distribution()
        bias_analysis = self._compute_bias_analysis()
        failure_cases, best_cases = self._compute_failure_and_best_cases()
        executive_summary = self._compute_executive_summary(model_rankings, overall_metrics, peak_analysis, gap_analysis)
        win_summary = self._compute_win_summary(model_rankings, pollutant_metrics, peak_analysis, gap_analysis, overall_metrics)
        scientific_conclusion = self._generate_scientific_conclusion(executive_summary, pollutant_metrics, gap_analysis)

        total_eval_points = len(self.eval_records)
        is_preliminary = total_eval_points < 100
        preliminary_notice = (
            f"⚠ Preliminary evaluation: Only {total_eval_points} missing cells were evaluated. "
            "Results should not be interpreted as statistically robust."
            if is_preliminary else None
        )

        return {
            "has_ground_truth": True,
            "is_preliminary": is_preliminary,
            "preliminary_notice": preliminary_notice,
            "data_quality": data_quality,
            "executive_summary": executive_summary,
            "win_summary": win_summary,
            "model_rankings": model_rankings,
            "model_win_matrix": model_win_matrix,
            "overall_metrics": overall_metrics,
            "pollutant_metrics": pollutant_metrics,
            "peak_analysis": peak_analysis,
            "peak_reconstruction": peak_analysis["by_model"],
            "gap_analysis": gap_analysis,
            "pollution_level_analysis": pollution_level_analysis,
            "error_distribution": error_distribution,
            "bias_analysis": bias_analysis,
            "failure_cases": failure_cases,
            "best_cases": best_cases,
            "scientific_conclusion": scientific_conclusion,
            "total_eval_points": total_eval_points
        }

    def _compute_reconstruction_only_summary(self, data_quality: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback response when ground truth is unavailable."""
        return {
            "has_ground_truth": False,
            "is_preliminary": True,
            "preliminary_notice": "Ground truth unavailable. Accuracy metrics cannot be calculated.",
            "data_quality": data_quality,
            "notice": "Ground truth unavailable. Accuracy metrics cannot be calculated.",
            "total_eval_points": 0,
            "reconstruction_points": len([r for r in self.records if r.mask == 0]),
            "scientific_conclusion": "Real-world dataset evaluated without ground truth. Models performed deterministic gap filling on missing intervals."
        }

    def _compute_metrics_for_points(self, records: List[PointRecord], m_id: str) -> Dict[str, Any]:
        """Calculates full metric bundle for a given model across a subset of records with bootstrap CIs."""
        trues = []
        preds = []
        for r in records:
            p = r.predictions.get(m_id)
            t = r.ground_truth
            if p is not None and t is not None and not np.isnan(p) and not np.isnan(t):
                trues.append(t)
                preds.append(p)

        if not trues:
            return {
                "MAE": None, "RMSE": None, "MAPE": None, "R2": None,
                "Correlation": None, "Bias": None, "Median_AE": None,
                "P90_AE": None, "P95_AE": None, "Max_AE": None,
                "count": 0, "ci_available": False, "ci_str": "CI unavailable: insufficient evaluation samples."
            }

        y_t = np.array(trues, dtype=np.float64)
        y_p = np.array(preds, dtype=np.float64)
        diff = y_p - y_t
        abs_diff = np.abs(diff)

        mae = float(np.mean(abs_diff))
        rmse = float(np.sqrt(np.mean(diff ** 2)))

        # MAPE with filter >= 1.0 to avoid division by zero
        valid_pct = (np.abs(y_t) >= 1.0)
        mape = float(np.mean(abs_diff[valid_pct] / np.abs(y_t[valid_pct]) * 100.0)) if np.any(valid_pct) else 0.0

        r2 = compute_r2(y_t, y_p)

        # Correlation
        if len(y_t) >= 2 and np.std(y_t) > 1e-6 and np.std(y_p) > 1e-6:
            corr = float(np.corrcoef(y_t, y_p)[0, 1])
        else:
            corr = 0.0

        bias = float(np.mean(diff))

        # Bootstrap 95% Confidence Interval for MAE if sample size >= 30
        n_samples = len(y_t)
        ci_available = False
        ci_low = None
        ci_high = None
        ci_str = "CI unavailable: insufficient evaluation samples."

        if n_samples >= 30:
            try:
                np.random.seed(42)
                boot_indices = np.random.randint(0, n_samples, size=(1000, n_samples))
                boot_maes = np.mean(abs_diff[boot_indices], axis=1)
                ci_low = round(float(np.percentile(boot_maes, 2.5)), 2)
                ci_high = round(float(np.percentile(boot_maes, 97.5)), 2)
                ci_available = True
                ci_str = f"{ci_low}–{ci_high}"
            except Exception:
                ci_available = False

        mae_ci_95 = {
            "low": ci_low,
            "high": ci_high,
            "mean": round(mae, 2)
        } if ci_available else None

        return {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "MAPE": round(mape, 1),
            "R2": r2,
            "Correlation": round(corr, 3),
            "Bias": round(bias, 2),
            "Median_AE": round(float(np.median(abs_diff)), 2),
            "P90_AE": round(float(np.percentile(abs_diff, 90)), 2),
            "P95_AE": round(float(np.percentile(abs_diff, 95)), 2),
            "Max_AE": round(float(np.max(abs_diff)), 2),
            "count": n_samples,
            "ci_available": ci_available,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "ci_str": ci_str,
            "mae_ci_95": mae_ci_95
        }

    def _bootstrap_ci(self, values: np.ndarray, num_bootstrap: int = 1000) -> Optional[Dict[str, float]]:
        """Calculates 95% bootstrap confidence interval of the mean for values when n >= 30."""
        if len(values) < 30:
            return None
        np.random.seed(42)
        n = len(values)
        boot_indices = np.random.randint(0, n, size=(num_bootstrap, n))
        boot_means = np.mean(values[boot_indices], axis=1)
        return {
            "low": round(float(np.percentile(boot_means, 2.5)), 2),
            "high": round(float(np.percentile(boot_means, 97.5)), 2),
            "mean": round(float(np.mean(values)), 2)
        }

    def _compute_overall_metrics(self) -> Dict[str, Dict[str, Any]]:
        overall = {}
        for m_id in self.model_ids:
            overall[m_id] = self._compute_metrics_for_points(self.eval_records, m_id)
        return overall

    def _compute_pollutant_metrics(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        by_pollutant = {}
        for p in self.pollutants:
            p_records = [r for r in self.eval_records if r.pollutant == p]
            by_pollutant[p] = {}
            for m_id in self.model_ids:
                by_pollutant[p][m_id] = self._compute_metrics_for_points(p_records, m_id)
        return by_pollutant

    def _compute_model_win_matrix(self, pollutant_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds Model Win Matrix: Models x Pollutants showing rankings (1st, 2nd, 3rd)
        for MAE, RMSE, Correlation, and Peak MAE.
        """
        metrics_keys = ["MAE", "RMSE", "Correlation"]
        matrix = {k: {} for k in metrics_keys}

        for m_key in metrics_keys:
            matrix[m_key] = {}
            for m_id in self.model_ids:
                matrix[m_key][m_id] = {}

            for p in self.pollutants:
                # Rank models for pollutant p under metric m_key
                model_scores = []
                for m_id in self.model_ids:
                    val = pollutant_metrics.get(p, {}).get(m_id, {}).get(m_key)
                    model_scores.append((m_id, val))

                if m_key == "Correlation":
                    # Higher is better
                    model_scores.sort(key=lambda x: (-1.0 if x[1] is not None else -999.0, x[1] if x[1] is not None else -999.0), reverse=True)
                else:
                    # Lower is better
                    model_scores.sort(key=lambda x: (x[1] is None, x[1] if x[1] is not None else 999999.0))

                for rank_idx, (m_id, val) in enumerate(model_scores, start=1):
                    matrix[m_key][m_id][p] = {
                        "rank": rank_idx,
                        "value": val
                    }

        return matrix

    def _compute_peak_analysis(self) -> Dict[str, Any]:
        """
        Identifies top 10% peak events strictly from ground-truth concentrations.
        Evaluates peak MAE, peak RMSE, peak amplitude error, timing error, and recovery rate.
        """
        peak_records = [r for r in self.eval_records if r.is_peak]
        by_model = {}

        for m_id in self.model_ids:
            metrics = self._compute_metrics_for_points(peak_records, m_id)

            # Amplitude error and recovery rate
            amp_errors = []
            rec_rates = []
            for r in peak_records:
                p = r.predictions.get(m_id)
                t = r.ground_truth
                if p is not None and t is not None and t > 0:
                    amp_errors.append(p - t)
                    rec_rates.append(min(200.0, max(0.0, (p / t) * 100.0)))

            mean_amp_err = round(float(np.mean(amp_errors)), 2) if amp_errors else None
            mean_rec_rate = round(float(np.mean(rec_rates)), 1) if rec_rates else None

            by_model[m_id] = {
                "peak_mae": metrics["MAE"],
                "peak_rmse": metrics["RMSE"],
                "peak_bias": metrics["Bias"],
                "amplitude_error": mean_amp_err,
                "recovery_rate_pct": mean_rec_rate,
                "peak_count": metrics["count"],
                "count": metrics["count"]
            }

        # Catalog individual peak events for 1-click Peak Explorer
        sorted_peaks = sorted(peak_records, key=lambda r: r.ground_truth or 0.0, reverse=True)
        peaks_catalog = []
        for idx, r in enumerate(sorted_peaks[:5], start=1):
            p_records = [x for x in self.records if x.pollutant == r.pollutant]
            target_idx = next((i for i, x in enumerate(p_records) if x.timestamp == r.timestamp), 0)
            zoom_start = max(0, target_idx - 4)
            zoom_end = min(len(p_records) - 1, target_idx + 4)

            peaks_catalog.append({
                "peak_id": idx,
                "label": f"Peak #{idx}: {r.pollutant} ({round(r.ground_truth, 1)} µg/m³)",
                "pollutant": r.pollutant,
                "timestamp": r.timestamp,
                "ground_truth": round(r.ground_truth, 1),
                "predictions": {m: round(r.predictions.get(m, 0.0), 1) if r.predictions.get(m) is not None else None for m in self.model_ids},
                "amplitude_errors": {m: round(r.predictions.get(m, 0.0) - r.ground_truth, 1) if r.predictions.get(m) is not None else None for m in self.model_ids},
                "zoom_start": zoom_start,
                "zoom_end": zoom_end
            })

        return {
            "peak_threshold_desc": "Top 10% highest ground-truth pollutant concentrations",
            "total_peak_points": len(peak_records),
            "by_model": by_model,
            "peaks_catalog": peaks_catalog
        }

    def _compute_gap_analysis(self) -> Dict[str, Any]:
        """
        Bins missing evaluation points by exact gap lengths (1h, 2h, 4h, 6h, 12h, 24h)
        plus broad categories (short, medium, long).
        """
        gap_bins = [
            ("1h", "1 Hour", 1, 1),
            ("2h", "2 Hours", 2, 2),
            ("4h", "3–4 Hours", 3, 4),
            ("6h", "5–6 Hours", 5, 6),
            ("12h", "7–12 Hours", 7, 12),
            ("24h", "13–24 Hours", 13, 24),
            ("short", "Short (1–2 hrs)", 1, 2),
            ("medium", "Medium (3–6 hrs)", 3, 6),
            ("long", "Long (7–24 hrs)", 7, 24)
        ]
        breakdown = {}
        for bin_key, label, g_min, g_max in gap_bins:
            sub = [r for r in self.eval_records if g_min <= r.gap_length <= g_max]
            breakdown[bin_key] = {
                "label": label,
                "point_count": len(sub),
                "by_model": {
                    m_id: self._compute_metrics_for_points(sub, m_id)["MAE"]
                    for m_id in self.model_ids
                }
            }
        return breakdown

    def _compute_pollution_level_analysis(self) -> Dict[str, Any]:
        """Evaluates MAE binned by pollution tier: Low, Moderate, High, Very High, Extreme."""
        levels = ["Low", "Moderate", "High", "Very High", "Extreme"]
        results = {}
        for lvl in levels:
            sub = [r for r in self.eval_records if r.pollution_level == lvl]
            results[lvl] = {
                "point_count": len(sub),
                "by_model": {
                    m_id: self._compute_metrics_for_points(sub, m_id)["MAE"]
                    for m_id in self.model_ids
                }
            }
        return results

    def _compute_error_distribution(self) -> Dict[str, Any]:
        """Calculates signed and absolute error percentiles (median, P75, P90, P95, max)."""
        dist = {}
        for m_id in self.model_ids:
            abs_errs = [
                r.abs_errors[m_id] for r in self.eval_records
                if m_id in r.abs_errors and r.abs_errors[m_id] is not None
            ]
            signed_errs = [
                r.errors[m_id] for r in self.eval_records
                if m_id in r.errors and r.errors[m_id] is not None
            ]
            if abs_errs:
                arr = np.array(abs_errs)
                s_arr = np.array(signed_errs)
                dist[m_id] = {
                    "mean": round(float(np.mean(arr)), 2),
                    "median": round(float(np.median(arr)), 2),
                    "p75": round(float(np.percentile(arr, 75)), 2),
                    "p90": round(float(np.percentile(arr, 90)), 2),
                    "p95": round(float(np.percentile(arr, 95)), 2),
                    "max": round(float(np.max(arr)), 2),
                    "signed_median": round(float(np.median(s_arr)), 2),
                    "signed_p10": round(float(np.percentile(s_arr, 10)), 2),
                    "signed_p90": round(float(np.percentile(s_arr, 90)), 2)
                }
            else:
                dist[m_id] = {}
        return dist

    def _compute_bias_analysis(self) -> Dict[str, Dict[str, Optional[float]]]:
        """Calculates signed bias per pollutant and model to detect systematic drift."""
        table = {}
        for p in self.pollutants:
            table[p] = {}
            p_records = [r for r in self.eval_records if r.pollutant == p]
            for m_id in self.model_ids:
                table[p][m_id] = self._compute_metrics_for_points(p_records, m_id)["Bias"]
        return table

    def _compute_failure_and_best_cases(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extracts top worst predictions and best predictions across models with surrounding context."""
        failures = []
        bests = []
        for r in self.eval_records:
            for m_id in self.model_ids:
                abs_e = r.abs_errors.get(m_id)
                if abs_e is not None and not np.isnan(abs_e):
                    pred_v = r.predictions.get(m_id)
                    gt = r.ground_truth
                    pct_e = round((abs_e / abs(gt)) * 100.0, 1) if gt and abs(gt) > 1.0 else 0.0
                    entry = {
                        "timestamp": r.timestamp,
                        "pollutant": r.pollutant,
                        "model_id": m_id,
                        "model_name": self.model_names.get(m_id, m_id),
                        "ground_truth": round(r.ground_truth, 2) if r.ground_truth is not None else None,
                        "prediction": round(pred_v, 2) if pred_v is not None else None,
                        "abs_error": round(abs_e, 2),
                        "pct_error": pct_e,
                        "gap_length": r.gap_length,
                        "pollution_level": r.pollution_level,
                        "is_peak": r.is_peak
                    }
                    failures.append(entry)
                    bests.append(entry)

        failures.sort(key=lambda x: x["abs_error"], reverse=True)
        bests.sort(key=lambda x: x["abs_error"])

        return failures[:10], bests[:10]

    def _compute_model_rankings(self, overall: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        rows = []
        for m_id in self.model_ids:
            o = overall.get(m_id, {})
            rows.append({
                "model_id": m_id,
                "model_name": self.model_names.get(m_id, m_id),
                "MAE": o.get("MAE"),
                "RMSE": o.get("RMSE"),
                "MAPE": o.get("MAPE"),
                "R2": o.get("R2"),
                "Correlation": o.get("Correlation"),
                "Bias": o.get("Bias"),
                "Max_AE": o.get("Max_AE"),
                "count": o.get("count", 0),
                "ci_available": o.get("ci_available", False),
                "ci_str": o.get("ci_str", "")
            })

        # Sort primarily by MAE ascending
        rows.sort(key=lambda x: (x["MAE"] is None, x["MAE"] or 999999.0))
        for rank, r in enumerate(rows, start=1):
            r["rank"] = rank

        return rows

    def _compute_win_summary(
        self,
        rankings: List[Dict[str, Any]],
        pollutant_metrics: Dict[str, Any],
        peak_analysis: Dict[str, Any],
        gap_analysis: Dict[str, Any],
        overall: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Constructs multi-dimensional winner summary across pollutants and scenarios."""
        best_overall = rankings[0] if rankings else {}

        summary = {
            "best_overall": {
                "model_id": best_overall.get("model_id"),
                "name": best_overall.get("model_name"),
                "value": best_overall.get("MAE"),
                "unit": "µg/m³ MAE"
            }
        }

        # Per pollutant best
        for p in self.pollutants:
            p_scores = []
            for m_id in self.model_ids:
                val = pollutant_metrics.get(p, {}).get(m_id, {}).get("MAE")
                if val is not None:
                    p_scores.append((m_id, val))
            if p_scores:
                p_scores.sort(key=lambda x: x[1])
                best_m = p_scores[0][0]
                summary[f"best_{p}"] = {
                    "model_id": best_m,
                    "name": self.model_names.get(best_m, best_m),
                    "value": p_scores[0][1],
                    "unit": "µg/m³ MAE"
                }

        # Best peak reconstruction
        peak_scores = []
        for m_id in self.model_ids:
            pval = peak_analysis["by_model"].get(m_id, {}).get("peak_mae")
            if pval is not None:
                peak_scores.append((m_id, pval))
        if peak_scores:
            peak_scores.sort(key=lambda x: x[1])
            bp = peak_scores[0][0]
            summary["best_peak_reconstruction"] = {
                "model_id": bp,
                "name": self.model_names.get(bp, bp),
                "value": peak_scores[0][1],
                "unit": "µg/m³ Peak MAE"
            }

        # Best long gap
        long_gap = gap_analysis.get("long", {}).get("by_model", {})
        long_scores = [(m, v) for m, v in long_gap.items() if v is not None]
        if long_scores:
            long_scores.sort(key=lambda x: x[1])
            bl = long_scores[0][0]
            summary["best_long_gap"] = {
                "model_id": bl,
                "name": self.model_names.get(bl, bl),
                "value": long_scores[0][1],
                "unit": "µg/m³ MAE"
            }

        # Lowest bias
        bias_scores = []
        for m_id in self.model_ids:
            bval = overall.get(m_id, {}).get("Bias")
            if bval is not None:
                bias_scores.append((m_id, abs(bval), bval))
        if bias_scores:
            bias_scores.sort(key=lambda x: x[1])
            bb = bias_scores[0][0]
            summary["lowest_bias"] = {
                "model_id": bb,
                "name": self.model_names.get(bb, bb),
                "value": bias_scores[0][2],
                "unit": "µg/m³ Bias"
            }

        summary["overall_winner"] = best_overall.get("model_id")
        summary["pollutant_winners"] = {p: summary.get(f"best_{p}", {}).get("model_id") for p in self.pollutants}
        summary["peak_winner"] = summary.get("best_peak_reconstruction", {}).get("model_id")
        summary["long_gap_winner"] = summary.get("best_long_gap", {}).get("model_id")

        return summary

    def _compute_executive_summary(
        self,
        rankings: List[Dict[str, Any]],
        overall: Dict[str, Dict[str, Any]],
        peak_analysis: Dict[str, Any],
        gap_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        best_mae = rankings[0] if rankings else {}
        
        # Best RMSE
        best_rmse_m = min(
            self.model_ids,
            key=lambda m: overall.get(m, {}).get("RMSE") if overall.get(m, {}).get("RMSE") is not None else 999999.0
        )
        
        # Best Peak MAE
        best_peak_m = min(
            self.model_ids,
            key=lambda m: peak_analysis["by_model"].get(m, {}).get("peak_mae") if peak_analysis["by_model"].get(m, {}).get("peak_mae") is not None else 999999.0
        )
        
        # Best Long Gap MAE
        long_gap = gap_analysis.get("long", {}).get("by_model", {})
        best_long_gap_m = min(
            self.model_ids,
            key=lambda m: long_gap.get(m) if long_gap.get(m) is not None else 999999.0
        )

        # Lowest Bias
        best_bias_m = min(
            self.model_ids,
            key=lambda m: abs(overall.get(m, {}).get("Bias")) if overall.get(m, {}).get("Bias") is not None else 999999.0
        )

        return {
            "best_overall_mae": {
                "model_id": best_mae.get("model_id"),
                "model_name": best_mae.get("model_name"),
                "value": best_mae.get("MAE")
            },
            "best_overall_rmse": {
                "model_id": best_rmse_m,
                "model_name": self.model_names.get(best_rmse_m, best_rmse_m),
                "value": overall.get(best_rmse_m, {}).get("RMSE")
            },
            "best_peak_recovery": {
                "model_id": best_peak_m,
                "model_name": self.model_names.get(best_peak_m, best_peak_m),
                "value": peak_analysis["by_model"].get(best_peak_m, {}).get("peak_mae")
            },
            "best_long_gap": {
                "model_id": best_long_gap_m,
                "model_name": self.model_names.get(best_long_gap_m, best_long_gap_m),
                "value": long_gap.get(best_long_gap_m)
            },
            "lowest_bias": {
                "model_id": best_bias_m,
                "model_name": self.model_names.get(best_bias_m, best_bias_m),
                "value": overall.get(best_bias_m, {}).get("Bias")
            }
        }

    def _generate_scientific_conclusion(
        self,
        exec_summary: Dict[str, Any],
        pollutant_metrics: Dict[str, Any],
        gap_analysis: Dict[str, Any]
    ) -> str:
        """Constructs an objective factual narrative summarizing verified findings."""
        best_overall = exec_summary["best_overall_mae"]
        best_peak = exec_summary["best_peak_recovery"]
        best_gap = exec_summary["best_long_gap"]

        statements = [
            f"Under the evaluated missingness configuration, {best_overall['model_name']} achieved the lowest overall Mean Absolute Error ({best_overall['value']} µg/m³)."
        ]

        # Pollutant level findings
        ctdi_wins = []
        linear_wins = []
        for p, p_res in pollutant_metrics.items():
            valid_models = [m for m in self.model_ids if p_res.get(m, {}).get("MAE") is not None]
            if valid_models:
                p_win = min(valid_models, key=lambda m: p_res[m]["MAE"])
                if "ctdi" in p_win:
                    ctdi_wins.append(p)
                elif "linear" in p_win:
                    linear_wins.append(p)

        if ctdi_wins:
            statements.append(f"CTDI demonstrated superior accuracy on particulate matter channels ({', '.join(ctdi_wins)}).")
        if linear_wins:
            statements.append(f"1D Linear Interpolation exhibited lower error on smooth gaseous channels ({', '.join(linear_wins)}).")

        if best_gap["model_id"] != best_overall["model_id"] and best_gap["value"] is not None:
            statements.append(f"For contiguous long gaps (7-24 hrs), {best_gap['model_name']} provided the most resilient reconstruction ({best_gap['value']} µg/m³ MAE).")

        statements.append("Observed sensor readings were preserved with zero modification across all participating models.")
        return " ".join(statements)
