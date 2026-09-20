# Frontend Navigation & Information Architecture Audit
**CTDI Air Pollution Imputation Research Platform**  
**Date:** September 20, 2026  
**Auditor:** Antigravity / Senior Frontend Engineering  
**Scope:** Navigation, Sidebar, Shell, Header, and Workflow Hierarchy  

---

## 1. Executive Summary

The current frontend architecture suffers from typical research-dashboard bloat: every feature, modal, experiment runner, and backend diagnostic flag has been promoted to a top-level visible control. The sidebar exposes 10 navigation items across 4 disjointed sections, the top navbar contains 8 concurrent status chips and selectors, and secondary configuration dialogues (e.g. raw hyperparameter inspection, synthetic sandbox injection) compete directly with daily research exploration workflows.

Applying core UX principles from **Nielsen Norman Group (Progressive Disclosure)** and modern dense workstation applications (**Linear, Notion, Vercel**), this audit establishes a streamlined information hierarchy:
* **Primary Workflows** are permanently visible and effortless to scan.
* **Secondary Workflows** are cleanly grouped under focused domains.
* **Advanced Configurations** are deferred to contextual page actions.
* **Global Configuration & Diagnostics** are consolidated into a dedicated Settings area and a compact, progressive system status popover.

---

## 2. Inventory of Current Routes & Navigation Items

| Current Tab ID | Current Label | Current Section | Component Rendered | Purpose / Category |
| :--- | :--- | :--- | :--- | :--- |
| `dashboard` | Dashboard | OVERVIEW | `TrajectoryExplorerView` + `BenchmarkView` | Landing overview & summary |
| `explorer` | 24h Trajectory | ANALYTICS | `TrajectoryExplorerView` | Primary 24h sequence inspector |
| `multigrid` | Multi-Pollutant Grid | ANALYTICS | `MultiPollutantView` | Small multiples across 13 channels |
| `scoreboard` | Benchmark Scoreboard | ANALYTICS | `BenchmarkView` | 12 frozen mask scenario evaluations |
| `station` | Station Analysis | ANALYTICS | `StationAnalysisView` | 16 Hong Kong EPD station geographic profiles |
| `data_explorer` | Data Explorer | ANALYTICS | `DataExplorerView` | Raw continuous sequence table & CSV export |
| `comparison` | Model Comparison Lab | EXPERIMENTS | `ModelComparisonLabView` | Multi-model benchmark comparison & agreement |
| `sandbox` | Live Imputation | EXPERIMENTS | `LiveImputationView` | Synthetic noise injection & CSV file imputation |
| `experiments` | Experiment History | EXPERIMENTS | `ExperimentHistoryView` | Chronological experiment run logs |
| `model_config` | Model Configuration | SYSTEM | Modal / Tab trigger (`ModelConfigModal`) | Raw PyTorch CNN-Transformer hyperparameters |

---

## 3. Workflow Classification

### 1. Primary Workflows (Always Visible in Navigation)
These represent the core reasons an environmental atmospheric researcher opens the application:
1. **Overview / Dashboard (`dashboard`)**: Unified entry point showing dataset summary, sample trajectory, and baseline protocol.
2. **24h Trajectory (`explorer`)**: Deep continuous sequence exploration across 13 channels and 16 monitoring stations.
3. **Multi-Pollutant Grid (`multigrid`)**: Inter-channel relationship inspection across criteria pollutants, meteorology, and traffic context.
4. **Station Analysis (`station`)**: Spatial distribution, sensor heights, urban/roadside classifications, and HKAQO regulatory limits.
5. **Data Explorer (`data_explorer`)**: Direct inspection of raw sensor readings, natural missingness masks, and split windows.
6. **Benchmark Evaluation (`benchmark` / `scoreboard`)**: Evaluation of imputation models across the 12 frozen benchmark mask scenarios.
7. **Model Comparison (`comparison`)**: Head-to-head performance analysis (MAE, RMSE, Peak error, Model Agreement) between neural models and baselines.
8. **Experiment History (`experiments`)**: Provenance logs of executed benchmark runs on the frozen test partition.

### 2. Secondary Workflows (Grouped & Contextual)
These are important specialized tasks that do not need top-level real estate competing with everyday exploration:
* **Live CSV File Imputation (`sandbox`)**: Relevant when a researcher has an external CSV with sensor dropouts. This belongs as a contextual action inside `DataExplorerView` or `ModelComparisonLabView`, or accessible via a secondary tab/modal.
* **Custom Corruption Sandbox**: Experimenting with synthetic MCAR/Block rates on arbitrary samples. Belongs inside the benchmark/comparison experimentation space.
* **A/B Run Comparison Drawer**: Secondary drawer inside `ModelComparisonLabView`.

### 3. Advanced Configuration (Contextual Actions)
* **Model Hyperparameters Inspection (`ModelConfigModal`)**: Static model architecture definition (1x1 Conv1d + Temporal Transformer Encoder). Belongs under **Settings > Model** or as an inspector button within **Model Comparison**.
* **Benchmark Mask Selection**: Advanced configuration within `BenchmarkView`.
* **Diurnal Peak Zoom & Amplitude Analysis**: Contextual filter toolbar within `ModelComparisonLabView`.

### 4. Utility Actions (Header / Overflow Menus)
* **Global Search (`Ctrl + K`)**: Command palette to jump directly to any of the 16 stations, 13 channels, or 62,224 test windows.
* **Workspace Export**: High-res figure rendering, telemetry CSV, or analysis JSON export.
* **Presentation Mode**: Fullscreen distraction-free display for research reviews.
* **Theme Toggle**: Dark / Light system preference.

### 5. Settings (Dedicated System Area)
* **General**: Theme, sidebar expanded/collapsed preference, UI display density.
* **Dataset Metadata**: Domain information (Hong Kong EPD, 2019–2021, 26,304 hours, 420,496 windows).
* **Model Specification**: Architecture, embedding dimension, attention heads, checkpoint target.
* **System Status & Diagnostics**: FastAPI connectivity, PyTorch device (CPU/CUDA), dataset checksum verification.

---

## 4. Current Navigation Problems & Deficiencies

1. **Information Architecture Fragmentation**:
   * "Benchmark Scoreboard" is categorized under `ANALYTICS`, while "Model Comparison Lab" is under `EXPERIMENTS`, despite both being core model evaluation tasks.
   * "Model Configuration" is an isolated top-level item under `SYSTEM` that merely opens a read-only modal.
   * "Live Imputation" sits at the top level as `sandbox`, despite model training not having commenced yet.
2. **Visual Clutter & Noise in Header**:
   * The top navbar permanently displays: Logo, App Title, Network Chip, Subtitle, Full Search Bar, Station Selector, Model Status Pill, API Status Chip, Export Button, Presentation Button, and Theme Button simultaneously.
   * This leaves almost no room on screens under 1440px, causing severe wrapping collisions.
3. **Redundant Status Badges**:
   * Model status ("Phase 4C: Awaiting Training") is duplicated in the Top Navbar, in the Sidebar Footer, and on the Dashboard.
   * API status ("FastAPI Connected / Offline") permanently occupies header real estate.
4. **Sidebar Lacks Strong Active Hierarchy**:
   * Active state uses large saturated purple blocks (`bg-indigo-600` or `bg-indigo-50`) that draw visual focus away from the workspace.
   * Icons rely on generic colored backgrounds.
5. **No Collapsed Label Access**:
   * In collapsed mode, icons sit alone with basic HTML title attributes, lacking a refined floating tooltip or keyboard focus indicator.

---

## 5. Items to Reorganize & Progressively Disclose

| Item | Current Location | Proposed Destination | Rationale |
| :--- | :--- | :--- | :--- |
| **Model Configuration** | Permanent Sidebar item (`SYSTEM`) | **Settings > Model** + contextual button in Model Comparison | Infrequently modified; read-only architectural spec. |
| **Live Imputation** | Permanent Sidebar item (`EXPERIMENTS`) | Contextual tab in Model Lab & Data Explorer | Niche workflow; requires a trained checkpoint to execute. |
| **FastAPI / Model Badges** | Always visible in Header & Sidebar footer | **Compact System Status Indicator** (`● System`) | Diagnostics should not permanently crowd navigation. |
| **Presentation / Export** | Permanent Header buttons | Breadcrumb / Page Action bar | Clean up global header; keep actions close to data. |
| **Settings & Help** | Scattered / Missing | Pinned bottom utility section in Sidebar | Standard application pattern (Linear/Notion). |

---

## 6. Proposed Target Information Architecture

```
┌───────────────────────────────────────────────┐
│ ◉ CTDI Air Pollution                         │
│   Imputation Studio                           │
│                                               │
│ ⌕ Search                                ⌘K    │
│                                               │
│ OVERVIEW                                      │
│ ▦ Dashboard                                   │
│                                               │
│ ANALYZE                                       │
│ ◒ 24h Trajectory                             │
│ ▦ Multi-Pollutant                            │
│ ◉ Stations                                    │
│ ▤ Data Explorer                              │
│                                               │
│ EXPERIMENTS                                   │
│ ◇ Benchmark                                   │
│ ⇄ Model Comparison                           │
│ ◷ Experiment History                         │
│                                               │
│ ───────────────────────────────────────────── │
│ ⚙ Settings                                    │
│ ? Help                                        │
│                                               │
│ ◯ Hrittik · Research Workspace                │
└───────────────────────────────────────────────┘
```

* **Collapsed Mode (56–64px):** Displays pristine line icons with high-contrast active state indicators and accessible floating tooltips.
* **Header Simplification:** Reduced to:
  `[Sidebar Toggle] [Breadcrumb / Page Title] ── [Station Selector] [● System Status] [Theme]`

---

## 7. Safety Verification & Non-Interference
* **Zero Backend Code Changes:** No modifications to Python files or API endpoints.
* **Zero Dataset Modifications:** All 46 frozen dataset artifacts remain strictly untouched.
* **Preserved Routes:** All existing views (`LiveImputationView`, `ModelConfigModal`, etc.) remain fully accessible via progressive disclosure and direct tabs.
