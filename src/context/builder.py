"""Backward-compatibility alias module for context_builder.

Direct imports from `src.context.context_builder` are preferred.
"""

from src.context.context_builder import (
    EnvironmentalContextBuilder,
    build_environmental_context,
)

__all__ = ["EnvironmentalContextBuilder", "build_environmental_context"]
