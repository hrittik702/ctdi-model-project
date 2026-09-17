# Canonical Dataset Definition

---

## 1. Mathematical Tensor Formulation

The canonical dataset represents a 3-dimensional multi-modal spatio-temporal tensor:
$$\mathbf{X} \in \mathbb{R}^{S \times T \times C}$$
accompanied by an immutable binary observation mask:
$$\mathbf{M}_{\text{obs}} \in \{0, 1\}^{S \times T \times C}$$

where:
- $S = 16$: Spatial nodes (the 16 continuous air quality monitoring stations in Hong Kong).
- $T = 26,304$: Temporal timestamps (hourly continuous time steps across 3 full calendar years).
- $C = 13$: Multi-modal feature channels matching published CTDI Table I.

### Tensor Volume Dimensions
$$\text{Total Elements} = 16 \times 26,304 \times 13 = \mathbf{5,471,232} \text{ float values}$$
$$\text{Total Tabular Station-Hour Rows} = 16 \times 26,304 = \mathbf{420,864} \text{ records}$$

---

## 2. Binary Observation Mask Formulation

The observation mask $\mathbf{M}_{\text{obs}}$ records true physical sensor presence:
$$M_{\text{obs}}(s, t, c) = \begin{cases} 1 & \text{if sensor reading exists and is valid} \\ 0 & \text{if reading is naturally missing (NaN)} \end{cases}$$

### Strict Integrity Rules
1. **Preservation of Natural Missingness**: Natural missing values in raw sensor channels are preserved as IEEE 754 `np.nan` in `tensor_features.npy` and marked as `0` in `tensor_mask.npy`.
2. **Zero Pre-Imputation**: The raw canonical tensor is never filled with heuristic or spline interpolations.
3. **Data Types**:
   - `tensor_features.npy`: `np.float32` (≈ 21.9 MB).
   - `tensor_mask.npy`: `np.uint8` (≈ 5.5 MB).

---

## 3. Storage Layout & Canonical Formats

```text
data/canonical/
├── tensor_features.npy               # Shape: (16, 26304, 13), float32
├── tensor_mask.npy                   # Shape: (16, 26304, 13), uint8
├── timestamps.csv                    # 26,304 ISO datetime strings
├── channels.json                     # Ordered list of 13 channel identifiers
├── stations.json                     # Metadata dictionary for the 16 stations
└── spatial_distance_matrix.npy       # Shape: (16, 16), float32 pairwise Haversine km
```
