# Frontend Content & Information Hierarchy Audit
## CTDI Air Pollution Studio

**Audit Execution Date**: 2026-09-20  
**Scope**: Full frontend client codebase (`frontend/src/`)  
**Core Principle**: Product UI = current usable state. Research documentation = methodology + development history + future work.

---

### 1. Pages Inspected
Every primary and secondary view in `frontend/src/views/` was thoroughly inspected:
- **Dashboard (`App.jsx` + embedded components)**: Executive overview, summary KPI row, 24-hour sequence preview, benchmark summary.
- **24h Concentration Trajectory (`TrajectoryExplorerView.jsx`)**: 24-hour hourly curve telemetry, observed vs. missing indicators, curve series controls.
- **Multi-Pollutant Workspace (`MultiPollutantView.jsx`)**: 13-channel small-multiples grid, group selectors (Criteria, Meteorology, Traffic).
- **Station Geographical Profile (`StationAnalysisView.jsx`)**: Hong Kong EPD 16-station network details, coordinates, spatial classification, HKAQO regulatory compliance benchmarks.
- **Data Explorer (`DataExplorerView.jsx`)**: Raw 24-hour tabular telemetry matrix, multi-channel filter presets, row inspection drawer.
- **Benchmark Suite (`BenchmarkView.jsx`)**: 12 controlled missingness scenarios across MCAR, Temporal Block, and Spatial Outage regimes, SHA-256 verification, mathematical metric definitions (MAE, RMSE, MRE).
- **Model Comparison (`ModelComparisonLabView.jsx`)**: Comparative evaluation suite across baseline algorithms and neural models on the frozen Hong Kong EPD test partition.
- **Experiment History (`ExperimentHistoryView.jsx`)**: Historical evaluation logs, run configurations, device environments.
- **Settings (`SettingsView.jsx`)**: Appearance preferences, theme toggles, sidebar persistence, dataset contract inspection, model architecture parameters.

---

### 2. Components Inspected
All shared and layout components in `frontend/src/components/` and UI primitives were inspected:
- `Sidebar.jsx`: Navigation hierarchy, groups, collapsed/expanded states, quick-access utility buttons.
- `TopNavbar.jsx`: Viewport header, station switcher, search/export/help triggers, service & model health status dropdown.
- `KpiRow.jsx`: 5-card dataset and network metric overview cards.
- `ChartWidget.jsx`: Shared Recharts canvas wrapper, interactive controls, high-resolution PNG export canvas generator.
- `ModelConfigModal.jsx`: Architecture specifications and hyperparameter inspector modal.
- `GlobalSearchModal.jsx`: Command palette search indexed by view, channel, and station.
- `HelpModal.jsx`: Keyboard shortcut guide, data glossary, system specs summary.
- `ExportModal.jsx`: CSV and JSON multi-pollutant telemetry exporter.
- `GlassmorphicTooltip.jsx`: Interactive portal-based hover tooltip for Recharts curves.
- `ui/SectionHeading.jsx`: Standardized section header with scroll-depth identity.
- `ui/InfoTooltip.jsx`: Terminology dictionary popover.
- `constants/datasetContract.js`: Canonical dataset schema, station lists, channel taxonomy.
- `constants/terminology.js`: Scientific definitions and caveats.
- `services/api.js`: Centralized client-side API layer and local fallback contracts.

---

### 3. Development-Only Content Removed
Internal project-management labels, phase tracking tags, and development scaffolding were purged across the entire frontend:
- **"Phase 4C" references**:
  - Removed `"Phase 4C Pending"` status badges from `TopNavbar`, `App.jsx`, `HelpModal`, and `ModelConfigModal`.
  - Removed `"Phase 4C Spec"` badges from `ModelComparisonLabView` and `SettingsView`.
  - Removed `"CTDI Imputer (Phase 4C)"` and `"CTDI Transformer (Phase 4C)"` from `App.jsx` curve series and `TrajectoryExplorerView`.
  - Removed `"Phase 4C Pre-Training Baseline"` watermark text from `ChartWidget.jsx` canvas figure generation.
  - Removed internal checkpoint scheduling banner in `SettingsView` (`"Target Checkpoint: checkpoints/ctdi_phase4c/best_model.pt"`, `"Training pipeline is scheduled in Phase 4C"`, `"Phase 4C Scheduled"`).
  - Removed `"Phase 4C architecture:"` prefix from `terminology.js`.
  - Updated `datasetContract.js` model spec version from `"Phase 4C Specification"` to `"CTDI CNN-Transformer v1.0"`.
- **Awaiting / Training status language**:
  - Replaced `"Phase 4C Benchmarking Lab · Awaiting Model Training"` in `ModelComparisonLabView` with product-focused copy: `"Model comparison is unavailable because no trained checkpoints are currently available."`
  - Replaced `"Awaiting Checkpoint"` badge with `"Not Available"`.
  - Replaced `"Awaiting Phase 4C trained model checkpoint..."` and `"Phase 4C Model not trained yet — execution unavailable."` in live simulation steps with clean feedback: `"Preparing model inference..."` and `"Model checkpoint unavailable."`
  - Replaced `"Awaiting Model Training"` and `"Awaiting Benchmark"` in `TrajectoryExplorerView` with `"Unavailable"` and `"Not Evaluated"`.
  - Removed `"upon completion of Phase 4C model training on the Hong Kong EPD dataset"` from `ExperimentHistoryView` empty state.
- **"In Dev" status**:
  - Replaced `"In Dev"` chip in `ModelComparisonLabView` with `"Unavailable"`.

---

### 4. Future-Plan Content Removed
Forward-looking promises and development roadmaps that do not reflect the current usable state of the software were removed:
- Removed `"Imputation Models (Future Phase 4C)"` category title in `TrajectoryExplorerView`; renamed to `"Imputation Models"`.
- Removed `"future"` category taxonomy in `api.js` and `ModelComparisonLabView`; categorized models cleanly under `neural` and `baseline`.
- Cleaned comments referencing future pipelines (e.g. `Future Model Imputations`, `Future SLM Integration`, `future diffusion architecture`).

---

### 5. Redundant Content Removed
- Eliminated redundant badge clutter where both the page title, subheader, and cards were repeating model specification status.
- Removed unused, dead scaffolding props passed into `KpiRow` from `App.jsx` (`modelStatus="Phase 4C Pending"`, `activeModel="CTDI CNN-Transformer (Spec)"`).
- Removed internal local checkpoint filepath (`checkpoints/ctdi_phase4c/best_model.pt`) from general user-facing status footers.

---

### 6. Scientific & User-Relevant Content Retained
All scientific, mathematical, and domain-specific context was strictly preserved:
- **Criteria Air Pollutants**: $\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{NO}_2$, $\text{SO}_2$, $\text{O}_3$ with statutory physical units ($\mu\text{g/m}^3$).
- **Covariates**: 6 Surface Meteorology channels (Pressure, Relative Humidity, Temperature, Precipitation, Wind Direction, Wind Speed) and 2 Traffic context channels (Speed, Congestion).
- **Network Geography**: All 16 Hong Kong EPD monitoring stations (13 general ambient, 3 urban roadside canyons) with exact coordinates, heights, and districts.
- **Evaluation Protocols**:
  - Strict evaluation on artificially masked test cells only (`eval_mask == 1`), zero reward on unobserved ground truth.
  - Mathematical definitions, formulas, and sensitivity properties for MAE ($\mu\text{g/m}^3$), RMSE ($\mu\text{g/m}^3$), and MRE (scale-invariant relative error).
- **Benchmark Regimes**: 12 frozen mask scenarios across MCAR (10%, 30%, 50%, 70%), Temporal Block (10%, 30%, 50%, 70%), and Spatial Outage (1, 2, 4, 16 stations) with reproducible SHA-256 integrity verification.

---

### 7. Pages Where Text Density Was Reduced
- **Model Comparison (`ModelComparisonLabView.jsx`)**: Replaced 4-line developer planning paragraph with a clean 1-line product empty state explaining how to compare available baselines.
- **Settings (`SettingsView.jsx`)**: Eliminated developer checkpoint scheduling banner, leaving only actionable user appearance controls, dataset contracts, and model hyperparameter inspection.
- **Experiment History (`ExperimentHistoryView.jsx`)**: Simplified empty table description from a multi-clause development promise to a concise factual description of what is recorded.
- **Top Navigation Status (`TopNavbar.jsx`)**: Reduced status dropdown text from speculative model training status to concise specification details.

---

### 8. Shared Components Changed
- `TopNavbar.jsx`: Operationalized status popover content.
- `ChartWidget.jsx`: Updated canvas export figure watermark to "Baseline Reference".
- `ModelConfigModal.jsx`: Cleaned version and checkpoint fallbacks.
- `HelpModal.jsx`: Cleaned system summary model status indicator.
- `GlobalSearchModal.jsx`: Standardized view titles.
- `GlassmorphicTooltip.jsx`: Removed roadmap comments.

---

### 9. Functional Behavior Preserved
- Full station selection across all 16 stations intact.
- Multi-pollutant small multiples filtering intact.
- 24-hour sequence stepping, temporal sliding, and date navigation intact.
- CSV upload, synthetic missingness sandbox, and baseline simulations intact.
- Benchmark scenario filtering, detail drawer expansion, and path copy actions intact.
- High-resolution analytical PNG and CSV exports intact.
- Dark/Light theme toggle and sidebar collapse persistence intact.

---

### 10. Files Modified
1. `frontend/src/constants/datasetContract.js`
2. `frontend/src/constants/terminology.js`
3. `frontend/src/services/api.js`
4. `frontend/src/App.jsx`
5. `frontend/src/components/TopNavbar.jsx`
6. `frontend/src/components/ModelConfigModal.jsx`
7. `frontend/src/components/HelpModal.jsx`
8. `frontend/src/components/ChartWidget.jsx`
9. `frontend/src/components/GlassmorphicTooltip.jsx`
10. `frontend/src/components/GlobalSearchModal.jsx`
11. `frontend/src/views/TrajectoryExplorerView.jsx`
12. `frontend/src/views/ModelComparisonLabView.jsx`
13. `frontend/src/views/LiveImputationView.jsx`
14. `frontend/src/views/SettingsView.jsx`
15. `frontend/src/views/ExperimentHistoryView.jsx`
16. `frontend/src/views/DataExplorerView.jsx`

---

### 11. Build & Verification Results
- Executed `npm run build` with Vite v5.4.21.
- Transformation of 4,421 modules completed with **zero errors**.
- Total client JavaScript bundle size decreased from 1,114.10 kB to 1,111.88 kB.
- Global grep searches for `Phase`, `awaiting`, `pending`, `In Dev`, `future`, and `roadmap` across `frontend/src/` returned **0 inappropriate matches**.

---

### 12. Intentionally Retained Content & Scientific Rationale
- **Model Architecture Parameters**: Kept dense hyperparameter inspection table (d_model=64, n_heads=4, num_layers=2, Sinusoidal Positional Encoding) in `SettingsView` and `ModelConfigModal` because it factually describes the structural interface of the CTDI neural model.
- **Statistical Metric Definitions**: Kept MAE, RMSE, and MRE LaTeX equations and property lists in `BenchmarkView` because they allow researchers to interpret physical error units.
- **Frozen Benchmark Scenarios**: Kept all 12 scenario titles, rates, descriptions, and mask file paths in `BenchmarkView` because they define the frozen evaluation protocol.
- **Statutory Limits & Air Chemistry**: Kept HKAQO regulatory limits and roadside vs. urban ambient empirical averages in `StationAnalysisView` because they provide indispensable context for environmental interpretation.
