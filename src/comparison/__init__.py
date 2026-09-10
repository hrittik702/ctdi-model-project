"""CTDI Model Comparison & Benchmarking Lab Package."""

from src.comparison.registry import ModelRegistry, BaseModelRunner, get_default_registry
from src.comparison.evaluation_engine import EvaluationEngine
from src.comparison.experiment_controller import ExperimentController
from src.comparison.canonical_data import CanonicalPredictionData
from src.comparison.history import ExperimentHistoryManager

__all__ = [
    "ModelRegistry",
    "BaseModelRunner",
    "get_default_registry",
    "EvaluationEngine",
    "ExperimentController",
    "CanonicalPredictionData",
    "ExperimentHistoryManager",
]
