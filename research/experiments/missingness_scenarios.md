# Missingness Scenarios & Benchmark Masks

Missingness evaluation masks $\mathbf{M}_{\text{eval}}$ are generated strictly across ground-truth observed entries ($\mathbf{M}_{\text{obs}} = 1$) under three distinct failure modes:

---

## 1. Scenario A: Point Missing Completely at Random (MCAR)
- **Rates**: $r \in \{10\%, 30\%, 50\%, 70\%\}$.
- **Mechanism**: Each observed element is independently masked with probability $r$.
- **Physical Analogue**: Transient telemetry packet drops.

---

## 2. Scenario B: Continuous Temporal Block Missingness
- **Rates**: $r \in \{10\%, 30\%, 50\%, 70\%\}$.
- **Mechanism**: Contiguous temporal intervals of length $L \in [3, 12]$ hours are removed from randomly selected channels and stations until the target fraction $r$ is masked.
- **Physical Analogue**: Telemetry hardware failure, sensor power outages, zero/span calibration cycles.

---

## 3. Scenario C: Spatial Station Outage
- **Mechanism**: All 5 pollutant channels at $k \in \{1, 2, 4\}$ entire stations are masked out simultaneously for the full 24-hour window.
- **Physical Analogue**: Station decommissioning, station-wide electrical failure, routine annual maintenance overhaul.
