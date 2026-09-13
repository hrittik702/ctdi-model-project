# Temporal Alignment & Cartesian Grid Assembly

---

## 1. Expected Cartesian Grid Generation

To guarantee that no timestamps are skipped or duplicated, the alignment pipeline (`src/preprocessing/alignment.py`) explicitly constructs the target Cartesian grid before merging any sensor files:

```python
expected_timestamps = pd.date_range(start="2019-01-01 00:00:00", end="2021-12-31 23:00:00", freq="h")
# Exactly 26,304 hourly timestamps
# Cartesian product: 16 stations x 26,304 hours = 420,864 station-hour rows
```

---

## 2. Merging Logic & Grid Preservation

When merging modality tables (air quality, meteorology, traffic):
1. Merges are performed via **left joins** onto the expected Cartesian grid:
   ```python
   df_aligned = pd.merge(df_grid, df_source, on=["station_name", "timestamp"], how="left")
   ```
2. If a station-hour record is absent in the source data, a row of `NaN` is produced automatically, preserving the structural row count ($420,864$).
3. The table is strictly sorted by `["station_name", "timestamp"]` to guarantee identical memory layout across all serialization formats.
