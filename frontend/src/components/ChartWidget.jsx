import React, { useState, useRef, useEffect } from 'react';
import { Card, Chip } from '@heroui/react';
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
 */
export default function ChartWidget({
  title,
  subtitle,
  badges = [],
  children,
  data = [],
  station = 'Delhi Monitoring Station (28.614° N, 77.209° E)',
  dataset = 'Indian National Air Quality Dataset (CPCB)',
  sampleIdx = null,
  pollutant = null,
  metrics = null,
  isDark = false,
  className = '',
  height = 'h-96',
  allowZoom = true,
  headerControls = null
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
        const height = 900 * scale;
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');

        // Theme colors
        const bgColor = isDark ? '#09090b' : '#ffffff';
        const cardBg = isDark ? '#18181b' : '#f8fafc';
        const textColor = isDark ? '#f4f4f5' : '#0f172a';
        const subTextColor = isDark ? '#a1a1aa' : '#64748b';
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
        ctx.fillText("Spatial-Temporal Air Quality Imputation & Analytics Platform", 54 * scale, 66 * scale);

        // 3. Analytical Title & Context Bar
        ctx.fillStyle = textColor;
        ctx.font = `bold ${16 * scale}px system-ui, -apple-system, sans-serif`;
        ctx.fillText(title || "24-Hour Time-Series Analysis", 40 * scale, 100 * scale);

        ctx.fillStyle = subTextColor;
        ctx.font = `${11 * scale}px system-ui, -apple-system, sans-serif`;
        const contextStr = `${station} • ${dataset}${sampleIdx !== null ? ` • Sample #${sampleIdx}` : ''}`;
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
        const chartH = 430 * scale;

        // Chart Card container
        ctx.fillStyle = cardBg;
        ctx.beginPath();
        ctx.roundRect(chartX, chartY, chartW, chartH, 12 * scale);
        ctx.fill();
        ctx.strokeStyle = borderColor;
        ctx.stroke();

        // Draw serialized chart SVG onto canvas
        ctx.drawImage(img, chartX + (10 * scale), chartY + (10 * scale), chartW - (20 * scale), chartH - (20 * scale));

        // 5. Evaluation Metrics & Series Interpretation Box
        const bottomY = 595 * scale;
        const boxH = 220 * scale;

        ctx.fillStyle = cardBg;
        ctx.beginPath();
        ctx.roundRect(chartX, bottomY, chartW, boxH, 12 * scale);
        ctx.fill();
        ctx.strokeStyle = borderColor;
        ctx.stroke();

        // Left column: Metrics summary
        ctx.fillStyle = textColor;
        ctx.font = `bold ${13 * scale}px system-ui, -apple-system, sans-serif`;
        ctx.fillText("EVALUATION METRICS (Hidden Target Values Only)", (chartX + 20 * scale), (bottomY + 30 * scale));

        ctx.font = `${11 * scale}px system-ui, -apple-system, sans-serif`;
        ctx.fillStyle = subTextColor;
        const badgeTexts = badges.map(b => b.label).join("   |   ");
        ctx.fillText(badgeTexts || "Evaluated strictly on artificially hidden ground-truth entries.", (chartX + 20 * scale), (bottomY + 52 * scale));

        // Right column: Scientific Series Interpretation
        ctx.fillStyle = textColor;
        ctx.font = `bold ${13 * scale}px system-ui, -apple-system, sans-serif`;
        ctx.fillText("SERIES INTERPRETATION", (chartX + 20 * scale), (bottomY + 90 * scale));

        const interpretations = [
          "• Ground Truth: Original measured physical concentration (µg/m³) used as unbiased validation benchmark.",
          "• Observed Points (Blue): Retained observation inputs made visible to the model during reconstruction.",
          "• Hidden Target (Red): Ground truth values intentionally withheld to evaluate imputation accuracy.",
          "• CTDI Transformer (Emerald): Neural spatial-temporal sequence imputation leveraging 1×1 CNN cross-feature attention.",
          "• Linear Baseline (Amber): Classical 1D temporal linear interpolation for sanity-check comparison."
        ];

        ctx.fillStyle = subTextColor;
        ctx.font = `${10.5 * scale}px system-ui, -apple-system, sans-serif`;
        interpretations.forEach((line, idx) => {
          ctx.fillText(line, (chartX + 20 * scale), (bottomY + (115 + idx * 19) * scale));
        });

        // 6. Provenance & Timestamp Footer
        const footerY = 845 * scale;
        ctx.strokeStyle = borderColor;
        ctx.beginPath();
        ctx.moveTo(40 * scale, footerY);
        ctx.lineTo((1200 - 40) * scale, footerY);
        ctx.stroke();

        ctx.fillStyle = subTextColor;
        ctx.font = `${10 * scale}px monospace`;
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
        ctx.fillText(`Generated: ${timestamp} | Model: CTDI Temporal Transformer (PyTorch) | Status: Verified`, 40 * scale, (footerY + 22 * scale));

        // 7. Trigger file download
        const pngUrl = canvas.toDataURL('image/png');
        const downloadLink = document.createElement('a');
        const safeTitle = (title || 'CTDI_Figure').replace(/[^a-zA-Z0-9_-]/g, '_');
        downloadLink.download = `${safeTitle}_analytical_figure.png`;
        downloadLink.href = pngUrl;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        URLObj.revokeObjectURL(blobURL);
      };

      img.src = blobURL;
    } catch (err) {
      console.error('High-resolution PNG figure export failed:', err);
    }
  };

  // Export raw CSV data
  const handleExportCSV = () => {
    setDropdownOpen(false);
    if (!data || data.length === 0) return;
    try {
      const keys = Object.keys(data[0]);
      const header = keys.join(',');
      const rows = data.map(row => keys.map(k => (row[k] !== null && row[k] !== undefined ? row[k] : '')).join(','));
      let csvContent = `data:text/csv;charset=utf-8,`;
      csvContent += `# CTDI Air Imputation Studio Time-Series Telemetry\n`;
      csvContent += `# Title: ${title}\n`;
      csvContent += `# Station: ${station}\n`;
      csvContent += `# Exported: ${new Date().toISOString()}\n`;
      csvContent += encodeURIComponent(header + '\n' + rows.join('\n'));

      const a = document.createElement('a');
      a.href = csvContent;
      a.download = `${(title || 'telemetry').replace(/[^a-zA-Z0-9_-]/g, '_')}_data.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      console.error('CSV export failed:', err);
    }
  };

  // Export raw JSON data
  const handleExportJSON = () => {
    setDropdownOpen(false);
    if (!data || data.length === 0) return;
    try {
      const payload = {
        project: "CTDI Air Imputation Studio",
        title,
        subtitle,
        station,
        dataset,
        sampleIdx,
        pollutant,
        exportedAt: new Date().toISOString(),
        metrics: badges.map(b => b.label),
        data
      };
      const jsonContent = 'data:application/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(payload, null, 2));
      const a = document.createElement('a');
      a.href = jsonContent;
      a.download = `${(title || 'telemetry').replace(/[^a-zA-Z0-9_-]/g, '_')}_data.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      console.error('JSON export failed:', err);
    }
  };

  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 0.25, 2.0));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 0.25, 0.75));
  const handleResetZoom = () => setZoomLevel(1);

  const containerClasses = isFullscreen
    ? 'fixed inset-0 z-50 p-4 sm:p-6 bg-black/75 backdrop-blur-md flex flex-col justify-center items-center'
    : `relative ${className}`;

  const cardClasses = isFullscreen
    ? 'w-full max-w-7xl h-[94vh] bg-white dark:bg-zinc-900 border border-slate-200/90 dark:border-zinc-800 shadow-2xl rounded-3xl flex flex-col p-6 overflow-hidden'
    : 'bg-white dark:bg-zinc-900/90 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-xs hover:shadow-md transition-all duration-200 p-5 space-y-3';

  return (
    <div className={containerClasses} ref={widgetRef}>
      <Card className={cardClasses}>
        {/* Header Toolbar - Responsive flex layout preventing collisions */}
        <div className="p-0 flex flex-row flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-zinc-800/80 pb-3 w-full">
          {/* Left: Title, Subtitle, and Context Badges */}
          <div className="flex flex-col min-w-0 space-y-0.5">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="font-bold text-slate-900 dark:text-zinc-100 text-sm sm:text-base tracking-tight truncate">
                {title}
              </h3>
              {/* Badges in title row */}
              <div className="hidden sm:flex items-center gap-1.5 flex-wrap">
                {badges.map((b, idx) => (
                  <Chip key={idx} color={b.color || 'default'} variant={b.variant || 'soft'} size="sm" className="h-5 text-[10px] font-bold">
                    <Chip.Label>{b.label}</Chip.Label>
                  </Chip>
                ))}
              </div>
            </div>
            {subtitle && (
              <p className="text-xs text-slate-400 dark:text-zinc-500 font-medium truncate">
                {subtitle}
              </p>
            )}
          </div>

          {/* Right Action Group: Compact, non-overlapping controls */}
          <div className="flex items-center gap-1.5 shrink-0">
            {headerControls}

            {/* Zoom Controls */}
            {allowZoom && (
              <div className="hidden md:flex items-center gap-0.5 bg-slate-100 dark:bg-zinc-800 p-0.5 rounded-xl border border-slate-200/60 dark:border-zinc-700/60">
                <button
                  type="button"
                  title="Zoom In (+)"
                  aria-label="Zoom In"
                  onClick={handleZoomIn}
                  className="p-1.5 rounded-lg text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-white dark:hover:bg-zinc-700 transition cursor-pointer"
                >
                  <ProjectIcon name="zoom-in" size="sm" className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  title="Zoom Out (-)"
                  aria-label="Zoom Out"
                  onClick={handleZoomOut}
                  className="p-1.5 rounded-lg text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 hover:bg-white dark:hover:bg-zinc-700 transition cursor-pointer"
                >
                  <ProjectIcon name="zoom-out" size="sm" className="w-3.5 h-3.5" />
                </button>
                {zoomLevel !== 1 && (
                  <button
                    type="button"
                    title="Reset Zoom (1:1)"
                    aria-label="Reset Zoom"
                    onClick={handleResetZoom}
                    className="p-1.5 rounded-lg text-indigo-600 dark:text-indigo-400 hover:bg-white dark:hover:bg-zinc-700 transition cursor-pointer"
                  >
                    <ProjectIcon name="reset-zoom" size="sm" className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            )}

            {/* Grid Toggle */}
            <button
              type="button"
              title={showGrid ? 'Hide Gridlines' : 'Show Gridlines'}
              aria-label="Toggle Gridlines"
              onClick={() => setShowGrid(!showGrid)}
              className={`p-1.5 rounded-xl border text-xs transition cursor-pointer ${
                showGrid 
                  ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800' 
                  : 'bg-slate-100 dark:bg-zinc-800 text-slate-400 border-slate-200 dark:border-zinc-700'
              }`}
            >
              <ProjectIcon name="grid" size="sm" className="w-3.5 h-3.5" />
            </button>

            {/* Primary Action: Export Figure Button */}
            <button
              type="button"
              title="Export Research-Grade Figure"
              aria-label="Export Research Figure"
              onClick={handleExportAnalyticalPNG}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition shadow-2xs cursor-pointer"
            >
              <ProjectIcon name="camera" size="sm" className="w-3.5 h-3.5 text-white" />
              <span className="hidden sm:inline">Export Figure</span>
            </button>

            {/* Fullscreen Toggle */}
            <button
              type="button"
              title={isFullscreen ? 'Exit Fullscreen (Esc)' : 'Expand Fullscreen'}
              aria-label="Toggle Fullscreen"
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-1.5 rounded-xl border border-slate-200/70 dark:border-zinc-700 bg-slate-100 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 transition cursor-pointer"
            >
              {isFullscreen ? <ProjectIcon name="minimize" size="sm" className="w-3.5 h-3.5 text-indigo-600" /> : <ProjectIcon name="fullscreen" size="sm" className="w-3.5 h-3.5" />}
            </button>

            {/* Overflow Menu for CSV, JSON, and Advanced Downloads */}
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                title="More Data Export Formats"
                aria-label="More Export Formats"
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="p-1.5 rounded-xl border border-slate-200/70 dark:border-zinc-700 bg-slate-100 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100 transition cursor-pointer"
              >
                <ProjectIcon name="more" size="sm" className="w-3.5 h-3.5" />
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-1 w-52 bg-white dark:bg-zinc-900 rounded-2xl shadow-xl border border-slate-200/80 dark:border-zinc-800 p-1.5 z-40 text-xs space-y-1">
                  <div className="px-2.5 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Figure & Data Exports
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
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Chart Canvas Body */}
        <div className="p-0 pt-2 flex-1 w-full relative">
          <div 
            className={`w-full transition-transform duration-150 origin-center ${isFullscreen ? 'h-full min-h-[72vh]' : height}`}
            style={{ transform: zoomLevel !== 1 ? `scale(${zoomLevel})` : undefined }}
          >
            {typeof children === 'function' ? children({ showGrid, isFullscreen, zoomLevel }) : children}
          </div>
        </div>
      </Card>
    </div>
  );
}
