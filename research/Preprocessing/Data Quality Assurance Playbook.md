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
Execution is cleanly terminated if real traffic data is unavailable.
