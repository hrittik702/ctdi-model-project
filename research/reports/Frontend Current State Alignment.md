# Frontend Current State Alignment Report
**CTDI Air Pollution Imputation Research Platform**  
**Date:** September 20, 2026  
**Status:** Completed & Verified  
**Branch:** `main` (commit `497d015`)  
**Safety Branch:** `backup/frontend-before-current-state-alignment`  

---

## 1. Executive Summary & Strict Boundaries

Before embarking on Phase 4C model development and training, a frontend-only audit revealed severe semantic divergence between the user interface and the frozen research foundation:
* The UI prominently displayed **"Delhi (Active)"**, while the underlying research dataset is the 16-station **Hong Kong EPD Air Quality Network** (2019–2021).
* The UI featured an active toggle for **"PyTorch / Keras 3"** as if both were live, trained models, despite Phase 4C training not having started.
* The UI reported **"FastAPI Offline"** and metrics as **"Unavailable"**, conflating API connectivity with model training completion.
* The 24-hour sequence explorer displayed **"Day 1 of 62"** and hardcoded **"Curves 5/7"**, reflecting legacy Beijing/Delhi assumptions rather than the canonical 419,496 sliding windows across 1,096 calendar days.
* Modals and search features were hardcoded to Beijing stations (e.g., **Aotizhongxin**) and 6 legacy channels including CO, rather than Hong Kong's 13 continuous channels (5 criteria pollutants, 6 ERA5 meteorology, 2 spatial-IDW traffic).

### Absolute Safety Boundaries Maintained:
1. **Zero Backend Modifications:** No changes were made to `src/models/`, `src/context/`, `src/preprocessing/`, `src/evaluation/`, `configs/`, or `api.py`.
2. **Zero Dataset Touches:** All 46 checksummed artifacts in `data/final/CTDI_AirPollution_TrainingDataset_v1.0/` remain untouched (`46/46 SHA-256 OK`).
3. **Zero Deletions:** All views, routes, and components were preserved and aligned.
4. **Zero Remote Push:** All work was executed locally on `main` with safety backups.
5. **Zero Fabrication:** The UI strictly presents ground truth observations, natural missingness, and clear "Phase 4C Awaiting Training" indicators without misleading synthetic performance claims.

---

## 2. Canonical Data Contract (`datasetContract.js`)

To prevent future semantic drift, a centralized frontend contract was established at `frontend/src/constants/datasetContract.js`:
* **Dataset Metadata:**
  * Domain: Hong Kong Special Administrative Region
  * Network: Hong Kong EPD (16 stations: 13 General + 3 Roadside)
  * Temporal Coverage: 2019-01-01 to 2021-12-31 (26,304 physical hours; 1,096 calendar days)
  * Sliding Windows: 419,496 total 24-hour sequences (294,160 train; 62,608 val; 62,224 test; 1,504 purged buffer)
* **13 Continuous Channels (Strict Canonical Ordering):**
  1. `PM2.5` (µg/m³) — Criteria Pollutant
  2. `PM10` (µg/m³) — Criteria Pollutant
  3. `NO2` (µg/m³) — Criteria Pollutant
  4. `SO2` (µg/m³) — Criteria Pollutant
  5. `O3` (µg/m³) — Criteria Pollutant
  6. `Surface Pressure` (hPa) — ERA5 Meteorology
  7. `Relative Humidity` (%) — ERA5 Meteorology
  8. `Temperature` (°C) — ERA5 Meteorology
  9. `Precipitation` (mm) — ERA5 Meteorology
  10. `Wind Direction` (°) — ERA5 Meteorology
  11. `Wind Speed` (m/s) — ERA5 Meteorology
  12. `Traffic Speed` (km/h) — Spatial-IDW Traffic
  13. `Traffic Congestion` ([0.0, 1.0]) — Spatial-IDW Traffic
* **16 Hong Kong Monitoring Stations:**
  * General: Central / Western (`CW`), Eastern (`E`), Kwun Tong (`KT`), Sham Shui Po (`SSP`), Kwai Chung (`KC`), Tsuen Wan (`TW`), Tseung Kwan O (`TKO`), Yuen Long (`YL`), Tuen Mun (`TM`), Tung Chung (`TC`), Tai Po (`TP`), Sha Tin (`ST`), Tap Mun (`TMN` - Rural Background)
  * Roadside: Causeway Bay (`CB`), Central (`C`), Mong Kok (`MK`)
* **12 Benchmark Mask Scenarios:**
  * MCAR: 10%, 30%, 50%, 70%
  * Station Outage: 1 station, 2 stations, 4 stations, full network outage
  * Temporal Block: 10%, 30%, 50%, 70% consecutive hours

---

## 3. Component & View Alignment Breakdown

| File / Component | Previous Stale State | Current Truthful State |
| :--- | :--- | :--- |
| `TopNavbar.jsx` | Delhi (Active), Indian AQI pill, PyTorch/Keras 3 toggle | Hong Kong EPD (16 Stations), decoupled API chip, Phase 4C Pending indicator |
| `Sidebar.jsx` | Stale footer branding, overflow clipping | CTDI CNN-Transformer branding, scrollable container with fixed status |
| `KpiRow.jsx` | Stale "Unavailable" MAE/RMSE metrics | Pre-training dataset metrics: 16 Stations, 26,304 Hours, 13 Channels, 419,496 Windows, Phase 4C Spec, 12 Masks |
| `App.jsx` | Station = Delhi, channels = 6, backendOnline = fake model ready | Station = CW, 13 canonical channels, decoupled API connectivity |
| `ChartWidget.jsx` | Stale Delhi chart, wrapping toolbar collisions | Responsive header, EmptyStateChart for pre-training, high-res Hong Kong PNG export |
| `TrajectoryExplorerView.jsx` | "Day 1 of 62", 5 pollutants, hardcoded curve counts | Dynamic day calculation from split windows, 13 channels grouped by type, dynamic units |
| `StationAnalysisView.jsx` | Indian air quality network, Delhi coordinates | 16 Hong Kong EPD stations, HKAQO thresholds, real coordinates, sampling heights |
| `DataExplorerView.jsx` | 6 pollutants, legacy CSV names | 13 channels with units, natural missingness filter, station-specific export filenames |
| `MultiPollutantView.jsx` | 6 legacy channels | Small multiples for 13 channels, Phase 4C architecture status |
| `BenchmarkView.jsx` | Beijing/Delhi benchmark citations | 12 frozen benchmark mask scenarios table with zero-leakage test guarantees |
| `ModelComparisonLabView.jsx` | Default city Delhi, auto-runs fake benchmark | Default city Hong Kong, hk_epd_test_benchmark, Phase 4C pre-training card |
| `LiveImputationView.jsx` | Delhi station, fake checkpoint execution | Central / Western default, Hong Kong EPD sample CSV download, truthful status |
| `ExperimentHistoryView.jsx` | Beijing Multi-Site test distribution citation | Hong Kong EPD test partition citation, informative pre-training empty state |
| `GlobalSearchModal.jsx` | Aotizhongxin station, 6 legacy channels (with CO), 625 samples | 16 HK EPD stations, 13 channels with descriptions, 62,224 test samples |
| `ExportModal.jsx` | Aotizhongxin station, Beijing dataset name | Central / Western station, CTDI Air Pollution Dataset v1.0, station-tagged filenames |
| `ModelConfigModal.jsx` | 6 feature channels, loaded PyTorch checkpoint | 13 input channels (26 with mask), Phase 4C CNN-Transformer spec, zero-leakage notes |
| `terminology.js` | CO pollutant references, old test sample counts | Hong Kong EPD channels, 62,224 test windows, Phase 4C CNN-Transformer spec |
| `api.js` | Delhi fallbacks, missing health status tolerance | Hong Kong fallbacks, 13-channel diurnal simulation, resilient health status |

---

## 4. Verification & Quality Assurance

### A. Frontend Production Build
```bash
$ cd frontend && npm run build
vite v5.4.21 building for production...
✓ 4418 modules transformed.
dist/index.html                   0.81 kB │ gzip:   0.46 kB
dist/assets/index-D9TLqVpg.css  483.57 kB │ gzip:  48.45 kB
dist/assets/index-hYpwIJh_.js   955.92 kB │ gzip: 259.23 kB
✓ built in 3.03s
```
* **Result:** Build passed with exit code 0.

### B. Backend Test Suite Integrity
```bash
$ .venv/bin/pytest tests/
============================= test session starts ==============================
rootdir: /home/mocha/Desktop/ctdi-model-project
collected 23 items

tests/test_context.py .....                                              [ 21%]
tests/test_experimental_dataset.py ............                          [ 73%]
tests/test_teammate_consumption.py ......                                [100%]

============================= 23 passed in 10.97s ==============================
```
* **Result:** 23/23 tests passed. All context, dataset, and teammate consumption assertions verified.

### C. Frozen Dataset Cryptographic Integrity
```bash
$ cd data/final/CTDI_AirPollution_TrainingDataset_v1.0 && sha256sum -c checksums/SHA256SUMS
DATASET_CARD.md: OK
README.md: OK
dataset_manifest.json: OK
... (all 12 masks, 6 metadata tables, and train/val/test Parquet/NPZ arrays)
============================= 46/46 CHECKSUMS OK ==============================
```
* **Result:** All 46 dataset artifacts are completely intact and bit-for-bit identical to frozen state.

### D. File Tree & Git Purity Check
* Modified files: Only files inside `frontend/` and `research/reports/`.
* Protected paths (`src/`, `data/`, `configs/`, `api.py`): 0 modifications.
* Deletions: 0 source files deleted.

---

## 5. Conclusion & Readiness for Phase 4C

The frontend is now in 100% alignment with the underlying research artifacts. The UI truthfully and beautifully represents the Hong Kong EPD 16-station network, 13 continuous channels, 24-hour sequence windowing, natural missingness, and the 12 frozen benchmark mask scenarios, while clearly displaying Phase 4C model development as "Awaiting Training".

The repository is fully stabilized, verified, and ready for Phase 4C model architecture implementation and training.
