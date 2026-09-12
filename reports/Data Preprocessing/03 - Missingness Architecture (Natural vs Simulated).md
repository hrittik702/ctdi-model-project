# 03 - Missingness Architecture (Natural vs Simulated)

> **Previous**: [[02 - Cleaning, Translation & Formatting]] | **Next**: [[04 - Spatial Alignment & 13-Channel Formulation]] | **Index**: [[00 - Overview & Pipeline Architecture]]

---

## 1. Conceptual Framework

In environmental time series imputation research, confusion often arises regarding missing values. There are **two distinct types of missingness** operating in our system:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               THE TWO FORMS OF MISSINGNESS                              │
├───────────────────────────────────────────┬─────────────────────────────────────────────┤
│ 1. NATURAL MISSINGNESS (~2.5%)            │ 2. SIMULATED BENCHMARK MISSINGNESS          │
├───────────────────────────────────────────┼─────────────────────────────────────────────┤
│ • Cause: Sensor recalibration, filter     │ • Cause: Artificially injected by our       │
│   replacement, power blips                │   code for evaluation                       │
│ • True value is UNKNOWN                   │ • True value is SECRETLY KNOWN              │
│ • Masked out during training loss:        │ • Used to calculate benchmark metrics       │
│   Loss = || M_obs ⊙ (X - X_pred) ||       │   (RMSE, MAE, MRE)                          │
│   (Never penalize on unknown labels)      │   (Evaluated strictly on held-out points)   │
└───────────────────────────────────────────┴─────────────────────────────────────────────┘
```

---

## 2. Natural Missingness in Hong Kong Air Quality

### 2.1 Why Does It Occur?
Fixed ambient monitoring stations in Hong Kong operate 24 hours a day, 365 days a year. However, real-world monitoring is interrupted by:
1. **Zero and Span Calibration**: Automated daily checks where known reference gases pass through analyzers.
2. **Filter Tape Advancements**: Periodic beta-attenuation tape changes on particulate analyzers ($\text{PM}_{2.5}, \text{PM}_{10}$).
3. **Routine Preventative Maintenance**: Semi-annual deep servicing of optical benches, laser optics, and pumps.
4. **Transient Line Noise & Telemetry Resets**: Power brownouts during severe typhoon conditions.

### 2.2 Empirical Missingness Statistics (Full 3-Year Archive)

Across the 420,864 total station-hours in `data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv`:

| Pollutant | Observed Valid Hours | Missing Hours (`N.A.`) | Missingness Rate (%) | Min ($\mu\text{g/m}^3$) | Max ($\mu\text{g/m}^3$) | Mean ($\mu\text{g/m}^3$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $\text{PM}_{2.5}$ | 410,207 | 10,657 | **2.53%** | 0.0 | 167.0 | 17.5 |
| $\text{PM}_{10}$ | 409,469 | 11,395 | **2.71%** | 0.0 | 241.0 | 29.7 |
| $\text{NO}_2$ | 409,213 | 11,651 | **2.77%** | 0.0 | 366.0 | 42.8 |
| $\text{O}_3$ | 409,747 | 11,117 | **2.64%** | 0.0 | 422.0 | 50.8 |
| $\text{SO}_2$ | 409,808 | 11,056 | **2.63%** | 0.0 | 81.0 | 4.9 |

> [!NOTE]
> An average natural missingness rate of ~2.6% over a continuous 3-year multi-site network confirms high data quality and sensor reliability (>97.3% network uptime).

---

## 3. The Natural Observation Mask ($\mathbf{M}_{\text{obs}}$)

We define a binary observation mask tensor $\mathbf{M}_{\text{obs}}$ matching the feature tensor shape:

$$\mathbf{M}_{\text{obs}} \in \{0, 1\}^{16 \times 26,304 \times 13}$$

$$\mathbf{M}_{\text{obs}}[s, t, c] = \begin{cases} 1 & \text{if station } s \text{ at time } t \text{ has an observed value for channel } c \\ 0 & \text{if station } s \text{ at time } t \text{ is naturally missing (NaN)} \end{cases}$$

### Role in Masked Loss Computation
When training any neural network (Transformer, Diffusion UNet, or MLP), the loss function must be masked with $\mathbf{M}_{\text{obs}}$:

$$\mathcal{L}(\mathbf{X}, \hat{\mathbf{X}}) = \frac{\sum_{s, t, c} \mathbf{M}_{\text{obs}}[s, t, c] \cdot \ell\big(\mathbf{X}[s, t, c], \hat{\mathbf{X}}[s, t, c]\big)}{\sum_{s, t, c} \mathbf{M}_{\text{obs}}[s, t, c]}$$

where $\ell$ is Mean Squared Error (MSE) or Mean Absolute Error (MAE).  
**Crucial Guarantee**: The model is never penalized for failing to predict a label that nobody knows.

---

## 4. Benchmark Simulated Missingness Protocols (CTDI Specification)

To benchmark our SLM-conditioned diffusion model against the CTDI paper and standard literature (SAITS, CSDI, BRITS), we inject artificial missingness into the observed cells.

### 4.1 Missingness Rates
Experiments are conducted at **4 missingness rates**:
$$\gamma \in \{10\%, 30\%, 50\%, 70\%\}$$

### 4.2 Missingness Patterns

```
PATTERN A: POINT MISSING (MCAR)         PATTERN B: BLOCK MISSING              PATTERN C: SPATIAL OUTAGE
   Time ──>                                Time ──>                              Time ──>
Stn 0:  ■ □ ■ ■ □ ■ ■ ■                Stn 0:  ■ ■ ■ ■ ■ ■ ■ ■               Stn 0:  ■ ■ ■ ■ ■ ■ ■ ■
Stn 1:  ■ ■ □ ■ ■ □ ■ ■                Stn 1:  ■ ■ □ □ □ □ ■ ■  <-- Block    Stn 1:  □ □ □ □ □ □ □ □  <-- Off
Stn 2:  □ ■ ■ ■ ■ ■ □ ■                Stn 2:  ■ ■ ■ ■ ■ ■ ■ ■               Stn 2:  ■ ■ ■ ■ ■ ■ ■ ■
(Independent random points)            (Contiguous time outage)              (Entire station offline)
```

1. **Random Point Missing (MCAR - Missing Completely at Random)**:
   - Each observed cell is dropped independently with probability $\gamma$.
   - Simulates wireless communication packet drops or isolated sampling errors.
2. **Continuous / Block Missing (Temporal Outage)**:
   - Consecutive segments of time (e.g. 4, 8, 12, or 24 hours) are dropped simultaneously across channels at random stations.
   - Simulates hardware breakdown or power failure.
3. **Spatial Station Outage**:
   - An entire station's pollutant channels are masked out for the entire 24-hour window.
   - Tests spatial cross-attention: can the model reconstruct the entire station's readings solely from the 15 neighboring stations and meteorology?

### 4.3 The Evaluation Mask ($\mathbf{M}_{\text{eval}}$)

Let $\mathbf{M}_{\text{sim}} \in \{0, 1\}^{16 \times 24 \times 13}$ be the simulation mask ($1 = \text{kept}, 0 = \text{artificially hidden}$).  
The evaluation mask identifies the exact cells where:
1. A genuine ground truth reading exists ($\mathbf{M}_{\text{obs}} = 1$), **AND**
2. The reading was intentionally hidden from the model ($\mathbf{M}_{\text{sim}} = 0$).

$$\mathbf{M}_{\text{eval}} = \mathbf{M}_{\text{obs}} \odot (1 - \mathbf{M}_{\text{sim}})$$

Evaluation metrics are computed **strictly on the evaluation mask**:

$$\text{RMSE} = \sqrt{\frac{\sum \mathbf{M}_{\text{eval}} \odot (\mathbf{X}_{\text{true}} - \hat{\mathbf{X}})^2}{\sum \mathbf{M}_{\text{eval}}}}$$

$$\text{MAE} = \frac{\sum \mathbf{M}_{\text{eval}} \odot |\mathbf{X}_{\text{true}} - \hat{\mathbf{X}}|}{\sum \mathbf{M}_{\text{eval}}}$$

$$\text{MRE} = \frac{\sum \mathbf{M}_{\text{eval}} \odot |\mathbf{X}_{\text{true}} - \hat{\mathbf{X}}|}{\sum \mathbf{M}_{\text{eval}} \odot |\mathbf{X}_{\text{true}}|}$$
