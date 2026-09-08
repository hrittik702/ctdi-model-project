/**
 * CTDI Air Imputation Studio - Central Terminology Registry
 * 
 * Single source of truth for all scientific terms, metric definitions,
 * model architectures, and evaluation concepts used across the platform.
 */

export const TERMINOLOGY = {
  // --- METRICS ---
  MAE: {
    term: "MAE",
    name: "Mean Absolute Error",
    short: "Average absolute magnitude of errors between imputed predictions and actual ground-truth values.",
    interpretation: "Lower is better. Represents typical error in physical concentration units.",
    unit: "µg/m³ (micrograms per cubic meter)",
    caveat: null
  },
  RMSE: {
    term: "RMSE",
    name: "Root Mean Square Error",
    short: "Square root of the average squared differences between imputed predictions and ground truth.",
    interpretation: "Lower is better. Penalizes large outlier errors more severely than MAE.",
    unit: "µg/m³",
    caveat: "More sensitive to occasional large spikes or abrupt errors than MAE."
  },
  MAPE: {
    term: "MAPE",
    name: "Mean Absolute Percentage Error",
    short: "Average magnitude of error expressed as a percentage relative to the actual measured ground truth.",
    interpretation: "Lower is better. Allows relative comparison across features of different scales.",
    unit: "%",
    caveat: "Interpret carefully when actual air pollution concentrations are near zero (e.g. clean background days)."
  },
  NMAE: {
    term: "NMAE",
    name: "Normalized Mean Absolute Error",
    short: "Mean Absolute Error computed on standardized Z-score normalized features.",
    interpretation: "Lower is better. Scale-independent metric allowing equal weighting across all pollutants.",
    unit: "Normalized (dimensionless)",
    caveat: "Values are relative to training set standard deviations."
  },
  NRMSE: {
    term: "NRMSE",
    name: "Normalized Root Mean Square Error",
    short: "Root Mean Square Error computed on standardized Z-score normalized features.",
    interpretation: "Lower is better. Reflects squared error magnitude normalized by feature variance.",
    unit: "Normalized (dimensionless)",
    caveat: null
  },

  // --- MODELS & BASELINES ---
  CTDI: {
    term: "CTDI Transformer",
    name: "CTDI Temporal Transformer Imputer",
    short: "The primary spatial-temporal neural model. Projects multivariate features with 1×1 Conv1D and models dependencies across the 24-hour window using multi-head self-attention.",
    interpretation: "State-of-the-art imputation that leverages cross-pollutant correlations to infer missing values.",
    unit: null,
    caveat: "Current V0.1 single-station implementation uses temporal attention with cross-channel convolutional mixing."
  },
  "Linear Interpolation": {
    term: "Linear Interpolation",
    name: "1D Temporal Linear Interpolation",
    short: "Baseline numerical method that draws straight lines between known hourly observations in time.",
    interpretation: "Standard sanity-check baseline. Fails to capture non-linear peaks or cross-pollutant interactions.",
    unit: null,
    caveat: "Operates strictly within individual channels without cross-pollutant awareness."
  },
  KNN: {
    term: "KNN Imputer",
    name: "K-Nearest Neighbors Imputation (k=5)",
    short: "Estimates missing values by finding similar historical 24-hour multivariate sequence profiles based on Euclidean distance.",
    interpretation: "Non-parametric comparison baseline that searches for matching historical weather/pollution patterns.",
    unit: null,
    caveat: "Computationally expensive during inference on high-dimensional sequences."
  },
  MLP: {
    term: "MLP Autoencoder",
    name: "Multi-Layer Perceptron Imputer",
    short: "A feed-forward neural network baseline that takes the flattened 24-hour multivariate sequence and mask to reconstruct missing values.",
    interpretation: "Serves as a non-recurrent, non-attention deep learning baseline.",
    unit: null,
    caveat: "Lacks explicit temporal sequence inductive bias compared to the Transformer."
  },
  Mean: {
    term: "Mean Imputer",
    name: "Global Feature Mean Imputation",
    short: "Replaces every missing entry with the long-term empirical average of that pollutant calculated from the training set.",
    interpretation: "Primitive reference baseline to confirm all advanced models outperform naive averaging.",
    unit: null,
    caveat: "Completely ignores temporal context and diurnal variations."
  },

  // --- ARCHITECTURE COMPONENTS ---
  "1x1 CNN": {
    term: "1×1 CNN",
    name: "Pointwise 1D Convolution",
    short: "A convolution with kernel size 1 that mixes cross-pollutant features and masks at each hour without altering the 24-hour sequence length.",
    interpretation: "Enables inter-channel feature communication (e.g. PM2.5 correlating with PM10 and CO).",
    unit: null,
    caveat: null
  },
  Transformer: {
    term: "Transformer Encoder",
    name: "Multi-Head Temporal Self-Attention",
    short: "Computes attention weights between every pair of hours in the 24-hour sequence to capture long-range temporal dependencies.",
    interpretation: "Allows the model to attend to early morning trends to impute missing evening values.",
    unit: null,
    caveat: null
  },
  "Positional Encoding": {
    term: "Positional Encoding",
    name: "Sinusoidal Temporal Encoding",
    short: "Injects hourly time-of-day information into the input representations using sine and cosine functions of varying frequencies.",
    interpretation: "Enables permutation-invariant attention layers to understand chronological sequence order.",
    unit: null,
    caveat: null
  },

  // --- EVALUATION & MISSINGNESS ---
  "Ground Truth": {
    term: "Ground Truth",
    name: "Actual Measured Concentration",
    short: "The original verified sensor reading used as the objective ground-truth reference for calculating error metrics.",
    interpretation: "Unbiased reference. Preserved in full during artificial missingness experiments.",
    unit: "µg/m³",
    caveat: null
  },
  "Observed Points": {
    term: "Observed Points",
    name: "Visible Model Inputs",
    short: "Sensor observations that were made visible to the imputation model during the forward pass.",
    interpretation: "The model conditions its predictions on these points and preserves them exactly in the final reconstructed output.",
    unit: null,
    caveat: null
  },
  "Hidden Target": {
    term: "Hidden Target",
    name: "Artificially Masked Evaluation Target",
    short: "Real ground-truth values intentionally hidden from the model during evaluation to objectively measure imputation accuracy.",
    interpretation: "All MAE, RMSE, and MAPE metrics are calculated EXCLUSIVELY at these withheld coordinates.",
    unit: null,
    caveat: "Ensures metrics reflect true imputation capability rather than trivial copying of observed inputs."
  },
  "Missing Rate": {
    term: "Missing Rate",
    name: "Target Missingness Fraction",
    short: "The proportion of observed coordinates intentionally masked during artificial evaluation.",
    interpretation: "E.g., 30% missing rate means approximately 30% of valid points are hidden for reconstruction testing.",
    unit: "%",
    caveat: null
  },
  MCAR: {
    term: "MCAR",
    name: "Missing Completely At Random",
    short: "Uniformly distributed random corruption where each hourly observation has an independent probability of being masked.",
    interpretation: "Simulates intermittent telemetry packet loss or scattered transient transmission dropouts.",
    unit: null,
    caveat: null
  },
  Block: {
    term: "Continuous Block Outage",
    name: "Consecutive Hours Sensor Blackout",
    short: "Simulates sustained sensor outages or power failures by masking consecutive hours (e.g. 4-8 hours continuous).",
    interpretation: "Harder imputation regime testing temporal extrapolation across extensive gaps.",
    unit: null,
    caveat: null
  },
  "24-Hour Window": {
    term: "24-Hour Window",
    name: "Daily Sequence Analysis Slice",
    short: "A contiguous 24-hour hourly time-series window extracted from the continuous atmospheric monitoring dataset.",
    interpretation: "Captures full diurnal cycles of photochemical reactions and traffic emissions.",
    unit: "Hours (00:00 to 23:00)",
    caveat: null
  },
  "Evaluation Points": {
    term: "Evaluation Points",
    name: "Count of Hidden Test Coordinates",
    short: "The exact number of withheld ground-truth observations across the test set over which metrics are computed.",
    interpretation: "For the default 30% benchmark, 26,708 distinct hidden coordinates were evaluated.",
    unit: "Count",
    caveat: "Observed values are never counted in the evaluation loss or metrics."
  },
  Normalization: {
    term: "Normalization",
    name: "StandardScaler Feature Scaling",
    short: "Transforms each pollutant channel to zero mean and unit variance ($Z = \\frac{X - \\mu}{\\sigma}$) using training-set statistics strictly.",
    interpretation: "Prevents high-magnitude pollutants (like CO in hundreds of µg/m³) from dominating loss over smaller ones (like SO2).",
    unit: "Standard deviations (Z-score)",
    caveat: "Scaler parameters are fitted strictly on the training set to prevent test data leakage."
  },
  "Reproducibility Seed": {
    term: "Reproducibility Seed",
    name: "Pseudorandom Number Generator Seed",
    short: "Controls the random number generator used for artificial mask generation in both Python and NumPy.",
    interpretation: "Using the same seed (e.g. 42) ensures exact deterministic mask recreation across repeat runs.",
    unit: "Integer",
    caveat: null
  }
};

/**
 * Retrieve definition object by term key, with case-insensitive matching fallback.
 */
export function getTerminology(termKey) {
  if (!termKey) return null;
  if (TERMINOLOGY[termKey]) return TERMINOLOGY[termKey];

  const lower = termKey.toLowerCase().trim();
  for (const key of Object.keys(TERMINOLOGY)) {
    if (key.toLowerCase() === lower || TERMINOLOGY[key].name.toLowerCase().includes(lower)) {
      return TERMINOLOGY[key];
    }
  }

  // Fallback if not found in dictionary
  return {
    term: termKey,
    name: termKey,
    short: `Scientific parameter: ${termKey}`,
    interpretation: null,
    unit: null,
    caveat: null
  };
}
