import React from 'react';

export default function GlassmorphicTooltip({ active, payload, label, isDark, unit = 'µg/m³' }) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0].payload;
  const channelUnit = d.unit || unit || 'µg/m³';
  const channelName = d.pollutantName || 'Value';

  const isObserved = d.observed !== null && d.observed !== undefined;
  const isNaturalMissing = d.isNaturalMissing || (d.observed === null && d.hiddenTarget === null);
  const isHiddenTarget = d.hiddenTarget !== null && d.hiddenTarget !== undefined;

  return (
    <div className="bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md border border-slate-200/90 dark:border-zinc-800 shadow-xl p-3.5 rounded-2xl text-xs space-y-2 min-w-[240px] max-w-xs motion-fade-enter">
      {/* Header with Timestamp & Step Offset */}
      <div className="border-b border-slate-100 dark:border-zinc-800 pb-2 flex items-center justify-between gap-3">
        <div className="flex items-baseline gap-1.5">
          <span className="font-extrabold text-slate-900 dark:text-zinc-100 text-sm font-mono">
            {label}
          </span>
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

      {/* Primary Channel Measurement Status */}
      <div className="space-y-1.5 pt-0.5">
        {isObserved ? (
          <div className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-slate-700 dark:text-zinc-300 font-medium">
              <span className="w-2 h-2 rounded-full bg-blue-500 shrink-0" />
              <span>{channelName}</span>
            </span>
            <strong className="text-slate-900 dark:text-zinc-100 font-extrabold font-mono text-[13px]">
              {d.observed} {channelUnit}
            </strong>
          </div>
        ) : isNaturalMissing ? (
          <div className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-slate-500 dark:text-zinc-400 font-medium">
              <span className="w-2 h-2 rounded-full border border-slate-400 dark:border-zinc-500 bg-transparent shrink-0" />
              <span>{channelName}</span>
            </span>
            <span className="text-amber-600 dark:text-amber-400 font-semibold font-mono text-[11px]">
              Natural Missing (NaN)
            </span>
          </div>
        ) : null}

        {/* Model Imputations (Only rendered if model output exists) */}
        {d.transformer !== null && d.transformer !== undefined && (
          <div className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
              <span>CTDI Transformer</span>
            </span>
            <strong className="text-emerald-600 dark:text-emerald-400 font-bold font-mono">
              {d.transformer} {channelUnit}
            </strong>
          </div>
        )}

        {d.linear !== null && d.linear !== undefined && (
          <div className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-amber-500 shrink-0" />
              <span>Linear Interp</span>
            </span>
            <strong className="text-amber-600 dark:text-amber-400 font-semibold font-mono">
              {d.linear} {channelUnit}
            </strong>
          </div>
        )}

        {d.knn !== null && d.knn !== undefined && (
          <div className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-purple-600 dark:text-purple-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-purple-500 shrink-0" />
              <span>KNN Baseline</span>
            </span>
            <strong className="text-purple-600 dark:text-purple-400 font-semibold font-mono">
              {d.knn} {channelUnit}
            </strong>
          </div>
        )}

        {d.mlp !== null && d.mlp !== undefined && (
          <div className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-cyan-600 dark:text-cyan-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-cyan-500 shrink-0" />
              <span>MLP Baseline</span>
            </span>
            <strong className="text-cyan-600 dark:text-cyan-400 font-semibold font-mono">
              {d.mlp} {channelUnit}
            </strong>
          </div>
        )}

        {/* Observation Status Footer Pill */}
        <div className="pt-2 border-t border-slate-100 dark:border-zinc-800 flex items-center justify-between gap-2 text-[10px]">
          <span className="text-slate-400 dark:text-zinc-500">
            Observation Status:
          </span>
          <span className={`font-semibold px-2 py-0.5 rounded-full ${
            isObserved 
              ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300' 
              : 'bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300'
          }`}>
            {isObserved ? 'Observed Measurement' : 'Unobserved / Natural Dropout'}
          </span>
        </div>
      </div>
    </div>
  );
}
