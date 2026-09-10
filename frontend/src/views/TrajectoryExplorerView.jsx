import React, { useState, useRef, useEffect } from 'react';
import { Card } from '@heroui/react';
import { Layers, ChevronDown, Wind } from 'lucide-react';
import ProjectIcon from '../components/ui/ProjectIcon';
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
import MissingnessBar from '../components/MissingnessBar';

// Custom SVG renderer for evaluation points: dynamic hue, saturation, and radius based on pointwise error
const DynamicErrorDot = (props) => {
  const { cx, cy, payload } = props;
  if (!cx || !cy || payload?.hiddenTarget == null) return null;

  const actual = payload.actual;
  const pred = payload.transformer;
  const error = (actual != null && pred != null) ? Math.abs(pred - actual) : 0;

  // Continuous mapping: error 0 to 25+ µg/m³
  const norm = Math.min(error / 25, 1);
  const hue = Math.max(0, Math.round(36 - norm * 36));
  const sat = Math.min(100, Math.round(45 + norm * 55));
  const light = Math.max(44, Math.round(58 - norm * 14));

  let r = 4;
  if (error >= 15) r = 7.5;
  else if (error >= 5) r = 5.5;

  const color = `hsl(${hue}, ${sat}%, ${light}%)`;
  const isHighError = error >= 15;

  return (
    <g key={`err-dot-${cx}-${cy}`}>
      {isHighError && (
        <circle
          cx={cx}
          cy={cy}
          r={r + 3.5}
          fill="none"
          stroke={color}
          strokeWidth={1.5}
          strokeOpacity={0.45}
          className="animate-pulse"
        />
      )}
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill={color}
        stroke="#ffffff"
        strokeWidth={1.5}
      >
        <title>{`Hour ${payload.hour}: Actual ${actual} µg/m³, Imputed ${pred} µg/m³, Error Δ=${error.toFixed(2)} µg/m³`}</title>
      </circle>
    </g>
  );
};

export default function TrajectoryExplorerView({
  sampleIdx,
  setSampleIdx,
  maxSamples = 1500,
  targetPollutant,
  setTargetPollutant,
  pollutants = [],
  sampleData,
  chartData = [],
  visibleModels,
  setVisibleModels,
  curveSeries = [],
  isDark = false,
  gridStroke,
  axisStroke
}) {
  const [isCurvesDropdownOpen, setIsCurvesDropdownOpen] = useState(false);
  const [stepHours, setStepHours] = useState(24);
  const curvesDropdownRef = useRef(null);

  // Dynamically calculate 4-hour interval tick marks from the active sliding window's real hours
  const fourHourTicks = [0, 4, 8, 12, 16, 20, 23]
    .map(idx => chartData[idx]?.hour)
    .filter(Boolean);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (curvesDropdownRef.current && !curvesDropdownRef.current.contains(e.target)) {
        setIsCurvesDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const pData = sampleData?.pollutants?.[targetPollutant];

  // Safe metrics extraction
  const tfMae = pData?.sample_mae?.transformer ?? null;
  const linMae = pData?.sample_mae?.linear ?? null;
  const hiddenCount = pData?.hidden_count ?? null;
  const activeCurvesCount = Object.values(visibleModels).filter(Boolean).length;

  // Day vs Hour stepping calculations
  const isDayMode = stepHours === 24;
  const totalDays = Math.floor(maxSamples / 24); // 62 days
  const currentStep = isDayMode ? Math.floor(sampleIdx / 24) : sampleIdx;
  const maxStep = isDayMode ? totalDays - 1 : maxSamples - 1;
  const denominatorLabel = isDayMode ? `${totalDays}` : `${maxSamples - 1}`;

  // Integrated Graph Header Controls (Window Slider/Stepper + Pollutant select + Curves Dropdown Checkbox)
  const headerControls = (
    <div className="flex items-center gap-1.5 flex-wrap sm:flex-nowrap">
      {/* 24-Hour Sequence Window Slider & Stepper */}
      <div className="flex items-center gap-1 px-2 py-1 rounded-xl bg-slate-100 dark:bg-zinc-800 border border-slate-200/70 dark:border-zinc-700/70 text-xs shadow-2xs">
        <button
          type="button"
          onClick={() => {
            if (isDayMode) {
              setSampleIdx(prev => Math.max(0, prev - 24));
            } else {
              setSampleIdx(prev => Math.max(0, prev - 1));
            }
          }}
          disabled={sampleIdx <= 0}
          title={isDayMode ? 'Previous Day (-24h)' : 'Previous Hour (-1h)'}
          aria-label={isDayMode ? 'Previous Day (-24h)' : 'Previous Hour (-1h)'}
          className="p-1 rounded-lg text-slate-600 hover:text-slate-900 dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-white dark:hover:bg-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed transition cursor-pointer"
        >
          <ProjectIcon name="chevron-left" size="sm" className="w-3.5 h-3.5" />
        </button>

        <span
          className="text-xs font-bold font-mono text-slate-800 dark:text-zinc-200 min-w-8 text-center"
          title={isDayMode ? `Day ${currentStep + 1} of ${totalDays} (Window #${sampleIdx})` : `Window #${sampleIdx} of ${maxSamples - 1}`}
        >
          #{currentStep}
        </span>

        <button
          type="button"
          onClick={() => {
            if (isDayMode) {
              setSampleIdx(prev => Math.min((totalDays - 1) * 24, prev + 24));
            } else {
              setSampleIdx(prev => Math.min(maxSamples - 1, prev + 1));
            }
          }}
          disabled={isDayMode ? sampleIdx >= (totalDays - 1) * 24 : sampleIdx >= maxSamples - 1}
          title={isDayMode ? 'Next Day (+24h)' : 'Next Hour (+1h)'}
          aria-label={isDayMode ? 'Next Day (+24h)' : 'Next Hour (+1h)'}
          className="p-1 rounded-lg text-slate-600 hover:text-slate-900 dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-white dark:hover:bg-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed transition cursor-pointer"
        >
          <ProjectIcon name="chevron-right" size="sm" className="w-3.5 h-3.5" />
        </button>

        <input
          type="range"
          min={0}
          max={maxStep}
          step={1}
          value={currentStep}
          onChange={(e) => {
            const val = parseInt(e.target.value, 10);
            setSampleIdx(isDayMode ? val * 24 : val);
          }}
          title={isDayMode ? `Day ${currentStep + 1} of ${totalDays} (Window #${currentStep * 24})` : `Window #${sampleIdx} / ${maxSamples - 1}`}
          aria-label="24H Sequence Window Slider"
          className="w-16 sm:w-24 md:w-28 accent-indigo-600 cursor-pointer h-1.5 bg-slate-200 dark:bg-zinc-700 rounded-lg"
        />

        <button
          type="button"
          onClick={() => setStepHours(prev => prev === 24 ? 1 : 24)}
          title={`Click to switch step mode (currently ${isDayMode ? '±24h Daily' : '±1h Hourly'})`}
          className="px-1.5 py-0.5 rounded-md font-mono text-[10px] font-bold bg-indigo-100/80 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-200 dark:hover:bg-indigo-900 border border-indigo-200/80 dark:border-indigo-800/80 transition cursor-pointer shrink-0"
        >
          ±{stepHours}h
        </button>

        <span className="text-[10px] font-mono text-slate-400 dark:text-zinc-500 hidden sm:inline min-w-7">
          /{denominatorLabel}
        </span>
      </div>

      {/* Pollutant Channel Selector Dropdown */}
      <div className="flex items-center gap-1 px-2 py-1 rounded-xl bg-slate-100 dark:bg-zinc-800 border border-slate-200/70 dark:border-zinc-700/70 text-xs font-semibold text-slate-800 dark:text-zinc-200 shadow-2xs">
        <Wind className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
        <select
          value={targetPollutant}
          onChange={(e) => setTargetPollutant(e.target.value)}
          className="bg-transparent border-none outline-none cursor-pointer text-xs font-bold text-slate-800 dark:text-zinc-100 pr-1"
          title="Select Pollutant Channel"
          aria-label="Select Pollutant Channel"
        >
          {pollutants.map(p => (
            <option key={p} value={p} className="bg-white dark:bg-zinc-900 text-slate-800 dark:text-zinc-100">
              {p}
            </option>
          ))}
        </select>
      </div>

      {/* Active Curve Selection Dropdown Checkbox Menu */}
      <div className="relative" ref={curvesDropdownRef}>
        <button
          type="button"
          onClick={() => setIsCurvesDropdownOpen(prev => !prev)}
          title="Active Curve Visibility Selection"
          aria-label="Active Curve Selection"
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-xl border text-xs font-semibold transition cursor-pointer shadow-2xs ${
            isCurvesDropdownOpen
              ? 'bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 border-indigo-300 dark:border-indigo-700'
              : 'bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-200 border-slate-200/70 dark:border-zinc-700/70 hover:bg-slate-200/70 dark:hover:bg-zinc-700'
          }`}
        >
          <Layers className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
          <span className="hidden sm:inline">Curves</span>
          <span className="px-1.5 py-0.2 rounded-md bg-white dark:bg-zinc-700 text-[10px] font-bold text-indigo-600 dark:text-indigo-300 border border-slate-200/60 dark:border-zinc-600">
            {activeCurvesCount}/{curveSeries.length}
          </span>
          <ChevronDown className="w-3 h-3 text-slate-400 shrink-0" />
        </button>

        {isCurvesDropdownOpen && (
          <div className="absolute right-0 mt-1.5 w-64 bg-white dark:bg-zinc-900 rounded-2xl shadow-xl border border-slate-200/90 dark:border-zinc-800 p-2.5 z-40 text-xs space-y-2 animate-in fade-in zoom-in-95 duration-100">
            {/* Dropdown Header with Quick Actions */}
            <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-zinc-800">
              <span className="font-bold text-slate-900 dark:text-zinc-100 text-[11px] uppercase tracking-wider">
                Visible Curves ({activeCurvesCount})
              </span>
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => {
                    const allOn = {};
                    curveSeries.forEach(s => { allOn[s.key] = true; });
                    setVisibleModels(allOn);
                  }}
                  className="px-1.5 py-0.5 rounded text-[10px] font-bold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/60 transition cursor-pointer"
                >
                  All
                </button>
                <span className="text-slate-300 dark:text-zinc-700">•</span>
                <button
                  type="button"
                  onClick={() => {
                    setVisibleModels({
                      groundTruth: true,
                      observed: true,
                      hiddenTarget: true,
                      transformer: true,
                      linear: true,
                      knn: false,
                      mlp: false
                    });
                  }}
                  className="px-1.5 py-0.5 rounded text-[10px] font-bold text-slate-500 hover:bg-slate-100 dark:hover:bg-zinc-800 transition cursor-pointer"
                >
                  Default
                </button>
                <span className="text-slate-300 dark:text-zinc-700">•</span>
                <button
                  type="button"
                  onClick={() => {
                    const allOff = {};
                    curveSeries.forEach(s => { allOff[s.key] = false; });
                    setVisibleModels(allOff);
                  }}
                  className="px-1.5 py-0.5 rounded text-[10px] font-bold text-slate-400 hover:text-slate-600 dark:hover:text-zinc-300 hover:bg-slate-100 dark:hover:bg-zinc-800 transition cursor-pointer"
                >
                  Clear
                </button>
              </div>
            </div>

            {/* Checkbox Series List (Show Only Selected) */}
            <div className="space-y-1 max-h-60 overflow-y-auto pr-0.5">
              {curveSeries.map(series => {
                const isChecked = !!visibleModels[series.key];
                return (
                  <div
                    key={series.key}
                    className={`group flex items-center justify-between px-2 py-1.5 rounded-xl transition select-none ${
                      isChecked
                        ? 'bg-slate-50 dark:bg-zinc-800/80 text-slate-900 dark:text-zinc-100 font-medium'
                        : 'text-slate-400 dark:text-zinc-500 hover:bg-slate-50 dark:hover:bg-zinc-800/40'
                    }`}
                  >
                    <label className="flex items-center gap-2 cursor-pointer flex-1 min-w-0">
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => {
                          setVisibleModels(prev => ({ ...prev, [series.key]: !prev[series.key] }));
                        }}
                        className="rounded accent-indigo-600 w-3.5 h-3.5 cursor-pointer shrink-0"
                      />
                      <span className={`w-2 h-2 rounded-full shrink-0 ${series.dotColor || 'bg-slate-500'}`} />
                      <span className="truncate text-xs">{series.label}</span>
                    </label>

                    {/* Quick "Only" action on hover to show only this selected curve */}
                    <button
                      type="button"
                      title={`Show only ${series.label}`}
                      onClick={() => {
                        const onlyThis = {};
                        curveSeries.forEach(s => { onlyThis[s.key] = (s.key === series.key); });
                        setVisibleModels(onlyThis);
                      }}
                      className="opacity-0 group-hover:opacity-100 text-[10px] font-bold text-indigo-600 dark:text-indigo-400 hover:underline px-1 py-0.5 rounded transition cursor-pointer"
                    >
                      Only
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-5">
      {/* Main 24H Trajectory Chart Container */}
      <ChartWidget
        title={`24-Hour Concentration Trajectory: ${targetPollutant}`}
        subtitle={`Window #${sampleIdx} (Day ${Math.floor(sampleIdx / 24) + 1} of ${totalDays}) • ${sampleData?.timestamps?.[0] || '00:00'} → ${sampleData?.timestamps?.[23] || '23:00'}`}
        data={chartData}
        sampleIdx={sampleIdx}
        pollutant={targetPollutant}
        isDark={isDark}
        headerControls={headerControls}
        badges={[
          { 
            label: hiddenCount !== null ? `Masked: ${hiddenCount} / 24 hrs (${Math.round((hiddenCount / 24) * 100)}%)` : 'Masked: N/A', 
            color: (hiddenCount ?? 0) > 0 ? 'danger' : 'default',
            variant: 'soft' 
          },
          { 
            label: tfMae !== null ? `Transformer MAE: ${tfMae.toFixed(2)} µg/m³` : 'Transformer MAE: N/A', 
            color: 'success',
            variant: 'soft' 
          },
          { 
            label: linMae !== null ? `Linear MAE: ${linMae.toFixed(2)} µg/m³` : 'Linear MAE: N/A', 
            color: 'warning',
            variant: 'soft' 
          }
        ]}
        height="h-[430px]"
      >
        {({ showGrid }) => (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
              {showGrid && (
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke={gridStroke} 
                  horizontal={true}
                  vertical={true}
                  verticalValues={fourHourTicks}
                />
              )}

              <XAxis 
                dataKey="hour" 
                ticks={fourHourTicks}
                stroke={axisStroke} 
                fontSize={12} 
                tickLine={true} 
              />
              <YAxis stroke={axisStroke} fontSize={12} tickLine={true} unit=" µg/m³" />
              <Tooltip content={<GlassmorphicTooltip isDark={isDark} />} />

              {/* Ground Truth reference curve */}
              {visibleModels.groundTruth && (
                <Line 
                  type="monotone" 
                  dataKey="actual" 
                  stroke={isDark ? '#e4e4e7' : '#0f172a'} 
                  strokeWidth={2.5} 
                  dot={false} 
                  name="Ground Truth" 
                />
              )}

              {/* Observed Points given to model */}
              {visibleModels.observed && (
                <Line 
                  type="monotone" 
                  dataKey="observed" 
                  stroke="transparent" 
                  dot={{ stroke: '#3b82f6', strokeWidth: 2, fill: '#3b82f6', r: 4 }} 
                  name="Observed Points" 
                />
              )}

              {/* Hidden Target evaluation points with dynamic error-based hue & saturation */}
              {visibleModels.hiddenTarget && (
                <Line 
                  type="monotone" 
                  dataKey="hiddenTarget" 
                  stroke="transparent" 
                  dot={<DynamicErrorDot />} 
                  name="Hidden Target (Error Scaled)" 
                />
              )}

              {/* CTDI Transformer reconstructed curve */}
              {visibleModels.transformer && (
                <Line 
                  type="monotone" 
                  dataKey="transformer" 
                  stroke="#10b981" 
                  strokeWidth={2.8} 
                  dot={false} 
                  name="CTDI Transformer" 
                />
              )}

              {/* Linear baseline */}
              {visibleModels.linear && (
                <Line 
                  type="monotone" 
                  dataKey="linear" 
                  stroke="#f59e0b" 
                  strokeWidth={1.8} 
                  strokeDasharray="4 4" 
                  dot={false} 
                  name="Linear Interpolation" 
                />
              )}

              {/* KNN Baseline */}
              {visibleModels.knn && (
                <Line 
                  type="monotone" 
                  dataKey="knn" 
                  stroke="#a855f7" 
                  strokeWidth={1.5} 
                  strokeDasharray="2 2" 
                  dot={false} 
                  name="KNN Imputer" 
                />
              )}

              {/* MLP Baseline */}
              {visibleModels.mlp && (
                <Line 
                  type="monotone" 
                  dataKey="mlp" 
                  stroke="#06b6d4" 
                  strokeWidth={1.5} 
                  strokeDasharray="2 2" 
                  dot={false} 
                  name="MLP Imputer" 
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )}
      </ChartWidget>

      {/* 24-Hour Observation Distribution Card */}
      <Card className="bg-white dark:bg-zinc-900/90 p-4 sm:p-5 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-xs hover:shadow-sm transition space-y-3">
        <MissingnessBar
          observedMask={pData?.observed_mask || []}
          evalMask={pData?.eval_mask || []}
          hours={sampleData?.hours || []}
        />

        {/* Dynamic Error Interpretability Scale Footer */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-2.5 border-t border-slate-100 dark:border-zinc-800/80 text-[11px]">
          <div className="flex items-center gap-1.5 text-slate-500 dark:text-zinc-400">
            <span className="font-semibold text-slate-700 dark:text-zinc-300">
              Pointwise Error Interpretability:
            </span>
            <span className="hidden sm:inline text-slate-400 dark:text-zinc-500">
              Evaluation dot radius & color dynamically scale with |y - ŷ|
            </span>
          </div>
          <div className="flex items-center gap-3.5 text-slate-600 dark:text-zinc-400 font-medium">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 ring-1 ring-amber-300" />
              <span>Minimal (&lt;5 µg/m³)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-orange-500 ring-1 ring-orange-400" />
              <span>Moderate (5–15 µg/m³)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3.5 h-3.5 rounded-full bg-red-600 ring-2 ring-red-400 animate-pulse" />
              <span className="text-red-600 dark:text-red-400 font-bold">High (&gt;15 µg/m³)</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
