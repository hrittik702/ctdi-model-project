import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  Database, 
  Cpu, 
  BarChart2, 
  ShieldCheck, 
  Sun, 
  Moon, 
  Copy, 
  Check, 
  RotateCcw, 
  Clock, 
  MapPin, 
  Activity, 
  ArrowRight, 
  FileCheck, 
  Terminal, 
  Info,
  SlidersHorizontal
} from 'lucide-react';
import SectionHeading from '../components/ui/SectionHeading';
import { 
  CANONICAL_CHANNELS 
} from '../constants/datasetContract';

export default function SettingsView({
  theme = 'dark',
  onToggleTheme,
  isSidebarCollapsed,
  onToggleSidebar,
  onOpenModelModal,
  onNavigateToTab
}) {
  const [activeTab, setActiveTab] = useState('general'); // 'general' | 'dataset' | 'model' | 'research'
  const [selectedChannelCategory, setSelectedChannelCategory] = useState('all'); // 'all' | 'air_quality' | 'meteorology' | 'traffic'
  const [copiedHash, setCopiedHash] = useState(false);
  const [cacheReset, setCacheReset] = useState(false);

  const tabs = [
    { id: 'general', label: 'General & Appearance', icon: Sliders },
    { id: 'dataset', label: 'Dataset Contract', icon: Database, badge: 'v1.0' },
    { id: 'model', label: 'Model Architecture', icon: Cpu },
    { id: 'research', label: 'Research & Benchmarks', icon: BarChart2, badge: '12 Masks' }
  ];

  const handleCopyManifestHash = () => {
    const hash = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';
    if (navigator.clipboard) {
      navigator.clipboard.writeText(hash);
    }
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  const handleClearCache = () => {
    try {
      localStorage.removeItem('ctdi_recent_queries');
      localStorage.removeItem('ctdi_table_density');
      setCacheReset(true);
      setTimeout(() => setCacheReset(false), 2500);
    } catch (e) {
      console.error(e);
    }
  };

  const handleScrollToSection = (tabId) => {
    setActiveTab(tabId);
    const element = document.getElementById(`section-${tabId}`);
    if (element) {
      const mainContainer = element.closest('main');
      if (mainContainer) {
        const topOffset = element.offsetTop - 72; // offset for sticky/floating navbar
        mainContainer.scrollTo({ top: Math.max(0, topOffset), behavior: 'smooth' });
      } else {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  };

  // Keep navigation active tab in sync with viewport scrolling
  useEffect(() => {
    const sectionIds = ['general', 'dataset', 'model', 'research'];
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id.replace('section-', '');
            setActiveTab(id);
          }
        });
      },
      {
        rootMargin: '-10% 0px -70% 0px',
        threshold: 0
      }
    );

    sectionIds.forEach((id) => {
      const el = document.getElementById(`section-${id}`);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const filteredChannels = selectedChannelCategory === 'all' 
    ? CANONICAL_CHANNELS 
    : CANONICAL_CHANNELS.filter(c => c.category === selectedChannelCategory);

  return (
    <div className="space-y-6 pb-12 select-none">
      {/* 1. Primary Page Identity Header */}
      <div>
        <SectionHeading
          id="workspace-settings"
          title="Workspace & Research Settings"
          icon="settings"
          action={
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-100 dark:bg-zinc-800 border border-slate-200/80 dark:border-zinc-700/60 text-[11px] font-mono text-slate-600 dark:text-zinc-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>CTDI Studio v1.0.0</span>
            </div>
          }
        />
        <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-zinc-400 mt-1 pl-0.5 flex-wrap">
          <strong className="text-slate-800 dark:text-zinc-200 font-semibold">Central / Western (CW)</strong>
          <span className="text-slate-300 dark:text-zinc-700">·</span>
          <span>Hong Kong EPD</span>
          <span className="text-slate-300 dark:text-zinc-700">·</span>
          <span className="text-indigo-600 dark:text-indigo-400 font-medium">Dataset Contract v1.0</span>
          <span className="text-slate-300 dark:text-zinc-700">·</span>
          <span>CNN-Transformer Spec</span>
          <span className="text-slate-300 dark:text-zinc-700">·</span>
          <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200/70 dark:border-indigo-800/60">
            12 Benchmark Scenarios
          </span>
        </div>
      </div>

      {/* 2. Compact Segmented Navigation Control */}
      <div className="p-1 bg-white dark:bg-zinc-900/95 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs flex items-center gap-1.5 overflow-x-auto">
        {tabs.map(tab => {
          const isActive = activeTab === tab.id;
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => handleScrollToSection(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl transition-all cursor-pointer whitespace-nowrap text-xs motion-tab-active motion-press ${
                isActive
                  ? 'bg-slate-100 dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 shadow-2xs border border-slate-200/80 dark:border-zinc-700 font-bold'
                  : 'text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-slate-50 dark:hover:bg-zinc-800/50 font-medium'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400 dark:text-zinc-500'}`} />
              <span>{tab.label}</span>
              {tab.badge && (
                <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded-md ${
                  isActive 
                    ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-semibold border border-indigo-200/60 dark:border-indigo-800/60' 
                    : 'bg-slate-200/60 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400 border border-transparent'
                }`}>
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* 3. SECTION 1: GENERAL & APPEARANCE */}
      <div id="section-general" className="space-y-3">
        {/* Section Heading with Scroll-Spy attributes */}
        <div 
          data-section-id="settings-general"
          data-section-title="General & Appearance"
          data-section-icon="settings"
          data-section-heading="true"
          className="transition-opacity duration-200 motion-reduce:transition-none pb-1 flex items-center justify-between"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold shrink-0 border border-indigo-200/60 dark:border-indigo-800/60">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-extrabold text-slate-900 dark:text-zinc-100 text-base sm:text-lg tracking-tight">
                General & Appearance
              </h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                Configure studio theme, sidebar navigation density, and global keyboard shortcuts.
              </p>
            </div>
          </div>
        </div>

        {/* Grayish zinc Card */}
        <div className="bg-white dark:bg-zinc-900/95 p-5 sm:p-6 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs space-y-5">
          {/* Subsection A: Interface Theme */}
          <div className="space-y-2.5">
            <div>
              <div className="text-xs font-bold text-slate-900 dark:text-zinc-100">Interface Theme</div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">
                Choose between dark studio mode or high-contrast daytime paper mode.
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-0.5">
              {/* Dark Studio Button */}
              <button
                type="button"
                onClick={theme !== 'dark' ? onToggleTheme : undefined}
                className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer flex items-center justify-between gap-3 motion-card-interactive motion-press ${
                  theme === 'dark'
                    ? 'border-indigo-500/60 dark:border-indigo-500/50 bg-indigo-50/20 dark:bg-indigo-950/30 ring-1 ring-indigo-500/30 shadow-2xs'
                    : 'border-slate-200 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-800/40 hover:border-slate-300 dark:hover:border-zinc-700'
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center text-indigo-400 shrink-0">
                    <Moon className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-bold text-slate-900 dark:text-zinc-100">Dark Studio</div>
                    <div className="text-[11px] text-slate-500 dark:text-zinc-400 truncate">Deep OLED black optimized for continuous telemetry</div>
                  </div>
                </div>
                <div className={`w-4 h-4 rounded-full flex items-center justify-center shrink-0 ${
                  theme === 'dark'
                    ? 'bg-indigo-600 dark:bg-indigo-500 text-white font-bold'
                    : 'border border-slate-300 dark:border-zinc-600'
                }`}>
                  {theme === 'dark' && <Check className="w-2.5 h-2.5 stroke-[3]" />}
                </div>
              </button>

              {/* Light Paper Button */}
              <button
                type="button"
                onClick={theme !== 'light' ? onToggleTheme : undefined}
                className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer flex items-center justify-between gap-3 motion-card-interactive motion-press ${
                  theme === 'light'
                    ? 'border-indigo-500/60 dark:border-indigo-500/50 bg-indigo-50/20 dark:bg-indigo-950/30 ring-1 ring-indigo-500/30 shadow-2xs'
                    : 'border-slate-200 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-800/40 hover:border-slate-300 dark:hover:border-zinc-700'
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-slate-100 border border-slate-300 flex items-center justify-center text-amber-500 shrink-0">
                    <Sun className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-bold text-slate-900 dark:text-zinc-100">Light Paper</div>
                    <div className="text-[11px] text-slate-500 dark:text-zinc-400 truncate">Clean daytime paper mode for reports & print</div>
                  </div>
                </div>
                <div className={`w-4 h-4 rounded-full flex items-center justify-center shrink-0 ${
                  theme === 'light'
                    ? 'bg-indigo-600 dark:bg-indigo-500 text-white font-bold'
                    : 'border border-slate-300 dark:border-zinc-600'
                }`}>
                  {theme === 'light' && <Check className="w-2.5 h-2.5 stroke-[3]" />}
                </div>
              </button>
            </div>
          </div>

          <div className="h-px bg-slate-100 dark:bg-zinc-800/80" />

          {/* Subsection B: Sidebar Navigation Layout */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="text-xs font-bold text-slate-900 dark:text-zinc-100">Sidebar Navigation</div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">
                Choose between expanded (240px) or compact (60px) navigation. Shortcut: <kbd className="px-1.5 py-0.2 rounded bg-slate-100 dark:bg-zinc-800 font-mono text-[10px] border border-slate-200 dark:border-zinc-700 text-slate-700 dark:text-zinc-300">Ctrl+B</kbd>
              </div>
            </div>

            <div className="inline-flex items-center p-1 rounded-xl bg-slate-100 dark:bg-zinc-800/80 border border-slate-200/80 dark:border-zinc-700/80 shrink-0">
              <button
                type="button"
                onClick={isSidebarCollapsed ? onToggleSidebar : undefined}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer motion-tab-active motion-press ${
                  !isSidebarCollapsed
                    ? 'bg-white dark:bg-zinc-900 text-slate-900 dark:text-zinc-100 font-bold shadow-2xs'
                    : 'text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100'
                }`}
              >
                Expanded (240px)
              </button>
              <button
                type="button"
                onClick={!isSidebarCollapsed ? onToggleSidebar : undefined}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer motion-tab-active motion-press ${
                  isSidebarCollapsed
                    ? 'bg-white dark:bg-zinc-900 text-slate-900 dark:text-zinc-100 font-bold shadow-2xs'
                    : 'text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100'
                }`}
              >
                Compact (60px)
              </button>
            </div>
          </div>

          <div className="h-px bg-slate-100 dark:bg-zinc-800/80" />

          {/* Subsection C: Studio Keyboard Shortcuts */}
          <div className="space-y-2.5">
            <div>
              <div className="text-xs font-bold text-slate-900 dark:text-zinc-100 flex items-center gap-2">
                <Terminal className="w-3.5 h-3.5 text-slate-400 dark:text-zinc-400" />
                <span>Studio Keyboard Shortcuts</span>
              </div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">
                Keyboard shortcuts available across all workspace views.
              </div>
            </div>

            <div className="rounded-xl border border-slate-200/80 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-800/30 divide-y divide-slate-200/60 dark:divide-zinc-800 overflow-hidden">
              {[
                { desc: 'Quick Command & Station Search', shortcut: 'Ctrl + K / ⌘K' },
                { desc: 'Toggle Sidebar Collapse Mode', shortcut: 'Ctrl + B / ⌘B' },
                { desc: 'Dismiss Active Modal or Dialog', shortcut: 'Esc' },
                { desc: 'Documentation & Help Shortcuts', shortcut: 'Ctrl + /' }
              ].map((item, idx) => (
                <div key={idx} className="px-4 py-2.5 flex items-center justify-between gap-3 text-xs">
                  <span className="text-slate-700 dark:text-zinc-300 font-medium">{item.desc}</span>
                  <kbd className="px-2.5 py-0.5 rounded-md bg-white dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 font-mono text-[11px] text-slate-800 dark:text-zinc-200 shadow-2xs shrink-0">
                    {item.shortcut}
                  </kbd>
                </div>
              ))}
            </div>
          </div>

          <div className="h-px bg-slate-100 dark:bg-zinc-800/80" />

          {/* Subsection D: Session Cache */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="text-xs font-bold text-slate-900 dark:text-zinc-100 flex items-center gap-2">
                <RotateCcw className="w-3.5 h-3.5 text-slate-400 dark:text-zinc-400" />
                <span>Session Cache & Local Preferences</span>
              </div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">
                Clear cached table filters and search histories without altering backend dataset files.
              </div>
            </div>

            <button
              type="button"
              onClick={handleClearCache}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer shrink-0 border ${
                cacheReset
                  ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30'
                  : 'bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-200 border-slate-200 dark:border-zinc-700 hover:bg-slate-200 dark:hover:bg-zinc-750'
              }`}
            >
              {cacheReset ? (
                <span className="flex items-center gap-1.5">
                  <Check className="w-3.5 h-3.5" />
                  Cache Cleared
                </span>
              ) : (
                'Reset Local Cache'
              )}
            </button>
          </div>
        </div>
      </div>

      {/* 4. SECTION 2: DATASET CONTRACT */}
      <div id="section-dataset" className="space-y-3">
        {/* Section Heading with Scroll-Spy attributes */}
        <div 
          data-section-id="settings-dataset"
          data-section-title="Dataset Contract"
          data-section-icon="data"
          data-section-heading="true"
          className="transition-opacity duration-200 motion-reduce:transition-none pb-1 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold shrink-0 border border-indigo-200/60 dark:border-indigo-800/60">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-extrabold text-slate-900 dark:text-zinc-100 text-base sm:text-lg tracking-tight">
                Authoritative Dataset Contract v1.0
              </h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                Permanent frozen air quality corpus with SHA-256 cryptographic verification and zero forward look-ahead leakage.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200/70 dark:border-emerald-800/60 text-[11px] font-mono font-bold">
              <ShieldCheck className="w-3.5 h-3.5" />
              Frozen Baseline
            </span>
          </div>
        </div>

        {/* Grayish zinc Card */}
        <div className="bg-white dark:bg-zinc-900/95 p-5 sm:p-6 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs space-y-5">
          {/* Dataset Dimension Metric Tiles (4 Summary Cards matching other views) */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="p-3.5 sm:p-4 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-wider text-slate-400 dark:text-zinc-500 font-bold">
                  Network Scope
                </span>
                <MapPin className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
              </div>
              <div className="mt-2">
                <div className="text-xl sm:text-2xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-zinc-100">
                  16 Stations
                </div>
                <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">
                  13 General · 3 Roadside
                </div>
              </div>
            </div>

            <div className="p-3.5 sm:p-4 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-wider text-slate-400 dark:text-zinc-500 font-bold">
                  Temporal Coverage
                </span>
                <Clock className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
              </div>
              <div className="mt-2">
                <div className="text-xl sm:text-2xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-zinc-100">
                  26,304 Hours
                </div>
                <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">
                  1,096 Days (3 Full Years)
                </div>
              </div>
            </div>

            <div className="p-3.5 sm:p-4 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-wider text-slate-400 dark:text-zinc-500 font-bold">
                  Window Corpus
                </span>
                <Activity className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
              </div>
              <div className="mt-2">
                <div className="text-xl sm:text-2xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-zinc-100">
                  419,496
                </div>
                <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">
                  24h windows · 1h stride
                </div>
              </div>
            </div>

            <div className="p-3.5 sm:p-4 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-wider text-slate-400 dark:text-zinc-500 font-bold">
                  Continuous Channels
                </span>
                <SlidersHorizontal className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
              </div>
              <div className="mt-2">
                <div className="text-xl sm:text-2xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-zinc-100">
                  13 Channels
                </div>
                <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">
                  5 Criteria · 6 Met · 2 Traf
                </div>
              </div>
            </div>
          </div>

          <div className="h-px bg-slate-100 dark:bg-zinc-800/80" />

          {/* Chronological Split Timeline & Purged Buffers */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900 dark:text-zinc-100">
                Chronological Split Timeline & Zero-Leakage Purged Buffers
              </span>
              <span className="text-[11px] font-mono text-slate-400 dark:text-zinc-500">420,864 Station-Hours</span>
            </div>

            {/* Segmented Timeline Bar */}
            <div className="h-3 w-full rounded-full bg-slate-100 dark:bg-zinc-800 flex overflow-hidden border border-slate-200/80 dark:border-zinc-700/60">
              <div style={{ width: '69.96%' }} className="bg-blue-600 dark:bg-blue-500" title="Train: 69.96% (294,160 windows)" />
              <div style={{ width: '1.2%' }} className="bg-amber-500" title="Buffer 1: 752 windows (24h barrier)" />
              <div style={{ width: '14.89%' }} className="bg-emerald-600 dark:bg-emerald-500" title="Val: 14.89% (62,608 windows)" />
              <div style={{ width: '1.2%' }} className="bg-amber-500" title="Buffer 2: 752 windows (24h barrier)" />
              <div style={{ width: '14.80%' }} className="bg-purple-600 dark:bg-purple-500" title="Test: 14.80% (62,224 windows)" />
            </div>

            {/* 3 Partition Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-800 dark:text-zinc-100 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-blue-500" />
                    Train Partition
                  </span>
                  <span className="font-mono font-bold text-blue-600 dark:text-blue-400">69.96%</span>
                </div>
                <div className="text-[11px] font-mono text-slate-500 dark:text-zinc-400">294,160 windows · 25 mos</div>
                <div className="text-[10px] text-slate-400 dark:text-zinc-500">2019-01-01 – 2021-02-05 (2.57% miss)</div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-800 dark:text-zinc-100 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    Validation Partition
                  </span>
                  <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">14.89%</span>
                </div>
                <div className="text-[11px] font-mono text-slate-500 dark:text-zinc-400">62,608 windows · 5.5 mos</div>
                <div className="text-[10px] text-slate-400 dark:text-zinc-500">2021-02-07 – 2021-07-20 (2.96% miss)</div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-800 dark:text-zinc-100 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-purple-500" />
                    Test Partition
                  </span>
                  <span className="font-mono font-bold text-purple-600 dark:text-purple-400">14.80%</span>
                </div>
                <div className="text-[11px] font-mono text-slate-500 dark:text-zinc-400">62,224 windows · 5.3 mos</div>
                <div className="text-[10px] text-slate-400 dark:text-zinc-500">2021-07-22 – 2021-12-31 (2.75% miss)</div>
              </div>
            </div>

            {/* Purged Buffers Note */}
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-800 dark:text-amber-300 text-xs flex items-start gap-2.5">
              <Info className="w-4 h-4 shrink-0 mt-0.5 text-amber-500" />
              <div className="text-xs leading-relaxed">
                <span className="font-bold">Purged Isolation Buffers (0.18% × 2 = 1,504 windows): </span>
                Exact 24h physical calendar barriers (2021-02-06 and 2021-07-21) are removed between splits to ensure sliding windows cannot straddle train-val or val-test split boundaries.
              </div>
            </div>
          </div>

          <div className="h-px bg-slate-100 dark:bg-zinc-800/80" />

          {/* 13 Canonical Continuous Channels Table */}
          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
              <div>
                <div className="text-xs font-bold text-slate-900 dark:text-zinc-100">13 Canonical Continuous Channels</div>
                <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">
                  Ordered feature tensor channels with empirical mean, std, and physical bounds.
                </div>
              </div>

              {/* Segmented Filter */}
              <div className="inline-flex p-1 rounded-xl bg-slate-100 dark:bg-zinc-800/80 border border-slate-200/80 dark:border-zinc-700/80 text-xs">
                {[
                  { id: 'all', label: 'All 13' },
                  { id: 'air_quality', label: 'Criteria (5)' },
                  { id: 'meteorology', label: 'Meteo (6)' },
                  { id: 'traffic', label: 'Traffic (2)' }
                ].map(c => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setSelectedChannelCategory(c.id)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-medium transition cursor-pointer ${
                      selectedChannelCategory === c.id
                        ? 'bg-white dark:bg-zinc-900 text-slate-900 dark:text-zinc-100 font-bold shadow-2xs'
                        : 'text-slate-500 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-zinc-200'
                    }`}
                  >
                    {c.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="overflow-x-auto rounded-xl border border-slate-200/80 dark:border-zinc-800">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="bg-slate-50/80 dark:bg-zinc-800/60 border-b border-slate-200/70 dark:border-zinc-800 text-[10px] text-slate-400 dark:text-zinc-400 uppercase font-sans">
                    <th className="py-2.5 px-3 font-bold">Idx</th>
                    <th className="py-2.5 px-3 font-bold">Channel</th>
                    <th className="py-2.5 px-3 font-bold">Group</th>
                    <th className="py-2.5 px-3 font-bold">Unit</th>
                    <th className="py-2.5 px-3 font-bold text-right">Mean</th>
                    <th className="py-2.5 px-3 font-bold text-right">Std</th>
                    <th className="py-2.5 px-3 font-bold text-right">Range</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/60 bg-white dark:bg-zinc-900/95">
                  {filteredChannels.map(ch => (
                    <tr key={ch.id} className="hover:bg-slate-50/60 dark:hover:bg-zinc-800/30 transition">
                      <td className="py-2 px-3 text-slate-400 dark:text-zinc-500 font-bold">{ch.index}</td>
                      <td className="py-2 px-3">
                        <div className="font-bold text-slate-900 dark:text-zinc-100 font-sans text-xs">{ch.name}</div>
                        <div className="text-[10px] text-slate-400 dark:text-zinc-500 font-sans">{ch.desc}</div>
                      </td>
                      <td className="py-2 px-3 font-sans">
                        <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-medium ${
                          ch.category === 'air_quality'
                            ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20'
                            : ch.category === 'meteorology'
                            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
                        }`}>
                          {ch.group}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-slate-600 dark:text-zinc-300">{ch.unit}</td>
                      <td className="py-2 px-3 text-right text-slate-800 dark:text-zinc-200">{ch.mean.toFixed(2)}</td>
                      <td className="py-2 px-3 text-right text-slate-800 dark:text-zinc-200">{ch.std.toFixed(2)}</td>
                      <td className="py-2 px-3 text-right text-slate-500 dark:text-zinc-400">
                        [{ch.min}, {ch.max}]
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="h-px bg-slate-100 dark:bg-zinc-800/80" />

          {/* SHA-256 Cryptographic Verification */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center shrink-0 border border-emerald-500/20">
                <FileCheck className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <div className="font-bold text-slate-900 dark:text-zinc-100 flex items-center gap-2">
                  <span>SHA-256 Manifest Integrity Verified</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-500 font-semibold">46 / 46 Files</span>
                </div>
                <div className="text-[11px] font-mono text-slate-400 dark:text-zinc-500 mt-0.5 truncate">
                  manifest.json checksum: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={handleCopyManifestHash}
              className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-200 border border-slate-200 dark:border-zinc-700 hover:bg-slate-200 dark:hover:bg-zinc-750 transition cursor-pointer shrink-0 motion-press"
            >
              {copiedHash ? (
                <span className="flex items-center gap-1.5 text-emerald-500">
                  <Check className="w-3.5 h-3.5" />
                  Hash Copied
                </span>
              ) : (
                <span className="flex items-center gap-1.5">
                  <Copy className="w-3.5 h-3.5" />
                  Copy SHA-256
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* 5. SECTION 3: MODEL ARCHITECTURE */}
      <div id="section-model" className="space-y-3">
        {/* Section Heading with Scroll-Spy attributes */}
        <div 
          data-section-id="settings-model"
          data-section-title="Model Architecture"
          data-section-icon="comparison"
          data-section-heading="true"
          className="transition-opacity duration-200 motion-reduce:transition-none pb-1 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold shrink-0 border border-indigo-200/60 dark:border-indigo-800/60">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-extrabold text-slate-900 dark:text-zinc-100 text-base sm:text-lg tracking-tight">
                Model Architecture Specification
              </h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                CTDI CNN-Transformer spatial feature projector and multi-head temporal encoder specification.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200/70 dark:border-indigo-800/60">
              Specification
            </span>
            <button
              type="button"
              onClick={onOpenModelModal}
              className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-200 border border-slate-200/80 dark:border-zinc-700 hover:bg-slate-200 dark:hover:bg-zinc-750 transition cursor-pointer"
            >
              Inspect Hyperparameters
            </button>
          </div>
        </div>

        {/* Grayish zinc Card */}
        <div className="bg-white dark:bg-zinc-900/95 p-5 sm:p-6 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs space-y-5">
          {/* Architecture Parameter Matrix */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800">
              <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase tracking-wider font-bold">Input Channels (F)</div>
              <div className="text-base font-extrabold text-slate-900 dark:text-zinc-100 font-mono mt-1">13 Features</div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">5 Criteria + 6 Met + 2 Traf</div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800">
              <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase tracking-wider font-bold">Observation Tensor (2·F)</div>
              <div className="text-base font-extrabold text-slate-900 dark:text-zinc-100 font-mono mt-1">26 Dims</div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">Values + binary mask</div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800">
              <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase tracking-wider font-bold">Window Length (T)</div>
              <div className="text-base font-extrabold text-slate-900 dark:text-zinc-100 font-mono mt-1">24 Hours</div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">Consecutive hourly steps</div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800">
              <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase tracking-wider font-bold">Latent Embedding (d_model)</div>
              <div className="text-base font-extrabold text-slate-900 dark:text-zinc-100 font-mono mt-1">64</div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">Dense projection dim</div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800">
              <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase tracking-wider font-bold">Multi-Head Attention</div>
              <div className="text-base font-extrabold text-slate-900 dark:text-zinc-100 font-mono mt-1">4 Heads</div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">16 dims per head</div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800">
              <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase tracking-wider font-bold">Encoder Depth</div>
              <div className="text-base font-extrabold text-slate-900 dark:text-zinc-100 font-mono mt-1">2 Layers</div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">Stacked Transformer blocks</div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800">
              <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase tracking-wider font-bold">Loss Function</div>
              <div className="text-sm font-extrabold text-slate-900 dark:text-zinc-100 font-mono mt-1">Masked L1</div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">Withheld cells only</div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800">
              <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase tracking-wider font-bold">Positional Encoding</div>
              <div className="text-sm font-extrabold text-slate-900 dark:text-zinc-100 font-mono mt-1">Sinusoidal</div>
              <div className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">24h harmonic frequency</div>
            </div>
          </div>
        </div>
      </div>

      {/* 6. SECTION 4: RESEARCH & BENCHMARKS */}
      <div id="section-research" className="space-y-3">
        {/* Section Heading with Scroll-Spy attributes */}
        <div 
          data-section-id="settings-research"
          data-section-title="Research & Benchmarks"
          data-section-icon="chart"
          data-section-heading="true"
          className="transition-opacity duration-200 motion-reduce:transition-none pb-1 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold shrink-0 border border-indigo-200/60 dark:border-indigo-800/60">
              <BarChart2 className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-extrabold text-slate-900 dark:text-zinc-100 text-base sm:text-lg tracking-tight">
                Research & Benchmark Protocols
              </h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                Standardized test partition evaluation protocols spanning 12 frozen mask scenarios.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => onNavigateToTab && onNavigateToTab('scoreboard')}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-200 border border-slate-200/80 dark:border-zinc-700 hover:bg-slate-200 dark:hover:bg-zinc-750 transition cursor-pointer shrink-0"
          >
            <span>View Benchmark Scoreboard</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Grayish zinc Card */}
        <div className="bg-white dark:bg-zinc-900/95 p-5 sm:p-6 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs space-y-5">
          {/* 3 Scenario Family Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 space-y-2">
              <div className="flex items-center justify-between gap-1.5 flex-wrap">
                <div className="font-bold text-slate-900 dark:text-zinc-100 flex items-center gap-1.5">
                  <Activity className="w-4 h-4 text-blue-500 shrink-0" />
                  <span>MCAR Stochastic (4)</span>
                </div>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-blue-500/10 text-blue-500 font-bold shrink-0">
                  Bernoulli
                </span>
              </div>
              <div className="text-[11px] font-mono text-slate-600 dark:text-zinc-300">
                Rates: 10%, 30%, 50%, 70%
              </div>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400 leading-relaxed">
                Evaluates reconstruction against independent wireless packet losses and intermittent telemetry gaps.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 space-y-2">
              <div className="flex items-center justify-between gap-1.5 flex-wrap">
                <div className="font-bold text-slate-900 dark:text-zinc-100 flex items-center gap-1.5">
                  <MapPin className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>Station Outages (4)</span>
                </div>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-500 font-bold shrink-0">
                  Spatial
                </span>
              </div>
              <div className="text-[11px] font-mono text-slate-600 dark:text-zinc-300">
                1, 2, 4 Stations & Network
              </div>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400 leading-relaxed">
                Tests spatial covariance modeling when entire monitoring stations suffer power failure or physical blackout.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 space-y-2">
              <div className="flex items-center justify-between gap-1.5 flex-wrap">
                <div className="font-bold text-slate-900 dark:text-zinc-100 flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-purple-500 shrink-0" />
                  <span>Temporal Blocks (4)</span>
                </div>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-purple-500/10 text-purple-500 font-bold shrink-0">
                  Consecutive
                </span>
              </div>
              <div className="text-[11px] font-mono text-slate-600 dark:text-zinc-300">
                Duration: 10%, 30%, 50%, 70%
              </div>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400 leading-relaxed">
                Evaluates diurnal continuity and recovery during sustained multi-hour hardware maintenance and calibration outages.
              </p>
            </div>
          </div>

          <div className="h-px bg-slate-100 dark:bg-zinc-800/80" />

          {/* Protocol Ground Rules */}
          <div className="space-y-2 text-xs">
            <div className="font-bold text-slate-900 dark:text-zinc-100">
              Evaluation & Fairness Ground Rules:
            </div>
            <ul className="space-y-1.5 text-slate-600 dark:text-zinc-400 pl-4 list-disc text-[11px]">
              <li>Strict evaluation solely at artificially masked cells where <code className="font-mono text-slate-800 dark:text-zinc-200">eval_mask == 1</code>.</li>
              <li>Zero loss penalty or metric credit is awarded on naturally unobserved ground truth data.</li>
              <li>All baselines (Forward Fill, Mean Impute, Linear, Spatial IDW) evaluated on the exact same coordinate masks.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
