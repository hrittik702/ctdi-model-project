import React, { useState, useMemo, useEffect } from 'react';
import { 
  Layers, 
  CloudRain, 
  Car, 
  Sparkles, 
  Activity,
  ArrowRight,
  CheckCircle2, 
  AlertCircle,
  Clock,
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

import GlassmorphicTooltip from '../components/GlassmorphicTooltip';
import SectionHeading from '../components/ui/SectionHeading';
import { 
  CANONICAL_CHANNELS, 
  POLLUTANT_CHANNELS, 
  METEOROLOGY_CHANNELS, 
  TRAFFIC_CHANNELS,
  CHANNEL_PALETTE
} from '../constants/datasetContract';

/**
 * Category metadata definitions
 */
const CATEGORIES = [
  {
    id: 'criteria',
    label: 'Criteria Pollutants',
    shortLabel: 'Pollutants',
    count: POLLUTANT_CHANNELS.length,
    channels: POLLUTANT_CHANNELS,
    Icon: Layers,
    title: 'Primary Criteria Air Pollutants',
    description: 'Target air quality channels regulated under Hong Kong Air Quality Objectives (HKAQO). Measured at continuous hourly resolution.',
    colorText: 'text-indigo-600 dark:text-indigo-400',
    colorBg: 'bg-indigo-50 dark:bg-indigo-950/40 border-indigo-200 dark:border-indigo-800/60'
  },
  {
    id: 'meteorology',
    label: 'Surface Meteorology',
    shortLabel: 'Meteorology',
    count: METEOROLOGY_CHANNELS.length,
    channels: METEOROLOGY_CHANNELS,
    Icon: CloudRain,
    title: 'Surface Meteorological Covariates',
    description: 'Continuous atmospheric reanalysis variables (ERA5) providing boundary layer, humidity, thermal, and wind vector context.',
    colorText: 'text-blue-600 dark:text-blue-400',
    colorBg: 'bg-blue-50 dark:bg-blue-950/40 border-blue-200 dark:border-blue-800/60'
  },
  {
    id: 'traffic',
    label: 'Traffic Context',
    shortLabel: 'Traffic',
    count: TRAFFIC_CHANNELS.length,
    channels: TRAFFIC_CHANNELS,
    Icon: Car,
    title: 'Road Network Traffic Dynamics',
    description: 'Spatial-IDW interpolated vehicular speed and road network congestion saturation levels.',
    colorText: 'text-emerald-600 dark:text-emerald-400',
    colorBg: 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/60'
  },
  {
    id: 'all',
    label: 'All Channels',
    shortLabel: 'All 13',
    count: CANONICAL_CHANNELS.length,
    channels: CANONICAL_CHANNELS,
    Icon: Sparkles,
    title: 'Complete 13-Channel Multimodal Space',
    description: 'Full multivariate tensor space (13 channels × 24 hours) for simultaneous multimodal imputation.',
    colorText: 'text-purple-600 dark:text-purple-400',
    colorBg: 'bg-purple-50 dark:bg-purple-950/40 border-purple-200 dark:border-purple-800/60'
  }
];

/**
 * Custom Multi-Channel Overview Tooltip
 */
function OverviewTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="bg-white/95 dark:bg-[#111113]/95 backdrop-blur-md border border-slate-200/90 dark:border-white/[0.08] shadow-2xl p-3 rounded-xl text-xs space-y-1.5 min-w-[210px] max-w-xs z-50">
      <div className="font-mono font-bold text-slate-900 dark:text-[#F4F4F5] border-b border-slate-100 dark:border-white/[0.06] pb-1 flex items-center justify-between">
        <span>{label}</span>
        <span className="text-[10px] text-slate-400 dark:text-zinc-500 font-sans">24h Synchronized Step</span>
      </div>
      <div className="space-y-1 pt-0.5 max-h-48 overflow-y-auto pr-1">
        {payload.map(item => {
          const ch = item.name;
          const val = item.value;
          const color = CHANNEL_PALETTE[ch] || item.color || '#6366F1';
          return (
            <div key={ch} className="flex items-center justify-between gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-slate-600 dark:text-zinc-300 truncate">
                <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: color }} />
                <span className="font-mono text-[11px] font-semibold">{ch}</span>
              </span>
              <span className="font-mono text-xs font-bold text-slate-900 dark:text-[#F4F4F5] shrink-0">
                {val !== null && val !== undefined ? val : 'NaN'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function MultiPollutantView({
  sampleData,
  pollutants = [],
  sampleIdx = 0,
  onDrillDown,
  isDark = false,
  gridStroke = '#e2e8f0',
  axisStroke = '#94a3b8'
}) {
  // Category state (Default to primary criteria pollutants to avoid visual overload)
  const [activeCategory, setActiveCategory] = useState('criteria');

  // Find active category definition
  const currentCategory = useMemo(() => {
    return CATEGORIES.find(c => c.id === activeCategory) || CATEGORIES[0];
  }, [activeCategory]);

  // Selected channel for detailed deep-dive inspection (defaults to first channel in category)
  const [selectedChannelName, setSelectedChannelName] = useState(() => POLLUTANT_CHANNELS[0]?.name || 'PM2.5');

  // Automatically synchronize selected channel when category switches
  useEffect(() => {
    if (!currentCategory.channels.some(ch => ch.name === selectedChannelName)) {
      setSelectedChannelName(currentCategory.channels[0]?.name || '');
    }
  }, [currentCategory, selectedChannelName]);

  // Contextual station and timestamp formatting
  const stationName = sampleData?.station || 'Central / Western';
  const rawFirstTimestamp = sampleData?.timestamps?.[0] || '';
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

  // Compute category-wide observability statistics
  const categoryStats = useMemo(() => {
    const totalChannels = currentCategory.channels.length;
    const totalPoints = totalChannels * 24;
    let totalObserved = 0;

    currentCategory.channels.forEach(ch => {
      const pData = sampleData?.pollutants?.[ch.name];
      const observedMask = pData?.observed_mask || [];
      const obsCount = observedMask.filter(m => m === 1).length;
      totalObserved += obsCount;
    });

    const totalMissing = totalPoints - totalObserved;
    const completenessPct = totalPoints > 0 ? ((totalObserved / totalPoints) * 100).toFixed(1) : '100.0';

    return {
      totalChannels,
      totalPoints,
      totalObserved,
      totalMissing,
      completenessPct
    };
  }, [currentCategory, sampleData]);

  // Compute stats dictionary for each channel in the current category
  const channelStatsMap = useMemo(() => {
    const map = {};
    currentCategory.channels.forEach(ch => {
      const pData = sampleData?.pollutants?.[ch.name];
      const observedMask = pData?.observed_mask || [];
      const actualArray = pData?.actual || [];
      const observedCount = observedMask.filter(m => m === 1).length;
      const missingCount = 24 - observedCount;

      const validValues = actualArray.filter((v, i) => observedMask[i] === 1 && v !== null && !isNaN(v));
      const meanVal = validValues.length
        ? (validValues.reduce((sum, v) => sum + v, 0) / validValues.length).toFixed(1)
        : '—';
      const minVal = validValues.length ? Math.min(...validValues).toFixed(1) : '—';
      const maxVal = validValues.length ? Math.max(...validValues).toFixed(1) : '—';

      map[ch.name] = {
        mean: meanVal,
        min: minVal,
        max: maxVal,
        range: minVal !== '—' && maxVal !== '—' ? `${minVal}–${maxVal}` : '—',
        observedCount,
        missingCount,
        completenessPct: ((observedCount / 24) * 100).toFixed(0)
      };
    });
    return map;
  }, [currentCategory, sampleData]);

  // Find currently selected channel definition
  const selectedChannel = useMemo(() => {
    return (
      currentCategory.channels.find(ch => ch.name === selectedChannelName) ||
      currentCategory.channels[0] ||
      CANONICAL_CHANNELS[0]
    );
  }, [currentCategory, selectedChannelName]);

  const selectedStats = channelStatsMap[selectedChannel?.name] || {
    mean: '—', min: '—', max: '—', range: '—', observedCount: 24, missingCount: 0
  };

  // Synchronized 24-Hour Overview Chart Data
  const overviewChartData = useMemo(() => {
    const hours = sampleData?.hours || Array.from({ length: 24 }, (_, i) => i);
    const timestamps = sampleData?.timestamps || [];

    return hours.map((hour, idx) => {
      const clockTime = timestamps[idx]?.includes(' ')
        ? timestamps[idx].split(' ')[1].slice(0, 5)
        : `${String(hour).padStart(2, '0')}:00`;

      const point = {
        hour: clockTime,
        time: clockTime,
        timestamp: timestamps[idx] || clockTime
      };

      currentCategory.channels.forEach(ch => {
        const pObj = sampleData?.pollutants?.[ch.name];
        const isObs = pObj?.observed_mask?.[idx] === 1;
        const val = pObj?.actual?.[idx];
        point[ch.name] = (isObs && val !== null && val !== undefined) ? Number(val.toFixed(2)) : null;
      });

      return point;
    });
  }, [sampleData, currentCategory]);

  // Selected Single Channel Trajectory Chart Data
  const selectedChannelChartData = useMemo(() => {
    if (!selectedChannel) return [];
    const hours = sampleData?.hours || Array.from({ length: 24 }, (_, i) => i);
    const timestamps = sampleData?.timestamps || [];
    const pData = sampleData?.pollutants?.[selectedChannel.name];
    const observedMask = pData?.observed_mask || [];
    const actualArray = pData?.actual || [];

    return hours.map((hour, idx) => {
      const isObs = observedMask[idx] === 1;
      const clockTime = timestamps[idx]?.includes(' ')
        ? timestamps[idx].split(' ')[1].slice(0, 5)
        : `${String(hour).padStart(2, '0')}:00`;
      const val = actualArray[idx] ?? null;

      return {
        hour: clockTime,
        time: clockTime,
        timestamp: timestamps[idx] || clockTime,
        actual: val !== null ? Number(val.toFixed(2)) : null,
        observed: isObs && val !== null ? Number(val.toFixed(2)) : null,
        naturalMissing: !isObs && val !== null ? Number(val.toFixed(2)) : null,
        isNaturalMissing: !isObs,
        unit: selectedChannel.unit
      };
    });
  }, [sampleData, selectedChannel]);

  // Ticks for charts mapped directly from current window timestamps
  const hourTicks = useMemo(() => {
    return [0, 4, 8, 12, 16, 20, 23]
      .map(idx => overviewChartData[idx]?.time)
      .filter(Boolean);
  }, [overviewChartData]);

  return (
    <div className="space-y-5 pb-12">
      {/* 1. Primary Page Identity with Scroll Morphed Section Header */}
      <div>
        <SectionHeading
          id="multi-pollutant"
          title="Multi-Pollutant Workspace"
          icon="multigrid"
        />
        <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-zinc-400 mt-1 pl-0.5">
          <strong className="text-slate-800 dark:text-zinc-200 font-semibold">{stationName}</strong>
          <span className="text-slate-300 dark:text-zinc-700">·</span>
          <span>Hong Kong EPD</span>
          <span className="text-slate-300 dark:text-zinc-700">·</span>
          <span>{formattedDate}</span>
          <span className="text-slate-300 dark:text-zinc-700">·</span>
          <span>00:00–23:00</span>
          <span className="ml-1 text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200/70 dark:border-indigo-800/60">
            Window {sampleIdx + 1} / 26,281
          </span>
        </div>
      </div>

      {/* 2. Window / Data Summary Strip (4 Truthful Derived Cards) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Card 1: Channel Count */}
        <div className="p-3.5 sm:p-4 rounded-2xl border border-slate-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/90 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
              Active Category
            </span>
            <Layers className="w-4 h-4 text-indigo-500 shrink-0" />
          </div>
          <div className="mt-2.5">
            <div className="text-xl sm:text-2xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-zinc-100">
              {categoryStats.totalChannels} Channels
            </div>
            <p className="mt-0.5 text-xs text-slate-500 dark:text-zinc-400 truncate">
              {currentCategory.shortLabel}
            </p>
          </div>
        </div>

        {/* Card 2: Sequence Window */}
        <div className="p-3.5 sm:p-4 rounded-2xl border border-slate-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/90 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
              Sequence Window
            </span>
            <Clock className="w-4 h-4 text-blue-500 shrink-0" />
          </div>
          <div className="mt-2.5">
            <div className="text-xl sm:text-2xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-zinc-100">
              24 Hours
            </div>
            <p className="mt-0.5 text-xs text-slate-500 dark:text-zinc-400 truncate">
              00:00 – 23:00 Synchronized
            </p>
          </div>
        </div>

        {/* Card 3: Observed Cells */}
        <div className="p-3.5 sm:p-4 rounded-2xl border border-slate-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/90 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
              Observed Cells
            </span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
          </div>
          <div className="mt-2.5">
            <div className="text-xl sm:text-2xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-zinc-100">
              {categoryStats.totalObserved} / {categoryStats.totalPoints}
            </div>
            <p className="mt-0.5 text-xs text-emerald-600 dark:text-emerald-400 font-semibold truncate">
              {categoryStats.completenessPct}% Ground Truth Verified
            </p>
          </div>
        </div>

        {/* Card 4: Natural Dropouts */}
        <div className="p-3.5 sm:p-4 rounded-2xl border border-slate-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/90 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
              Natural Dropouts
            </span>
            <AlertCircle className={`w-4 h-4 shrink-0 ${categoryStats.totalMissing > 0 ? 'text-amber-500' : 'text-slate-400'}`} />
          </div>
          <div className="mt-2.5">
            <div className={`text-xl sm:text-2xl font-extrabold font-mono tracking-tight ${categoryStats.totalMissing > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-900 dark:text-zinc-100'}`}>
              {categoryStats.totalMissing} Dropouts
            </div>
            <p className="mt-0.5 text-xs text-slate-500 dark:text-zinc-400 truncate">
              {categoryStats.totalMissing > 0 
                ? `${((categoryStats.totalMissing / categoryStats.totalPoints) * 100).toFixed(1)}% natural sensor dropouts` 
                : 'Zero missing cells in window'}
            </p>
          </div>
        </div>
      </div>

      {/* 3. Category Filter Navigation Bar & Compact Context Line */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
        {/* Left: Segmented Channel Group Selector */}
        <div className="inline-flex p-1 rounded-xl bg-slate-200/70 dark:bg-zinc-800/80 border border-slate-200/80 dark:border-zinc-700/60 text-xs select-none">
          {CATEGORIES.map(cat => {
            const isSelected = activeCategory === cat.id;
            return (
              <button
                key={cat.id}
                type="button"
                onClick={() => setActiveCategory(cat.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition cursor-pointer motion-press motion-tab-active ${
                  isSelected
                    ? 'bg-white dark:bg-zinc-900 text-slate-900 dark:text-zinc-100 font-bold shadow-xs'
                    : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-200'
                }`}
              >
                <cat.Icon className={`w-3.5 h-3.5 shrink-0 ${isSelected ? cat.colorText : 'text-slate-400 dark:text-zinc-500'}`} />
                <span className="hidden md:inline">{cat.label}</span>
                <span className="md:hidden">{cat.shortLabel}</span>
                <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                  isSelected 
                    ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-bold' 
                    : 'bg-slate-300/60 dark:bg-zinc-700/60 text-slate-500 dark:text-zinc-400'
                }`}>
                  {cat.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Right: Observability indicator */}
        <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-zinc-400">
          <Activity className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
          <span>Observability:</span>
          <strong className="text-slate-800 dark:text-zinc-200 font-mono font-bold">
            {categoryStats.completenessPct}%
          </strong>
          <span className="text-[11px] text-slate-400 dark:text-zinc-500">
            ({categoryStats.totalObserved}/{categoryStats.totalPoints} cells)
          </span>
        </div>
      </div>

      {/* Compact Category Context Note (Replaced giant colored banner) */}
      <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-100/70 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800/80 text-xs text-slate-600 dark:text-zinc-400">
        <Info className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
        <span className="font-semibold text-slate-800 dark:text-zinc-200">{currentCategory.title} ({currentCategory.channels.length} channels):</span>
        <span className="truncate">{currentCategory.description}</span>
      </div>

      {/* 4. Cross-Pollutant Primary Overview Chart */}
      <div className="bg-white dark:bg-zinc-900/95 p-4 sm:p-5 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-zinc-800/80 pb-3">
          <div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <h3 className="font-extrabold text-slate-900 dark:text-zinc-100 text-sm sm:text-base tracking-tight">
                24-Hour Cross-Pollutant Overview
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
              Synchronized temporal trajectories across all {currentCategory.channels.length} channels in {currentCategory.label}
            </p>
          </div>

          {/* Channel Legend Pills */}
          <div className="flex items-center gap-2 flex-wrap">
            {currentCategory.channels.slice(0, 7).map(ch => (
              <span 
                key={ch.name} 
                className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-mono font-semibold bg-slate-50 dark:bg-zinc-800/80 border border-slate-200/60 dark:border-zinc-700/60 text-slate-700 dark:text-zinc-300"
              >
                <span 
                  className="w-2 h-2 rounded-full shrink-0" 
                  style={{ backgroundColor: CHANNEL_PALETTE[ch.name] || '#6366F1' }} 
                />
                <span>{ch.name}</span>
              </span>
            ))}
            {currentCategory.channels.length > 7 && (
              <span className="text-[10px] text-slate-400 dark:text-zinc-500 font-mono">
                +{currentCategory.channels.length - 7} more
              </span>
            )}
          </div>
        </div>

        {/* Multi-Line Synchronized Chart */}
        <div className="h-[220px] w-full pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={overviewChartData} margin={{ top: 8, right: 16, left: -16, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} opacity={0.6} />
              <XAxis 
                dataKey="time" 
                ticks={hourTicks}
                stroke={axisStroke} 
                fontSize={11} 
                tickLine={false} 
              />
              <YAxis 
                stroke={axisStroke} 
                fontSize={11} 
                tickLine={false} 
              />
              <Tooltip content={<OverviewTooltip />} />
              {currentCategory.channels.map(ch => (
                <Line
                  key={ch.name}
                  type="monotone"
                  dataKey={ch.name}
                  name={ch.name}
                  stroke={CHANNEL_PALETTE[ch.name] || '#6366F1'}
                  strokeWidth={1.8}
                  dot={false}
                  activeDot={{ r: 4, strokeWidth: 1 }}
                  connectNulls={false}
                  isAnimationActive={true}
                  animationDuration={450}
                  animationEasing="ease-out"
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 5. Channel Comparison Bar (Compact Interactive Selection Grid) */}
      <div className="space-y-2">
        <div className="flex items-center justify-between px-0.5">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500">
            Channel Comparison & Inspection Selector (Click to inspect)
          </span>
          <span className="text-xs text-slate-400 dark:text-zinc-500">
            Selected: <strong className="text-indigo-600 dark:text-indigo-400 font-mono">{selectedChannel.name}</strong>
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6 gap-2.5">
          {currentCategory.channels.map(ch => {
            const isSelected = selectedChannelName === ch.name;
            const st = channelStatsMap[ch.name] || { mean: '—', range: '—', observedCount: 24, missingCount: 0 };
            const color = CHANNEL_PALETTE[ch.name] || '#6366F1';

            return (
              <button
                key={ch.name}
                type="button"
                onClick={() => setSelectedChannelName(ch.name)}
                className={`p-3 rounded-2xl border text-left cursor-pointer flex flex-col justify-between select-none motion-card-interactive motion-press ${
                  isSelected
                    ? 'bg-indigo-50/60 dark:bg-indigo-950/40 border-indigo-400 dark:border-indigo-600 shadow-xs ring-1 ring-indigo-400/50 dark:ring-indigo-600/50'
                    : 'bg-white dark:bg-zinc-900/90 border-slate-200/80 dark:border-zinc-800 hover:border-slate-300 dark:hover:border-zinc-700'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-1.5">
                    <div className="flex items-center gap-1.5 min-w-0">
                      <span 
                        className="w-2.5 h-2.5 rounded-full shrink-0" 
                        style={{ backgroundColor: color }}
                      />
                      <span className="font-bold font-mono text-xs text-slate-900 dark:text-zinc-100 truncate">
                        {ch.name}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400 dark:text-zinc-500 shrink-0">
                      {ch.unit}
                    </span>
                  </div>

                  <p className="text-[10px] text-slate-400 dark:text-zinc-500 truncate mt-1" title={ch.desc}>
                    {ch.desc}
                  </p>
                </div>

                <div className="mt-2.5 pt-2 border-t border-slate-100 dark:border-zinc-800/80 flex items-center justify-between text-xs font-mono">
                  <div>
                    <span className="text-[9px] uppercase font-sans text-slate-400 block leading-none mb-0.5">Mean</span>
                    <strong className="text-slate-800 dark:text-zinc-200 text-[11px]">{st.mean}</strong>
                  </div>
                  <div className="text-right">
                    <span className="text-[9px] uppercase font-sans text-slate-400 block leading-none mb-0.5">Observed</span>
                    <span className={`text-[11px] font-semibold ${st.missingCount === 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}`}>
                      {st.observedCount}/24
                    </span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 6. Selected Channel Deep Dive Panel */}
      <div className="bg-white dark:bg-zinc-900/95 p-4 sm:p-5 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs space-y-4">
        {/* Panel Header: Channel Identity + Single Contextual Action Button */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-zinc-800/80 pb-3">
          <div className="flex items-center gap-3">
            <div 
              className="w-10 h-10 rounded-xl flex items-center justify-center font-bold text-white shadow-xs shrink-0"
              style={{ backgroundColor: CHANNEL_PALETTE[selectedChannel.name] || '#6366F1' }}
            >
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="font-extrabold text-slate-900 dark:text-zinc-100 text-base tracking-tight font-mono">
                  {selectedChannel.name}
                </h3>
                <span className="text-xs px-2 py-0.5 rounded-md bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-300 font-mono font-medium border border-slate-200/60 dark:border-zinc-700/60">
                  {selectedChannel.unit}
                </span>
                <span className="text-[11px] px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 font-sans font-semibold border border-indigo-200/60 dark:border-indigo-800/60">
                  {selectedChannel.group || currentCategory.label}
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                {selectedChannel.desc}
              </p>
            </div>
          </div>

          {/* SINGLE Contextual Action: Open in 24h Trajectory (Replaced 5 repeated buttons) */}
          <button
            type="button"
            onClick={() => onDrillDown && onDrillDown(selectedChannel.name)}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition cursor-pointer shadow-xs shrink-0 group motion-press"
            title={`Open ${selectedChannel.name} in 24-Hour Trajectory Workspace`}
          >
            <span>Open in 24h Trajectory</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </button>
        </div>

        {/* Selected Channel Metrics Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
          <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-zinc-800/50 border border-slate-100 dark:border-zinc-800">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 block">
              24h Mean
            </span>
            <span className="text-lg font-extrabold font-mono text-slate-900 dark:text-zinc-100 mt-0.5 block">
              {selectedStats.mean} <span className="text-[10px] text-slate-400 font-normal">{selectedChannel.unit}</span>
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-zinc-800/50 border border-slate-100 dark:border-zinc-800">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 block">
              24h Min – Max
            </span>
            <span className="text-lg font-extrabold font-mono text-slate-900 dark:text-zinc-100 mt-0.5 block">
              {selectedStats.range}
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-zinc-800/50 border border-slate-100 dark:border-zinc-800">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 block">
              Observed Steps
            </span>
            <span className="text-lg font-extrabold font-mono text-emerald-600 dark:text-emerald-400 mt-0.5 block">
              {selectedStats.observedCount} / 24
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-zinc-800/50 border border-slate-100 dark:border-zinc-800">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 block">
              Natural Dropouts
            </span>
            <span className={`text-lg font-extrabold font-mono mt-0.5 block ${selectedStats.missingCount > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-900 dark:text-zinc-100'}`}>
              {selectedStats.missingCount}
            </span>
          </div>
        </div>

        {/* Selected Channel Dedicated Detailed 24h Trajectory Chart */}
        <div className="space-y-2 pt-1">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-zinc-400">
            <span className="font-semibold text-slate-700 dark:text-zinc-300">
              {selectedChannel.name} 24-Hour Sequence Trajectory
            </span>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                <span>Observed</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full border border-amber-500 bg-transparent" />
                <span>Natural Missing</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-slate-300 dark:bg-zinc-600" />
                <span>Ground Truth</span>
              </span>
            </div>
          </div>

          <div className="h-[210px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={selectedChannelChartData} margin={{ top: 8, right: 16, left: -16, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} opacity={0.6} />
                <XAxis 
                  dataKey="hour" 
                  ticks={hourTicks} 
                  stroke={axisStroke} 
                  fontSize={11} 
                  tickLine={false} 
                />
                <YAxis 
                  stroke={axisStroke} 
                  fontSize={11} 
                  tickLine={false} 
                  domain={['auto', 'auto']} 
                />
                <Tooltip content={<GlassmorphicTooltip isDark={isDark} unit={selectedChannel.unit} />} />

                {/* Ground truth reference baseline */}
                <Line 
                  type="linear" 
                  dataKey="actual" 
                  name="Ground Truth"
                  stroke={isDark ? 'rgba(255, 255, 255, 0.2)' : '#cbd5e1'} 
                  strokeWidth={1.2} 
                  strokeDasharray="3 3" 
                  dot={false} 
                  isAnimationActive={true}
                  animationDuration={450}
                  animationEasing="ease-out"
                />

                {/* Observed values */}
                <Line 
                  type="linear" 
                  dataKey="observed" 
                  name="Observed"
                  stroke={CHANNEL_PALETTE[selectedChannel.name] || '#3B82F6'} 
                  strokeWidth={2.2} 
                  dot={{ stroke: CHANNEL_PALETTE[selectedChannel.name] || '#3B82F6', strokeWidth: 1.5, fill: isDark ? '#18181b' : '#ffffff', r: 3 }} 
                  activeDot={{ r: 5 }}
                  connectNulls={false} 
                  isAnimationActive={true}
                  animationDuration={450}
                  animationEasing="ease-out"
                />

                {/* Natural Missing hours */}
                <Line 
                  type="linear" 
                  dataKey="naturalMissing" 
                  name="Natural Missing"
                  stroke="none" 
                  dot={{ stroke: '#f59e0b', strokeWidth: 1.5, fill: 'transparent', r: 4 }} 
                  isAnimationActive={true}
                  animationDuration={450}
                  animationEasing="ease-out"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
