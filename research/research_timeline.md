# Chronological Research Timeline

This document maintains the high-level historical narrative and chronological evolution of the project. Each entry summarizes a key working session, referencing the corresponding dated checkpoint in `research/checkpoints/`.

---

## 2026-09-10 — Project Initialization & Environment Setup

### Objective
Initialize the research repository, establish the Python virtual environment, define project directory scaffolding, and set up core dependencies.

### Work
- Created root structure (`src/`, `data/`, `configs/`, `reports/`, `tests/`).
- Initialized Python 3.12 virtual environment (`.venv/`) with PyTorch CPU optimization, Pandas, NumPy, and PyArrow.
- Configured Pytest test framework and Ruff linting rules.

### Finding
- PyTorch CPU threading configuration significantly improves batch processing on local hardware without GPU overhead.

### Decision
- Standardize on `.venv/` for all Python executions.
- Use PyArrow engine for all Parquet and tabular serialization.

### Evidence
- Commit `3960162` ("Faster Development Tools"), Commit `9a8d1d6` ("add : pytest config"), Commit `48838a7` ("optimise pytorch cpu threadpool").

### Status
- **`COMPLETED`** (Refer to checkpoint archive).

---

## 2026-09-11 — Preliminary Keras & Graph Modeling Experiments

### Objective
Explore deep learning baseline architectures for spatio-temporal data and evaluate graph neural network implementations.

### Work
- Implemented test harnesses for spatial graph convolutions and multi-layer perceptron benchmarks.
- Evaluated Keras vs. native PyTorch graph implementations.

### Finding
- Native PyTorch provides greater modularity and lower memory overhead for multi-modal conditional diffusion and custom attention masking.

### Decision
- Standardize all future model implementations strictly on PyTorch. Deprecate Keras prototypes.

### Evidence
- Commit `ced37cc` ("Keras & Graph testing"), Commit `d4a8d26` ("keras Enhace & CTDI Original").

### Status
- **`SUPERSEDED`** (Keras prototypes archived; PyTorch chosen).

---

## 2026-09-12 — Phase 1 Raw Data Ingestion & Station Metadata Verification

### Objective
Acquire and validate raw public datasets across Hong Kong: air quality (EPD), meteorology (HKO/Open-Meteo), and traffic (TD ATC), verifying spatial station consistency and 3-year temporal coverage (2019–2021).

### Work
- Ingested 36 monthly air quality archives from HKEPD (`data/raw/air_quality/`).
- Ingested hourly surface meteorology for 16 station coordinates (`data/raw/meteorology/`).
- Downloaded Transport Department Annual Traffic Census (ATC) survey files (`ATC_TRAFFIC_DATA.zip`).
- Catalogued 18 air quality stations; verified coordinates and elevations.
- Wrote automated verification suite `scripts/verify_raw_datasets.py`.
- Documented data engineering lifecycle in `reports/Data Preprocessing/00` to `09`.

### Finding
- 16 stations operated continuously from 2019 to 2021 ($26,304$ hours = $420,864$ rows).
- Confirmed paper statement: *"Two newer Hong Kong air-pollution monitoring stations were excluded for data consistency."* The two excluded stations are **Southern (#84)** and **North (#85)**, commissioned on July 10, 2020. Retaining them would inject an 18-month 100% missingness gap.
- Air quality natural missingness across criteria pollutants is $\approx 2.53\%$ to $2.77\%$.

### Decision
- Restrict study domain strictly to the 16 continuous stations.
- Exclude Southern (#84) and North (#85).
- Enforce Zero Data Leakage: fit all normalization scalers on Train split only.

### Evidence
- `reports/Phase 1.md`, `reports/CTDI Dataset Description.md`, Commit `fe4322c` ("Data Preprocessing : Phase 1 Complete").

### Status
- **`VERIFIED`** for Station Metadata and Air Quality.

---

## 2026-09-13 — CTDI Table I Reconstruction, Traffic Source Audit & Research Freeze

### Objective
Perform strict, research-grade verification of the published CTDI 13-channel dataset specification against Yu et al. (IEEE Transactions on Big Data, 2025), audit traffic and meteorological data sources, prevent synthetic data contamination, and establish a permanent research documentation architecture.

### Work
- Analyzed published CTDI paper (IEEE TBD 2025), focusing on Table I (Page 2448), Section III-A, IV-A, and V-C.
- Audited candidate traffic variables and data sources (ATC, City Dashboard, parent 1st Gen Speedmap).
- Computed 16×16 station Haversine distance matrix (`data/interim/spatial_distance_matrix.npy`).
- Implemented strict safety halt in `src/preprocessing/alignment.py` to prevent synthetic traffic injection.
- Reconstructed verbatim Table I and published analytical reports (`ctdi_table_i_reconstruction.md`, `ctdi_traffic_variable_verification.md`, `ctdi_channel_reconstruction.md`).
- Established modular research documentation hierarchy under `research/` (`MASTER_RESEARCH_DOCUMENT.md`, `research_status.md`, `research_timeline.md`, `checkpoints/`, `decisions/`, `findings/`, `literature/`, `dataset/`, `preprocessing/`, `architecture/`, `experiments/`).

### Finding
- **Finding 1**: CTDI Table I explicitly defines 13 channels: 5 pollutants, 6 weather, 2 traffic.
- **Finding 2**: CTDI traffic variables are **`Traffic speed`** ($\text{km/h}$) and **`Traffic congestion`** ($\text{N/A}$, derived from `ROAD_SATURATION_LEVEL`). The variable **`traffic_volume` does not exist in CTDI**.
- **Finding 3**: CTDI traffic domain possesses **`607 roads`**, not the 6 harbour links on the City Dashboard portal. The parent 1st Gen Traffic Speed Map (`speedmap.xml`) contains exactly $607$ links and $774,686$ archived snapshots covering 100% of 2019–2021.
- **Finding 4**: CTDI meteorological variable 4 is **`Visibility` ($\text{km}$)**, not `rainfall`.
- **Finding 5**: The Annual Traffic Census (ATC) provides annual averages and cannot produce continuous hourly time-series without synthetic data generation.
- **Finding 6**: City Dashboard historical archive on DATA.GOV.HK only starts Dec 24, 2019 (missing 97.9% of 2019).

### Decision
- Remove `traffic_volume` from target channel list; adopt `traffic_congestion`.
- Halt alignment pipeline until real traffic data from the 607-link parent system is ingested. Prohibit synthetic traffic data under all circumstances.
- Freeze implementation and research for today; establish permanent documentation and checkpoint records.

### Evidence
- `research/checkpoints/2026-09-13.md`
- `research/reports/ctdi_table_i_reconstruction.md`
- `research/reports/ctdi_traffic_variable_verification.md`
- `research/reports/ctdi_channel_reconstruction.md`
- `data/interim/traffic/traffic_validation_report.json`
- `data/interim/traffic/ctdi_traffic_reconstruction.json`
- `data/interim/dataset_validation_report.json`
- `reports/Alignment - PY.md`

### Status
- **`PARTIAL_SUCCESS / INVESTIGATION_ONLY (WORK PAUSED FOR TODAY)`**
