import React, { useState } from 'react';

/**
 * Custom line-based SVG icons for research-oriented navigation.
 * 24x24 viewBox, stroke-based, consistent geometry, zero colorful box containers.
 */

function CtdiBrandIcon({ className = "w-4 h-4", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <circle cx="12" cy="12" r="3" fill="currentColor" />
      <path d="M12 3v3" />
      <path d="M12 18v3" />
      <path d="M3 12h3" />
      <path d="M18 12h3" />
      <circle cx="12" cy="12" r="8" strokeDasharray="3 3" />
    </svg>
  );
}

function ProjectDiamondLogo({ className = "w-4 h-4", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <polygon points="12 2.5 21.5 12 12 21.5 2.5 12" />
    </svg>
  );
}

function DashboardNavIcon({ className = "w-5 h-5", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.85"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
    </svg>
  );
}

function TrajectoryNavIcon({ className = "w-5 h-5", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.85"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <polyline points="3 12 7 12 10 5 14 19 17 12 21 12" />
    </svg>
  );
}

function MultiPollutantNavIcon({ className = "w-5 h-5", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.85"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <path d="M12 2L2 7l10 5 10-5-10-5z" />
      <path d="M2 12l10 5 10-5" />
      <path d="M2 17l10 5 10-5" />
    </svg>
  );
}

function StationsNavIcon({ className = "w-5 h-5", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.85"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <path d="M12 2a4.5 4.5 0 0 0-4.5 4.5c0 3.2 4.5 7.5 4.5 7.5s4.5-4.3 4.5-7.5A4.5 4.5 0 0 0 12 2z" />
      <circle cx="12" cy="6.5" r="1.5" />
      <circle cx="4.5" cy="19.5" r="2" />
      <circle cx="19.5" cy="19.5" r="2" />
      <circle cx="12" cy="20" r="1.5" />
      <path d="M6.5 19.5h4" />
      <path d="M13.5 20h4" />
      <path d="M12 14v4.5" />
    </svg>
  );
}

function DataExplorerNavIcon({ className = "w-5 h-5", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.85"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <line x1="3" y1="10" x2="21" y2="10" />
      <line x1="9" y1="10" x2="9" y2="20" />
      <line x1="15" y1="10" x2="15" y2="20" />
    </svg>
  );
}

function BenchmarkNavIcon({ className = "w-5 h-5", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.85"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <circle cx="12" cy="12" r="9" />
      <path d="M8.5 12l2.5 2.5 4.5-5" />
    </svg>
  );
}

function ModelComparisonNavIcon({ className = "w-5 h-5", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.85"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <circle cx="18" cy="18" r="3" />
      <circle cx="6" cy="6" r="3" />
      <path d="M6 9v12" />
      <path d="M18 15V3" />
      <path d="M6 15l4-4" />
      <path d="M18 9l-4 4" />
    </svg>
  );
}

function ExperimentHistoryNavIcon({ className = "w-5 h-5", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.85"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
      <path d="M3 3v5h5" />
      <polyline points="12 7 12 12 15 15" />
    </svg>
  );
}

function SettingsNavIcon({ className = "w-5 h-5", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.85"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  );
}

function HelpNavIcon({ className = "w-5 h-5", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.85"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <circle cx="12" cy="12" r="9" />
      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

function SearchHeaderIcon({ className = "w-4 h-4", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function CollapseHeaderIcon({ className = "w-4 h-4", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <rect width="18" height="18" x="3" y="3" rx="2" />
      <path d="M9 3v18" />
      <path d="m16 15-3-3 3-3" />
    </svg>
  );
}

function ExpandHeaderIcon({ className = "w-4 h-4", ...props }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      <rect width="18" height="18" x="3" y="3" rx="2" />
      <path d="M9 3v18" />
      <path d="m14 9 3 3-3 3" />
    </svg>
  );
}

/**
 * Authoritative Navigation Groups
 */
const NAVIGATION_GROUPS = [
  {
    title: 'OVERVIEW',
    items: [
      { id: 'dashboard', label: 'Dashboard', Icon: DashboardNavIcon }
    ]
  },
  {
    title: 'ANALYZE',
    items: [
      { id: 'explorer', label: '24h Trajectory', Icon: TrajectoryNavIcon },
      { id: 'multigrid', label: 'Multi-Pollutant', Icon: MultiPollutantNavIcon },
      { id: 'station', label: 'Stations', Icon: StationsNavIcon },
      { id: 'data_explorer', label: 'Data Explorer', Icon: DataExplorerNavIcon }
    ]
  },
  {
    title: 'EXPERIMENTS',
    items: [
      { id: 'scoreboard', label: 'Benchmark', Icon: BenchmarkNavIcon },
      { id: 'comparison', label: 'Model Comparison', Icon: ModelComparisonNavIcon },
      { id: 'experiments', label: 'Experiment History', Icon: ExperimentHistoryNavIcon }
    ]
  }
];

export default function Sidebar({
  currentTab,
  onSelectTab,
  isCollapsed,
  onToggleCollapse,
  onOpenSearch,
  onOpenHelp
}) {
  const [hoveredTooltip, setHoveredTooltip] = useState(null);

  return (
    <aside
      className={`h-full bg-slate-50/80 dark:bg-[#050505] border-r border-slate-200/80 dark:border-zinc-800 flex flex-col transition-[width] duration-300 ease-in-out shrink-0 select-none z-30 min-h-0 relative overflow-x-hidden will-change-[width] ${
        isCollapsed ? 'w-[60px]' : 'w-[240px]'
      }`}
    >
      {/* 1. Sidebar Brand Header with Title, Search, and Collapse Actions */}
      <div className={`h-14 px-3 flex items-center shrink-0 overflow-hidden relative ${
        isCollapsed ? 'justify-center' : 'justify-between'
      }`}>
        <div className={`flex items-center min-w-0 ${
          isCollapsed ? 'gap-0 justify-center' : 'gap-2.5'
        }`}>
          {/* Logo / Expand Trigger Button */}
          <button
            type="button"
            onClick={isCollapsed ? onToggleCollapse : undefined}
            title={isCollapsed ? "Expand sidebar (Ctrl+B)" : undefined}
            aria-label={isCollapsed ? "Expand sidebar" : "Air Pollution CTDI Studio"}
            className={`group relative w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-colors ${
              isCollapsed
                ? 'cursor-pointer hover:bg-slate-200/60 dark:hover:bg-zinc-800'
                : 'cursor-default'
            }`}
          >
            {/* Diamond Logo Icon */}
            <span className={`w-7 h-7 rounded-lg bg-slate-200/70 dark:bg-zinc-800 text-slate-800 dark:text-zinc-100 flex items-center justify-center shrink-0 border border-slate-300/80 dark:border-zinc-700/80 transition-all duration-200 ${
              isCollapsed ? 'group-hover:opacity-0 group-hover:scale-75' : ''
            }`}>
              <ProjectDiamondLogo className="w-[18px] h-[18px]" />
            </span>

            {/* Hover Expand Icon (only active when collapsed) */}
            {isCollapsed && (
              <span className="absolute inset-0 flex items-center justify-center text-slate-800 dark:text-zinc-100 transition-all duration-200 opacity-0 scale-75 group-hover:opacity-100 group-hover:scale-100 pointer-events-none">
                <ExpandHeaderIcon className="w-5 h-5 text-slate-800 dark:text-zinc-100" />
              </span>
            )}
          </button>

          {/* Project Title (Smoothly collapses width & fades) */}
          <div className={`flex flex-col min-w-0 transition-all duration-300 ease-in-out whitespace-nowrap overflow-hidden ${
            isCollapsed 
              ? 'opacity-0 max-w-0 -translate-x-2 pointer-events-none' 
              : 'opacity-100 max-w-[120px] translate-x-0'
          }`}>
            <span className="font-bold text-[13px] text-slate-900 dark:text-zinc-100 tracking-tight leading-tight truncate">
              Air Pollution
            </span>
            <span className="text-[10px] text-slate-400 dark:text-zinc-400 truncate font-medium">
              CTDI Studio
            </span>
          </div>
        </div>

        {/* Right Action Icons (Search & Collapse) - Smoothly collapses width & fades */}
        <div className={`flex items-center gap-0.5 shrink-0 transition-all duration-300 ease-in-out whitespace-nowrap overflow-hidden ${
          isCollapsed
            ? 'opacity-0 max-w-0 scale-90 pointer-events-none'
            : 'opacity-100 max-w-[80px] scale-100'
        }`}>
          <button
            type="button"
            onClick={onOpenSearch}
            title="Search dataset, stations, channels, and views (Ctrl+K)"
            aria-label="Search"
            tabIndex={isCollapsed ? -1 : 0}
            className="p-1.5 rounded-lg text-slate-400 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-zinc-100 hover:bg-slate-100 dark:hover:bg-zinc-800/80 transition cursor-pointer"
          >
            <SearchHeaderIcon className="w-[18px] h-[18px]" />
          </button>
          <button
            type="button"
            onClick={onToggleCollapse}
            title="Collapse sidebar (Ctrl+B)"
            aria-label="Collapse sidebar"
            tabIndex={isCollapsed ? -1 : 0}
            className="p-1.5 rounded-lg text-slate-400 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-zinc-100 hover:bg-slate-100 dark:hover:bg-zinc-800/80 transition cursor-pointer"
          >
            <CollapseHeaderIcon className="w-[18px] h-[18px]" />
          </button>
        </div>
      </div>

      {/* 2. Primary Navigation Area */}
      <nav 
        aria-label="Primary Research Workflows"
        className={`flex-1 overflow-y-auto overflow-x-hidden min-h-0 ${
          isCollapsed ? 'px-3 py-1.5' : 'px-2.5 py-3 space-y-2.5'
        }`}
      >
        {NAVIGATION_GROUPS.map((group, gIdx) => (
          <div key={group.title}>
            {/* Collapsed Inter-Group Divider (Compact, equally spaced, and perfectly even) */}
            {isCollapsed && gIdx > 0 && (
              <div className="py-1 flex items-center justify-center" aria-hidden="true">
                <div className="w-5 h-px bg-slate-200/80 dark:bg-zinc-800/80" />
              </div>
            )}

            {/* Section Header (Expanded mode only) */}
            {!isCollapsed && (
              <div className={`px-2 pt-1.5 pb-1 text-[10px] font-semibold text-slate-400 dark:text-[#7F7F86] uppercase tracking-wider whitespace-nowrap overflow-hidden ${
                gIdx > 0 ? 'mt-1.5' : ''
              }`}>
                {group.title}
              </div>
            )}

            {/* Navigation Rows */}
            <div className="space-y-0.5">
              {group.items.map(item => {
              const isActive = currentTab === item.id;
              return (
                <div key={item.id} className="relative group">
                  <button
                    type="button"
                    onClick={() => onSelectTab(item.id)}
                    onMouseEnter={() => isCollapsed && setHoveredTooltip(item.label)}
                    onMouseLeave={() => isCollapsed && setHoveredTooltip(null)}
                    aria-label={item.label}
                    aria-current={isActive ? 'page' : undefined}
                    className={`w-full h-9 rounded-lg transition-colors duration-150 cursor-pointer flex items-center min-w-0 overflow-hidden ${
                      isCollapsed ? 'justify-center' : ''
                    } ${
                      isActive
                        ? 'bg-slate-200/80 dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 font-medium shadow-2xs'
                        : 'text-slate-600 dark:text-[#d4d4d8] hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-slate-100/70 dark:hover:bg-zinc-800/60'
                    }`}
                  >
                    <div className="w-9 h-9 shrink-0 flex items-center justify-center">
                      <item.Icon 
                        className={`w-5 h-5 shrink-0 transition-colors ${
                          isActive
                            ? 'text-slate-900 dark:text-zinc-100'
                            : 'text-slate-500 dark:text-[#d4d4d8] group-hover:text-slate-900 dark:group-hover:text-zinc-100'
                        }`}
                      />
                    </div>

                    <span className={`truncate text-left text-[13px] font-medium tracking-tight whitespace-nowrap transition-all duration-300 ease-in-out overflow-hidden ${
                      isCollapsed
                        ? 'opacity-0 max-w-0 w-0 p-0 m-0 -translate-x-2 pointer-events-none'
                        : 'opacity-100 max-w-[160px] translate-x-0 pl-0.5'
                    }`}>
                      {item.label}
                    </span>
                  </button>

                  {/* Accessible Floating Tooltip (Collapsed mode) */}
                  {isCollapsed && hoveredTooltip === item.label && (
                    <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-2.5 py-1 rounded-md bg-slate-900 dark:bg-zinc-800 text-white dark:text-zinc-100 text-xs font-medium whitespace-nowrap shadow-lg z-50 pointer-events-none border border-slate-700 dark:border-zinc-700 animate-in fade-in duration-100">
                      {item.label}
                    </div>
                  )}
                </div>
              );
            })}
            </div>
          </div>
        ))}
      </nav>

      {/* 3. Pinned Utility Section (Settings, Help) */}
      <div className={`border-t border-slate-200/80 dark:border-zinc-800 shrink-0 bg-slate-50/50 dark:bg-[#050505] overflow-hidden ${
        isCollapsed ? 'px-3 pt-1.5 pb-2 space-y-0.5' : 'p-2.5 space-y-1'
      }`}>
        {/* Settings Navigation Item */}
        <div className="relative group">
          <button
            type="button"
            onClick={() => onSelectTab('settings')}
            onMouseEnter={() => isCollapsed && setHoveredTooltip('Settings')}
            onMouseLeave={() => isCollapsed && setHoveredTooltip(null)}
            aria-label="Settings"
            aria-current={currentTab === 'settings' ? 'page' : undefined}
            className={`w-full h-9 rounded-lg transition-colors duration-150 cursor-pointer flex items-center min-w-0 overflow-hidden ${
              isCollapsed ? 'justify-center' : ''
            } ${
              currentTab === 'settings'
                ? 'bg-slate-200/80 dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 font-medium shadow-2xs'
                : 'text-slate-600 dark:text-[#d4d4d8] hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-slate-100/70 dark:hover:bg-zinc-800/60'
            }`}
          >
            <div className="w-9 h-9 shrink-0 flex items-center justify-center">
              <SettingsNavIcon 
                className={`w-5 h-5 shrink-0 transition-colors ${
                  currentTab === 'settings'
                    ? 'text-slate-900 dark:text-zinc-100'
                    : 'text-slate-500 dark:text-[#d4d4d8] group-hover:text-slate-800 dark:group-hover:text-zinc-100'
                }`}
              />
            </div>
            <span className={`truncate text-left text-[13px] font-medium tracking-tight whitespace-nowrap transition-all duration-300 ease-in-out overflow-hidden ${
              isCollapsed
                ? 'opacity-0 max-w-0 w-0 p-0 m-0 -translate-x-2 pointer-events-none'
                : 'opacity-100 max-w-[160px] translate-x-0 pl-0.5'
            }`}>
              Settings
            </span>
          </button>
          {isCollapsed && hoveredTooltip === 'Settings' && (
            <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-2.5 py-1 rounded-md bg-slate-900 dark:bg-zinc-800 text-white dark:text-zinc-100 text-xs font-medium whitespace-nowrap shadow-lg z-50 pointer-events-none border border-slate-700 dark:border-zinc-700 animate-in fade-in duration-100">
              Settings
            </div>
          )}
        </div>

        {/* Help & Shortcuts Trigger */}
        <div className="relative group">
          <button
            type="button"
            onClick={onOpenHelp}
            onMouseEnter={() => isCollapsed && setHoveredTooltip('Help & Shortcuts')}
            onMouseLeave={() => isCollapsed && setHoveredTooltip(null)}
            aria-label="Help & Keyboard Shortcuts"
            className={`w-full h-9 rounded-lg transition-colors duration-150 cursor-pointer flex items-center min-w-0 text-slate-600 dark:text-[#d4d4d8] hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-slate-100/70 dark:hover:bg-zinc-800/60 overflow-hidden ${
              isCollapsed ? 'justify-center' : ''
            }`}
          >
            <div className="w-9 h-9 shrink-0 flex items-center justify-center">
              <HelpNavIcon className="w-5 h-5 shrink-0 text-slate-500 dark:text-[#d4d4d8] group-hover:text-slate-800 dark:group-hover:text-zinc-100" />
            </div>
            <span className={`truncate text-left text-[13px] font-medium tracking-tight whitespace-nowrap transition-all duration-300 ease-in-out overflow-hidden ${
              isCollapsed
                ? 'opacity-0 max-w-0 w-0 p-0 m-0 -translate-x-2 pointer-events-none'
                : 'opacity-100 max-w-[160px] translate-x-0 pl-0.5'
            }`}>
              Help & Shortcuts
            </span>
          </button>
          {isCollapsed && hoveredTooltip === 'Help & Shortcuts' && (
            <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-2.5 py-1 rounded-md bg-slate-900 dark:bg-zinc-800 text-white dark:text-zinc-100 text-xs font-medium whitespace-nowrap shadow-lg z-50 pointer-events-none border border-slate-700 dark:border-zinc-700 animate-in fade-in duration-100">
              Help & Shortcuts
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
