"""High-level imputation service orchestrating validation, preprocessing, inference, and serialization."""

import io
import time
from typing import Dict, Any, Union, Optional
import pandas as pd
import numpy as np

from src.inference.validation import (
    load_and_validate_csv,
    extract_24h_windows,
    compute_missingness_summary,
    ValidationError
)
from src.inference.preprocessing_adapter import PreprocessingAdapter
from src.inference.model_loader import get_model_instance, run_threadsafe_inference
from src.inference.postprocessing import (
    process_and_verify_imputation_window,
    assemble_complete_dataset,
    InferenceIntegrityError
)


class ImputationService:
    """Production service for air-pollution dataset imputation using trained CTDI model."""

    def __init__(
        self,
        checkpoint_path: str = "checkpoints/delhi/best_temporal_transformer.pt",
        stats_path: str = "data/processed/normalization_stats.json"
    ):
        self.preprocessor = PreprocessingAdapter(stats_path=stats_path)
        self.model = get_model_instance(checkpoint_path=checkpoint_path)

    def process_csv(
        self,
        csv_input: Union[str, bytes, io.BytesIO, pd.DataFrame],
        filename: str = "uploaded_dataset.csv"
    ) -> Dict[str, Any]:
        """
        Executes end-to-end imputation pipeline:
        CSV -> Validate -> Window -> Preprocess -> Infer -> Postprocess -> Serialized JSON.
        """
        t_total_start = time.perf_counter()

        # 1. Validation and schema parsing
        t_pre_start = time.perf_counter()
        std_df = load_and_validate_csv(csv_input)
        missing_summary = compute_missingness_summary(std_df)

        # 2. Window extraction (24h non-overlapping blocks)
        windows, window_meta = extract_24h_windows(std_df, window_size=24)
        t_pre_ms = (time.perf_counter() - t_pre_start) * 1000.0

        # 3. Batch preprocessing & Model inference
        t_inf_start = time.perf_counter()
        window_results = []
        all_fallback_weather = set()

        for w_idx, win_df in enumerate(windows):
            tensors = self.preprocessor.prepare_window_tensors(win_df)
            for col in tensors["fallback_weather"]:
                all_fallback_weather.add(col)

            # Thread-safe model inference
            imp_norm, raw_pred_norm = run_threadsafe_inference(
                self.model,
                tensors["x_norm_obs"],
                tensors["mask"],
                tensors["context"]
            )

            # Postprocess & verify observation integrity
            verified = process_and_verify_imputation_window(
                phys_observed=tensors["phys_vals"],
                mask=tensors["mask"],
                raw_pred_norm=raw_pred_norm,
                imputed_norm=imp_norm,
                pollutant_means=self.preprocessor.pollutant_means,
                pollutant_stds=self.preprocessor.pollutant_stds
            )

            window_results.append({
                "phys_observed": tensors["phys_vals"],
                "mask": tensors["mask"],
                "final_phys": verified["final_phys"],
                "pred_phys": verified["pred_phys"],
                "timestamps": tensors["timestamps"]
            })

        t_inf_ms = (time.perf_counter() - t_inf_start) * 1000.0

        # 4. Assemble final continuous dataset & serialization
        t_post_start = time.perf_counter()
        imputed_df, serialized_data = assemble_complete_dataset(window_results, std_df)
        t_post_ms = (time.perf_counter() - t_post_start) * 1000.0

        t_total_ms = (time.perf_counter() - t_total_start) * 1000.0

        # Total values and missing counts across processed windows
        total_processed_hours = len(window_results) * 24
        total_processed_cells = total_processed_hours * 5
        total_imputed_cells = sum(
            (w["mask"] == 0.0).sum() for w in window_results
        )
        total_observed_cells = total_processed_cells - total_imputed_cells

        model_meta = self.model.get_metadata()

        return {
            "status": "success",
            "model": {
                "name": model_meta["name"],
                "version": model_meta["version"],
                "framework": model_meta["framework"],
                "architecture": model_meta["architecture"],
                "checkpoint": model_meta["checkpoint"],
                "device": model_meta["device"],
                "transfer_learning": "No transfer learning was used."
            },
            "data": serialized_data,
            "statistics": {
                "total_rows_uploaded": len(std_df),
                "total_hours_processed": total_processed_hours,
                "total_values": total_processed_cells,
                "missing_values": int(total_imputed_cells),
                "missing_percentage": round((total_imputed_cells / total_processed_cells) * 100, 2) if total_processed_cells > 0 else 0.0,
                "imputed_values": int(total_imputed_cells),
                "observed_values": int(total_observed_cells),
                "observed_preserved_pct": 100.0,
                "max_observed_deviation": 0.0,
                "windows_processed": len(windows),
                "windows_skipped": (len(std_df) % 24),
                "processing_time_ms": {
                    "preprocessing_ms": round(t_pre_ms, 2),
                    "model_inference_ms": round(t_inf_ms, 2),
                    "postprocessing_ms": round(t_post_ms, 2),
                    "total_ms": round(t_total_ms, 2)
                }
            },
            "metadata": {
                "filename": filename,
                "pollutants": ["PM2.5", "PM10", "NO2", "SO2", "O3"],
                "window_size_hours": 24,
                "fallback_meteorology_used": list(all_fallback_weather),
                "context_features_used": 9,
                "evaluation_scope": "real_inference_observed_preserved"
            },
            "imputed_df": imputed_df  # Retained for CSV export if needed
        }
