# Spatial Alignment Implementation

---

## 1. IDW Implementation Algorithm

The Inverse Distance Weighting module projects measurements from $N$ distributed source nodes to the $S = 16$ air monitoring stations:

```python
def compute_idw(
    source_values: np.ndarray,      # Shape: (N_sources, T_hours)
    source_coords: np.ndarray,      # Shape: (N_sources, 2) [lat, lon]
    target_coords: np.ndarray,      # Shape: (16, 2) [lat, lon]
    power: float = 2.0
) -> np.ndarray:                    # Returns: (16, T_hours)
    # Compute Haversine distances D[i, j] between source i and target j
    # w_ij = 1.0 / (D_ij ** power)
    # u'_j = sum(w_ij * u_i) / sum(w_ij)
    ...
```

---

## 2. Handling Missing Source Observations & Zero Distance

1. **Unobserved Links**: If source link $i$ is unobserved at timestamp $t$, it is dynamically omitted from both the numerator and denominator:
   $$u'_{j,t} = \frac{\sum_{i \in \mathcal{O}_t} w_{ij} u_{i,t}}{\sum_{i \in \mathcal{O}_t} w_{ij}}$$
2. **Co-located Source and Target ($d(i, j) = 0$)**: The piecewise definition directly assigns $u'_j = u_i$, preventing division by zero.
3. **Power Exponent**: Fixed to $p = 2.0$ matching Section III-A of Yu et al. (2025).
