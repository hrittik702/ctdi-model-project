import React, { useState, useRef, useEffect, useMemo } from 'react';
import { 
  MapPin, 
  ChevronDown, 
  Search, 
  Check, 
  X,
  Compass,
  Radio
} from 'lucide-react';

/**
 * Custom Hong Kong EPD Station Selector Dropdown
 * 
 * Provides an accessible, studio-styled station selector matching
 * the CTDI dark/light design system with quick search, category filtering
 * (General vs. Roadside), district context, and full keyboard navigation.
 */
export default function StationSelector({
  currentStation = 'CW',
  stations = [],
  onSelectStation,
  className = ''
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL'); // 'ALL' | 'General' | 'Roadside'
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  const containerRef = useRef(null);
  const triggerRef = useRef(null);
  const searchInputRef = useRef(null);
  const listRef = useRef(null);

  // Canonical active station object
  const activeStation = useMemo(() => {
    return stations.find(s => 
      s.id === currentStation || 
      s.code === currentStation || 
      s.name === currentStation ||
      String(s.station_id) === String(currentStation)
    ) || stations[0] || {
      name: 'Central / Western',
      code: 'CW',
      type: 'General',
      district: 'Central and Western'
    };
  }, [stations, currentStation]);

  // Filtered stations based on search query & type filter
  const filteredStations = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();
    return stations.filter(stn => {
      const matchesSearch = !q || 
        stn.name.toLowerCase().includes(q) ||
        stn.code.toLowerCase().includes(q) ||
        (stn.district && stn.district.toLowerCase().includes(q));

      const matchesType = typeFilter === 'ALL' ||
        (typeFilter === 'Roadside' ? stn.type === 'Roadside' : stn.type !== 'Roadside');

      return matchesSearch && matchesType;
    });
  }, [stations, searchQuery, typeFilter]);

  // Auto-focus search input when opened
  useEffect(() => {
    if (isOpen) {
      setHighlightedIndex(0);
      setTimeout(() => {
        if (searchInputRef.current) {
          searchInputRef.current.focus();
        }
      }, 50);
    } else {
      setSearchQuery('');
      setTypeFilter('ALL');
    }
  }, [isOpen]);

  // Handle outside click & global Escape key
  useEffect(() => {
    function handleClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    }
    function handleKeyDown(e) {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
        if (triggerRef.current) triggerRef.current.focus();
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  // Keyboard navigation within list
  const handleKeyDown = (e) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
        e.preventDefault();
        setIsOpen(true);
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex(prev => (prev + 1) % Math.max(1, filteredStations.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex(prev => (prev - 1 + filteredStations.length) % Math.max(1, filteredStations.length));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const selected = filteredStations[highlightedIndex];
      if (selected) {
        onSelectStation && onSelectStation(selected.code || selected.id);
        setIsOpen(false);
        if (triggerRef.current) triggerRef.current.focus();
      }
    }
  };

  // Short display label without parenthesized suffix for the compact pill
  const displayName = useMemo(() => {
    const raw = activeStation.name || activeStation.code || 'Central / Western';
    return raw.replace(/\s*\([^)]*\)/g, '').trim();
  }, [activeStation]);

  const handleSelect = (stn) => {
    onSelectStation && onSelectStation(stn.code || stn.id);
    setIsOpen(false);
    if (triggerRef.current) triggerRef.current.focus();
  };

  return (
    <div className={`relative ${className}`} ref={containerRef} onKeyDown={handleKeyDown}>
      {/* 1. Compact Floating Station Pill */}
      <button
        ref={triggerRef}
        type="button"
        onClick={() => setIsOpen(prev => !prev)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={`Select monitoring station. Currently selected: ${activeStation.name}`}
        title={`Selected Station: ${activeStation.name} (${activeStation.code}) · Click to switch`}
        className={`flex items-center gap-1.5 h-8 px-2.5 rounded-lg text-xs font-medium transition cursor-pointer border select-none shadow-sm shadow-black/5 dark:shadow-[0_2px_6px_rgba(0,0,0,0.45)] ${
          isOpen
            ? 'bg-slate-200/90 dark:bg-[#18181B] text-slate-900 dark:text-[#F4F4F5] border-slate-300 dark:border-white/[0.12]'
            : 'bg-white/95 dark:bg-[#111113] border-slate-200/80 dark:border-white/[0.07] text-slate-700 dark:text-[#F4F4F5] hover:bg-slate-100 dark:hover:bg-[#18181B] hover:border-slate-300 dark:hover:border-white/[0.1]'
        }`}
      >
        <MapPin className="w-3.5 h-3.5 shrink-0 text-slate-700 dark:text-[#F4F4F5]" />
        
        <span className="font-medium text-slate-800 dark:text-[#F4F4F5] truncate max-w-[125px] sm:max-w-[155px] text-xs">
          {displayName}
        </span>

        <ChevronDown className={`w-3 h-3 text-slate-400 dark:text-[#B4B4BC] shrink-0 ml-0.5 transition-transform duration-150 ${
          isOpen ? 'rotate-180 text-slate-600 dark:text-[#F4F4F5]' : ''
        }`} />
      </button>

      {/* 2. Elevated Station Dropdown Menu */}
      {isOpen && (
        <div 
          role="listbox"
          className="absolute left-0 top-full mt-2 w-76 sm:w-84 bg-white dark:bg-[#111113] border border-slate-200/90 dark:border-white/[0.08] rounded-xl shadow-2xl z-50 text-xs overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        >
          {/* Header & Search */}
          <div className="p-3 border-b border-slate-100 dark:border-white/[0.06] space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-900 dark:text-[#F4F4F5] flex items-center gap-1.5">
                <Compass className="w-3.5 h-3.5 text-slate-700 dark:text-[#F4F4F5]" />
                Hong Kong EPD Stations
              </span>
              <span className="text-[10px] text-slate-400 dark:text-[#85858F] font-mono">
                16 Verified
              </span>
            </div>

            {/* Quick Search Input */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 dark:text-[#85858F] absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Search station, code, district..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-7 py-1.5 rounded-lg bg-slate-100 dark:bg-[#18181B] border border-slate-200/70 dark:border-white/[0.07] text-xs text-slate-800 dark:text-[#F4F4F5] placeholder-slate-400 dark:placeholder-[#85858F] outline-none focus:border-slate-400 dark:focus:border-white/[0.2] transition"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:text-[#85858F] dark:hover:text-[#F4F4F5]"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>

            {/* Category Segmented Filters */}
            <div className="flex items-center gap-1 pt-0.5">
              {[
                { id: 'ALL', label: 'All (16)' },
                { id: 'General', label: 'General (13)' },
                { id: 'Roadside', label: 'Roadside (3)' }
              ].map(tab => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setTypeFilter(tab.id)}
                  className={`flex-1 py-1 text-[11px] font-medium rounded-md transition cursor-pointer text-center ${
                    typeFilter === tab.id
                      ? 'bg-slate-900 text-white dark:bg-white/[0.12] dark:text-[#F4F4F5] shadow-2xs'
                      : 'bg-slate-100 dark:bg-white/[0.04] text-slate-600 dark:text-[#B4B4BC] hover:bg-slate-200 dark:hover:bg-white/[0.07]'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Station Items List */}
          <div 
            ref={listRef}
            className="max-h-64 overflow-y-auto divide-y divide-slate-100 dark:divide-white/[0.05]"
          >
            {filteredStations.length === 0 ? (
              <div className="p-4 text-center text-slate-400 dark:text-[#85858F] text-xs">
                No stations match &ldquo;{searchQuery}&rdquo;
              </div>
            ) : (
              filteredStations.map((stn, idx) => {
                const isSelected = stn.code === activeStation.code || stn.id === activeStation.id;
                const isItemRoadside = stn.type === 'Roadside';
                const isHighlighted = idx === highlightedIndex;

                return (
                  <button
                    key={stn.code || stn.id}
                    type="button"
                    role="option"
                    aria-selected={isSelected}
                    onClick={() => handleSelect(stn)}
                    onMouseEnter={() => setHighlightedIndex(idx)}
                    className={`w-full px-3 py-2 flex items-center justify-between text-left transition cursor-pointer ${
                      isSelected
                        ? 'bg-slate-100 dark:bg-white/[0.08] text-slate-900 dark:text-[#F4F4F5]'
                        : isHighlighted
                        ? 'bg-slate-50 dark:bg-[#18181B] text-slate-900 dark:text-[#F4F4F5]'
                        : 'hover:bg-slate-50 dark:hover:bg-[#18181B]/60 text-slate-700 dark:text-[#B4B4BC]'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className={`w-2 h-2 rounded-full shrink-0 ${
                        isItemRoadside ? 'bg-amber-500' : 'bg-emerald-500'
                      }`} />
                      <div className="truncate">
                        <div className="flex items-center gap-1.5">
                          <span className="font-medium truncate text-xs text-slate-900 dark:text-[#F4F4F5]">
                            {stn.name}
                          </span>
                          <span className={`text-[10px] font-mono px-1 rounded ${
                            isSelected
                              ? 'bg-slate-200 dark:bg-white/[0.12] text-slate-800 dark:text-[#F4F4F5]'
                              : 'bg-slate-100 dark:bg-white/[0.06] text-slate-500 dark:text-[#85858F]'
                          }`}>
                            {stn.code}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-500 dark:text-[#85858F] truncate mt-0.5">
                          {stn.district} · {stn.type || 'General'}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0 ml-2">
                      {isSelected && (
                        <Check className="w-3.5 h-3.5 text-slate-900 dark:text-[#F4F4F5]" />
                      )}
                    </div>
                  </button>
                );
              })
            )}
          </div>

          {/* Footer Context Note */}
          <div className="p-2.5 bg-slate-50 dark:bg-[#0D0D0F] border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between text-[10px] text-slate-400 dark:text-[#85858F]">
            <span>26,281 windows / station</span>
            <span className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 inline-block" /> Roadside Canyons (3)
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
