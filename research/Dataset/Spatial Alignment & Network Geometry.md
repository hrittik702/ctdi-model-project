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
`data/interim/spatial_distance_matrix.npy`.

### Validation Properties
1. **Dimension**: Exactly $(16, 16)$, `np.float32`.
2. **Diagonal**: $D_{ii} = 0.0\text{ km}$ for all $i \in \{1, \dots, 16\}$.
3. **Symmetry**: $D_{ij} = D_{ji}$ for all $i, j$ (difference $< 10^{-6}$).
4. **Range**: Minimum non-zero distance is $1.98\text{ km}$ (between Causeway Bay and Central); maximum distance is $45.2\text{ km}$ (between Tung Chung and Tap Mun).
