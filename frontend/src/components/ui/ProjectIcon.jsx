import React from 'react';

/**
 * CTDI Air Imputation Studio - Unified Custom SVG Icon System
 * 
 * Consistent geometric stroke system tailored for scientific data analytics:
 * - viewBox="0 0 24 24"
 * - fill="none"
 * - stroke="currentColor" (inherits surrounding text/semantic color)
 * - strokeWidth="1.75"
 * - strokeLinecap="round" strokeLinejoin="round"
 * - flex-shrink: 0 (guarantees zero layout distortion)
 */

const SIZE_MAP = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 20,
  '2xl': 24
};

export default function ProjectIcon({
  name,
  size = 'md',
  className = '',
  strokeWidth = 1.75,
  'aria-label': ariaLabel,
  'aria-hidden': ariaHidden = ariaLabel ? false : true,
  ...props
}) {
  const pixelSize = typeof size === 'number' ? size : (SIZE_MAP[size] || 16);

  const renderPath = () => {
    switch (name) {
      // --- PROJECT & BRANDING ---
      case 'ctdi-logo':
        return (
          <>
            <path d="M4 8h8a4 4 0 0 1 4 4v0a4 4 0 0 1-4 4H4" />
            <path d="M3 12h14a4 4 0 0 0 4-4v0" />
            <circle cx="18" cy="8" r="1.5" fill="currentColor" stroke="none" />
            <circle cx="8" cy="16" r="1.5" fill="currentColor" stroke="none" />
            <path d="M7 4v4" />
            <path d="M11 16v4" />
          </>
        );

      case 'air-flow':
      case 'air-pollution':
        return (
          <>
            <path d="M3 8h11a3 3 0 1 0-3-3" />
            <path d="M2 12h16a3 3 0 1 1-3 3" />
            <path d="M4 16h8a2 2 0 1 0-2-2" />
          </>
        );

      // --- APPLICATION NAVIGATION ---
      case 'dashboard':
        return (
          <>
            <rect x="3" y="3" width="7" height="7" rx="2" />
            <rect x="14" y="3" width="7" height="7" rx="2" />
            <rect x="14" y="14" width="7" height="7" rx="2" />
            <rect x="3" y="14" width="7" height="7" rx="2" />
          </>
        );

      case 'trajectory':
      case 'time-series':
        return (
          <>
            <path d="M3 18l4-8 5 4 4-7 5 3" />
            <circle cx="3" cy="18" r="1" fill="currentColor" />
            <circle cx="7" cy="10" r="1" fill="currentColor" />
            <circle cx="12" cy="14" r="1" fill="currentColor" />
            <circle cx="16" cy="7" r="1" fill="currentColor" />
            <circle cx="21" cy="10" r="1" fill="currentColor" />
          </>
        );

      case 'multi-pollutant':
      case 'layers':
        return (
          <>
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
            <path d="M2 12l10 5 10-5" />
            <path d="M2 17l10 5 10-5" />
          </>
        );

      case 'benchmark':
      case 'scoreboard':
        return (
          <>
            <path d="M18 20V10" />
            <path d="M12 20V4" />
            <path d="M6 20v-6" />
            <path d="M3 20h18" />
          </>
        );

      case 'station':
      case 'location':
        return (
          <>
            <path d="M12 21s-7-5.5-7-11a7 7 0 0 1 14 0c0 5.5-7 11-7 11z" />
            <circle cx="12" cy="10" r="2.5" />
          </>
        );

      case 'data-explorer':
      case 'database':
        return (
          <>
            <ellipse cx="12" cy="5" rx="9" ry="3" />
            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
          </>
        );

      case 'sandbox':
      case 'live-imputation':
      case 'sparkles':
        return (
          <>
            <path d="M12 3l1.9 4.7L18.5 9.6l-3.8 3.3 1.2 5.1-3.9-2.6-3.9 2.6 1.2-5.1-3.8-3.3 4.6-1.9z" />
            <path d="M19 3l.6 1.4 1.4.6-1.4.6L19 7l-.6-1.4-1.4-.6 1.4-.6z" />
          </>
        );

      case 'experiment':
      case 'history':
        return (
          <>
            <circle cx="12" cy="12" r="9" />
            <polyline points="12 7 12 12 15 15" />
            <path d="M3 12a9 9 0 0 1 3.5-7" />
          </>
        );

      case 'model-config':
      case 'cpu':
        return (
          <>
            <rect x="5" y="5" width="14" height="14" rx="2" />
            <rect x="9" y="9" width="6" height="6" />
            <path d="M9 1v4" />
            <path d="M15 1v4" />
            <path d="M9 19v4" />
            <path d="M15 19v4" />
            <path d="M1 9h4" />
            <path d="M1 15h4" />
            <path d="M19 9h4" />
            <path d="M19 15h4" />
          </>
        );

      // --- SCIENTIFIC CONCEPTS & METRICS ---
      case 'mae':
        return (
          <>
            <path d="M5 4v16" />
            <path d="M19 4v16" />
            <path d="M9 14l3-6 3 6" />
            <path d="M10 12h4" />
          </>
        );

      case 'rmse':
        return (
          <>
            <path d="M3 14h3l3 7 4-17h8" />
            <path d="M15 9l2 3 3-4" />
          </>
        );

      case 'mape':
        return (
          <>
            <circle cx="7" cy="7" r="2.5" />
            <circle cx="17" cy="17" r="2.5" />
            <line x1="18" y1="6" x2="6" y2="18" />
          </>
        );

      case 'ground-truth':
        return (
          <>
            <circle cx="12" cy="12" r="8" />
            <circle cx="12" cy="12" r="3" fill="currentColor" />
          </>
        );

      case 'observed-points':
        return (
          <>
            <circle cx="12" cy="12" r="5" fill="currentColor" />
            <path d="M12 2v3" />
            <path d="M12 19v3" />
            <path d="M2 12h3" />
            <path d="M19 12h3" />
          </>
        );

      case 'hidden-target':
        return (
          <>
            <circle cx="12" cy="12" r="6" strokeDasharray="3 3" />
            <circle cx="12" cy="12" r="2" />
          </>
        );

      case 'transformer':
        return (
          <>
            <circle cx="6" cy="6" r="2.5" />
            <circle cx="18" cy="6" r="2.5" />
            <circle cx="12" cy="18" r="2.5" />
            <path d="M8 7.5l8 0" />
            <path d="M7 8l4 8" />
            <path d="M17 8l-4 8" />
          </>
        );

      case 'linear-interp':
        return (
          <>
            <circle cx="4" cy="18" r="2" />
            <circle cx="20" cy="6" r="2" />
            <line x1="5.5" y1="16.5" x2="18.5" y2="7.5" strokeDasharray="4 3" />
          </>
        );

      case 'knn':
        return (
          <>
            <circle cx="12" cy="12" r="7" strokeDasharray="2 2" />
            <circle cx="12" cy="12" r="2" fill="currentColor" />
            <circle cx="10" cy="8" r="1.5" />
            <circle cx="15" cy="10" r="1.5" />
            <circle cx="13" cy="15" r="1.5" />
          </>
        );

      case 'mlp':
        return (
          <>
            <circle cx="5" cy="7" r="1.5" />
            <circle cx="5" cy="17" r="1.5" />
            <circle cx="12" cy="6" r="1.5" />
            <circle cx="12" cy="12" r="1.5" />
            <circle cx="12" cy="18" r="1.5" />
            <circle cx="19" cy="12" r="1.5" />
            <line x1="6.5" y1="7" x2="10.5" y2="6" />
            <line x1="6.5" y1="7" x2="10.5" y2="12" />
            <line x1="6.5" y1="17" x2="10.5" y2="12" />
            <line x1="6.5" y1="17" x2="10.5" y2="18" />
            <line x1="13.5" y1="12" x2="17.5" y2="12" />
          </>
        );

      case 'missingness':
        return (
          <>
            <rect x="3" y="8" width="5" height="8" rx="1" fill="currentColor" />
            <rect x="10" y="8" width="4" height="8" rx="1" strokeDasharray="2 2" />
            <rect x="16" y="8" width="5" height="8" rx="1" fill="currentColor" />
          </>
        );

      // --- ACTIONS & CONTROLS ---
      case 'fullscreen':
        return (
          <>
            <polyline points="15 3 21 3 21 9" />
            <polyline points="9 21 3 21 3 15" />
            <line x1="21" y1="3" x2="14" y2="10" />
            <line x1="3" y1="21" x2="10" y2="14" />
          </>
        );

      case 'minimize':
        return (
          <>
            <polyline points="4 14 10 14 10 20" />
            <polyline points="20 10 14 10 14 4" />
            <line x1="14" y1="10" x2="21" y2="3" />
            <line x1="3" y1="21" x2="10" y2="14" />
          </>
        );

      case 'zoom-in':
        return (
          <>
            <circle cx="11" cy="11" r="7" />
            <line x1="21" y1="21" x2="16" y2="16" />
            <line x1="11" y1="8" x2="11" y2="14" />
            <line x1="8" y1="11" x2="14" y2="11" />
          </>
        );

      case 'zoom-out':
        return (
          <>
            <circle cx="11" cy="11" r="7" />
            <line x1="21" y1="21" x2="16" y2="16" />
            <line x1="8" y1="11" x2="14" y2="11" />
          </>
        );

      case 'reset-zoom':
        return (
          <>
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <polyline points="3 3 3 8 8 8" />
          </>
        );

      case 'grid':
        return (
          <>
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <line x1="3" y1="9" x2="21" y2="9" />
            <line x1="3" y1="15" x2="21" y2="15" />
            <line x1="9" y1="3" x2="9" y2="21" />
            <line x1="15" y1="3" x2="15" y2="21" />
          </>
        );

      case 'camera':
        return (
          <>
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
            <circle cx="12" cy="13" r="4" />
          </>
        );

      case 'download':
      case 'export':
        return (
          <>
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </>
        );

      case 'search':
        return (
          <>
            <circle cx="11" cy="11" r="7" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </>
        );

      case 'filter':
        return <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />;

      case 'calendar':
        return (
          <>
            <rect x="3" y="4" width="18" height="18" rx="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </>
        );

      case 'clock':
        return (
          <>
            <circle cx="12" cy="12" r="9" />
            <polyline points="12 6 12 12 16 14" />
          </>
        );

      case 'info':
        return (
          <>
            <circle cx="12" cy="12" r="9" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" strokeWidth={strokeWidth + 0.5} />
          </>
        );

      case 'warning':
        return (
          <>
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" strokeWidth={strokeWidth + 0.5} />
          </>
        );

      case 'success':
      case 'check':
        return (
          <>
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </>
        );

      case 'close':
      case 'x':
        return (
          <>
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </>
        );

      case 'more':
        return (
          <>
            <circle cx="12" cy="12" r="1.2" fill="currentColor" />
            <circle cx="12" cy="5" r="1.2" fill="currentColor" />
            <circle cx="12" cy="19" r="1.2" fill="currentColor" />
          </>
        );

      case 'chevron-left':
        return <polyline points="15 18 9 12 15 6" />;

      case 'chevron-right':
        return <polyline points="9 18 15 12 9 6" />;

      case 'sun':
        return (
          <>
            <circle cx="12" cy="12" r="5" />
            <line x1="12" y1="1" x2="12" y2="3" />
            <line x1="12" y1="21" x2="12" y2="23" />
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
            <line x1="1" y1="12" x2="3" y2="12" />
            <line x1="21" y1="12" x2="23" y2="12" />
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
          </>
        );

      case 'moon':
        return <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />;

      case 'presentation':
        return (
          <>
            <path d="M2 3h20" />
            <path d="M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3" />
            <path d="M12 16v5" />
            <path d="M8 21h8" />
          </>
        );

      case 'menu':
        return (
          <>
            <line x1="4" y1="6" x2="20" y2="6" />
            <line x1="4" y1="12" x2="20" y2="12" />
            <line x1="4" y1="18" x2="20" y2="18" />
          </>
        );

      default:
        // Default technical particle node
        return (
          <>
            <circle cx="12" cy="12" r="8" />
            <circle cx="12" cy="12" r="2" fill="currentColor" />
          </>
        );
    }
  };

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      width={pixelSize}
      height={pixelSize}
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`shrink-0 select-none ${className}`}
      aria-hidden={ariaHidden}
      aria-label={ariaLabel}
      {...props}
    >
      {renderPath()}
    </svg>
  );
}
