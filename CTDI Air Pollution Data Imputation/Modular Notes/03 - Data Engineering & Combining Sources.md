# 03 - Data Engineering & Combining Sources

> [!INFO] Module Context
> - **Parent**: [[00 - Index (Map of Content)]]
> - **Previous**: [[02 - Input-Process-Output Architecture]]
> - **Next**: [[04 - Neural Model & Masked Training]]
> - **Tags**: `#data-engineering` `#preprocessing` `#pandas` `#meteorology`

---

## 1. The Core Question: Separate Files vs. Adding Columns?

> **Question**: *"What if I have processed data like 10 pollutant features in one file, and meteorological data in another file? Do I prepare separate files or add columns?"*

### The Verdict:
**Add them as columns aligned by a single `timestamp` column** (or merge them into a single CSV table before feeding into the pipeline).

---

## 2. Why a Unified Time-Indexed Table is Essential

### Reason 1: Strict Temporal Synchronization
In time-series modeling, each row in a sequence tensor represents a single time step:
$$\mathbf{X}[t] = [P_1(t), P_2(t), \dots, P_{10}(t), M_1(t), \dots, M_5(t)]$$
Both pollutants and weather sensors must align on the exact same hour $t$. Having them in a single table indexed by `timestamp` guarantees zero offset.

### Reason 2: Cross-Channel Neural Correlation
The model's $1\times 1$ CNN treats each column as an input channel:
- When **Rain (`RAIN`)** occurs, **$\text{PM}_{2.5}$** is washed out.
- When **Wind Speed (`WSPM`)** is high, local pollution disperses.
- When **Temperature (`TEMP`)** rises under high sunlight, photochemical **$\text{O}_3$** spikes.
By feeding weather directly as feature channels in the same $(24 \times F)$ matrix, the neural network learns these physical relationships directly.

---

## 3. Targets vs. Covariates: An Important Decision

When combining pollutants and meteorology, decide between two modeling strategies:

| Strategy | Description | When to Use |
|---|---|---|
| **Case A: Joint Imputation (All are Targets)** | Pollutants and weather sensors are all placed in `data.pollutants`. The model imputes whichever sensor drops out. | When weather sensors also suffer from hardware dropouts and need repair. |
| **Case B: Weather as Exogenous Covariates (Guides Only)** | Weather is assumed to be always known (from satellite or official airport stations). The model conditions on weather to impute pollutants, but the loss function is evaluated **only on the pollutants**. | When you have a reliable external weather feed and want to maximize pollutant imputation accuracy. |

---

## 4. How to Merge Separate CSV Files

If your data is currently split into multiple files:
- `pollutants.csv` (`timestamp`, `PM2.5`, `PM10`, `SO2`, ...)
- `meteorology.csv` (`timestamp`, `TEMP`, `PRES`, `DEWP`, `RAIN`, `WSPM`, ...)
- `traffic.csv` (optional: `timestamp`, `traffic_volume`, ...)

Run this Python script to align and merge them into a single clean CSV:

```python
import pandas as pd

# 1. Load the raw files
df_pollutants = pd.read_csv("data/raw/pollutants.csv")
df_meteo = pd.read_csv("data/raw/meteorology.csv")

# 2. Ensure timestamps are in standard datetime format
df_pollutants["timestamp"] = pd.to_datetime(df_pollutants["timestamp"])
df_meteo["timestamp"] = pd.to_datetime(df_meteo["timestamp"])

# 3. Perform an outer merge on 'timestamp'
# (Outer merge ensures no hours are dropped if one file has slightly more records)
df_merged = pd.merge(df_pollutants, df_meteo, on="timestamp", how="outer")

# 4. Sort chronologically and reset index
df_merged = df_merged.sort_values("timestamp").reset_index(drop=True)

# 5. Export unified dataset
output_path = "data/raw/PRSA_Data_Aotizhongxin_20130301-20170228.csv"
df_merged.to_csv(output_path, index=False)
print(f"Successfully created unified dataset with {df_merged.shape[1]} columns!")
```

---

## 5. Updating the Configuration File

Once your columns are present in the CSV file, open `configs/default_config.yaml` and declare all columns you want the model to see:

```yaml
data:
  dataset_name: "Beijing_Aotizhongxin"
  station_name: "Aotizhongxin"
  # Add all 10 pollutants + meteorological features
  pollutants:
    - "PM2.5"
    - "PM10"
    - "SO2"
    - "NO2"
    - "CO"
    - "O3"
    - "NH3"
    - "BC"
    - "NOx"
    - "VOC"
    - "TEMP"
    - "PRES"
    - "DEWP"
    - "RAIN"
    - "WSPM"
```

### What Happens Automatically:
1. `src/data/preprocessing.py` reads the CSV, filters the columns, and checks physical ranges (e.g. concentrations cannot be negative).
2. `AirPollutionScaler` computes $\mu_f$ and $\sigma_f$ on the training split non-NaN values with **zero data leakage**.
3. `src/data/windowing.py` slices the unified table into $(N, 24, F)$ tensors where $F = 15$.
4. The $1\times 1$ CNN dynamically adjusts its input channels from $12 \to 2F = 30$.

---

👉 **Next Step**: Read [[04 - Neural Model & Masked Training]] to see how the model trains on this data without cheating.
