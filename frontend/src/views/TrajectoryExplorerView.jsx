import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { Layers, ChevronDown, Wind, ChevronLeft, ChevronRight } from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid
} from 'recharts';

import ChartWidget from '../components/ChartWidget';
import GlassmorphicTooltip from '../components/GlassmorphicTooltip';
import ProjectIcon from '../components/ui/ProjectIcon';
import { CANONICAL_CHANNELS } from '../constants/datasetContract';
import SectionHeading from '../components/ui/SectionHeading';

// Static channel categories grouped once at module level
const CRITERIA_POLLUTANTS = CANONICAL_CHANNELS.filter(c => c.category === 'air_quality');
const METEOROLOGY_CHANNELS = CANONICAL_CHANNELS.filter(c => c.category === 'meteorology');
const TRAFFIC_CHANNELS = CANONICAL_CHANNELS.filter(c => c.category === 'traffic');

export default function TrajectoryExplorerView({
  isDashboard = false,
  sampleIdx,
  setSampleIdx,
  maxSamples = 26281,
  targetPollutant = 'PM2.5',
  setTargetPollutant,
  pollutants = [],
  sampleData,
  chartData = [],
  visibleModels,
  setVisibleModels,
  curveSeries = [],
  isDark = false,
  gridStroke,
  axisStroke,
  isLoading = false
}) {
  const [isSeriesDropdownOpen, setIsSeriesDropdownOpen] = useState(false);
  const [isChannelDropdownOpen, setIsChannelDropdownOpen] = useState(false);
  const seriesDropdownRef = useRef(null);
  const channelDropdownRef = useRef(null);

  // Directional sliding tracking for window changes (curve-only motion) & initial entrance
  const prevSampleIdxRef = useRef(sampleIdx);
  const [slideDirection, setSlideDirection] = useState('initial'); // 'initial' | 'forward' | 'backward'
  const [curveAnimToggle, setCurveAnimToggle] = useState(0);
  const isInitialMountRef = useRef(true);

  // Check system prefers-reduced-motion
  const prefersReducedMotion = typeof window !== 'undefined'
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : false;

  useEffect(() => {
    if (isInitialMountRef.current) {
      isInitialMountRef.current = false;
      return;
    }

    if (prevSampleIdxRef.current !== sampleIdx) {
      if (sampleIdx > prevSampleIdxRef.current) {
        setSlideDirection('forward'); // forward in time -> slide left
      } else {
        setSlideDirection('backward'); // backward in time -> slide right
      }
      setCurveAnimToggle(prev => (prev === 0 ? 1 : 0));
      prevSampleIdxRef.current = sampleIdx;
    }
  }, [sampleIdx]);

  // Close dropdowns on click outside or Escape
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (seriesDropdownRef.current && !seriesDropdownRef.current.contains(e.target)) {
        setIsSeriesDropdownOpen(false);
      }
      if (channelDropdownRef.current && !channelDropdownRef.current.contains(e.target)) {
        setIsChannelDropdownOpen(false);
      }
    };
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setIsSeriesDropdownOpen(false);
        setIsChannelDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const pData = sampleData?.pollutants?.[targetPollutant];
  const channelObj = CANONICAL_CHANNELS.find(c => c.name === targetPollutant || c.label === targetPollutant) || CANONICAL_CHANNELS[0];
  const channelUnit = channelObj?.unit || 'µg/m³';

  // Group channels for organized selection (module-level reference)
  const criteriaPollutants = CRITERIA_POLLUTANTS;
  const meteorologyChannels = METEOROLOGY_CHANNELS;
  const trafficChannels = TRAFFIC_CHANNELS;

  // Format contextual date from sample timestamps (e.g. '17 Apr 2021')
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

  const stationDisplayName = sampleData?.station || 'Central / Western';

  // 4-hour tick marks along 24h trajectory: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00, 23:00
  const fourHourTicks = useMemo(() => {
    return [0, 4, 8, 12, 16, 20, 23]
      .map(idx => chartData[idx]?.hour)
      .filter(Boolean);
  }, [chartData]);

  // Missingness counts for current 24-hour window
  const totalPoints = chartData.length || 24;
  const { observedCount, naturalMissingCount, observedPct } = useMemo(() => {
    const obs = chartData.filter(d => d.observed !== null).length;
    return {
      observedCount: obs,
      naturalMissingCount: totalPoints - obs,
      observedPct: Math.round((obs / totalPoints) * 100)
    };
  }, [chartData, totalPoints]);

  // Active series count (only counting series that have actual data)
  const availableSeries = useMemo(() => [
    { key: 'observed', label: 'Observed Measurements', type: 'observed', hasData: true, color: 'bg-blue-500' },
    { key: 'hiddenTarget', label: 'Natural Missing Dropout', type: 'missing', hasData: true, color: 'border border-red-500 bg-transparent' },
    { key: 'groundTruth', label: 'Ground Truth Line', type: 'reference', hasData: true, color: isDark ? 'bg-zinc-200' : 'bg-slate-800' },
    { key: 'transformer', label: 'CTDI Imputer', type: 'model', hasData: false, statusText: 'Unavailable', color: 'bg-emerald-500' },
    { key: 'linear', label: 'Linear Baseline', type: 'baseline', hasData: false, statusText: 'Not Evaluated', color: 'bg-amber-500' },
    { key: 'knn', label: 'KNN Baseline', type: 'baseline', hasData: false, statusText: 'Not Evaluated', color: 'bg-purple-500' },
    { key: 'mlp', label: 'MLP Baseline', type: 'baseline', hasData: false, statusText: 'Not Evaluated', color: 'bg-cyan-500' }
  ], [isDark]);

  const activeSeriesCount = useMemo(() => {
    return availableSeries.filter(s => s.hasData && visibleModels[s.key]).length;
  }, [availableSeries, visibleModels]);

  // LAYER 2: Unified Single-Row Controls Bar (memoized)
  const renderControlsBar = useCallback(({
    showGrid,
    setShowGrid,
    zoomLevel,
    handleZoomIn,
    handleZoomOut,
    handleResetZoom,
    isFullscreen,
    setIsFullscreen,
    handleExportAnalyticalPNG,
    handleExportCSV,
    handleExportJSON,
    dropdownOpen,
    setDropdownOpen,
    dropdownRef
  }) => (
    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 text-xs">
      {/* Window Stepper & Navigation Slider */}
      <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
        {/* Segmented Stepper Pill */}
        <div className="inline-flex items-center rounded-lg border border-slate-200/80 dark:border-zinc-700/80 bg-slate-100 dark:bg-zinc-800/90 p-0.5 shadow-2xs">
          <button
            type="button"
            onClick={() => setSampleIdx(prev => Math.max(0, prev - 1))}
            disabled={sampleIdx <= 0}
            title="Previous Window (-1h)"
            aria-label="Previous Window"
            className="p-1 rounded-md text-slate-600 hover:text-slate-900 dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-white dark:hover:bg-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed transition cursor-pointer motion-press"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
          </button>

          <span 
            className="px-2 py-0.5 font-mono font-bold text-slate-800 dark:text-zinc-200 text-xs whitespace-nowrap min-w-[124px] text-center select-none"
            title={`Station-local Window index ${sampleIdx + 1} of ${maxSamples.toLocaleString()}`}
          >
            Window {(sampleIdx + 1).toLocaleString()} / {maxSamples.toLocaleString()}
          </span>

          <button
            type="button"
            onClick={() => setSampleIdx(prev => Math.min(maxSamples - 1, prev + 1))}
            disabled={sampleIdx >= maxSamples - 1}
            title="Next Window (+1h)"
            aria-label="Next Window"
            className="p-1 rounded-md text-slate-600 hover:text-slate-900 dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-white dark:hover:bg-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed transition cursor-pointer motion-press"
          >
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Timeline Slider */}
        <div className="flex items-center gap-1.5 flex-1 min-w-[90px] max-w-[140px] sm:max-w-[180px]">
          <input
            type="range"
            min={0}
            max={maxSamples - 1}
            step={1}
            value={sampleIdx}
            onChange={(e) => setSampleIdx(Number(e.target.value))}
            title={`Slide across all ${maxSamples.toLocaleString()} station windows (Current: ${sampleIdx + 1})`}
            aria-label="Station Window Navigation Slider"
            className="w-full accent-indigo-600 cursor-pointer h-1.5 bg-slate-200 dark:bg-zinc-700 rounded-lg"
          />
        </div>

        {/* Quick Day Step Buttons */}
        <div className="inline-flex items-center rounded-lg border border-slate-200/80 dark:border-zinc-700/80 bg-slate-100 dark:bg-zinc-800/90 p-0.5 shadow-2xs">
          <button
            type="button"
            onClick={() => setSampleIdx(prev => Math.max(0, prev - 24))}
            disabled={sampleIdx < 24}
            title="Step backward 24 hours (1 calendar day)"
            className="px-2 py-0.5 rounded-md text-[11px] font-mono font-semibold text-slate-600 dark:text-zinc-400 hover:bg-white dark:hover:bg-zinc-700 disabled:opacity-30 transition cursor-pointer motion-press"
          >
            -24h
          </button>
          <div className="w-px h-3 bg-slate-200 dark:bg-zinc-700" />
          <button
            type="button"
            onClick={() => setSampleIdx(prev => Math.min(maxSamples - 1, prev + 24))}
            disabled={sampleIdx >= maxSamples - 24}
            title="Step forward 24 hours (1 calendar day)"
            className="px-2 py-0.5 rounded-md text-[11px] font-mono font-semibold text-slate-600 dark:text-zinc-400 hover:bg-white dark:hover:bg-zinc-700 disabled:opacity-30 transition cursor-pointer motion-press"
          >
            +24h
          </button>
        </div>
      </div>

      {/* Right: Channel Selector, Series Menu, and Utility Action Group */}
      <div className="flex items-center gap-1.5 flex-wrap sm:flex-nowrap shrink-0 justify-end">
        {/* Modern 13-Channel Selector Dropdown */}
        <div className="relative" ref={channelDropdownRef}>
          <button
            type="button"
            onClick={() => {
              setIsChannelDropdownOpen(prev => !prev);
              setIsSeriesDropdownOpen(false);
            }}
            aria-expanded={isChannelDropdownOpen}
            aria-haspopup="true"
            title="Select Atmospheric Feature (13 Canonical Channels)"
            aria-label="Select Atmospheric Feature"
            className={`flex items-center gap-1.5 h-8 px-2.5 rounded-lg border text-xs font-semibold transition cursor-pointer shadow-2xs motion-press ${
              isChannelDropdownOpen
                ? 'bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 border-indigo-300 dark:border-indigo-700'
                : 'bg-slate-100 dark:bg-zinc-800 text-slate-800 dark:text-zinc-200 border-slate-200/80 dark:border-zinc-700/80 hover:bg-slate-200 dark:hover:bg-zinc-700'
            }`}
          >
            <Wind className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
            <span className="font-bold text-slate-800 dark:text-zinc-100">{channelObj.name}</span>
            <span className="text-[10px] font-mono text-slate-400 dark:text-zinc-400 hidden sm:inline">
              ({channelUnit})
            </span>
            <ChevronDown className={`w-3 h-3 text-slate-400 shrink-0 transition-transform duration-fast ease-out-subtle ${isChannelDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {isChannelDropdownOpen && (
            <div className="absolute right-0 mt-1.5 w-64 sm:w-72 max-h-80 overflow-y-auto bg-white dark:bg-zinc-900 rounded-2xl shadow-xl border border-slate-200/90 dark:border-zinc-800 p-2 z-50 text-xs space-y-2 motion-popover-enter">
              <div className="flex items-center justify-between pb-1.5 px-1 border-b border-slate-100 dark:border-zinc-800">
                <span className="font-bold text-slate-900 dark:text-zinc-100 text-[11px] uppercase tracking-wider">
                  Atmospheric Channels
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  13 Channels
                </span>
              </div>

              {/* Criteria Pollutants (5) */}
              <div className="space-y-0.5">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-1.5 py-0.5">
                  Criteria Air Pollutants
                </div>
                {criteriaPollutants.map(c => {
                  const isSelected = c.name === targetPollutant;
                  return (
                    <button
                      key={c.name}
                      type="button"
                      onClick={() => {
                        setTargetPollutant(c.name);
                        setIsChannelDropdownOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-2 py-1.5 rounded-xl text-left cursor-pointer transition ${
                        isSelected
                          ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 font-semibold'
                          : 'hover:bg-slate-50 dark:hover:bg-zinc-800/70 text-slate-700 dark:text-zinc-300'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full shrink-0 ${isSelected ? 'bg-indigo-600 dark:bg-indigo-400' : 'bg-slate-300 dark:bg-zinc-600'}`} />
                        <span>{c.name}</span>
                        <span className="text-[11px] text-slate-400 dark:text-zinc-500 font-mono">({c.unit})</span>
                      </div>
                      {isSelected && <span className="text-xs text-indigo-600 dark:text-indigo-400 font-bold">✓</span>}
                    </button>
                  );
                })}
              </div>

              {/* Meteorology (6) */}
              <div className="pt-1 border-t border-slate-100 dark:border-zinc-800 space-y-0.5">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-1.5 py-0.5">
                  Meteorological Context
                </div>
                {meteorologyChannels.map(c => {
                  const isSelected = c.name === targetPollutant;
                  return (
                    <button
                      key={c.name}
                      type="button"
                      onClick={() => {
                        setTargetPollutant(c.name);
                        setIsChannelDropdownOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-2 py-1.5 rounded-xl text-left cursor-pointer transition ${
                        isSelected
                          ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 font-semibold'
                          : 'hover:bg-slate-50 dark:hover:bg-zinc-800/70 text-slate-700 dark:text-zinc-300'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full shrink-0 ${isSelected ? 'bg-indigo-600 dark:bg-indigo-400' : 'bg-slate-300 dark:bg-zinc-600'}`} />
                        <span>{c.name}</span>
                        <span className="text-[11px] text-slate-400 dark:text-zinc-500 font-mono">({c.unit})</span>
                      </div>
                      {isSelected && <span className="text-xs text-indigo-600 dark:text-indigo-400 font-bold">✓</span>}
                    </button>
                  );
                })}
              </div>

              {/* Traffic Context (2) */}
              <div className="pt-1 border-t border-slate-100 dark:border-zinc-800 space-y-0.5">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-1.5 py-0.5">
                  Traffic Context
                </div>
                {trafficChannels.map(c => {
                  const isSelected = c.name === targetPollutant;
                  return (
                    <button
                      key={c.name}
                      type="button"
                      onClick={() => {
                        setTargetPollutant(c.name);
                        setIsChannelDropdownOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-2 py-1.5 rounded-xl text-left cursor-pointer transition ${
                        isSelected
                          ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 font-semibold'
                          : 'hover:bg-slate-50 dark:hover:bg-zinc-800/70 text-slate-700 dark:text-zinc-300'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full shrink-0 ${isSelected ? 'bg-indigo-600 dark:bg-indigo-400' : 'bg-slate-300 dark:bg-zinc-600'}`} />
                        <span>{c.name}</span>
                        <span className="text-[11px] text-slate-400 dark:text-zinc-500 font-mono">({c.unit})</span>
                      </div>
                      {isSelected && <span className="text-xs text-indigo-600 dark:text-indigo-400 font-bold">✓</span>}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Series Selector Dropdown */}
        <div className="relative" ref={seriesDropdownRef}>
          <button
            type="button"
            onClick={() => {
              setIsSeriesDropdownOpen(prev => !prev);
              setIsChannelDropdownOpen(false);
            }}
            aria-expanded={isSeriesDropdownOpen}
            aria-haspopup="true"
            title="Select Visible Series on Chart"
            aria-label="Select Visible Series"
            className={`flex items-center gap-1.5 h-8 px-2.5 rounded-lg border text-xs font-semibold transition cursor-pointer shadow-2xs motion-press ${
              isSeriesDropdownOpen
                ? 'bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 border-indigo-300 dark:border-indigo-700'
                : 'bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-200 border-slate-200/80 dark:border-zinc-700/80 hover:bg-slate-200 dark:hover:bg-zinc-700'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
            <span>Series</span>
            <span className="px-1.5 py-0.2 rounded-md bg-white dark:bg-zinc-700 text-[10px] font-bold text-indigo-600 dark:text-indigo-300 border border-slate-200/60 dark:border-zinc-600">
              {activeSeriesCount}
            </span>
            <ChevronDown className={`w-3 h-3 text-slate-400 shrink-0 transition-transform duration-fast ease-out-subtle ${isSeriesDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {isSeriesDropdownOpen && (
            <div className="absolute right-0 mt-1.5 w-72 bg-white dark:bg-zinc-900 rounded-2xl shadow-xl border border-slate-200/90 dark:border-zinc-800 p-2.5 z-50 text-xs space-y-2 motion-popover-enter">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-zinc-800">
                <span className="font-bold text-slate-900 dark:text-zinc-100 text-[11px] uppercase tracking-wider">
                  Active Series
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  {activeSeriesCount} Visible
                </span>
              </div>

              {/* Data-backed Series (Active & Toggleable) */}
              <div className="space-y-1">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-1">
                  Dataset Observations
                </div>
                {availableSeries.filter(s => s.hasData).map(series => {
                  const isChecked = !!visibleModels[series.key];
                  return (
                    <label
                      key={series.key}
                      className="flex items-center justify-between px-2 py-1.5 rounded-xl hover:bg-slate-50 dark:hover:bg-zinc-800/70 cursor-pointer transition select-none"
                    >
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => {
                            setVisibleModels(prev => ({
                              ...prev,
                              [series.key]: !prev[series.key]
                            }));
                          }}
                          className="rounded accent-indigo-600 cursor-pointer"
                        />
                        <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${series.color}`} />
                        <span className={`text-xs ${isChecked ? 'font-semibold text-slate-900 dark:text-zinc-100' : 'text-slate-400'}`}>
                          {series.label}
                        </span>
                      </div>
                    </label>
                  );
                })}
              </div>

              {/* Model Imputations */}
              <div className="pt-1.5 border-t border-slate-100 dark:border-zinc-800 space-y-1">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-1">
                  Imputation Models
                </div>
                {availableSeries.filter(s => !s.hasData).map(series => (
                  <div
                    key={series.key}
                    className="flex items-center justify-between px-2 py-1.5 rounded-xl opacity-60 cursor-not-allowed select-none bg-slate-50/50 dark:bg-zinc-800/50"
                  >
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={false}
                        disabled={true}
                        className="rounded cursor-not-allowed opacity-50"
                      />
                      <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${series.color}`} />
                      <span className="text-xs text-slate-500 dark:text-zinc-400">
                        {series.label}
                      </span>
                    </div>
                    <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-100/70 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400">
                      {series.statusText}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Subtle Divider (Desktop only) */}
        <div className="h-4 w-px bg-slate-200 dark:bg-zinc-700/80 mx-0.5 hidden xl:block" />

        {/* Tertiary Controls: Zoom (Desktop only, collapsed to More menu on smaller screens) */}
        <div className="hidden xl:flex items-center gap-0.5 p-0.5 h-8 rounded-lg bg-slate-100 dark:bg-zinc-800 border border-slate-200/60 dark:border-zinc-700/60">
          <button
            type="button"
            title="Zoom In (+)"
            aria-label="Zoom In"
            onClick={handleZoomIn}
            className="p-1 rounded-md text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-white dark:hover:bg-zinc-700 transition cursor-pointer"
          >
            <ProjectIcon name="zoom-in" size="sm" className="w-3 h-3" />
          </button>
          <button
            type="button"
            title="Zoom Out (-)"
            aria-label="Zoom Out"
            onClick={handleZoomOut}
            className="p-1 rounded-md text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-white dark:hover:bg-zinc-700 transition cursor-pointer"
          >
            <ProjectIcon name="zoom-out" size="sm" className="w-3 h-3" />
          </button>
          {zoomLevel !== 1 && (
            <div className="flex items-center gap-0.5">
              <span className="text-[10px] font-mono font-bold text-indigo-600 dark:text-indigo-400 px-1">
                {zoomLevel.toFixed(2).replace(/\.?0+$/, '')}×
              </span>
              <button
                type="button"
                title="Reset Zoom (1:1)"
                aria-label="Reset Zoom"
                onClick={handleResetZoom}
                className="p-1 rounded-md text-indigo-600 dark:text-indigo-400 hover:bg-white dark:hover:bg-zinc-700 transition cursor-pointer"
              >
                <ProjectIcon name="reset-zoom" size="sm" className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>

        {/* Grid Toggle Button (Desktop only, collapsed to More menu on smaller screens) */}
        <button
          type="button"
          title={showGrid ? 'Hide Gridlines' : 'Show Gridlines'}
          aria-label="Toggle Gridlines"
          onClick={() => setShowGrid(!showGrid)}
          className={`hidden xl:flex h-8 w-8 items-center justify-center rounded-lg border text-xs transition cursor-pointer shrink-0 ${
            showGrid 
              ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800' 
              : 'bg-slate-100 dark:bg-zinc-800 text-slate-400 border-slate-200/70 dark:border-zinc-700'
          }`}
        >
          <ProjectIcon name="grid" size="sm" className="w-3.5 h-3.5" />
        </button>

        {/* Secondary Action: Export Figure Button */}
        <button
          type="button"
          title="Export Research-Grade Analytical Figure (PNG)"
          aria-label="Export Research Figure"
          onClick={handleExportAnalyticalPNG}
          className="h-8 flex items-center gap-1.5 px-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold transition shadow-2xs cursor-pointer shrink-0"
        >
          <ProjectIcon name="camera" size="sm" className="w-3.5 h-3.5 text-white shrink-0" />
          <span>Export</span>
        </button>

        {/* Fullscreen Toggle */}
        <button
          type="button"
          title={isFullscreen ? 'Exit Fullscreen (Esc)' : 'Expand Fullscreen'}
          aria-label="Toggle Fullscreen"
          onClick={() => setIsFullscreen(!isFullscreen)}
          className="h-8 w-8 flex items-center justify-center rounded-lg border border-slate-200/70 dark:border-zinc-700 bg-slate-100 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 transition cursor-pointer shrink-0"
        >
          {isFullscreen ? (
            <ProjectIcon name="minimize" size="sm" className="w-3.5 h-3.5 text-indigo-600" />
          ) : (
            <ProjectIcon name="fullscreen" size="sm" className="w-3.5 h-3.5" />
          )}
        </button>

        {/* Overflow Menu (⋯) */}
        <div className="relative shrink-0" ref={dropdownRef}>
          <button
            type="button"
            title="Additional Chart & Data Actions"
            aria-label="Additional Actions"
            onClick={() => {
              setDropdownOpen(!dropdownOpen);
              setIsChannelDropdownOpen(false);
              setIsSeriesDropdownOpen(false);
            }}
            className="h-8 w-8 flex items-center justify-center rounded-lg border border-slate-200/70 dark:border-zinc-700 bg-slate-100 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 transition cursor-pointer"
          >
            <ProjectIcon name="more" size="sm" className="w-3.5 h-3.5" />
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-1.5 w-56 bg-white dark:bg-zinc-900 rounded-2xl shadow-xl border border-slate-200/80 dark:border-zinc-800 p-1.5 z-50 text-xs space-y-1">
              {/* Responsive actions for smaller screens */}
              <div className="xl:hidden border-b border-slate-100 dark:border-zinc-800 pb-1 mb-1">
                <button
                  type="button"
                  onClick={() => setShowGrid(!showGrid)}
                  className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-200 transition text-left cursor-pointer"
                >
                  <ProjectIcon name="grid" size="sm" className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                  <span>{showGrid ? 'Hide Gridlines' : 'Show Gridlines'}</span>
                </button>
                <div className="flex items-center justify-between px-2.5 py-1 text-slate-500 dark:text-zinc-400">
                  <span>Zoom</span>
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      onClick={handleZoomIn}
                      className="px-2 py-0.5 rounded bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 font-bold"
                    >
                      +
                    </button>
                    <button
                      type="button"
                      onClick={handleZoomOut}
                      className="px-2 py-0.5 rounded bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 font-bold"
                    >
                      -
                    </button>
                  </div>
                </div>
              </div>

              <div className="px-2.5 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Data & Export Options
              </div>
              <button
                type="button"
                onClick={handleExportAnalyticalPNG}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-200 transition text-left cursor-pointer"
              >
                <ProjectIcon name="camera" size="sm" className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                <span>Analytical PNG Figure</span>
              </button>
              <button
                type="button"
                onClick={handleExportCSV}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-200 transition text-left cursor-pointer"
              >
                <ProjectIcon name="database" size="sm" className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                <span>Raw CSV Telemetry</span>
              </button>
              <button
                type="button"
                onClick={handleExportJSON}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-200 transition text-left cursor-pointer"
              >
                <ProjectIcon name="export" size="sm" className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                <span>Structured JSON Payload</span>
              </button>
              <div className="border-t border-slate-100 dark:border-zinc-800 pt-1">
                <button
                  type="button"
                  onClick={() => {
                    handleResetZoom();
                    setShowGrid(true);
                    setDropdownOpen(false);
                  }}
                  className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-500 dark:text-zinc-400 transition text-left cursor-pointer"
                >
                  <ProjectIcon name="refresh" size="sm" className="w-3.5 h-3.5 shrink-0" />
                  <span>Reset Chart View</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  ), [
    sampleIdx,
    setSampleIdx,
    maxSamples,
    isChannelDropdownOpen,
    isSeriesDropdownOpen,
    channelObj,
    channelUnit,
    criteriaPollutants,
    targetPollutant,
    setTargetPollutant,
    meteorologyChannels,
    trafficChannels,
    activeSeriesCount,
    availableSeries,
    visibleModels,
    setVisibleModels
  ]);

  // LAYER 4: Footer Legend & Observation Summary Bar (memoized)
  const footer = useMemo(() => (
    <div className="space-y-2.5">
      {/* Legend and Summary Statistics */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Scientific Legend */}
        <div className="flex items-center gap-4 text-[11px] text-slate-600 dark:text-zinc-400">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500 shrink-0" />
            <span className="font-medium text-slate-800 dark:text-zinc-200">Observed Measurement</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full border-2 border-red-500 bg-transparent shrink-0" />
            <span className="font-medium text-slate-800 dark:text-zinc-200">Natural Missing (Sensor Dropout)</span>
          </div>
          {visibleModels.groundTruth && (
            <div className="flex items-center gap-1.5">
              <span className="w-4 h-0.5 border-t-2 border-dashed border-slate-400 dark:border-zinc-500 shrink-0" />
              <span className="font-medium text-slate-500 dark:text-zinc-400">Ground Truth Baseline</span>
            </div>
          )}
        </div>

        {/* Observation Quality Statistics */}
        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span className="text-slate-700 dark:text-zinc-300 font-semibold">
            {observedCount}/{totalPoints} Hours Observed ({observedPct}%)
          </span>
          {naturalMissingCount > 0 ? (
            <span className="text-amber-600 dark:text-amber-400 font-semibold">
              • {naturalMissingCount} Missing Dropout{naturalMissingCount > 1 ? 's' : ''}
            </span>
          ) : (
            <span className="text-emerald-600 dark:text-emerald-400 font-semibold">
              • 100% Sensor Completeness
            </span>
          )}
        </div>
      </div>

      {/* Segmented 24-Hour Timeline Bar */}
      <div className="flex items-center gap-0.5 w-full h-2 rounded-full overflow-hidden bg-slate-100 dark:bg-zinc-800 p-0.5">
        {chartData.map((pt, idx) => {
          const isObs = pt.observed !== null;
          return (
            <div
              key={idx}
              className={`flex-1 h-full rounded-xs transition-opacity hover:opacity-80 cursor-help ${
                isObs ? 'bg-blue-500' : 'bg-red-400 dark:bg-red-500'
              }`}
              title={`Hour ${pt.hour} (${pt.timestamp}): ${isObs ? `Observed (${pt.observed} ${channelUnit})` : 'Natural Missing (Sensor Dropout)'}`}
            />
          );
        })}
      </div>
    </div>
  ), [visibleModels.groundTruth, observedCount, totalPoints, observedPct, naturalMissingCount, chartData, channelUnit]);

  return (
    <div className={`space-y-5 select-none ${isDashboard ? '' : 'pb-6'}`}>
      {/* 1. Primary Page Identity with Scroll Morphed Section Header */}
      {!isDashboard && (
        <div>
          <SectionHeading
            id="trajectory-explorer"
            title="24-Hour Concentration Trajectory"
            shortTitle="24h Trajectory"
            icon="trajectory"
          />
          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-zinc-400 mt-1 pl-0.5 flex-wrap">
            <strong className="text-slate-800 dark:text-zinc-200 font-semibold">{stationDisplayName}</strong>
            <span className="text-slate-300 dark:text-zinc-700">·</span>
            <span>Hong Kong EPD</span>
            <span className="text-slate-300 dark:text-zinc-700">·</span>
            <span>{formattedDate}</span>
            <span className="text-slate-300 dark:text-zinc-700">·</span>
            <span>00:00–23:00</span>
          </div>
        </div>
      )}

      {/* 2. Trajectory Hero Workspace */}
      <ChartWidget
        showHeader={false}
        title={null}
        data={chartData}
        station={stationDisplayName}
        dataset="Hong Kong EPD Air Quality Network (2019–2021)"
        sampleIdx={sampleIdx}
        pollutant={targetPollutant}
        isDark={isDark}
        controlsBar={renderControlsBar}
        footer={footer}
        height="h-[480px]"
        isLoading={isLoading}
      >
        {({ showGrid, zoomLevel = 1 }) => {
          // Anchor Y-axis origin strictly at 0, with top as overall channel max (+5 buffer)
          const allVals = [];
          if (Array.isArray(chartData) && chartData.length > 0) {
            chartData.forEach(d => {
              if (d.actual != null && !isNaN(d.actual)) allVals.push(d.actual);
              if (d.observed != null && !isNaN(d.observed)) allVals.push(d.observed);
              if (d.transformer != null && !isNaN(d.transformer)) allVals.push(d.transformer);
              if (d.linear != null && !isNaN(d.linear)) allVals.push(d.linear);
              if (d.knn != null && !isNaN(d.knn)) allVals.push(d.knn);
              if (d.mlp != null && !isNaN(d.mlp)) allVals.push(d.mlp);
            });
          }

          const dataMax = allVals.length > 0 ? Math.max(...allVals) : 0;
          const channelOverallMax = channelObj?.max != null ? channelObj.max : (dataMax || 35);
          const yMax = Math.max(channelOverallMax, dataMax);
          let yDomain = [0, yMax];

          if (zoomLevel && zoomLevel !== 1) {
            const span = Math.max(yMax, 5) / zoomLevel;
            yDomain = [0, Math.ceil(span)];
          }

          return (
            <div
              className={`w-full h-full ${
                prefersReducedMotion
                  ? ''
                  : slideDirection === 'forward'
                  ? `motion-curve-slide-forward-${curveAnimToggle}`
                  : slideDirection === 'backward'
                  ? `motion-curve-slide-backward-${curveAnimToggle}`
                  : 'motion-curve-initial'
              }`}
            >
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 18, right: 28, left: 16, bottom: 16 }}>
                  {showGrid && (
                    <CartesianGrid 
                      strokeDasharray="3 3" 
                      stroke={gridStroke} 
                      horizontal={true} 
                      vertical={true}
                      verticalValues={fourHourTicks}
                    />
                  )}

                  {/* X-Axis: Clean 4-Hour Hourly Intervals with increased label tickMargin */}
                  <XAxis 
                    dataKey="hour" 
                    ticks={fourHourTicks}
                    stroke={axisStroke} 
                    fontSize={11} 
                    tickLine={true} 
                    tickMargin={12}
                    tickFormatter={(val) => {
                      if (typeof val === 'string' && val.includes(':')) {
                        return val.slice(0, 5);
                      }
                      return val;
                    }}
                  />

                  {/* Y-Axis: Channel-Specific Unit with increased label tickMargin */}
                  <YAxis 
                    stroke={axisStroke} 
                    fontSize={11} 
                    tickLine={true} 
                    tickMargin={12}
                    width={80}
                    unit={` ${channelUnit}`} 
                    domain={yDomain}
                    allowDataOverflow={true}
                  />

                  <Tooltip 
                    content={<GlassmorphicTooltip isDark={isDark} unit={channelUnit} />} 
                  />

                  {/* 1. Ground Truth Reference (Dashed baseline) */}
                  {visibleModels.groundTruth && (
                    <Line 
                      type="linear" 
                      dataKey="actual" 
                      stroke={isDark ? '#52525b' : '#cbd5e1'} 
                      strokeWidth={1.5} 
                      strokeDasharray="3 3" 
                      dot={false} 
                      name="Ground Truth" 
                      isAnimationActive={!prefersReducedMotion}
                      animationDuration={slideDirection === 'initial' ? 450 : 250}
                      animationEasing="ease-out"
                    />
                  )}

                  {/* 2. Observed Points: Scientifically honest - line breaks on NaNs (connectNulls=false) */}
                  {visibleModels.observed && (
                    <Line 
                      type="linear" 
                      dataKey="observed" 
                      stroke="#3b82f6" 
                      strokeWidth={2.2} 
                      dot={{ stroke: '#3b82f6', strokeWidth: 2, fill: isDark ? '#18181b' : '#ffffff', r: 4 }} 
                      connectNulls={false} 
                      name="Observed Measurements" 
                      isAnimationActive={!prefersReducedMotion}
                      animationDuration={slideDirection === 'initial' ? 450 : 250}
                      animationEasing="ease-out"
                    />
                  )}

                  {/* 3. Natural Missingness: Distinct hollow marker dots without drawing lines through missing intervals */}
                  {visibleModels.hiddenTarget && (
                    <Line 
                      type="linear" 
                      dataKey="naturalMissing" 
                      stroke="transparent" 
                      dot={{ stroke: '#ef4444', strokeWidth: 2, fill: isDark ? '#18181b' : '#ffffff', r: 5 }} 
                      name="Natural Missing Dropout" 
                      isAnimationActive={!prefersReducedMotion}
                      animationDuration={slideDirection === 'initial' ? 450 : 250}
                      animationEasing="ease-out"
                    />
                  )}

                  {/* 4. Model Imputation (Only renders when non-null) */}
                  {visibleModels.transformer && (
                    <Line 
                      type="linear" 
                      dataKey="transformer" 
                      stroke="#10b981" 
                      strokeWidth={2.5} 
                      dot={false} 
                      connectNulls={false}
                      name="CTDI Transformer" 
                      isAnimationActive={!prefersReducedMotion}
                      animationDuration={slideDirection === 'initial' ? 500 : 280}
                      animationEasing="ease-out"
                    />
                  )}

                  {/* 5. Baselines (When evaluated) */}
                  {visibleModels.linear && (
                    <Line 
                      type="linear" 
                      dataKey="linear" 
                      stroke="#f59e0b" 
                      strokeWidth={1.5} 
                      strokeDasharray="4 4" 
                      dot={false} 
                      connectNulls={false}
                      name="Linear Baseline" 
                      isAnimationActive={!prefersReducedMotion}
                      animationDuration={slideDirection === 'initial' ? 450 : 250}
                      animationEasing="ease-out"
                    />
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          );
        }}
      </ChartWidget>
    </div>
  );
}
