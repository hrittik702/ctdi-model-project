import React, { useState, useEffect, useCallback } from 'react';

// API Service
import api from './services/api';

// Shell & Navigation Components
import Sidebar from './components/Sidebar';
import TopNavbar from './components/TopNavbar';
import KpiRow from './components/KpiRow';

// Views
import TrajectoryExplorerView from './views/TrajectoryExplorerView';
import MultiPollutantView from './views/MultiPollutantView';
import BenchmarkView from './views/BenchmarkView';
import StationAnalysisView from './views/StationAnalysisView';
import DataExplorerView from './views/DataExplorerView';
import LiveImputationView from './views/LiveImputationView';
import ExperimentHistoryView from './views/ExperimentHistoryView';

// Modals
import GlobalSearchModal from './components/GlobalSearchModal';
import ExportModal from './components/ExportModal';
import ModelConfigModal from './components/ModelConfigModal';

export default function App() {
  // Theme state: dark / light
  const [theme, setTheme] = useState(() => localStorage.getItem('ctdi_theme') || 'dark');
  const isDark = theme === 'dark';

  // Navigation & Shell state
  const [currentTab, setCurrentTab] = useState('explorer');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
    return localStorage.getItem('ctdi_sidebar_collapsed') === 'true';
  });
  const [isPresentationMode, setIsPresentationMode] = useState(false);

  // Modal dialog states
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);
  const [isModelConfigOpen, setIsModelConfigOpen] = useState(false);

  // Backend data states
  const [metadata, setMetadata] = useState(null);
  const [stations, setStations] = useState([]);
  const [selectedStation, setSelectedStation] = useState('Delhi');
  const [metrics, setMetrics] = useState([]);
  const [pollutantMetrics, setPollutantMetrics] = useState({});
  const [experiments, setExperiments] = useState([]);
  const [modelConfig, setModelConfig] = useState(null);
  const [healthInfo, setHealthInfo] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);

  // Trajectory exploration state
  const [sampleIdx, setSampleIdx] = useState(0);
  const [targetPollutant, setTargetPollutant] = useState('PM2.5');
  const [sampleData, setSampleData] = useState(null);
  const [isLoadingSample, setIsLoadingSample] = useState(false);

  // Visibility toggles for curve series
  const [visibleModels, setVisibleModels] = useState({
    groundTruth: true,
    observed: true,
    hiddenTarget: true,
    transformer: true,
    linear: true,
    knn: false,
    mlp: false
  });

  // Live simulation sandbox state
  const [liveRate, setLiveRate] = useState(0.35);
  const [liveMechanism, setLiveMechanism] = useState('random');
  const [liveSeed, setLiveSeed] = useState(42);
  const [liveResult, setLiveResult] = useState(null);
  const [liveLoading, setLiveLoading] = useState(false);
  const [liveStep, setLiveStep] = useState('');

  // Synchronize theme with documentElement
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('ctdi_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const toggleSidebar = () => {
    setIsSidebarCollapsed(prev => {
      const next = !prev;
      localStorage.setItem('ctdi_sidebar_collapsed', String(next));
      return next;
    });
  };

  // Keyboard shortcut for Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsSearchOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Poll health and fetch initial metadata & global metrics
  const loadInitialData = useCallback(async () => {
    try {
      const health = await api.getHealth();
      setHealthInfo(health);
      setBackendOnline(health.status === 'ok');

      const [stnsRes, meta, metList, polMets, exps, config] = await Promise.all([
        api.getStations(),
        api.getMetadata(selectedStation),
        api.getMetrics(),
        api.getPollutantMetrics(),
        api.getExperiments(),
        api.getModelConfig()
      ]);

      if (stnsRes?.stations) {
        setStations(stnsRes.stations);
        if (stnsRes.active_station) {
          setSelectedStation(stnsRes.active_station);
        }
      }
      setMetadata(meta);
      setMetrics(metList);
      setPollutantMetrics(polMets);
      setExperiments(exps);
      setModelConfig(config);

      if (meta.pollutants?.length > 0 && !targetPollutant) {
        setTargetPollutant(meta.pollutants[0]);
      }
    } catch (err) {
      console.warn('Initial data load failed:', err);
      setBackendOnline(false);
    }
  }, [targetPollutant, selectedStation]);

  useEffect(() => {
    loadInitialData();
    // Health polling every 10 seconds
    const interval = setInterval(async () => {
      try {
        const health = await api.getHealth();
        setBackendOnline(health.status === 'ok');
      } catch {
        setBackendOnline(false);
      }
    }, 10000);
    return () => clearInterval(interval);
  }, [loadInitialData]);

  // Handle station selection
  const handleSelectStation = async (stationName) => {
    setSelectedStation(stationName);
    try {
      await api.selectStation(stationName);
      const newMeta = await api.getMetadata(stationName);
      setMetadata(newMeta);
      const newSample = await api.getSample(sampleIdx, stationName);
      setSampleData(newSample);
    } catch (err) {
      console.warn('Failed to switch station:', err);
    }
  };

  // Fetch sample telemetry whenever sampleIdx or selectedStation changes
  useEffect(() => {
    async function fetchSample() {
      setIsLoadingSample(true);
      try {
        const data = await api.getSample(sampleIdx, selectedStation);
        setSampleData(data);
      } catch (err) {
        console.error(`Failed to fetch sample ${sampleIdx}:`, err);
      } finally {
        setIsLoadingSample(false);
      }
    }
    fetchSample();
  }, [sampleIdx, selectedStation]);

  // Execute live model inference with progress feedback
  const handleRunLiveImpute = async () => {
    setLiveLoading(true);
    setLiveStep('Preparing 24h sample tensor...');
    try {
      await new Promise(r => setTimeout(r, 120)); // Brief visual step
      setLiveStep(`Applying ${liveMechanism.toUpperCase()} corruption (${Math.round(liveRate * 100)}%)...`);
      await new Promise(r => setTimeout(r, 150));
      setLiveStep('Executing PyTorch CTDI Transformer forward pass...');
      
      const res = await api.liveImpute({
        sampleIdx,
        missingRate: liveRate,
        mechanism: liveMechanism,
        seed: liveSeed
      });

      setLiveStep('Evaluating masked metrics...');
      await new Promise(r => setTimeout(r, 100));
      setLiveResult(res);
      setLiveStep('Complete');
    } catch (err) {
      console.error('Live imputation failed:', err);
    } finally {
      setLiveLoading(false);
    }
  };

  // Build chart dataset for the active trajectory view
  const pData = sampleData?.pollutants?.[targetPollutant];
  const chartData = sampleData?.hours?.map((hour, i) => {
    const isObs = pData?.observed_mask?.[i] === 1;
    const isEval = pData?.eval_mask?.[i] === 1;
    const actualVal = pData?.actual?.[i];
    const rawTimestamp = sampleData.timestamps?.[i] || '';
    const clockTime = rawTimestamp.includes(' ') ? rawTimestamp.split(' ')[1] : hour;
    const datePart = rawTimestamp.includes(' ') ? rawTimestamp.split(' ')[0] : '';

    return {
      hour: clockTime,
      time: clockTime,
      timeIndex: i,
      stepOffset: `+${i}h`,
      date: datePart,
      timestamp: rawTimestamp,
      actual: actualVal,
      observed: isObs ? actualVal : null,
      hiddenTarget: isEval ? actualVal : null,
      transformer: pData?.transformer?.[i],
      linear: pData?.linear?.[i],
      knn: pData?.knn?.[i],
      mlp: pData?.mlp?.[i],
      mean: pData?.mean?.[i]
    };
  }) || [];

  // Theme-aware Recharts styling tokens
  const gridStroke = isDark ? '#3f3f46' : '#e2e8f0';
  const axisStroke = isDark ? '#71717a' : '#94a3b8';

  // Curve series definitions for interactive legend chips
  const curveSeries = [
    { key: 'groundTruth', label: 'Ground Truth', dotColor: isDark ? 'bg-zinc-200' : 'bg-slate-900', activeStyle: isDark ? 'bg-zinc-800 text-zinc-100 border-zinc-700' : 'bg-slate-900 text-white border-slate-900 shadow-xs' },
    { key: 'observed', label: 'Observed Points', dotColor: 'bg-blue-500', activeStyle: isDark ? 'bg-blue-950/60 text-blue-300 border-blue-800' : 'bg-blue-50 text-blue-700 border-blue-200 shadow-xs' },
    { key: 'hiddenTarget', label: 'Hidden Target', dotColor: 'bg-red-500', activeStyle: isDark ? 'bg-red-950/60 text-red-300 border-red-800' : 'bg-red-50 text-red-700 border-red-200 shadow-xs' },
    { key: 'transformer', label: 'CTDI Transformer', dotColor: 'bg-emerald-500', activeStyle: isDark ? 'bg-emerald-950/60 text-emerald-300 border-emerald-800 font-bold' : 'bg-emerald-50 text-emerald-800 border-emerald-300 font-bold shadow-xs' },
    { key: 'linear', label: 'Linear Interp', dotColor: 'bg-amber-500', activeStyle: isDark ? 'bg-amber-950/60 text-amber-300 border-amber-800' : 'bg-amber-50 text-amber-800 border-amber-300 shadow-xs' },
    { key: 'knn', label: 'KNN', dotColor: 'bg-purple-500', activeStyle: isDark ? 'bg-purple-950/60 text-purple-300 border-purple-800' : 'bg-purple-50 text-purple-700 border-purple-200' },
    { key: 'mlp', label: 'MLP', dotColor: 'bg-cyan-500', activeStyle: isDark ? 'bg-cyan-950/60 text-cyan-300 border-cyan-800' : 'bg-cyan-50 text-cyan-700 border-cyan-200' }
  ];

  // View title helper
  const viewTitles = {
    dashboard: 'Analytical Dashboard Overview',
    explorer: '24-Hour Trajectory Explorer',
    multigrid: 'Multi-Pollutant Small Multiples',
    scoreboard: 'Benchmark Evaluation Scoreboard',
    station: 'Station Geographical Profile',
    data_explorer: 'Raw Sequence Data Explorer',
    sandbox: 'Live Imputation Workspace',
    experiments: 'Benchmark Experiment History',
    model_config: 'Model Architecture & Configuration'
  };

  const handleSelectTab = (tabId) => {
    if (tabId === 'model_config') {
      setIsModelConfigOpen(true);
    } else {
      setCurrentTab(tabId);
    }
  };

  const handleDrillDownToPollutant = (pollutant) => {
    setTargetPollutant(pollutant);
    setCurrentTab('explorer');
  };

  return (
    <div className="h-screen w-screen overflow-hidden bg-slate-50 dark:bg-zinc-950 text-slate-900 dark:text-zinc-100 flex flex-col font-sans transition-colors duration-200 select-none">
      {/* Top Navigation Bar - Sticky z-20 */}
      <TopNavbar
        currentViewTitle={viewTitles[currentTab] || 'Analytics Studio'}
        currentStation={selectedStation}
        stations={stations}
        onSelectStation={handleSelectStation}
        backendOnline={backendOnline}
        theme={theme}
        onToggleTheme={toggleTheme}
        onOpenSearch={() => setIsSearchOpen(true)}
        onOpenExport={() => setIsExportOpen(true)}
        isPresentationMode={isPresentationMode}
        onTogglePresentationMode={() => setIsPresentationMode(prev => !prev)}
        onMobileMenuToggle={toggleSidebar}
      />

      {/* Main Workspace Layout (Fixed Sidebar + Independently Scrollable Viewport) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Fixed h-full z-30 */}
        {!isPresentationMode && (
          <Sidebar
            currentTab={currentTab}
            onSelectTab={handleSelectTab}
            isCollapsed={isSidebarCollapsed}
            onToggleCollapse={toggleSidebar}
            backendOnline={backendOnline}
            modelName={healthInfo?.model_name || 'CTDI Transformer'}
            modelStatus={healthInfo?.status_label || (backendOnline ? 'Ready' : 'Offline')}
          />
        )}

        {/* Main Viewport Content Area - Independently Scrollable */}
        <main className="flex-1 h-full overflow-y-auto p-4 sm:p-6 space-y-6">
          {/* Executive Dynamic KPI Row (Always backend-driven) */}
          <KpiRow
            metrics={metrics}
            metadata={metadata}
            sampleHiddenCount={pData?.hidden_count ?? null}
            totalHours={24}
            modelStatus={backendOnline ? (healthInfo?.status_label || 'Ready') : 'Offline'}
            activeModel={healthInfo?.model_name || 'CTDI Transformer'}
            targetPollutant={targetPollutant}
          />

          {/* Active View Router */}
          {currentTab === 'dashboard' && (
            <div className="space-y-6">
              <TrajectoryExplorerView
                sampleIdx={sampleIdx}
                setSampleIdx={setSampleIdx}
                maxSamples={metadata?.num_samples || 1500}
                targetPollutant={targetPollutant}
                setTargetPollutant={setTargetPollutant}
                pollutants={metadata?.pollutants || ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3']}
                sampleData={sampleData}
                chartData={chartData}
                visibleModels={visibleModels}
                setVisibleModels={setVisibleModels}
                curveSeries={curveSeries}
                isDark={isDark}
                gridStroke={gridStroke}
                axisStroke={axisStroke}
              />
              <BenchmarkView
                metrics={metrics}
                isDark={isDark}
                gridStroke={gridStroke}
                axisStroke={axisStroke}
              />
            </div>
          )}

          {currentTab === 'explorer' && (
            <TrajectoryExplorerView
              sampleIdx={sampleIdx}
              setSampleIdx={setSampleIdx}
              maxSamples={metadata?.num_samples || 1500}
              targetPollutant={targetPollutant}
              setTargetPollutant={setTargetPollutant}
              pollutants={metadata?.pollutants || ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3']}
              sampleData={sampleData}
              chartData={chartData}
              visibleModels={visibleModels}
              setVisibleModels={setVisibleModels}
              curveSeries={curveSeries}
              isDark={isDark}
              gridStroke={gridStroke}
              axisStroke={axisStroke}
            />
          )}

          {currentTab === 'multigrid' && (
            <MultiPollutantView
              sampleData={sampleData}
              pollutants={metadata?.pollutants || ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3']}
              sampleIdx={sampleIdx}
              onDrillDown={handleDrillDownToPollutant}
              isDark={isDark}
              gridStroke={gridStroke}
              axisStroke={axisStroke}
            />
          )}

          {currentTab === 'scoreboard' && (
            <BenchmarkView
              metrics={metrics}
              isDark={isDark}
              gridStroke={gridStroke}
              axisStroke={axisStroke}
            />
          )}

          {currentTab === 'station' && (
            <StationAnalysisView
              metadata={metadata}
              stations={stations}
              selectedStation={selectedStation}
              onSelectStation={handleSelectStation}
              sampleIdx={sampleIdx}
              pollutantMetrics={pollutantMetrics}
              isDark={isDark}
              gridStroke={gridStroke}
              axisStroke={axisStroke}
            />
          )}

          {currentTab === 'data_explorer' && (
            <DataExplorerView
              sampleData={sampleData}
              sampleIdx={sampleIdx}
              pollutants={metadata?.pollutants || ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3']}
            />
          )}

          {currentTab === 'sandbox' && (
            <LiveImputationView
              sampleIdx={sampleIdx}
              liveRate={liveRate}
              setLiveRate={setLiveRate}
              liveMechanism={liveMechanism}
              setLiveMechanism={setLiveMechanism}
              liveSeed={liveSeed}
              setLiveSeed={setLiveSeed}
              liveResult={liveResult}
              liveLoading={liveLoading}
              liveStep={liveStep}
              onRunLiveImpute={handleRunLiveImpute}
              targetPollutant={targetPollutant}
              setTargetPollutant={setTargetPollutant}
              pollutants={metadata?.pollutants || ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3']}
              isDark={isDark}
              gridStroke={gridStroke}
              axisStroke={axisStroke}
            />
          )}

          {currentTab === 'experiments' && (
            <ExperimentHistoryView
              experiments={experiments}
            />
          )}
        </main>
      </div>

      {/* Global Modals - Neutral charcoal z-50 */}
      <GlobalSearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onSelectPollutant={setTargetPollutant}
        onSelectSample={setSampleIdx}
        onSelectTab={setCurrentTab}
        metadata={metadata}
      />

      <ExportModal
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        sampleIdx={sampleIdx}
        targetPollutant={targetPollutant}
        station={metadata?.station || selectedStation || 'Delhi'}
        dataset={metadata?.dataset || 'Indian National Air Quality Dataset (CPCB)'}
        chartData={chartData}
        metrics={metrics}
      />

      <ModelConfigModal
        isOpen={isModelConfigOpen}
        onClose={() => setIsModelConfigOpen(false)}
        modelConfig={modelConfig}
      />
    </div>
  );
}
