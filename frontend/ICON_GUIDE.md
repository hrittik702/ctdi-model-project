# CTDI Air Imputation Studio - Custom Icon Guide

This project uses a unified, custom SVG icon system designed specifically for scientific air-pollution analytics and machine learning imputation.

All icons follow a strict visual standard:
* **Geometry**: Geometric, clean technical aesthetic with 1.75px stroke width.
* **Palette Inheritance**: Uses `stroke="currentColor"` so icons automatically match text and semantic colors (`text-indigo-600`, `text-emerald-500`, `text-amber-500`, `text-rose-500`, etc.).
* **Zero Layout Distortion**: Icons enforce `flex-shrink: 0` to prevent resizing when adjacent labels wrap or truncate.

---

## 1. Quick Usage

```jsx
import ProjectIcon from './components/ui/ProjectIcon';

// Basic usage
<ProjectIcon name="trajectory" size="md" />

// Color inheritance via Tailwind text utility classes
<ProjectIcon name="ground-truth" size="lg" className="text-emerald-600 dark:text-emerald-400" />

// Numeric custom size
<ProjectIcon name="ctdi-logo" size={28} />
```

---

## 2. Standard Size Presets

| Size Preset | Pixel Size | Semantic Usage |
| :--- | :---: | :--- |
| `xs` | `12px` | Information tooltips (`ⓘ`), compact tags, inline indicators |
| `sm` | `14px` | Chart controls, secondary buttons, breadcrumb indicators |
| `md` | `16px` | Navigation items, default button icons, input prefixes |
| `lg` | `18px` | Sidebar primary icons, major modal triggers |
| `xl` | `20px` | KPI scorecards, header action buttons |
| `2xl` | `24px` | Branding badges, empty-state feature illustrations |

---

## 3. Complete Icon Library

### A. Branding & Atmosphere
| Name | Description & Usage |
| :--- | :--- |
| `ctdi-logo` | CTDI convolutional attention lattice with airflow dynamics. |
| `air-flow` | Atmospheric wind vectors with particulate matter dispersion. |

### B. Navigation & Studio Views
| Name | Description & Usage |
| :--- | :--- |
| `dashboard` | 4-quadrant layout grid for analytical overview. |
| `trajectory` | 24-hour continuous time-series curve with hourly nodes. |
| `multi-pollutant` | Stacked isometric sensor channel layers ($PM_{2.5}, PM_{10}, SO_2...$). |
| `benchmark` | Comparative model error performance scoreboard. |
| `station` | Geographic monitoring site pin with sensor coordinate waves. |
| `data-explorer` | Tabular telemetry database cylinder. |
| `sandbox` | Real-time neural inference simulation wand. |
| `experiment` | Historical evaluation log with clock face. |
| `model-config` | PyTorch neural chip with multi-head attention interconnects. |

### C. Scientific Concepts & Error Metrics
| Name | Description & Usage |
| :--- | :--- |
| `mae` | Absolute value delta brackets $| \Delta |$ for Mean Absolute Error. |
| `rmse` | Radical square-root sign $\sqrt{\Sigma}$ for Root Mean Square Error. |
| `mape` | Diagonal percentage ratio $\%$ for Relative Percentage Error. |
| `ground-truth` | Verified concentric sensor calibration target. |
| `observed-points` | Solid observation node with directional coordinate axes. |
| `hidden-target` | Dashed circle representing artificially masked evaluation target. |
| `transformer` | Multi-head temporal attention node network. |
| `linear-interp` | Dashed secant line connecting two known points in time. |
| `knn` | Clustered nearest neighbor nodes with radial boundary. |
| `mlp` | Multi-layer feed-forward neural layers with weight connections. |
| `missingness` | Segmented timeline bar showing observed blocks and missing gaps. |

### D. Actions & Chart Controls
| Name | Description & Usage |
| :--- | :--- |
| `fullscreen` | 4 expanding corner arrows. |
| `minimize` | 4 contracting corner arrows for exiting fullscreen. |
| `zoom-in` | Magnifying lens with plus mark. |
| `zoom-out` | Magnifying lens with minus mark. |
| `reset-zoom` | Counter-clockwise reset arrow to 1:1 scale. |
| `grid` | Cartesian coordinate gridlines toggle. |
| `camera` | High-resolution publication figure snapshot. |
| `download` | Universal export tray with arrow. |
| `search` | Global command palette search lens. |
| `filter` | Funnel filter for observation status. |
| `calendar` | Date selector for 24-hour window extraction. |
| `clock` | Hourly timestamp indicator. |
| `info` | Circular technical information icon for `InfoTooltip`. |
| `warning` | Triangular caution sign for caveats. |
| `success` | Circular checkmark for verified results. |
| `more` | 3 vertical dots for overflow dropdown menus. |
