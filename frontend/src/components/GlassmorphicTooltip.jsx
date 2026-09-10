import React from 'react';

export default function GlassmorphicTooltip({ active, payload, label, isDark }) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0].payload;

  return (
    <div className="bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md border border-slate-200/90 dark:border-zinc-800 shadow-xl p-4 rounded-2xl text-xs space-y-2 min-w-[250px]">
      {/* Header with Timestamp & Step Offset */}
      <div className="border-b border-slate-100 dark:border-zinc-800 pb-2 flex items-center justify-between gap-3">
        <div className="flex items-baseline gap-1.5">
          <span className="font-extrabold text-slate-900 dark:text-zinc-100 text-sm font-mono">{label}</span>
          {d.stepOffset && (
            <span className="text-[10px] font-mono text-indigo-600 dark:text-indigo-400 font-bold bg-indigo-50 dark:bg-indigo-950/80 px-1 py-0.2 rounded border border-indigo-200/60 dark:border-indigo-800/60">
              {d.stepOffset}
            </span>
          )}
        </div>
        <span className="text-slate-400 dark:text-zinc-500 font-mono text-[11px] font-medium">
          {d.date || (d.timestamp && d.timestamp.includes(' ') ? d.timestamp.split(' ')[0] : d.timestamp) || ''}
        </span>
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

        {/* Observation Status & Dynamic Error Diagnosis */}
        {d.hiddenTarget !== null && d.hiddenTarget !== undefined && (() => {
          const actual = d.actual;
          const pred = d.transformer;
          const hasError = actual !== null && actual !== undefined && pred !== null && pred !== undefined;
          const err = hasError ? Math.abs(pred - actual) : null;
          const pctErr = (hasError && actual > 0) ? (err / actual) * 100 : null;

          return (
            <div className="pt-2 border-t border-slate-100 dark:border-zinc-800 space-y-1.5">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-500 dark:text-zinc-400 font-semibold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                  Hidden Target
                </span>
                <span className="text-red-500 font-mono text-[10px] font-bold">Artificially Masked</span>
              </div>

              {err !== null && (
                <div className="p-2 rounded-xl bg-slate-50 dark:bg-zinc-800/80 border border-slate-200/70 dark:border-zinc-700/60 space-y-1">
                  <div className="flex items-center justify-between text-[10px] uppercase font-bold text-slate-400 dark:text-zinc-400">
                    <span>Reconstruction Error (Δ)</span>
                    <span className={`px-1.5 py-0.2 rounded font-extrabold ${
                      err < 5 
                        ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300' 
                        : err < 15 
                        ? 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300' 
                        : 'bg-red-100 dark:bg-red-950 text-red-600 dark:text-red-300'
                    }`}>
                      {err < 5 ? 'Minimal Error' : err < 15 ? 'Moderate Drift' : 'High Deviation'}
                    </span>
                  </div>
                  <div className="flex items-baseline justify-between">
                    <span className="font-mono font-extrabold text-sm text-slate-900 dark:text-zinc-100">
                      {err.toFixed(2)} µg/m³
                    </span>
                    {pctErr !== null && (
                      <span className="text-[11px] font-mono text-slate-500 dark:text-zinc-400">
                        ({pctErr.toFixed(1)}% error)
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })()}

        {d.observed !== null && d.observed !== undefined && (
          <div className="pt-1.5 border-t border-slate-100 dark:border-zinc-800 flex items-center justify-between gap-3 text-[11px]">
            <span className="text-blue-500 font-semibold flex items-center gap-1.5 shrink-0">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              Observed Point
            </span>
            <span className="text-blue-600 dark:text-blue-400 font-mono text-[10px] truncate">
              Conditioning Input
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
