import React, { useState } from 'react';
import { Card, Button, Chip, Spinner } from '@heroui/react';
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

export default function LiveImputationView({
  sampleIdx,
  liveRate,
  setLiveRate,
  liveMechanism,
  setLiveMechanism,
  liveSeed,
  setLiveSeed,
  liveResult,
  liveLoading,
  liveStep,
  onRunLiveImpute,
  targetPollutant,
  setTargetPollutant,
  pollutants = [],
  isDark = false,
  gridStroke,
  axisStroke
}) {
  const livePData = liveResult?.pollutants?.[targetPollutant];
  
  // Safe extraction of metrics avoiding any undefined or null
  const transformerMae = livePData?.sample_mae?.transformer ?? livePData?.tf_mae ?? null;
  const linearMae = livePData?.sample_mae?.linear ?? livePData?.lin_mae ?? null;
  const hiddenCount = livePData?.hidden_count ?? null;
  const observedCount = livePData?.observed_count ?? null;

  const liveChartData = liveResult?.hours?.map((hour, i) => {
    const isObs = livePData?.observed_mask?.[i] === 1;
    const isEval = livePData?.eval_mask?.[i] === 1;
    const act = livePData?.actual?.[i];
    const rawTimestamp = liveResult?.timestamps?.[i] || '';
    const clockTime = rawTimestamp.includes(' ') ? rawTimestamp.split(' ')[1] : hour;
    const datePart = rawTimestamp.includes(' ') ? rawTimestamp.split(' ')[0] : '';

    return {
      hour: clockTime,
      time: clockTime,
      stepOffset: `+${i}h`,
      date: datePart,
      timestamp: rawTimestamp,
      actual: act,
      observed: isObs ? act : null,
      hiddenTarget: isEval ? act : null,
      transformer: livePData?.transformer?.[i],
      linear: livePData?.linear?.[i]
    };
  }) || [];

  return (
    <div className="space-y-5">
      {/* 1. Main Graph Component (Positioned immediately after info cards) */}
      {liveResult ? (
        <ChartWidget
          title={`Live Neural Imputation Result: ${targetPollutant}`}
          subtitle={`${liveMechanism.toUpperCase()} Masking @ ${Math.round(liveRate * 100)}% on Sample #${sampleIdx} (Seed ${liveSeed})`}
          data={liveChartData}
          sampleIdx={sampleIdx}
          pollutant={targetPollutant}
          isDark={isDark}
          badges={[
            { 
              label: hiddenCount !== null ? `Masked: ${hiddenCount} / 24 hrs` : 'Masked: N/A', 
              variant: 'secondary' 
            },
            { 
              label: transformerMae !== null ? `Transformer MAE: ${transformerMae.toFixed(2)} µg/m³` : 'Transformer MAE: N/A', 
              color: 'success' 
            },
            { 
              label: linearMae !== null ? `Linear MAE: ${linearMae.toFixed(2)} µg/m³` : 'Linear MAE: N/A', 
              color: 'warning' 
            }
          ]}
          height="h-[400px]"
        >
          {({ showGrid }) => (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={liveChartData} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
                {showGrid && (
                  <CartesianGrid 
                    strokeDasharray="3 3" 
                    stroke={gridStroke} 
                    horizontal={true}
                    vertical={true}
                    verticalValues={['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:00']}
                  />
                )}
                <XAxis 
                  dataKey="hour" 
                  ticks={['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:00']}
                  stroke={axisStroke} 
                  fontSize={12} 
                  tickLine={true} 
                />
                <YAxis stroke={axisStroke} fontSize={12} tickLine={true} unit=" µg/m³" />
                <Tooltip content={<GlassmorphicTooltip isDark={isDark} />} />
                <Legend />
                <Line type="monotone" dataKey="actual" stroke={isDark ? '#e4e4e7' : '#0f172a'} strokeWidth={2.5} dot={false} name="Actual Ground Truth" />
                <Line type="monotone" dataKey="transformer" stroke="#10b981" strokeWidth={3} dot={false} name="Live CTDI Transformer" />
                <Line type="monotone" dataKey="linear" stroke="#f59e0b" strokeWidth={2} strokeDasharray="4 4" dot={false} name="Linear Interpolation" />
                <Line type="monotone" dataKey="hiddenTarget" stroke="transparent" dot={{ stroke: '#ef4444', strokeWidth: 2, fill: 'transparent', r: 6 }} name="Masked Evaluation Points" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </ChartWidget>
      ) : (
        <Card className="bg-white dark:bg-zinc-900/90 p-12 rounded-2xl border border-dashed border-slate-300 dark:border-zinc-800 flex flex-col items-center justify-center text-center space-y-3 h-[380px]">
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 flex items-center justify-center">
            <ProjectIcon name="sparkles" size="2xl" className="w-6 h-6" />
          </div>
          <h4 className="font-bold text-slate-800 dark:text-zinc-200 text-sm">
            Interactive Neural Imputation Sandbox
          </h4>
          <p className="text-xs text-slate-400 dark:text-zinc-500 max-w-sm">
            Configure corruption pattern, missingness rate, and reproducibility seed below, then click <strong>Execute Live Imputation</strong> to test real-time PyTorch reconstruction.
          </p>
        </Card>
      )}

      {/* 2. Simulation Controls Card (Positioned below the graph) */}
      <Card className="bg-white dark:bg-zinc-900/90 p-5 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-zinc-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 rounded-xl shrink-0">
              <ProjectIcon name="sandbox" size="md" className="w-4 h-4 text-indigo-600" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 dark:text-zinc-100 text-sm">Simulation Parameters & Execution</h3>
              <p className="text-[11px] text-slate-400 dark:text-zinc-500">Configure synthetic corruption pattern and run real-time model inference</p>
            </div>
          </div>

          <div className="p-2 bg-slate-50 dark:bg-zinc-800/40 rounded-xl border border-slate-200/60 dark:border-zinc-800 flex items-center gap-2 text-xs">
            <ProjectIcon name="success" size="sm" className="w-3.5 h-3.5 text-emerald-600" />
            <span className="text-slate-500 dark:text-zinc-400 font-medium">Evaluation: Hidden ground-truth coordinates only</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 text-xs">
          {/* Target Pollutant Selector */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider">
              Target Channel
            </label>
            <div className="flex flex-wrap gap-1">
              {pollutants.map(p => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setTargetPollutant(p)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold transition cursor-pointer ${
                    targetPollutant === p
                      ? 'bg-indigo-600 text-white shadow-2xs'
                      : 'bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 hover:bg-slate-200'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Missing Rate */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1">
                <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider">
                  Missingness Rate
                </label>
                <InfoTooltip term="Missing Rate" />
              </div>
              <Chip color="accent" variant="soft" size="sm" className="bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-bold h-5 text-[10px]">
                <Chip.Label>{Math.round(liveRate * 100)}%</Chip.Label>
              </Chip>
            </div>
            <input
              type="range"
              min={0.10}
              max={0.80}
              step={0.05}
              value={liveRate}
              onChange={e => setLiveRate(parseFloat(e.target.value))}
              className="w-full accent-indigo-600 cursor-pointer h-2 bg-slate-200 dark:bg-zinc-700 rounded-lg"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>10% (Sparse)</span>
              <span>80% (Severe)</span>
            </div>
          </div>

          {/* Missing Mechanism */}
          <div className="space-y-1.5">
            <div className="flex items-center gap-1">
              <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider">
                Corruption Mechanism
              </label>
              <InfoTooltip term="MCAR" />
            </div>
            <select
              value={liveMechanism}
              onChange={e => setLiveMechanism(e.target.value)}
              className="w-full border border-slate-200 dark:border-zinc-700 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 shadow-2xs"
            >
              <option value="random">Random MCAR (Uniform Scattered)</option>
              <option value="block">Continuous Block (Sensor Blackout)</option>
            </select>
          </div>

          {/* Seed */}
          <div className="space-y-1.5">
            <div className="flex items-center gap-1">
              <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider">
                Reproducibility Seed
              </label>
              <InfoTooltip term="Reproducibility Seed" />
            </div>
            <input
              type="number"
              value={liveSeed}
              onChange={e => setLiveSeed(parseInt(e.target.value) || 0)}
              className="w-full border border-slate-200 dark:border-zinc-700 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 font-mono shadow-2xs"
            />
          </div>
        </div>

        {/* Execution Button Row */}
        <div className="pt-2 flex items-center justify-between gap-4">
          <span className="text-xs text-slate-400 hidden sm:inline">
            FastAPI server executes PyTorch checkpoint <code className="text-slate-600 dark:text-zinc-300 font-mono">best_temporal_transformer.pt</code>
          </span>
          <Button
            variant="primary"
            size="md"
            onPress={onRunLiveImpute}
            isDisabled={liveLoading}
            className="w-full sm:w-auto px-6 bg-indigo-600 hover:bg-indigo-700 text-white font-bold flex items-center justify-center gap-2 py-2.5 rounded-xl shadow-xs cursor-pointer ml-auto"
          >
            {liveLoading ? <Spinner size="sm" color="current" /> : <ProjectIcon name="sandbox" size="sm" className="w-4 h-4 text-white" />}
            <span>
              {liveLoading ? (liveStep || 'Running PyTorch Model...') : 'Execute Live Imputation'}
            </span>
          </Button>
        </div>
      </Card>
    </div>
  );
}
