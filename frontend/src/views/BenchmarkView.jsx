import React, { useState } from 'react';
import { Card, Chip } from '@heroui/react';
import { 
  Trophy, 
  ArrowUpDown
} from 'lucide-react';
import ProjectIcon from '../components/ui/ProjectIcon';
import InfoTooltip from '../components/ui/InfoTooltip';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid 
} from 'recharts';

import ChartWidget from '../components/ChartWidget';

const getModelIcon = (modelName = '') => {
  if (modelName.includes('Transformer')) return 'transformer';
  if (modelName.includes('Linear')) return 'linear-interp';
  if (modelName.includes('KNN')) return 'knn';
  if (modelName.includes('MLP')) return 'mlp';
  return 'benchmark';
};

export default function BenchmarkView({
  metrics = [],
  isDark = false,
  gridStroke,
  axisStroke
}) {
  const [selectedMetric, setSelectedMetric] = useState('both');
  const [sortKey, setSortKey] = useState('MAE (Original Units)');
  const [sortAsc, setSortAsc] = useState(true);

  // Sorting
  const sortedMetrics = [...metrics].sort((a, b) => {
    const valA = parseFloat(a[sortKey]) || 0;
    const valB = parseFloat(b[sortKey]) || 0;
    return sortAsc ? valA - valB : valB - valA;
  });

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(true);
    }
  };

  // Find best (lowest MAE)
  const bestModel = metrics.length > 0 ? metrics.reduce((min, cur) => {
    const curMae = parseFloat(cur['MAE (Original Units)']);
    const minMae = parseFloat(min?.['MAE (Original Units)']);
    if (isNaN(curMae)) return min;
    if (isNaN(minMae)) return cur;
    return curMae < minMae ? cur : min;
  }, metrics[0]) : null;

  const linearModel = metrics.find(m => m.Model === 'Linear_Interp' || m.Model === 'Linear_Interpolation');
  const bestMae = bestModel ? parseFloat(bestModel['MAE (Original Units)']) : null;
  const linearMae = linearModel ? parseFloat(linearModel['MAE (Original Units)']) : null;
  
  const maeImprovementPercent = (linearMae !== null && bestMae !== null && linearMae > 0)
    ? Math.round(((linearMae - bestMae) / linearMae) * 100)
    : null;

  return (
    <div className="space-y-6">
      {/* Dynamic Key Findings Summary Box */}
      <Card className="bg-white dark:bg-zinc-900/90 p-5 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-xs space-y-3">
        <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-bold text-sm">
          <ProjectIcon name="sparkles" size="sm" className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <span>Dynamically Computed Research Findings</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3 bg-emerald-50/60 dark:bg-emerald-950/40 rounded-xl border border-emerald-200/60 dark:border-emerald-800/40 space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-emerald-900 dark:text-emerald-200">
              <ProjectIcon name="mae" size="sm" className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span>1. Lowest Absolute Error</span>
            </div>
            <p className="text-emerald-700 dark:text-emerald-300/80">
              {bestModel && bestMae !== null ? (
                <>
                  <strong>{bestModel.Model.replace(/_/g, ' ')}</strong> leads the benchmark with the lowest overall MAE of <strong>{bestMae.toFixed(2)} µg/m³</strong>.
                </>
              ) : (
                <span>Benchmarking results loading from backend...</span>
              )}
            </p>
          </div>
          <div className="p-3 bg-indigo-50/60 dark:bg-indigo-950/40 rounded-xl border border-indigo-200/60 dark:border-indigo-800/40 space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-indigo-900 dark:text-indigo-200">
              <ProjectIcon name="linear-interp" size="sm" className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <span>2. Baseline Superiority</span>
            </div>
            <p className="text-indigo-700 dark:text-indigo-300/80">
              {maeImprovementPercent !== null ? (
                <>
                  Reduces reconstruction error by <strong>{maeImprovementPercent}%</strong> relative to standard 1D linear temporal interpolation.
                </>
              ) : (
                <span>Evaluating baseline comparison from backend...</span>
              )}
            </p>
          </div>
          <div className="p-3 bg-slate-100/70 dark:bg-zinc-800/60 rounded-xl border border-slate-200/60 dark:border-zinc-700/60 space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-slate-900 dark:text-zinc-200">
              <ProjectIcon name="multi-pollutant" size="sm" className="w-3.5 h-3.5 text-slate-600 dark:text-zinc-400" />
              <span>3. Spatial-Temporal Gain</span>
            </div>
            <p className="text-slate-600 dark:text-zinc-400">
              Cross-pollutant 1×1 CNN channel mixing successfully infers sharp transitions where univariate models fail.
            </p>
          </div>
        </div>
      </Card>

      {/* Comparative Bar Chart Widget (Directly after findings cards) */}
      <ChartWidget
        title="Model Benchmark Comparison: MAE vs RMSE"
        subtitle="Evaluated across all test sequence hidden targets (Lower is better)"
        data={metrics}
        isDark={isDark}
        height="h-72"
        badges={[
          { label: 'Units: µg/m³', variant: 'secondary' },
          { label: 'Evaluation: Hidden Values Only', color: 'success' }
        ]}
      >
        {({ showGrid }) => (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={metrics} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />}
              <XAxis dataKey="Model" stroke={axisStroke} fontSize={11} tickLine={false} tickFormatter={(v) => v.replace(/_/g, ' ')} />
              <YAxis stroke={axisStroke} fontSize={11} tickLine={false} unit=" µg/m³" />
              <Tooltip 
                contentStyle={{
                  backgroundColor: isDark ? '#18181b' : '#ffffff',
                  borderColor: isDark ? '#27272a' : '#e2e8f0',
                  borderRadius: '12px',
                  fontSize: '12px'
                }}
              />
              <Legend />
              <Bar dataKey="MAE (Original Units)" fill="#10b981" radius={[6, 6, 0, 0]} name="MAE (µg/m³)" />
              <Bar dataKey="RMSE (Original Units)" fill="#6366f1" radius={[6, 6, 0, 0]} name="RMSE (µg/m³)" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </ChartWidget>

      {/* Benchmark Scoreboard Table (Situated below the graph) */}
      <Card className="bg-white dark:bg-zinc-900/90 p-6 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-xs hover:shadow-sm transition space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 w-full">
          <div>
            <h3 className="font-bold text-slate-900 dark:text-zinc-100 text-lg">
              Full Test-Set Benchmark Evaluation
            </h3>
            <p className="text-xs text-slate-400 dark:text-zinc-500 font-medium mt-0.5">
              Evaluated across 26,708 hidden test points under 30% artificial missingness. Evaluated strictly on hidden target positions.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Chip color="success" variant="soft" size="sm" className="font-bold text-xs">
              <Chip.Label>
                {bestModel ? `Best: ${bestModel.Model.replace(/_/g, ' ')}` : 'Loading...'}
              </Chip.Label>
            </Chip>
          </div>
        </div>

        <div className="w-full">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 dark:border-zinc-800 text-slate-400 dark:text-zinc-500 font-bold uppercase">
                  <th 
                    onClick={() => handleSort('Model')} 
                    className="py-3 px-3 cursor-pointer hover:text-slate-800 dark:hover:text-zinc-200"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>Model Architecture</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th 
                    onClick={() => handleSort('MAE (Original Units)')} 
                    className="py-3 px-3 cursor-pointer hover:text-slate-800 dark:hover:text-zinc-200"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>MAE (µg/m³)</span>
                      <InfoTooltip term="MAE" />
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th 
                    onClick={() => handleSort('RMSE (Original Units)')} 
                    className="py-3 px-3 cursor-pointer hover:text-slate-800 dark:hover:text-zinc-200"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>RMSE (µg/m³)</span>
                      <InfoTooltip term="RMSE" />
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th 
                    onClick={() => handleSort('MAPE (%)')} 
                    className="py-3 px-3 cursor-pointer hover:text-slate-800 dark:hover:text-zinc-200"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>MAPE (%)</span>
                      <InfoTooltip term="MAPE" />
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="py-3 px-3">
                    <div className="flex items-center gap-1">
                      <span>MAE (Norm)</span>
                      <InfoTooltip term="NMAE" />
                    </div>
                  </th>
                  <th className="py-3 px-3">
                    <div className="flex items-center gap-1">
                      <span>RMSE (Norm)</span>
                      <InfoTooltip term="NRMSE" />
                    </div>
                  </th>
                  <th className="py-3 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/80 font-mono">
                {sortedMetrics.map((row, idx) => {
                  const isBest = row.Model === bestModel?.Model;
                  return (
                    <tr 
                      key={row.Model || idx} 
                      className={`transition ${isBest ? 'bg-indigo-50/40 dark:bg-indigo-950/20 font-semibold' : 'hover:bg-slate-50/60 dark:hover:bg-zinc-800/40'}`}
                    >
                      <td className="py-3 px-3 text-slate-900 dark:text-zinc-100 font-sans flex items-center gap-2">
                        {isBest && <Trophy className="w-3.5 h-3.5 text-amber-500 shrink-0" />}
                        <ProjectIcon name={getModelIcon(row.Model)} size="sm" className="w-3.5 h-3.5 text-slate-500 dark:text-zinc-400 shrink-0" />
                        <span className="truncate">{row.Model.replace(/_/g, ' ')}</span>
                      </td>
                      <td className="py-3 px-3 text-emerald-600 dark:text-emerald-400 font-bold">
                        {row['MAE (Original Units)']}
                      </td>
                      <td className="py-3 px-3 text-slate-700 dark:text-zinc-300">
                        {row['RMSE (Original Units)']}
                      </td>
                      <td className="py-3 px-3 text-slate-600 dark:text-zinc-400">
                        {row['MAPE (%)'] ? `${row['MAPE (%)']}%` : '—'}
                      </td>
                      <td className="py-3 px-3 text-slate-500 dark:text-zinc-400">
                        {row['MAE (Norm)']}
                      </td>
                      <td className="py-3 px-3 text-slate-500 dark:text-zinc-400">
                        {row['RMSE (Norm)']}
                      </td>
                      <td className="py-3 px-3 font-sans">
                        {isBest ? (
                          <Chip color="success" variant="soft" size="sm" className="font-bold h-5 text-[10px]">
                            <Chip.Label>Top Performer</Chip.Label>
                          </Chip>
                        ) : (
                          <Chip color="default" variant="soft" size="sm" className="h-5 text-[10px] text-slate-400">
                            <Chip.Label>Baseline</Chip.Label>
                          </Chip>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </Card>
    </div>
  );
}
