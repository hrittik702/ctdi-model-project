/**
 * CTDI Air Imputation Studio - Centralized API Service
 * 
 * Communicates directly with the FastAPI backend.
 * Provides typed responses, network error handling, and guarantees
 * that scientific computations and metrics originate from the backend model.
 */

const API_BASE = 'http://127.0.0.1:8000';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!res.ok) {
      let errorData;
      try {
        errorData = await res.json();
      } catch {
        errorData = { detail: res.statusText };
      }
      throw new ApiError(
        errorData.detail || `HTTP ${res.status}: ${res.statusText}`,
        res.status,
        errorData
      );
    }

    return await res.json();
  } catch (err) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(`Unable to connect to backend service: ${err.message}`, 0, null);
  }
}

export const api = {
  /** Health check & active model status */
  async getHealth(station = null) {
    const query = station ? `?station=${encodeURIComponent(station)}` : '';
    return request(`/api/health${query}`);
  },

  /** List of Indian monitoring stations catalog */
  async getStations() {
    return request('/api/stations');
  },

  /** Switch active Indian monitoring station */
  async selectStation(stationName) {
    return request('/api/stations/select', {
      method: 'POST',
      body: JSON.stringify({ station: stationName })
    });
  },

  /** Dataset & station metadata */
  async getMetadata(station = null) {
    const query = station ? `?station=${encodeURIComponent(station)}` : '';
    return request(`/api/metadata${query}`);
  },

  /** Global benchmark metrics table across test set */
  async getMetrics(station = null) {
    const query = station ? `?station=${encodeURIComponent(station)}` : '';
    return request(`/api/metrics${query}`);
  },

  /** Real computed per-pollutant test set metrics */
  async getPollutantMetrics(station = null) {
    const query = station ? `?station=${encodeURIComponent(station)}` : '';
    return request(`/api/metrics/pollutants${query}`);
  },

  /** 24-hour sequence trajectory for a given sample index */
  async getSample(sampleIdx, station = null) {
    const query = station ? `?station=${encodeURIComponent(station)}` : '';
    return request(`/api/samples/${sampleIdx}${query}`);
  },

  /** Live inference forward pass with custom missingness parameters */
  async liveImpute({ sampleIdx = 0, missingRate = 0.30, mechanism = 'random', seed = 42, blockLength = 4, station = null }) {
    return request('/api/impute', {
      method: 'POST',
      body: JSON.stringify({
        sample_idx: Number(sampleIdx),
        missing_rate: Number(missingRate),
        mechanism,
        seed: Number(seed),
        block_length: Number(blockLength),
        station
      })
    });
  },

  /** Historical benchmark experiments */
  async getExperiments() {
    return request('/api/experiments');
  },

  /** PyTorch model architecture configuration & checkpoint info */
  async getModelConfig(station = null) {
    const query = station ? `?station=${encodeURIComponent(station)}` : '';
    return request(`/api/model/config${query}`);
  },

  /** Upload and preview user CSV for validation and missingness statistics */
  async uploadAndPreviewCSV(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API_BASE}/api/impute/preview`, {
        method: 'POST',
        body: formData
      });
      if (!res.ok) {
        let err;
        try {
          err = await res.json();
        } catch {
          err = { detail: res.statusText };
        }
        const msg = typeof err?.detail === 'object'
          ? (err.detail.message || JSON.stringify(err.detail))
          : (err?.detail || `HTTP ${res.status}: ${res.statusText}`);
        throw new ApiError(msg, res.status, err);
      }
      return await res.json();
    } catch (err) {
      if (err instanceof ApiError) throw err;
      throw new ApiError(`Unable to connect to backend service: ${err.message}`, 0, null);
    }
  },

  /** Upload user CSV and run complete CTDI neural imputation pipeline */
  async uploadAndImputeCSV(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API_BASE}/api/impute/upload`, {
        method: 'POST',
        body: formData
      });
      if (!res.ok) {
        let err;
        try {
          err = await res.json();
        } catch {
          err = { detail: res.statusText };
        }
        const msg = typeof err?.detail === 'object'
          ? (err.detail.message || JSON.stringify(err.detail))
          : (err?.detail || `HTTP ${res.status}: ${res.statusText}`);
        throw new ApiError(msg, res.status, err);
      }
      return await res.json();
    } catch (err) {
      if (err instanceof ApiError) throw err;
      throw new ApiError(`Unable to connect to backend service: ${err.message}`, 0, null);
    }
  },

  /* -------------------------------------------------------------
   * MODEL COMPARISON & BENCHMARKING LAB METHODS
   * ----------------------------------------------------------- */
  /** List registered models for comparison, optionally filtered by city */
  async getComparisonModels(city = null) {
    const query = city ? `?city=${encodeURIComponent(city)}` : '';
    return request(`/api/comparison/models${query}`);
  },

  /** List available benchmarking datasets, optionally filtered by city */
  async getComparisonDatasets(city = null) {
    const query = city ? `?city=${encodeURIComponent(city)}` : '';
    return request(`/api/comparison/datasets${query}`);
  },

  /** List geographic cities with available comparison models */
  async getComparisonCities() {
    return request('/api/comparison/cities');
  },

  /** Select active model for live production inference */
  async selectActiveModel(modelId) {
    return request('/api/models/select', {
      method: 'POST',
      body: JSON.stringify({ model_id: modelId })
    });
  },

  /** Run scientific comparison experiment */
  async runComparison({
    dataset_id = 'delhi_test_benchmark',
    city = 'Delhi',
    model_ids = null,
    strategy = 'random',
    missing_rate = 0.30,
    block_length = 4,
    target_pollutant_outage = null,
    seed = 42137,
    num_windows = 5
  }) {
    return request('/api/comparison/run', {
      method: 'POST',
      body: JSON.stringify({
        dataset_id,
        city,
        model_ids,
        strategy,
        missing_rate: Number(missing_rate),
        block_length: Number(block_length),
        target_pollutant_outage,
        seed: Number(seed),
        num_windows: Number(num_windows)
      })
    });
  },

  /** Run comparison with uploaded user CSV */
  async runComparisonUpload({
    file,
    city = 'Delhi',
    model_ids = null,
    strategy = 'random',
    missing_rate = 0.30,
    block_length = 4,
    target_pollutant_outage = null,
    seed = 42137,
    num_windows = 5
  }) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('city', city);
      if (model_ids) formData.append('model_ids', JSON.stringify(model_ids));
      formData.append('strategy', strategy);
      formData.append('missing_rate', String(missing_rate));
      formData.append('block_length', String(block_length));
      if (target_pollutant_outage) formData.append('target_pollutant_outage', target_pollutant_outage);
      formData.append('seed', String(seed));
      formData.append('num_windows', String(num_windows));

      const res = await fetch(`${API_BASE}/api/comparison/run-upload`, {
        method: 'POST',
        body: formData
      });
      if (!res.ok) {
        let err;
        try {
          err = await res.json();
        } catch {
          err = { detail: res.statusText };
        }
        const msg = typeof err?.detail === 'object'
          ? (err.detail.message || JSON.stringify(err.detail))
          : (err?.detail || `HTTP ${res.status}: ${res.statusText}`);
        throw new ApiError(msg, res.status, err);
      }
      return await res.json();
    } catch (err) {
      if (err instanceof ApiError) throw err;
      throw new ApiError(`Unable to connect to backend service: ${err.message}`, 0, null);
    }
  },

  /** Get historical benchmarking runs */
  async getComparisonHistory() {
    return request('/api/comparison/history');
  },

  /** Get specific historical experiment run */
  async getComparisonExperiment(experimentId) {
    return request(`/api/comparison/history/${encodeURIComponent(experimentId)}`);
  },

  /** Side-by-side comparison of two historical runs */
  async compareTwoExperiments(id_a, id_b) {
    return request('/api/comparison/compare-runs', {
      method: 'POST',
      body: JSON.stringify({ id_a, id_b })
    });
  },

  /** Re-run an existing historical experiment with exact configuration and seed */
  async reRunComparisonExperiment(experimentId) {
    return request(`/api/comparison/re-run/${encodeURIComponent(experimentId)}`, {
      method: 'POST'
    });
  },

  /** Direct download URL for canonical export */
  getComparisonExportUrl(experimentId, format = 'csv') {
    return `${API_BASE}/api/comparison/export/${encodeURIComponent(experimentId)}?format=${format}`;
  }
};

export default api;
