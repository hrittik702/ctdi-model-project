import React, { useState } from 'react';
import { Card, Chip, Button } from '@heroui/react';
import { MapPin, CheckCircle, Navigation, Wind } from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';
import ChartWidget from '../components/ChartWidget';
import ProjectIcon from '../components/ui/ProjectIcon';
import InfoTooltip from '../components/ui/InfoTooltip';

export default function StationAnalysisView({ 
  metadata, 
  stations = [],
  selectedStation = 'Delhi',
  onSelectStation,
  sampleIdx, 
  pollutantMetrics = {},
  isDark = false,
  gridStroke,
  axisStroke
}) {
  const [stationSearch, setStationSearch] = useState('');
  const stationName = metadata?.station || selectedStation || 'Delhi';
  const stateName = metadata?.state || 'Delhi';
  const pollutants = metadata?.pollutants || ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3'];
  const totalSamples = metadata?.num_samples || 1500;
  const evalPoints = metadata?.total_eval_points || 54084;
  const missingRate = metadata?.missing_rate_percent || 30.0;
  const isModelTrained = metadata?.model_trained ?? (stationName.toLowerCase() === 'delhi');

  const pollutantGuidelines = {
    'PM2.5': { unit: 'µg/m³', desc: 'Fine Particulate Matter (≤2.5µm)', threshold: '60 µg/m³ (NAAQS 24h)' },
    'PM10': { unit: 'µg/m³', desc: 'Inhalable Particulate Matter (≤10µm)', threshold: '100 µg/m³ (NAAQS 24h)' },
    'NO2': { unit: 'µg/m³', desc: 'Nitrogen Dioxide (combustion & traffic)', threshold: '80 µg/m³ (NAAQS 24h)' },
    'SO2': { unit: 'µg/m³', desc: 'Sulfur Dioxide (industrial emissions)', threshold: '80 µg/m³ (NAAQS 24h)' },
    'O3': { unit: 'µg/m³', desc: 'Ground-level Ozone (photochemical)', threshold: '100 µg/m³ (NAAQS 8h)' }
  };

  const chartData = pollutants.map(pol => {
    const p = pollutantMetrics[pol];
    return {
      pollutant: pol,
      reduction: p?.reduction_mae_pct ?? 0,
      ctdi_mae: p?.ctdi_mae ?? 0,
      linear_mae: p?.linear_mae ?? 0,
      hidden_points: p?.hidden_points ?? 0
    };
  });

  const filteredStations = stations.filter(s => 
    s.name.toLowerCase().includes(stationSearch.toLowerCase()) ||
    s.state.toLowerCase().includes(stationSearch.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* 1. Indian Monitoring Stations Network Selector */}
      <Card className="bg-white dark:bg-zinc-900/90 p-5 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-xs space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-zinc-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-orange-50 dark:bg-orange-950/60 text-orange-600 flex items-center justify-center font-bold">
              <MapPin className="w-4 h-4" />
            </div>
            <div>
              <h4 className="font-extrabold text-slate-900 dark:text-zinc-100 text-sm tracking-tight">
                Indian National Air Quality Network (CPCB)
              </h4>
              <p className="text-[11px] text-slate-400 dark:text-zinc-500">
                29 continuous hourly monitoring stations across India • Select a station to view telemetry profile
              </p>
            </div>
          </div>
          <div className="w-full sm:w-64">
            <input
              type="text"
              placeholder="Search Indian city or state..."
              value={stationSearch}
              onChange={(e) => setStationSearch(e.target.value)}
              className="w-full px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-zinc-800 border border-slate-200/70 dark:border-zinc-700 text-xs text-slate-800 dark:text-zinc-200 outline-none focus:border-indigo-500 transition"
            />
          </div>
        </div>

        {/* Station Selection Chips Grid */}
        <div className="flex flex-wrap gap-2 max-h-36 overflow-y-auto py-1 pr-1">
          {filteredStations.map(stn => {
            const isSelected = stn.id.toLowerCase() === stationName.toLowerCase();
            return (
              <button
                key={stn.id}
                type="button"
                onClick={() => onSelectStation && onSelectStation(stn.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer border ${
                  isSelected
                    ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs'
                    : 'bg-slate-50 dark:bg-zinc-800/80 text-slate-700 dark:text-zinc-300 border-slate-200/70 dark:border-zinc-700/60 hover:bg-slate-100 dark:hover:bg-zinc-700'
                }`}
              >
                <span>{stn.name}</span>
                <span className={`text-[10px] ${isSelected ? 'text-indigo-200' : 'text-slate-400 dark:text-zinc-500'}`}>
                  ({stn.state})
                </span>
                {stn.model_trained && (
                  <span className={`w-2 h-2 rounded-full ${isSelected ? 'bg-emerald-300' : 'bg-emerald-500'}`} title="Trained Model Active" />
                )}
              </button>
            );
          })}
        </div>
      </Card>

      {/* 2. Active Station Profile Card */}
      <Card className="bg-white dark:bg-zinc-900/90 p-6 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 dark:border-zinc-800 pb-4">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 flex items-center justify-center font-bold">
              <ProjectIcon name="station" size="2xl" className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-extrabold text-slate-900 dark:text-zinc-100 text-lg sm:text-xl tracking-tight">
                  {stationName} Monitoring Station
                </h3>
                <Chip color={isModelTrained ? "success" : "default"} variant="soft" size="sm">
                  <Chip.Label>{isModelTrained ? "Active Benchmark Site" : "CPCB Continuous Station"}</Chip.Label>
                </Chip>
              </div>
              <p className="text-xs text-slate-400 dark:text-zinc-500 mt-0.5">
                {metadata?.dataset || 'Indian National Air Quality Dataset (CPCB)'} • State: <strong className="text-slate-700 dark:text-zinc-300">{stateName}</strong>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <div className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-zinc-800 border border-slate-200/60 dark:border-zinc-700/60">
              <span className="text-slate-400 dark:text-zinc-500 mr-1.5">Coordinates:</span>
              <strong className="text-slate-800 dark:text-zinc-200 font-mono">
                {metadata?.coordinates?.latitude ?? 28.6139}° N, {metadata?.coordinates?.longitude ?? 77.2090}° E
              </strong>
            </div>
            <div className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-zinc-800 border border-slate-200/60 dark:border-zinc-700/60">
              <span className="text-slate-400 dark:text-zinc-500 mr-1.5">Elevation:</span>
              <strong className="text-slate-800 dark:text-zinc-200 font-mono">
                {metadata?.coordinates?.elevation_m ?? 216} m
              </strong>
            </div>
          </div>
        </div>

        {/* Station Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs pt-2">
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 dark:text-zinc-500 font-medium">Test Window Sequences</span>
              <InfoTooltip term="24-Hour Window" />
            </div>
            <div className="text-xl font-extrabold text-slate-900 dark:text-zinc-100 font-mono">{totalSamples} Windows</div>
            <span className="text-[11px] text-slate-400">24-hour continuous blocks</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 dark:text-zinc-500 font-medium">Sensor Channels</span>
              <ProjectIcon name="multi-pollutant" size="sm" className="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div className="text-xl font-extrabold text-slate-900 dark:text-zinc-100 font-mono">{pollutants.length} Pollutants</div>
            <span className="text-[11px] text-slate-400">Continuous hourly telemetry</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 dark:text-zinc-500 font-medium">Evaluation Mask Rate</span>
              <InfoTooltip term="Missing Rate" />
            </div>
            <div className="text-xl font-extrabold text-slate-900 dark:text-zinc-100 font-mono">{missingRate}% Missing</div>
            <span className="text-[11px] text-slate-400">{evalPoints.toLocaleString()} hidden test points</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 dark:text-zinc-500 font-medium">Evaluation Integrity</span>
              <InfoTooltip term="Hidden Target" />
            </div>
            <div className="text-xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono">Hidden Only</div>
            <span className="text-[11px] text-slate-400">Chronological train/test split</span>
          </div>
        </div>
      </Card>

      {/* 3. Cross-Pollutant Model Gain Chart */}
      <ChartWidget
        title={`Cross-Pollutant Evaluation: ${stationName}`}
        subtitle={`Benchmark error performance across all ${evalPoints.toLocaleString()} hidden test points`}
        data={chartData}
        isDark={isDark}
        height="h-64"
        badges={[
          { label: 'Baseline: Linear Interp', variant: 'secondary' },
          { label: 'Scope: Artificially Masked Only', color: 'success' }
        ]}
      >
        {({ showGrid }) => (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 15, right: 30, left: 10, bottom: 10 }}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />}
              <XAxis dataKey="pollutant" stroke={axisStroke} fontSize={12} tickLine={false} />
              <YAxis stroke={axisStroke} fontSize={12} tickLine={false} unit=" µg/m³" />
              <Tooltip
                contentStyle={{
                  backgroundColor: isDark ? '#18181b' : '#ffffff',
                  borderColor: isDark ? '#27272a' : '#e2e8f0',
                  borderRadius: '12px',
                  fontSize: '12px'
                }}
              />
              <Bar dataKey="ctdi_mae" fill="#10b981" radius={[6, 6, 0, 0]} name="CTDI Transformer MAE" />
              <Bar dataKey="linear_mae" fill="#f59e0b" radius={[6, 6, 0, 0]} name="Linear Baseline MAE" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </ChartWidget>

      {/* 4. Monitored Sensor Channels Table */}
      <Card className="bg-white dark:bg-zinc-900/90 p-6 rounded-2xl border border-slate-200/80 dark:border-zinc-800 shadow-xs space-y-4">
        <div>
          <h4 className="font-bold text-slate-900 dark:text-zinc-100 text-base">
            Indian CPCB Criteria Pollutants & National Standards (NAAQS)
          </h4>
          <p className="text-xs text-slate-400 dark:text-zinc-500 mt-0.5">
            Real test-set evaluation scores calculated across {totalSamples} test sequences (strictly at hidden ground-truth positions).
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-zinc-800 text-slate-400 dark:text-zinc-500 font-bold uppercase">
                <th className="py-3 px-3">Pollutant</th>
                <th className="py-3 px-3">Description</th>
                <th className="py-3 px-3">India NAAQS Standard</th>
                <th className="py-3 px-3">
                  <div className="flex items-center gap-1">
                    <span>Linear Baseline MAE</span>
                    <InfoTooltip term="Linear Interpolation" />
                  </div>
                </th>
                <th className="py-3 px-3">
                  <div className="flex items-center gap-1">
                    <span>CTDI Transformer MAE</span>
                    <InfoTooltip term="CTDI" />
                  </div>
                </th>
                <th className="py-3 px-3">
                  <div className="flex items-center gap-1">
                    <span>Hidden Points</span>
                    <InfoTooltip term="Evaluation Points" />
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/80 font-mono">
              {pollutants.map(pol => {
                const info = pollutantGuidelines[pol] || { unit: 'µg/m³', desc: pol, threshold: 'N/A' };
                const pMetrics = pollutantMetrics[pol];
                const linMae = pMetrics?.linear_mae;
                const ctdiMae = pMetrics?.ctdi_mae;
                const hiddenPts = pMetrics?.hidden_points;

                return (
                  <tr key={pol} className="hover:bg-slate-50/60 dark:hover:bg-zinc-800/40 transition">
                    <td className="py-3.5 px-3 font-bold text-slate-900 dark:text-zinc-100 font-sans">
                      {pol}
                    </td>
                    <td className="py-3.5 px-3 text-slate-600 dark:text-zinc-400 font-sans">
                      {info.desc}
                    </td>
                    <td className="py-3.5 px-3 text-slate-500 dark:text-zinc-400">
                      {info.threshold}
                    </td>
                    <td className="py-3.5 px-3 text-amber-600 dark:text-amber-400 font-bold">
                      {linMae !== undefined ? `${linMae.toFixed(2)} ${info.unit}` : 'Unavailable'}
                    </td>
                    <td className="py-3.5 px-3 text-emerald-600 dark:text-emerald-400 font-bold">
                      {ctdiMae !== undefined ? `${ctdiMae.toFixed(2)} ${info.unit}` : 'Unavailable'}
                    </td>
                    <td className="py-3.5 px-3 text-slate-500 dark:text-zinc-400">
                      {hiddenPts !== undefined ? hiddenPts.toLocaleString() : 'N/A'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
