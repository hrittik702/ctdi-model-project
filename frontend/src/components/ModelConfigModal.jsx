import React from 'react';
import { X, Cpu, ShieldCheck } from 'lucide-react';
import { Button, Chip } from '@heroui/react';

export default function ModelConfigModal({ isOpen, onClose, modelConfig = null }) {
  if (!isOpen) return null;

  const configs = [
    { label: 'Model Architecture', value: modelConfig?.architecture || '1×1 Conv1d + Temporal Transformer Encoder' },
    { label: 'Model Version', value: modelConfig?.version || 'v0.1 Prototype' },
    { label: 'Sequence Length (Window)', value: `${modelConfig?.window_size || 24} Hours (Continuous sliding)` },
    { label: 'Input Feature Channels (F)', value: `${modelConfig?.in_features || 6} Pollutants (PM2.5, PM10, SO2, NO2, CO, O3)` },
    { label: 'Concatenated Channels (2*F)', value: `${(modelConfig?.in_features || 6) * 2} (Observations + Binary Masks)` },
    { label: 'Embedding Dimension (d_model)', value: `${modelConfig?.d_model || 64} dimensions` },
    { label: 'Multi-Head Attention (n_head)', value: `${modelConfig?.nhead || 4} attention heads` },
    { label: 'Transformer Encoder Layers', value: `${modelConfig?.num_layers || 2} layers` },
    { label: 'Feedforward Dimension', value: `${modelConfig?.dim_feedforward || 128} dimensions` },
    { label: 'Dropout Rate', value: `${modelConfig?.dropout || 0.1}` },
    { label: 'Positional Encoding', value: 'Sinusoidal (24 temporal positions)' },
    { label: 'Loss Function', value: modelConfig?.loss_function || 'Masked L1 Loss (artificially hidden points only)' },
    { label: 'Execution Framework', value: modelConfig?.framework || 'PyTorch' },
    { label: 'Execution Device', value: (modelConfig?.device || 'cpu').toUpperCase() },
    { label: 'Loaded Checkpoint', value: modelConfig?.checkpoint_path || 'checkpoints/transformer/best_temporal_transformer.pt' }
  ];

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 select-none"
      style={{
        backgroundColor: 'rgba(0, 0, 0, 0.55)',
        backdropFilter: 'blur(8px)'
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-white dark:bg-zinc-900 w-full max-w-xl rounded-3xl border border-slate-200/90 dark:border-zinc-800 shadow-2xl overflow-hidden p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-zinc-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 rounded-xl">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-slate-900 dark:text-zinc-100 text-base">Model Architecture & Hyperparameters</h3>
                <Chip color="success" variant="soft" size="sm" className="h-5 text-[10px] font-bold">
                  <Chip.Label>{modelConfig?.status === 'ready' ? 'Online' : 'Loaded'}</Chip.Label>
                </Chip>
              </div>
              <p className="text-xs text-slate-400 dark:text-zinc-500">CTDI {modelConfig?.framework || 'PyTorch'} Spatial-Temporal Attention Specification</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close model configuration"
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-zinc-800 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Hyperparameter Table */}
        <div className="divide-y divide-slate-100 dark:divide-zinc-800 max-h-96 overflow-y-auto pr-1 text-xs">
          {configs.map((c, i) => (
            <div key={i} className="py-2.5 flex items-center justify-between gap-4">
              <span className="text-slate-500 dark:text-zinc-400 font-medium">{c.label}</span>
              <span className="font-mono font-semibold text-slate-800 dark:text-zinc-200 text-right">{c.value}</span>
            </div>
          ))}
        </div>

        {/* Verification Footer */}
        <div className="p-3.5 bg-emerald-50/70 dark:bg-emerald-950/30 rounded-2xl border border-emerald-200/60 dark:border-emerald-800/40 flex items-center gap-2.5 text-xs text-emerald-800 dark:text-emerald-300">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Zero leakage: Preprocessing standard scaler fitted strictly on train split observations.</span>
        </div>

        <div className="flex justify-end pt-1">
          <Button
            size="sm"
            variant="primary"
            onPress={onClose}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-6 cursor-pointer"
          >
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
