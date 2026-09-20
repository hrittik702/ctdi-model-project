# Frontend Current State Audit Report

**Project**: CTDI Air Pollution Imputation & Spatiotemporal Modeling  
**Date**: 2026-09-20  
**Branch Baseline**: `main` (`497d015ce5296c26a6a484be2edf1260b142a00e`)  
**Scope**: Complete audit of `frontend/` architecture, components, routes, data contracts, and visual states prior to Phase 4C model development.  
**Rule Compliance**: Read-only audit; zero frontend modifications made during this phase.

---

## 1. Executive Summary

This audit investigates the entire `frontend/` directory (React 19, Tailwind CSS v4, Vite 5, Recharts, HeroUI) against the current canonical repository state on the `main` branch.

### Core Audit Finding:
The frontend currently carries **severe cognitive dissonance** between the frontend UI surface and the actual research repository state:
1. **Domain Mismatch**: The UI displays **"Delhi (Active)"** and cites the **"Indian National Air Quality Network (CPCB)"** with 29 stations, whereas the current canonical frozen dataset is the **Hong Kong EPD 16-station network (2019–2021)**.
2. **Framework & Model Mismatch**: The top navigation prominently displays a toggle between **"PyTorch"** and **"Keras 3"** as if both were active production backends for Delhi, when in fact Phase 4C model architecture implementation has **not started yet**.
3. **Misleading Offline vs. Untrained State**: An unstarted backend or missing endpoints causes the badge **"FastAPI Offline"** to appear in red, while metric cards display "Unavailable". This misleads users into believing an infrastructure or API server outage is responsible, rather than the truthful state: **Phase 4C model training has not yet occurred**.
4. **Hardcoded Legacy Assumptions**:
   - The Trajectory Explorer displays **"Day 1 of 62"** because a default `maxSamples = 1500` is divided by 24 ($1500 / 24 = 62.5 \rightarrow 62$). The canonical frozen dataset contains **419,496 windows** ($26,304$ physical hours).
   - The curve selector displays **"Curves 5/7"** reflecting 7 hardcoded curves (`groundTruth`, `observed`, `hiddenTarget`, `transformer`, `linear`, `knn`, `mlp`), 5 of which are active by default even though none of the 4 model curves have any trained checkpoints.
   - Channel lists in search modals and configs hardcode 6 legacy pollutants (`PM2.5, PM10, SO2, NO2, CO, O3`) and cite Beijing station **"Aotizhongxin"**, conflicting directly with the canonical **13 continuous channels** (`pm25, pm10, no2, so2, o3, pressure, relative_humidity, temperature, rainfall, wind_direction, wind_speed, traffic_speed, traffic_congestion`).
5. **Empty Chart Behavior**: When no inference data is returned by the backend, Recharts renders a blank, unexplained rectangle without communicating why data or imputation is absent.
6. **UI Layout Collisions**: In smaller viewports ($< 1440$px), the chart header toolbar buttons (window stepper, pollutant selector, curves dropdown, zoom controls, export button) wrap and collide with the chart title and status chips.

---

## 2. Frontend Architecture & Technology Stack

- **Framework**: React 19 (`19.2.8`) with Vite (`5.3.1`)
- **Styling**: Tailwind CSS v4 (`@tailwindcss/vite 4.3.3`) + HeroUI (`@heroui/react 3.2.4`)
- **Charting**: Recharts (`2.12.7`)
- **Iconography**: Lucide React (`1.16.0`) + Custom SVG registry (`ProjectIcon.jsx`)
- **Build Status**: `npm run build` succeeds in 3.3s with bundle size 945 kB JS / 480 kB CSS.
- **Routing**: Single-Page Tab Router managed in `App.jsx` (`currentTab` state), without external `react-router-dom` dependency.

---

## 3. View & Route Inventory

The application provides 8 active views and 3 modal dialogs:

| View ID | Title / Label | File Path | Current Stale Assumptions | Role in Canonical Project |
|:---|:---|:---|:---|:---|
| `dashboard` | Dashboard Overview | Composed in `App.jsx` (Trajectory + Benchmark) | Shows empty charts, "FastAPI Offline", 62 days, 5/7 curves | Executive overview of 16 HK stations & dataset readiness |
| `explorer` | 24h Trajectory Explorer | `views/TrajectoryExplorerView.jsx` | Hardcoded `maxSamples=1500` ("Day 1 of 62"), assumes 5/7 curves | Visualizes 24h observed sequence across 13 HK channels |
| `multigrid` | Multi-Pollutant Grid | `views/MultiPollutantView.jsx` | Hardcodes 5 pollutants (`PM2.5, PM10, NO2, SO2, O3`) | Small-multiples view across all 13 canonical channels |
| `scoreboard` | Benchmark Scoreboard | `views/BenchmarkView.jsx` | Expects active model MAE/RMSE; empty state says "loading..." | Exposes 12 real benchmark mask scenarios (MCAR, Outage, Block) |
| `station` | Station Geographical Profile| `views/StationAnalysisView.jsx` | "Indian National Air Quality Network (CPCB) • 29 stations" | 16 Hong Kong EPD stations with true coordinates |
| `data_explorer`| Data Explorer | `views/DataExplorerView.jsx` | Cites "Aotizhongxin" (Beijing) & "6 monitoring channels" | Tabular telemetry browser across 13 HK channels |
| `comparison` | Model Comparison Lab | `views/ModelComparisonLabView.jsx` | City="Delhi", dataset="delhi_test_benchmark", models="delhi_ctdi_*"| Framework preserved for Phase 4C post-training benchmarks |
| `sandbox` | Live Imputation Workspace | `views/LiveImputationView.jsx` | Checkpoint="checkpoints/delhi/...", "Download Sample Delhi CSV" | Standby interface for live forward pass once model trained |
| `experiments`| Experiment History | `views/ExperimentHistoryView.jsx` | "Beijing Multi-Site Air Quality test distribution" | Preserved log table for post-training experiment tracking |
| *(Modal)* | Global Search Modal | `components/GlobalSearchModal.jsx` | Includes "CO", "Aotizhongxin" station at 39.982° N | Global jump palette for HK stations, 13 channels, and views |
| *(Modal)* | Export Modal | `components/ExportModal.jsx` | Station defaults to "Aotizhongxin", dataset "Beijing" | Exports analytical publication figures with HK metadata |
| *(Modal)* | Model Architecture Modal | `components/ModelConfigModal.jsx` | Hardcodes "6 Pollutants (PM2.5..CO, O3)", "checkpoints/transformer/.."| Displays Phase 4C CNN-Transformer architecture specification |

---

## 4. API Dependency & Contract Audit

### 4.1 Backend Service Analysis (`api.py` vs `frontend/src/services/api.js`)

| Frontend API Method | Target Backend Endpoint | Implemented in `api.py`? | Current Behavior |
|:---|:---|:---:|:---|
| `api.getHealth()` | `GET /api/health` | **YES** (`{"status": "healthy"}`) | Frontend checks `health.status === 'ok'`, fails because API returns `"healthy"`. |
| `api.getStations()` | `GET /api/stations` | **NO** (404) | Fails, causes `Promise.all` in `App.jsx` to reject. |
| `api.getMetadata()` | `GET /api/metadata` | **NO** (404) | Fails, causes `Promise.all` to reject. |
| `api.getMetrics()` | `GET /api/metrics` | **NO** (404) | Fails, causes `Promise.all` to reject. |
| `api.getPollutantMetrics()`| `GET /api/metrics/pollutants` | **NO** (404) | Fails, causes `Promise.all` to reject. |
| `api.getSample(sampleIdx)` | `GET /api/samples/{idx}` | **NO** (404) | Fails, results in `sampleData = null` (blank chart). |
| `api.getModelConfig()` | `GET /api/model/config` | **NO** (404) | Fails, causes `Promise.all` to reject. |
| `api.getExperiments()` | `GET /api/experiments` | **NO** (404) | Fails, causes `Promise.all` to reject. |
| `api.liveImpute()` | `POST /api/impute` | **NO** (404) | Cannot execute without trained model. |
| `api.getComparisonModels()` | `GET /api/comparison/models`| **NO** (404) | Cannot execute without trained model. |

### 4.2 Impact of Current Architecture
In `App.jsx` (lines 119–148):
```javascript
const [health, stnsRes, meta, metList, polMets, exps, config] = await Promise.all([
  api.getHealth(initialStation),
  api.getStations(),
  api.getMetadata(initialStation),
  api.getMetrics(initialStation),
  api.getPollutantMetrics(initialStation),
  api.getExperiments(),
  api.getModelConfig(initialStation)
]);
```
Because 6 of these 7 endpoints do not exist in `api.py`, the entire `Promise.all` throws an exception on app load. As a consequence:
- `setBackendOnline(false)` is triggered even when FastAPI is actively running.
- All state variables (`stations`, `metadata`, `metrics`, `pollutantMetrics`) remain empty/null.
- The UI falls back to hardcoded defaults ("Delhi", "CPCB", empty charts).

---

## 5. Audit of Stale Assumptions & Legacy Fragments

### 5.1 "Delhi" and "Indian AQI Network" References
- **`TopNavbar.jsx`**:
  - Line 49: Chip reads `"Indian AQI Network"`.
  - Line 8: `currentStation = 'Delhi'`.
  - Line 87: Title attribute: `"Select Indian Monitoring Station"`.
  - Lines 106–134: Hardcoded pill toggle for `PyTorch` vs `Keras 3` when `currentStation === 'Delhi'`.
- **`App.jsx`**:
  - Lines 46–47: Default state `selectedStation = 'Delhi'`, `activeModel = 'delhi_ctdi_original'`.
  - Line 240: `selectedStation.toLowerCase().includes('keras') ? 'Keras 3' : 'PyTorch'`.
  - Lines 526–527: Default export station `'Delhi'`, dataset `'Indian National Air Quality Dataset (CPCB)'`.
- **`StationAnalysisView.jsx`**:
  - Line 72: Header `"Indian National Air Quality Network (CPCB)"`.
  - Line 75: `"29 continuous hourly monitoring stations across India"`.
  - Line 35: `isModelTrained = (stationName.toLowerCase() === 'delhi')`.
  - Lines 38–42: CPCB / Indian NAAQS thresholds (e.g. 60 µg/m³ for PM2.5).
- **`ChartWidget.jsx`**:
  - Line 21: `station = 'Delhi Monitoring Station (28.614° N, 77.209° E)'`.
  - Line 22: `dataset = 'Indian National Air Quality Dataset (CPCB)'`.
- **`LiveImputationView.jsx`**:
  - Line 49: `checkpoint = 'checkpoints/delhi/best_temporal_transformer.pt'`.
  - Line 319: Button `"Download Sample Delhi CSV"`.
- **`ModelComparisonLabView.jsx`**:
  - Lines 83–86: `selectedCity = 'Delhi'`, `selectedDataset = 'delhi_test_benchmark'`.
  - Lines 88–89: `delhi_ctdi_original`, `delhi_ctdi_keras`.

### 5.2 "Beijing" & "Aotizhongxin" Fragments
- **`DataExplorerView.jsx`** (Line 54): `a.download = 'Station_Aotizhongxin_Sample_${sampleIdx}_24h_telemetry.csv'`.
- **`ExportModal.jsx`** (Lines 10–11): `station = 'Aotizhongxin'`, `dataset = 'Beijing Multi-Site Air Quality Dataset'`.
- **`GlobalSearchModal.jsx`** (Lines 66–68): Search entry for `"Aotizhongxin Monitoring Station (39.982° N, 116.397° E)"`.
- **`ExperimentHistoryView.jsx`** (Line 18): Subtitle references `"Beijing Multi-Site Air Quality test distribution"`.

### 5.3 Stale Channel Schema (6 channels vs 13 canonical channels)
- `GlobalSearchModal.jsx` hardcodes: `['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']` (includes CO, which is NOT in the Hong Kong dataset).
- `ModelConfigModal.jsx` cites: `"Input Feature Channels: 6 Pollutants (PM2.5, PM10, SO2, NO2, CO, O3)"`.
- Canonical channel list from `data/final/CTDI_AirPollution_TrainingDataset_v1.0/metadata/channel_schema.csv`:
  0. `pm25` (PM2.5, µg/m³)
  1. `pm10` (PM10, µg/m³)
  2. `no2` (NO2, µg/m³)
  3. `so2` (SO2, µg/m³)
  4. `o3` (O3, µg/m³)
  5. `pressure` (Surface Pressure, hPa)
  6. `relative_humidity` (Relative Humidity, %)
  7. `temperature` (Air Temperature, °C)
  8. `rainfall` (Hourly Rainfall, mm)
  9. `wind_direction` (Wind Bearing, °)
  10. `wind_speed` (Wind Speed, m/s)
  11. `traffic_speed` (Traffic Speed, km/h)
  12. `traffic_congestion` (Traffic Congestion, [0, 1])

### 5.4 Stale Trajectory Window Accounting ("Day 1 of 62")
- In `TrajectoryExplorerView.jsx` (lines 115–119):
  `const totalDays = Math.floor(maxSamples / 24); // 62 days`
  Because `maxSamples` defaults to 1500, `1500 / 24 = 62.5 \rightarrow 62`.
- The actual dataset contains:
  - 419,496 total 24-hour sliding windows (Train: 294,160, Val: 62,608, Test: 62,224).
  - 26,304 consecutive hours per station (1,096 calendar days across 2019–2021).

### 5.5 Stale Model Curves ("Curves 5/7")
- In `App.jsx` (lines 62–70, 295–303):
  `curveSeries` contains 7 models: `groundTruth`, `observed`, `hiddenTarget`, `transformer`, `linear`, `knn`, `mlp`.
  Default active: 5 curves (`groundTruth`, `observed`, `hiddenTarget`, `transformer`, `linear`).
  This creates the indicator `Curves 5/7`.
- Because neither CTDI Transformer nor KNN/MLP/Linear have been run or evaluated for Phase 4C, 4 of these 5 curves have zero values, leading to confusing blank line plots.

---

## 6. UI Bugs & Visual Deficiencies

### Bug 1: Icon/Text Collisions in Compact Cards
- In `TopNavbar.jsx`, `KpiRow.jsx`, and `Sidebar.jsx`, text containers lack `min-w-0` and icons lack `shrink-0`.
- In narrow viewports, text overflows and pushes icon elements out of visual bounds or shrinks SVG dimensions.

### Bug 2: Chart Toolbar Collisions
- In `TrajectoryExplorerView.jsx` and `ChartWidget.jsx`:
  The chart header places the title, badges, window stepper, pollutant selector, curves dropdown, zoom controls, grid toggle, export button, and more menu in a single flex container.
  On viewports between 1024px and 1440px, the controls wrap unpredictably and collide directly with the title and badges.

### Bug 3: Empty Chart Black Hole
- When `sampleData` is `null` or when model imputation is unavailable:
  The `ChartWidget` renders an empty Recharts container with blank axes. There is no empty state explaining:
  - Is the dataset missing?
  - Is the API offline?
  - Is the model simply not trained yet?
- Users see a giant empty rectangle with confusing "Unavailable" badges.

### Bug 4: Inconsistent Scientific Export
- In `ExportModal.jsx` and `ChartWidget.jsx`:
  Canvas PNG export currently hardcodes Delhi/Beijing labels.
  Exporting while in "model not trained" state generates a figure with fake/blank curve legends rather than an honest "Dataset Observation Only" export.

---

## 7. Recommended Solution Architecture (Phased Plan)

To bring the frontend into 100% alignment with the canonical repository without modifying the backend or dataset:

### Step 1: Create Frontend Canonical Project Contract (`frontend/src/constants/datasetContract.js`)
- Store authoritative metadata directly in the frontend:
  - 16 Hong Kong EPD stations (IDs, codes, names, coordinates, types, districts).
  - 13 canonical channels (indices, IDs, display names, units, categories, Z-score statistics).
  - Chronological splits (2019–2021, window counts: 294,160 train, 62,608 val, 62,224 test).
  - 12 benchmark mask scenarios (MCAR, Station Outage, Temporal Block).
- Decouple frontend rendering from runtime API failures: the frontend will always be able to display genuine dataset geometry, channels, and statistics.

### Step 2: Implement Explicit System & Model Lifecycle States
- Replace ambiguous booleans (`backendOnline`, `isOnline`) with clean decoupled states:
  - `API_STATUS`: `ONLINE` (FastAPI connected) vs `OFFLINE` (service down).
  - `MODEL_STATUS`: `NOT_TRAINED` (Phase 4C pending) vs `TRAINED` vs `INFERENCE_AVAILABLE`.
  - `DATASET_STATUS`: `AVAILABLE` (CTDI Air Pollution Training Dataset v1.0).
- Update the top navigation and sidebar to show:
  - Location: **"Hong Kong · 16 Stations"**
  - Model: **"Phase 4C · Awaiting Training"**
  - Backend: **"FastAPI Connected"** (or **"Offline"**)

### Step 3: Align KPI Row & Dashboard
- Redesign KPI cards to reflect currently verifiable project metrics:
  1. **Dataset**: 16 Stations (Hong Kong EPD)
  2. **Temporal Coverage**: 26,304 Hours (2019–2021)
  3. **Feature Channels**: 13 Synchronized Channels
  4. **Window Corpus**: 419,496 Windows (24h)
  5. **Model Status**: Awaiting Phase 4C Training
  6. **Benchmark Masks**: 12 Evaluation Scenarios

### Step 4: Fix 24-Hour Trajectory Explorer
- Remove `"Day 1 of 62"`: compute day and window denominators from actual split sizes (e.g. 62,224 test windows / 2,592 days).
- Support all 13 channels in the selector (PM2.5, PM10, NO2, SO2, O3, Pressure, Humidity, Temperature, Rainfall, Wind Dir, Wind Speed, Traffic Speed, Traffic Congestion).
- Differentiate curve modes:
  - **Dataset Mode** (Active): Shows Observed Points + Natural Missing regions.
  - **Imputation Mode** (Pending Phase 4C): Shows Model Imputed curves only when trained checkpoint exists.

### Step 5: Fix Empty Chart State & UI Collisions
- Add a dedicated `<EmptyStateChart>` in `ChartWidget` with clear, informative scientific messaging.
- Refactor the toolbar layout in `ChartWidget` with responsive wrapping, fixed button sizing, and proper z-index layering.

### Step 6: Update Station Analysis, Data Explorer, & Modals
- Replace Indian CPCB station selector with the 16 Hong Kong EPD stations and coordinates.
- Update Data Explorer to show 13 channels instead of 6.
- Update Export Modal and ChartWidget PNG export to brand figures with the Hong Kong EPD dataset identity.

---

## 8. Safety & Integrity Confirmation

- **Zero backend modifications**: No changes to `api.py`, `src/`, or `configs/`.
- **Zero dataset modifications**: No changes to `data/`.
- **Zero model modifications**: No changes to `src/models/` or checkpoint files.
- **Zero deletions**: All components, views, and routes are preserved and clarified.
