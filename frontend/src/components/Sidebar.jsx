import React from 'react';
import ProjectIcon from './ui/ProjectIcon';

export default function Sidebar({ 
  currentTab, 
  onSelectTab, 
  isCollapsed, 
  onToggleCollapse,
  backendOnline,
  modelName = 'CTDI Transformer',
  modelStatus = 'Ready',
  framework = 'PyTorch'
}) {
  const sections = [
    {
      title: 'OVERVIEW',
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: 'dashboard' }
      ]
    },
    {
      title: 'ANALYTICS',
      items: [
        { id: 'explorer', label: '24h Trajectory', icon: 'trajectory' },
        { id: 'multigrid', label: 'Multi-Pollutant Grid', icon: 'multi-pollutant' },
        { id: 'scoreboard', label: 'Benchmark Scoreboard', icon: 'benchmark' },
        { id: 'station', label: 'Station Analysis', icon: 'station' },
        { id: 'data_explorer', label: 'Data Explorer', icon: 'data-explorer' }
      ]
    },
    {
      title: 'EXPERIMENTS',
      items: [
        { id: 'comparison', label: 'Model Comparison Lab', icon: 'benchmark' },
        { id: 'sandbox', label: 'Live Imputation', icon: 'sandbox' },
        { id: 'experiments', label: 'Experiment History', icon: 'experiment' }
      ]
    },
    {
      title: 'SYSTEM',
      items: [
        { id: 'model_config', label: 'Model Configuration', icon: 'model-config' }
      ]
    }
  ];

  return (
    <aside 
      className={`h-full bg-white dark:bg-zinc-900 border-r border-slate-200/80 dark:border-zinc-800 flex flex-col transition-all duration-200 ease-in-out shrink-0 select-none z-30 min-h-0 ${
        isCollapsed 
          ? 'w-16 min-w-[64px] max-w-[64px]' 
          : 'w-60 min-w-[240px] max-w-[240px]'
      }`}
    >
      {/* Navigation Area - Starts directly below TopNavbar without redundant header */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-4 min-h-0">
        {sections.map((sec, secIdx) => (
          <div key={sec.title} className="space-y-1">
            {/* Section Header or Collapsed Divider */}
            {!isCollapsed ? (
              <div className="px-2.5 pb-1 text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider truncate">
                {sec.title}
              </div>
            ) : (
              secIdx > 0 && <div className="w-8 h-px bg-slate-200/80 dark:border-zinc-800 dark:bg-zinc-800 mx-auto my-2" />
            )}

            {sec.items.map(item => {
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => onSelectTab(item.id)}
                  title={isCollapsed ? item.label : undefined}
                  aria-label={item.label}
                  className={`transition-all duration-150 cursor-pointer ${
                    isCollapsed
                      ? `w-10 h-10 mx-auto flex items-center justify-center rounded-xl ${
                          isActive
                            ? 'bg-indigo-600 text-white shadow-xs'
                            : 'text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-slate-100 dark:hover:bg-zinc-800'
                        }`
                      : `w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold min-w-0 ${
                          isActive
                            ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs'
                            : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-slate-100/80 dark:hover:bg-zinc-800/60 font-medium'
                        }`
                  }`}
                >
                  <ProjectIcon 
                    name={item.icon} 
                    size="md"
                    className={`w-4 h-4 shrink-0 ${
                      isCollapsed && isActive 
                        ? 'text-white' 
                        : isActive 
                          ? 'text-indigo-600 dark:text-indigo-400' 
                          : 'text-slate-400 dark:text-zinc-500'
                    }`} 
                  />
                  {!isCollapsed && (
                    <span className="truncate text-left min-w-0 flex-1">
                      {item.label}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer Area: Model Status Card & Collapse Toggle - Fully visible inside viewport */}
      <div className="p-2.5 border-t border-slate-100 dark:border-zinc-800/80 shrink-0 space-y-2 bg-slate-50/50 dark:bg-zinc-900/50">
        {!isCollapsed ? (
          <div className="p-2.5 rounded-xl bg-white dark:bg-zinc-800/80 border border-slate-200/70 dark:border-zinc-700/70 text-[11px] space-y-1.5 shadow-2xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 dark:text-zinc-500 font-medium">Model Pipeline</span>
              <span className="flex items-center gap-1.5 font-bold">
                <span className={`w-1.5 h-1.5 rounded-full ${backendOnline ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
                <span className={backendOnline ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600'}>
                  {backendOnline ? modelStatus : 'Offline'}
                </span>
              </span>
            </div>
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-slate-600 dark:text-zinc-300 font-medium truncate max-w-[130px]">{modelName}</span>
              <span className="text-slate-400 font-mono text-[9px] truncate max-w-[80px]" title={framework}>{framework}</span>
            </div>
          </div>
        ) : (
          <div 
            className="w-10 h-10 mx-auto rounded-xl bg-white dark:bg-zinc-800/80 border border-slate-200/70 dark:border-zinc-700/70 flex items-center justify-center shadow-2xs"
            title={`Model Pipeline: ${backendOnline ? modelStatus : 'Offline'} (${modelName})`}
          >
            <span 
              className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} 
            />
          </div>
        )}

        {/* Dedicated Collapse / Expand Toggle Button */}
        <button
          type="button"
          onClick={onToggleCollapse}
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          aria-label={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          className={`text-slate-400 hover:text-slate-700 dark:hover:text-zinc-200 hover:bg-slate-200/60 dark:hover:bg-zinc-800 rounded-xl transition cursor-pointer ${
            isCollapsed
              ? 'w-10 h-8 mx-auto flex items-center justify-center'
              : 'w-full flex items-center justify-between px-3 py-1.5 text-xs font-medium'
          }`}
        >
          {!isCollapsed && <span>Collapse sidebar</span>}
          {isCollapsed ? <ProjectIcon name="chevron-right" size="sm" className="w-4 h-4" /> : <ProjectIcon name="chevron-left" size="sm" className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
}
