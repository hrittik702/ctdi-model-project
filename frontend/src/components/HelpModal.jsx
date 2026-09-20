import React, { useEffect } from 'react';
import { 
  X, 
  Command, 
  Keyboard, 
  BookOpen, 
  Database,
  ExternalLink
} from 'lucide-react';

export default function HelpModal({ isOpen, onClose, onNavigateToSettings }) {
  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const shortcuts = [
    { keyCombo: ['Ctrl', 'K'], label: 'Open Search & Command Palette', desc: 'Jump to any view, station, or channel' },
    { keyCombo: ['Ctrl', 'B'], label: 'Toggle Sidebar', desc: 'Expand or collapse sidebar navigation' },
    { keyCombo: ['Esc'], label: 'Close Dialogs', desc: 'Dismiss active modals and overlays' }
  ];

  const workflowSections = [
    {
      title: 'OVERVIEW',
      desc: 'High-level dashboard summarizing spatial coverage, dataset metrics, and research KPIs.'
    },
    {
      title: 'ANALYZE',
      desc: 'Detailed trajectory investigation (24-hour windows), multi-pollutant multiples, station profiles, and raw sequence inspection.'
    },
    {
      title: 'EXPERIMENTS',
      desc: 'Evaluation scoreboards, multi-model comparison across 12 masking scenarios, and experiment run history.'
    },
    {
      title: 'SETTINGS',
      desc: 'Comprehensive configuration: general preferences, frozen dataset contract, model architecture spec, and system health.'
    }
  ];

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 dark:bg-black/80 backdrop-blur-xs motion-modal-backdrop"
      onClick={onClose}
    >
      <div 
        className="w-full max-w-2xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh] motion-modal-content"
        onClick={e => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Help & Keyboard Shortcuts"
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200/80 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-900/50">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center border border-indigo-200 dark:border-indigo-800/60">
              <Keyboard className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-zinc-100">
                Help & Keyboard Shortcuts
              </h2>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400">
                CTDI Air Pollution Imputation Studio Quick Reference
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close dialog"
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-zinc-800 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="overflow-y-auto p-6 space-y-6 text-xs text-slate-600 dark:text-zinc-300">
          {/* Keyboard Shortcuts Section */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <Command className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
                Keyboard Shortcuts
              </h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              {shortcuts.map((item, idx) => (
                <div 
                  key={idx}
                  className="p-3 rounded-xl border border-slate-200/80 dark:border-zinc-800 bg-slate-50/60 dark:bg-zinc-800/60 flex flex-col justify-between"
                >
                  <div className="flex items-center gap-1 mb-2">
                    {item.keyCombo.map((k, kIdx) => (
                      <kbd 
                        key={kIdx} 
                        className="px-2 py-1 rounded bg-white dark:bg-zinc-800 border border-slate-300 dark:border-zinc-700 text-[10px] font-mono font-bold text-slate-800 dark:text-zinc-200 shadow-2xs"
                      >
                        {k}
                      </kbd>
                    ))}
                  </div>
                  <div>
                    <span className="font-semibold text-slate-800 dark:text-zinc-200 block mb-0.5">
                      {item.label}
                    </span>
                    <span className="text-[11px] text-slate-400 dark:text-zinc-500">
                      {item.desc}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Research Architecture & Navigation Map */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <BookOpen className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
                Information Architecture
              </h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {workflowSections.map((sec, idx) => (
                <div 
                  key={idx} 
                  className="p-3 rounded-xl border border-slate-200/70 dark:border-zinc-800 bg-white dark:bg-zinc-800/60 space-y-1"
                >
                  <span className="text-[11px] font-bold text-indigo-600 dark:text-indigo-400">
                    {sec.title}
                  </span>
                  <p className="text-[11px] text-slate-500 dark:text-zinc-400 leading-relaxed">
                    {sec.desc}
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* Research Truthfulness & Status Summary */}
          <section className="p-4 rounded-xl border border-slate-200/80 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-800/40 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-800 dark:text-zinc-200 flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                Frozen Dataset Contract v1.0
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-200 dark:bg-zinc-700 text-slate-700 dark:text-zinc-300">
                46 Verified Files
              </span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
              <div>
                <span className="text-slate-400 dark:text-zinc-500 block">Spatial Network</span>
                <span className="font-semibold text-slate-700 dark:text-zinc-200">16 HK Stations</span>
              </div>
              <div>
                <span className="text-slate-400 dark:text-zinc-500 block">Temporal Windows</span>
                <span className="font-semibold text-slate-700 dark:text-zinc-200">420,496 (24h)</span>
              </div>
              <div>
                <span className="text-slate-400 dark:text-zinc-500 block">Channels</span>
                <span className="font-semibold text-slate-700 dark:text-zinc-200">13 Continuous</span>
              </div>
              <div>
                <span className="text-slate-400 dark:text-zinc-500 block">Model Status</span>
                <span className="font-semibold text-slate-700 dark:text-zinc-200">Specification Ready</span>
              </div>
            </div>
          </section>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-slate-200/80 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-900/50">
          <button
            type="button"
            onClick={() => {
              onClose();
              if (onNavigateToSettings) onNavigateToSettings();
            }}
            className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 cursor-pointer flex items-center gap-1.5"
          >
            <span>Open Full Workspace Settings</span>
            <ExternalLink className="w-3 h-3" />
          </button>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-slate-200 dark:bg-zinc-800 hover:bg-slate-300 dark:hover:bg-zinc-700 text-xs font-semibold text-slate-800 dark:text-zinc-200 transition cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
