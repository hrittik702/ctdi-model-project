import React, { useState, useMemo } from 'react';
import { 
  ShieldCheck, 
  Target, 
  Clock, 
  MapPin, 
  Activity, 
  FileCheck,
  Zap,
  Percent
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid 
} from 'recharts';

import ChartWidget from '../components/ChartWidget';
import SectionHeading from '../components/ui/SectionHeading';
import { BENCHMARK_SCENARIOS } from '../constants/datasetContract';

/**
 * Masking family definitions and scientific scope
 */
const MASKING_FAMILIES = [
  {
    id: 'ALL',
    label: 'All Scenarios',
    shortLabel: 'All (12)',
    count: 12,
    Icon: Target,
    title: 'Comprehensive 12-Scenario Benchmark Suite',
    description: 'Evaluation protocols spanning independent stochastic dropouts, consecutive temporal bursts, and complete spatial station blackouts.',
    colorText: 'text-indigo-600 dark:text-indigo-400',
    colorBg: 'bg-indigo-50/60 dark:bg-indigo-950/40 border-indigo-200/80 dark:border-indigo-800/60'
  },
  {
    id: 'MCAR',
    label: 'MCAR Stochastic',
    shortLabel: 'MCAR (4)',
    count: 4,
    Icon: Activity,
    title: 'Missing Completely at Random (MCAR) Regimes',
    description: 'Independent random dropouts across the spatio-temporal tensor. Evaluates model robustness against random telemetry loss in wireless sensor networks.',
    colorText: 'text-blue-600 dark:text-blue-400',
    colorBg: 'bg-blue-50/60 dark:bg-blue-950/40 border-blue-200/80 dark:border-blue-800/60'
  },
  {
    id: 'Temporal Block',
    label: 'Temporal Block',
    shortLabel: 'Temporal (4)',
    count: 4,
    Icon: Clock,
    title: 'Consecutive Temporal Burst Outages',
    description: 'Contiguous multi-hour blackout windows across monitoring channels. Evaluates diurnal reconstruction and temporal continuity during sustained sensor failure.',
    colorText: 'text-rose-600 dark:text-rose-400',
    colorBg: 'bg-rose-50/60 dark:bg-rose-950/40 border-rose-200/80 dark:border-rose-800/60'
  },
  {
    id: 'Spatial Outage',
    label: 'Spatial Outage',
    shortLabel: 'Spatial (4)',
    count: 4,
    Icon: MapPin,
    title: 'Network-Wide Spatial Station Blackouts',
    description: 'Complete 24-hour blackouts of 1, 2, 4, or all 16 monitoring stations. Evaluates spatial transfer and cross-station spatial correlation across Hong Kong.',
    colorText: 'text-amber-600 dark:text-amber-400',
    colorBg: 'bg-amber-50/60 dark:bg-amber-950/40 border-amber-200/80 dark:border-amber-800/60'
  }
];

/**
 * Metric Protocol Definitions for Evaluation Metrics Display
 */
const METRIC_PROTOCOLS = [
  {
    id: 'mae',
    acronym: 'MAE',
    name: 'Mean Absolute Error',
    unit: 'µg/m³',
    icon: Activity,
    color: 'emerald',
    badgeClass: 'text-emerald-700 dark:text-emerald-300 bg-emerald-500/10 border-emerald-500/20',
    iconBg: 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-800/60',
    dotColor: 'bg-emerald-500',
    summary: 'Measures average reconstruction error in original physical units (µg/m³). Treats all error magnitudes linearly with equal weighting.',
    properties: [
      'Original physical unit interpretability',
      'Robust against isolated measurement anomalies',
      'Linear penalization across all error magnitudes'
    ]
  },
  {
    id: 'rmse',
    acronym: 'RMSE',
    name: 'Root Mean Squared Error',
    unit: 'µg/m³',
    icon: Zap,
    color: 'indigo',
    badgeClass: 'text-indigo-700 dark:text-indigo-300 bg-indigo-500/10 border-indigo-500/20',
    iconBg: 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200/60 dark:border-indigo-800/60',
    dotColor: 'bg-indigo-500',
    summary: 'Penalizes larger reconstruction errors through quadratic weighting. Highly sensitive to severe concentration deviations during peak pollution episodes.',
    properties: [
      'High sensitivity to large estimation deviations',
      'Quadratic error magnification for extreme peaks',
      'Critical for statutory health warning thresholds'
    ]
  },
  {
    id: 'mre',
    acronym: 'MRE',
    name: 'Mean Relative Error',
    unit: '%',
    icon: Percent,
    color: 'sky',
    badgeClass: 'text-sky-700 dark:text-sky-300 bg-sky-500/10 border-sky-500/20',
    iconBg: 'bg-sky-50 dark:bg-sky-950/60 text-sky-600 dark:text-sky-400 border border-sky-200/60 dark:border-sky-800/60',
    dotColor: 'bg-sky-500',
    summary: 'Expresses reconstruction error relative to reference concentrations. Ensures low-baseline trace gases (such as SO₂) receive equitable weighting.',
    properties: [
      'Scale-invariant across different trace gases',
      'Prevents high-concentration pollutants from dominating',
      'Equitable weighting for low-baseline species'
    ]
  }
];

export default function BenchmarkView({
  isDashboard = false,
  metrics = [],
  isDark = false,
  gridStroke = '#e2e8f0',
  axisStroke = '#94a3b8'
}) {
  const [selectedFamily, setSelectedFamily] = useState('ALL');
  const [selectedMetric, setSelectedMetric] = useState('both');
  const [sortKey, setSortKey] = useState('MAE (Original Units)');
  const [sortAsc, setSortAsc] = useState(true);

  // Active family object
  const activeFamily = useMemo(() => {
    return MASKING_FAMILIES.find(f => f.id === selectedFamily) || MASKING_FAMILIES[0];
  }, [selectedFamily]);

  // Filtered scenarios based on active family
  const filteredScenarios = useMemo(() => {
    if (selectedFamily === 'ALL') return BENCHMARK_SCENARIOS;
    return BENCHMARK_SCENARIOS.filter(s => s.type === selectedFamily);
  }, [selectedFamily]);

  // Grouped scenarios by family (used when 'ALL' is selected)
  const scenariosByFamily = useMemo(() => {
    const families = [
      { key: 'MCAR', label: 'MCAR Stochastic Regimes', icon: Activity, colorText: 'text-blue-600 dark:text-blue-400' },
      { key: 'Temporal Block', label: 'Temporal Block Regimes', icon: Clock, colorText: 'text-rose-600 dark:text-rose-400' },
      { key: 'Spatial Outage', label: 'Spatial Outage Regimes', icon: MapPin, colorText: 'text-amber-600 dark:text-amber-400' }
    ];
    return families.map(f => ({
      ...f,
      items: BENCHMARK_SCENARIOS.filter(s => s.type === f.key)
    }));
  }, []);

  const hasMetrics = Array.isArray(metrics) && metrics.length > 0;

  // Sorting for evaluated metrics
  const sortedMetrics = useMemo(() => {
    if (!hasMetrics) return [];
    return [...metrics].sort((a, b) => {
      const valA = parseFloat(a[sortKey]) || 0;
      const valB = parseFloat(b[sortKey]) || 0;
      return sortAsc ? valA - valB : valB - valA;
    });
  }, [metrics, sortKey, sortAsc, hasMetrics]);

  return (
    <div className="space-y-6">
      {/* Primary Section: Benchmark Suite (Standalone View Only) */}
      {!isDashboard && (
        <SectionHeading
          id="benchmark-suite"
          title="Benchmark Suite"
          shortTitle="Benchmark Suite"
          icon="benchmark"
        />
      )}

      {/* 1. Benchmark Suite Header & Objective Card */}
      <div className="bg-white dark:bg-zinc-900/95 p-5 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-zinc-800/80">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold shrink-0 border border-indigo-200/60 dark:border-indigo-800/60">
                <Target className="w-4 h-4" />
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="font-extrabold text-slate-900 dark:text-zinc-100 text-base sm:text-lg tracking-tight">
                  Air Quality Imputation Benchmark Suite
                </h2>
                <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200/70 dark:border-indigo-800/60">
                  12 Scenarios
                </span>
              </div>
            </div>
            <p className="text-xs text-slate-500 dark:text-zinc-400 pl-0 sm:pl-10.5">
              Evaluate missing air-pollution data reconstruction under controlled temporal, stochastic, and spatial missingness conditions across 16 monitoring stations.
            </p>
          </div>

          {/* Verification Badge */}
          <div className="flex items-center gap-2 shrink-0 pl-0 sm:pl-0">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-800/60 text-xs font-semibold shadow-2xs">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
              <span>12 Benchmark Masks Verified</span>
            </div>
          </div>
        </div>

        {/* 2. Benchmark Scope Overview Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-1">
          <div className="p-3 rounded-xl bg-slate-50/70 dark:bg-zinc-800/50 border border-slate-200/60 dark:border-zinc-800 flex flex-col justify-between">
            <span className="text-[10px] font-medium text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              Test Period
            </span>
            <div className="mt-1 font-mono font-bold text-xs text-slate-800 dark:text-zinc-200 truncate" title="2021-07-22 → 2021-12-31">
              07-22 → 12-31
            </div>
            <span className="text-[10px] text-slate-400 dark:text-zinc-500 mt-0.5 truncate">
              Hong Kong EPD 2021
            </span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50/70 dark:bg-zinc-800/50 border border-slate-200/60 dark:border-zinc-800 flex flex-col justify-between">
            <span className="text-[10px] font-medium text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              Test Windows
            </span>
            <div className="mt-1 font-mono font-bold text-xs text-slate-800 dark:text-zinc-200">
              62,224
            </div>
            <span className="text-[10px] text-slate-400 dark:text-zinc-500 mt-0.5 truncate">
              24-hour sequences
            </span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50/70 dark:bg-zinc-800/50 border border-slate-200/60 dark:border-zinc-800 flex flex-col justify-between">
            <span className="text-[10px] font-medium text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              Window Shape
            </span>
            <div className="mt-1 font-mono font-bold text-xs text-slate-800 dark:text-zinc-200">
              24h × 13 Ch
            </div>
            <span className="text-[10px] text-slate-400 dark:text-zinc-500 mt-0.5 truncate">
              312 values / window
            </span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50/70 dark:bg-zinc-800/50 border border-slate-200/60 dark:border-zinc-800 flex flex-col justify-between">
            <span className="text-[10px] font-medium text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              Evaluation Scope
            </span>
            <div className="mt-1 font-mono font-bold text-xs text-indigo-600 dark:text-indigo-400">
              Masked Cells Only
            </div>
            <span className="text-[10px] text-slate-400 dark:text-zinc-500 mt-0.5 truncate">
              Zero data leakage
            </span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50/70 dark:bg-zinc-800/50 border border-slate-200/60 dark:border-zinc-800 flex flex-col justify-between">
            <span className="text-[10px] font-medium text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              Missing Regimes
            </span>
            <div className="mt-1 font-mono font-bold text-xs text-slate-800 dark:text-zinc-200">
              3 Categories
            </div>
            <span className="text-[10px] text-slate-400 dark:text-zinc-500 mt-0.5 truncate">
              MCAR, Block, Outage
            </span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50/70 dark:bg-zinc-800/50 border border-slate-200/60 dark:border-zinc-800 flex flex-col justify-between">
            <span className="text-[10px] font-medium text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              Mask Integrity
            </span>
            <div className="mt-1 font-mono font-bold text-xs text-emerald-600 dark:text-emerald-400 truncate">
              SHA-256 Verified
            </div>
            <span className="text-[10px] text-slate-400 dark:text-zinc-500 mt-0.5 truncate">
              Reproducible masks
            </span>
          </div>
        </div>

        {/* 3. Category Filter Switcher & Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pt-2">
          <div className="flex items-center p-1 rounded-xl bg-slate-100 dark:bg-zinc-800/90 text-xs border border-slate-200/70 dark:border-zinc-700/60 select-none overflow-x-auto max-w-full">
            {MASKING_FAMILIES.map(family => {
              const isSelected = selectedFamily === family.id;
              return (
                <button
                  key={family.id}
                  type="button"
                  onClick={() => setSelectedFamily(family.id)}
                  className={`flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 rounded-lg font-medium transition cursor-pointer shrink-0 ${
                    isSelected
                      ? 'bg-white dark:bg-zinc-900 text-slate-900 dark:text-zinc-100 font-bold shadow-2xs'
                      : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-200'
                  }`}
                >
                  <family.Icon className={`w-3.5 h-3.5 shrink-0 ${isSelected ? family.colorText : 'text-slate-400'}`} />
                  <span className="hidden md:inline">{family.label}</span>
                  <span className="md:hidden">{family.shortLabel}</span>
                  <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded-md ${
                    isSelected 
                      ? 'bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 font-bold' 
                      : 'bg-slate-200/60 dark:bg-zinc-700/60 text-slate-500 dark:text-zinc-400'
                  }`}>
                    {family.count}
                  </span>
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-zinc-400 self-end sm:self-auto shrink-0">
            <span className="font-mono text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-zinc-800/60 border border-slate-200/60 dark:border-zinc-700/60 text-slate-500 dark:text-zinc-400">
              Evaluation Slice: (62,224, 24, 13)
            </span>
          </div>
        </div>

        {/* 4. Active Family Description Banner */}
        <div className={`px-4 py-3 rounded-xl border text-xs leading-relaxed flex items-start gap-3 transition-colors ${activeFamily.colorBg}`}>
          <activeFamily.Icon className={`w-4 h-4 shrink-0 mt-0.5 ${activeFamily.colorText}`} />
          <div className="flex-1 min-w-0">
            <div className="font-bold text-slate-900 dark:text-zinc-100 flex items-center gap-2">
              <span>{activeFamily.title}</span>
              <span className="text-[11px] font-normal text-slate-500 dark:text-zinc-400">
                ({filteredScenarios.length} {filteredScenarios.length === 1 ? 'scenario' : 'scenarios'})
              </span>
            </div>
            <p className="text-slate-600 dark:text-zinc-400 mt-0.5">
              {activeFamily.description}
            </p>
          </div>
        </div>

        {/* 5. Scenario Explorer List — Scenarios Are the Primary Content */}
        <div className="space-y-4 pt-1">
          {selectedFamily === 'ALL' ? (
            // Grouped view by family for structured scannability
            scenariosByFamily.map(familyGroup => (
              <div key={familyGroup.key} className="space-y-2">
                <div className="flex items-center gap-2 px-1 pt-2">
                  <familyGroup.icon className={`w-3.5 h-3.5 ${familyGroup.colorText}`} />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300">
                    {familyGroup.label}
                  </h3>
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-100 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400">
                    {familyGroup.items.length}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {familyGroup.items.map(sc => (
                    <ScenarioCard
                      key={sc.id}
                      scenario={sc}
                    />
                  ))}
                </div>
              </div>
            ))
          ) : (
            // Filtered single-family view
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {filteredScenarios.map(sc => (
                <ScenarioCard
                  key={sc.id}
                  scenario={sc}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 6. Real Comparative Chart (Rendered only when real model metrics are available) */}
      {hasMetrics && (
        <ChartWidget
          title="Model Benchmark Comparison: MAE vs RMSE"
          subtitle="Evaluated across all test sequence withheld targets (Lower is better)"
          data={metrics}
          isDark={isDark}
          height="h-72"
        >
          {({ showGrid }) => (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sortedMetrics} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
                {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />}
                <XAxis dataKey="Model" stroke={axisStroke} fontSize={11} interval={0} tickFormatter={val => val.replace(/_/g, ' ')} />
                <YAxis stroke={axisStroke} fontSize={11} unit=" µg/m³" />
                <Tooltip 
                  cursor={{ fill: isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.04)', rx: 4 }}
                  contentStyle={{
                    backgroundColor: isDark ? '#18181b' : '#ffffff',
                    borderColor: isDark ? '#27272a' : '#e2e8f0',
                    borderRadius: '0.75rem',
                    color: isDark ? '#f4f4f5' : '#0f172a',
                    fontSize: '11px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                {(selectedMetric === 'both' || selectedMetric === 'mae') && (
                  <Bar dataKey="MAE (Original Units)" name="MAE (µg/m³)" fill="#10b981" radius={[4, 4, 0, 0]} />
                )}
                {(selectedMetric === 'both' || selectedMetric === 'rmse') && (
                  <Bar dataKey="RMSE (Original Units)" name="RMSE (µg/m³)" fill="#6366f1" radius={[4, 4, 0, 0]} />
                )}
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartWidget>
      )}

      {/* 7. Evaluation Metrics Section */}
      <div className="bg-white dark:bg-zinc-900/95 p-5 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-100 dark:border-zinc-800/80">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold shrink-0 border border-indigo-200/60 dark:border-indigo-800/60">
              <FileCheck className="w-3.5 h-3.5" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-slate-900 dark:text-zinc-100">
                Evaluation Metrics
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400">
                Standard statistical metrics used to evaluate reconstruction fidelity against reference observations.
              </p>
            </div>
          </div>
          <span className="text-[11px] font-medium text-slate-500 dark:text-zinc-400">
            Evaluation: Masked Cells Only
          </span>
        </div>

        {/* 3 Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {METRIC_PROTOCOLS.map(m => {
            const Icon = m.icon;
            return (
              <div 
                key={m.id}
                className="p-5 rounded-2xl bg-gradient-to-b from-white to-slate-50/80 dark:from-zinc-900/90 dark:to-zinc-900/40 border border-slate-200/80 dark:border-zinc-800 shadow-2xs hover:border-slate-300 dark:hover:border-zinc-700 transition-all duration-200 flex flex-col justify-between group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 transition-transform group-hover:scale-105 ${m.iconBg}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="font-mono font-extrabold text-base tracking-tight text-slate-900 dark:text-zinc-100 block leading-tight">
                          {m.acronym}
                        </span>
                        <span className="text-[11px] font-medium text-slate-400 dark:text-zinc-500 block leading-tight">
                          {m.name}
                        </span>
                      </div>
                    </div>
                    <span className={`text-[11px] font-mono font-bold px-2 py-0.5 rounded-md border ${m.badgeClass}`}>
                      {m.unit}
                    </span>
                  </div>

                  <p className="text-xs leading-relaxed text-slate-600 dark:text-zinc-400 pt-0.5">
                    {m.summary}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-zinc-800/80 space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 block mb-1">
                    Key Characteristics
                  </span>
                  {m.properties.map((prop, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-[11px] text-slate-600 dark:text-zinc-400 leading-tight">
                      <div className={`w-1.5 h-1.5 rounded-full mt-1 shrink-0 ${m.dotColor}`} />
                      <span>{prop}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

/**
 * Clean, compact Scenario Card Component for horizontal grid presentation
 */
function ScenarioCard({ scenario }) {
  return (
    <div className="p-3.5 rounded-xl border border-slate-200/80 dark:border-zinc-800 bg-white/70 dark:bg-zinc-900/70 shadow-2xs hover:bg-white dark:hover:bg-zinc-800/60 hover:border-slate-300 dark:hover:border-zinc-700 transition-all flex flex-col justify-between space-y-2 group">
      <div className="flex items-center justify-between gap-1.5">
        <span className="font-bold text-xs sm:text-sm text-slate-900 dark:text-zinc-100 tracking-tight truncate" title={scenario.name}>
          {scenario.name}
        </span>
        <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 border border-slate-200/60 dark:border-zinc-700/60 shrink-0">
          {scenario.rate}
        </span>
      </div>

      <p className="text-[11px] text-slate-500 dark:text-zinc-400 leading-snug flex-1">
        {scenario.description}
      </p>

      <div className="flex items-center justify-between pt-1.5 border-t border-slate-100 dark:border-zinc-800/80 text-[10px] font-mono text-slate-400 dark:text-zinc-500">
        <span className="text-slate-400 dark:text-zinc-500">Slice: (24, 13)</span>
        <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
          <ShieldCheck className="w-3 h-3" />
          <span>Verified</span>
        </span>
      </div>
    </div>
  );
}
