# CTDI Paper Exhaustive Analysis

**Paper Citation**:  
Yangwen Yu, Victor O. K. Li, Jacqueline C. K. Lam, Kelvin Chan, Qi Zhang, *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, **IEEE Transactions on Big Data**, vol. 11, no. 5, pp. 2442–2455, Sept.–Oct. 2025.  
DOI: [10.1109/TBDATA.2025.3533882](https://doi.org/10.1109/TBDATA.2025.3533882).

---

## 1. Executive Summary & Core Contribution

The authors propose **CTDI**, a deterministic deep learning architecture designed to impute missing air quality sensor records by jointly modeling spatial correlations (via Convolutional Neural Networks) and temporal dynamics (via Transformer self-attention). The model explicitly incorporates external urban factors—specifically surface meteorology and road traffic dynamics—into the input space.

---

## 2. Exhaustive Table I Analysis (Page 2448)

Table I of the paper provides the ground-truth specification of the experimental dataset collected for Hong Kong:

| Domain | Number of Data Nodes | Data Category | Unit | Update Frequency | Source Reference in Paper |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **Air pollution** | 16 stations | $\text{PM}_{2.5}$ | $\mu\text{g/m}^3$ | 1 hour | HKEPD Database [80] |
| | | $\text{PM}_{10}$ | $\mu\text{g/m}^3$ | 1 hour | HKEPD Database [80] |
| | | $\text{NO}_2$ | $\mu\text{g/m}^3$ | 1 hour | HKEPD Database [80] |
| | | $\text{SO}_2$ | $\mu\text{g/m}^3$ | 1 hour | HKEPD Database [80] |
| | | $\text{O}_3$ | $\mu\text{g/m}^3$ | 1 hour | HKEPD Database [80] |
| **Meteorology** | 47 stations | Pressure | $\text{hPa}$ | 10 min | HKO Open Database [81] |
| | | Relative humidity | $\%$ | 10 min | HKO Open Database [81] |
| | | Temperature | $^\circ\text{C}$ | 10 min | HKO Open Database [81] |
| | | Visibility | $\text{km}$ | 10 min | HKO Open Database [81] |
| | | Wind direction | N/A | 10 min | HKO Open Database [81] |
| | | Wind speed | $\text{km/h}$ | 10 min | HKO Open Database [81] |
| **Traffic** | 607 roads | Traffic speed | $\text{km/h}$ | 5min | HK Traffic Speed Map [82] |
| | | Traffic congestion | N/A | 5min | HK Traffic Speed Map [82] |

### Key Takeaways from Table I
1. **Total Channels = 13**: 5 criteria pollutants + 6 meteorological variables + 2 traffic variables.
2. **Traffic Variables**: Are `Traffic speed` and `Traffic congestion`. `traffic_volume` does **not** appear.
3. **Traffic Spatial Nodes**: Exactly **607 road links**.
4. **Meteorological Variables**: The fourth variable is **Visibility** ($\text{km}$), NOT rainfall.
5. **Meteorological Nodes**: 47 Automatic Weather Stations across Hong Kong.
6. **Air Quality Nodes**: Exactly 16 stations. Footnote 1 explicitly notes: *"Two newer Hong Kong air-pollution monitoring stations were excluded for data consistency"* (confirmed to be Southern #84 and North #85, opened July 10, 2020).

---

## 3. Spatial Preprocessing Component & IDW Formulation (Section III-A)

Section III-A (Page 2445, Equation 1) specifies the exact inverse distance weighting formula used to project the 607 road links and 47 meteorological stations to the 16 air quality monitoring stations:

$$u'_j = \begin{cases} \frac{\sum_{i=1}^N w_{ij} u_i}{\sum_{i=1}^N w_{ij}} & \text{if } d(i, j) \neq 0 \\ u_i & \text{if } d(i, j) = 0 \end{cases}$$

where:
- $u_i$ is the raw measurement at the $i$-th source location ($i \in \{1, \dots, N\}$).
- $u'_j$ is the interpolated value at the $j$-th air quality station ($j \in \{1, \dots, 16\}$).
- $d(i, j)$ is the geographic distance between source node $i$ and target air station $j$.
- $w_{ij} = \frac{1}{d(i, j)^p}$ with power exponent $p = 2$.
- When $d(i, j) = 0$, the station value equals the source observation directly.

---

## 4. Dataset Evaluation in Section V-C

Section V-C evaluates the impact of multimodal data on imputation performance:
- **Dataset A**: Contains only the 5 air pollutant channels ($\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{SO}_2, \text{O}_3$).
- **Dataset AU**: Contains the full 13 channels (5 pollutants + 6 meteorological + 2 traffic variables).

**Key Empirical Finding from Section V-C**:
The authors report that CTDI trained on **Dataset AU** consistently achieves significantly lower MAE and RMSE across all missing rates (10%, 30%, 50%, 70%) compared to Dataset A. This proves that external urban and meteorological factors are essential for resolving air pollution dynamics.

---

## 5. Critical Analysis: What CTDI Lacks

1. **Deterministic Point Estimation**: CTDI generates a single numerical prediction $\hat{y}$. It does not produce predictive distributions or uncertainty bounds.
2. **Lack of High-Level Context**: CTDI treats weather and traffic purely as concatenated floats in a tensor. It cannot recognize overarching atmospheric synoptic regimes (e.g., strong regional inversion vs. convective maritime washout).
3. **Quadratic Complexity**: Standard full self-attention across large temporal windows incurs high memory cost.

These gaps motivate our proposed **SLM-Conditioned Diffusion** framework.
