# 24-Hour Trajectory Component Audit
**CTDI Air Pollution Imputation Research Platform**  
**Date:** September 20, 2026  
**Component:** 24-Hour Concentration Trajectory / `TrajectoryExplorerView` + `ChartWidget`  
**Auditor:** Antigravity / Senior Frontend Engineering  

---

## 1. Executive Summary

The 24-Hour Trajectory visualization is the central analytical workspace of the CTDI Air Pollution Studio. Researchers use it to inspect diurnal air quality cycles, evaluate temporal missingness patterns across 16 monitoring stations and 13 continuous channels, and will soon use it to evaluate Phase 4C imputation reconstructions.

However, the existing implementation suffers from critical design and data discrepancies:
1. **Toolbar Overcrowding:** The chart header attempts to host 11 disparate items on a single horizontal row (Title, Subtitle, 3 large pill badges, window stepper, ±24h toggle, channel dropdown, Curves 3/7 dropdown, 3 zoom buttons, grid toggle, export button, fullscreen toggle, overflow menu).
2. **Invalid & Confused Metrics ("Window #43128" alongside "/2592"):** The prototype divided global test-set window counts across 16 stations by 24, manufacturing an artificial `2592` "days" denominator and displaying `#1797 / 2592` while the title read `Window #43128 (Day 1798)`.
3. **Scientific Inaccuracy in Curve Rendering:** The chart rendered a continuous smooth curve through natural missing intervals using `type="monotone"` on `actual`, giving the false visual impression that unobserved periods had measurements.
4. **Ambiguous Series Control ("Curves 3/7"):** The dropdown listed 7 series—4 of which are untrained models returning `null`—giving users clickable options that had no effect.
5. **Hardcoded Units in Tooltips:** The tooltip hardcoded `µg/m³` for all 13 channels, incorrectly labeling Temperature, Humidity, Pressure, Wind Speed, and Traffic.
6. **Model-Centric Clutter in an Observation Workspace:** A large `Model: Awaiting Phase 4C` pill dominated the chart header, treating the workspace as a broken model evaluator rather than a functional 24-hour observation analysis platform.

---

## 2. Component Inventory & Data Flow

```
frontend/src/App.jsx
  │
  ├── sampleIdx (number, 0..N)
  ├── selectedStation (e.g. 'CW', 'MK')
  ├── targetPollutant (e.g. 'PM2.5')
  ├── api.getSample(sampleIdx, selectedStation)
  │     └── returns: { sample_idx, station, hours: [0..23], timestamps, pollutants: { [channel]: { actual, observed_mask, eval_mask, transformer: null, ... } } }
  │
  └── TrajectoryExplorerView.jsx
        │
        ├── headerControls (stepper, ±24h button, pollutant select, curves select)
        └── ChartWidget.jsx
              │
              ├── Header: title, subtitle, badges (Pills)
              ├── Actions: headerControls + zoom buttons + grid toggle + export + fullscreen + more
              └── Body: Recharts <LineChart>
                    ├── CartesianGrid
                    ├── XAxis (hours 0..23)
                    ├── YAxis (channelUnit)
                    ├── Tooltip (GlassmorphicTooltip)
                    └── Lines (Ground Truth, Observed, HiddenTarget, Transformer, Linear, KNN, MLP)
```

---

## 3. Critical Value Investigation & Truth Table

| Value / Label | Screenshot / Prototype State | Actual Frozen Dataset State | Classification | Root Cause & Resolution |
| :--- | :--- | :--- | :--- | :--- |
| **`43128`** | `Window #43128` | Window ID 43,128 in full dataset belongs to Tai Po (station 69, windows 26,281–52,561). | **Stale Prototype State** | Prototype passed an arbitrary global window index into a station-scoped view. Resolution: Use station-local window index (0 to 26,280 for full 3-year timeline, or 0 to 3,888 for test benchmark split). |
| **`2592`** | `/#1797 ... /2592` | 62,224 test windows across 16 stations divided by 24 = 2592.66. | **Math / Semantics Error** | Prototype divided multi-station window counts by 24 assuming hours-in-a-day. Resolution: Eradicate 2592. Single station has **26,281 total windows** (1,096 days) or **3,889 test windows** (163 days). |
| **`Day 1798`** | `Window #43128 (Day 1798 of 2592)` | 43,128 / 24 = 1,797 days. 1,797 days from 2019-01-01 is in 2023, past dataset boundary. | **Stale Calculation** | Result of dividing arbitrary global window index by 24. Resolution: Derive actual calendar date and time from the window's starting timestamp (`17 Apr 2021 · 00:00–23:00`). |
| **`Curves 3/7`** | `Curves 3/7` | 3 active models out of 7 listed (Ground Truth, Observed, HiddenTarget). 4 models untrained (`null`). | **Ambiguous UI State** | Label "Curves 3/7" fails to explain 3 of 7 what. 4 checkboxes are dead controls. Resolution: Rename to `Series` / `Series · 2`. Only enable series with existing data; disable future models with clear explanation. |
| **`±24h`** | Button `±24h` | Toggled `stepHours` between 24 and 1. | **Confusing Interaction** | Looked like a static badge or confused window length with step size. Resolution: Remove the button; provide clear window navigation `[‹] Window 1,797 / 26,281 [›]` and standard daily jump options. |
| **`PM2.5`** | `PM2.5 (µg/m³)` | Channel 0 of 13 canonical channels. | **Valid UI Default** | Legitimate default pollutant. Keep, but ensure all 13 channels are categorized and use dynamic units. |
| **`Hong Kong EPD`** | Badge: `Dataset: Hong Kong EPD` | Valid 16-station network. | **Redundant Badge** | Accurate research metadata, but oversized badge clutters header. Resolution: Merge into subtitle (`Mong Kok · Hong Kong EPD · 17 Apr 2021`). |
| **`Model: Awaiting Phase 4C`** | Pill badge in chart header | Phase 4C is upcoming model phase; no model trained yet. | **Misplaced Priority** | Permanently dominates chart header, making it feel like a broken dashboard. Resolution: Demote to subtle status in series selector / footer. |
| **`µg/m³` in Tooltip** | Hardcoded for all channels | 13 channels have 8 distinct units: `µg/m³`, `hPa`, `%`, `°C`, `mm`, `m/s`, `°`, `km/h`. | **Hardcoded Bug** | Tooltip hardcoded `µg/m³` on every row. Resolution: Pass channel unit dynamically to tooltip and axis. |
| **Smooth Curve Through NaNs** | Recharts `<Line type="monotone" dataKey="actual">` | Missing sensor hours are NaNs in raw data. | **Scientific Violation** | Continuous interpolation manufactured fake measurements through missing hours. Resolution: Do NOT connect nulls across natural missingness; render explicit gaps or hollow missing markers. |

---

## 4. Frozen Dataset Ground Truth Reference

* **Spatial Coverage:** 16 Hong Kong EPD Monitoring Stations (13 General + 3 Roadside).
* **Temporal Coverage:** 2019-01-01 00:00:00 to 2021-12-31 23:00:00 (26,304 physical hours = 1,096 calendar days).
* **Sliding 24-Hour Windows:**
  * Windows per station (full dataset): `26,304 - 24 + 1 = 26,281` windows.
  * Total windows across 16 stations: `26,281 × 16 = 420,496` windows.
  * Windows per station (test split: 2021-07-22 to 2021-12-31): `3,912 - 24 + 1 = 3,889` windows (163 days).
  * Total windows in test split across 16 stations: `3,889 × 16 = 62,224` windows.
* **13 Continuous Channels:**
  * 5 Criteria Pollutants: `PM2.5` (`µg/m³`), `PM10` (`µg/m³`), `NO2` (`µg/m³`), `SO2` (`µg/m³`), `O3` (`µg/m³`)
  * 6 Meteorology: `Pressure` (`hPa`), `Relative Humidity` (`%`), `Temperature` (`°C`), `Rainfall` (`mm`), `Wind Direction` (`°`), `Wind Speed` (`m/s`)
  * 2 Traffic: `Traffic Speed` (`km/h`), `Traffic Congestion` (normalized index)

---

## 5. Architectural Redesign Recommendations

The component must transition from a "chart with a congested toolbar" to a **4-layer scientific analysis workspace**:

1. **Layer 1: Context Header (Top-Left & Top-Right):**
   * Top-Left: `24-Hour Concentration Trajectory`
   * Subtitle: `[STATION NAME] · [DATE] · 00:00–23:00` (e.g. `Mong Kok · 17 Apr 2021 · 00:00–23:00`)
   * Top-Right: High-priority actions: `[Export Figure]` and `[⋯ More Options]`
2. **Layer 2: Dedicated Control Bar:**
   * Left: Window navigation `[‹] Window 1,797 / 26,281 [slider] [›]`
   * Right: Channel selector `[PM2.5 (µg/m³)]` and Series selector `[Series · 2]`
3. **Layer 3: Hero Visualization Area:**
   * High-contrast scientific line chart.
   * X-axis: Clean hourly ticks (`00:00`, `04:00`, `08:00`, `12:00`, `16:00`, `20:00`, `23:00`).
   * Y-axis: Channel-specific unit in axis header, clean numeric tick labels.
   * Scientifically honest missingness: Line breaks across unobserved hours; natural missing points displayed with distinct hollow circles.
4. **Layer 4: Footer Legend & Status:**
   * Clean legend: `● Observed` and `○ Natural Missing`.
   * Discreet data status indicator: `Hong Kong EPD Network · 100% Observed` or `Natural Missingness: 2 Dropouts`.
   * Future-proof: Ready to display `Imputed (CTDI)` and `Confidence Interval` once Phase 4C outputs exist, without UI overhaul.
