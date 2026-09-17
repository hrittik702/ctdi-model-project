# Cleaning, Translation & Validation Rules

---

## 1. Bilingual Sanitization & Schema Normalization

Raw EPD and HKO files contain bilingual headers (Traditional Chinese and English) and irregular spacing. The cleaning pipeline applies the following deterministic transformations:

### 1.1 Column Mapping
```text
Raw EPD Header                  -> Normalized Identifier
---------------------------------------------------------
"微細懸浮粒子 F.S.P."           -> "pm25"
"可吸入懸浮粒子 R.S.P."         -> "pm10"
"二氧化氮 NO2"                  -> "no2"
"臭氧 O3"                       -> "o3"
"二氧化硫 SO2"                  -> "so2"
"一氧化碳 CO"                   -> "co"
"氮氧化物 NOx"                  -> "nox"
"日期 Date"                     -> "date"
"小時 Hour"                     -> "hour"
"監測站 Station"                -> "station_name"
```

### 1.2 Hour Convention Harmonization
- Raw EPD files use 1-indexed hours: `Hour 1` to `Hour 24`.
- In ISO 8601, `Hour 24` of date $D$ corresponds to `00:00:00` of date $D + 1$.
- Conversion logic:
  $$\text{Timestamp} = \text{pd.to\_datetime}(\text{Date}) + \text{pd.to\_timedelta}(\text{Hour} - 1, \text{unit}='h')$$
  This yields a continuous, monotonic hourly sequence from `2019-01-01 00:00:00` to `2021-12-31 23:00:00`.

### 1.3 Missing Flag Sanitization
String missingness flags (e.g., `"N.A."`, `"*"`, `"-"`, `""`, whitespace) are converted directly to IEEE 754 `np.nan` floats. Zero values (`0.0`) are preserved as valid physical observations.
