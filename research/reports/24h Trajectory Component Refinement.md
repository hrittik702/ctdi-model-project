# 24-Hour Trajectory Component Refinement Report
**CTDI Air Pollution Imputation Research Platform**  
**Date:** September 20, 2026  
**Status:** Completed & Fully Verified  
**Component:** 24-Hour Concentration Trajectory / `TrajectoryExplorerView` + `ChartWidget`  
**Engineer:** Antigravity / Senior Frontend Engineering  

---

## 1. Existing Component Structure

Previously, the 24-Hour Trajectory component consisted of `TrajectoryExplorerView.jsx` passing header controls into `ChartWidget.jsx`. The layout suffered from extreme horizontal overcrowding:
* Single-row header cramming Title, Subtitle, 3 pill badges, window stepper, ±24h button, channel dropdown, Curves 3/7 dropdown, 3 zoom buttons, grid toggle, export button, fullscreen toggle, and overflow menu.
* A separate, visually disconnected `MissingnessBar` card below the chart widget.

```
[Previous Architecture - Fragmented & Overcrowded]
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Title  [Pill] [Pill] [Pill] | < #1797 > [±24h] /2592 | [PM2.5] [Curves 3/7] | + - Grid Export [⛶] ⋯│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Smooth curve drawn through actual values (including natural NaNs)                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [Disconnected MissingnessBar Card]                                                     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Problems Found & Data/State Inconsistencies Discovered

1. **The "Window #43128" / "/2592" Mystery Solved:**
   * In the prototype, `sampleIdx` was passed as an arbitrary number up to 62,224 (the total test windows across ALL 16 stations: 3,889 × 16 = 62,224).
   * The prototype then divided `62,224` by 24 (assuming 24 hours in a day), manufacturing `2,592.66` → `2592` pseudo-days.
   * When `sampleIdx` was 43,128, `43128 / 24 = 1797`, displaying `#1797 / 2592` while the title read `Window #43128 (Day 1798)`.
   * **Ground Truth:** For a selected station, there are **26,281 total sliding 24-hour windows** (1,096 calendar days) across the 3-year dataset (2019-01-01 to 2021-12-31), or **3,889 sliding windows** (163 calendar days) in the test split. Dividing multi-station counts by 24 had zero physical meaning.
2. **Scientific Violation in Curve Rendering:**
   * The chart previously rendered `<Line type="monotone" dataKey="actual">`. Because `actual` was continuously connected across natural sensor dropouts, it visually manufactured observations during unobserved periods.
3. **Ambiguous "Curves 3/7" Control:**
   * Listed 7 series, 4 of which were untrained models returning `null`. Users were given dead checkboxes.
4. **Hardcoded Units in Tooltip:**
   * `GlassmorphicTooltip` hardcoded `µg/m³` on every row, labeling Temperature as `°C` with `µg/m³`, Pressure as `hPa` with `µg/m³`, etc.
5. **Model-Centric Clutter:**
   * A large `Model: Awaiting Phase 4C` pill dominated the chart title bar, framing the interface as a defective model runner rather than an active observation workspace.

---

## 3. The New 4-Layer Component Architecture

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: TITLE & CONTEXT                                                 │
│  24-Hour Concentration Trajectory                         [Export]  [⋯]  │
│  MONG KOK · Hong Kong EPD · 17 APR 2021 · 00:00–23:00                  │
│                                                                          │
│ LAYER 2: CONTROLS BAR                                                    │
│  ‹  Window 1,797 / 26,281   ━━━━━●━━━━━   ›  -24h +24h  [PM2.5]  [Series]│
├──────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: HERO 24-HOUR VISUALIZATION                                      │
│                                                                          │
│   µg/m³                                                                  │
│     │                                                                    │
│  28 │                         ●────●                                     │
│     │                     ●───     ──●   (Line breaks across NaNs)       │
│  21 │            ●────●───             ●──●                              │
│     │        ●───                            ──●                         │
│  14 │   ●───              ○  (Hollow dropout)     ●──●                   │
│     │                                                                    │
│   7 │                                                                    │
│     └──────────────────────────────────────────────────────────────       │
│       00:00  04:00  08:00  12:00  16:00  20:00  23:00                    │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│ LAYER 4: SCIENTIFIC LEGEND & OBSERVATION DISTRIBUTION                    │
│  ● Observed (95.8%)  ○ Natural Missing (1 Dropout)  --- Ground Truth     │
│  [■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■]  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Specific Refinements Made

### A. Context & Typography (Layer 1)
* High-legibility title: `24-Hour Concentration Trajectory`.
* Subtitle dynamically derives station, network, date, and 24h range: e.g. `Mong Kok · Hong Kong EPD · 17 Apr 2021 · 00:00–23:00`.
* Eradicated the 4 large pill badges.
* Primary actions (`[Export]` button and `[⋯]` overflow menu) sit quietly at the top-right.

### B. Window Navigation (Layer 2)
* Clear station-local semantics: `Window 1,797 / 26,281` (derived from station's 26,281 sliding windows).
* Eradicated `2592` math error.
* Replaced confusing `±24h` toggle with explicit daily jump buttons `[-24h]` and `[+24h]`.
* Timeline slider directly maps to window index `0` to `26,280`.

### C. 13 Canonical Channels with Dynamic Units
* Dropdown categorizes all 13 canonical channels:
  * Criteria Pollutants: `PM2.5` (`µg/m³`), `PM10` (`µg/m³`), `NO2` (`µg/m³`), `SO2` (`µg/m³`), `O3` (`µg/m³`)
  * Meteorology: `Pressure` (`hPa`), `Relative Humidity` (`%`), `Temperature` (`°C`), `Rainfall` (`mm`), `Wind Direction` (`°`), `Wind Speed` (`m/s`)
  * Traffic: `Traffic Speed` (`km/h`), `Traffic Congestion` (index)
* Y-axis displays channel-specific unit in header; tick labels display clean numbers.
* Tooltip displays channel-specific unit dynamically.

### D. Series Control & Future Model Isolation
* Renamed `Curves 3/7` to `Series · 2`.
* Active toggleable series: `Observed Measurements`, `Natural Missing Dropout`, `Ground Truth Line`.
* Future Phase 4C models (`CTDI Imputer`, `Linear`, `KNN`, `MLP`) are clearly labeled as disabled with `Awaiting Model Training` / `Awaiting Benchmark`.

### E. Scientifically Honest Missingness Rendering (Layer 3)
* `connectNulls={false}` applied to `<Line dataKey="observed">`: the continuous line breaks on unobserved hours.
* Natural missing hours are rendered with distinct hollow circle dots: `○ Natural Missing`.
* Zero synthetic curve smoothing across missing sensor intervals.

### F. Integrated Legend & Timeline Distribution (Layer 4)
* Directly integrated at bottom of workspace card:
  * Legend: `● Observed Measurement`, `○ Natural Missing (Sensor Dropout)`, `--- Ground Truth Baseline`.
  * Observation statistics: `23/24 Hours Observed (95.8%) • 1 Missing Dropout`.
  * High-density 24h segmented bar showing hourly status at a glance.

### G. Publication-Quality Analytical Figure Export
* Canvas PNG generator includes:
  * Brand banner: `CTDI AIR IMPUTATION STUDIO`
  * Subtitle: `Hong Kong EPD Monitoring Network · 16 Stations · 13 Continuous Channels`
  * Figure title: `24-Hour Concentration Trajectory`
  * Metadata context: Station name, dataset name, window index, channel name, and unit
  * Recharts visual plot with line breaks and hollow missing markers
  * Clear legend: Observed vs. Natural Missing vs. Ground Truth
  * Provenance footnote: Timestamp, dataset version, Phase 4C pre-training baseline disclaimer

---

## 5. Files Modified & Intentionally Untouched

### Modified Files:
* [`frontend/src/views/TrajectoryExplorerView.jsx`](file:///home/mocha/Desktop/ctdi-model-project/frontend/src/views/TrajectoryExplorerView.jsx): Full 4-layer workspace refactor.
* [`frontend/src/components/ChartWidget.jsx`](file:///home/mocha/Desktop/ctdi-model-project/frontend/src/components/ChartWidget.jsx): Added `controlsBar` and `footer` slots; upgraded publication figure export.
* [`frontend/src/components/GlassmorphicTooltip.jsx`](file:///home/mocha/Desktop/ctdi-model-project/frontend/src/components/GlassmorphicTooltip.jsx): Dynamic units and observation status.
* [`frontend/src/services/api.js`](file:///home/mocha/Desktop/ctdi-model-project/frontend/src/services/api.js): Corrected station-local window counts (`26,281`) and base epoch mapping (`2019-01-01`).
* [`frontend/src/App.jsx`](file:///home/mocha/Desktop/ctdi-model-project/frontend/src/App.jsx): Updated initial window index to `1797`, updated `totalWindowCount` to `26,281`, and added channel units to `chartData`.

### Intentionally Untouched Files (Zero Changes):
* `data/raw/`, `data/interim/`, `data/final/` (Zero dataset files modified).
* `src/preprocessing/`, `src/models/`, `src/context/`, `src/evaluation/` (Zero Python files modified).
* `tests/` (Zero test modifications; all 23 existing tests run unmodified).

---

## 6. Verification Results

| Check / Test | Command | Result | Status |
| :--- | :--- | :--- | :--- |
| **Vite Bundle Build** | `cd frontend && npm run build` | Built in 3.34s, 0 syntax/type errors | **PASS** |
| **PyTest Suite** | `.venv/bin/pytest tests/` | 23 passed in 10.25s | **PASS** |
| **Dataset Checksums** | `sha256sum -c checksums/SHA256SUMS` | 46/46 files OK | **PASS** |
| **Window Stepper** | `Window 1,797 / 26,281` | Correct station-local window bounds | **PASS** |
| **Channel Units** | Tested all 13 channels | Dynamic units rendered on axis, tooltip, export | **PASS** |
| **Missingness Gaps** | `connectNulls={false}` | Verified line breaks across NaNs | **PASS** |

---

## 7. Explicit Boundary Commitments

* [x] **No model trained**
* [x] **No dataset modified**
* [x] **No preprocessing modified**
* [x] **No model architecture modified**
* [x] **No remote push**
