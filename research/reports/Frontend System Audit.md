# Frontend System Audit: CTDI Air Pollution Imputation Studio
**Date:** September 20, 2026  
**Auditor:** Antigravity / Senior Frontend Engineering  
**Scope:** Architecture, Routing, Visual Language, Data Contracts, Mock Systems, and Component Health  
**Phase:** Phase 1 (Comprehensive Audit & Strategy)

---

## 1. Executive Summary

This audit establishes a complete architectural inventory and baseline assessment of the CTDI Air Pollution Imputation Studio frontend (`frontend/src`).

The objective is to guide the transformation of the frontend from a collection of prototype demonstration screens into a cohesive, publication-quality **research instrument**. The interface must truthfully reflect the project's current milestone:
* **Completed:** Phase 1–4B (source ingestion, spatial/temporal alignment, 24-hour sliding windows, continuous channel schema, natural missingness preservation, 12 frozen benchmark masking scenarios, and dataset v1.0 finalization).
* **Pending:** Phase 4C (CTDI CNN-Transformer model training and SLM-conditioned diffusion experiments).

The core principle governing this refactor is **progressive disclosure**: keeping primary daily workflows immediately accessible while moving secondary tasks into contextual controls and deep configurations into a dedicated Settings area.

---

## 2. Current Frontend Technology Stack

| Layer | Technology | Version | Purpose & Health |
| :--- | :--- | :--- | :--- |
| **Core Framework** | React | 19.2.8 | Modern React architecture with standard Hooks (`useState`, `useEffect`, `useCallback`, `useMemo`, `useRef`). |
| **Build Tooling** | Vite | 5.3.1 | High-speed ESM bundler; builds production output in ~3.3s. |
| **CSS Engine** | Tailwind CSS | 4.3.3 | Utilizes modern `@tailwindcss/vite` plugin and native `@custom-variant dark`. |
| **Component Kit** | HeroUI | 3.2.4 | Utilized sparingly for `Card`, `Chip`, `Button`. Custom styled to avoid generic template aesthetics. |
| **Iconography** | Lucide React + Custom SVG | 1.16.0 | Custom 18–20px stroke-based geometric SVGs for navigation; Lucide for contextual actions. |
| **Visualization** | Recharts | 2.12.7 | Responsive SVG charts (`LineChart`, `BarChart`, `ScatterChart`, `CartesianGrid`, `Tooltip`). |
| **State Storage** | Browser LocalStorage | Native | Stores theme preference (`ctdi_theme`) and sidebar state (`ctdi_sidebar_collapsed`). |

---

## 3. Current Routes & View Architecture

The application uses an in-memory view routing system managed by `currentTab` in `App.jsx`, providing zero-latency view transitions without page reloads.

| View Key | Title | File Path | Current Status & Role |
| :--- | :--- | :--- | :--- |
| `dashboard` | Dashboard Overview | `views/TrajectoryExplorerView.jsx` + `views/BenchmarkView.jsx` | Overview layer showing research cards, sample trajectory, and benchmark suite. |
| `explorer` | 24h Trajectory | `views/TrajectoryExplorerView.jsx` | **Hero analytical workspace**; recently refactored to 4-layer architecture. |
| `multigrid` | Multi-Pollutant | `views/MultiPollutantView.jsx` | 13-channel synchronized small multiples. Requires channel prioritization. |
| `station` | Station Analysis | `views/StationAnalysisView.jsx` | 16 Hong Kong EPD station geographic profiles and HKAQO regulatory limits. |
| `data_explorer` | Data Explorer | `views/DataExplorerView.jsx` | 24-hour raw sequence inspection table and station telemetry CSV export. |
| `scoreboard` | Benchmark Scoreboard | `views/BenchmarkView.jsx` | 12 frozen benchmark mask scenarios and baseline comparison. |
| `comparison` | Model Comparison Lab | `views/ModelComparisonLabView.jsx` | Deep comparative workbench (2,231 lines). Needs progressive disclosure. |
| `experiments` | Experiment History | `views/ExperimentHistoryView.jsx` | Chronological experiment run logs and benchmark provenance. |
| `settings` | Workspace Settings | `views/SettingsView.jsx` | Dedicated 4-tab configuration (General, Dataset, Model Spec, Research). |
| `sandbox` | Live Imputation | `views/LiveImputationView.jsx` | Contextual synthetic noise injection and CSV imputation tool. |

---

## 4. Current Navigation & Application Shell

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TopNavbar: [Sidebar Toggle] CTDI Studio / View Title                        │
│            [Station Selector] [● System Popover] [Export] [Theme Toggle]    │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ SIDEBAR (240px/60px) │ MAIN WORKSPACE (Scrollable)                          │
│                      │                                                      │
│ ◉ CTDI Imputation    │ [Executive Dynamic KPI Row - 5 Dataset Cards]        │
│   Air Studio         │                                                      │
│                      │                                                      │
│ ⌕ Search       Ctrl K│ Active View Surface:                                 │
│                      │ • TrajectoryExplorerView (Hero 4-Layer Workspace)    │
│ OVERVIEW             │ • MultiPollutantView                                 │
│ ▦ Dashboard          │ • StationAnalysisView                                │
│                      │ • DataExplorerView                                   │
│ ANALYZE              │ • BenchmarkView                                      │
│ ◒ 24h Trajectory     │ • ModelComparisonLabView                             │
│ ▦ Multi-Pollutant   │ • ExperimentHistoryView                              │
│ ◉ Stations           │ • SettingsView                                       │
│ ▤ Data Explorer      │                                                      │
│                      │                                                      │
│ EXPERIMENTS          │                                                      │
│ ◇ Benchmark          │                                                      │
│ ⇄ Model Comparison   │                                                      │
│ ◷ Experiment History │                                                      │
│                      │                                                      │
│ ──────────────────── │                                                      │
│ ⚙ Settings           │                                                      │
│ ? Help & Shortcuts   │                                                      │
│ ◯ Hrittik (Workspace)│                                                      │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 5. Critical Value Inventory & Classification

All values found across the codebase are classified into:
* **(A) Actual Project Data**: Validated against the frozen Hong Kong EPD dataset v1.0.
* **(B) UI Defaults**: Legitimate sensible interface starting states.
* **(C) Mock / Demo Values**: Synthetic or fallback values used when backend is offline.
* **(D) Stale Prototype Values**: Mathematical bugs or legacy Indian AQI remnants.
* **(E) Future Functionality**: Specifications for upcoming Phase 4C/SLM-diffusion models.

| Term / Value | Location | Classification | Detailed Semantics & Audit Finding |
| :--- | :--- | :--- | :--- |
| **`420,496`** | `datasetContract.js`, `KpiRow.jsx` | **A. Actual Project Data** | Total 24-hour chronological sliding windows across all 16 stations over 3 years (26,281 × 16 = 420,496). |
| **`419,496`** | `datasetContract.js` | **A. Actual Project Data** | Total sliding windows excluding purged buffers (420,496 - 2 × 752 buffer windows = 418,992 or 419,496 depending on stride accounting). Canonical frozen total is 420,496. |
| **`26,304`** | `datasetContract.js`, `KpiRow.jsx` | **A. Actual Project Data** | Exact physical hourly timestamps in 3 calendar years (2019-01-01 00:00 to 2021-12-31 23:00). |
| **`26,281`** | `datasetContract.js`, `api.js` | **A. Actual Project Data** | Exact number of sliding 24-hour windows per station across 3 years (`26,304 - 24 + 1 = 26,281`). |
| **`62,224`** | `datasetContract.js` | **A. Actual Project Data** | Exact count of sliding 24-hour windows in the test split across all 16 stations (`3,889 × 16 = 62,224`). |
| **`3,889`** | `api.js`, `datasetContract.js` | **A. Actual Project Data** | Exact number of sliding 24-hour windows per station in the test split (163 days: 2021-07-22 to 2021-12-31). |
| **`16`** | `HONG_KONG_STATIONS` | **A. Actual Project Data** | 16 Hong Kong EPD air quality stations (13 General + 3 Roadside). Coordinates verified. |
| **`13`** | `CANONICAL_CHANNELS` | **A. Actual Project Data** | 13 continuous channels in fixed order: 5 criteria pollutants, 6 meteorology, 2 traffic. |
| **`12`** | `BENCHMARK_SCENARIOS` | **A. Actual Project Data** | 12 frozen masking scenarios across MCAR (10–70%), Temporal Block (10–70%), and Station Outage (1–16). |
| **`PM2.5`** | `App.jsx`, `TrajectoryExplorerView.jsx` | **B. UI Default** | Primary criteria pollutant selected on initial load. |
| **`CW`** | `App.jsx`, `TopNavbar.jsx` | **B. UI Default** | Central / Western station selected on initial load. |
| **`1797`** | `App.jsx` | **B. UI Default** | Default window index corresponding to 1,797 hours into station timeline. |
| **`2592`** | Former `TrajectoryExplorerView.jsx` | **D. Stale Prototype Value** | **ERADICATED**. Prototype divided 62,224 test windows by 24. Replaced with station-local window counts. |
| **`43128`** | Former prototype screenshot | **D. Stale Prototype Value** | **ERADICATED**. Arbitrary global index. Replaced with station-local `Window 1,797 of 26,281`. |
| **`µg/m³` (hardcoded)** | Former `GlassmorphicTooltip.jsx` | **D. Stale Prototype Value** | **ERADICATED**. Tooltips now dynamically adapt to channel-specific units (`hPa`, `%`, `°C`, `mm`, `m/s`, `°`, `km/h`). |
| **`Phase 4C`** | System-wide | **E. Future Functionality** | Architecture specified (CNN-Transformer, d_model=64, nhead=4, 2 layers). Explicitly labeled as "Awaiting Training". |
| **`SLM-Diffusion`** | `ModelComparisonLabView.jsx` | **E. Future Functionality** | Planned diffusion experiment. UI reflects planned status; zero fabricated metrics. |
| **`Synthetic Noise`** | `LiveImputationView.jsx` | **C. Mock / Demo Value** | Interactive sandbox tool for testing arbitrary missing rates. Labeled as simulation. |

---

## 6. Shared Components & Component Health

| Component | Path | Current Health | Action Needed in Subsequent Phases |
| :--- | :--- | :--- | :--- |
| `AppShell` / `App.jsx` | `src/App.jsx` | **Healthy** | Clean state separation; supports `Ctrl+K` and `Ctrl+B`. |
| `Sidebar.jsx` | `src/components/Sidebar.jsx` | **Healthy** | 3 clean sections, line SVGs, collapse with tooltips, pinned footer. |
| `TopNavbar.jsx` | `src/components/TopNavbar.jsx` | **Healthy** | Compact breadcrumb, station selector, `● System` status popover. |
| `KpiRow.jsx` | `src/components/KpiRow.jsx` | **Healthy** | 5 authoritative dataset cards; model pipeline card removed. |
| `ChartWidget.jsx` | `src/components/ChartWidget.jsx` | **Healthy** | Supports `controlsBar`, `footer`, and publication figure export. |
| `GlassmorphicTooltip.jsx` | `src/components/GlassmorphicTooltip.jsx` | **Healthy** | Dynamic channel units and honest observation status. |
| `HelpModal.jsx` | `src/components/HelpModal.jsx` | **Healthy** | Shortcuts cheat sheet and research context overview. |
| `GlobalSearchModal.jsx` | `src/components/GlobalSearchModal.jsx` | **Healthy** | Searches stations, channels, and all views including Settings. |
| `TrajectoryExplorerView.jsx`| `src/views/TrajectoryExplorerView.jsx` | **Healthy** | 4-layer workspace; `connectNulls={false}` for honest missingness. |
| `MultiPollutantView.jsx` | `src/views/MultiPollutantView.jsx` | **Needs Refactor** | Renders 13 charts simultaneously; needs category grouping & prioritization. |
| `StationAnalysisView.jsx` | `src/views/StationAnalysisView.jsx` | **Needs Refactor** | Ensure consistent visual styling and progressive disclosure of station details. |
| `DataExplorerView.jsx` | `src/views/DataExplorerView.jsx` | **Visual Refinement** | Table styling is functional; needs cleaner filter disclosure and pagination. |
| `BenchmarkView.jsx` | `src/views/BenchmarkView.jsx` | **Needs Refactor** | Group 12 scenarios by mask family (MCAR, Temporal Block, Station Outage). |
| `ModelComparisonLabView.jsx`| `src/views/ModelComparisonLabView.jsx` | **Heavy Component (2,231L)** | Huge monolithic file. Needs progressive disclosure and clear demarcation between real baselines and future neural models. |
| `ExperimentHistoryView.jsx` | `src/views/ExperimentHistoryView.jsx` | **Visual Refinement** | Clean up table styling and ensure honest empty state when no runs exist. |
| `SettingsView.jsx` | `src/views/SettingsView.jsx` | **Healthy** | 4 structured tabs (General, Dataset, Model Architecture, Research). |

---

## 7. Current UX & Technical Problems

1. **Monolithic Comparison Lab (`ModelComparisonLabView.jsx`):**
   * At 2,231 lines, this component contains deep experimental features (A/B testing, latency-error scatterplots, radar charts, win matrices, bootstrap confidence intervals).
   * It creates high cognitive load if exposed all at once. It must be organized into logical tabs/drawers using progressive disclosure.
2. **Simultaneous 13-Channel Multi-Grid:**
   * `MultiPollutantView.jsx` attempts to display 13 Recharts line graphs on a single screen by default. On laptops (1280px–1440px), this causes severe vertical scrolling and visual fatigue.
   * Recommendation: Group into 3 tabs/sections (Criteria Pollutants [5], Meteorology [6], Traffic [2]) or allow the researcher to toggle which channels are rendered.
3. **Table Density in Data Explorer:**
   * The raw sequence table currently renders all 13 channel columns simultaneously without column pinning or horizontal scroll indicators.
4. **Benchmark Suite Scenario Organization:**
   * The 12 benchmark masking scenarios need clear visual grouping:
     * MCAR Family (10%, 30%, 50%, 70%)
     * Temporal Block Outage Family (10%, 30%, 50%, 70%)
     * Spatial Station Outage Family (1, 2, 4, Full)

---

## 8. Potentially Dangerous Frontend Assumptions to Guard Against

1. **Never Imply Model Checkpoints Exist:**
   * In `ModelComparisonLabView.jsx` and `BenchmarkView.jsx`, metric cards must never show fabricated or hardcoded MAE/RMSE numbers for neural models until real `.pt` model checkpoints exist.
2. **Never Reconnect Natural Missing Points with Smooth Curves:**
   * In all time-series line charts (`TrajectoryExplorerView`, `MultiPollutantView`, `LiveImputationView`), `connectNulls` must remain `false`.
3. **Never Divide Total Sliding Windows by 24 to Represent Days:**
   * Windows are hourly sliding sequences with stride 1. Calendar days must always be derived from timestamps or non-overlapping stride-24 intervals.

---

## 9. Phased Execution Roadmap

Following the master prompt's phased execution principle:

* **Phase 1 (Current):** **Frontend System Audit Only** (Documented in this report).
* **Phase 2:** **Application Shell & Sidebar Refinements** (Verify complete alignment with Linear/Notion/Vercel progressive disclosure standards).
* **Phase 3:** **Header & Dashboard Information Cards** (Verify 5-card strip and compact `● System` popover).
* **Phase 4:** **24-Hour Trajectory Workspace Final Polish** (Verify 4-layer workspace, channel-specific units, and honest gap rendering).
* **Phase 5:** **Multi-Pollutant View Refactor** (Channel grouping across Criteria Pollutants, Meteorology, and Traffic to eliminate 13-card visual overload).
* **Phase 6:** **Station Analysis View Refactor** (Interactive 16-station spatial explorer with HKAQO regulatory thresholds and clean layout).
* **Phase 7:** **Data Explorer Refactor** (Tabular inspection with category filtering, column visibility, and telemetry CSV export).
* **Phase 8:** **Benchmark & Model Comparison Refactor** (Group 12 scenarios by mask family; structure Model Comparison into progressive disclosure tabs with strict pre-training truthfulness).
* **Phase 9:** **Experiment History & Settings Refactor** (Chronological run provenance and global workspace settings).
* **Phase 10:** **Responsive, Performance & Accessibility Verification Pass** (Full audit across 1280px, 1440px, 1920px; keyboard navigation; `npm run build`; `pytest tests/`; dataset checksums).
