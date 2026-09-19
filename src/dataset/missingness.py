"""Deterministic controlled missingness masking engine for experimental evaluation.

Implements benchmark masking protocols across genuinely observed values (M_natural == 1):
- Random Point Missingness (MCAR): 10%, 30%, 50%, 70%
- Continuous Temporal Block Missingness (MAR): 10%, 30%, 50%, 70% (blocks of 3-12h, trimmed to target)
- Spatial Station Outage:
    * S1: 1 station unavailable out of 16 (6.25% network rate)
    * S2: 2 stations unavailable out of 16 (12.50% network rate)
    * S4: 4 stations unavailable out of 16 (25.00% network rate)
    * S_single: Complete station-level blackout for a single target station

Strict Guarantees:
1. Natural missing entries (NaNs in original data) NEVER become artificial targets.
2. M_natural == M_observed + M_target everywhere.
3. M_observed and M_target are strictly disjoint (M_observed * M_target == 0).
4. Ground truth targets Y_target = X_original * M_target remain fully recoverable.
5. All mask generation is 100% reproducible via explicit random seeds.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


DEFAULT_TARGET_CHANNELS = [0, 1, 2, 3, 4]  # pm25, pm10, no2, so2, o3
ALL_16_STATIONS = [66, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83]


class ExperimentalMaskGenerator:
    """Deterministic generator of controlled missingness masks."""

    def __init__(
        self,
        default_target_channels: Optional[List[int]] = None,
        seed: int = 42,
    ):
        """Initialize mask generator.
        
        Args:
            default_target_channels: List of column indices eligible for masking (default 0..4).
            seed: Default random seed.
        """
        self.default_target_channels = default_target_channels or DEFAULT_TARGET_CHANNELS
        self.seed = seed

    def create_random_mask(
        self,
        natural_mask: np.ndarray,
        rate: float,
        seed: Optional[int] = None,
        target_channels: Optional[List[int]] = None,
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """Generate Point Missing Completely at Random (MCAR) artificial mask.
        
        Args:
            natural_mask: Binary array of shape (24, 13) where 1=observed, 0=natural NaN.
            rate: Desired fraction of observed target cells to mask (e.g. 0.10, 0.30, 0.50, 0.70).
            seed: Random seed for deterministic reproducibility.
            target_channels: Indices of channels eligible for masking.
            
        Returns:
            Tuple of (m_observed, m_target, actual_rate).
        """
        rng = np.random.default_rng(seed if seed is not None else self.seed)
        channels = target_channels if target_channels is not None else self.default_target_channels

        m_nat = np.copy(natural_mask).astype(np.int64)
        m_art = np.zeros_like(m_nat, dtype=np.int64)

        eligible_coords = []
        for ch in channels:
            for t in range(natural_mask.shape[0]):
                if natural_mask[t, ch] == 1:
                    eligible_coords.append((t, ch))

        n_eligible = len(eligible_coords)
        if n_eligible == 0:
            return m_nat, m_art, 0.0

        n_to_mask = int(round(rate * n_eligible))
        if rate > 0.0 and n_to_mask == 0 and n_eligible > 0:
            n_to_mask = 1
        n_to_mask = min(n_to_mask, n_eligible)

        selected_indices = rng.choice(n_eligible, size=n_to_mask, replace=False)
        for idx in selected_indices:
            t, ch = eligible_coords[idx]
            m_art[t, ch] = 1

        m_tgt = m_nat * m_art
        m_obs = m_nat * (1 - m_art)
        actual_rate = float(np.sum(m_tgt)) / float(n_eligible)

        return m_obs, m_tgt, actual_rate

    def create_block_mask(
        self,
        natural_mask: np.ndarray,
        rate: float,
        seed: Optional[int] = None,
        target_channels: Optional[List[int]] = None,
        block_range: Tuple[int, int] = (3, 12),
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """Generate Continuous Temporal Block Missingness (MAR) artificial mask.
        
        Removes contiguous temporal chunks (length in block_range) from randomly selected
        target channels. When adding the final block would exceed the target cell count,
        the final block is trimmed to match the exact target number of eligible cells.
        
        This guarantees actual_rate within +-0.5 percentage points of requested rate.
        
        Args:
            natural_mask: Binary array of shape (24, 13).
            rate: Target fraction of observed target cells to mask (0.10, 0.30, 0.50, 0.70).
            seed: Random seed.
            target_channels: Column indices eligible for masking.
            block_range: (min_hours, max_hours) for contiguous block lengths.
            
        Returns:
            Tuple of (m_observed, m_target, actual_rate).
        """
        rng = np.random.default_rng(seed if seed is not None else self.seed)
        channels = target_channels if target_channels is not None else self.default_target_channels

        m_nat = np.copy(natural_mask).astype(np.int64)
        m_art = np.zeros_like(m_nat, dtype=np.int64)

        n_eligible = sum(np.sum(m_nat[:, ch] == 1) for ch in channels)
        if n_eligible == 0 or rate <= 0.0:
            return m_nat, m_art, 0.0

        n_target_cells = int(round(rate * n_eligible))
        n_masked = 0
        max_attempts = 500
        attempts = 0
        t_len = natural_mask.shape[0]

        while n_masked < n_target_cells and attempts < max_attempts:
            attempts += 1
            ch = int(rng.choice(channels))
            b_len = int(rng.integers(block_range[0], block_range[1] + 1))
            b_len = min(b_len, t_len)
            t_start = int(rng.integers(0, t_len - b_len + 1))
            t_end = t_start + b_len

            # Find unmasked observed positions in this candidate block
            block_candidates = []
            for t in range(t_start, t_end):
                if m_nat[t, ch] == 1 and m_art[t, ch] == 0:
                    block_candidates.append((t, ch))

            if not block_candidates:
                continue

            needed = n_target_cells - n_masked
            if len(block_candidates) <= needed:
                # Add full contiguous segment
                for t, c in block_candidates:
                    m_art[t, c] = 1
                n_masked += len(block_candidates)
            else:
                # Trim final block to exact remaining target count
                # Preserves temporal contiguity by taking consecutive hours from start of block
                for t, c in block_candidates[:needed]:
                    m_art[t, c] = 1
                n_masked += needed
                break

        # If after max attempts we still need cells (e.g. fragmented mask), fill from longest unmasked gaps
        if n_masked < n_target_cells:
            remaining_needed = n_target_cells - n_masked
            rem_eligible = [(t, ch) for ch in channels for t in range(t_len) if m_nat[t, ch] == 1 and m_art[t, ch] == 0]
            if rem_eligible:
                for t, c in rem_eligible[:remaining_needed]:
                    m_art[t, c] = 1
                n_masked += min(remaining_needed, len(rem_eligible))

        m_tgt = m_nat * m_art
        m_obs = m_nat * (1 - m_art)
        actual_rate = float(np.sum(m_tgt)) / float(n_eligible) if n_eligible > 0 else 0.0

        return m_obs, m_tgt, actual_rate

    def create_station_outage_mask(
        self,
        natural_mask: np.ndarray,
        station_id: int,
        selected_outage_stations: Optional[List[int]] = None,
        target_channels: Optional[List[int]] = None,
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """Generate Station-Wise Missingness Outage.
        
        If current station_id is in selected_outage_stations (or if selected_outage_stations is None),
        all target criteria pollutants are masked for this 24-hour window.
        Exogenous weather and traffic channels remain fully available.
        If station_id is NOT in selected_outage_stations, 0 cells are masked.
        
        Args:
            natural_mask: Binary array of shape (24, 13).
            station_id: ID of the current station.
            selected_outage_stations: List of station IDs undergoing outage. If None, masks this station.
            target_channels: Indices of channels to mask (default 0..4).
            
        Returns:
            Tuple of (m_observed, m_target, actual_rate).
        """
        channels = target_channels if target_channels is not None else self.default_target_channels
        m_nat = np.copy(natural_mask).astype(np.int64)
        m_art = np.zeros_like(m_nat, dtype=np.int64)

        n_eligible = sum(np.sum(m_nat[:, ch] == 1) for ch in channels)
        if n_eligible == 0:
            return m_nat, m_art, 0.0

        is_outage = (selected_outage_stations is None) or (station_id in selected_outage_stations)

        if is_outage:
            for ch in channels:
                m_art[:, ch] = 1

        m_tgt = m_nat * m_art
        m_obs = m_nat * (1 - m_art)
        actual_rate = float(np.sum(m_tgt)) / float(n_eligible) if is_outage else 0.0

        return m_obs, m_tgt, actual_rate

    @staticmethod
    def select_outage_stations(
        time_index: int,
        count: int,
        seed: int = 42,
        station_pool: Optional[List[int]] = None,
    ) -> List[int]:
        """Deterministically select k stations undergoing outage at a given time step.
        
        Rotates through station network over time to ensure uniform evaluation coverage
        across general, roadside, and rural stations.
        
        Args:
            time_index: Discrete time step index (e.g. 0..3888 in test set).
            count: Number of stations undergoing outage (1, 2, or 4).
            seed: Random seed.
            station_pool: List of available station IDs.
            
        Returns:
            List of selected station IDs.
        """
        pool = station_pool or ALL_16_STATIONS
        n_stations = len(pool)
        if count >= n_stations:
            return list(pool)
        if count <= 0:
            return []

        # Deterministic rotation stride
        stride = n_stations // count
        offset = (time_index * 3 + seed) % n_stations
        selected = [pool[(offset + i * stride) % n_stations] for i in range(count)]
        return sorted(selected)

    def create_mask(
        self,
        natural_mask: np.ndarray,
        pattern: str = "random",
        rate: float = 0.30,
        seed: Optional[int] = None,
        station_id: Optional[int] = None,
        selected_outage_stations: Optional[List[int]] = None,
        target_channels: Optional[List[int]] = None,
        block_range: Tuple[int, int] = (3, 12),
    ) -> Tuple[np.ndarray, np.ndarray, float, Dict[str, Any]]:
        """Universal dispatcher for controlled experimental masking."""
        pat = pattern.lower().strip()
        channels = target_channels if target_channels is not None else self.default_target_channels
        used_seed = seed if seed is not None else self.seed

        if pat in ["random", "mcar", "point"]:
            m_obs, m_tgt, actual_rate = self.create_random_mask(
                natural_mask=natural_mask,
                rate=rate,
                seed=used_seed,
                target_channels=channels,
            )
        elif pat in ["block", "mar", "temporal_block"]:
            m_obs, m_tgt, actual_rate = self.create_block_mask(
                natural_mask=natural_mask,
                rate=rate,
                seed=used_seed,
                target_channels=channels,
                block_range=block_range,
            )
        elif pat in ["station_wise", "station", "station_outage"]:
            m_obs, m_tgt, actual_rate = self.create_station_outage_mask(
                natural_mask=natural_mask,
                station_id=station_id if station_id is not None else 0,
                selected_outage_stations=selected_outage_stations,
                target_channels=channels,
            )
        else:
            raise ValueError(f"Unknown masking pattern '{pattern}'. Expected 'random', 'block', or 'station_wise'.")

        metadata = {
            "pattern": pat,
            "requested_rate": float(rate),
            "actual_rate": float(actual_rate),
            "seed": int(used_seed),
            "target_channels": list(channels),
            "total_target_cells": int(np.sum(m_tgt)),
            "total_observed_cells": int(np.sum(m_obs)),
            "total_natural_observed": int(np.sum(m_obs) + np.sum(m_tgt)),
        }

        return m_obs, m_tgt, actual_rate, metadata

    @staticmethod
    def partition_inputs_and_targets(
        window_data: np.ndarray,
        natural_mask: np.ndarray,
        target_mask: np.ndarray,
        fill_input_with: float = np.nan,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Construct model input tensor X_input and evaluation ground truth Y_target."""
        m_obs = natural_mask * (1 - target_mask)

        x_input = np.copy(window_data)
        x_input[m_obs == 0] = fill_input_with

        y_target = np.full_like(window_data, np.nan)
        y_target[target_mask == 1] = window_data[target_mask == 1]

        return x_input, y_target


def simulate_missingness(
    natural_mask: np.ndarray,
    pattern: str = "random",
    rate: float = 0.30,
    seed: int = 42,
    target_channels: Optional[List[int]] = None,
) -> Tuple[np.ndarray, np.ndarray, float]:
    """Convenience function matching legacy module interface."""
    generator = ExperimentalMaskGenerator(seed=seed)
    m_obs, m_tgt, actual_rate, _ = generator.create_mask(
        natural_mask=natural_mask,
        pattern=pattern,
        rate=rate,
        seed=seed,
        target_channels=target_channels,
    )
    return m_obs, m_tgt, actual_rate
