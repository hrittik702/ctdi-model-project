import React from 'react';

/**
 * Custom line-based SVG icons matching research-oriented minimal design language.
 * Standard 24x24 viewBox, stroke-based, no background boxes, no filled containers.
 */

function SpatialNetworkIcon({ className = "w-5 h-5", ...props }) {
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
      {/* Central monitoring station pin */}
      <path d="M12 2a4.5 4.5 0 0 0-4.5 4.5c0 3.2 4.5 7.5 4.5 7.5s4.5-4.3 4.5-7.5A4.5 4.5 0 0 0 12 2z" />
      <circle cx="12" cy="6.5" r="1.5" />
      {/* Connected station network nodes */}
      <circle cx="4.5" cy="19.5" r="2" />
      <circle cx="19.5" cy="19.5" r="2" />
      <circle cx="12" cy="20" r="1.5" />
      {/* Network lattice connections */}
      <path d="M6.5 19.5h4" />
      <path d="M13.5 20h4" />
      <path d="M12 14v4.5" />
    </svg>
  );
}

function TemporalSpanIcon({ className = "w-5 h-5", ...props }) {
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
      <polyline points="12 7 12 12 15.5 14" />
      <path d="M12 2v2" />
      <path d="M12 20v2" />
      <path d="M20 12h2" />
      <path d="M2 12h2" />
    </svg>
  );
}

function FeatureChannelsIcon({ className = "w-5 h-5", ...props }) {
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

function CorpusWindowsIcon({ className = "w-5 h-5", ...props }) {
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
      {/* Primary 24h sequence window frame */}
      <rect x="3" y="7" width="13" height="14" rx="2" />
      {/* Offset sliding successor window */}
      <path d="M8 7V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-3" />
      {/* Sequence partition tracks */}
      <line x1="3" y1="12" x2="16" y2="12" />
      <line x1="8.5" y1="7" x2="8.5" y2="21" />
    </svg>
  );
}

function BenchmarkScenariosIcon({ className = "w-5 h-5", ...props }) {
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
      {/* Benchmark evaluation target with validation check */}
      <circle cx="12" cy="12" r="9" />
      <path d="M8.5 12l2.5 2.5 4.5-5" />
    </svg>
  );
}

/**
 * Authoritative 5-card dataset specification for research overview cards.
 * Represents dataset characteristics exclusively; model runtime state is decoupled.
 */
const RESEARCH_OVERVIEW_CARDS = [
  {
    id: 'spatial-network',
    title: 'Spatial Network',
    primaryValue: '16',
    primaryUnit: 'stations',
    supportingLine1: 'Hong Kong EPD',
    supportingLine2: '13 general · 3 roadside',
    Icon: SpatialNetworkIcon
  },
  {
    id: 'temporal-span',
    title: 'Temporal Span',
    primaryValue: '26,304',
    primaryUnit: 'hours',
    supportingLine1: '2019–2021',
    supportingLine2: '1,096 days · Hourly resolution',
    Icon: TemporalSpanIcon
  },
  {
    id: 'feature-channels',
    title: 'Feature Channels',
    primaryValue: '13',
    primaryUnit: 'channels',
    supportingLine1: '5 air quality · 6 meteorology',
    supportingLine2: '2 traffic context',
    Icon: FeatureChannelsIcon
  },
  {
    id: 'corpus-windows',
    title: 'Corpus Windows',
    primaryValue: '420,496',
    primaryUnit: 'windows',
    supportingLine1: '24-hour sequences',
    supportingLine2: '294k train · 62.6k val · 62.2k test',
    Icon: CorpusWindowsIcon
  },
  {
    id: 'benchmark-scenarios',
    title: 'Benchmark Scenarios',
    primaryValue: '12',
    primaryUnit: 'scenarios',
    supportingLine1: 'Synthetic missingness',
    supportingLine2: 'MCAR · Block · Station outage',
    Icon: BenchmarkScenariosIcon
  }
];

/**
 * Seamless Research Overview Information Cards.
 * Single coherent information system spanning 5 equal-height, aligned cards.
 */
export default function KpiRow() {
  return (
    <section 
      aria-label="Dataset and Research Corpus Overview"
      className="rounded-2xl border border-slate-200/80 dark:border-zinc-800 bg-slate-200/70 dark:bg-zinc-800/70 p-[1px] shadow-2xs overflow-hidden"
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-[1px] bg-slate-200/70 dark:bg-zinc-800/70">
        {RESEARCH_OVERVIEW_CARDS.map(card => (
          <div
            key={card.id}
            className="bg-white dark:bg-zinc-900/95 p-3.5 sm:p-4 flex flex-col justify-between h-full transition-colors duration-fast ease-out-subtle hover:bg-slate-50/90 dark:hover:bg-zinc-800/80"
          >
            {/* Header: Custom SVG Icon + Title on the SAME line */}
            <div className="flex items-center gap-2 min-w-0">
              <card.Icon className="w-5 h-5 text-slate-600 dark:text-[#E4E4E7] shrink-0" />
              <span className="text-[11px] font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider truncate">
                {card.title}
              </span>
            </div>

            {/* Primary Metric */}
            <div className="mt-3 flex items-baseline gap-1.5">
              <span className="text-2xl font-extrabold text-slate-900 dark:text-zinc-100 tracking-tight font-display">
                {card.primaryValue}
              </span>
              <span className="text-xs font-normal text-slate-400 dark:text-zinc-500 font-sans">
                {card.primaryUnit}
              </span>
            </div>

            {/* Supporting Context (Aligned 2-line metadata) */}
            <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-zinc-800/80 text-[11px] leading-relaxed">
              <div className="font-medium text-slate-700 dark:text-zinc-300 truncate">
                {card.supportingLine1}
              </div>
              <div className="text-slate-400 dark:text-zinc-500 truncate mt-0.5">
                {card.supportingLine2}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
