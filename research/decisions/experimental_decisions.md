# Experimental Decision Records

---

## Decision E01: Multi-Scenario Missingness Benchmarking Protocol

- **Date**: 2026-09-13
- **Status**: **`ACCEPTED`**

### Context
Real-world sensor failures do not occur solely under Missing Completely At Random (MCAR) assumptions. Evaluating an imputation model on single-point missingness fails to evaluate real operational outages.

### Evidence
Yu et al. (CTDI 2025) evaluate across missing rates $r \in \{10\%, 30\%, 50\%, 70\%\}$. Real environmental networks experience three distinct failure modes:
1. Random telemetry packet dropouts (MCAR).
2. Prolonged sensor failure / power disruption (Continuous temporal blocks of 4 to 12 hours).
3. Entire station offline for maintenance (Spatial station outage).

### Decision
Implement and benchmark three distinct evaluation mask generators across rates $r \in \{0.10, 0.30, 0.50, 0.70\}$:
- **Pattern A (Point MCAR)**: Uniform independent bernoulli masking.
- **Pattern B (Continuous Block)**: Temporal consecutive masked blocks of length $L \in [3, 12]$ hours.
- **Pattern C (Spatial Station Outage)**: Masking all 5 pollutant channels simultaneously at $1$ to $4$ entire stations for the full 24-hour window.

### Alternatives Considered
Testing MCAR only.

### Why Alternatives Were Rejected
Point MCAR is easily solved by spline interpolation; models must prove robustness on severe block and spatial outages.

### Consequences
Requires multi-scenario evaluation loops and reporting separate metric tables for each scenario.

### Revisit Conditions
Permanent.

---

## Decision E02: Dual Deterministic & Probabilistic Evaluation Metrics

- **Date**: 2026-09-12
- **Status**: **`ACCEPTED`**

### Context
CTDI reports only point metrics: Mean Absolute Error (MAE), Root Mean Square Error (RMSE), and Mean Absolute Percentage Error (MAPE). However, as a generative diffusion model, our architecture outputs posterior distributions.

### Evidence
Reporting only MAE/RMSE discards the core advantage of generative modeling (uncertainty estimation). The Continuous Ranked Probability Score (CRPS) and Prediction Interval Coverage Probability (PICP) are standard probabilistic scoring rules.

### Decision
1. To enable direct apples-to-apples comparison with Yu et al. (2025), compute **MAE, RMSE, and MAPE** on the posterior sample median trajectory.
2. To quantify uncertainty calibration, compute **CRPS, 95% PICP, and MPIW (Mean Prediction Interval Width)** across 50 generated posterior sample trajectories.

### Alternatives Considered
Reporting only MAE/RMSE, or reporting only CRPS.

### Why Alternatives Were Rejected
Reporting only point metrics conceals generative value; reporting only probabilistic metrics prevents direct comparison with CTDI.

### Consequences
Evaluation script outputs both point and probabilistic summary tables.

### Revisit Conditions
Permanent.

---

## Decision E03: Primary Published Baseline: CTDI (Yu et al., IEEE TBD 2025)

- **Date**: 2026-09-12
- **Status**: **`ACCEPTED`**

### Context
Selecting the primary competitive target for the research project.

### Evidence
Yu et al., *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, IEEE Transactions on Big Data (2025) represents the most recent, published state-of-the-art specifically designed for Hong Kong air quality across 2019–2021.

### Decision
Adopt CTDI as the primary competitive baseline benchmark. All performance claims will be measured relative to their published MAE/RMSE numbers on Dataset AU (13 channels) and Dataset A (5 channels).

### Alternatives Considered
CSDI (Tashiro et al., 2021), SAITS (Du et al., 2023), BRITS (Cao et al., 2018).

### Why Alternatives Were Rejected
These are general time-series models; CTDI was specifically developed for the exact same geographic territory, station network, and time period.

### Consequences
Ensures maximum scientific relevance and publication impact.

### Revisit Conditions
Permanent.
