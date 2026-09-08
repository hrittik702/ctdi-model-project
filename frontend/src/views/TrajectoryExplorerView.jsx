import React from 'react';
import { Card, Button, Chip } from '@heroui/react';
import ProjectIcon from '../components/ui/ProjectIcon';
import InfoTooltip from '../components/ui/InfoTooltip';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid 
} from 'recharts';

import ChartWidget from '../components/ChartWidget';
import GlassmorphicTooltip from '../components/GlassmorphicTooltip';
import MissingnessBar from '../components/MissingnessBar';

export default function TrajectoryExplorerView({
  sampleIdx,
  setSampleIdx,
  maxSamples = 625,
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
  const pData = sampleData?.pollutants?.[targetPollutant];

  // Safe metrics extraction
  const tfMae = pData?.sample_mae?.transformer ?? null;
  const linMae = pData?.sample_mae?.linear ?? null;
  const hiddenCount = pData?.hidden_count ?? null;

  return (
    <div className="space-y-5">
      {/* Main 24H Trajectory Chart Container (Positioned immediately after info cards) */}
      <ChartWidget
        title={`24-Hour Concentration Trajectory: ${targetPollutant}`}
        subtitle={`Continuous window #${sampleIdx} (${sampleData?.timestamps?.[0] || '00:00'} → ${sampleData?.timestamps?.[23] || '23:00'})`}
        data={chartData}
        sampleIdx={sampleIdx}
        pollutant={targetPollutant}
        isDark={isDark}
        badges={[
          { 
            label: hiddenCount !== null ? `Hidden: ${hiddenCount} / 24 hrs` : 'Hidden: N/A', 
            variant: 'secondary' 
          },
          { 
            label: tfMae !== null ? `Transformer MAE: ${tfMae.toFixed(2)} µg/m³` : 'Transformer MAE: N/A', 
            color: 'success' 
          },
          { 
            label: linMae !== null ? `Linear MAE: ${linMae.toFixed(2)} µg/m³` : 'Linear MAE: N/A', 
            color: 'warning' 
          }
        ]}
        height="h-[430px]"
      >
        {({ showGrid }) => (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />}
              <XAxis dataKey="hour" stroke={axisStroke} fontSize={12} tickLine={false} />
              <YAxis stroke={axisStroke} fontSize={12} tickLine={false} unit=" µg/m³" />
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

              {/* Hidden Target evaluation points */}
              {visibleModels.hiddenTarget && (
                <Line 
                  type="monotone" 
                  dataKey="hiddenTarget" 
                  stroke="transparent" 
                  dot={{ stroke: '#ef4444', strokeWidth: 2, fill: 'transparent', r: 5 }} 
                  name="Hidden Target" 
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
                  strokeDasharray="3 3" 
                  dot={false} 
                  name="MLP Autoencoder" 
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )}
      </ChartWidget>

      {/* Analytical Controls Card (Situated cleanly below the graph) */}
      <Card className="bg-white dark:bg-zinc-900/90 p-5 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-xs hover:shadow-sm transition space-y-4">
        {/* Row 1: Sample Stepper & Pollutant Channel Selector */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          {/* Sample Navigation */}
          <div className="flex flex-wrap items-center gap-3 sm:gap-4">
            <span className="text-xs font-semibold text-slate-400 dark:text-zinc-500 uppercase tracking-wider">
              24H Sequence Window:
            </span>

            {/* Stepper Buttons */}
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-zinc-800 p-1 rounded-xl border border-slate-200/60 dark:border-zinc-700/60">
              <Button 
                size="sm"
                variant="secondary"
                onPress={() => setSampleIdx(prev => Math.max(0, prev - 1))}
                isDisabled={sampleIdx <= 0}
                aria-label="Previous 24-hour sample"
                className="min-w-8 h-8 p-0 dark:bg-zinc-700 dark:text-zinc-200 cursor-pointer"
              >
                <ProjectIcon name="chevron-left" size="sm" className="w-4 h-4" />
              </Button>
              <span className="text-sm font-bold px-3 text-slate-800 dark:text-zinc-200 font-mono">
                #{sampleIdx}
              </span>
              <Button 
                size="sm"
                variant="secondary"
                onPress={() => setSampleIdx(prev => Math.min(maxSamples - 1, prev + 1))}
                isDisabled={sampleIdx >= maxSamples - 1}
                aria-label="Next 24-hour sample"
                className="min-w-8 h-8 p-0 dark:bg-zinc-700 dark:text-zinc-200 cursor-pointer"
              >
                <ProjectIcon name="chevron-right" size="sm" className="w-4 h-4" />
              </Button>
            </div>

            {/* Slider with Step Context */}
            <div className="flex items-center gap-2">
              <input
                type="range"
                min={0}
                max={maxSamples - 1}
                value={sampleIdx}
                onChange={(e) => setSampleIdx(parseInt(e.target.value))}
                className="w-32 sm:w-48 accent-indigo-600 cursor-pointer h-2 bg-slate-200 dark:bg-zinc-700 rounded-lg"
              />
              <span className="text-xs font-medium text-slate-400 dark:text-zinc-500 font-mono">
                / {maxSamples - 1}
              </span>
            </div>
          </div>

          {/* Pollutant Pills */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs font-semibold text-slate-400 dark:text-zinc-500 uppercase tracking-wider mr-1">
              Pollutant:
            </span>
            {pollutants.map(p => {
              const isSelected = targetPollutant === p;
              return (
                <button
                  key={p}
                  type="button"
                  onClick={() => setTargetPollutant(p)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all duration-150 cursor-pointer ${
                    isSelected
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100/90 dark:bg-zinc-800 text-slate-600 dark:text-zinc-300 hover:bg-slate-200/80 dark:hover:bg-zinc-700'
                  }`}
                >
                  {p}
                </button>
              );
            })}
          </div>
        </div>

        {/* Row 2: Missingness Distribution Bar */}
        <MissingnessBar
          observedMask={pData?.observed_mask || []}
          evalMask={pData?.eval_mask || []}
          hours={sampleData?.hours || []}
        />

        {/* Row 3: Interactive Curve Series Legend Chips */}
        <div className="pt-2 border-t border-slate-100 dark:border-zinc-800 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-400 dark:text-zinc-500 uppercase tracking-wider mr-2">
            Active Curves:
          </span>
          {curveSeries.map(item => {
            const isActive = visibleModels[item.key];
            return (
              <div key={item.key} className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => setVisibleModels(v => ({ ...v, [item.key]: !v[item.key] }))}
                  className={`px-3 py-1.5 rounded-xl text-xs flex items-center gap-2 transition-all duration-150 cursor-pointer border ${
                    isActive 
                      ? item.activeStyle 
                      : 'bg-slate-100/70 dark:bg-zinc-800/70 text-slate-400 dark:text-zinc-500 border-transparent hover:bg-slate-200/60 dark:hover:bg-zinc-700 hover:text-slate-600 dark:hover:text-zinc-300'
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full shrink-0 ${isActive ? item.dotColor : 'bg-slate-300 dark:bg-zinc-600'}`} />
                  <span className="truncate">{item.label}</span>
                  {isActive && <ProjectIcon name="check" size="xs" className="w-3 h-3 ml-0.5 opacity-80 shrink-0" />}
                </button>
                <InfoTooltip term={item.label} />
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
