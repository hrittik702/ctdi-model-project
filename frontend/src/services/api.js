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
  async getHealth() {
    return request('/api/health');
  },

  /** Dataset & station metadata */
  async getMetadata() {
    return request('/api/metadata');
  },

  /** Global benchmark metrics table across test set */
  async getMetrics() {
    return request('/api/metrics');
  },

  /** Real computed per-pollutant test set metrics */
  async getPollutantMetrics() {
    return request('/api/metrics/pollutants');
  },

  /** 24-hour sequence trajectory for a given sample index */
  async getSample(sampleIdx) {
    return request(`/api/samples/${sampleIdx}`);
  },

  /** Live inference forward pass with custom missingness parameters */
  async liveImpute({ sampleIdx = 0, missingRate = 0.30, mechanism = 'random', seed = 42, blockLength = 4 }) {
    return request('/api/impute', {
      method: 'POST',
      body: JSON.stringify({
        sample_idx: Number(sampleIdx),
        missing_rate: Number(missingRate),
        mechanism,
        seed: Number(seed),
        block_length: Number(blockLength)
      })
    });
  },

  /** Historical benchmark experiments */
  async getExperiments() {
    return request('/api/experiments');
  },

  /** PyTorch model architecture configuration & checkpoint info */
  async getModelConfig() {
    return request('/api/model/config');
  }
};

export default api;
