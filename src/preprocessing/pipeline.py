"""Historical preprocessing orchestrator placeholder.

Note: Data preprocessing was executed via individual validated pipeline modules:
- clean_air_quality.py / clean_meteorology.py / clean_traffic.py (Phase 1)
- traffic_hourly_aggregation.py / traffic_spatial_mapping.py (Phase 1.2)
- temporal_alignment.py / build_aligned_dataset.py (Phase 2)
- build_windows.py (Phase 3)
"""


def run_preprocessing_pipeline(*args, **kwargs):
    """Run preprocessing pipeline. Refer to individual stage scripts in src/preprocessing/."""
    raise NotImplementedError(
        "Preprocessing pipeline steps are implemented as individual validated modules "
        "in src/preprocessing/ (e.g. clean_air_quality.py, build_aligned_dataset.py)."
    )
