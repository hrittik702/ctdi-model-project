# Preprocessing Decision Records

---

## Decision P01: Inverse Distance Weighting (IDW, $p=2$) for Spatial Feature Mapping

- **Date**: 2026-09-13
- **Status**: **`ACCEPTED`**

### Context
Meteorology (measured at 47 HKO stations) and traffic (monitored along 607 road links) are physically decoupled from the 16 air-quality monitoring stations. A spatial interpolation method is required to map these distributed measurements to the 16 station coordinates.

### Evidence
Section III-A (Equation 1, Page 2445) of Yu et al. (IEEE TBD 2025) explicitly specifies:
$$u'_j = \begin{cases} \frac{\sum_{i=1}^N w_{ij} u_i}{\sum_{i=1}^N w_{ij}} & \text{if } d(i, j) \neq 0 \\ u_i & \text{if } d(i, j) = 0 \end{cases}$$
with $w_{ij} = \frac{1}{d(i, j)^2}$ ($p = 2$).

### Decision
Apply exact inverse distance weighting with power parameter $p = 2$ using great-circle Haversine distances to project the 607 road link midpoint centroids to the 16 air stations.

### Alternatives Considered
Kriging, nearest-neighbor matching, Voronoi tessellation.

### Why Alternatives Were Rejected
Yu et al. explicitly used IDW ($p=2$). Using another interpolation method would introduce an uncontrolled confounding variable into our benchmark comparison.

### Consequences
Requires computing an immutable $607 \times 16$ distance matrix between all road link centroids and air stations.

### Revisit Conditions
None; matches benchmark ground truth.

---

## Decision P02: Air Quality Stations as Immutable Spatial Anchors

- **Date**: 2026-09-12
- **Status**: **`ACCEPTED`**

### Context
Determining whether the spatial grid should be anchored on weather stations, traffic detectors, or air quality stations.

### Evidence
Air quality criteria pollutants are the primary target variables of the imputation benchmark. Meteorological and traffic factors serve strictly as auxiliary predictive context.

### Decision
Anchor the Cartesian grid strictly to the coordinates of the 16 continuous air quality stations.

### Alternatives Considered
Uniform geographic raster grid across Hong Kong.

### Why Alternatives Were Rejected
Raster grids require interpolating air quality itself, creating ground-truth artifacts. Real sensor observations must be preserved.

### Consequences
Dataset tensor spatial dimension is strictly fixed at $S = 16$.

### Revisit Conditions
Permanent.

---

## Decision P03: Zero Data Leakage (Chronological Splitting & Train-Only Scaler Fitting)

- **Date**: 2026-09-12
- **Status**: **`ACCEPTED`**

### Context
Improper feature scaling (e.g., fitting MinMax or Z-score scalers on the entire 3-year dataset) leaks future test-set statistics (min, max, mean, variance) into training, artificially deflating test errors.

### Evidence
Best practices in machine learning and atmospheric modeling mandate strict causal separation between training and evaluation splits.

### Decision
1. Split the 26,304 hours chronologically:
   - **Train**: 70% ($18,412$ hours, `2019-01-01 00:00` to `2021-02-05 03:00`).
   - **Validation**: 15% ($3,946$ hours, `2021-02-05 04:00` to `2021-07-18 13:00`).
   - **Test**: 15% ($3,946$ hours, `2021-07-18 14:00` to `2021-12-31 23:00`).
2. Fit all normalizers strictly on observed entries ($\mathbf{M}_{\text{obs}} = 1$) within the **Train set only**.
3. Save scaler parameters (`mean`, `std`, `min`, `max`) to JSON for deterministic reproduction during test inference.

### Alternatives Considered
Random k-fold cross validation; whole-dataset normalization.

### Why Alternatives Were Rejected
Random splitting leaks future temporal correlations; whole-dataset scaling violates basic scientific validity.

### Consequences
Guarantees completely honest, leak-free test metrics.

### Revisit Conditions
Permanent.

---

## Decision P04: 24-Hour Sliding Window Segmentation Geometry

- **Date**: 2026-09-12
- **Status**: **`ACCEPTED`**

### Context
Selecting the temporal window length $K$ for DataLoader batching.

### Evidence
Urban air quality and boundary layer dynamics operate on 24-hour diurnal solar cycles (morning traffic emissions, solar noon photochemical ozone peak, evening rush hour, nocturnal temperature inversion). Yu et al. (CTDI 2025) and standard baselines evaluate on 24-hour windows.

### Decision
Fix the sample temporal window length to $K = 24$ hours. For training, extract sliding windows with stride $s = 1$ hour. For evaluation, extract non-overlapping windows with stride $s = 24$ hours.

### Alternatives Considered
12-hour windows, 48-hour windows, 7-day windows.

### Why Alternatives Were Rejected
24 hours captures complete diurnal cycles while fitting comfortably within GPU memory and transformer attention budgets.

### Consequences
Produces $B \times [16, 24, 13]$ tensor batches.

### Revisit Conditions
If multi-day synoptic persistence requires testing an extended 48-hour window ablation.
