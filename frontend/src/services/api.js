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
  async getMetrics() {
    return request('/api/metrics');
  },

  /** Real computed per-pollutant test set metrics */
  async getPollutantMetrics() {
    return request('/api/metrics/pollutants');
  },

  /** 24-hour sequence trajectory for a given sample index */
  async getSample(sampleIdx, station = null) {
    const query = station ? `?station=${encodeURIComponent(station)}` : '';
    return request(`/api/samples/${sampleIdx}${query}`);
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
  },

  /** Upload and preview user CSV for validation and missingness statistics */
  async uploadAndPreviewCSV(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/api/impute/preview`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(err.detail || `HTTP ${res.status}: ${res.statusText}`, res.status, err);
    }
    return await res.json();
  },

  /** Upload user CSV and run complete CTDI neural imputation pipeline */
  async uploadAndImputeCSV(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/api/impute/upload`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(err.detail || `HTTP ${res.status}: ${res.statusText}`, res.status, err);
    }
    return await res.json();
  }
};

export default api;
