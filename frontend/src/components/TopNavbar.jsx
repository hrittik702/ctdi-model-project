import React from 'react';
import { Chip } from '@heroui/react';
import { ChevronDown, MapPin } from 'lucide-react';
import ProjectIcon from './ui/ProjectIcon';

export default function TopNavbar({
  currentViewTitle,
  currentStation = 'Delhi',
  stations = [],
  onSelectStation,
  backendOnline,
  theme,
  onToggleTheme,
  onOpenSearch,
  onOpenExport,
  isPresentationMode,
  onTogglePresentationMode,
  onMobileMenuToggle
}) {
  const isDark = theme === 'dark';

  return (
    <header className="bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md border-b border-slate-200/80 dark:border-zinc-800 sticky top-0 z-20 h-16 px-4 sm:px-6 flex items-center justify-between shadow-2xs shrink-0">
      {/* Left Section: Master Identity & Subtitle */}
      <div className="flex items-center gap-3 min-w-0">
        {/* Sidebar collapse/expand trigger */}
        <button
          type="button"
          onClick={onMobileMenuToggle}
          title="Toggle Sidebar"
          aria-label="Toggle sidebar navigation"
          className="p-2 rounded-xl text-slate-500 hover:text-slate-800 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-zinc-800 transition cursor-pointer shrink-0"
        >
          <ProjectIcon name="menu" size="md" className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 min-w-0">
          <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-xs shrink-0">
            <ProjectIcon name="ctdi-logo" size="md" className="w-4 h-4 text-white" />
          </div>
          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-sm sm:text-base text-slate-900 dark:text-zinc-100 tracking-tight truncate">
                CTDI Air Imputation Studio
              </h1>
              <Chip color="default" variant="soft" size="sm" className="hidden md:inline-flex h-5 text-[10px] font-bold bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400">
                <Chip.Label>Indian AQI Network</Chip.Label>
              </Chip>
            </div>
            <p className="text-[11px] text-slate-400 dark:text-zinc-500 font-medium truncate hidden sm:block">
              Spatial-Temporal Air Quality Imputation & Analytics
            </p>
          </div>
        </div>
      </div>

      {/* Center Section: Global Search Command Palette Bar */}
      <div className="hidden lg:flex items-center flex-1 max-w-sm mx-6">
        <button
          type="button"
          onClick={onOpenSearch}
          aria-label="Open global search palette"
          className="w-full flex items-center justify-between px-3.5 py-1.5 rounded-xl bg-slate-100/90 dark:bg-zinc-800/80 border border-slate-200/70 dark:border-zinc-700/60 text-slate-400 dark:text-zinc-400 hover:border-slate-300 dark:hover:border-zinc-600 text-xs transition cursor-pointer shadow-2xs"
        >
          <div className="flex items-center gap-2 truncate">
            <ProjectIcon name="search" size="sm" className="w-3.5 h-3.5 text-slate-400 dark:text-zinc-400 shrink-0" />
            <span className="truncate">Search pollutants, samples, views...</span>
          </div>
          <kbd className="px-1.5 py-0.5 rounded-md bg-white dark:bg-zinc-700 text-[10px] font-mono text-slate-500 dark:text-zinc-300 border border-slate-200 dark:border-zinc-600 shadow-2xs shrink-0">
            Ctrl K
          </kbd>
        </button>
      </div>

      {/* Right Section: Station, API Status, Export, Presentation, Theme */}
      <div className="flex items-center gap-2 sm:gap-2.5 shrink-0">
        {/* Interactive Indian Station Selector */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-slate-100 dark:bg-zinc-800 border border-slate-200/80 dark:border-zinc-700/80 text-xs font-semibold text-slate-800 dark:text-zinc-200 shadow-2xs hover:border-indigo-400 dark:hover:border-indigo-500 transition">
          <MapPin className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
          <div className="relative flex items-center">
            <select
              value={currentStation}
              onChange={(e) => onSelectStation && onSelectStation(e.target.value)}
              className="bg-transparent border-none outline-none cursor-pointer text-xs font-bold text-slate-800 dark:text-zinc-100 pr-4 appearance-none hover:text-indigo-600 dark:hover:text-indigo-400 transition"
              title="Select Indian Monitoring Station"
              aria-label="Select Indian Monitoring Station"
            >
              {stations.length > 0 ? (
                stations.map(stn => (
                  <option key={stn.id} value={stn.id} className="bg-white dark:bg-zinc-900 text-slate-800 dark:text-zinc-100">
                    {stn.name} {stn.model_trained ? '★ (Active Model)' : `(${stn.state})`}
                  </option>
                ))
              ) : (
                <option value={currentStation} className="bg-white dark:bg-zinc-900 text-slate-800 dark:text-zinc-100">
                  {currentStation} (Active)
                </option>
              )}
            </select>
            <ChevronDown className="w-3 h-3 text-slate-400 pointer-events-none absolute right-0" />
          </div>
        </div>

        {/* API Status Chip */}
        <Chip 
          color={backendOnline ? "success" : "danger"} 
          variant="soft" 
          size="sm"
          className="dark:bg-emerald-950/40 dark:text-emerald-300 font-medium h-7"
        >
          <span className={`w-1.5 h-1.5 rounded-full mr-1.5 shrink-0 ${backendOnline ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
          <Chip.Label>{backendOnline ? 'FastAPI Connected' : 'FastAPI Offline'}</Chip.Label>
        </Chip>

        {/* Global Export Button */}
        <button
          type="button"
          onClick={onOpenExport}
          title="Export Workspace Data & Reports"
          aria-label="Export Workspace Data & Reports"
          className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-200 hover:bg-slate-200 dark:hover:bg-zinc-700 text-xs font-semibold transition border border-slate-200/70 dark:border-zinc-700/60 cursor-pointer h-7"
        >
          <ProjectIcon name="export" size="sm" className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
          <span className="hidden sm:inline">Export</span>
        </button>

        {/* Presentation Mode Toggle */}
        <button
          type="button"
          onClick={onTogglePresentationMode}
          title={isPresentationMode ? "Exit Presentation Mode" : "Enter Presentation Mode"}
          aria-label={isPresentationMode ? "Exit Presentation Mode" : "Enter Presentation Mode"}
          className={`p-1.5 rounded-xl border transition cursor-pointer h-7 w-7 flex items-center justify-center ${
            isPresentationMode
              ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs'
              : 'border-slate-200/80 dark:border-zinc-700/80 bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-300 hover:bg-slate-200 dark:hover:bg-zinc-700'
          }`}
        >
          <ProjectIcon name="presentation" size="sm" className="w-3.5 h-3.5 shrink-0" />
        </button>

        {/* Theme Toggle */}
        <button
          type="button"
          onClick={onToggleTheme}
          title={`Switch to ${isDark ? 'Light' : 'Dark'} Theme`}
          aria-label={`Switch to ${isDark ? 'Light' : 'Dark'} Theme`}
          className="p-1.5 rounded-xl border border-slate-200/80 dark:border-zinc-700/80 bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-300 hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-slate-200 dark:hover:bg-zinc-700 transition cursor-pointer h-7 w-7 flex items-center justify-center"
        >
          {isDark ? <ProjectIcon name="sun" size="sm" className="w-3.5 h-3.5 text-amber-400 shrink-0" /> : <ProjectIcon name="moon" size="sm" className="w-3.5 h-3.5 text-indigo-600 shrink-0" />}
        </button>
      </div>
    </header>
  );
}
