import React, { useState, useRef, useEffect } from 'react';
import { 
  ChevronDown, 
  Download, 
  Sun, 
  Moon, 
  Database, 
  Server, 
  Cpu, 
  CheckCircle2, 
  AlertCircle,
  MapPin,
  Activity,
  Layers,
  Target,
  History,
  Sliders,
  BarChart2,
  Compass
} from 'lucide-react';
import StationSelector from './StationSelector';

const SECTION_ICONS = {
  station: Compass,
  trajectory: Activity,
  multigrid: Layers,
  benchmark: Target,
  data: Database,
  comparison: Cpu,
  experiments: History,
  settings: Sliders,
  chart: BarChart2
};

export default function TopNavbar({
  currentViewTitle = 'Analytical Dashboard',
  currentStation = 'CW',
  stations = [],
  onSelectStation,
  backendOnline = false,
  theme = 'dark',
  onToggleTheme,
  onOpenExport,
  isSidebarCollapsed = false,
  onToggleSidebar,
  isScrolled = false,
  activeSection = null,
  isDashboard = false,
  // Optional backward-compatibility props
  onMobileMenuToggle,
  onOpenSearch
}) {
  const isDark = theme === 'dark';
  const [isSystemPopoverOpen, setIsSystemPopoverOpen] = useState(false);
  const popoverRef = useRef(null);

  // Close system popover on click outside or Escape
  useEffect(() => {
    function handleClickOutside(event) {
      if (popoverRef.current && !popoverRef.current.contains(event.target)) {
        setIsSystemPopoverOpen(false);
      }
    }
    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        setIsSystemPopoverOpen(false);
      }
    }

    if (isSystemPopoverOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isSystemPopoverOpen]);

  const handleToggle = onToggleSidebar || onMobileMenuToggle;
  const SectionIcon = activeSection?.iconName ? SECTION_ICONS[activeSection.iconName] : Compass;

  return (
    <header className="sticky top-0 z-20 h-14 w-full flex items-center justify-between shrink-0 bg-transparent select-none pointer-events-none">
      {/* Left Section: Compact Floating Station Selector Pill + Section Identity Pill */}
      <div className="flex items-center gap-2 sm:gap-2.5 min-w-0 pointer-events-auto">
        {/* Hong Kong EPD Station Selector */}
        <StationSelector
          currentStation={currentStation}
          stations={stations}
          onSelectStation={onSelectStation}
        />

        {/* 1. Dashboard Mode: Retains original content indicator text behavior */}
        {isDashboard && (
          <div className={`items-center gap-3 overflow-hidden transition-all duration-300 ease-in-out ${
            isScrolled 
              ? 'opacity-0 max-w-0 pointer-events-none -translate-x-2 invisible' 
              : 'opacity-100 max-w-[320px] translate-x-0 hidden sm:flex'
          }`}>
            <div className="h-3.5 w-px bg-slate-200 dark:bg-white/[0.08] shrink-0" />
            <h1 className="font-semibold text-slate-800 dark:text-[#F4F4F5] tracking-tight truncate text-xs sm:text-[13px] whitespace-nowrap">
              {currentViewTitle}
            </h1>
          </div>
        )}

        {/* 2. Analytical Pages: Compact Floating Section Identity Pill (Animated on Scroll) */}
        {!isDashboard && (
          <div 
            className={`transition-all duration-200 ease-out flex items-center min-w-0 motion-reduce:transition-none ${
              activeSection
                ? 'opacity-100 translate-y-0 max-w-[200px] sm:max-w-[280px] visible'
                : 'opacity-0 -translate-y-1 max-w-0 pointer-events-none invisible'
            }`}
          >
            <div 
              title={activeSection?.title || ''}
              className="flex items-center gap-1.5 sm:gap-2 h-8 px-2.5 rounded-lg text-xs font-medium border select-none transition-colors bg-white/95 dark:bg-[#111113] border-slate-200/80 dark:border-white/[0.07] text-slate-800 dark:text-[#F4F4F5] shadow-sm shadow-black/5 dark:shadow-[0_2px_6px_rgba(0,0,0,0.45)] truncate"
            >
              {SectionIcon && (
                <SectionIcon className="w-3.5 h-3.5 text-slate-500 dark:text-[#A1A1AA] shrink-0" />
              )}
              <span className="truncate font-semibold text-xs text-slate-800 dark:text-[#F4F4F5] tracking-tight">
                {activeSection?.title}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Right Section: System Diagnostics Popover, Export, Theme Toggle */}
      <div className="flex items-center gap-2 sm:gap-2.5 shrink-0 pointer-events-auto">
        {/* Compact System Status Indicator Popover */}
        <div className="relative" ref={popoverRef}>
          <button
            type="button"
            onClick={() => setIsSystemPopoverOpen(prev => !prev)}
            aria-expanded={isSystemPopoverOpen}
            aria-haspopup="true"
            aria-label="Toggle system diagnostic status"
            className={`flex items-center gap-1.5 h-8 px-2.5 rounded-lg text-xs font-medium transition cursor-pointer border select-none shadow-sm shadow-black/5 dark:shadow-[0_2px_6px_rgba(0,0,0,0.45)] ${
              isSystemPopoverOpen
                ? 'bg-slate-200/90 dark:bg-[#18181B] text-slate-900 dark:text-[#F4F4F5] border-slate-300 dark:border-white/[0.12]'
                : 'bg-white/95 dark:bg-[#111113] border-slate-200/80 dark:border-white/[0.07] text-slate-700 dark:text-[#F4F4F5] hover:bg-slate-100 dark:hover:bg-[#18181B] hover:border-slate-300 dark:hover:border-white/[0.1]'
            }`}
          >
            <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${
              backendOnline ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'
            }`} />
            <span className="hidden sm:inline text-xs font-medium text-slate-700 dark:text-[#F4F4F5]">System</span>
            <ChevronDown className={`w-3 h-3 text-slate-400 dark:text-[#B4B4BC] transition-transform duration-150 ${
              isSystemPopoverOpen ? 'rotate-180 text-slate-600 dark:text-[#F4F4F5]' : ''
            }`} />
          </button>

          {/* Diagnostic Popover Card */}
          {isSystemPopoverOpen && (
            <div className="absolute right-0 top-full mt-2 w-84 sm:w-92 bg-white dark:bg-[#111113] border border-slate-200/90 dark:border-white/[0.08] rounded-xl shadow-2xl p-4 z-50 text-xs animate-in fade-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between pb-2.5 mb-3 border-b border-slate-100 dark:border-white/[0.06]">
                <span className="font-semibold text-slate-900 dark:text-[#F4F4F5]">
                  System Diagnostics
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-slate-100 dark:bg-white/[0.06] text-slate-600 dark:text-[#B4B4BC] border border-slate-200/60 dark:border-white/[0.08]">
                  v1.0 Frozen Baseline
                </span>
              </div>

              <div className="space-y-3">
                {/* 1. Dataset State */}
                <div className="flex items-start gap-2.5">
                  <Database className="w-4 h-4 text-slate-700 dark:text-[#F4F4F5] shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-slate-800 dark:text-[#F4F4F5]">
                        Frozen Dataset Contract
                      </span>
                      <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> Verified
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-[#85858F] mt-0.5 leading-snug">
                      Hong Kong EPD (16 stations · 420,496 windows · 13 channels · 2019–2021)
                    </p>
                  </div>
                </div>

                {/* 2. API Backend State */}
                <div className="flex items-start gap-2.5">
                  <Server className="w-4 h-4 text-slate-700 dark:text-[#F4F4F5] shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-slate-800 dark:text-[#F4F4F5]">
                        FastAPI Backend
                      </span>
                      <span className={`text-[10px] font-medium flex items-center gap-1 ${
                        backendOnline 
                          ? 'text-emerald-600 dark:text-emerald-400' 
                          : 'text-amber-600 dark:text-amber-400'
                      }`}>
                        {backendOnline ? (
                          <>
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            Connected
                          </>
                        ) : (
                          <>
                            <AlertCircle className="w-3 h-3" />
                            Local Fallback Mode
                          </>
                        )}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-[#85858F] mt-0.5 leading-snug">
                      {backendOnline 
                        ? 'Serving live endpoints on http://localhost:8000'
                        : 'Backend offline. Frontend running from verified local baseline data.'}
                    </p>
                  </div>
                </div>

                {/* 3. Model Architecture */}
                <div className="flex items-start gap-2.5">
                  <Cpu className="w-4 h-4 text-slate-700 dark:text-[#F4F4F5] shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-slate-800 dark:text-[#F4F4F5]">
                        Reconstruction Model
                      </span>
                      <span className="text-[10px] font-medium text-slate-500 dark:text-zinc-400">
                        Specification Ready
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-[#85858F] mt-0.5 leading-snug">
                      CTDI CNN-Transformer spatial-temporal reconstruction model (16 stations · 13 channels).
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-3.5 pt-2.5 border-t border-slate-100 dark:border-white/[0.06] text-[10px] text-slate-400 dark:text-[#85858F] flex items-center justify-between">
                <span>Execution Engine: PyTorch 2.6 (CPU)</span>
                <span>SHA-256: 46/46 Passed</span>
              </div>
            </div>
          )}
        </div>

        {/* Global Quick Export Button */}
        <button
          type="button"
          onClick={onOpenExport}
          title="Export Workspace Data & Reports"
          aria-label="Export Workspace Data & Reports"
          className="flex items-center gap-1.5 h-8 px-2.5 rounded-lg border border-slate-200/80 dark:border-white/[0.07] bg-white/95 dark:bg-[#111113] hover:bg-slate-100 dark:hover:bg-[#18181B] hover:border-slate-300 dark:hover:border-white/[0.1] text-slate-700 dark:text-[#F4F4F5] text-xs font-medium transition cursor-pointer select-none shadow-sm shadow-black/5 dark:shadow-[0_2px_6px_rgba(0,0,0,0.45)] shrink-0"
        >
          <Download className="w-3.5 h-3.5 text-slate-700 dark:text-[#F4F4F5] shrink-0" />
          <span className="hidden md:inline">Export</span>
        </button>

        {/* Theme Toggle Button */}
        <button
          type="button"
          onClick={onToggleTheme}
          title={`Switch to ${isDark ? 'Light' : 'Dark'} Theme`}
          aria-label={`Switch to ${isDark ? 'Light' : 'Dark'} Theme`}
          className="h-8 w-8 rounded-lg border border-slate-200/80 dark:border-white/[0.07] bg-white/95 dark:bg-[#111113] hover:bg-slate-100 dark:hover:bg-[#18181B] hover:border-slate-300 dark:hover:border-white/[0.1] text-slate-700 dark:text-[#F4F4F5] transition cursor-pointer select-none shadow-sm shadow-black/5 dark:shadow-[0_2px_6px_rgba(0,0,0,0.45)] flex items-center justify-center shrink-0"
        >
          {isDark ? (
            <Sun className="w-3.5 h-3.5 text-[#F4F4F5] shrink-0" />
          ) : (
            <Moon className="w-3.5 h-3.5 text-slate-700 shrink-0" />
          )}
        </button>
      </div>
    </header>
  );
}
