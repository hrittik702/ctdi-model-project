import React, { useState, useMemo, useRef, useEffect } from 'react';
import { 
  Download, 
  Database, 
  Filter, 
  SlidersHorizontal, 
  CheckCircle2, 
  AlertCircle, 
  Layers, 
  ChevronDown, 
  Check,
  FileSpreadsheet,
  Clock,
  Activity,
  X,
  Eye,
  Info
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';
import { 
  CANONICAL_CHANNELS, 
  POLLUTANT_CHANNELS, 
  METEOROLOGY_CHANNELS, 
  TRAFFIC_CHANNELS,
  CHANNEL_PALETTE
} from '../constants/datasetContract';
import SectionHeading from '../components/ui/SectionHeading';

/**
 * Authoritative Channel Groupings for Segmented Selector
 */
const CHANNEL_GROUPS = [
  {
    id: 'criteria',
    label: 'Pollutants',
    badge: '5',
    channels: POLLUTANT_CHANNELS.map(c => c.name),
    desc: 'Criteria Atmospheric Pollutants (µg/m³)'
  },
  {
    id: 'meteorology',
    label: 'Meteorology',
    badge: '6',
    channels: METEOROLOGY_CHANNELS.map(c => c.name),
    desc: 'Surface Weather & ERA5 Physical Covariates'
  },
  {
    id: 'traffic',
    label: 'Traffic',
    badge: '2',
    channels: TRAFFIC_CHANNELS.map(c => c.name),
    desc: 'Spatial-IDW Road Velocity & Saturation'
  },
  {
    id: 'all',
    label: 'All Channels',
    badge: '13',
    channels: CANONICAL_CHANNELS.map(c => c.name),
    desc: 'Complete 13-Channel Multimodal Observation Tensor'
  }
];

/**
 * Concise scientific abbreviations and display units for analytical telemetry table
 */
const COMPACT_CHANNEL_MAP = {
  'PM2.5': { label: 'PM2.5', unit: 'µg/m³', fullName: 'PM2.5 Particulate Matter' },
  'PM10': { label: 'PM10', unit: 'µg/m³', fullName: 'PM10 Particulate Matter' },
  'NO2': { label: 'NO2', unit: 'µg/m³', fullName: 'Nitrogen Dioxide' },
  'SO2': { label: 'SO2', unit: 'µg/m³', fullName: 'Sulfur Dioxide' },
  'O3': { label: 'O3', unit: 'µg/m³', fullName: 'Ground-Level Ozone' },
  'Surface Pressure': { label: 'Pressure', unit: 'hPa', fullName: 'Surface Pressure (ERA5)' },
  'Relative Humidity': { label: 'RH', unit: '%', fullName: 'Relative Humidity (ERA5)' },
  'Temperature': { label: 'Temp', unit: '°C', fullName: '2m Ambient Temperature' },
  'Precipitation': { label: 'Rain', unit: 'mm', fullName: 'Hourly Precipitation (ERA5)' },
  'Wind Direction': { label: 'Wind °', unit: '°', fullName: '10m Wind Direction Bearing' },
  'Wind Speed': { label: 'Wind', unit: 'm/s', fullName: '10m Wind Speed (ERA5)' },
  'Traffic Speed': { label: 'Speed', unit: 'km/h', fullName: 'Spatial-IDW Road Speed' },
  'Traffic Congestion': { label: 'Cong.', unit: '0–1', fullName: 'Traffic Congestion Index' },
};

/**
 * Format raw timestamps into parsed hour and date representation
 */
function formatRowTimestamp(rawTs, hour, fallbackDate) {
  const clock = `${String(hour).padStart(2, '0')}:00`;
  if (!rawTs) {
    return {
      clockTime: clock,
      date: fallbackDate || '—',
      fullTimestamp: clock
    };
  }

  const parts = rawTs.split(' ');
  const rawDate = parts[0];
  const timePart = parts[1] ? parts[1].slice(0, 5) : clock;

  let formattedDate = rawDate;
  try {
    const iso = rawTs.includes('T') ? rawTs : rawTs.replace(' ', 'T') + 'Z';
    const d = new Date(iso);
    if (!isNaN(d.getTime())) {
      const weekday = d.toLocaleDateString('en-GB', { weekday: 'short', timeZone: 'UTC' });
      const day = d.getUTCDate();
      const month = d.toLocaleDateString('en-GB', { month: 'short', timeZone: 'UTC' });
      const year = d.getUTCFullYear();
      formattedDate = `${weekday} · ${day} ${month} ${year}`;
    }
  } catch {
    formattedDate = rawDate;
  }

  return {
    clockTime: timePart,
    date: formattedDate,
    fullTimestamp: rawTs
  };
}

/**
 * Custom Tooltip for 24-Hour Visual Overview Chart
 */
function CustomOverviewTooltip({ active, payload, label, channelMap }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="bg-white/95 dark:bg-[#111113]/95 backdrop-blur-md border border-slate-200/90 dark:border-white/[0.08] shadow-2xl p-3.5 rounded-xl text-xs space-y-2 min-w-[220px] max-w-xs z-50">
      <div className="font-mono font-bold text-slate-900 dark:text-[#F4F4F5] border-b border-slate-100 dark:border-white/[0.06] pb-1.5 flex items-center justify-between">
        <span className="text-sm font-extrabold">{label}</span>
        <span className="text-[10px] text-slate-400 dark:text-zinc-500 font-sans">24h Window Step</span>
      </div>
      <div className="space-y-1.5 pt-0.5 max-h-52 overflow-y-auto pr-1">
        {payload.map(item => {
          const ch = item.name;
          const val = item.value;
          const meta = channelMap[ch] || {};
          const color = CHANNEL_PALETTE[ch] || item.color || '#6366F1';
          return (
            <div key={ch} className="flex items-center justify-between gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-slate-600 dark:text-zinc-300 truncate">
                <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: color }} />
                <span className="font-mono text-[11px] font-semibold">{ch}</span>
              </span>
              <span className="font-mono text-xs font-bold text-slate-900 dark:text-[#F4F4F5] shrink-0">
                {val !== null && val !== undefined ? `${val} ${meta.unit || ''}` : 'NaN (Missing)'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function DataExplorerView({
  sampleData,
  sampleIdx = 0,
  pollutants = [],
  stationName = 'Central / Western',
  isDark = false,
  gridStroke = '#e2e8f0',
  axisStroke = '#94a3b8'
}) {
  // Category preset state: 'all' | 'criteria' | 'meteorology' | 'traffic'
  const [activePreset, setActivePreset] = useState('all');

  // Observation filter mode: 'all' | 'observed' | 'missing'
  const [filterMode, setFilterMode] = useState('all');

  // Advanced custom channel filter popover
  const [isColumnPickerOpen, setIsColumnPickerOpen] = useState(false);
  const columnPickerRef = useRef(null);

  // Active custom visible channel override (null when using preset)
  const [customVisibleChannels, setCustomVisibleChannels] = useState(null);

  // Row Inspection state (hour of selected row, null when none)
  const [selectedRowHour, setSelectedRowHour] = useState(null);

  // Close column picker on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (columnPickerRef.current && !columnPickerRef.current.contains(event.target)) {
        setIsColumnPickerOpen(false);
      }
    }
    if (isColumnPickerOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isColumnPickerOpen]);

  // Fast channel lookup dictionary
  const channelMap = useMemo(() => {
    const map = {};
    CANONICAL_CHANNELS.forEach(c => { map[c.name] = c; });
    return map;
  }, []);

  // Determine currently displayed channels for table and chart
  const activeChannels = useMemo(() => {
    if (customVisibleChannels) return customVisibleChannels;
    const group = CHANNEL_GROUPS.find(g => g.id === activePreset) || CHANNEL_GROUPS[0];
    return group.channels;
  }, [activePreset, customVisibleChannels]);

  // Active group definition
  const activeGroup = useMemo(() => {
    return CHANNEL_GROUPS.find(g => g.id === activePreset) || CHANNEL_GROUPS[0];
  }, [activePreset]);

  // Handle switching preset (resets custom column overrides and selected row)
  const handleSelectPreset = (presetId) => {
    setActivePreset(presetId);
    setCustomVisibleChannels(null);
  };

  // Toggle individual channel visibility in advanced menu
  const handleToggleChannel = (channelName) => {
    const currentList = customVisibleChannels || activeChannels;
    let nextList;
    if (currentList.includes(channelName)) {
      if (currentList.length <= 1) return; // Keep at least one channel
      nextList = currentList.filter(c => c !== channelName);
    } else {
      nextList = [...currentList, channelName];
    }
    setCustomVisibleChannels(nextList);
  };

  const hours = sampleData?.hours || Array.from({ length: 24 }, (_, i) => i);
  const timestamps = sampleData?.timestamps || [];

  // Format contextual date from sample timestamps
  const rawFirstTimestamp = timestamps[0] || '';
  let formattedDate = 'Historical Sequence';
  if (rawFirstTimestamp) {
    try {
      const d = new Date(rawFirstTimestamp.replace(' ', 'T') + 'Z');
      if (!isNaN(d.getTime())) {
        formattedDate = d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
      }
    } catch {
      formattedDate = rawFirstTimestamp.split(' ')[0] || 'Historical Sequence';
    }
  }

  // Group counts for currently active channels (for grouped table headers)
  const pollutantActive = useMemo(
    () => activeChannels.filter(ch => POLLUTANT_CHANNELS.some(p => p.name === ch)),
    [activeChannels]
  );
  const metActive = useMemo(
    () => activeChannels.filter(ch => METEOROLOGY_CHANNELS.some(m => m.name === ch)),
    [activeChannels]
  );
  const trafficActive = useMemo(
    () => activeChannels.filter(ch => TRAFFIC_CHANNELS.some(t => t.name === ch)),
    [activeChannels]
  );

  // Build comprehensive row objects for table display & row inspection
  const rows = useMemo(() => {
    return hours.map((hour, idx) => {
      const rawTs = timestamps[idx];
      const parsed = formatRowTimestamp(rawTs, hour, formattedDate);
      
      const row = {
        hour,
        clockTime: parsed.clockTime,
        date: parsed.date,
        timestamp: parsed.fullTimestamp,
        values: {},
        masks: {},
        allValues: {},
        allMasks: {},
        rowMissingCount: 0,
        isFullyObserved: true
      };

      // Store values for currently active channels
      activeChannels.forEach(ch => {
        const polObj = sampleData?.pollutants?.[ch];
        const val = polObj?.actual?.[idx];
        const isObs = polObj?.observed_mask?.[idx] === 1;
        
        row.values[ch] = (val !== null && val !== undefined) ? Number(val.toFixed(2)) : null;
        row.masks[ch] = isObs;

        if (!isObs) {
          row.rowMissingCount += 1;
          row.isFullyObserved = false;
        }
      });

      // Always cache complete 13-channel snapshot for row inspect mode
      CANONICAL_CHANNELS.forEach(ch => {
        const polObj = sampleData?.pollutants?.[ch.name];
        const val = polObj?.actual?.[idx];
        const isObs = polObj?.observed_mask?.[idx] === 1;
        row.allValues[ch.name] = (val !== null && val !== undefined) ? Number(val.toFixed(2)) : null;
        row.allMasks[ch.name] = isObs;
      });

      return row;
    });
  }, [hours, timestamps, activeChannels, sampleData, formattedDate]);

  // Overall sequence observability across ALL 13 channels (Strictly Truthful)
  const overallStats = useMemo(() => {
    const totalChannels = CANONICAL_CHANNELS.length; // 13
    const totalHours = hours.length; // 24
    const totalCells = totalChannels * totalHours; // 312
    let totalObserved = 0;

    CANONICAL_CHANNELS.forEach(ch => {
      const polObj = sampleData?.pollutants?.[ch.name];
      const mask = polObj?.observed_mask || [];
      const obsCount = mask.filter(m => m === 1).length;
      totalObserved += obsCount;
    });

    const missingCells = totalCells - totalObserved;
    const completenessPct = totalCells > 0 ? ((totalObserved / totalCells) * 100).toFixed(1) : '100.0';

    return {
      totalHours,
      totalChannels,
      totalCells,
      validCells: totalObserved,
      missingCells,
      completenessPct
    };
  }, [hours, sampleData]);

  // Filter rows based on filterMode
  const filteredRows = useMemo(() => {
    return rows.filter(r => {
      if (filterMode === 'observed') return r.isFullyObserved;
      if (filterMode === 'missing') return !r.isFullyObserved;
      return true;
    });
  }, [rows, filterMode]);

  // 24-Hour Visual Overview Chart Data
  const visualChartData = useMemo(() => {
    return hours.map((hour, idx) => {
      const clockTime = timestamps[idx]?.includes(' ') 
        ? timestamps[idx].split(' ')[1] 
        : `${String(hour).padStart(2, '0')}:00`;
      
      const point = {
        hour: clockTime,
        time: clockTime,
        stepOffset: `+${idx}h`,
        timestamp: timestamps[idx] || `${formattedDate} ${clockTime}`
      };

      activeChannels.forEach(ch => {
        const polObj = sampleData?.pollutants?.[ch];
        const val = polObj?.actual?.[idx];
        const isObs = polObj?.observed_mask?.[idx] === 1;
        point[ch] = (isObs && val !== null && val !== undefined) ? Number(val.toFixed(2)) : null;
      });

      return point;
    });
  }, [hours, timestamps, activeChannels, sampleData, formattedDate]);

  // High-resolution scientific CSV export
  const handleExportCSV = () => {
    const safeStation = (stationName || 'HongKong_EPD').replace(/[^a-zA-Z0-9]/g, '_');
    const metadataHeader = [
      `# CTDI Air Pollution Imputation Studio - 24-Hour Telemetry Export`,
      `# Station: ${stationName}`,
      `# Window Index: ${sampleIdx + 1} / 26281`,
      `# Date Range: ${formattedDate} (00:00 to 23:00 UTC)`,
      `# Generated: ${new Date().toISOString()}`,
      `# Channels: ${activeChannels.join(', ')}`
    ].join('\n');

    const headers = ['Hour', 'Timestamp', ...activeChannels, 'Row_Missing_Count', 'Observation_Status'];
    const csvRows = rows.map(r => [
      r.clockTime,
      r.timestamp,
      ...activeChannels.map(ch => r.masks[ch] ? r.values[ch] : 'NaN'),
      r.rowMissingCount,
      r.isFullyObserved ? '100%_Observed' : `${r.rowMissingCount}_Natural_Dropouts`
    ].join(','));

    const content = 'data:text/csv;charset=utf-8,' + encodeURIComponent(`${metadataHeader}\n${headers.join(',')}\n${csvRows.join('\n')}`);
    const a = document.createElement('a');
    a.href = content;
    a.download = `Station_${safeStation}_Window_${sampleIdx + 1}_24h_telemetry.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  // Find currently inspected row
  const inspectedRow = useMemo(() => {
    if (selectedRowHour === null) return null;
    return rows.find(r => r.hour === selectedRowHour) || null;
  }, [selectedRowHour, rows]);

  return (
    <div className="space-y-5 pb-12">
      {/* 1. Page Identity Header (with ~10% top margin & scroll morphing) */}
      <div>
        <SectionHeading
          id="data-explorer"
          title="Data Explorer"
          icon="data"
        />
        <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-zinc-400 mt-1 pl-0.5">
          <strong className="text-slate-800 dark:text-zinc-200 font-semibold">{stationName}</strong>
          <span className="text-slate-300 dark:text-zinc-700">·</span>
          <span>{formattedDate}</span>
          <span className="text-slate-300 dark:text-zinc-700">·</span>
          <span>00:00–23:00</span>
          <span className="ml-1 text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200/70 dark:border-indigo-800/60">
            Window {sampleIdx + 1} / 26,281
          </span>
        </div>
      </div>

      {/* 2. Compact Sequence Summary (4 Truthful Derived Cards) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Card 1: Sequence Length */}
        <div className="p-3.5 sm:p-4 rounded-2xl border border-slate-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/90 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
              Sequence Window
            </span>
            <Clock className="w-4 h-4 text-indigo-500 shrink-0" />
          </div>
          <div className="mt-2.5">
            <div className="text-xl sm:text-2xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-zinc-100">
              {overallStats.totalHours} Hours
            </div>
            <p className="mt-0.5 text-xs text-slate-500 dark:text-zinc-400 truncate">
              00:00 – 23:00 (100% Window)
            </p>
          </div>
        </div>

        {/* Card 2: Multimodal Channels */}
        <div className="p-3.5 sm:p-4 rounded-2xl border border-slate-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/90 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
              Multimodal Tensor
            </span>
            <Layers className="w-4 h-4 text-purple-500 shrink-0" />
          </div>
          <div className="mt-2.5">
            <div className="text-xl sm:text-2xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-zinc-100">
              {overallStats.totalChannels} Channels
            </div>
            <p className="mt-0.5 text-xs text-slate-500 dark:text-zinc-400 truncate">
              5 Pollutants · 6 Met · 2 Traffic
            </p>
          </div>
        </div>

        {/* Card 3: Observed Measurements */}
        <div className="p-3.5 sm:p-4 rounded-2xl border border-slate-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/90 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
              Observed Cells
            </span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
          </div>
          <div className="mt-2.5">
            <div className="text-xl sm:text-2xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-zinc-100">
              {overallStats.validCells} / {overallStats.totalCells}
            </div>
            <p className="mt-0.5 text-xs text-emerald-600 dark:text-emerald-400 font-semibold truncate">
              {overallStats.completenessPct}% Verified Telemetry
            </p>
          </div>
        </div>

        {/* Card 4: Natural Dropouts */}
        <div className="p-3.5 sm:p-4 rounded-2xl border border-slate-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/90 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
              Natural Missing
            </span>
            <AlertCircle className={`w-4 h-4 shrink-0 ${overallStats.missingCells > 0 ? 'text-amber-500' : 'text-slate-400'}`} />
          </div>
          <div className="mt-2.5">
            <div className={`text-xl sm:text-2xl font-extrabold font-mono tracking-tight ${overallStats.missingCells > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-900 dark:text-zinc-100'}`}>
              {overallStats.missingCells} Dropouts
            </div>
            <p className="mt-0.5 text-xs text-slate-500 dark:text-zinc-400 truncate">
              {overallStats.missingCells > 0 
                ? `${((overallStats.missingCells / overallStats.totalCells) * 100).toFixed(1)}% natural sensor dropouts` 
                : 'Zero missing values in window'}
            </p>
          </div>
        </div>
      </div>

      {/* 3. Segmented Channel Navigation & Action Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
        {/* Left: Segmented Channel Group Selector */}
        <div className="inline-flex p-1 rounded-xl bg-slate-200/70 dark:bg-zinc-800/80 border border-slate-200/80 dark:border-zinc-700/60 text-xs select-none">
          {CHANNEL_GROUPS.map(group => {
            const isSelected = activePreset === group.id && !customVisibleChannels;
            return (
              <button
                key={group.id}
                type="button"
                onClick={() => handleSelectPreset(group.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition cursor-pointer motion-press motion-tab-active ${
                  isSelected
                    ? 'bg-white dark:bg-zinc-900 text-slate-900 dark:text-zinc-100 font-bold shadow-xs'
                    : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-200'
                }`}
              >
                <span>{group.label}</span>
                <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                  isSelected 
                    ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-bold' 
                    : 'bg-slate-300/60 dark:bg-zinc-700/60 text-slate-500 dark:text-zinc-400'
                }`}>
                  {group.badge}
                </span>
              </button>
            );
          })}
        </div>

        {/* Right: Custom Filter Popover + Observation Filter + Export CSV */}
        <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
          {/* Advanced Column Customizer Popover */}
          <div className="relative" ref={columnPickerRef}>
            <button
              type="button"
              onClick={() => setIsColumnPickerOpen(prev => !prev)}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border text-xs font-semibold transition cursor-pointer motion-press ${
                customVisibleChannels 
                  ? 'bg-indigo-50 dark:bg-indigo-950/50 border-indigo-300 dark:border-indigo-700 text-indigo-700 dark:text-indigo-300'
                  : 'bg-white dark:bg-zinc-900/90 border-slate-200/80 dark:border-zinc-800 text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-200 shadow-2xs'
              }`}
              title="Customize specific columns"
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>Filters {customVisibleChannels ? `(${activeChannels.length})` : ''}</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </button>

            {isColumnPickerOpen && (
              <div className="absolute right-0 top-full mt-2 w-72 bg-white dark:bg-zinc-900 border border-slate-200/90 dark:border-zinc-800 rounded-2xl shadow-xl p-3 z-50 text-xs motion-popover-enter">
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 dark:border-zinc-800">
                  <span className="font-bold text-slate-900 dark:text-zinc-100">
                    Visible Channels
                  </span>
                  {customVisibleChannels && (
                    <button
                      type="button"
                      onClick={() => setCustomVisibleChannels(null)}
                      className="text-[10px] text-indigo-600 dark:text-indigo-400 hover:underline font-semibold cursor-pointer"
                    >
                      Reset to Preset
                    </button>
                  )}
                </div>
                <div className="max-h-60 overflow-y-auto space-y-1">
                  {CANONICAL_CHANNELS.map(ch => {
                    const isVisible = activeChannels.includes(ch.name);
                    return (
                      <button
                        key={ch.name}
                        type="button"
                        onClick={() => handleToggleChannel(ch.name)}
                        className={`w-full flex items-center justify-between px-2 py-1.5 rounded-lg transition cursor-pointer text-left ${
                          isVisible
                            ? 'bg-indigo-50/70 dark:bg-indigo-950/40 text-indigo-900 dark:text-indigo-200 font-semibold'
                            : 'text-slate-500 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-800'
                        }`}
                      >
                        <div className="flex items-center gap-2 min-w-0">
                          <span className={`w-3.5 h-3.5 rounded border flex items-center justify-center shrink-0 ${
                            isVisible 
                              ? 'bg-indigo-600 border-indigo-600 text-white' 
                              : 'border-slate-300 dark:border-zinc-600'
                          }`}>
                            {isVisible && <Check className="w-2.5 h-2.5 stroke-[3]" />}
                          </span>
                          <span className="font-mono text-xs truncate">{ch.name}</span>
                        </div>
                        <span className="text-[10px] text-slate-400 font-mono shrink-0 ml-2">
                          {ch.unit}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Row Observability Filter */}
          <div className="inline-flex p-1 rounded-xl bg-slate-200/70 dark:bg-zinc-800/80 text-xs border border-slate-200/80 dark:border-zinc-700/60">
            <button
              type="button"
              onClick={() => setFilterMode('all')}
              className={`px-2.5 py-1 rounded-lg font-medium transition cursor-pointer motion-press motion-tab-active ${
                filterMode === 'all'
                  ? 'bg-white dark:bg-zinc-900 text-slate-900 dark:text-zinc-100 font-bold shadow-xs'
                  : 'text-slate-500 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-zinc-200'
              }`}
            >
              All (24h)
            </button>
            <button
              type="button"
              onClick={() => setFilterMode('observed')}
              className={`px-2.5 py-1 rounded-lg font-medium transition cursor-pointer motion-press motion-tab-active ${
                filterMode === 'observed'
                  ? 'bg-white dark:bg-zinc-900 text-blue-600 dark:text-blue-400 font-bold shadow-xs'
                  : 'text-slate-500 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-zinc-200'
              }`}
            >
              Observed
            </button>
            <button
              type="button"
              onClick={() => setFilterMode('missing')}
              className={`px-2.5 py-1 rounded-lg font-medium transition cursor-pointer motion-press motion-tab-active ${
                filterMode === 'missing'
                  ? 'bg-white dark:bg-zinc-900 text-amber-600 dark:text-amber-400 font-bold shadow-xs'
                  : 'text-slate-500 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-zinc-200'
              }`}
            >
              Dropouts
            </button>
          </div>

          {/* Export CSV Button */}
          <button
            type="button"
            onClick={handleExportCSV}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white dark:bg-zinc-900/90 text-slate-700 dark:text-zinc-200 hover:bg-slate-100 dark:hover:bg-zinc-800 text-xs font-semibold transition cursor-pointer border border-slate-200/80 dark:border-zinc-800 shadow-2xs motion-press"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
            <span className="hidden sm:inline">Export CSV</span>
          </button>
        </div>
      </div>

      {/* 4. Visual 24-Hour Sequence Overview Chart */}
      <div className="bg-white dark:bg-zinc-900/95 p-4 sm:p-5 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-zinc-800/80 pb-3">
          <div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <h3 className="font-extrabold text-slate-900 dark:text-zinc-100 text-sm sm:text-base tracking-tight">
                24-Hour Sequence Overview
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
              {activeGroup.desc} ({activeChannels.length} active channels displayed)
            </p>
          </div>

          {/* Channel Color Pills Legend */}
          <div className="flex items-center gap-2 flex-wrap">
            {activeChannels.slice(0, 7).map(ch => (
              <span 
                key={ch} 
                className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-mono font-semibold bg-slate-50 dark:bg-zinc-800/80 border border-slate-200/60 dark:border-zinc-700/60 text-slate-700 dark:text-zinc-300"
              >
                <span 
                  className="w-2 h-2 rounded-full shrink-0" 
                  style={{ backgroundColor: CHANNEL_PALETTE[ch] || '#6366F1' }} 
                />
                <span>{ch}</span>
              </span>
            ))}
            {activeChannels.length > 7 && (
              <span className="text-[10px] text-slate-400 dark:text-zinc-500 font-mono">
                +{activeChannels.length - 7} more
              </span>
            )}
          </div>
        </div>

        {/* Multi-Series Line Chart */}
        <div className="h-[210px] w-full pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={visualChartData} margin={{ top: 8, right: 16, left: -16, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} opacity={0.6} />
              <XAxis 
                dataKey="time" 
                stroke={axisStroke} 
                fontSize={11} 
                tickLine={false} 
                interval="preserveStartEnd" 
              />
              <YAxis 
                stroke={axisStroke} 
                fontSize={11} 
                tickLine={false} 
              />
              <Tooltip 
                content={<CustomOverviewTooltip channelMap={channelMap} />} 
              />
              {activeChannels.map(ch => (
                <Line
                  key={ch}
                  type="monotone"
                  dataKey={ch}
                  name={ch}
                  stroke={CHANNEL_PALETTE[ch] || '#6366F1'}
                  strokeWidth={1.8}
                  dot={false}
                  activeDot={{ r: 4, strokeWidth: 1 }}
                  connectNulls={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 5. Detailed Telemetry Table (with Sticky Identifiers & Grouped Headers) */}
      <div className="bg-white dark:bg-zinc-900/95 p-4 sm:p-5 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-zinc-800/80 pb-3">
          <div>
            <h3 className="font-extrabold text-slate-900 dark:text-zinc-100 text-sm sm:text-base tracking-tight">
              Detailed Telemetry
            </h3>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
              Displaying {filteredRows.length} hourly steps · Click any row to inspect all 13 channels
            </p>
          </div>
          {selectedRowHour !== null && (
            <button
              type="button"
              onClick={() => setSelectedRowHour(null)}
              className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline font-semibold flex items-center gap-1 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
              <span>Close Inspect Mode</span>
            </button>
          )}
        </div>

        {/* Sticky-Header & Sticky-Hour Table Container */}
        <div className="overflow-x-auto rounded-xl border border-slate-200/80 dark:border-zinc-800 max-h-[540px] relative">
          <table className="w-full text-left text-xs whitespace-nowrap border-collapse">
            <thead className="sticky top-0 bg-slate-50 dark:bg-zinc-900 shadow-2xs z-20 border-b border-slate-200 dark:border-zinc-800">
              {/* Row 1: Scientific Group Headers */}
              <tr className="border-b border-slate-200/70 dark:border-zinc-800 text-[10px] font-extrabold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
                {/* Row Status Header */}
                <th 
                  rowSpan={2} 
                  className="sticky left-0 bg-slate-50 dark:bg-zinc-900 z-30 py-2 px-1 text-center w-8 min-w-[32px] max-w-[32px] border-r border-slate-200/80 dark:border-zinc-800 select-none text-slate-400 dark:text-zinc-500"
                  title="Row Observability Status"
                >
                  ✓
                </th>
                {/* Hour Header */}
                <th 
                  rowSpan={2} 
                  className="sticky left-[32px] bg-slate-50 dark:bg-zinc-900 z-30 py-2 px-2.5 text-left text-[11px] font-bold font-mono uppercase tracking-wider text-slate-700 dark:text-zinc-300 w-14 min-w-[56px] border-r border-slate-200/80 dark:border-zinc-800"
                >
                  Hour
                </th>
                {/* Parsed Date Header */}
                <th 
                  rowSpan={2} 
                  className="py-2 px-2.5 text-left text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400 border-r border-slate-200/80 dark:border-zinc-800 w-36 min-w-[124px]"
                >
                  Date
                </th>

                {/* Group Category Headers */}
                {pollutantActive.length > 0 && (
                  <th 
                    colSpan={pollutantActive.length} 
                    className="py-1 px-2 text-center text-[10px] font-extrabold uppercase tracking-widest text-blue-600 dark:text-blue-400 bg-blue-50/40 dark:bg-blue-950/20 border-r border-slate-200/80 dark:border-zinc-800 font-sans"
                  >
                    AIR QUALITY
                  </th>
                )}
                {metActive.length > 0 && (
                  <th 
                    colSpan={metActive.length} 
                    className={`py-1 px-2 text-center text-[10px] font-extrabold uppercase tracking-widest text-indigo-600 dark:text-indigo-400 bg-indigo-50/40 dark:bg-indigo-950/20 font-sans ${
                      trafficActive.length > 0 ? 'border-r border-slate-200/80 dark:border-zinc-800' : ''
                    }`}
                  >
                    METEOROLOGY
                  </th>
                )}
                {trafficActive.length > 0 && (
                  <th 
                    colSpan={trafficActive.length} 
                    className="py-1 px-2 text-center text-[10px] font-extrabold uppercase tracking-widest text-emerald-600 dark:text-emerald-400 bg-emerald-50/40 dark:bg-emerald-950/20 font-sans"
                  >
                    TRAFFIC
                  </th>
                )}
              </tr>

              {/* Row 2: Compact Channel Labels & Units */}
              <tr className="text-slate-500 dark:text-zinc-400 font-bold text-[11px]">
                {activeChannels.map((ch) => {
                  const meta = COMPACT_CHANNEL_MAP[ch] || { label: ch, unit: '', fullName: ch };
                  const isGroupEnd = (
                    (pollutantActive.length > 0 && ch === pollutantActive[pollutantActive.length - 1] && (metActive.length > 0 || trafficActive.length > 0)) ||
                    (metActive.length > 0 && ch === metActive[metActive.length - 1] && trafficActive.length > 0)
                  );
                  return (
                    <th 
                      key={ch} 
                      className={`py-1.5 px-2 font-mono select-none text-center ${
                        isGroupEnd ? 'border-r border-slate-200/80 dark:border-zinc-800' : ''
                      }`}
                      title={`${meta.fullName} (${meta.unit})`}
                    >
                      <div className="flex flex-col leading-tight items-center">
                        <span className="text-slate-800 dark:text-zinc-200 font-bold">{meta.label}</span>
                        <span className="text-[9px] text-slate-400 dark:text-zinc-500 font-sans font-normal tracking-tight">
                          {meta.unit}
                        </span>
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/80 font-mono">
              {filteredRows.length === 0 ? (
                <tr>
                  <td colSpan={activeChannels.length + 3} className="py-12 text-center text-slate-400 dark:text-zinc-500 font-sans">
                    No rows match the selected filter mode ({filterMode}).
                  </td>
                </tr>
              ) : (
                filteredRows.map(r => {
                  const isRowSelected = selectedRowHour === r.hour;
                  return (
                    <tr 
                      key={r.hour} 
                      onClick={() => setSelectedRowHour(prev => (prev === r.hour ? null : r.hour))}
                      className={`transition-colors cursor-pointer ${
                        isRowSelected
                          ? 'bg-indigo-50/70 dark:bg-indigo-950/40'
                          : 'hover:bg-slate-50/80 dark:hover:bg-zinc-800/40'
                      }`}
                      title="Click to inspect all 13 channels for this hour"
                    >
                      {/* 1. Row Observability Status Indicator */}
                      <td className={`sticky left-0 z-10 py-2 px-1 text-center w-8 min-w-[32px] max-w-[32px] border-r border-slate-200/60 dark:border-zinc-800/80 transition-colors ${
                        isRowSelected
                          ? 'bg-indigo-50/90 dark:bg-[#14141e]'
                          : 'bg-white dark:bg-zinc-900'
                      }`}>
                        {r.isFullyObserved ? (
                          <span 
                            className="inline-flex items-center justify-center text-emerald-500 dark:text-emerald-400"
                            title="Complete row · All displayed channels valid"
                          >
                            <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                          </span>
                        ) : (
                          <span 
                            className="inline-flex items-center justify-center text-amber-500 dark:text-amber-400"
                            title={`Contains ${r.rowMissingCount} natural missing value${r.rowMissingCount > 1 ? 's' : ''}`}
                          >
                            <AlertCircle className="w-3.5 h-3.5 stroke-[2]" />
                          </span>
                        )}
                      </td>

                      {/* 2. Sticky Hour Column */}
                      <td className={`sticky left-[32px] z-10 py-2 px-2.5 font-bold font-mono text-xs border-r border-slate-200/60 dark:border-zinc-800/80 transition-colors ${
                        isRowSelected
                          ? 'bg-indigo-50/90 dark:bg-[#14141e] text-indigo-600 dark:text-indigo-400'
                          : 'bg-white dark:bg-zinc-900 text-slate-900 dark:text-zinc-100'
                      }`}>
                        {r.clockTime}
                      </td>

                      {/* 3. Parsed Date Column */}
                      <td 
                        className="py-2 px-2.5 font-sans text-xs text-slate-500 dark:text-zinc-400 border-r border-slate-200/60 dark:border-zinc-800/80 whitespace-nowrap"
                        title={r.timestamp}
                      >
                        {r.date}
                      </td>

                      {/* 4. Active Channel Value Cells */}
                      {activeChannels.map(ch => {
                        const isObs = r.masks[ch];
                        const val = r.values[ch];
                        const meta = COMPACT_CHANNEL_MAP[ch] || { label: ch, unit: '', fullName: ch };
                        const isGroupEnd = (
                          (pollutantActive.length > 0 && ch === pollutantActive[pollutantActive.length - 1] && (metActive.length > 0 || trafficActive.length > 0)) ||
                          (metActive.length > 0 && ch === metActive[metActive.length - 1] && trafficActive.length > 0)
                        );
                        return (
                          <td 
                            key={ch} 
                            className={`py-2 px-2 font-mono text-xs text-center ${
                              isGroupEnd ? 'border-r border-slate-200/60 dark:border-zinc-800/80' : ''
                            }`}
                            title={`${meta.fullName}: ${isObs && val !== null && val !== undefined ? `${val} ${meta.unit}` : 'Missing (NaN)'}`}
                          >
                            {isObs && val !== null && val !== undefined ? (
                              <span className="text-slate-800 dark:text-zinc-100 font-medium">
                                {val}
                              </span>
                            ) : (
                              <span className="text-amber-500/90 dark:text-amber-400/90 font-bold" title="Natural missing sensor dropout (NaN)">
                                —
                              </span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* 6. Row Inspection Drawer (Expands upon row click to inspect all 13 channels without horizontal scroll) */}
        {inspectedRow && (
          <div className="bg-slate-50/90 dark:bg-zinc-950/90 p-4 sm:p-5 rounded-2xl border border-indigo-200/80 dark:border-indigo-900/60 shadow-lg space-y-4 animate-in fade-in slide-in-from-top-2 duration-200">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-zinc-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-extrabold font-mono text-xs border border-indigo-200/60 dark:border-indigo-800/60">
                  {inspectedRow.clockTime}
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <h4 className="font-extrabold text-slate-900 dark:text-zinc-100 text-sm">
                      Complete 13-Channel Snapshot for {inspectedRow.clockTime}
                    </h4>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 font-bold border border-indigo-200/60 dark:border-indigo-800/60">
                      {inspectedRow.timestamp}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                    Inspect all 13 atmospheric and mobility channels for this step without horizontal scrolling.
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelectedRowHour(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-zinc-200 hover:bg-slate-200/60 dark:hover:bg-zinc-800 transition cursor-pointer"
                title="Close Snapshot Inspector"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* 3 Categories: Pollutants, Meteorology, Traffic */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
              {/* Criteria Pollutants (5) */}
              <div className="p-3.5 rounded-xl bg-white dark:bg-zinc-900/90 border border-slate-200/70 dark:border-zinc-800 space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 flex items-center justify-between">
                  <span>Criteria Pollutants</span>
                  <span className="text-indigo-600 dark:text-indigo-400 font-mono text-[10px]">5 Channels</span>
                </span>
                <div className="space-y-1.5 divide-y divide-slate-100 dark:divide-zinc-800/60 text-xs">
                  {POLLUTANT_CHANNELS.map(ch => {
                    const isObs = inspectedRow.allMasks[ch.name];
                    const val = inspectedRow.allValues[ch.name];
                    return (
                      <div key={ch.name} className="pt-1.5 first:pt-0 flex items-center justify-between">
                        <span className="font-mono font-medium text-slate-700 dark:text-zinc-300">{ch.name}</span>
                        {isObs ? (
                          <span className="font-mono font-bold text-slate-900 dark:text-zinc-100">
                            {val} <span className="text-[10px] text-slate-400 font-normal">{ch.unit}</span>
                          </span>
                        ) : (
                          <span className="text-[10px] font-mono text-amber-600 dark:text-amber-400 font-bold bg-amber-50 dark:bg-amber-950/40 px-1.5 py-0.2 rounded border border-amber-200/60 dark:border-amber-800/60">
                            NaN (Dropout)
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Surface Meteorology (6) */}
              <div className="p-3.5 rounded-xl bg-white dark:bg-zinc-900/90 border border-slate-200/70 dark:border-zinc-800 space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 flex items-center justify-between">
                  <span>Surface Meteorology</span>
                  <span className="text-blue-600 dark:text-blue-400 font-mono text-[10px]">6 Channels</span>
                </span>
                <div className="space-y-1.5 divide-y divide-slate-100 dark:divide-zinc-800/60 text-xs">
                  {METEOROLOGY_CHANNELS.map(ch => {
                    const isObs = inspectedRow.allMasks[ch.name];
                    const val = inspectedRow.allValues[ch.name];
                    return (
                      <div key={ch.name} className="pt-1.5 first:pt-0 flex items-center justify-between">
                        <span className="font-mono font-medium text-slate-700 dark:text-zinc-300 truncate mr-2" title={ch.name}>
                          {ch.label || ch.name}
                        </span>
                        {isObs ? (
                          <span className="font-mono font-bold text-slate-900 dark:text-zinc-100 shrink-0">
                            {val} <span className="text-[10px] text-slate-400 font-normal">{ch.unit}</span>
                          </span>
                        ) : (
                          <span className="text-[10px] font-mono text-amber-600 dark:text-amber-400 font-bold bg-amber-50 dark:bg-amber-950/40 px-1.5 py-0.2 rounded border border-amber-200/60 dark:border-amber-800/60 shrink-0">
                            NaN (Dropout)
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Traffic Context (2) */}
              <div className="p-3.5 rounded-xl bg-white dark:bg-zinc-900/90 border border-slate-200/70 dark:border-zinc-800 space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 flex items-center justify-between">
                  <span>Traffic Context</span>
                  <span className="text-emerald-600 dark:text-emerald-400 font-mono text-[10px]">2 Channels</span>
                </span>
                <div className="space-y-1.5 divide-y divide-slate-100 dark:divide-zinc-800/60 text-xs">
                  {TRAFFIC_CHANNELS.map(ch => {
                    const isObs = inspectedRow.allMasks[ch.name];
                    const val = inspectedRow.allValues[ch.name];
                    return (
                      <div key={ch.name} className="pt-1.5 first:pt-0 flex items-center justify-between">
                        <span className="font-mono font-medium text-slate-700 dark:text-zinc-300 truncate mr-2" title={ch.name}>
                          {ch.label || ch.name}
                        </span>
                        {isObs ? (
                          <span className="font-mono font-bold text-slate-900 dark:text-zinc-100 shrink-0">
                            {val} <span className="text-[10px] text-slate-400 font-normal">{ch.unit}</span>
                          </span>
                        ) : (
                          <span className="text-[10px] font-mono text-amber-600 dark:text-amber-400 font-bold bg-amber-50 dark:bg-amber-950/40 px-1.5 py-0.2 rounded border border-amber-200/60 dark:border-amber-800/60 shrink-0">
                            NaN (Dropout)
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer info strip */}
        <div className="pt-2 text-[11px] text-slate-400 dark:text-zinc-500 flex items-center justify-between border-t border-slate-100 dark:border-zinc-800/80">
          <span>
            Displaying {filteredRows.length} of 24 hourly sequence intervals ({activeChannels.length} active channels)
          </span>
          <span className="font-mono">
            Hong Kong EPD Dataset v1.0 · Ground Truth Aligned
          </span>
        </div>
      </div>
    </div>
  );
}
