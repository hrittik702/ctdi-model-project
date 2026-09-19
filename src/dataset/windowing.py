"""Windowing sequence generation specification.

Note: Canonical 24-hour sliding window generation with chronological indexing,
missingness masks, and purge buffer identification is implemented in
`src/preprocessing/build_windows.py`.
"""


def create_sliding_windows(*args, **kwargs):
    """Create sliding temporal windows. Refer to src/preprocessing/build_windows.py."""
    raise NotImplementedError(
        "Canonical 24-hour window generation is implemented in src/preprocessing/build_windows.py."
    )
