import React from 'react';
import { Card, Chip } from '@heroui/react';
import { History, Download, ExternalLink, CheckCircle2, ShieldCheck } from 'lucide-react';

export default function ExperimentHistoryView({ experiments = [] }) {
  return (
    <div className="space-y-6">
      <Card className="bg-white dark:bg-zinc-900/90 p-6 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-zinc-800 pb-3">
          <div>
            <div className="flex items-center gap-2">
              <History className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <h3 className="font-bold text-slate-900 dark:text-zinc-100 text-base">
                Experiment & Evaluation History
              </h3>
            </div>
            <p className="text-xs text-slate-400 dark:text-zinc-500 mt-0.5">
              Archived evaluation runs over Beijing Multi-Site Air Quality test distribution. Sourced from backend experiment logs.
            </p>
          </div>

          <Chip color="accent" variant="soft" size="sm" className="bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 font-bold">
            <Chip.Label>{experiments.length} Runs Recorded</Chip.Label>
          </Chip>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-zinc-800 text-slate-400 dark:text-zinc-500 font-bold uppercase">
                <th className="py-2.5 px-3">Run ID</th>
                <th className="py-2.5 px-3">Experiment Description</th>
                <th className="py-2.5 px-3">Model Architecture</th>
                <th className="py-2.5 px-3">Evaluation Mask</th>
                <th className="py-2.5 px-3">MAE (µg/m³)</th>
                <th className="py-2.5 px-3">RMSE (µg/m³)</th>
                <th className="py-2.5 px-3">Device</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/80 font-mono">
              {experiments.length > 0 ? (
                experiments.map(exp => (
                  <tr key={exp.id} className="hover:bg-slate-50/60 dark:hover:bg-zinc-800/40">
                    <td className="py-3 px-3 font-bold text-indigo-600 dark:text-indigo-400 font-sans">
                      {exp.id}
                    </td>
                    <td className="py-3 px-3 text-slate-800 dark:text-zinc-200 font-sans max-w-xs truncate">
                      {exp.title}
                    </td>
                    <td className="py-3 px-3 text-slate-600 dark:text-zinc-400">
                      {exp.model.replace(/_/g, ' ')}
                    </td>
                    <td className="py-3 px-3 text-slate-500 dark:text-zinc-400">
                      {exp.mask_rate || '30% Random'}
                    </td>
                    <td className="py-3 px-3 text-emerald-600 dark:text-emerald-400 font-bold">
                      {exp.mae}
                    </td>
                    <td className="py-3 px-3 text-slate-700 dark:text-zinc-300">
                      {exp.rmse}
                    </td>
                    <td className="py-3 px-3 text-slate-400">
                      {exp.device || 'CPU'}
                    </td>
                    <td className="py-3 px-3 font-sans">
                      <Chip color="success" variant="soft" size="sm" className="h-5 text-[10px] font-bold">
                        <Chip.Label>{exp.status}</Chip.Label>
                      </Chip>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-6 text-center text-slate-400 font-sans">
                    No experiment logs loaded from backend.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
