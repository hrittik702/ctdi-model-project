import React, { useState } from 'react';
import { Card, Chip, Button } from '@heroui/react';
import { Search, Download, Database, Filter } from 'lucide-react';

export default function DataExplorerView({
  sampleData,
  sampleIdx,
  pollutants = []
}) {
  const [filterMode, setFilterMode] = useState('all'); // all, observed, hidden

  const hours = sampleData?.hours || Array.from({ length: 24 }, (_, i) => i);
  const timestamps = sampleData?.timestamps || [];

  // Build rows
  const rows = hours.map((hour, idx) => {
    const row = {
      hour,
      timestamp: timestamps[idx] || `Hour ${hour}:00`,
      values: {},
      isEval: false,
      isObs: false
    };

    pollutants.forEach(p => {
      const polObj = sampleData?.pollutants?.[p];
      const val = polObj?.actual?.[idx];
      row.values[p] = val !== null && val !== undefined ? val : 'NaN';
      if (polObj?.eval_mask?.[idx] === 1) row.isEval = true;
      if (polObj?.observed_mask?.[idx] === 1) row.isObs = true;
    });

    return row;
  });

  const filteredRows = rows.filter(r => {
    if (filterMode === 'observed') return r.isObs;
    if (filterMode === 'hidden') return r.isEval;
    return true;
  });

  const handleExportCSV = () => {
    const headers = ['Hour', 'Timestamp', ...pollutants, 'Evaluation_Status'];
    const csvRows = rows.map(r => [
      r.hour,
      r.timestamp,
      ...pollutants.map(p => r.values[p]),
      r.isEval ? 'Artificially_Hidden_Target' : (r.isObs ? 'Observed' : 'Natural_NaN')
    ].join(','));

    const content = 'data:text/csv;charset=utf-8,' + encodeURIComponent([headers.join(','), ...csvRows].join('\n'));
    const a = document.createElement('a');
    a.href = content;
    a.download = `Station_Aotizhongxin_Sample_${sampleIdx}_24h_telemetry.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="space-y-6">
      <Card className="bg-white dark:bg-zinc-900/90 p-6 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 dark:border-zinc-800 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <h3 className="font-bold text-slate-900 dark:text-zinc-100 text-base">
                24-Hour Raw Sequence Telemetry (Sample #{sampleIdx})
              </h3>
            </div>
            <p className="text-xs text-slate-400 dark:text-zinc-500 mt-0.5">
              Inspect exact hourly observations and artificial masking across all 6 monitoring channels.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Filter pills */}
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-zinc-800 p-1 rounded-xl text-xs">
              <button
                type="button"
                onClick={() => setFilterMode('all')}
                className={`px-2.5 py-1 rounded-lg font-semibold transition cursor-pointer ${
                  filterMode === 'all'
                    ? 'bg-white dark:bg-zinc-700 text-slate-900 dark:text-zinc-100 shadow-2xs'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                All (24h)
              </button>
              <button
                type="button"
                onClick={() => setFilterMode('observed')}
                className={`px-2.5 py-1 rounded-lg font-semibold transition cursor-pointer ${
                  filterMode === 'observed'
                    ? 'bg-white dark:bg-zinc-700 text-blue-600 dark:text-blue-400 shadow-2xs'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Observed
              </button>
              <button
                type="button"
                onClick={() => setFilterMode('hidden')}
                className={`px-2.5 py-1 rounded-lg font-semibold transition cursor-pointer ${
                  filterMode === 'hidden'
                    ? 'bg-white dark:bg-zinc-700 text-red-600 dark:text-red-400 shadow-2xs'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Hidden Target
              </button>
            </div>

            {/* Export button */}
            <Button
              size="sm"
              variant="secondary"
              onPress={handleExportCSV}
              className="flex items-center gap-1.5 text-xs font-semibold cursor-pointer dark:bg-zinc-800 dark:text-zinc-200"
            >
              <Download className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <span>Export CSV</span>
            </Button>
          </div>
        </div>

        {/* Telemetry Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-zinc-800 text-slate-400 dark:text-zinc-500 font-bold uppercase">
                <th className="py-2.5 px-3">Hour</th>
                <th className="py-2.5 px-3">Timestamp</th>
                {pollutants.map(p => (
                  <th key={p} className="py-2.5 px-3">{p} (µg/m³)</th>
                ))}
                <th className="py-2.5 px-3">Conditioning Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/80 font-mono">
              {filteredRows.map(r => (
                <tr key={r.hour} className="hover:bg-slate-50/70 dark:hover:bg-zinc-800/50 transition">
                  <td className="py-2.5 px-3 font-bold text-slate-900 dark:text-zinc-100">
                    {r.hour.toString().padStart(2, '0')}:00
                  </td>
                  <td className="py-2.5 px-3 text-slate-500 dark:text-zinc-400">
                    {r.timestamp}
                  </td>
                  {pollutants.map(p => (
                    <td key={p} className="py-2.5 px-3 text-slate-800 dark:text-zinc-200">
                      {r.values[p]}
                    </td>
                  ))}
                  <td className="py-2.5 px-3">
                    {r.isEval ? (
                      <Chip color="danger" variant="soft" size="sm" className="h-5 text-[10px] font-bold">
                        <Chip.Label>Hidden Target</Chip.Label>
                      </Chip>
                    ) : r.isObs ? (
                      <Chip color="success" variant="soft" size="sm" className="h-5 text-[10px]">
                        <Chip.Label>Observed</Chip.Label>
                      </Chip>
                    ) : (
                      <Chip variant="secondary" size="sm" className="h-5 text-[10px] text-slate-400">
                        <Chip.Label>Natural NaN</Chip.Label>
                      </Chip>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="pt-2 text-[11px] text-slate-400 dark:text-zinc-500 flex items-center justify-between border-t border-slate-100 dark:border-zinc-800">
          <span>Displaying {filteredRows.length} of 24 hourly sequence intervals</span>
          <span>Station Aotizhongxin • Telemetry Feed</span>
        </div>
      </Card>
    </div>
  );
}
