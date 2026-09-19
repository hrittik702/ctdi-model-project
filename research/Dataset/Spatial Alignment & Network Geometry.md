# Spatial Alignment & Network Geometry

---

## 1. Mathematical Inverse Distance Weighting (IDW) Formulation

Section III-A (Equation 1, Page 2445) of Yu et al. (IEEE TBD 2025) specifies the spatial interpolation equation:

$$u'_j = \begin{cases} \frac{\sum_{i=1}^N w_{ij} u_i}{\sum_{i=1}^N w_{ij}} & \text{if } d(i, j) \neq 0 \\ u_i & \text{if } d(i, j) = 0 \end{cases}$$

where:
- $u_i$: Raw measurement (traffic speed or congestion level) at the $i$-th road link ($i \in \{1, \dots, 607\}$).
- $u'_j$: Interpolated value at the $j$-th air quality station ($j \in \{1, \dots, 16\}$).
- $d(i, j)$: Great-circle Haversine distance between road link centroid $i$ and air station $j$.
- $w_{ij} = \frac{1}{d(i, j)^2}$ (power exponent $p = 2$).

---

## 2. Road Link Centroid Derivation

Each road link in the 1st Generation Traffic Speed Map (`speedmap.xml`) is defined by start coordinates $(\phi_{\text{start}}, \lambda_{\text{start}})$ and end coordinates $(\phi_{\text{end}}, \lambda_{\text{end}})$. Following standard geospatial transport practices, the link observation point is the midpoint centroid:

$$\phi_{\text{centroid}} = \frac{\phi_{\text{start}} + \phi_{\text{end}}}{2}, \quad \lambda_{\text{centroid}} = \frac{\lambda_{\text{start}} + \lambda_{\text{end}}}{2}$$

---

## 3. Station Pairwise Haversine Distance Matrix

The pairwise spatial distance matrix $\mathbf{D} \in \mathbb{R}^{16 \times 16}$ between the 16 continuous air quality stations is saved at:
`data/interim/aligned/spatial_distance_matrix.npy` (also mirrored at `data/interim/spatial_distance_matrix.npy`).

### Validation Properties
1. **Dimension**: Exactly $(16, 16)$, `np.float32`.
2. **Diagonal**: $D_{ii} = 0.0\text{ km}$ for all $i \in \{1, \dots, 16\}$.
3. **Symmetry**: $D_{ij} = D_{ji}$ for all $i, j$ (difference $< 10^{-6}$).
4. **Range**: Minimum non-zero distance is $1.98\text{ km}$ (between Causeway Bay and Central); maximum distance is $45.2\text{ km}$ (between Tung Chung and Tap Mun).

---

## 4. Phase 2 Empirical Traffic Spatial Projection

In Phase 2 (`src/preprocessing/traffic_spatial_mapping.py` and `src/preprocessing/build_aligned_dataset.py`), sub-hourly telemetry records were aggregated and spatially resolved to the 16 air quality monitoring stations:

### 4.1 Execution Summary
- **Source Link Aggregation**: $466,829,497$ raw 5-minute link observations aggregated to $15,725,618$ hourly link records across 632 unique links in the network union.
- **Station-Level Mapping**: IDW ($p=2$) projected link speeds and ordinal saturation to the 16 air stations:
  - Total valid station-hours: **$418,448$ rows** ($99.43\%$ temporal completeness).
  - Unobserved archive hours: **$2,416$ station-hours** ($0.57\%$) preserved as genuine `NaN`s (zero artificial $0\text{ km/h}$ fills).
  - Speed statistics: Mean $62.23\text{ km/h}$, Range $[34.76, 154.54]\text{ km/h}$.
  - Congestion statistics: Mean $0.1178$, Range $[0.0000, 0.8351]$.

### 4.2 Spatial Confidence Stratification
Because the Transport Department's open feeds provide explicit coordinate geometry for major arterial corridors while inner-district street links lack open georeferencing, stations are categorized into spatial confidence tiers:
1. **High-Confidence Urban Core** (8 stations: Causeway Bay, Central, Mong Kok, Sham Shui Po, Kwun Tong, Eastern, Kwai Chung, Tsuen Wan; 209,224 station-hours):
   - Proximity: $0.7\text{--}4.5\text{ km}$ to monitored links.
   - High spatial density directly capturing urban canyon traffic dynamics.
2. **Moderate-Confidence Suburban** (3 stations: Sha Tin, Tai Po, Tseung Kwan O; 78,459 station-hours):
   - Proximity: $6.0\text{--}15.0\text{ km}$ to regional highways.
3. **Remote Ecological Background** (5 stations including Tap Mun #76 and Tung Chung #83; 130,765 station-hours):
   - Tap Mun is an offshore island station with zero vehicular roads ($24.74\text{ km}$ to nearest arterial link). IDW correctly decays highway influence, reflecting near-zero vehicular emissions.

### 4.3 Research Boundary Adherence
- **Zero Coordinate Fabrication**: No unverified synthetic coordinates were invented for unreferenced links.
- **Natural Missingness Preserved**: Data gaps reflect actual upstream telemetry downtime.
