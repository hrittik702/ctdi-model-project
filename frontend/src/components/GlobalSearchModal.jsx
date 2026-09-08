import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  X, 
  ChevronRight, 
  Activity, 
  Layers, 
  BarChart3, 
  Sparkles, 
  MapPin, 
  Database,
  Cpu,
  History,
  CornerDownLeft
} from 'lucide-react';

export default function GlobalSearchModal({
  isOpen,
  onClose,
  onSelectPollutant,
  onSelectSample,
  onSelectTab,
  metadata
}) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);

  // Pollutants from metadata
  const pollutants = metadata?.pollutants || ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'];
  const totalSamples = metadata?.num_samples || 625;

  // Build searchable items
  const searchItems = [];

  // 1. Views
  const views = [
    { id: 'explorer', title: '24h Trajectory Explorer', category: 'Views', icon: Activity, action: () => onSelectTab('explorer') },
    { id: 'multigrid', title: 'Multi-Pollutant Small Multiples', category: 'Views', icon: Layers, action: () => onSelectTab('multigrid') },
    { id: 'scoreboard', title: 'Benchmark Evaluation Scoreboard', category: 'Views', icon: BarChart3, action: () => onSelectTab('scoreboard') },
    { id: 'sandbox', title: 'Live Imputation Workspace', category: 'Experiments', icon: Sparkles, action: () => onSelectTab('sandbox') },
    { id: 'station', title: 'Station Geographical Profile', category: 'Stations', icon: MapPin, action: () => onSelectTab('station') },
    { id: 'data_explorer', title: 'Raw Sequence Data Explorer', category: 'Datasets', icon: Database, action: () => onSelectTab('data_explorer') },
    { id: 'experiments', title: 'Benchmark Experiment History', category: 'Experiments', icon: History, action: () => onSelectTab('experiments') },
    { id: 'model_config', title: 'Model Architecture & Checkpoint', category: 'Models', icon: Cpu, action: () => onSelectTab('model_config') }
  ];
  searchItems.push(...views);

  // 2. Pollutants
  pollutants.forEach(p => {
    searchItems.push({
      id: `pollutant_${p}`,
      title: `${p} Pollutant Channel`,
      subtitle: `Switch focus channel to ${p}`,
      category: 'Pollutants',
      icon: Activity,
      action: () => {
        onSelectPollutant(p);
        onSelectTab('explorer');
      }
    });
  });

  // 3. Station
  searchItems.push({
    id: 'station_aotizhongxin',
    title: 'Aotizhongxin Monitoring Station',
    subtitle: 'Coordinates: 39.982° N, 116.397° E • Elevation: 43m',
    category: 'Stations',
    icon: MapPin,
    action: () => onSelectTab('station')
  });

  // 4. Sample Jump if query contains integer
  const parsedNum = parseInt(query.trim());
  const isNumeric = !isNaN(parsedNum) && parsedNum >= 0 && parsedNum < totalSamples;
  if (isNumeric) {
    searchItems.unshift({
      id: `sample_${parsedNum}`,
      title: `Jump to 24-Hour Sample #${parsedNum}`,
      subtitle: `Inspect continuous sequence window #${parsedNum} of ${totalSamples - 1}`,
      category: 'Samples',
      icon: Activity,
      action: () => {
        onSelectSample(parsedNum);
        onSelectTab('explorer');
      }
    });
  }

  // Filter items by query
  const q = query.toLowerCase().trim();
  const filtered = q
    ? searchItems.filter(item => 
        item.title.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q) ||
        (item.subtitle && item.subtitle.toLowerCase().includes(q))
      )
    : searchItems;

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => (prev < filtered.length - 1 ? prev + 1 : 0));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : filtered.length - 1));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filtered[selectedIndex]) {
          filtered[selectedIndex].action();
          onClose();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, filtered, selectedIndex, onClose]);

  // Reset selection on query change
  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-start justify-center pt-20 p-4 select-none"
      style={{
        backgroundColor: 'rgba(0, 0, 0, 0.55)',
        backdropFilter: 'blur(8px)'
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-white dark:bg-zinc-900 w-full max-w-xl rounded-3xl border border-slate-200/90 dark:border-zinc-800 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150 flex flex-col max-h-[80vh]">
        {/* Search Input Bar */}
        <div className="p-4 border-b border-slate-100 dark:border-zinc-800 flex items-center gap-3 shrink-0">
          <Search className="w-5 h-5 text-slate-400 dark:text-zinc-500 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search stations, pollutants, sample #, models, views..."
            className="w-full bg-transparent text-slate-900 dark:text-zinc-100 placeholder:text-slate-400 dark:placeholder:text-zinc-500 text-sm focus:outline-none"
          />
          <button
            type="button"
            onClick={onClose}
            aria-label="Close search"
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-zinc-800 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="overflow-y-auto p-2 space-y-1 flex-1">
          {filtered.length > 0 ? (
            filtered.map((item, idx) => {
              const isSelected = idx === selectedIndex;
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => {
                    item.action();
                    onClose();
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-2xl text-xs transition cursor-pointer text-left ${
                    isSelected
                      ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-900 dark:text-indigo-200 shadow-2xs font-semibold'
                      : 'text-slate-700 dark:text-zinc-300 hover:bg-slate-50 dark:hover:bg-zinc-800/60'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className={`p-2 rounded-xl ${isSelected ? 'bg-indigo-600 text-white' : 'bg-slate-100 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400'}`}>
                      <Icon className="w-4 h-4 shrink-0" />
                    </div>
                    <div className="flex flex-col min-w-0">
                      <span className="truncate font-medium">{item.title}</span>
                      {item.subtitle && (
                        <span className="text-[11px] text-slate-400 dark:text-zinc-500 truncate">
                          {item.subtitle}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0 ml-3">
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-md bg-slate-100 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400">
                      {item.category}
                    </span>
                    {isSelected && (
                      <CornerDownLeft className="w-3.5 h-3.5 text-indigo-500" />
                    )}
                  </div>
                </button>
              );
            })
          ) : (
            <div className="p-8 text-center text-xs text-slate-400 dark:text-zinc-500">
              No results found for "{query}". Try searching "PM2.5", "Aotizhongxin", or sample number like "42".
            </div>
          )}
        </div>

        {/* Command Palette Keyboard Hints Footer */}
        <div className="p-3 border-t border-slate-100 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-900/50 flex items-center justify-between text-[11px] text-slate-400 dark:text-zinc-500 shrink-0">
          <div className="flex items-center gap-3">
            <span><kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-zinc-700 font-mono text-[10px]">↑</kbd> <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-zinc-700 font-mono text-[10px]">↓</kbd> to navigate</span>
            <span><kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-zinc-700 font-mono text-[10px]">Enter</kbd> to select</span>
            <span><kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-zinc-700 font-mono text-[10px]">Esc</kbd> to close</span>
          </div>
          <span className="font-mono text-[10px]">{filtered.length} results</span>
        </div>
      </div>
    </div>
  );
}
