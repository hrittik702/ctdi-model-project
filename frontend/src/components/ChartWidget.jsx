import React, { useState, useRef, useEffect } from 'react';
import { Chip } from '@heroui/react';
import ProjectIcon from './ui/ProjectIcon';

/**
 * Enterprise-grade scientific ChartWidget.
 * Generates publication-quality analytical figures including:
 * - Title, subtitle, dataset, station, and sample context
 * - Visual chart serialization
 * - Comprehensive color-coded legend
 * - Scientific series interpretation
 * - Metric summary (strictly on hidden values)
 * - Metadata timestamp & model provenance
 * - Informative empty state when model predictions are not yet available
 */
export default function ChartWidget({
  title,
  subtitle,
  badges = [],
  children,
  data = [],
  station = 'Central / Western',
  dataset = 'CTDI Air Pollution Training Dataset v1.0 (Hong Kong EPD)',
  sampleIdx = null,
  pollutant = null,
  metrics = null,
  isDark = false,
  className = '',
  height = 'h-96',
  allowZoom = true,
  headerControls = null,
  controlsBar = null,
  footer = null,
  isLoading = false,
  showHeader = true
}) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showGrid, setShowGrid] = useState(true);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const widgetRef = useRef(null);
  const dropdownRef = useRef(null);

  // Close fullscreen on ESC
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen]);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Check if data has actual observations or if it is completely empty
  const hasData = Array.isArray(data) && data.length > 0;
  const hasObservedValues = hasData && data.some(d => d.actual != null || d.observed != null);

  // Export full analytical publication figure (PNG)
  const handleExportAnalyticalPNG = () => {
    setDropdownOpen(false);
    if (!widgetRef.current) return;
    const svgElement = widgetRef.current.querySelector('svg.recharts-surface');
    if (!svgElement) return;

    try {
      const svgString = new XMLSerializer().serializeToString(svgElement);
      const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
      const URLObj = window.URL || window.webkitURL || window;
      const blobURL = URLObj.createObjectURL(svgBlob);
      const img = new Image();

      img.onload = () => {
        const scale = 2; // Retina 2x resolution
        const width = 1200 * scale;
        const height = 850 * scale;
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');

        // Theme colors
        const bgColor = isDark ? '#050505' : '#ffffff';
        const cardBg = isDark ? '#18181b' : '#f8fafc';
        const textColor = isDark ? '#f5f5f5' : '#0f172a';
        const subTextColor = isDark ? '#c4c4c8' : '#64748b';
        const borderColor = isDark ? '#27272a' : '#e2e8f0';
        const accentColor = '#4f46e5';

        // 1. Draw Canvas Background
        ctx.fillStyle = bgColor;
        ctx.fillRect(0, 0, width, height);

        // 2. Header Banner
        ctx.fillStyle = accentColor;
        ctx.fillRect(40 * scale, 35 * scale, 6 * scale, 32 * scale);

        ctx.fillStyle = textColor;
        ctx.font = `bold ${18 * scale}px system-ui, -apple-system, sans-serif`;
        ctx.fillText("CTDI AIR IMPUTATION STUDIO", 54 * scale, 50 * scale);

        ctx.fillStyle = subTextColor;
        ctx.font = `${11 * scale}px system-ui, -apple-system, sans-serif`;
        ctx.fillText("Hong Kong EPD Monitoring Network · 16 Stations · 13 Continuous Channels", 54 * scale, 66 * scale);

        // 3. Analytical Title & Context Bar
        ctx.fillStyle = textColor;
        ctx.font = `bold ${16 * scale}px system-ui, -apple-system, sans-serif`;
        ctx.fillText(title || "24-Hour Time-Series Analysis", 40 * scale, 100 * scale);

        ctx.fillStyle = subTextColor;
        ctx.font = `${11 * scale}px system-ui, -apple-system, sans-serif`;
        const contextStr = `${station} • ${dataset}${sampleIdx !== null ? ` • Window ${sampleIdx + 1} of 26,281` : ''}${pollutant ? ` • Channel: ${pollutant}` : ''}`;
        ctx.fillText(contextStr, 40 * scale, 118 * scale);

        // Horizontal rule
        ctx.strokeStyle = borderColor;
        ctx.lineWidth = 1 * scale;
        ctx.beginPath();
        ctx.moveTo(40 * scale, 130 * scale);
        ctx.lineTo((1200 - 40) * scale, 130 * scale);
        ctx.stroke();

        // 4. Draw Main Chart
        const chartX = 40 * scale;
        const chartY = 145 * scale;
        const chartW = (1200 - 80) * scale;
        const chartH = 460 * scale;

        // Chart Card container
        ctx.fillStyle = cardBg;
        ctx.beginPath();
        if (ctx.roundRect) {
          ctx.roundRect(chartX, chartY, chartW, chartH, 12 * scale);
        } else {
          ctx.rect(chartX, chartY, chartW, chartH);
        }
        ctx.fill();
        ctx.strokeStyle = borderColor;
        ctx.stroke();

        // Draw serialized chart SVG onto canvas
        ctx.drawImage(img, chartX + 10 * scale, chartY + 10 * scale, chartW - 20 * scale, chartH - 20 * scale);

        // 5. Scientific Legend on Canvas
        const legY = chartY + chartH + 28 * scale;
        ctx.font = `bold ${11 * scale}px system-ui, -apple-system, sans-serif`;
        
        // Observed dot
        ctx.fillStyle = '#3b82f6';
        ctx.beginPath();
        ctx.arc(45 * scale, legY, 5 * scale, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = textColor;
        ctx.fillText("Observed Measurements (Continuous)", 56 * scale, legY + 4 * scale);

        // Natural Missing circle
        ctx.strokeStyle = isDark ? '#a1a1aa' : '#64748b';
        ctx.lineWidth = 1.5 * scale;
        ctx.beginPath();
        ctx.arc(280 * scale, legY, 5 * scale, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.fillStyle = textColor;
        ctx.fillText("Natural Missing Dropout (Unobserved)", 291 * scale, legY + 4 * scale);

        // Ground Truth line
        ctx.strokeStyle = isDark ? '#e4e4e7' : '#0f172a';
        ctx.lineWidth = 2 * scale;
        ctx.beginPath();
        ctx.moveTo(520 * scale, legY);
        ctx.lineTo(545 * scale, legY);
        ctx.stroke();
        ctx.fillStyle = textColor;
        ctx.fillText("Ground Truth Trajectory", 552 * scale, legY + 4 * scale);

        // 6. Figure Metadata & Provenance Footer
        const footerY = (850 - 35) * scale;
        ctx.strokeStyle = borderColor;
        ctx.beginPath();
        ctx.moveTo(40 * scale, footerY);
        ctx.lineTo((1200 - 40) * scale, footerY);
        ctx.stroke();

        ctx.fillStyle = subTextColor;
        ctx.font = `${10 * scale}px system-ui, -apple-system, sans-serif`;
        ctx.fillText(`Generated: ${new Date().toUTCString()} • CTDI Air Pollution Dataset v1.0 • Baseline Reference`, 40 * scale, footerY + 18 * scale);

        // Download canvas as high-res PNG
        const sanitizedTitle = (title || 'CTDI_Figure').replace(/[^a-zA-Z0-9_-]/g, '_');
        const filename = `${sanitizedTitle}_${station.split(' ')[0]}_Window${sampleIdx !== null ? sampleIdx + 1 : 0}.png`;
        const a = document.createElement('a');
        a.download = filename;
        a.href = canvas.toDataURL('image/png', 1.0);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URLObj.revokeObjectURL(blobURL);
      };

      img.src = blobURL;
    } catch (err) {
      console.error('Failed to export analytical figure:', err);
    }
  };

  // Export raw tabular CSV
  const handleExportCSV = () => {
    setDropdownOpen(false);
    if (!data || data.length === 0) return;
    const headers = ['hour', 'time', 'timestamp', 'pollutant', 'unit', 'observed', 'naturalMissing', 'actual'];
    const csvRows = data.map(row => 
      [
        row.hour,
        row.time,
        row.timestamp,
        pollutant || row.pollutantName || '',
        row.unit || '',
        row.observed === null || row.observed === undefined ? '' : row.observed,
        row.naturalMissing === null || row.naturalMissing === undefined ? '' : row.naturalMissing,
        row.actual === null || row.actual === undefined ? '' : row.actual
      ].join(',')
    );
    const content = 'data:text/csv;charset=utf-8,' + encodeURIComponent([headers.join(','), ...csvRows].join('\n'));
    const a = document.createElement('a');
    a.href = content;
    a.download = `CTDI_Trajectory_${station.split(' ')[0]}_Window_${sampleIdx !== null ? sampleIdx + 1 : 0}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  // Export structured JSON
  const handleExportJSON = () => {
    setDropdownOpen(false);
    const payload = {
      figure_title: title,
      station,
      dataset,
      window_index: sampleIdx !== null ? sampleIdx + 1 : null,
      total_station_windows: 26281,
      pollutant,
      exported_at: new Date().toISOString(),
      provenance: "CTDI Air Imputation Studio v1.0 (Hong Kong EPD)",
      trajectory: data
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `CTDI_Trajectory_${station.split(' ')[0]}_Window_${sampleIdx !== null ? sampleIdx + 1 : 0}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 0.25, 2.5));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 0.25, 0.75));
  const handleResetZoom = () => setZoomLevel(1);

  return (
    <div 
      ref={widgetRef}
      className={`transition-all duration-200 ${
        isFullscreen 
          ? 'fixed inset-0 z-50 p-4 sm:p-6 bg-slate-950/80 backdrop-blur-md flex flex-col justify-center overflow-auto' 
          : 'relative'
      } ${className}`}
    >
      <div className={`bg-white dark:bg-zinc-900/95 p-5 sm:p-6 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs flex flex-col justify-between overflow-hidden ${isFullscreen ? 'h-full max-w-7xl mx-auto w-full' : ''}`}>
        {/* Layer 1: Context Header (Title, Subtitle, and Primary Actions) */}
        {showHeader && Boolean(title) && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-zinc-800/80 pb-3">
          {/* Left: Title & Context Subtitle */}
          <div className="space-y-0.5 min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="font-extrabold text-slate-900 dark:text-zinc-100 text-sm sm:text-base tracking-tight truncate">
                {title}
              </h2>
              {badges.map((b, i) => (
                <Chip 
                  key={i} 
                  color={b.color || "default"} 
                  variant={b.variant || "soft"} 
                  size="sm" 
                  className="h-5 text-[10px] font-bold shrink-0"
                >
                  <Chip.Label>{b.label}</Chip.Label>
                </Chip>
              ))}
            </div>
            {subtitle && (
              <p className="text-xs text-slate-500 dark:text-zinc-400 font-medium truncate">
                {subtitle}
              </p>
            )}
          </div>

          {/* Right: Primary Action (Export) + Tertiary Toolbars + Overflow Menu */}
          <div className="flex items-center gap-1.5 shrink-0 justify-end flex-wrap sm:flex-nowrap">
            {/* Backward-compatibility slot if headerControls provided without controlsBar */}
            {!controlsBar && headerControls}

            {/* Tertiary Controls: Zoom & Grid */}
            {allowZoom && (
              <div className="hidden md:flex items-center gap-0.5 p-0.5 rounded-lg bg-slate-100 dark:bg-zinc-800 border border-slate-200/60 dark:border-zinc-700/60">
                <button
                  type="button"
                  title="Zoom In (+)"
                  aria-label="Zoom In"
                  onClick={handleZoomIn}
                  className="p-1 rounded-md text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-white dark:hover:bg-zinc-700 transition cursor-pointer"
                >
                  <ProjectIcon name="zoom-in" size="sm" className="w-3 h-3" />
                </button>
                <button
                  type="button"
                  title="Zoom Out (-)"
                  aria-label="Zoom Out"
                  onClick={handleZoomOut}
                  className="p-1 rounded-md text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-white dark:hover:bg-zinc-700 transition cursor-pointer"
                >
                  <ProjectIcon name="zoom-out" size="sm" className="w-3 h-3" />
                </button>
                {zoomLevel !== 1 && (
                  <div className="flex items-center gap-0.5">
                    <span className="text-[10px] font-mono font-bold text-indigo-600 dark:text-indigo-400 px-1">
                      {zoomLevel.toFixed(2).replace(/\.?0+$/, '')}×
                    </span>
                    <button
                      type="button"
                      title="Reset Zoom (1:1)"
                      aria-label="Reset Zoom"
                      onClick={handleResetZoom}
                      className="p-1 rounded-md text-indigo-600 dark:text-indigo-400 hover:bg-white dark:hover:bg-zinc-700 transition cursor-pointer"
                    >
                      <ProjectIcon name="reset-zoom" size="sm" className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Grid Toggle Button */}
            <button
              type="button"
              title={showGrid ? 'Hide Gridlines' : 'Show Gridlines'}
              aria-label="Toggle Gridlines"
              onClick={() => setShowGrid(!showGrid)}
              className={`p-1.5 rounded-lg border text-xs transition cursor-pointer shrink-0 ${
                showGrid 
                  ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800' 
                  : 'bg-slate-100 dark:bg-zinc-800 text-slate-400 border-slate-200/70 dark:border-zinc-700'
              }`}
            >
              <ProjectIcon name="grid" size="sm" className="w-3.5 h-3.5" />
            </button>

            {/* Secondary Action: Export Figure Button */}
            <button
              type="button"
              title="Export Research-Grade Analytical Figure (PNG)"
              aria-label="Export Research Figure"
              onClick={handleExportAnalyticalPNG}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition shadow-2xs cursor-pointer shrink-0"
            >
              <ProjectIcon name="camera" size="sm" className="w-3.5 h-3.5 text-white shrink-0" />
              <span>Export</span>
            </button>

            {/* Fullscreen Toggle */}
            <button
              type="button"
              title={isFullscreen ? 'Exit Fullscreen (Esc)' : 'Expand Fullscreen'}
              aria-label="Toggle Fullscreen"
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-1.5 rounded-lg border border-slate-200/70 dark:border-zinc-700 bg-slate-100 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 transition cursor-pointer shrink-0"
            >
              {isFullscreen ? (
                <ProjectIcon name="minimize" size="sm" className="w-3.5 h-3.5 text-indigo-600" />
              ) : (
                <ProjectIcon name="fullscreen" size="sm" className="w-3.5 h-3.5" />
              )}
            </button>

            {/* Overflow Menu (⋯) */}
            <div className="relative shrink-0" ref={dropdownRef}>
              <button
                type="button"
                title="Additional Chart & Data Actions"
                aria-label="Additional Actions"
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="p-1.5 rounded-lg border border-slate-200/70 dark:border-zinc-700 bg-slate-100 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 transition cursor-pointer"
              >
                <ProjectIcon name="more" size="sm" className="w-3.5 h-3.5" />
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-1.5 w-56 bg-white dark:bg-zinc-900 rounded-2xl shadow-xl border border-slate-200/80 dark:border-zinc-800 p-1.5 z-40 text-xs space-y-1">
                  <div className="px-2.5 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Data & Export Options
                  </div>
                  <button
                    type="button"
                    onClick={handleExportAnalyticalPNG}
                    className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-200 transition text-left cursor-pointer"
                  >
                    <ProjectIcon name="camera" size="sm" className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                    <span>Analytical PNG Figure</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleExportCSV}
                    className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-200 transition text-left cursor-pointer"
                  >
                    <ProjectIcon name="database" size="sm" className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                    <span>Raw CSV Telemetry</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleExportJSON}
                    className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-200 transition text-left cursor-pointer"
                  >
                    <ProjectIcon name="export" size="sm" className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                    <span>Structured JSON Payload</span>
                  </button>
                  <div className="border-t border-slate-100 dark:border-zinc-800 pt-1">
                    <button
                      type="button"
                      onClick={() => {
                        handleResetZoom();
                        setShowGrid(true);
                        setDropdownOpen(false);
                      }}
                      className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-500 dark:text-zinc-400 transition text-left cursor-pointer"
                    >
                      <ProjectIcon name="refresh" size="sm" className="w-3.5 h-3.5 shrink-0" />
                      <span>Reset Chart View</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
        )}

        {/* Layer 2: Dedicated Control Bar (When passed) */}
        {controlsBar && (
          <div className={`${showHeader && Boolean(title) ? 'py-2.5' : 'pb-3'} border-b border-slate-100 dark:border-zinc-800/80`}>
            {typeof controlsBar === 'function'
              ? controlsBar({
                  showGrid,
                  setShowGrid,
                  zoomLevel,
                  handleZoomIn,
                  handleZoomOut,
                  handleResetZoom,
                  isFullscreen,
                  setIsFullscreen,
                  handleExportAnalyticalPNG,
                  handleExportCSV,
                  handleExportJSON,
                  dropdownOpen,
                  setDropdownOpen,
                  dropdownRef
                })
              : controlsBar}
          </div>
        )}

        {/* Layer 3: Main Chart Canvas Body */}
        <div className="p-0 pt-2 flex-1 w-full relative">
          {isLoading ? (
            <div className={`w-full flex flex-col items-center justify-center rounded-xl bg-slate-50/50 dark:bg-zinc-950/40 border border-slate-200/60 dark:border-zinc-800/60 p-8 text-center ${height}`}>
              <div className="w-8 h-8 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin mb-3" />
              <p className="text-xs font-semibold text-slate-700 dark:text-zinc-300">
                Fetching station sequence telemetry...
              </p>
              <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-1">
                Querying verified Hong Kong EPD dataset v1.0
              </p>
            </div>
          ) : !hasObservedValues ? (
            <div className={`w-full flex flex-col items-center justify-center rounded-xl bg-slate-50/50 dark:bg-zinc-950/40 border border-dashed border-slate-200 dark:border-zinc-800 p-8 text-center ${height}`}>
              <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-3 shadow-2xs">
                <ProjectIcon name="trajectory" size="xl" className="w-6 h-6" />
              </div>
              <h4 className="font-bold text-slate-900 dark:text-zinc-100 text-sm mb-1">
                No Trajectory Data Available
              </h4>
              <p className="text-xs text-slate-400 dark:text-zinc-500 max-w-md mb-3">
                No observations found for this window. Verify that the monitoring station was active during this 24-hour interval.
              </p>
              <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-zinc-400 font-medium">
                <span className="w-2 h-2 rounded-full bg-amber-400" />
                <span>Station: {station.split(' ')[0]} • Window {sampleIdx !== null ? sampleIdx + 1 : 1} of 26,281</span>
              </div>
            </div>
          ) : (
            <div 
              className={`w-full overflow-hidden ${isFullscreen ? 'h-full min-h-[72vh]' : height}`}
            >
              {typeof children === 'function' ? children({ showGrid, isFullscreen, zoomLevel }) : children}
            </div>
          )}
        </div>

        {/* Layer 4: Footer Legend & Observation Summary (When passed) */}
        {footer && (
          <div className="pt-2.5 border-t border-slate-100 dark:border-zinc-800/80">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
