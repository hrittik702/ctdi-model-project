# Missingness Architecture: Natural vs. Simulated

---

## 1. The Fundamental Epistemic Distinction

A core requirement of benchmark imputation research is the absolute separation between:
1. **Natural Sensor Missingness ($\mathbf{M}_{\text{obs}}$)**: The ground-truth real-world gaps caused by physical sensor telemetry drops, filter changes, and calibration cycles.
2. **Simulated Evaluation Missingness ($\mathbf{M}_{\text{eval}}$)**: Synthetic evaluation masks applied to uncorrupted ground-truth readings to measure model imputation error.

```
┌─────────────────────────────────────────────────────────────┐
│ RAW PHYSICAL OBSERVATION                                    │
│ • Valid Sensor Reading  -> M_obs = 1, Value = float         │
│ • Natural Telemetry Gap -> M_obs = 0, Value = NaN           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ BENCHMARK EVALUATION SIMULATION (M_eval)                    │
│ • Evaluated strictly where M_obs == 1 (True ground truth)   │
│ • Masked dynamically at 10%, 30%, 50%, 70%                  │
│ • Loss computed ONLY on simulated missing entries           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Empirical Natural Missingness in Hong Kong Air Quality

Audited across the full 3-year study period ($420,864$ station-hour records) in `data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv`:

| Pollutant Channel | Valid Observations | Missing Measurements | Natural Missing Percentage | Physical Range in Dataset | Observed Mean |
| :---: | :---: | :---: | :---: | :---: | :---: |
| $\text{PM}_{2.5}$ | 410,207 | 10,657 | **2.53%** | $[0.0, 167.0]\ \mu\text{g/m}^3$ | $17.46\ \mu\text{g/m}^3$ |
| $\text{PM}_{10}$ | 409,469 | 11,395 | **2.71%** | $[0.0, 241.0]\ \mu\text{g/m}^3$ | $29.65\ \mu\text{g/m}^3$ |
| $\text{NO}_2$ | 409,213 | 11,651 | **2.77%** | $[0.0, 366.0]\ \mu\text{g/m}^3$ | $42.85\ \mu\text{g/m}^3$ |
| $\text{O}_3$ | 409,747 | 11,117 | **2.64%** | $[0.0, 422.0]\ \mu\text{g/m}^3$ | $50.77\ \mu\text{g/m}^3$ |
| $\text{SO}_2$ | 409,808 | 11,056 | **2.63%** | $[0.0, 81.0]\ \mu\text{g/m}^3$ | $4.85\ \mu\text{g/m}^3$ |

### Natural Missingness Observations
- Across all 5 criteria pollutants, natural missingness is remarkably uniform, falling between **2.53% and 2.77%**.
- There are **zero negative concentrations** in the EPD dataset (valid physical lower bound at $0.0$).
- There are **zero duplicate timestamps** on `(station_name, timestamp)`.

---

## 3. Benchmark Evaluation Mask Protocols ($\mathbf{M}_{\text{eval}}$)

To benchmark against Yu et al. (CTDI 2025) and evaluate real-world robustness, we implement three simulated missingness patterns:

### Pattern A: Point Missing Completely at Random (MCAR)
- Independent Bernoulli trials: $P(M_{s,t,c} = 0) = r$ for $r \in \{0.10, 0.30, 0.50, 0.70\}$.
- Simulates random wireless packet drops.

### Pattern B: Continuous Temporal Block Missingness
- For a selected station and channel, a continuous temporal window of length $L \sim \text{Uniform}(3, 12)$ hours is masked out.
- Simulates power outages or equipment recalibration shutdowns.

### Pattern C: Spatial Station Outages
- All 5 criteria pollutants at $k \in \{1, 2, 3, 4\}$ entire stations are masked out for the full 24-hour period.
- Tests spatial reconstruction capacity using surviving regional stations.
