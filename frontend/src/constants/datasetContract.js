/**
 * CTDI Air Imputation Studio - Canonical Dataset Contract v1.0
 * 
 * Authoritative single source of truth for frontend metadata, aligned
 * directly with data/final/CTDI_AirPollution_TrainingDataset_v1.0/
 * 
 * Guarantees zero data leakage, correct 13-channel ordering, exact
 * 16 Hong Kong EPD station coordinates, and clear decoupled lifecycle states.
 */

export const DATASET_METADATA = {
  version: '1.0.0',
  name: 'CTDI Air Pollution Training Dataset v1.0',
  domain: 'Hong Kong Special Administrative Region',
  network: 'Hong Kong EPD Air Quality Network',
  spatial_resolution: '16 Monitoring Stations (13 General + 3 Roadside)',
  temporal_coverage: {
    start: '2019-01-01 00:00:00',
    end: '2021-12-31 23:00:00',
    total_physical_hours: 26304,
    total_station_hours: 420864,
    calendar_days: 1096
  },
  windowing: {
    window_hours: 24,
    stride_hours: 1,
    total_windows: 419496
  },
  splits: {
    train: {
      name: 'Train',
      start: '2019-01-01 00:00:00',
      end: '2021-02-05 23:00:00',
      windows: 294160,
      percentage: 69.96,
      missing_pct: 2.57,
      description: 'Primary chronological training split (25 months)'
    },
    buffer_train_val: {
      name: 'Purged Buffer (Train-Val)',
      windows: 752,
      percentage: 0.18,
      description: '24h calendar buffer (2021-02-06, 25h physical gap) to eliminate leakage'
    },
    validation: {
      name: 'Validation',
      start: '2021-02-07 00:00:00',
      end: '2021-07-20 23:00:00',
      windows: 62608,
      percentage: 14.89,
      missing_pct: 2.96,
      description: 'Chronological validation split (5.5 months)'
    },
    buffer_val_test: {
      name: 'Purged Buffer (Val-Test)',
      windows: 752,
      percentage: 0.18,
      description: '24h calendar buffer (2021-07-21, 25h physical gap) to eliminate leakage'
    },
    test: {
      name: 'Test',
      start: '2021-07-22 00:00:00',
      end: '2021-12-31 23:00:00',
      windows: 62224,
      percentage: 14.80,
      missing_pct: 2.75,
      description: 'Chronological test split (5.3 months, benchmark evaluated)'
    }
  },
  missingness: {
    total_pollutant_missing_cells: 1335723,
    overall_missing_pct: 2.66,
    natural_missingness_preserved: true,
    benchmark_masks_count: 12
  }
};

/** 16 Hong Kong EPD Monitoring Stations with genuine coordinates */
export const HONG_KONG_STATIONS = [
  { id: 'CW', name: 'Central / Western', code: 'CW', station_id: 80, type: 'General', lat: 22.2848, lng: 114.1441, height_m: 16.0, district: 'Central and Western' },
  { id: 'E', name: 'Eastern', code: 'E', station_id: 73, type: 'General', lat: 22.2831, lng: 114.2190, height_m: 15.0, district: 'Eastern' },
  { id: 'KT', name: 'Kwun Tong', code: 'KT', station_id: 74, type: 'General', lat: 22.3107, lng: 114.2312, height_m: 15.0, district: 'Kwun Tong' },
  { id: 'SSP', name: 'Sham Shui Po', code: 'SSP', station_id: 66, type: 'General', lat: 22.3304, lng: 114.1591, height_m: 17.0, district: 'Sham Shui Po' },
  { id: 'KC', name: 'Kwai Chung', code: 'KC', station_id: 72, type: 'General', lat: 22.3569, lng: 114.1293, height_m: 13.0, district: 'Kwai Tsing' },
  { id: 'TW', name: 'Tsuen Wan', code: 'TW', station_id: 77, type: 'General', lat: 22.3715, lng: 114.1146, height_m: 17.0, district: 'Tsuen Wan' },
  { id: 'TKO', name: 'Tseung Kwan O', code: 'TKO', station_id: 83, type: 'General', lat: 22.3173, lng: 114.2596, height_m: 16.0, district: 'Sai Kung' },
  { id: 'YL', name: 'Yuen Long', code: 'YL', station_id: 70, type: 'General', lat: 22.4450, lng: 114.0227, height_m: 25.0, district: 'Yuen Long' },
  { id: 'TM', name: 'Tuen Mun', code: 'TM', station_id: 82, type: 'General', lat: 22.3911, lng: 113.9768, height_m: 27.0, district: 'Tuen Mun' },
  { id: 'TC', name: 'Tung Chung', code: 'TC', station_id: 78, type: 'General', lat: 22.2885, lng: 113.9431, height_m: 28.0, district: 'Islands' },
  { id: 'TP', name: 'Tai Po', code: 'TP', station_id: 69, type: 'General', lat: 22.4508, lng: 114.1644, height_m: 28.0, district: 'Tai Po' },
  { id: 'ST', name: 'Sha Tin', code: 'ST', station_id: 75, type: 'General', lat: 22.3764, lng: 114.1846, height_m: 25.0, district: 'Sha Tin' },
  { id: 'TMN', name: 'Tap Mun', code: 'TMN', station_id: 76, type: 'General (Rural Background)', lat: 22.4757, lng: 114.3619, height_m: 11.0, district: 'Tai Po' },
  { id: 'CB', name: 'Causeway Bay', code: 'CB', station_id: 71, type: 'Roadside', lat: 22.2801, lng: 114.1855, height_m: 3.0, district: 'Wan Chai' },
  { id: 'C', name: 'Central', code: 'C', station_id: 79, type: 'Roadside', lat: 22.2802, lng: 114.1606, height_m: 4.5, district: 'Central and Western' },
  { id: 'MK', name: 'Mong Kok', code: 'MK', station_id: 81, type: 'Roadside', lat: 22.3225, lng: 114.1685, height_m: 3.0, district: 'Yau Tsim Mong' }
];

/** 13 Canonical Continuous Channels in strict index ordering */
export const CANONICAL_CHANNELS = [
  { index: 0, id: 'pm25', name: 'PM2.5', label: 'PM2.5', unit: 'µg/m³', category: 'air_quality', group: 'Criteria Pollutants', desc: 'Fine Particulate Matter (<2.5 µm)', mean: 18.4007, std: 12.5468, min: 0.0, max: 167.0 },
  { index: 1, id: 'pm10', name: 'PM10', label: 'PM10', unit: 'µg/m³', category: 'air_quality', group: 'Criteria Pollutants', desc: 'Respirable Suspended Particulates (<10 µm)', mean: 31.1885, std: 20.0397, min: 0.0, max: 241.0 },
  { index: 2, id: 'no2', name: 'NO2', label: 'NO2', unit: 'µg/m³', category: 'air_quality', group: 'Criteria Pollutants', desc: 'Nitrogen Dioxide', mean: 43.7296, std: 32.0178, min: 0.0, max: 366.0 },
  { index: 3, id: 'so2', name: 'SO2', label: 'SO2', unit: 'µg/m³', category: 'air_quality', group: 'Criteria Pollutants', desc: 'Sulphur Dioxide', mean: 4.8857, std: 2.9916, min: 0.0, max: 81.0 },
  { index: 4, id: 'o3', name: 'O3', label: 'O3', unit: 'µg/m³', category: 'air_quality', group: 'Criteria Pollutants', desc: 'Ground-Level Ozone', mean: 51.4587, std: 39.3490, min: 0.0, max: 422.0 },
  { index: 5, id: 'pressure', name: 'Surface Pressure', label: 'Pressure', unit: 'hPa', category: 'meteorology', group: 'Meteorology', desc: 'Surface Atmospheric Pressure (ERA5)', mean: 1010.9061, std: 6.6221, min: 988.8, max: 1029.4 },
  { index: 6, id: 'relative_humidity', name: 'Relative Humidity', label: 'Humidity', unit: '%', category: 'meteorology', group: 'Meteorology', desc: 'Surface Relative Humidity (ERA5)', mean: 81.2846, std: 15.0711, min: 13.0, max: 100.0 },
  { index: 7, id: 'temperature', name: 'Temperature', label: 'Temperature', unit: '°C', category: 'meteorology', group: 'Meteorology', desc: '2-Meter Dry-Bulb Air Temperature (ERA5)', mean: 22.7707, std: 5.0677, min: 2.9, max: 35.6 },
  { index: 8, id: 'rainfall', name: 'Precipitation', label: 'Rainfall', unit: 'mm', category: 'meteorology', group: 'Meteorology', desc: 'Total Hourly Surface Precipitation (ERA5)', mean: 0.2320, std: 1.0006, min: 0.0, max: 61.8 },
  { index: 9, id: 'wind_direction', name: 'Wind Direction', label: 'Wind Direction', unit: '°', category: 'meteorology', group: 'Meteorology', desc: '10-Meter Wind Bearing (0°–360°)', mean: 116.8105, std: 80.0363, min: 1.0, max: 360.0 },
  { index: 10, id: 'wind_speed', name: 'Wind Speed', label: 'Wind Speed', unit: 'm/s', category: 'meteorology', group: 'Meteorology', desc: '10-Meter Wind Speed (ERA5)', mean: 3.5634, std: 1.7061, min: 0.0, max: 17.35 },
  { index: 11, id: 'traffic_speed', name: 'Traffic Speed', label: 'Traffic Speed', unit: 'km/h', category: 'traffic', group: 'Traffic Context', desc: 'Spatial-IDW Road Vehicular Speed', mean: 62.0280, std: 5.7545, min: 34.76, max: 146.66 },
  { index: 12, id: 'traffic_congestion', name: 'Traffic Congestion', label: 'Traffic Congestion', unit: '[0.0, 1.0]', category: 'traffic', group: 'Traffic Context', desc: 'Spatial-IDW Road Saturation Level', mean: 0.1196, std: 0.0626, min: 0.0, max: 0.7959 }
];

export const POLLUTANT_CHANNELS = CANONICAL_CHANNELS.filter(c => c.category === 'air_quality');
export const METEOROLOGY_CHANNELS = CANONICAL_CHANNELS.filter(c => c.category === 'meteorology');
export const TRAFFIC_CHANNELS = CANONICAL_CHANNELS.filter(c => c.category === 'traffic');

/** 12 Frozen Test Benchmark Mask Scenarios */
export const BENCHMARK_SCENARIOS = [
  { id: 'mcar_10', name: 'MCAR 10%', type: 'MCAR', rate: '10%', description: 'Missing completely at random (10% independent sensor dropout)', path: 'masks/mcar/mcar_10.npz' },
  { id: 'mcar_30', name: 'MCAR 30%', type: 'MCAR', rate: '30%', description: 'Missing completely at random (30% independent sensor dropout)', path: 'masks/mcar/mcar_30.npz' },
  { id: 'mcar_50', name: 'MCAR 50%', type: 'MCAR', rate: '50%', description: 'Missing completely at random (50% independent sensor dropout)', path: 'masks/mcar/mcar_50.npz' },
  { id: 'mcar_70', name: 'MCAR 70%', type: 'MCAR', rate: '70%', description: 'Missing completely at random (70% severe telemetry dropout)', path: 'masks/mcar/mcar_70.npz' },
  { id: 'station_outage_1', name: 'Station Outage (1)', type: 'Spatial Outage', rate: '1 Station', description: 'Complete 24h spatial blackout of 1 monitoring station', path: 'masks/station_outage/station_outage_1.npz' },
  { id: 'station_outage_2', name: 'Station Outage (2)', type: 'Spatial Outage', rate: '2 Stations', description: 'Complete 24h spatial blackout of 2 monitoring stations', path: 'masks/station_outage/station_outage_2.npz' },
  { id: 'station_outage_4', name: 'Station Outage (4)', type: 'Spatial Outage', rate: '4 Stations', description: 'Complete 24h spatial blackout of 4 monitoring stations', path: 'masks/station_outage/station_outage_4.npz' },
  { id: 'station_outage_full', name: 'Station Outage (Full)', type: 'Spatial Outage', rate: 'Full Blackout', description: 'Simultaneous multi-station spatial network blackout', path: 'masks/station_outage/station_outage_full.npz' },
  { id: 'block_10', name: 'Temporal Block 10%', type: 'Temporal Block', rate: '10%', description: 'Consecutive multi-hour burst sensor outage (10% duration)', path: 'masks/temporal_block/block_10.npz' },
  { id: 'block_30', name: 'Temporal Block 30%', type: 'Temporal Block', rate: '30%', description: 'Consecutive multi-hour burst sensor outage (30% duration)', path: 'masks/temporal_block/block_30.npz' },
  { id: 'block_50', name: 'Temporal Block 50%', type: 'Temporal Block', rate: '50%', description: 'Consecutive multi-hour burst sensor outage (50% duration)', path: 'masks/temporal_block/block_50.npz' },
  { id: 'block_70', name: 'Temporal Block 70%', type: 'Temporal Block', rate: '70%', description: 'Severe sustained sensor blackout (70% contiguous duration)', path: 'masks/temporal_block/block_70.npz' }
];

/** Architecture Specification for CTDI Spatial-Temporal Model */
export const MODEL_ARCHITECTURE_SPEC = {
  architecture: '1×1 Conv1D Spatial Feature Mixing + Multi-Head Temporal Transformer Encoder',
  version: 'CTDI CNN-Transformer v1.0',
  sequence_length: 24,
  input_channels: 13,
  input_features_with_mask: 26,
  d_model: 64,
  n_heads: 4,
  num_layers: 2,
  dim_feedforward: 128,
  dropout: 0.1,
  positional_encoding: 'Sinusoidal Temporal Encoding (24 hours)',
  loss_function: 'Masked L1 Loss (evaluated strictly at withheld target coordinates)',
  normalization: 'Z-Score Standardization (derived strictly from training split, zero leakage)'
};

/** Lifecycle state constants */
export const LIFECYCLE_STATES = {
  API_ONLINE: 'API_ONLINE',
  API_OFFLINE: 'API_OFFLINE',
  MODEL_NOT_TRAINED: 'MODEL_NOT_TRAINED',
  MODEL_LOADED: 'MODEL_LOADED',
  INFERENCE_AVAILABLE: 'INFERENCE_AVAILABLE',
  INFERENCE_UNAVAILABLE: 'INFERENCE_UNAVAILABLE',
  DATASET_AVAILABLE: 'DATASET_AVAILABLE'
};

/** Authoritative 13-channel studio color palette */
export const CHANNEL_PALETTE = {
  // Criteria Pollutants (5)
  'PM2.5': '#3B82F6', // Blue
  'PM10': '#8B5CF6',  // Purple
  'NO2': '#10B981',   // Emerald
  'SO2': '#F59E0B',   // Amber
  'O3': '#EC4899',    // Pink

  // Surface Meteorology (6)
  'Surface Pressure': '#06B6D4',   // Cyan
  'Relative Humidity': '#6366F1',  // Indigo
  'Temperature': '#F97316',        // Orange
  'Precipitation': '#3B82F6',      // Blue
  'Wind Direction': '#14B8A6',     // Teal
  'Wind Speed': '#84CC16',         // Lime

  // Traffic Context (2)
  'Traffic Speed': '#10B981',      // Emerald
  'Traffic Congestion': '#EF4444'  // Red
};
