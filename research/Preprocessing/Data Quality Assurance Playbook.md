# Data Quality Assurance Playbook

---

## 1. Automated Assertion Suite (`scripts/verify_raw_datasets.py`)

Before any canonical tensor assembly or model training is initiated, all datasets must pass the automated verification suite:

```bash
.venv/bin/python scripts/verify_raw_datasets.py
```

### Verification Assertions
1. **Station Count**: Exactly 16 stations included; exactly 2 stations excluded (Southern #84, North #85).
2. **Row Counts**: Air quality and meteorology tables must have exactly $420,864$ rows ($16 \text{ stations} \times 26,304 \text{ hours}$).
3. **Temporal Monotonicity**: Timestamps must be strictly continuous and monotonic from `2019-01-01 00:00:00` to `2021-12-31 23:00:00` HKT.
4. **Zero Duplicates**: Zero duplicate records on `(station_name, timestamp)`.
5. **Physical Value Bounds**:
   - Criteria air pollutants: $[0.0, 500.0]\ \mu\text{g/m}^3$ (zero negative values).
   - Relative humidity: $[0.0, 100.0]\%$.
   - Temperature: $[-10.0, 50.0]^\circ\text{C}$.
   - Surface pressure: $[950.0, 1050.0]\ \text{hPa}$.
   - Wind speed: $[0.0, 50.0]\ \text{m/s}$.
   - Wind direction: $[0.0, 360.0]^\circ$.

---

## 2. Alignment Pipeline Safety Halt

`src/preprocessing/alignment.py` enforces a hard assertion preventing synthetic traffic data injection:
```python
if not traffic_path.exists():
    raise FileNotFoundError(
        "Real CTDI traffic dataset not found. Synthetic traffic generation has been completely removed. "
        "Alignment correctly halted to preserve research integrity."
    )
```
Execution is cleanly terminated if real traffic data is unavailable. This safety assertion was cleanly satisfied in Phase 2 using the fully extracted 3-year Transport Department speedmap archive.

---

## 3. Phase 2 Spatio-Temporal Alignment Validation Suite (`src/preprocessing/validate_alignment.py`)

Following the execution of Phase 2 alignment, the dataset must pass the comprehensive 9-point validation suite:

```bash
.venv/bin/python src/preprocessing/validate_alignment.py
```

### The Nine Automated Validation Assertions (9/9 Passed)
1. **Temporal Grid Integrity**:
   - Exactly $26,304$ unique continuous hours spanning `2019-01-01 00:00:00` to `2021-12-31 23:00:00` HKT.
   - Zero missing timestamps, zero leap-year skips (2020 leap year has 8,784 hours).
2. **Station Spatial Coverage**:
   - Exactly 16 operational stations (IDs 66–83).
   - Southern (#84) and North (#85) verified strictly absent.
3. **Cartesian Grid Invariance**:
   - Total rows: exactly $16 \times 26,304 = 420,864$.
   - Duplicates on `(station_id, timestamp)`: exactly $0$.
   - Monotonic sorting: strictly verified.
4. **Air Quality Natural Missingness Conservation**:
   - Total missing values: exactly $55,876$ NaNs conserved bit-for-bit with raw EPD data ($\text{PM}_{2.5}$: 10,657, $\text{PM}_{10}$: 11,395, $\text{NO}_2$: 11,651, $\text{SO}_2$: 11,056, $\text{O}_3$: 11,117).
   - Range bounds: zero negative concentrations ($[0.0, 422.0]\ \mu\text{g/m}^3$).
5. **Meteorological Completeness & Physical Fidelity**:
   - Zero NaNs across all 6 meteorological channels ($420,864 \times 6 = 2,525,184$ valid values).
   - Pressure: $[986.5, 1029.9]\ \text{hPa}$.
   - Relative Humidity: $[13.0, 100.0]\%$.
   - Temperature: $[2.9, 35.6]^\circ\text{C}$.
   - Rainfall: $[0.0, 61.8]\ \text{mm}$ (naming rule strictly enforced).
   - Wind Speed: $[0.0, 17.35]\ \text{m/s}$.
   - Wind Direction: $[0.0, 360.0]^\circ$.
6. **Traffic Dynamics & Zero-Fill Prohibition**:
   - Valid station-hours: $418,448$ ($99.43\%$ completeness).
   - Missing station-hours: $2,416$ ($0.57\%$) preserved as genuine `NaN`s representing upstream archive outages.
   - Zero synthetic 0 km/h standstill filling: verified.
   - Speeds: $[34.76, 154.54]\ \text{km/h}$ (mean $62.23\ \text{km/h}$).
   - Saturation: $[0.0000, 0.8351]$ (mean $0.1178$).
7. **Spatial Confidence Stratification**:
   - High-confidence urban: $209,224$ station-hours.
   - Moderate-confidence suburban: $78,459$ station-hours.
   - Remote ecological background: $130,765$ station-hours.
8. **3D Tensor Reshape Parity**:
   - Canonical 13 channels verified in order.
   - 2D matrix shape: $(420864, 13)$.
   - 3D tensor shape: $(16, 26304, 13)$.
   - Distance matrix shape: $(16, 16)$, symmetric with zero diagonal.
9. **Cryptographic Raw Data Immutability**:
   - All 683 raw files in `data/raw/` audited against SHA-256 manifest.
   - 0 modified, 0 added, 0 deleted.

### Audit Artifacts Generated
- `data/interim/aligned/alignment_validation.json` (Machine-readable test results)
- `data/interim/aligned/alignment_summary.json` (High-level dataset summary)
- `research/Reports/Phase 2 - Spatio-Temporal Alignment Report.md` (Formal research report)
