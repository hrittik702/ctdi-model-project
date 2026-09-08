import React from 'react';
import { Card, Chip } from '@heroui/react';
import ProjectIcon from './ui/ProjectIcon';
import InfoTooltip from './ui/InfoTooltip';

/**
 * High-density Executive KPI Bar.
 * All scientific values are sourced dynamically from the backend evaluation cache.
 * Strictly avoids hardcoding any metrics.
 */
export default function KpiRow({ 
  metrics = [],
  metadata = null,
  sampleHiddenCount = null,
  totalHours = 24,
  modelStatus = 'Loading...',
  activeModel = 'CTDI Transformer',
  targetPollutant = 'PM2.5',
  isLoading = false
}) {
  // Extract real benchmark results from backend metrics table
  const transformerRow = metrics.find(m => m.Model === 'Temporal_Transformer');
  const linearRow = metrics.find(m => m.Model === 'Linear_Interpolation' || m.Model === 'Linear_Interp');

  const ctdiMae = transformerRow ? parseFloat(transformerRow['MAE (Original Units)']) : null;
  const ctdiRmse = transformerRow ? parseFloat(transformerRow['RMSE (Original Units)']) : null;
  const linearMae = linearRow ? parseFloat(linearRow['MAE (Original Units)']) : null;
  const evalPoints = metadata?.total_eval_points ?? transformerRow?.eval_points ?? null;

  // Calculate dynamic error reduction relative to linear baseline
  const maeReduction = (linearMae !== null && ctdiMae !== null && linearMae > 0)
    ? Math.round(((linearMae - ctdiMae) / linearMae) * 100)
    : null;

  const rmseReduction = (linearRow && transformerRow)
    ? Math.round(((parseFloat(linearRow['RMSE (Original Units)']) - ctdiRmse) / parseFloat(linearRow['RMSE (Original Units)'])) * 100)
    : null;

  const hiddenPercent = sampleHiddenCount !== null && totalHours > 0
    ? Math.round((sampleHiddenCount / totalHours) * 100)
    : null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3.5">
      {/* 1. CTDI Transformer MAE */}
      <Card className="bg-white dark:bg-zinc-900/90 rounded-2xl p-4 border border-slate-200/80 dark:border-zinc-800 shadow-xs hover:shadow-md transition duration-200 flex flex-col justify-between">
        {/* Header: Title + Info Tooltip on Left, Domain Icon Badge on Right */}
        <div className="flex flex-row items-center justify-between w-full mb-2">
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="text-[11px] font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider truncate">
              CTDI MAE
            </span>
            <InfoTooltip term="MAE" />
          </div>
          <div className="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0 border border-emerald-200/50 dark:border-emerald-800/50 shadow-2xs">
            <ProjectIcon name="mae" size="sm" className="w-4 h-4" />
          </div>
        </div>

        {/* Value */}
        <div className="text-2xl font-extrabold text-slate-900 dark:text-zinc-100 tracking-tight">
          {ctdiMae !== null ? (
            <>
              {ctdiMae.toFixed(2)} <span className="text-xs font-normal text-slate-400 dark:text-zinc-500 font-sans">µg/m³</span>
            </>
          ) : (
            <span className="text-base font-medium text-slate-400 font-sans">Unavailable</span>
          )}
        </div>

        {/* Subtitle / Context */}
        <div className="mt-2.5 flex items-center gap-1.5 min-w-0 text-xs">
          {maeReduction !== null ? (
            <Chip color="success" variant="soft" size="sm" className="h-5 text-[10px] dark:bg-emerald-950/60 dark:text-emerald-300 font-bold shrink-0">
              <Chip.Label>↓ {maeReduction}%</Chip.Label>
            </Chip>
          ) : null}
          <span className="text-[10px] text-slate-400 dark:text-zinc-500 truncate">
            Hidden values only
          </span>
        </div>
      </Card>

      {/* 2. CTDI Transformer RMSE */}
      <Card className="bg-white dark:bg-zinc-900/90 rounded-2xl p-4 border border-slate-200/80 dark:border-zinc-800 shadow-xs hover:shadow-md transition duration-200 flex flex-col justify-between">
        <div className="flex flex-row items-center justify-between w-full mb-2">
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="text-[11px] font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider truncate">
              CTDI RMSE
            </span>
            <InfoTooltip term="RMSE" />
          </div>
          <div className="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0 border border-emerald-200/50 dark:border-emerald-800/50 shadow-2xs">
            <ProjectIcon name="rmse" size="sm" className="w-4 h-4" />
          </div>
        </div>

        <div className="text-2xl font-extrabold text-slate-900 dark:text-zinc-100 tracking-tight">
          {ctdiRmse !== null ? (
            <>
              {ctdiRmse.toFixed(2)} <span className="text-xs font-normal text-slate-400 dark:text-zinc-500 font-sans">µg/m³</span>
            </>
          ) : (
            <span className="text-base font-medium text-slate-400 font-sans">Unavailable</span>
          )}
        </div>

        <div className="mt-2.5 flex items-center gap-1.5 min-w-0 text-xs">
          {rmseReduction !== null ? (
            <Chip color="success" variant="soft" size="sm" className="h-5 text-[10px] dark:bg-emerald-950/60 dark:text-emerald-300 font-bold shrink-0">
              <Chip.Label>↓ {rmseReduction}%</Chip.Label>
            </Chip>
          ) : null}
          <span className="text-[10px] text-slate-400 dark:text-zinc-500 truncate">
            vs Linear baseline
          </span>
        </div>
      </Card>

      {/* 3. Linear Baseline MAE */}
      <Card className="bg-white dark:bg-zinc-900/90 rounded-2xl p-4 border border-slate-200/80 dark:border-zinc-800 shadow-xs hover:shadow-md transition duration-200 flex flex-col justify-between">
        <div className="flex flex-row items-center justify-between w-full mb-2">
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="text-[11px] font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider truncate">
              Linear MAE
            </span>
            <InfoTooltip term="Linear Interpolation" />
          </div>
          <div className="w-8 h-8 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center shrink-0 border border-amber-200/50 dark:border-amber-800/50 shadow-2xs">
            <ProjectIcon name="linear-interp" size="sm" className="w-4 h-4" />
          </div>
        </div>

        <div className="text-2xl font-extrabold text-slate-900 dark:text-zinc-100 tracking-tight">
          {linearMae !== null ? (
            <>
              {linearMae.toFixed(2)} <span className="text-xs font-normal text-slate-400 dark:text-zinc-500 font-sans">µg/m³</span>
            </>
          ) : (
            <span className="text-base font-medium text-slate-400 font-sans">Unavailable</span>
          )}
        </div>

        <div className="mt-2.5 text-xs">
          <span className="text-[10px] text-slate-400 dark:text-zinc-500 truncate block">
            1D Temporal Interpolation
          </span>
        </div>
      </Card>

      {/* 4. Evaluation Points */}
      <Card className="bg-white dark:bg-zinc-900/90 rounded-2xl p-4 border border-slate-200/80 dark:border-zinc-800 shadow-xs hover:shadow-md transition duration-200 flex flex-col justify-between">
        <div className="flex flex-row items-center justify-between w-full mb-2">
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="text-[11px] font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider truncate">
              Eval Test Points
            </span>
            <InfoTooltip term="Evaluation Points" />
          </div>
          <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0 border border-indigo-200/50 dark:border-indigo-800/50 shadow-2xs">
            <ProjectIcon name="layers" size="sm" className="w-4 h-4" />
          </div>
        </div>

        <div className="text-2xl font-extrabold text-slate-900 dark:text-zinc-100 tracking-tight font-mono">
          {evalPoints !== null ? (
            evalPoints.toLocaleString()
          ) : (
            <span className="text-base font-medium text-slate-400 font-sans">Unavailable</span>
          )}
        </div>

        <div className="mt-2.5 text-xs">
          <span className="text-[10px] text-slate-400 dark:text-zinc-500 truncate block">
            {metadata?.missing_rate_percent ? `${metadata.missing_rate_percent}% Artificial Mask` : 'Evaluation mask'}
          </span>
        </div>
      </Card>

      {/* 5. Sequence Missingness */}
      <Card className="bg-white dark:bg-zinc-900/90 rounded-2xl p-4 border border-slate-200/80 dark:border-zinc-800 shadow-xs hover:shadow-md transition duration-200 flex flex-col justify-between">
        <div className="flex flex-row items-center justify-between w-full mb-2">
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="text-[11px] font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider truncate">
              Sample Masked
            </span>
            <InfoTooltip term="Hidden Target" />
          </div>
          <div className="w-8 h-8 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 flex items-center justify-center shrink-0 border border-rose-200/50 dark:border-rose-800/50 shadow-2xs">
            <ProjectIcon name="hidden-target" size="sm" className="w-4 h-4" />
          </div>
        </div>

        <div className="text-2xl font-extrabold text-slate-900 dark:text-zinc-100 tracking-tight font-mono">
          {sampleHiddenCount !== null ? (
            `${sampleHiddenCount} / ${totalHours}h`
          ) : (
            <span className="text-base font-medium text-slate-400 font-sans">Unavailable</span>
          )}
        </div>

        <div className="mt-2.5 text-xs">
          <span className="text-[10px] text-slate-400 dark:text-zinc-500 font-mono truncate block">
            {hiddenPercent !== null ? `${hiddenPercent}% hidden target` : '24h sequence'}
          </span>
        </div>
      </Card>

      {/* 6. Active Model Status */}
      <Card className="bg-white dark:bg-zinc-900/90 rounded-2xl p-4 border border-slate-200/80 dark:border-zinc-800 shadow-xs hover:shadow-md transition duration-200 flex flex-col justify-between">
        <div className="flex flex-row items-center justify-between w-full mb-2">
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="text-[11px] font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider truncate">
              Model Status
            </span>
            <InfoTooltip term="CTDI" />
          </div>
          <div className="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0 border border-emerald-200/50 dark:border-emerald-800/50 shadow-2xs">
            <ProjectIcon name="cpu" size="sm" className="w-4 h-4" />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${modelStatus === 'Ready' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
          <span className="text-2xl font-extrabold text-slate-900 dark:text-zinc-100 tracking-tight truncate">
            {modelStatus}
          </span>
        </div>

        <div className="mt-2.5 text-xs">
          <span className="text-[10px] text-slate-400 dark:text-zinc-500 truncate block">
            {activeModel}
          </span>
        </div>
      </Card>
    </div>
  );
}
