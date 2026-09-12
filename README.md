# Air Pollution Missing Data Imputation

A research project focused on recovering missing air-quality observations using a proposed framework: **Context-Aware Generative Imputation of Air Pollution Using SLM-Conditioned Diffusion**.

## Project Overview

Missing observations in air pollution monitoring networks (due to sensor degradation, transmission dropouts, and maintenance outages) severely impede environmental modeling and public health decision-making. 

This research investigates whether semantic environmental context (meteorological conditions, seasonal dynamics, station topology, and surrounding influences) can guide generative imputation models to accurately reconstruct missing time-series observations under high missing rates and extended block outages.

> **Current Status**: The project is currently at the initial **Backend / Data-Pipeline Foundation** stage (Stage 1 completed). The machine learning models (Small Language Model context encoding and conditional diffusion) have **not** yet been implemented.

---

## Research Development Roadmap

The project is being developed across the following sequential phases:

1. **Repository & Backend Reset** `[COMPLETED]`
   - Cleaned legacy experimental artifacts and established modular backend package architecture.
   - Preserved raw air-quality datasets, frontend application, and environment.
   - Established minimal configuration and API entry point.
2. **Data Preprocessing** `[NEXT]`
   - Loading raw multi-station air quality data (e.g., UCI Beijing dataset).
   - Data cleaning, validation, temporal alignment, and feature normalization.
3. **Dataset Construction**
   - Sliding window sequence generation (e.g., 24-hour temporal windows).
   - Multi-station tensor formatting.
4. **Missingness Simulation**
   - Controlled simulation of Missing Completely at Random (MCAR), contiguous block outages, and sensor failure patterns.
5. **Context Construction**
   - Extraction and structuring of temporal, meteorological, and geospatial metadata.
6. **SLM Context Encoding**
   - Converting structured environmental context into dense semantic embeddings using a Small Language Model (SLM).
7. **Conditional Diffusion**
   - Generative diffusion modeling conditioned on the semantic environmental embeddings to impute missing observations.
8. **Temporal / Spatial / Context Consistency**
   - Enforcing physical plausibility, multi-pollutant correlations, and cross-station spatial relationships.
9. **Uncertainty-Aware Imputation**
   - Generating distributional imputation samples to quantify prediction confidence and uncertainty intervals.
10. **Experimental Evaluation**
    - Rigorous benchmarking against standard imputation baselines across varied missingness regimes using metrics such as MAE, RMSE, MRE, and CRPS.
11. **API Integration**
    - Exposing model inference, dataset exploration, and evaluation endpoints via FastAPI.
12. **Frontend Integration**
    - Connecting the existing web interface to the backend imputation pipeline.

---

## Project Structure

```text
ctdi-model-project/
├── configs/
│   └── config.yaml             # Core pipeline & dataset configuration
├── data/
│   ├── raw/                    # Raw air-quality datasets (e.g., Beijing PRSA)
│   └── processed/              # Processed tensors & cache (placeholder)
├── frontend/                   # Web interface (React + Tailwind CSS)
├── src/
│   ├── __init__.py
│   ├── preprocessing/          # Data cleaning, normalization, alignment
│   │   ├── __init__.py
│   │   └── pipeline.py
│   ├── dataset/                # Windowing & missingness generation
│   │   ├── __init__.py
│   │   ├── windowing.py
│   │   └── missingness.py
│   ├── context/                # Environmental context builder
│   │   ├── __init__.py
│   │   └── builder.py
│   ├── models/                 # Model architectures (SLM & diffusion)
│   │   └── __init__.py
│   └── evaluation/             # Imputation metrics & benchmarks
│       ├── __init__.py
│       └── metrics.py
├── tests/
│   └── __init__.py
├── api.py                      # FastAPI service entry point
├── requirements.txt            # Python package dependencies
├── README.md                   # Project documentation
├── .gitignore
└── .venv/                      # Python virtual environment
```

---

## Setup & Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Running the API Backend
```bash
python api.py
# Or with uvicorn:
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```
Check health endpoint: `http://127.0.0.1:8000/api/health`

### Frontend Application
```bash
cd frontend
npm install
npm run dev
```
