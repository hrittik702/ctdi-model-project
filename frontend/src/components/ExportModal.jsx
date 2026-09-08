import React, { useState } from 'react';
import { X, Download, FileSpreadsheet, FileCode, Check, Camera, Layers, CheckCircle2 } from 'lucide-react';
import { Button, Chip } from '@heroui/react';

export default function ExportModal({
  isOpen,
  onClose,
  sampleIdx = 0,
  targetPollutant = 'PM2.5',
  station = 'Aotizhongxin',
  dataset = 'Beijing Multi-Site Air Quality Dataset',
  chartData = [],
  metrics = []
}) {
  const [exportFormat, setExportFormat] = useState('png');
  const [includeMetadata, setIncludeMetadata] = useState(true);
  const [includeLegend, setIncludeLegend] = useState(true);
  const [includeMetrics, setIncludeMetrics] = useState(true);
  const [includeExplanation, setIncludeExplanation] = useState(true);
  const [includeEvaluationScope, setIncludeEvaluationScope] = useState(true);

  if (!isOpen) return null;

  const handleExecuteExport = () => {
    if (exportFormat === 'csv') {
      if (!chartData || chartData.length === 0) return;
      const headers = ['hour', 'timestamp', 'actual', 'observed', 'hiddenTarget', 'transformer', 'linear', 'knn', 'mlp'];

      const rows = chartData.map(item =>
        headers.map(h => item[h] === null || item[h] === undefined ? '' : item[h]).join(',')
      );

      let content = '';
      if (includeMetadata) {
        content += `# CTDI Air Imputation Studio Analysis Export\n`;
        content += `# Dataset: ${dataset}\n`;
        content += `# Station: ${station}, Pollutant: ${targetPollutant}, Sample: #${sampleIdx}\n`;
        content += `# Evaluation Scope: Hidden values only (artificially masked evaluation)\n`;
        content += `# Export Date: ${new Date().toISOString()}\n`;
      }
      content += headers.join(',') + '\n' + rows.join('\n');

      const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `CTDI_Analysis_Sample_${sampleIdx}_${targetPollutant}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } else if (exportFormat === 'json') {
      const payload = {
        project: "CTDI Air Imputation Studio",
        title: `24-Hour ${targetPollutant} Concentration Analysis`,
        metadata: includeMetadata ? {
          dataset,
          station,
          pollutant: targetPollutant,
          sampleIdx,
          evaluationScope: "hidden_values_only",
          exportedAt: new Date().toISOString()
        } : undefined,
        metricsSummary: includeMetrics ? metrics : undefined,
        trajectoryData: chartData,
        interpretation: includeExplanation ? {
          ground_truth: "Original measured concentration used for evaluation reference",
          observed_points: "Values available to the model during reconstruction",
          hidden_target: "Artificially masked points to evaluate imputation accuracy",
          ctdi_transformer: "Spatial-temporal reconstruction via 1x1 CNN and Temporal Transformer",
          linear_baseline: "1D temporal linear interpolation"
        } : undefined
      };
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `CTDI_Analysis_Sample_${sampleIdx}_${targetPollutant}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } else if (exportFormat === 'png' || exportFormat === 'svg') {
      // Trigger figure export via page ChartWidget
      const exportBtn = document.querySelector('button[title="Export Research-Grade Figure"]');
      if (exportBtn) {
        exportBtn.click();
      }
    }
    onClose();
  };

  const formats = [
    {
      id: 'png',
      name: 'PNG',
      icon: Camera,
      title: 'High-Resolution Figure',
      desc: 'Complete research-ready graphic with chart, legend, metrics, and interpretation.'
    },
    {
      id: 'csv',
      name: 'CSV',
      icon: FileSpreadsheet,
      title: 'Telemetry & Imputations',
      desc: 'Tabular time-series data with ground-truth, observed, and reconstructed curves.'
    },
    {
      id: 'json',
      name: 'JSON',
      icon: FileCode,
      title: 'Complete Structured Analysis',
      desc: 'Full hierarchical schema including dataset metadata, model provenance, and metrics.'
    }
  ];

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 select-none"
      style={{
        backgroundColor: 'rgba(0, 0, 0, 0.55)',
        backdropFilter: 'blur(8px)'
      }}
    >
      <div className="bg-white dark:bg-zinc-900 w-full max-w-lg rounded-3xl border border-slate-200/90 dark:border-zinc-800 shadow-2xl overflow-hidden p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-zinc-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 rounded-xl">
              <Download className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 dark:text-zinc-100 text-base">
                Export Analysis
              </h3>
              <p className="text-xs text-slate-400 dark:text-zinc-500">
                Export the current analytical view with data, metrics, and interpretation.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close export dialog"
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-zinc-800 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Format Selection Cards */}
        <div className="space-y-2">
          <label className="text-[11px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider">
            Select Export Format
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            {formats.map(f => {
              const Icon = f.icon;
              const isSelected = exportFormat === f.id;
              return (
                <button
                  key={f.id}
                  type="button"
                  onClick={() => setExportFormat(f.id)}
                  className={`p-3 rounded-2xl border text-left transition cursor-pointer flex flex-col justify-between ${
                    isSelected
                      ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/40 text-indigo-900 dark:text-indigo-200 shadow-xs'
                      : 'border-slate-200 dark:border-zinc-800 hover:border-slate-300 dark:hover:border-zinc-700 bg-slate-50/60 dark:bg-zinc-800/40 text-slate-600 dark:text-zinc-400'
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <Icon className={`w-4 h-4 ${isSelected ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400'}`} />
                    <span className="font-mono text-xs font-bold">{f.name}</span>
                  </div>
                  <span className="font-bold text-xs text-slate-900 dark:text-zinc-100">{f.title}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Export Options Checklist */}
        <div className="space-y-2.5 pt-1">
          <label className="text-[11px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider">
            Analytical Export Inclusions
          </label>
          <div className="space-y-2 text-xs bg-slate-50 dark:bg-zinc-800/50 p-3.5 rounded-2xl border border-slate-200/60 dark:border-zinc-800">
            <label className="flex items-center gap-2 cursor-pointer text-slate-700 dark:text-zinc-300">
              <input
                type="checkbox"
                checked={includeMetadata}
                onChange={e => setIncludeMetadata(e.target.checked)}
                className="accent-indigo-600 rounded"
              />
              <span>Include Station, Dataset, & Sample Metadata</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-slate-700 dark:text-zinc-300">
              <input
                type="checkbox"
                checked={includeLegend}
                onChange={e => setIncludeLegend(e.target.checked)}
                className="accent-indigo-600 rounded"
              />
              <span>Include Complete Visual Legend</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-slate-700 dark:text-zinc-300">
              <input
                type="checkbox"
                checked={includeMetrics}
                onChange={e => setIncludeMetrics(e.target.checked)}
                className="accent-indigo-600 rounded"
              />
              <span>Include Metric Summary (CTDI MAE & RMSE)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-slate-700 dark:text-zinc-300">
              <input
                type="checkbox"
                checked={includeExplanation}
                onChange={e => setIncludeExplanation(e.target.checked)}
                className="accent-indigo-600 rounded"
              />
              <span>Include Series Interpretation (Scientific Definitions)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-slate-700 dark:text-zinc-300">
              <input
                type="checkbox"
                checked={includeEvaluationScope}
                onChange={e => setIncludeEvaluationScope(e.target.checked)}
                className="accent-indigo-600 rounded"
              />
              <span>Include Evaluation Scope ("Hidden values only")</span>
            </label>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button
            variant="secondary"
            size="md"
            onPress={onClose}
            className="rounded-xl font-medium cursor-pointer"
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            size="md"
            onPress={handleExecuteExport}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-xs cursor-pointer flex items-center gap-1.5"
          >
            <Download className="w-4 h-4" />
            <span>Generate Export</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
