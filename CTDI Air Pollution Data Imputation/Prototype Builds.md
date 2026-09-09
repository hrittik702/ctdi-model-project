Your two documents actually give us a sensible progression: the proposed work extends a VAE approach toward SLM-conditioned diffusion, while CTDI gives you a concrete spatial-temporal architecture using **24-hour windows + 1×1 CNN + spatial/temporal Transformer**.

## What I recommend building first

Build this prototype in **5 stages**:

```text
                 PHASE 1
        Real Air Pollution Dataset
                  │
                  ▼
          Data Preprocessing
                  │
                  ▼
          24-hour Data Windows
                  │
                  ▼
            Missingness Mask
                  │
                  ▼
                 PHASE 2
        Basic Imputation Model
          CNN / Transformer
                  │
                  ▼
            Evaluate MAE/RMSE
                  │
                  ▼
                 PHASE 3
        Conditional Diffusion
                  │
                  ▼
       Multiple Possible Imputations
                  │
                  ▼
                 PHASE 4
           Context Encoder
             SLM / Small LM
                  │
                  ▼
        Context-conditioned Diffusion
                  │
                  ▼
                 PHASE 5
      Uncertainty + Experiments
```

The **first working prototype should only go as far as Phase 2**.

---

# 1. First define exactly what your prototype does

Don't make the first version handle everything.

For example:

### Input

Suppose you have:

```text
Timestamp     PM2.5   PM10   NO2   SO2   O3
10:00         52      70     31    8     20
11:00         55      NaN    32    9     21
12:00         NaN     NaN    40    10    23
...
```

Your model receives:

```text
X_observed
+
Mask
```

where:

```text
Mask = 1 → value exists
Mask = 0 → value missing
```

Then:

```text
Model
   ↓
Predicted complete tensor
   ↓
Take predictions ONLY where mask = 0
   ↓
Compare with original hidden values
```

This is the fundamental experiment.

Your proposed research document explicitly defines this setup using an observation mask and evaluates generated values at artificially hidden positions.

---

# 2. Pick a dataset

For the **first prototype**, don't worry about getting traffic + meteorology + 100 stations.

Start with:

### Option A: Air pollution only

Something like:

```text
timestamp
station
PM2.5
PM10
NO2
SO2
O3
```

This is enough to prove the core idea.

Interestingly, the CTDI paper itself found that, for its Hong Kong experiment, the air-pollution-only dataset performed slightly better than the pollution + urban-data version for recovery, although urban data helped training convergence.

So you don't need to drag half of a smart city into version 0.1.

---

# 3. Convert the dataset into 24-hour samples

This is one of the most important pieces.

CTDI uses:

```text
24 hours
×
stations
×
features
```

and slides the window by one hour.

For example, if you have:

```text
16 stations
24 hours
5 pollutants
```

one sample becomes:

```text
X.shape = (16, 24, 5)
```

For a simpler prototype with one station:

```text
X.shape = (24, 5)
```

I would actually start with the **single-station version first**.

Then move to:

```text
multiple stations
       ↓
spatial relationships
       ↓
spatial transformer
```

---

# 4. Artificially create missing data

This is critical because you need the original values to evaluate the model.

Start with:

### Random missingness

Example:

```text
Original:

PM2.5
50
52
55
58
60
63

Mask:

1
1
0
1
0
1
```

Model sees:

```text
50
52
0
58
0
63
```

But you secretly retain:

```text
55
60
```

for evaluation.

Then:

```text
Prediction:

50
52
56
58
61
63
```

Calculate:

```text
MAE
RMSE
```

on:

```text
55 vs 56
60 vs 61
```

**not on the observed values.**

The proposed research structure explicitly emphasizes evaluating only artificially hidden positions.

---

# 5. Build the simplest possible baseline

Before diffusion, build:

```text
Input
  ↓
Mask + Data
  ↓
MLP / Autoencoder
  ↓
Reconstructed Data
```

Then compare against:

```text
Mean
Linear interpolation
KNN
```

This gives you a sanity check.

If your neural network can't beat linear interpolation on a simple dataset, adding an SLM isn't going to summon scientific enlightenment from the GPU.

---

# 6. Then implement the CTDI-inspired model

This is where your second paper becomes very useful.

The CTDI architecture has:

```text
Incomplete 24h Tensor
        │
        ▼
     1×1 CNN
        │
        ▼
Spatial Transformer
        │
        ▼
Temporal Transformer
        │
        ▼
     1×1 CNN
        │
        ▼
Reconstructed Tensor
```

The 1×1 CNN learns interactions between different feature channels, while the spatial and temporal Transformers model relationships across stations and time.

For your prototype:

```text
X + Mask
    ↓
1×1 Conv
    ↓
Temporal Transformer
    ↓
1×1 Conv
    ↓
Prediction
```

Don't implement spatial Transformer immediately.

First:

### Version 1

```text
1 station
24 hours
5 pollutants
Temporal Transformer
```

Then:

### Version 2

```text
multiple stations
24 hours
5 pollutants
Spatial Transformer
        +
Temporal Transformer
```

---

# 7. Only after that, add diffusion

This is where your actual research contribution begins.

Your proposed architecture says:

```text
Incomplete Data
      │
      ├───────────────┐
      │               │
      ▼               ▼
Numerical Encoder   Context Builder
                        │
                        ▼
                       SLM
                        │
                        ▼
                     zC
      │               │
      └───────┬───────┘
              ▼
      Conditional Diffusion
              │
              ▼
      Spatio-Temporal
         Denoiser
              │
              ▼
       Generated Missing
          Values
```

That's the architecture described in your research structure.

But your first diffusion prototype should be much smaller:

```text
Observed data
     +
Mask
     +
Noise
     +
Condition
     ↓
Small neural denoiser
     ↓
Missing-value reconstruction
```

Don't immediately build a giant Stable-Diffusion-looking monstrosity for pollution. This is **tabular/spatio-temporal diffusion**, not image generation.

---

# 8. Where the SLM comes in

This is the part I'd deliberately postpone.

Your proposed context could look like:

```text
Season: Winter
Hour: 08:00
Temperature: 12°C
Humidity: 82%
Wind speed: Low
Traffic: High
Station type: Urban
Industrial influence: High
```

Turn that into a structured textual context:

```text
"Winter morning at an urban monitoring station.
Temperature is low, humidity is high, wind speed is low,
traffic intensity is high and industrial influence is high."
```

Then:

```text
Context
   ↓
Small Language Model
   ↓
Embedding zC
   ↓
Projection Layer
   ↓
Diffusion conditioning
```

Your research document specifically proposes using the SLM as a **context encoder**, not as the numerical generator itself.

That distinction is important.

---

# 9. Your MVP should actually be this

If I were building this with you, I'd make **Prototype V0.1**:

```text
                    DATASET
                       │
                       ▼
              Data preprocessing
                       │
                       ▼
              Normalize features
                       │
                       ▼
              Create 24h windows
                       │
                       ▼
             Artificial missingness
                       │
                       ▼
                 X + MASK
                       │
                       ▼
                 1×1 CNN
                       │
                       ▼
             Temporal Transformer
                       │
                       ▼
                 1×1 CNN
                       │
                       ▼
              Reconstructed X
                       │
                       ▼
          Replace only missing values
                       │
                       ▼
             MAE / RMSE / MAPE
```

That alone gives you a **working air-pollution imputation prototype**.

---

# 10. Then V0.2

Add diffusion:

```text
X + Mask
   │
   ▼
Condition Encoder
   │
   ▼
Diffusion Denoiser
   │
   ▼
Generated X
   │
   ▼
Missing values
```

Now generate:

```text
Sample 1
Sample 2
Sample 3
...
Sample K
```

For example:

```text
Missing PM2.5

Sample 1 → 81.2
Sample 2 → 83.7
Sample 3 → 79.8
Sample 4 → 82.4
Sample 5 → 85.1
```

Then:

```text
Mean       = 82.44
Std        = 2.03
Interval   = ...
```

This is where your **uncertainty-aware imputation** starts becoming meaningful. Your research plan explicitly proposes multiple reverse-diffusion samples for this purpose.

---

# 11. Then V0.3: SLM conditioning

Now add:

```text
                 Context
                    │
                    ▼
                   SLM
                    │
                    ▼
               Context Embedding
                    │
                    ▼
Observed ──────► Diffusion
Mask ─────────►    │
                    ▼
               Imputed Data
```

And now you can perform the experiment that actually matters scientifically:

### Without SLM

```text
Diffusion
```

versus

### With SLM

```text
SLM + Diffusion
```

If the second one doesn't improve something meaningful, then your supposed novelty is mostly decorative architecture.

Your own research document correctly identifies this ablation as essential.

---

# 12. Project structure

I'd structure the repository like this:

```text
air-pollution-imputation/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── masks/
│
├── configs/
│   └── config.yaml
│
├── src/
│   ├── data/
│   │   ├── loader.py
│   │   ├── preprocessing.py
│   │   ├── windowing.py
│   │   └── masking.py
│   │
│   ├── models/
│   │   ├── baseline.py
│   │   ├── temporal_transformer.py
│   │   ├── spatial_transformer.py
│   │   ├── diffusion.py
│   │   └── context_encoder.py
│   │
│   ├── training/
│   │   ├── train_baseline.py
│   │   ├── train_diffusion.py
│   │   └── losses.py
│   │
│   ├── evaluation/
│   │   ├── metrics.py
│   │   ├── evaluation.py
│   │   └── uncertainty.py
│   │
│   └── utils/
│       └── visualization.py
│
├── notebooks/
│   ├── 01_data_analysis.ipynb
│   ├── 02_missingness.ipynb
│   └── 03_results.ipynb
│
├── checkpoints/
│
├── results/
│
├── requirements.txt
└── README.md
```

---

# 13. Technology stack

Keep it boring.

That's a compliment.

```text
Python
PyTorch
NumPy
Pandas
Scikit-learn
Matplotlib
Jupyter
```

Later:

```text
Hugging Face Transformers
```

for the SLM.

Don't start by installing seventeen AI frameworks because somebody on YouTube said their logo looks futuristic.

---

# 14. Your first milestone

Don't define the milestone as:

> "Build SLM-conditioned diffusion model."

That's too large.

Define it as:

> **Given a 24-hour air-pollution sequence with artificially hidden values, reconstruct the missing values and measure the reconstruction error.**

### Milestone 1

Get this working:

```text
CSV
 ↓
Clean data
 ↓
24h windows
 ↓
Artificial mask
 ↓
Model
 ↓
Prediction
 ↓
MAE/RMSE
 ↓
Plot actual vs imputed
```

For example:

```text
PM2.5
│
│       actual
│      /\
│  /\ /  \      /\
│ /  \    \____/  \
│
│       imputed
│      /\
│  /\ /  \      /\
│ /  \    \____/  \
└──────────────────── time
```

Once that works reliably, **then** introduce diffusion.

---

# 15. The exact development sequence I'd use

### Week/Phase 1

**Data pipeline**

- Dataset acquisition
    
- Cleaning
    
- Missing-value analysis
    
- Normalization
    
- 24-hour window generation
    
- Train/validation/test split
    

### Phase 2

**Baseline**

- Mean
    
- Linear interpolation
    
- KNN
    
- Simple MLP/Autoencoder
    

### Phase 3

**CTDI-inspired neural model**

- 1×1 CNN
    
- Temporal Transformer
    
- Spatial Transformer
    
- Mask-aware reconstruction
    

### Phase 4

**Diffusion**

- Forward noise process
    
- Noise prediction network
    
- Reverse diffusion
    
- Conditional generation
    
- Multiple samples
    

### Phase 5

**SLM**

- Build environmental context
    
- Generate context representation
    
- Extract SLM embedding
    
- Projection layer
    
- Inject embedding into diffusion
    

### Phase 6

**Research experiments**

```text
10% missing
30%
50%
70%
```

and:

```text
Random
Block
Station-wise
```

Your research document recommends exactly these kinds of missingness-rate and missingness-mechanism experiments.

Then compare:

```text
Mean
Interpolation
KNN
LSTM/GRU
VAE
Diffusion
SLM-Diffusion
```

---

## The important part

Your **actual research hypothesis** isn't:

> "Transformer + SLM + Diffusion = better."

That's architecture soup.

The hypothesis should be:

> **Environmental context provides useful information for conditioning the distribution of missing pollution values.**

Therefore your critical experiment becomes:

```text
                    SAME DATA
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       Diffusion only       SLM + Diffusion
             │                   │
             ▼                   ▼
        Predictions          Predictions
             │                   │
             └─────────┬─────────┘
                       ▼
                 Compare them
```

And then go one step further:

```text
Correct context
      vs
Shuffled context
```

If correct context produces better reconstructions while shuffled context hurts performance, **now you have evidence that the semantic context is actually doing something**. Your research plan specifically calls for context-shuffling experiments for this reason.

### So, start here:

**Do not touch the SLM or diffusion yet.**

Your first coding target is:

> **`dataset → 24h tensor → artificial mask → simple Transformer imputer → MAE/RMSE → actual-vs-imputed plot`**

Once that pipeline works, the rest becomes an incremental engineering problem rather than a giant pile of buzzwords pretending to be a research project.