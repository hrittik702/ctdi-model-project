"""Environmental Context Builder orchestrator.

Transforms 24-hour multi-channel window tensors, observation masks, and window metadata
into structured environmental contexts and deterministic text prompts for SLM encoding.

Strictly enforces information leakage boundaries:
- Meteorological and traffic channels are exogenous.
- Missingness pattern is derived strictly from effective observation masks.
- Target pollutant values hidden during experimental evaluation (X_hidden) are NEVER
  passed to prompt generation or SLM feature extractors.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from src.context.context_features import (
    CHANNEL_NAMES,
    extract_window_features,
)
from src.context.context_serializer import serialize_context


DEFAULT_STATION_META_PATH = Path(__file__).parents[2] / "data" / "raw" / "station_metadata" / "air_quality_stations.csv"


def window_row_to_numpy(row: Union[pd.Series, Dict[str, Any]]) -> np.ndarray:
    """Convert a row containing channel list columns into a (24, 13) numpy array."""
    cols = [row[ch] for ch in CHANNEL_NAMES]
    return np.column_stack(cols).astype(np.float64)


def mask_row_to_numpy(row: Union[pd.Series, Dict[str, Any]]) -> np.ndarray:
    """Convert a mask row containing channel list columns into a (24, 13) binary numpy array."""
    cols = [row[ch] for ch in CHANNEL_NAMES]
    return np.column_stack(cols).astype(np.int64)


class EnvironmentalContextBuilder:
    """Deterministic builder of rich environmental context representations."""

    def __init__(
        self,
        station_metadata_path: Optional[Union[str, Path]] = None,
        default_format: str = "narrative",
        include_observed_aq: bool = False,
    ):
        """Initialize the context builder.
        
        Args:
            station_metadata_path: Path to air_quality_stations.csv. If None, uses default.
            default_format: Default serialization format ('narrative', 'key_value', 'json').
            include_observed_aq: Whether to include observed pollutant statistics.
                Defaults to False for strict leakage protection.
        """
        self.default_format = default_format
        self.include_observed_aq = include_observed_aq
        self.station_info: Dict[int, Dict[str, Any]] = {}
        
        meta_path = Path(station_metadata_path) if station_metadata_path else DEFAULT_STATION_META_PATH
        if meta_path.exists():
            df_st = pd.read_csv(meta_path)
            for _, row in df_st.iterrows():
                st_id = int(row["station_id"])
                self.station_info[st_id] = {
                    "station_name": str(row.get("display_name", row.get("station_name", ""))),
                    "station_code": str(row.get("station_code", "")),
                    "station_type": str(row.get("station_type", "General")),
                    "latitude": float(row.get("latitude", 0.0)),
                    "longitude": float(row.get("longitude", 0.0)),
                    "sampling_height_m": float(row.get("sampling_height_m", 0.0)) if pd.notnull(row.get("sampling_height_m")) else 15.0,
                    "district": str(row.get("district", "Hong Kong")),
                }

    def _enrich_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich window metadata dictionary with station catalog properties."""
        enriched = dict(metadata)
        st_id = int(enriched.get("station_id", 0))
        if st_id in self.station_info:
            info = self.station_info[st_id]
            if "station_name" not in enriched or not enriched["station_name"]:
                enriched["station_name"] = info["station_name"]
            if "station_type" not in enriched:
                enriched["station_type"] = info["station_type"]
            if "district" not in enriched:
                enriched["district"] = info["district"]
            enriched["latitude"] = info["latitude"]
            enriched["longitude"] = info["longitude"]
            enriched["sampling_height_m"] = info["sampling_height_m"]
        return enriched

    def _ensure_numpy_24x13(self, data: Union[np.ndarray, pd.Series, Dict[str, Any]], is_mask: bool = False) -> np.ndarray:
        """Convert input data to (24, 13) numpy array if needed."""
        if isinstance(data, np.ndarray):
            if data.shape == (24, 13):
                return data
            elif data.size == 24 * 13:
                return data.reshape(24, 13)
            raise ValueError(f"Expected array shape (24, 13) or size 312, got shape {data.shape}")
        elif isinstance(data, (pd.Series, dict)):
            if is_mask:
                return mask_row_to_numpy(data)
            return window_row_to_numpy(data)
        else:
            raise TypeError(f"Unsupported data type for window conversion: {type(data)}")

    def build_context(
        self,
        window_data: Union[np.ndarray, pd.Series, Dict[str, Any]],
        mask_data: Union[np.ndarray, pd.Series, Dict[str, Any]],
        metadata: Dict[str, Any],
        eval_mask: Optional[Union[np.ndarray, pd.Series, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Build structured context dictionary for a single window.
        
        Args:
            window_data: Array of shape (24, 13) or Series/dict with channel columns.
            mask_data: Array of shape (24, 13) or Series/dict with natural observation mask.
            metadata: Window metadata dictionary.
            eval_mask: Optional simulated missingness mask.
            
        Returns:
            Structured context dictionary.
        """
        w_arr = self._ensure_numpy_24x13(window_data, is_mask=False)
        m_arr = self._ensure_numpy_24x13(mask_data, is_mask=True)
        em_arr = self._ensure_numpy_24x13(eval_mask, is_mask=True) if eval_mask is not None else None

        enriched_meta = self._enrich_metadata(metadata)
        return extract_window_features(
            window_data=w_arr,
            mask_data=m_arr,
            metadata=enriched_meta,
            eval_mask=em_arr,
        )

    def build_prompt(
        self,
        window_data: Union[np.ndarray, pd.Series, Dict[str, Any]],
        mask_data: Union[np.ndarray, pd.Series, Dict[str, Any]],
        metadata: Dict[str, Any],
        eval_mask: Optional[Union[np.ndarray, pd.Series, Dict[str, Any]]] = None,
        format_type: Optional[str] = None,
    ) -> str:
        """Build serialized text prompt for a single window.
        
        Args:
            window_data: Array of shape (24, 13) or Series/dict.
            mask_data: Array of shape (24, 13) or Series/dict.
            metadata: Window metadata dictionary.
            eval_mask: Optional simulated missingness mask.
            format_type: Override default serialization format ('narrative', 'key_value', 'json').
            
        Returns:
            Serialized string prompt for SLM encoder.
        """
        fmt = format_type if format_type is not None else self.default_format
        context = self.build_context(window_data, mask_data, metadata, eval_mask=eval_mask)
        return serialize_context(
            context,
            format_type=fmt,
            include_observed_aq=self.include_observed_aq,
        )

    def build_batch_prompts(
        self,
        windows: Union[np.ndarray, List[Any]],
        masks: Union[np.ndarray, List[Any]],
        metadatas: List[Dict[str, Any]],
        eval_masks: Optional[Union[np.ndarray, List[Any]]] = None,
        format_type: Optional[str] = None,
    ) -> List[str]:
        """Build a batch of serialized text prompts.
        
        Args:
            windows: Array of shape (B, 24, 13) or list of windows.
            masks: Array of shape (B, 24, 13) or list of masks.
            metadatas: List of B metadata dictionaries.
            eval_masks: Optional array or list of simulated masks.
            format_type: Serialization format.
            
        Returns:
            List of B serialized prompt strings.
        """
        b = len(metadatas)
        prompts = []
        for i in range(b):
            w = windows[i]
            m = masks[i]
            meta = metadatas[i]
            em = eval_masks[i] if eval_masks is not None else None
            p = self.build_prompt(w, m, meta, eval_mask=em, format_type=format_type)
            prompts.append(p)
        return prompts

    @staticmethod
    def audit_leakage(
        window_data: np.ndarray,
        eval_mask: np.ndarray,
        prompt: str,
        pollutant_indices: List[int] = (0, 1, 2, 3, 4),
    ) -> bool:
        """Audit whether any hidden numerical pollutant values leaked into the prompt.
        
        Args:
            window_data: Array of shape (24, 13).
            eval_mask: Binary mask where 0 = artificially hidden ground truth.
            prompt: Generated prompt string.
            pollutant_indices: Indices of pollutant channels.
            
        Returns:
            True if audit passes (no leakage detected).
            Raises AssertionError if hidden value is discovered in prompt text.
        """
        for p_idx in pollutant_indices:
            hidden_hours = np.where(eval_mask[:, p_idx] == 0)[0]
            for h in hidden_hours:
                hidden_val = window_data[h, p_idx]
                if not np.isnan(hidden_val):
                    val_str = f"{hidden_val:.2f}"
                    if val_str in prompt:
                        raise AssertionError(
                            f"LEAKAGE DETECTED: Hidden ground truth pollutant value {val_str} "
                            f"(channel {p_idx}, hour {h}) found in context prompt!"
                        )
        return True


def build_environmental_context(
    window_data: Union[np.ndarray, pd.Series, Dict[str, Any]],
    mask_data: Union[np.ndarray, pd.Series, Dict[str, Any]],
    metadata: Dict[str, Any],
    eval_mask: Optional[Union[np.ndarray, pd.Series, Dict[str, Any]]] = None,
    format_type: str = "narrative",
) -> str:
    """Convenience function matching legacy interface."""
    builder = EnvironmentalContextBuilder(default_format=format_type)
    return builder.build_prompt(window_data, mask_data, metadata, eval_mask=eval_mask)
