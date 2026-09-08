import React from 'react';
import { Card, Chip, Button } from '@heroui/react';
import { ExternalLink, TrendingDown, Layers } from 'lucide-react';
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

export default function MultiPollutantView({
  sampleData,
  pollutants = [],
  sampleIdx,
  onDrillDown,
  isDark = false,
  gridStroke,
  axisStroke
}) {
  return (
    <div className="space-y-5">
      {/* Section Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="font-extrabold text-slate-900 dark:text-zinc-100 text-base sm:text-lg tracking-tight">
            Synchronized 6-Pollutant Concentration Grid
          </h3>
          <p className="text-xs text-slate-400 dark:text-zinc-500 font-medium">
            Simultaneous multivariate sequence reconstruction over 24-hour test window #{sampleIdx}.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-zinc-400 font-medium">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-900 dark:bg-zinc-200" /> Ground Truth
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> CTDI Transformer
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Linear Baseline
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full border border-red-500" /> Hidden Target
          </span>
        </div>
      </div>

      {/* 3x2 Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {pollutants.map(pol => {
          const polData = sampleData?.pollutants?.[pol];
          const gridChartData = sampleData?.hours?.map((hour, i) => ({
            hour,
            timestamp: sampleData?.timestamps?.[i],
            actual: polData?.actual?.[i],
            transformer: polData?.transformer?.[i],
            linear: polData?.linear?.[i],
            hidden: polData?.eval_mask?.[i] === 1 ? polData?.actual?.[i] : null
          })) || [];

          const tfMae = polData?.sample_mae?.transformer ?? null;

          return (
            <ChartWidget
              key={pol}
              title={pol}
              subtitle={`Sample #${sampleIdx} • 24h Window`}
              data={gridChartData}
              sampleIdx={sampleIdx}
              pollutant={pol}
              isDark={isDark}
              height="h-52"
              badges={[
                { 
                  label: tfMae !== null ? `MAE: ${tfMae.toFixed(2)}` : 'MAE: N/A', 
                  color: 'success' 
                }
              ]}
            >
              {({ showGrid }) => (
                <div className="flex flex-col h-full justify-between">
                  <div className="h-44 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={gridChartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />}
                        <XAxis dataKey="hour" tick={false} axisLine={false} />
                        <YAxis stroke={axisStroke} fontSize={10} tickLine={false} />
                        <Tooltip content={<GlassmorphicTooltip isDark={isDark} />} />
                        <Line type="monotone" dataKey="actual" stroke={isDark ? '#e4e4e7' : '#1e293b'} strokeWidth={1.5} dot={false} />
                        <Line type="monotone" dataKey="linear" stroke="#f59e0b" strokeWidth={1.2} strokeDasharray="3 3" dot={false} />
                        <Line type="monotone" dataKey="transformer" stroke="#10b981" strokeWidth={2.2} dot={false} />
                        <Line type="monotone" dataKey="hidden" stroke="transparent" dot={{ stroke: '#ef4444', strokeWidth: 1.5, fill: 'transparent', r: 4 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Drill-down action bar */}
                  <div className="pt-2 border-t border-slate-100 dark:border-zinc-800 flex items-center justify-between text-xs">
                    <span className="text-slate-400 dark:text-zinc-500 font-mono text-[11px]">
                      {polData?.hidden_count !== undefined ? `Hidden: ${polData.hidden_count} / 24 hrs` : 'Hidden: N/A'}
                    </span>
                    <button
                      type="button"
                      onClick={() => onDrillDown(pol)}
                      className="flex items-center gap-1 font-bold text-indigo-600 dark:text-indigo-400 hover:underline cursor-pointer"
                    >
                      <span>Explore Curve</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              )}
            </ChartWidget>
          );
        })}
      </div>
    </div>
  );
}
