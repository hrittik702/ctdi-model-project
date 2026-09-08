import React from 'react';

export default function GlassmorphicTooltip({ active, payload, label, isDark }) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0].payload;

  return (
    <div className="bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md border border-slate-200/90 dark:border-zinc-800 shadow-xl p-4 rounded-2xl text-xs space-y-2 min-w-[210px]">
      {/* Header with Timestamp */}
      <div className="border-b border-slate-100 dark:border-zinc-800 pb-2 flex items-center justify-between">
        <span className="font-bold text-slate-900 dark:text-zinc-100 text-sm">{label}</span>
        <span className="text-slate-400 dark:text-zinc-500 font-mono text-[11px]">{d.timestamp || ''}</span>
      </div>

      {/* Series Items */}
      <div className="space-y-1.5 pt-0.5">
        {d.actual !== null && d.actual !== undefined && (
          <div className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-slate-600 dark:text-zinc-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-slate-900 dark:bg-zinc-200" />
              Ground Truth
            </span>
            <strong className="text-slate-900 dark:text-zinc-100 font-bold">{d.actual} µg/m³</strong>
          </div>
        )}

        {d.transformer !== null && d.transformer !== undefined && (
          <div className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              CTDI Transformer
            </span>
            <strong className="text-emerald-600 dark:text-emerald-400 font-bold">{d.transformer} µg/m³</strong>
          </div>
        )}

        {d.linear !== null && d.linear !== undefined && (
          <div className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              Linear Interp
            </span>
            <strong className="text-amber-600 dark:text-amber-400 font-semibold">{d.linear} µg/m³</strong>
          </div>
        )}

        {d.knn !== null && d.knn !== undefined && (
          <div className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-purple-600 dark:text-purple-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-purple-500" />
              KNN
            </span>
            <strong className="text-purple-600 dark:text-purple-400 font-semibold">{d.knn} µg/m³</strong>
          </div>
        )}

        {d.mlp !== null && d.mlp !== undefined && (
          <div className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-cyan-600 dark:text-cyan-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-cyan-500" />
              MLP
            </span>
            <strong className="text-cyan-600 dark:text-cyan-400 font-semibold">{d.mlp} µg/m³</strong>
          </div>
        )}

        {/* Observation Status Badges */}
        {d.hiddenTarget !== null && d.hiddenTarget !== undefined && (
          <div className="pt-1.5 border-t border-slate-100 dark:border-zinc-800 flex items-center justify-between text-[11px]">
            <span className="text-red-500 font-semibold flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full border border-red-500" />
              Evaluation Point
            </span>
            <span className="text-red-600 dark:text-red-400 font-mono">Artificially Masked</span>
          </div>
        )}

        {d.observed !== null && d.observed !== undefined && (
          <div className="pt-1.5 border-t border-slate-100 dark:border-zinc-800 flex items-center justify-between text-[11px]">
            <span className="text-blue-500 font-semibold flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              Observed Point
            </span>
            <span className="text-blue-600 dark:text-blue-400 font-mono">Conditioning Feature</span>
          </div>
        )}
      </div>
    </div>
  );
}
