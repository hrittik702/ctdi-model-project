# 📖 07 - Glossary & Short Terms Reference

> [!ABSTRACT] Quick Reference
> This document provides a complete, alphabetical and categorized dictionary of all **acronyms, short terms, mathematical notations, and evaluation metrics** used across the CTDI Air Pollution Imputation research framework, neural codebase, and web dashboard.

---

## 🗂️ Quick Index by Category

1. [[#1. Evaluation & Accuracy Metrics]]
2. [[#2. Air Pollution & Environmental Terms]]
3. [[#3. Neural Architecture & Deep Learning]]
4. [[#4. Missingness & Masking Mathematics]]
5. [[#5. Classical Baseline Models]]
6. [[#6. Training & Optimization Techniques]]
7. [[#7. Software, Backend & Deployment Terms]]

---

## 1. Evaluation & Accuracy Metrics

### **MAE (Mean Absolute Error)**
- **Definition**: The average absolute difference between the actual observed physical values and the model's imputed predictions.
- **Formula**:
  $$\text{MAE} = \frac{1}{N} \sum_{i=1}^{N} \left| y_{\text{actual}, i} - \hat{y}_{\text{pred}, i} \right|$$
- **Units**: Identical to the physical target ($\mu\text{g/m}^3$).
- **Significance**: Highly intuitive; tells you exactly how many micrograms per cubic meter the model is off by on average.
- **CTDI Project Benchmark**: **$4.297\,\mu\text{g/m}^3$** (outperforming Linear Interpolation at $5.730\,\mu\text{g/m}^3$).

### **RMSE (Root Mean Square Error)**
- **Definition**: The square root of the average squared errors.
- **Formula**:
  $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (y_{\text{actual}, i} - \hat{y}_{\text{pred}, i})^2}$$
- **Units**: Micrograms per cubic meter ($\mu\text{g/m}^3$).
- **Significance**: Heavily penalizes large outlier errors because errors are squared before averaging. Useful for verifying that the model does not produce extreme wild spikes.
- **CTDI Project Benchmark**: **$11.763\,\mu\text{g/m}^3$** (vs $14.034\,\mu\text{g/m}^3$ for Linear).

### **MAPE (Mean Absolute Percentage Error)**
- **Definition**: The average absolute error expressed as a percentage relative to the true ground-truth value.
- **Formula**:
  $$\text{MAPE} = \frac{1}{N} \sum_{i=1}^{N} \left| \frac{y_{\text{actual}, i} - \hat{y}_{\text{pred}, i}}{y_{\text{actual}, i}} \right| \times 100\%$$
- **Units**: Percentage ($\%$).
- **Significance**: Normalizes error across both high-magnitude pollutants (like $\text{PM}_{10}$ at $160\,\mu\text{g/m}^3$) and trace pollutants (like $\text{SO}_2$ at $15\,\mu\text{g/m}^3$).
- **CTDI Project Benchmark**: **$6.63\%$** (representing $> 93.3\%$ overall reconstruction accuracy).

### **RMAE / nRMSE (Relative MAE / Normalized RMSE)**
- **Definition**: Error metrics scaled by either the channel standard deviation ($\sigma$) or mean ($\mu$), rendering metrics unitless across differing air sheds.

### **Huber Loss / Smooth L1 Loss**
- **Definition**: A hybrid loss function that is quadratic for small errors ($<\beta$) and linear for large errors ($\ge \beta$).
- **Formula**:
  $$\mathcal{L}_{\beta}(e) = \begin{cases} 0.5 \frac{e^2}{\beta}, & \text{if } |e| < \beta \\ |e| - 0.5 \beta, & \text{otherwise} \end{cases}$$
- **In Our Project**: Configured with $\beta = 0.1$ to strictly optimize for MAE while remaining stable against extreme pollution peaks.

---

## 2. Air Pollution & Environmental Terms

### **AQI (Air Quality Index)**
- An official single numerical scale (typically 0–500 in India/US) that aggregates multiple criteria pollutants to communicate health severity to the public. Missing sensor values cause erroneous or unavailable AQI calculations.

### **CPCB (Central Pollution Control Board)**
- The statutory government agency in India operating the National Ambient Air Quality Monitoring (NAAQM) station network.

### **$\text{PM}_{2.5}$ (Particulate Matter $\le 2.5\,\mu\text{m}$)**
- Fine combustion particles, dust, and aerosols with diameter $\le 2.5$ microns. Able to penetrate deep into lungs and bloodstream.
- **Delhi Mean**: $\approx 68.6\,\mu\text{g/m}^3$ | **CTDI MAE**: **$3.32\,\mu\text{g/m}^3$**.

### **$\text{PM}_{10}$ (Particulate Matter $\le 10\,\mu\text{m}$)**
- Inhalable coarse dust particles, construction debris, road dust, and pollen.
- **Delhi Mean**: $\approx 160.9\,\mu\text{g/m}^3$ | **CTDI MAE**: **$11.23\,\mu\text{g/m}^3$**.

### **$\text{NO}_2$ (Nitrogen Dioxide)**
- Reddish-brown toxic gas produced by vehicular exhaust and fossil fuel power plants. Strong diurnal rush-hour peaks.
- **Delhi Mean**: $\approx 35.2\,\mu\text{g/m}^3$ | **CTDI MAE**: **$1.81\,\mu\text{g/m}^3$** ($47\%$ reduction vs baseline).

### **$\text{SO}_2$ (Sulfur Dioxide)**
- Pungent gas emitted from coal-fired power plants, smelting, and heavy fuel oils.
- **Delhi Mean**: $\approx 28.1\,\mu\text{g/m}^3$ | **CTDI MAE**: **$1.30\,\mu\text{g/m}^3$**.

### **$\text{O}_3$ (Ground-Level Ozone)**
- Secondary photochemical pollutant formed when $\text{NO}_x$ and VOCs react in sunlight. Peaks in hot afternoons and drops at night.
- **Delhi Mean**: $\approx 93.8\,\mu\text{g/m}^3$ | **CTDI MAE**: **$3.83\,\mu\text{g/m}^3$** ($51\%$ reduction vs baseline).

### **$\mu\text{g/m}^3$ (Micrograms Per Cubic Meter)**
- The international standard concentration unit for atmospheric particulate and gaseous pollutants ($1\,\mu\text{g} = 10^{-6}\,\text{grams}$).

---

## 3. Neural Architecture & Deep Learning

### **CTDI (Convolutional Transformer for Data Imputation)**
- The flagship architecture developed in this project. It merges local temporal convolutional filters (for continuous derivatives) with global Pre-LN multi-head self-attention (for cross-pollutant and meteorological correlations).

### **1D Conv (One-Dimensional Convolution)**
- Convolutional filter sliding across time steps ($T=24$). 
  - $1\times 1$ pointwise conv mixes cross-channel chemical relationships.
  - $3\times 1$ conv aggregates local temporal trends ($t-1, t, t+1$).

### **MHA (Multi-Head Attention)**
- Allows the model to jointly attend to information from different representation subspaces across different hours of the day.

### **PE (Positional Encoding)**
- Sinusoidal geometric vectors ($\sin / \cos$) injected into input embeddings to inform the permutation-invariant Transformer of the sequential hour-of-day order ($t \in [0, 23]$).

### **Pre-LN (Pre-Layer Normalization)**
- Transformer architecture variant where Layer Normalization is applied *before* the self-attention and feedforward layers (`norm_first=True`), ensuring gradient stability and smooth loss descent.

### **GELU (Gaussian Error Linear Unit)**
- A smooth, non-linear activation function ($x \cdot \Phi(x)$) superior to standard ReLU for continuous atmospheric modeling.

---

## 4. Missingness & Masking Mathematics

### **Imputation**
- The statistical and computational process of inferring and substituting values for missing data points in an observed matrix.

### **MCAR (Missing Completely at Random)**
- Missingness where the probability of a data point being lost is entirely independent of observed and unobserved variables (e.g., random network packet loss).

### **MAR (Missing at Random)**
- Missingness where probability of loss depends on observed variables (e.g., sensor offline during extreme rain).

### **MNAR (Missing Not at Random)**
- Missingness where loss is tied to the value itself (e.g., sensor clips or shuts off when $\text{PM}_{2.5} > 500\,\mu\text{g/m}^3$).

### **$M_{\text{obs}}$ (Observation Mask)**
- Binary matrix marking actual physical sensor data:
  $$M_{\text{obs}}[t, f] = \begin{cases} 1, & \text{if sensor successfully recorded a value} \\ 0, & \text{if NaN / hardware dropout} \end{cases}$$

### **$M_{\text{art}}$ (Artificial Visibility Mask)**
- Controlled corruption mask created during training/evaluation to hide known observed values:
  $$M_{\text{art}}[t, f] = \begin{cases} 1, & \text{model is allowed to see the point} \\ 0, & \text{hidden from model} \end{cases}$$

### **$M_{\text{eval}}$ (Evaluation Target Mask)**
- Exact boolean matrix identifying where ground truth exists AND was artificially hidden:
  $$M_{\text{eval}} = M_{\text{obs}} \odot (1 - M_{\text{art}})$$
  All benchmark metrics are computed **strictly** where $M_{\text{eval}} = 1$.

### **Block Missingness**
- Realistic failure pattern where a sensor experiences contiguous outages lasting several consecutive hours (e.g., 2h to 6h) due to battery or transmission downtime.

---

## 5. Classical Baseline Models

### **Mean Imputer**
- Replaces missing gaps with the overall historical channel mean.
- **Drawback**: Destroys diurnal variance, daily peaks, and seasonal trends (Test MAE: $43.796\,\mu\text{g/m}^3$).

### **Linear Interpolation**
- Draws a straight line chord connecting the nearest observed value before and after a missing window.
- **Strength**: Effective for isolated 1-hour gaps.
- **Flaw**: Completely fails on multi-hour blocks and ignores weather/chemical dynamics (Test MAE: $5.730\,\mu\text{g/m}^3$).

### **KNN (K-Nearest Neighbors)**
- Imputes missing coordinates using distance-weighted averaging of the $k$ most similar 24-hour historical windows.

### **MLP (Multi-Layer Perceptron Autoencoder)**
- Feedforward neural network mapping vectorized flattened 24-hour windows through bottleneck hidden layers.

---

## 6. Training & Optimization Techniques

### **Inductive Continuous Linear Prior Residual Learning**
- The novel architectural technique introduced in CTDI:
  $$\hat{X} = X_{\text{linear\_prior}} + \Delta X_{\text{transformer}}$$
  The transformer directly models the atmospheric and photochemical *residual deviation* from the continuous linear chord, ensuring the model's accuracy is mathematically guaranteed to meet or exceed linear interpolation from step zero.

### **CosineAnnealingLR**
- Learning rate scheduler that gradually decreases learning rate following a cosine half-cycle from $1\text{e-}3 \to 1\text{e-}5$, allowing the optimizer to settle into the global minimum.

### **AdamW**
- Optimization algorithm with decoupled weight decay ($1\text{e-}4$) preventing network weights from growing excessively large while updating moment vectors.

### **Vectorized Dynamic Masking**
- Generating artificial masks on-the-fly across all $20,305$ sequence windows in NumPy/C within $55\,\text{ms}$ at the beginning of each epoch to prevent neural memorization.

---

## 7. Software, Backend & Deployment Terms

### **REST (Representational State Transfer)**
- Architectural style for web services using stateless HTTP methods (`GET`, `POST`).

### **FastAPI**
- Modern, asynchronous Python web framework used for `api.py` to serve live neural inference and benchmark metrics.

### **Uvicorn**
- Lightning-fast ASGI (Asynchronous Server Gateway Interface) web server used to run FastAPI.

### **NPZ (.npz)**
- Compressed zip archive format in NumPy used to store multi-dimensional test tensors, masks, and precomputed baseline predictions efficiently on disk.

### **Vite**
- Next-generation frontend build tool and dev server powering the React dashboard on port `5173`.
