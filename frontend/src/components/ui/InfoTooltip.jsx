import React, { useState, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import ProjectIcon from './ProjectIcon';
import { getTerminology } from '../../constants/terminology';

/**
 * Enterprise-grade, portal-rendered scientific information tooltip & popover.
 * 
 * Key Highlights:
 * - Rendered via createPortal(..., document.body) to escape parent clipping & overflow
 * - position: fixed with z-[99999] so it NEVER lies under navbar or other layers
 * - Instant hover response (0ms delay) with smooth leave grace period
 * - Dynamic viewport collision detection (flips below if near navbar or screen top)
 * - Automatic horizontal screen clamping (never cut off on left or right edges)
 * - Pixel-perfect arrow indicator pointing directly to trigger icon
 * - Theme-matched styling for both Light and Dark modes
 */
export default function InfoTooltip({
  term,
  title,
  description,
  interpretation,
  unit,
  caveat,
  size = 'xs',
  placement = 'auto',
  className = ''
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [coords, setCoords] = useState({
    top: 0,
    left: 0,
    width: 290,
    showBelow: true,
    arrowLeft: 145
  });

  const triggerRef = useRef(null);
  const closeTimeoutRef = useRef(null);

  // Retrieve term info from dictionary or fallback to props
  const def = term ? getTerminology(term) : null;
  const displayTitle = title || def?.name || term || 'Information';
  const displayTerm = def?.term || term || '';
  const displayDesc = description || def?.short || '';
  const displayInterp = interpretation !== undefined ? interpretation : def?.interpretation;
  const displayUnit = unit !== undefined ? unit : def?.unit;
  const displayCaveat = caveat !== undefined ? caveat : def?.caveat;

  const updatePosition = useCallback(() => {
    if (!triggerRef.current) return;
    const rect = triggerRef.current.getBoundingClientRect();
    const tooltipWidth = Math.min(300, window.innerWidth - 32);

    // Smart vertical placement:
    // If rect.top < 230 (e.g. inside top KPI row below 64px navbar), ALWAYS show below
    // Otherwise, respect placement or default to top if plenty of headroom
    const showBelow = placement === 'bottom' || (placement === 'auto' && rect.top < 230) || (placement === 'top' && rect.top < 200);

    let top = 0;
    if (showBelow) {
      top = rect.bottom + 8;
    } else {
      top = rect.top - 8;
    }

    // Horizontal centering with viewport boundary clamping
    const idealLeft = rect.left + rect.width / 2 - tooltipWidth / 2;
    const left = Math.max(16, Math.min(idealLeft, window.innerWidth - tooltipWidth - 16));

    // Calculate indicator arrow position relative to tooltip box
    const arrowLeft = Math.max(14, Math.min(rect.left + rect.width / 2 - left, tooltipWidth - 14));

    setCoords({
      top,
      left,
      width: tooltipWidth,
      showBelow,
      arrowLeft
    });
  }, [placement]);

  const handleOpen = () => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }
    updatePosition();
    setIsOpen(true);
  };

  const handleClose = () => {
    closeTimeoutRef.current = setTimeout(() => {
      setIsOpen(false);
    }, 120);
  };

  const handleCancelClose = () => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }
  };

  const handleToggle = (e) => {
    e.stopPropagation();
    if (isOpen) {
      setIsOpen(false);
    } else {
      handleOpen();
    }
  };

  // Track scroll and resize while open
  useEffect(() => {
    if (!isOpen) return;
    updatePosition();

    const handleScrollOrResize = () => {
      updatePosition();
    };

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    const handleClickOutside = (e) => {
      if (triggerRef.current && !triggerRef.current.contains(e.target)) {
        // Also check if clicked inside tooltip card
        const tooltipEl = document.getElementById('info-tooltip-portal-card');
        if (tooltipEl && tooltipEl.contains(e.target)) return;
        setIsOpen(false);
      }
    };

    window.addEventListener('scroll', handleScrollOrResize, true);
    window.addEventListener('resize', handleScrollOrResize);
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);

    return () => {
      window.removeEventListener('scroll', handleScrollOrResize, true);
      window.removeEventListener('resize', handleScrollOrResize);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, [isOpen, updatePosition]);

  return (
    <>
      {/* Interactive Trigger Button */}
      <span 
        className={`inline-flex items-center align-middle shrink-0 ${className}`}
        ref={triggerRef}
        onMouseEnter={handleOpen}
        onMouseLeave={handleClose}
      >
        <button
          type="button"
          onClick={handleToggle}
          aria-label={`Information: ${displayTitle}`}
          aria-expanded={isOpen}
          className="w-5 h-5 rounded-full inline-flex items-center justify-center text-slate-400 dark:text-zinc-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50/80 dark:hover:bg-zinc-800 transition cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 shrink-0"
        >
          <ProjectIcon name="info" size={size === 'sm' ? 14 : 12} />
        </button>
      </span>

      {/* Fixed Portal Tooltip Box (Rendered into document.body to never get clipped) */}
      {isOpen && typeof document !== 'undefined' && createPortal(
        <div
          id="info-tooltip-portal-card"
          role="tooltip"
          onMouseEnter={handleCancelClose}
          onMouseLeave={handleClose}
          style={{
            position: 'fixed',
            top: `${coords.top}px`,
            left: `${coords.left}px`,
            width: `${coords.width}px`,
            transform: coords.showBelow ? 'none' : 'translateY(-100%)',
            zIndex: 99999
          }}
          className="bg-white dark:bg-zinc-900 text-slate-900 dark:text-zinc-100 p-3.5 rounded-2xl border border-slate-200/90 dark:border-zinc-700/80 shadow-2xl shadow-slate-900/15 dark:shadow-black/70 text-left pointer-events-auto transition-opacity duration-150 animate-in fade-in zoom-in-95"
        >
          {/* Indicator Arrow */}
          <div
            style={{
              left: `${coords.arrowLeft}px`,
              top: coords.showBelow ? '-5px' : 'auto',
              bottom: coords.showBelow ? 'auto' : '-5px'
            }}
            className={`absolute w-2.5 h-2.5 rotate-45 -translate-x-1/2 bg-white dark:bg-zinc-900 ${
              coords.showBelow
                ? 'border-t border-l border-slate-200/90 dark:border-zinc-700/80'
                : 'border-b border-r border-slate-200/90 dark:border-zinc-700/80'
            }`}
          />

          {/* Header Row */}
          <div className="flex items-center justify-between gap-2 border-b border-slate-100 dark:border-zinc-800 pb-2 mb-2">
            <div className="flex items-center gap-1.5 min-w-0">
              <div className="p-1 rounded-md bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 shrink-0">
                <ProjectIcon name="info" size={12} />
              </div>
              <span className="font-bold text-xs text-slate-900 dark:text-zinc-100 truncate">
                {displayTitle}
              </span>
            </div>
            {displayTerm && (
              <span className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-zinc-800 text-[10px] font-mono text-slate-600 dark:text-zinc-300 font-bold uppercase shrink-0">
                {displayTerm}
              </span>
            )}
          </div>

          {/* Detailed Description */}
          <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed font-normal">
            {displayDesc}
          </p>

          {/* Scientific Interpretation Guidance */}
          {displayInterp && (
            <div className="mt-2.5 p-2 rounded-xl bg-emerald-50/80 dark:bg-emerald-950/40 border border-emerald-200/70 dark:border-emerald-800/60 text-[11px] text-emerald-900 dark:text-emerald-200 flex items-start gap-1.5 leading-snug">
              <span className="font-bold shrink-0 text-emerald-700 dark:text-emerald-400">Guidance:</span>
              <span>{displayInterp}</span>
            </div>
          )}

          {/* Physical Unit */}
          {displayUnit && (
            <div className="mt-2 pt-1.5 border-t border-slate-100/80 dark:border-zinc-800/80 flex items-center justify-between text-[10px] text-slate-400 dark:text-zinc-500 font-mono">
              <span>Standard Unit:</span>
              <span className="font-semibold text-slate-700 dark:text-zinc-200">{displayUnit}</span>
            </div>
          )}

          {/* Scientific Caveat / Outlier Notice */}
          {displayCaveat && (
            <div className="mt-2 p-2 rounded-xl bg-amber-50/80 dark:bg-amber-950/40 border border-amber-200/70 dark:border-amber-800/60 text-[10px] text-amber-900 dark:text-amber-200 leading-normal">
              <strong className="text-amber-700 dark:text-amber-400">Note:</strong> {displayCaveat}
            </div>
          )}
        </div>,
        document.body
      )}
    </>
  );
}
