"""Evaluation metrics specification for reconstructed air quality tensors.

Implements standard benchmark metrics (MAE, RMSE, MRE, CRPS, temporal smoothness)
for evaluating conditional diffusion model imputation against test benchmark masks.
"""


def compute_imputation_metrics(*args, **kwargs):
    """Compute imputation metrics across evaluated pollutant channels."""
    raise NotImplementedError("Evaluation metrics will be executed in Phase 4C/5 after model inference.")
