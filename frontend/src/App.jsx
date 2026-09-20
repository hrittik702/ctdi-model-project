import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';

// API Service & Canonical Data Contract
import api from './services/api';
import {
  HONG_KONG_STATIONS,
  CANONICAL_CHANNELS,
  DATASET_METADATA
} from './constants/datasetContract';

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
import ModelComparisonLabView from './views/ModelComparisonLabView';
import SettingsView from './views/SettingsView';

// Modals
import GlobalSearchModal from './components/GlobalSearchModal';
import ExportModal from './components/ExportModal';
import ModelConfigModal from './components/ModelConfigModal';
import HelpModal from './components/HelpModal';

export default function App() {
  // Theme state: dark / light
  const [theme, setTheme] = useState(() => localStorage.getItem('ctdi_theme') || 'dark');
  const isDark = theme === 'dark';

  // Navigation & Shell state
  const [currentTab, setCurrentTab] = useState(() => {
    const hash = window.location.hash ? window.location.hash.replace('#', '') : '';
    return hash || 'dashboard';
  });
  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash.replace('#', '');
      if (hash) {
        setCurrentTab(hash);
      }
    };
    window.addEventListener('hashchange', handleHash);
    return () => window.removeEventListener('hashchange', handleHash);
  }, []);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.has('collapsed')) return params.get('collapsed') === 'true';
      return localStorage.getItem('ctdi_sidebar_collapsed') === 'true';
    }
    return false;
  });
  const [isPresentationMode, setIsPresentationMode] = useState(false);

  // Modal dialog states
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);
  const [isModelConfigOpen, setIsModelConfigOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  // Backend data states (Aligned to Hong Kong 16 Stations & 13 Channels)
  const [metadata, setMetadata] = useState(null);
  const [stations, setStations] = useState(HONG_KONG_STATIONS);
  const [selectedStation, setSelectedStation] = useState('CW');
  const [activeModel, setActiveModel] = useState('ctdi_cnn_transformer');
  const [metrics, setMetrics] = useState([]);
  const [pollutantMetrics, setPollutantMetrics] = useState({});
  const [experiments, setExperiments] = useState([]);
  const [modelConfig, setModelConfig] = useState(null);
  const [healthInfo, setHealthInfo] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);

  // Trajectory exploration state (Station-local window index: 0 to 26,280)
  const [sampleIdx, setSampleIdx] = useState(() => {
    const p = new URLSearchParams(window.location.search).get('sample');
    return p !== null && !isNaN(Number(p)) ? Number(p) : 0;
  });
  const [targetPollutant, setTargetPollutant] = useState('PM2.5');
  const [sampleData, setSampleData] = useState(null);
  const [isLoadingSample, setIsLoadingSample] = useState(false);

  // Visibility toggles for curve series
  const [visibleModels, setVisibleModels] = useState({
    groundTruth: true,
    observed: true,
    hiddenTarget: true,
    transformer: false, // Model imputation series
    linear: false,
    knn: false,
    mlp: false
  });

  // Live simulation sandbox state
  const [liveRate, setLiveRate] = useState(0.30);
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

  // Keyboard shortcuts: Ctrl+K (Search) & Ctrl+B (Sidebar toggle)
  useEffect(() => {
    const handleKeyDown = (e) => {
      const isMac = typeof navigator !== 'undefined' && navigator.platform?.toUpperCase().indexOf('MAC') >= 0;
      const modifier = isMac ? e.metaKey : e.ctrlKey;

      if (modifier && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsSearchOpen(prev => !prev);
      }
      if (modifier && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        toggleSidebar();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Poll health and fetch initial metadata & global metrics on mount
  const loadInitialData = useCallback(async () => {
    try {
      const initialStation = selectedStation || 'CW';
      const [health, stnsRes, meta, metList, polMets, exps, config] = await Promise.all([
        api.getHealth(initialStation),
        api.getStations(),
        api.getMetadata(initialStation),
        api.getMetrics(initialStation),
        api.getPollutantMetrics(initialStation),
        api.getExperiments(),
        api.getModelConfig(initialStation)
      ]);

      setHealthInfo(health);
      setBackendOnline(health.status === 'ok');

      if (stnsRes?.stations) {
        setStations(stnsRes.stations);
      }
      setMetadata(meta);
      setMetrics(metList || []);
      setPollutantMetrics(polMets || {});
      setExperiments(exps || []);
      setModelConfig(config);

      if (meta?.pollutants?.length > 0) {
        setTargetPollutant(prev => prev || meta.pollutants[0]);
      }
    } catch (err) {
      console.warn('Initial data load completed with fallbacks:', err);
      setBackendOnline(false);
    }
  }, []);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Periodic health polling
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const health = await api.getHealth(selectedStation);
        setBackendOnline(health.status === 'ok');
      } catch {
        setBackendOnline(false);
      }
    }, 15000);
    return () => clearInterval(interval);
  }, [selectedStation]);

  // Handle station selection
  const handleSelectStation = async (stationId) => {
    setSelectedStation(stationId);
    try {
      await api.selectStation(stationId);
      const [newHealth, newMeta, newConfig] = await Promise.all([
        api.getHealth(stationId),
        api.getMetadata(stationId),
        api.getModelConfig(stationId)
      ]);
      setHealthInfo(newHealth);
      setMetadata(newMeta);
      setModelConfig(newConfig);
    } catch (err) {
      console.warn('Failed to switch station metadata:', err);
    }
  };

  // Handle active model selection
  const handleSelectActiveModel = async (modelId) => {
    setActiveModel(modelId);
    try {
      await api.selectActiveModel(modelId);
      const newConfig = await api.getModelConfig(selectedStation);
      setModelConfig(newConfig);
    } catch (err) {
      console.warn('Failed to switch active model:', err);
    }
  };

  // Fetch sample telemetry whenever sampleIdx or selectedStation changes
  useEffect(() => {
    let isMounted = true;
    async function fetchSample() {
      setIsLoadingSample(true);
      try {
        const data = await api.getSample(sampleIdx, selectedStation);
        if (isMounted) {
          setSampleData(data);
        }
      } catch (err) {
        console.error(`Failed to fetch sample ${sampleIdx} for station ${selectedStation}:`, err);
        if (isMounted) {
          setSampleData(null);
        }
      } finally {
        if (isMounted) {
          setIsLoadingSample(false);
        }
      }
    }
    fetchSample();
    return () => {
      isMounted = false;
    };
  }, [sampleIdx, selectedStation]);

  // Execute live model inference with progress feedback
  const handleRunLiveImpute = async () => {
    setLiveLoading(true);
    setLiveStep('Preparing 24h sample tensor...');
    try {
      await new Promise(r => setTimeout(r, 120));
      setLiveStep(`Applying ${liveMechanism.toUpperCase()} corruption (${Math.round(liveRate * 100)}%)...`);
      await new Promise(r => setTimeout(r, 150));
      setLiveStep('Preparing model inference...');
      
      const res = await api.liveImpute({
        sampleIdx,
        missingRate: liveRate,
        mechanism: liveMechanism,
        seed: liveSeed,
        station: selectedStation
      });

      setLiveStep('Complete');
      setLiveResult(res);
    } catch (err) {
      console.error('Live imputation execution state:', err);
      setLiveStep('Model checkpoint unavailable.');
    } finally {
      setLiveLoading(false);
    }
  };

  // Build chart dataset for the active trajectory view (memoized to prevent re-mapping on scroll)
  const channelObj = useMemo(() => {
    return CANONICAL_CHANNELS.find(c => c.name === targetPollutant || c.label === targetPollutant) || CANONICAL_CHANNELS[0];
  }, [targetPollutant]);
  const channelUnit = channelObj?.unit || 'µg/m³';

  const chartData = useMemo(() => {
    if (!sampleData?.hours) return [];
    const pData = sampleData?.pollutants?.[targetPollutant];
    return sampleData.hours.map((hour, i) => {
      const isObs = pData?.observed_mask?.[i] === 1;
      const isEval = pData?.eval_mask?.[i] === 1;
      const actualVal = pData?.actual?.[i];
      const rawTimestamp = sampleData.timestamps?.[i] || '';
      const clockTime = rawTimestamp.includes(' ') ? rawTimestamp.split(' ')[1] : `H${hour}`;
      const datePart = rawTimestamp.includes(' ') ? rawTimestamp.split(' ')[0] : '';

      return {
        hour: clockTime,
        time: clockTime,
        timeIndex: i,
        stepOffset: `+${i}h`,
        date: datePart,
        timestamp: rawTimestamp,
        unit: channelUnit,
        pollutantName: targetPollutant,
        actual: actualVal,
        observed: isObs ? actualVal : null,
        hiddenTarget: isEval ? actualVal : null,
        naturalMissing: !isObs ? actualVal : null,
        isNaturalMissing: !isObs,
        transformer: pData?.transformer?.[i] ?? null,
        linear: pData?.linear?.[i] ?? null,
        knn: pData?.knn?.[i] ?? null,
        mlp: pData?.mlp?.[i] ?? null
      };
    });
  }, [sampleData, targetPollutant, channelUnit]);

  // Theme-aware Recharts styling tokens
  const gridStroke = isDark ? 'rgba(255, 255, 255, 0.08)' : '#e2e8f0';
  const axisStroke = isDark ? '#71717a' : '#94a3b8';

  // Curve series definitions for interactive legend chips (memoized by theme)
  const curveSeries = useMemo(() => [
    { key: 'observed', label: 'Observed Points', dotColor: 'bg-blue-500', activeStyle: isDark ? 'bg-blue-950/60 text-blue-300 border-blue-800' : 'bg-blue-50 text-blue-700 border-blue-200 shadow-xs' },
    { key: 'groundTruth', label: 'Ground Truth Line', dotColor: isDark ? 'bg-zinc-200' : 'bg-slate-900', activeStyle: isDark ? 'bg-zinc-800 text-zinc-100 border-zinc-700' : 'bg-slate-900 text-white border-slate-900 shadow-xs' },
    { key: 'hiddenTarget', label: 'Natural Missing Dropout', dotColor: 'bg-red-500', activeStyle: isDark ? 'bg-red-950/60 text-red-300 border-red-800' : 'bg-red-50 text-red-700 border-red-200 shadow-xs' },
    { key: 'transformer', label: 'CTDI Imputer', dotColor: 'bg-emerald-500', activeStyle: isDark ? 'bg-emerald-950/60 text-emerald-300 border-emerald-800 font-bold' : 'bg-emerald-50 text-emerald-800 border-emerald-300 font-bold shadow-xs' },
    { key: 'linear', label: 'Linear Baseline', dotColor: 'bg-amber-500', activeStyle: isDark ? 'bg-amber-950/60 text-amber-300 border-amber-800' : 'bg-amber-50 text-amber-800 border-amber-300 shadow-xs' },
    { key: 'knn', label: 'KNN Baseline', dotColor: 'bg-purple-500', activeStyle: isDark ? 'bg-purple-950/60 text-purple-300 border-purple-800' : 'bg-purple-50 text-purple-700 border-purple-200' },
    { key: 'mlp', label: 'MLP Baseline', dotColor: 'bg-cyan-500', activeStyle: isDark ? 'bg-cyan-950/60 text-cyan-300 border-cyan-800' : 'bg-cyan-50 text-cyan-700 border-cyan-200' }
  ], [isDark]);

  // View title helper
  const viewTitles = {
    dashboard: 'Dashboard',
    explorer: '24h Concentration Trajectory',
    multigrid: 'Multi-Pollutant Workspace',
    scoreboard: 'Benchmark Suite',
    station: 'Station Geographical Profile',
    data_explorer: 'Data Explorer',
    sandbox: 'Live Imputation Workspace',
    comparison: 'Model Comparison',
    experiments: 'Experiment History',
    settings: 'Settings',
    model_config: 'Model Architecture & Configuration'
  };

  // Content scroll depth state (Header scroll shadow)
  const [isContentScrolled, setIsContentScrolled] = useState(false);
  // Section identity currently active in header on scroll
  const [activeSection, setActiveSection] = useState(null);
  const mainContentRef = useRef(null);

  const handleContentScroll = useCallback((e) => {
    const container = e.currentTarget;
    const scrollTop = container.scrollTop;
    const scrolled = scrollTop > 4;
    setIsContentScrolled(prev => (prev !== scrolled ? scrolled : prev));

    // Dashboard is deliberately excluded per requirements
    if (currentTab === 'dashboard') {
      setActiveSection(prev => (prev !== null ? null : prev));
      return;
    }

    const sectionElements = container.querySelectorAll('[data-section-title]');
    if (!sectionElements || sectionElements.length === 0) {
      setActiveSection(prev => (prev !== null ? null : prev));
      return;
    }

    const containerRect = container.getBoundingClientRect();
    // Threshold is less than 6% of viewport height (typically ~50px-65px, matching floating navbar)
    const threshold = Math.max(48, window.innerHeight * 0.06);

    let currentActive = null;
    for (let i = 0; i < sectionElements.length; i++) {
      const el = sectionElements[i];
      const isHeading = el.hasAttribute('data-section-heading');
      const rect = el.getBoundingClientRect();
      const relativeTop = rect.top - containerRect.top;

      if (relativeTop <= threshold) {
        // Less than 6% threshold: hide heading in content page, activate in header
        if (isHeading) {
          el.style.opacity = '0';
          el.style.pointerEvents = 'none';
        }
        currentActive = {
          id: el.getAttribute('data-section-id') || `sec-${i}`,
          title: el.getAttribute('data-section-title'),
          iconName: el.getAttribute('data-section-icon') || null
        };
      } else {
        // Above threshold: keep heading fully visible in content page
        if (isHeading) {
          el.style.opacity = '1';
          el.style.pointerEvents = 'auto';
        }
      }
    }

    setActiveSection(prev => {
      if (!prev && !currentActive) return null;
      if (prev && currentActive && prev.id === currentActive.id && prev.title === currentActive.title) {
        return prev;
      }
      return currentActive;
    });
  }, [currentTab]);

  const handleSelectTab = (tabId) => {
    if (tabId === 'model_config') {
      setIsModelConfigOpen(true);
    } else {
      setCurrentTab(tabId);
      setActiveSection(null);
      if (mainContentRef.current) {
        mainContentRef.current.scrollTop = 0;
        const els = mainContentRef.current.querySelectorAll('[data-section-heading]');
        els.forEach(el => {
          el.style.opacity = '1';
          el.style.pointerEvents = 'auto';
        });
      }
      setIsContentScrolled(false);
    }
  };

  const handleDrillDownToPollutant = (pollutant) => {
    setTargetPollutant(pollutant);
    setCurrentTab('explorer');
    setActiveSection(null);
    if (mainContentRef.current) {
      mainContentRef.current.scrollTop = 0;
      const els = mainContentRef.current.querySelectorAll('[data-section-heading]');
      els.forEach(el => {
        el.style.opacity = '1';
        el.style.pointerEvents = 'auto';
      });
    }
    setIsContentScrolled(false);
  };

  const availableChannels = metadata?.pollutants || CANONICAL_CHANNELS.map(c => c.name);
  const totalWindowCount = metadata?.station_windows || 26281;

  return (
    <div className="h-screen w-screen overflow-hidden bg-slate-50 dark:bg-[#050505] text-slate-900 dark:text-zinc-100 flex font-sans transition-colors duration-200 select-none">
      {/* 1. Full-Height Sidebar on the Left */}
      {!isPresentationMode && (
        <Sidebar
          currentTab={currentTab}
          onSelectTab={handleSelectTab}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={toggleSidebar}
          onOpenSearch={() => setIsSearchOpen(true)}
          onOpenHelp={() => setIsHelpOpen(true)}
        />
      )}

      {/* 2. Right Column: Content Header + Independently Scrollable Workspace */}
      <div className="flex-1 min-w-0 h-full overflow-hidden relative">
        {/* Main Viewport Content Area - Sticky Header + Scrollable Views */}
        <main 
          ref={mainContentRef}
          onScroll={handleContentScroll}
          className="h-full overflow-y-auto px-4 pb-6 sm:px-6 sm:pb-6 space-y-4 min-h-0 bg-transparent"
        >
          <TopNavbar
            currentViewTitle={viewTitles[currentTab] || 'Analytics Studio'}
            currentStation={selectedStation}
            stations={stations}
            onSelectStation={handleSelectStation}
            backendOnline={backendOnline}
            theme={theme}
            onToggleTheme={toggleTheme}
            onOpenExport={() => setIsExportOpen(true)}
            isSidebarCollapsed={isSidebarCollapsed}
            onToggleSidebar={toggleSidebar}
            onOpenSearch={() => setIsSearchOpen(true)}
            isScrolled={isContentScrolled}
            activeSection={activeSection}
            isDashboard={currentTab === 'dashboard'}
          />

          {/* Active View Router */}
          {currentTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Executive Dynamic KPI Row */}
              <KpiRow />

              <TrajectoryExplorerView
                isDashboard={true}
                sampleIdx={sampleIdx}
                setSampleIdx={setSampleIdx}
                maxSamples={totalWindowCount}
                targetPollutant={targetPollutant}
                setTargetPollutant={setTargetPollutant}
                pollutants={availableChannels}
                sampleData={sampleData}
                chartData={chartData}
                visibleModels={visibleModels}
                setVisibleModels={setVisibleModels}
                curveSeries={curveSeries}
                isDark={isDark}
                gridStroke={gridStroke}
                axisStroke={axisStroke}
                isLoading={isLoadingSample}
              />
              <BenchmarkView
                isDashboard={true}
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
              maxSamples={totalWindowCount}
              targetPollutant={targetPollutant}
              setTargetPollutant={setTargetPollutant}
              pollutants={availableChannels}
              sampleData={sampleData}
              chartData={chartData}
              visibleModels={visibleModels}
              setVisibleModels={setVisibleModels}
              curveSeries={curveSeries}
              isDark={isDark}
              gridStroke={gridStroke}
              axisStroke={axisStroke}
              isLoading={isLoadingSample}
            />
          )}

          {currentTab === 'multigrid' && (
            <MultiPollutantView
              sampleData={sampleData}
              pollutants={availableChannels}
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
              onNavigateToTab={handleSelectTab}
              isDark={isDark}
              gridStroke={gridStroke}
              axisStroke={axisStroke}
            />
          )}

          {currentTab === 'data_explorer' && (
            <DataExplorerView
              sampleData={sampleData}
              sampleIdx={sampleIdx}
              pollutants={availableChannels}
              stationName={metadata?.station || selectedStation}
              isDark={isDark}
              gridStroke={gridStroke}
              axisStroke={axisStroke}
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
              pollutants={availableChannels}
              selectedStation={selectedStation}
              framework="PyTorch"
              checkpoint={null}
              isDark={isDark}
              gridStroke={gridStroke}
              axisStroke={axisStroke}
            />
          )}

          {currentTab === 'comparison' && (
            <ModelComparisonLabView
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

          {currentTab === 'settings' && (
            <SettingsView
              theme={theme}
              onToggleTheme={toggleTheme}
              isSidebarCollapsed={isSidebarCollapsed}
              onToggleSidebar={toggleSidebar}
              onOpenModelModal={() => setIsModelConfigOpen(true)}
              onNavigateToTab={handleSelectTab}
            />
          )}
        </main>
      </div>

      {/* Global Modals */}
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
        station={metadata?.station || selectedStation || 'Central / Western'}
        dataset={metadata?.dataset || 'CTDI Air Pollution Training Dataset v1.0'}
        chartData={chartData}
        metrics={metrics}
      />

      <ModelConfigModal
        isOpen={isModelConfigOpen}
        onClose={() => setIsModelConfigOpen(false)}
        modelConfig={modelConfig}
      />

      <HelpModal
        isOpen={isHelpOpen}
        onClose={() => setIsHelpOpen(false)}
        onNavigateToSettings={() => {
          setIsHelpOpen(false);
          setCurrentTab('settings');
        }}
      />
    </div>
  );
}
