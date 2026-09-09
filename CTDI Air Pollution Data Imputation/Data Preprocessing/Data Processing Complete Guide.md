CTDI research document says the preprocessing should include normalization, observation masks, simulated missingness, temporal samples, and contextual information. The CTDI paper you provided gives a very useful practical precedent: align data, create a station × time × feature tensor, and divide it into **24-hour sliding-window samples**.

# 1. First understand what "data preprocessing" means

Suppose your raw data looks like this:

|timestamp|station|PM2.5|PM10|NO2|temperature|humidity|wind|
|---|---|--:|--:|--:|--:|--:|--:|
|2025-01-01 00:00|Station_A|82|120|35|18|72|2.1|
|2025-01-01 01:00|Station_A|79|115|34|17|74|1.8|
|2025-01-01 02:00|Station_A|NaN|110|32|17|75|1.7|
|2025-01-01 00:00|Station_B|65|95|28|19|68|2.5|

Your model **cannot simply be handed this messy table and told "please do science."**

We need to transform it.

The overall pipeline will be:

```text
RAW DATA
   ↓
Load data
   ↓
Understand columns
   ↓
Clean timestamps
   ↓
Align time intervals
   ↓
Handle duplicate records
   ↓
Handle invalid values
   ↓
Handle naturally missing values
   ↓
Organize stations × time × features
   ↓
Create context
   ↓
Normalize features
   ↓
Create observation mask
   ↓
Create artificial missingness for training/evaluation
   ↓
Create 24-hour samples
   ↓
Train / Validation / Test split
   ↓
Save processed dataset
   ↓
MODEL
```

That's preprocessing.

---

# 2. Your first job: understand your dataset

Before writing a single fancy preprocessing function, you need to answer:

### What data do we actually have?

For your project, likely categories are:

### Air pollution

For example:

```text
PM2.5
PM10
NO2
SO2
O3
CO
```

### Meteorological data

For example:

```text
temperature
humidity
pressure
wind speed
wind direction
rainfall
```

### Spatial information

```text
station_id
latitude
longitude
```

### Time information

```text
timestamp
date
hour
day
month
season
```

### Context

Eventually your proposed architecture wants environmental context such as:

```text
season
traffic intensity
industrial influence
meteorology
station characteristics
```

Your research document explicitly describes these as contextual information for the SLM.

---

# 3. Step 1: Load the raw dataset

Suppose your file is:

```text
air_pollution.csv
```

Using Python:

```python
import pandas as pd

df = pd.read_csv("air_pollution.csv")

print(df.head())
print(df.shape)
print(df.columns)
```

You need to understand three things immediately:

```python
print(df.shape)
print(df.columns.tolist())
print(df.info())
```

For example:

```text
(100000, 10)
```

means:

```text
100,000 rows
10 columns
```

Then:

```python
df.head()
```

shows you what one row actually represents.

---

# 4. Step 2: Check missing values

This is extremely important for **your project**, because your entire project is about missing data.

Run:

```python
print(df.isnull().sum())
```

You might get:

```text
timestamp          0
station_id         0
PM2.5           1250
PM10             980
NO2              720
temperature      300
humidity         420
wind_speed       500
latitude           0
longitude          0
```

This tells you:

> How much information is naturally missing from each variable?

Do **not immediately fill these missing values**.

That's a common beginner mistake.

Your model is supposed to learn **imputation**.

If you blindly do:

```python
df.fillna(df.mean())
```

you've just performed imputation before your imputation model gets a chance to exist. Spectacularly self-defeating.

---

# 5. Step 3: Check timestamps

Time-series projects live or die by timestamps.

Convert:

```python
df["timestamp"] = pd.to_datetime(df["timestamp"])
```

Then:

```python
print(df["timestamp"].min())
print(df["timestamp"].max())
```

Check whether timestamps are ordered:

```python
df = df.sort_values(["station_id", "timestamp"])
```

Now check the time difference:

```python
df["time_diff"] = df.groupby("station_id")["timestamp"].diff()

print(df["time_diff"].value_counts())
```

You might discover:

```text
1 hour       95000
2 hours       3000
3 hours       1000
```

That means your data isn't perfectly hourly.

This matters because your model will eventually work with **24-hour sequences**.

The CTDI paper specifically standardized different data sources to hourly frequency and then created 24-hour tensors using a sliding window.

---

# 6. Step 4: Convert everything to a common time frequency

Suppose pollution data comes every:

```text
1 hour
```

but weather data comes every:

```text
10 minutes
```

and traffic every:

```text
5 minutes
```

You cannot directly combine them.

The CTDI paper faced exactly this problem. Their pollution data was hourly, meteorological data was 10-minute, and traffic data was 5-minute, so they standardized the data to **one-hour intervals**.

For example:

```text
10:00
10:10
10:20
10:30
10:40
10:50
```

becomes:

```text
10:00 → average
```

In pandas:

```python
df["timestamp"] = pd.to_datetime(df["timestamp"])

df = (
    df.set_index("timestamp")
      .groupby("station_id")
      .resample("1h")
      .mean()
      .reset_index()
)
```

But **don't blindly run this yet**. Your actual dataset structure determines exactly how aggregation should be done.

---

# 7. Step 5: Remove duplicate records

Imagine:

```text
Station_A | 2025-01-01 10:00 | PM2.5 = 50
Station_A | 2025-01-01 10:00 | PM2.5 = 52
```

You have two measurements for the same station and timestamp.

Check:

```python
duplicates = df.duplicated(
    subset=["station_id", "timestamp"]
)

print(duplicates.sum())
```

If duplicates exist, we need a defined policy.

For example:

```python
df = df.groupby(
    ["station_id", "timestamp"]
).mean().reset_index()
```

But again, whether averaging is appropriate depends on how your source data was recorded.

---

# 8. Step 6: Deal with impossible values

This is different from missing values.

For example:

```text
PM2.5 = -20
humidity = 250
wind_speed = -5
```

These aren't missing.

They're **invalid**.

You need domain rules.

For example:

```python
df.loc[df["PM2.5"] < 0, "PM2.5"] = pd.NA
```

Similarly:

```python
df.loc[df["humidity"] < 0, "humidity"] = pd.NA
df.loc[df["humidity"] > 100, "humidity"] = pd.NA
```

But don't randomly invent limits. Use the documentation of your actual dataset or accepted physical ranges.

---

# 9. Step 7: Organize the data

This is where your project starts becoming interesting.

Your raw table:

```text
timestamp | station | PM2.5 | PM10 | NO2 | temperature | ...
```

eventually needs to become something conceptually like:

```text
             Features
        ┌─────────────────────┐
Station │ PM2.5 PM10 NO2 ... │
        ├─────────────────────┤
A       │ ...                 │
B       │ ...                 │
C       │ ...                 │
        └─────────────────────┘
              ×
            Time
```

Your research formulation describes the complete observations as:

```text
X ∈ R^(T × N × F)
```

where:

- `T` = time steps
    
- `N` = monitoring stations
    
- `F` = pollutant/meteorological variables
    

The CTDI paper similarly represents its raw data as a station × time × feature tensor and then extracts 24-hour tensors.

---

# 10. Step 8: Create the 24-hour samples

This is one of the most important parts.

Suppose you have:

```text
00:00
01:00
02:00
...
23:00
00:00
01:00
...
```

We take:

```text
Sample 1:
00:00 → 23:00
```

Then:

```text
Sample 2:
01:00 → next 00:00
```

Then:

```text
Sample 3:
02:00 → next 01:00
```

So:

```text
24-hour window
       ↓
████████████████████
        ↓ 1 hour
 ████████████████████
          ↓ 1 hour
  ████████████████████
```

The CTDI paper uses exactly this idea: a **24-hour window with a 1-hour sliding stride**.

For your prototype, I'd use the same basic structure.

---

# 11. Step 9: Create the observation mask

This is **absolutely essential** for your model.

Suppose the original data is:

```text
PM2.5

80
75
NaN
70
68
```

Create:

```text
Mask

1
1
0
1
1
```

Meaning:

```text
1 = observed
0 = missing
```

Your research document defines the mask exactly this way.

In Python:

```python
mask = df[features].notna().astype(int)
```

For example:

```text
PM2.5   PM10   NO2

 80      100    30      → 1 1 1
 75       NaN    32      → 1 0 1
 NaN      90     31      → 0 1 1
```

---

# 12. Step 10: Artificially create missing data

This is slightly confusing but extremely important.

Your dataset might contain mostly complete observations.

How do you train an imputation model then?

You **hide some known values yourself**.

Suppose original:

```text
80
75
72
70
68
```

You create:

```text
80
75
NaN
70
68
```

The model sees:

```text
80
75
?
70
68
```

and tries to predict:

```text
72
```

But because **you know the original value was 72**, you can calculate the error.

This is how you evaluate imputation.

Your research document explicitly proposes simulated missingness at different rates such as **10%, 30%, 50%, and 70%**, while preserving the original hidden values exclusively for evaluation.

The CTDI paper also creates masks to simulate missing air-pollution data and evaluates different missingness rates and patterns.

---

# 13. Don't only simulate random missing values

This is important for your research.

You should eventually test:

### Random missingness

```text
80
NaN
72
NaN
68
```

### Block missingness

```text
80
75
NaN
NaN
NaN
NaN
68
```

### Station-wise missingness

```text
Station A → normal
Station B → missing for some period
Station C → normal
```

Your research plan specifically proposes random, block, and station-wise missingness.

The CTDI paper also distinguishes consecutive missing patterns such as temporal, spatial, pollutant-wise and mixed consecutive missingness.

For your **first prototype**, however:

> Start with random missingness.

Don't build five kinds of missingness on day one. You have enough ways to make your life miserable already.

---

# 14. Step 11: Normalize the data

Suppose PM2.5 ranges:

```text
0 → 500
```

and humidity:

```text
0 → 100
```

and temperature:

```text
-5 → 45
```

Neural networks generally work better when numerical variables are put onto comparable scales.

For your project, the research plan says to normalize pollutant and meteorological variables using **training-set statistics**.

A common approach is standardization:

xnormalized=x−μσx_{normalized} = \frac{x-\mu}{\sigma}

where:

- `μ` = training-set mean
    
- `σ` = training-set standard deviation
    

Using Python:

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

train[features] = scaler.fit_transform(train[features])

val[features] = scaler.transform(val[features])

test[features] = scaler.transform(test[features])
```

Notice the important part:

```python
fit_transform(train)
```

but:

```python
transform(val)
transform(test)
```

**Never calculate normalization statistics using the test set.**

Your research document explicitly warns against this kind of leakage.

---

# 15. Step 12: Create your environmental context

This is where your project differs from the CTDI baseline.

Your proposed model doesn't just use numbers.

It creates structured environmental context such as:

```text
Season: Winter
Temperature: Low
Humidity: High
Wind speed: Low
Traffic intensity: High
Industrial influence: Low
Station type: Urban
```

Your research document describes creating a structured context record from meteorological variables, temporal information, station metadata and pollution-related descriptors.

Then eventually:

```text
Structured Context
       ↓
      SLM
       ↓
Context Embedding zC
       ↓
Diffusion Model
```

But **do not start with the SLM yet**.

First get the numerical preprocessing working.

---

# 16. Step 13: Train/validation/test split

This is another place beginners accidentally cheat.

Suppose your data is:

```text
2023
2024
2025
```

A sensible time-series split could be:

```text
2023 → Training
2024 → Validation
2025 → Test
```

The exact split depends on your dataset.

The important principle is:

```text
TRAIN
  ↓
learn parameters

VALIDATION
  ↓
choose model/hyperparameters

TEST
  ↓
final evaluation
```

Your research document says the original complete observations used for evaluation must not be used for model selection, and normalization statistics should come only from training data.

---

# 17. Your final preprocessing output

After all of this, you want something like:

```text
X_obs
```

Observed input:

```text
[stations × 24 hours × features]
```

and:

```text
M
```

Mask:

```text
[stations × 24 hours × features]
```

and:

```text
X_true
```

Original complete target used only for evaluation/training where appropriate.

And:

```text
C
```

Context information.

Conceptually:

```text
                RAW DATA
                   │
                   ▼
             Cleaning
                   │
                   ▼
          Time Alignment
                   │
                   ▼
        Station × Time × Feature
                   │
          ┌────────┴────────┐
          ▼                 ▼
      Numerical          Context
       Features           Builder
          │                 │
          ▼                 ▼
     Normalization         C
          │                 │
          └────────┬────────┘
                   ▼
             24-hour window
                   │
          ┌────────┴────────┐
          ▼                 ▼
        X_obs               M
          │                 │
          └────────┬────────┘
                   ▼
          YOUR MODEL INPUT
                   │
                   ▼
          SLM + Diffusion
```

This matches the high-level architecture in your project document.

---

# 18. What YOU should actually do first

Don't try to implement all of that immediately.

Your first milestone should be ridiculously simple:

### Phase 1: Dataset understanding

Learn:

```text
Python
   ↓
Pandas
   ↓
CSV
   ↓
DataFrame
   ↓
missing values
   ↓
timestamps
   ↓
groupby
   ↓
resampling
```

Then build this:

```text
raw.csv
   ↓
clean.csv
```

---

### Phase 2: Time-series preparation

Build:

```text
clean.csv
   ↓
hourly data
   ↓
station × time × features
   ↓
24-hour windows
```

Output:

```text
X.shape

(number_of_samples, number_of_stations, 24, number_of_features)
```

For example:

```text
(5000, 10, 24, 8)
```

means:

```text
5000 samples
10 stations
24 hours
8 features
```

---

### Phase 3: Missingness

Build:

```text
complete X
    ↓
missingness generator
    ↓
X_obs + mask
```

For example:

```text
X_true
   ↓
hide 30%
   ↓
X_obs
   +
Mask
```

Then verify visually that the mask is actually hiding the intended values.

---

### Phase 4: Normalization

Only after the above works:

```text
train statistics
       ↓
normalization
       ↓
train / validation / test
```

---

### Phase 5: Context

Then:

```text
weather + time + station information
             ↓
       context builder
             ↓
     structured context
```

---

### Phase 6: Model

Only **after all five phases work**:

```text
X_obs
Mask
Context
  ↓
SLM
  ↓
Context embedding
  ↓
Diffusion
```

That's the sensible development order.

---

# 19. The most important thing: don't use the paper's preprocessing blindly

This needs to be clear.

The CTDI paper is useful because it gives us a proven **spatio-temporal preprocessing strategy**, including hourly alignment and 24-hour sliding windows.

But your proposed project is **not CTDI**.

Your project adds:

```text
SLM context encoder
        +
conditional diffusion
        +
context alignment
        +
uncertainty
```

Your own research structure explicitly describes this difference.

So we should use CTDI as a **reference for preprocessing**, not copy its entire pipeline.

---

# 20. Your first actual coding exercise

Before touching the real project, learn this tiny example.

Create:

```text
practice_air.csv
```

with:

```csv
timestamp,station_id,PM2.5,PM10,temperature,humidity
2025-01-01 00:00,A,80,120,18,70
2025-01-01 01:00,A,75,115,17,72
2025-01-01 02:00,A,,110,17,74
2025-01-01 03:00,A,70,105,16,76
2025-01-01 00:00,B,60,90,19,65
2025-01-01 01:00,B,62,92,18,66
2025-01-01 02:00,B,64,,18,68
2025-01-01 03:00,B,63,91,17,70
```

Then write Python that can do **only these seven things**:

```python
1. Load CSV
2. Print first 5 rows
3. Print shape
4. Print column names
5. Count missing values
6. Convert timestamp to datetime
7. Sort by station and timestamp
```

Don't touch neural networks.

Don't touch diffusion.

Don't touch transformers.

Don't touch SLMs.

If you can do these seven things and explain **why each one is necessary**, you're actually learning preprocessing rather than performing ceremonial Python.

## What I recommend for your team

Make **one person responsible for understanding the raw dataset**, while everyone learns the basics.

Your immediate project task should be:

```text
             WEEK 1

Day 1 → Understand dataset
Day 2 → Pandas + missing values
Day 3 → Timestamp + hourly alignment
Day 4 → Station/time/feature organization
Day 5 → 24-hour sliding windows
Day 6 → Mask + artificial missingness
Day 7 → Test and visualize everything
```

At the end of that, you should have a working file like:

```text
processed_data.npz
```

containing something conceptually like:

```text
X_true
X_obs
mask
context
timestamps
station_ids
```

**That is the first real milestone of your project.** Once this works, the diffusion model has something sensible to consume. Before that, building the model is mostly decorating an empty plate.

And since you said you don't know preprocessing yet, the best next step is to **learn it practically from your actual dataset**, not through a 40-hour generic Pandas course. Upload/provide the raw dataset your team plans to use, and we can go through it column-by-column and build the preprocessing pipeline from scratch, explaining every line rather than dumping a finished script on you.