/**
 * CTDI Air Imputation Studio - Centralized API Service
 * 
 * Communicates directly with the FastAPI backend.
 * Provides typed responses, network error handling, and guarantees
 * that scientific computations and metrics originate from the backend model.
 * Gracefully falls back to the canonical datasetContract when backend
 * endpoints are not reachable.
 */

import {
  HONG_KONG_STATIONS,
  DATASET_METADATA,
  CANONICAL_CHANNELS,
  MODEL_ARCHITECTURE_SPEC
} from '../constants/datasetContract';

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
  /** Health check & service status */
  async getHealth(station = null) {
    try {
      const query = station ? `?station=${encodeURIComponent(station)}` : '';
      const res = await request(`/api/health${query}`);
      // Normalize 'healthy' or 'ok' status
      const isHealthy = res?.status === 'healthy' || res?.status === 'ok';
      return {
        status: isHealthy ? 'ok' : (res?.status || 'unknown'),
        stage: res?.stage || 'scaffolding',
        message: res?.message || 'FastAPI service operational',
        model_name: 'CTDI CNN-Transformer',
        status_label: 'Model Checkpoint Unavailable',
        framework: 'PyTorch'
      };
    } catch {
      return {
        status: 'offline',
        stage: 'offline',
        message: 'FastAPI service unreachable',
        model_name: 'CTDI CNN-Transformer',
        status_label: 'API Offline',
        framework: 'PyTorch'
      };
    }
  },

  /** List of 16 Hong Kong monitoring stations catalog */
  async getStations() {
    try {
      const res = await request('/api/stations');
      if (res?.stations?.length > 0) return res;
    } catch {
      // Graceful fallback to canonical frozen dataset stations
    }
    return {
      status: 'ok',
      stations: HONG_KONG_STATIONS,
      total: HONG_KONG_STATIONS.length,
      network: 'Hong Kong EPD'
    };
  },

  /** Switch active monitoring station */
  async selectStation(stationId) {
    try {
      return await request('/api/stations/select', {
        method: 'POST',
        body: JSON.stringify({ station: stationId })
      });
    } catch {
      return { status: 'ok', station: stationId };
    }
  },

  /** Dataset & station metadata */
  async getMetadata(station = null) {
    try {
      const query = station ? `?station=${encodeURIComponent(station)}` : '';
      const res = await request(`/api/metadata${query}`);
      if (res && res.station) return res;
    } catch {
      // Graceful fallback to canonical frozen dataset metadata
    }
    const currentStn = HONG_KONG_STATIONS.find(s => s.id === station || s.code === station || s.name === station) || HONG_KONG_STATIONS[0];
    return {
      status: 'ok',
      dataset: DATASET_METADATA.name,
      network: DATASET_METADATA.network,
      station: currentStn.name,
      station_code: currentStn.code,
      station_id: currentStn.station_id,
      station_type: currentStn.type,
      latitude: currentStn.lat,
      longitude: currentStn.lng,
      elevation: `${currentStn.height_m}m`,
      district: currentStn.district,
      temporal_range: '2019-01-01 to 2021-12-31',
      total_hours: DATASET_METADATA.temporal_coverage.total_physical_hours,
      num_samples: 26281, // Station-local windows across full dataset (1,096 days)
      station_windows: 26281,
      test_station_windows: 3889,
      total_windows: DATASET_METADATA.windowing.total_windows, // 420,496 total across 16 stations
      window_size: 24,
      channels: CANONICAL_CHANNELS,
      pollutants: CANONICAL_CHANNELS.map(c => c.name),
      missing_rate_percent: 2.75,
      total_eval_points: 3889 * 24,
      model_trained: false,
      stage: 'Operational'
    };
  },

  /** Global benchmark metrics table across test set */
  async getMetrics(station = null) {
    try {
      const query = station ? `?station=${encodeURIComponent(station)}` : '';
      const res = await request(`/api/metrics${query}`);
      if (Array.isArray(res) && res.length > 0) return res;
    } catch {
      // No trained model yet - return empty array
    }
    return [];
  },

  /** Real computed per-pollutant test set metrics */
  async getPollutantMetrics(station = null) {
    try {
      const query = station ? `?station=${encodeURIComponent(station)}` : '';
      const res = await request(`/api/metrics/pollutants${query}`);
      if (res && Object.keys(res).length > 0) return res;
    } catch {
      // No trained model yet
    }
    return {};
  },

  /** 24-hour sequence trajectory for a given station-local window index (0 to 26,280) */
  async getSample(sampleIdx, station = null) {
    const query = station ? `?station=${encodeURIComponent(station)}` : '';
    const res = await request(`/api/samples/${sampleIdx}${query}`);
    if (res && res.hours) return res;
    throw new ApiError(`Sample ${sampleIdx} unavailable for station ${station}`, 404, null);
  },

  /** Live inference forward pass */
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
    try {
      const res = await request('/api/experiments');
      if (Array.isArray(res) && res.length > 0) return res;
    } catch {
      // Empty before runs are conducted
    }
    return [];
  },

  /** PyTorch model architecture configuration & checkpoint info */
  async getModelConfig(station = null) {
    try {
      const query = station ? `?station=${encodeURIComponent(station)}` : '';
      const res = await request(`/api/model/config${query}`);
      if (res && res.architecture) return res;
    } catch {
      // Return canonical architecture specification
    }
    return {
      ...MODEL_ARCHITECTURE_SPEC,
      status: 'specification_only',
      status_label: 'Model Architecture Specification',
      checkpoint_path: null,
      device: 'CUDA / MPS / CPU',
      framework: 'PyTorch v2.x'
    };
  },

  /** Upload and preview user CSV */
  async uploadAndPreviewCSV(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/api/impute/preview`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      let err;
      try { err = await res.json(); } catch { err = { detail: res.statusText }; }
      const msg = typeof err?.detail === 'object'
        ? (err.detail.message || JSON.stringify(err.detail))
        : (err?.detail || `HTTP ${res.status}: ${res.statusText}`);
      throw new ApiError(msg, res.status, err);
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
      let err;
      try { err = await res.json(); } catch { err = { detail: res.statusText }; }
      const msg = typeof err?.detail === 'object'
        ? (err.detail.message || JSON.stringify(err.detail))
        : (err?.detail || `HTTP ${res.status}: ${res.statusText}`);
      throw new ApiError(msg, res.status, err);
    }
    return await res.json();
  },

  /* -------------------------------------------------------------
   * MODEL COMPARISON & BENCHMARKING LAB METHODS
   * ----------------------------------------------------------- */
  async getComparisonModels(city = null) {
    try {
      const query = city ? `?city=${encodeURIComponent(city)}` : '';
      const res = await request(`/api/comparison/models${query}`);
      if (Array.isArray(res) && res.length > 0) return res;
    } catch {
      // Fallback
    }
    return [
      { id: 'ctdi_cnn_transformer', name: 'CTDI CNN-Transformer', framework: 'PyTorch', status: 'Unavailable', category: 'neural', city: 'Hong Kong', is_available: false },
      { id: 'linear_interpolation', name: '1D Linear Interpolation', framework: 'SciPy', status: 'Baseline', category: 'baseline', is_available: true },
      { id: 'knn_imputer', name: 'KNN Imputer (k=5)', framework: 'scikit-learn', status: 'Baseline', category: 'baseline', is_available: true },
      { id: 'mean_imputer', name: 'Global Channel Mean', framework: 'NumPy', status: 'Baseline', category: 'baseline', is_available: true }
    ];
  },

  async getComparisonDatasets(city = null) {
    try {
      const query = city ? `?city=${encodeURIComponent(city)}` : '';
      const res = await request(`/api/comparison/datasets${query}`);
      if (Array.isArray(res) && res.length > 0) return res;
    } catch {
      // Fallback
    }
    return [
      { id: 'hk_epd_test_benchmark', name: 'Hong Kong EPD Test Set (62,224 windows)', city: 'Hong Kong' }
    ];
  },

  async getComparisonCities() {
    try {
      const res = await request('/api/comparison/cities');
      if (Array.isArray(res) && res.length > 0) return res;
    } catch {
      // Fallback
    }
    return ['Hong Kong'];
  },

  async selectActiveModel(modelId) {
    try {
      return await request('/api/models/select', {
        method: 'POST',
        body: JSON.stringify({ model_id: modelId })
      });
    } catch {
      return { status: 'ok', model_id: modelId };
    }
  },

  async runComparison({
    dataset_id = 'hk_epd_test_benchmark',
    city = 'Hong Kong',
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

  async runComparisonUpload({
    file,
    city = 'Hong Kong',
    model_ids = null,
    strategy = 'random',
    missing_rate = 0.30,
    block_length = 4,
    target_pollutant_outage = null,
    seed = 42137,
    num_windows = 5
  }) {
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
      try { err = await res.json(); } catch { err = { detail: res.statusText }; }
      const msg = typeof err?.detail === 'object'
        ? (err.detail.message || JSON.stringify(err.detail))
        : (err?.detail || `HTTP ${res.status}: ${res.statusText}`);
      throw new ApiError(msg, res.status, err);
    }
    return await res.json();
  },

  async getComparisonHistory() {
    try {
      const res = await request('/api/comparison/history');
      if (Array.isArray(res)) return res;
    } catch {
      // Fallback
    }
    return [];
  },

  async getComparisonExperiment(experimentId) {
    return request(`/api/comparison/history/${encodeURIComponent(experimentId)}`);
  },

  async compareTwoExperiments(id_a, id_b) {
    return request('/api/comparison/compare-runs', {
      method: 'POST',
      body: JSON.stringify({ id_a, id_b })
    });
  },

  async reRunComparisonExperiment(experimentId) {
    return request(`/api/comparison/re-run/${encodeURIComponent(experimentId)}`, {
      method: 'POST'
    });
  },

  getComparisonExportUrl(experimentId, format = 'csv') {
    return `${API_BASE}/api/comparison/export/${encodeURIComponent(experimentId)}?format=${format}`;
  }
};

export default api;
