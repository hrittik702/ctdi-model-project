import React from 'react';
import { Chip } from '@heroui/react';
import InfoTooltip from './ui/InfoTooltip';

export default function MissingnessBar({
  observedMask = [],
  evalMask = [],
  hours = []
}) {
  const total = hours.length || 24;
  let observedCount = 0;
  let hiddenCount = 0;
  let naturalMissingCount = 0;

  for (let i = 0; i < total; i++) {
    if (evalMask[i] === 1) {
      hiddenCount++;
    } else if (observedMask[i] === 1) {
      observedCount++;
    } else {
      naturalMissingCount++;
    }
  }

  const hiddenRate = Math.round((hiddenCount / total) * 100);
  const observedRate = Math.round((observedCount / total) * 100);

  return (
    <div className="bg-slate-50 dark:bg-zinc-800/40 p-3.5 rounded-2xl border border-slate-200/60 dark:border-zinc-800 space-y-2.5">
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-2">
          <span className="font-bold text-slate-700 dark:text-zinc-300">24-Hour Observation Distribution:</span>
          <span className="text-slate-400 dark:text-zinc-500 font-mono text-[11px]">
            {observedCount} Observed • {hiddenCount} Hidden Target • {naturalMissingCount} Natural NaN
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <Chip color="success" variant="soft" size="sm" className="h-5 text-[10px] font-semibold dark:bg-emerald-950/40 dark:text-emerald-300">
            <Chip.Label>{observedRate}% Conditioned</Chip.Label>
          </Chip>
          <Chip color="danger" variant="soft" size="sm" className="h-5 text-[10px] font-semibold dark:bg-red-950/40 dark:text-red-300">
            <Chip.Label>{hiddenRate}% Evaluated</Chip.Label>
          </Chip>
        </div>
      </div>

      {/* Segmented Timeline Bar */}
      <div className="flex items-center gap-1 w-full h-3.5 rounded-lg overflow-hidden bg-slate-200/70 dark:bg-zinc-700/60 p-0.5">
        {Array.from({ length: total }).map((_, idx) => {
          const isEval = evalMask[idx] === 1;
          const isObs = observedMask[idx] === 1 && !isEval;
          
          let color = 'bg-slate-300 dark:bg-zinc-600'; // natural NaN
          let title = `Hour ${idx}:00 - Naturally Missing`;

          if (isEval) {
            color = 'bg-red-500';
            title = `Hour ${idx}:00 - Artificially Hidden (Evaluation Target)`;
          } else if (isObs) {
            color = 'bg-blue-600';
            title = `Hour ${idx}:00 - Observed (Model Feature)`;
          }

          return (
            <div
              key={idx}
              className={`flex-1 h-full rounded-xs transition hover:opacity-80 cursor-help ${color}`}
              title={title}
            />
          );
        })}
      </div>

      {/* Legend markers */}
      <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-zinc-400 pt-0.5">
        <span className="font-mono text-[10px]">Hour 00:00</span>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-xs bg-blue-600 shrink-0" />
            <span>Observed (Given)</span>
            <InfoTooltip term="Observed Points" />
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-xs bg-red-500 shrink-0" />
            <span>Artificially Hidden (Target)</span>
            <InfoTooltip term="Hidden Target" />
          </div>
          {naturalMissingCount > 0 && (
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-xs bg-slate-300 dark:bg-zinc-600 shrink-0" />
              <span>Natural NaN</span>
            </span>
          )}
        </div>
        <span className="font-mono text-[10px]">Hour 23:00</span>
      </div>
    </div>
  );
}
