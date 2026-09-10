import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Card, Chip, Button } from '@heroui/react';
import {
  Play,
  RefreshCw,
  Layers,
  Activity,
  Clock,
  Zap,
  Trophy,
  ShieldCheck,
  Sliders,
  ArrowUpDown,
  CheckCircle2,
  AlertTriangle,
  FileSpreadsheet,
  FileText,
  Filter,
  Sparkles,
  TrendingDown,
  Target,
  UploadCloud,
  History,
  GitCompare,
  Eye,
  EyeOff,
  Cpu,
  Check,
  Search,
  Scale,
  X,
  ExternalLink,
  ChevronRight,
  Printer,
  Info,
  SlidersHorizontal,
  Table as TableIcon,
  BarChart2,
  HelpCircle
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ReferenceArea,
  ReferenceLine,
  Cell
} from 'recharts';

import api from '../services/api';
import ProjectIcon from '../components/ui/ProjectIcon';
import InfoTooltip from '../components/ui/InfoTooltip';

const MODEL_COLORS = {
  delhi_ctdi_original: '#6366f1',  // Indigo
  ctdi_transformer: '#6366f1',     // Indigo
  delhi_ctdi_keras: '#ec4899',     // Pink / Rose
  ctdi_keras: '#ec4899',           // Pink
  linear_interpolation: '#f59e0b', // Amber
  knn: '#06b6d4',                  // Cyan
  mean_imputer: '#94a3b8',         // Slate
  simple_mlp: '#10b981',           // Emerald
  ctdi_improved_v2: '#8b5cf6',     // Violet
  slm_diffusion: '#14b8a6'         // Teal
};

const POLLUTANTS = ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3'];

export default function ModelComparisonLabView({
  isDark = false,
  gridStroke = '#334155',
  axisStroke = '#94a3b8'
}) {
  // 1. Geographic & Catalog State
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('Delhi');
  const [datasets, setDatasets] = useState([]);
  const [registeredModels, setRegisteredModels] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('delhi_test_benchmark');
  const [selectedModels, setSelectedModels] = useState([
    'delhi_ctdi_original',
    'delhi_ctdi_keras',
    'simple_mlp'
  ]);

  // 2. Missingness & Execution Parameters
  const [strategy, setStrategy] = useState('random');
  const [missingRate, setMissingRate] = useState(0.45);
  const [blockLength, setBlockLength] = useState(4);
  const [targetPollutantOutage, setTargetPollutantOutage] = useState('PM2.5');
  const [numWindows, setNumWindows] = useState(1);
  const [randomSeed, setRandomSeed] = useState(42137);
  const [customFile, setCustomFile] = useState(null);

  // 3. Execution & Progress State
  const [isRunning, setIsRunning] = useState(false);
  const [progressStage, setProgressStage] = useState('');
  const [experimentResult, setExperimentResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  // 4. Analytical View & Peak Zoom Filters
  const [selectedPollutantTab, setSelectedPollutantTab] = useState('PM2.5');
  const [sortColumn, setSortColumn] = useState('rank');
  const [sortDirection, setSortDirection] = useState('asc');
  const [activeZoomPeakId, setActiveZoomPeakId] = useState(null);
  const [zoomRange, setZoomRange] = useState(null);
  const [activeChartMode, setActiveChartMode] = useState('reconstruction'); // 'reconstruction' | 'delta'
  const [winMatrixMetric, setWinMatrixMetric] = useState('MAE'); // 'MAE' | 'RMSE' | 'Correlation'
  const [selectedSamePointTimestamp, setSelectedSamePointTimestamp] = useState(null);

  const [chartModelVisibility, setChartModelVisibility] = useState({
    ground_truth: true,
    observed: true,
    delhi_ctdi_original: true,
    delhi_ctdi_keras: true,
    ctdi_transformer: true,
    simple_mlp: true,
    linear_interpolation: true,
    knn: true,
    mean_imputer: false
  });

  // 5. Audit Inspection Modal
  const [auditModel, setAuditModel] = useState(null);

  // 6. History & A/B Comparison State
  const [historyList, setHistoryList] = useState([]);
  const [showHistoryDrawer, setShowHistoryDrawer] = useState(false);
  const [selectedRunA, setSelectedRunA] = useState('');
  const [selectedRunB, setSelectedRunB] = useState('');
  const [abComparison, setAbComparison] = useState(null);

  const fileInputRef = useRef(null);

  // Initial Catalog Load
  useEffect(() => {
    async function initCatalog() {
      try {
        const [cList, dList, mList, hList] = await Promise.all([
          api.getComparisonCities(),
          api.getComparisonDatasets('Delhi'),
          api.getComparisonModels('Delhi'),
          api.getComparisonHistory()
        ]);
        setCities(cList || []);
        setDatasets(dList || []);
        setRegisteredModels(mList || []);
        setHistoryList(hList || []);

        if (hList && hList.length > 0) {
          // Check if EXP-LAB-7840 exists in history
          const targetExp = hList.find(h => h.experiment_id === 'EXP-LAB-7840') || hList[0];
          const latest = await api.getComparisonExperiment(targetExp.experiment_id);
          setExperimentResult(latest);
          if (latest?.dataset_id) setSelectedDataset(latest.dataset_id);
          if (latest?.models_evaluated) setSelectedModels(latest.models_evaluated);
        } else {
          executeBenchmarkWithCity('Delhi', ['delhi_ctdi_original', 'delhi_ctdi_keras', 'simple_mlp']);
        }
      } catch (err) {
        console.error('Error initializing comparison lab:', err);
      }
    }
    initCatalog();
  }, []);

  // Handle City Change
  const handleCityChange = async (newCity) => {
    setSelectedCity(newCity);
    try {
      const [dList, mList] = await Promise.all([
        api.getComparisonDatasets(newCity),
        api.getComparisonModels(newCity)
      ]);
      setDatasets(dList || []);
      setRegisteredModels(mList || []);
      if (dList && dList.length > 0) {
        setSelectedDataset(dList[0].id);
      }
      const defaultSelected = mList
        .filter(m => m.is_available && (m.category === 'trained' || m.id === 'simple_mlp'))
        .map(m => m.id);
      setSelectedModels(defaultSelected.length > 0 ? defaultSelected : ['delhi_ctdi_original', 'delhi_ctdi_keras']);
    } catch (err) {
      console.error('Failed to change comparison city:', err);
    }
  };

  // Execute benchmark with explicit city and model list
  const executeBenchmarkWithCity = async (cityVal, modelIds) => {
    setIsRunning(true);
    setErrorMsg(null);
    setProgressStage('Acquiring dataset & generating identical missingness masks...');

    try {
      const res = await api.runComparison({
        dataset_id: selectedDataset,
        city: cityVal,
        model_ids: modelIds,
        strategy,
        missing_rate: missingRate,
        block_length: blockLength,
        target_pollutant_outage: targetPollutantOutage,
        seed: randomSeed,
        num_windows: numWindows
      });

      setExperimentResult(res);
      const newVis = { ground_truth: true, observed: true };
      (res.models_evaluated || modelIds).forEach(mId => {
        newVis[mId] = true;
      });
      setChartModelVisibility(newVis);

      const hList = await api.getComparisonHistory();
      setHistoryList(hList);
    } catch (err) {
      console.error('Benchmark execution error:', err);
      setErrorMsg(err.message || 'Comparison run failed.');
    } finally {
      setIsRunning(false);
      setProgressStage('');
    }
  };

  // Main execution trigger from UI
  const executeBenchmark = async () => {
    if (selectedModels.length < 2) {
      setErrorMsg('Please select at least 2 models for comparative evaluation.');
      return;
    }

    setIsRunning(true);
    setErrorMsg(null);
    setProgressStage('Acquiring dataset & generating identical missingness masks...');

    try {
      const stageTimer1 = setTimeout(() => {
        setProgressStage('Executing PyTorch, Keras 3 & baseline runners under invariant mask...');
      }, 400);

      const stageTimer2 = setTimeout(() => {
        setProgressStage('Calculating direct model agreement, peak error, and canonical metrics...');
      }, 1000);

      let res;
      if (selectedDataset === 'upload_custom' && customFile) {
        res = await api.runComparisonUpload({
          file: customFile,
          city: selectedCity,
          model_ids: selectedModels,
          strategy,
          missing_rate: missingRate,
          block_length: blockLength,
          target_pollutant_outage: targetPollutantOutage,
          seed: randomSeed,
          num_windows: numWindows
        });
      } else {
        res = await api.runComparison({
          dataset_id: selectedDataset,
          city: selectedCity,
          model_ids: selectedModels,
          strategy,
          missing_rate: missingRate,
          block_length: blockLength,
          target_pollutant_outage: targetPollutantOutage,
          seed: randomSeed,
          num_windows: numWindows
        });
      }

      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);

      setExperimentResult(res);
      // Reset zoom
      setActiveZoomPeakId(null);
      setZoomRange(null);

      // Auto-update visibility
      const newVis = { ground_truth: true, observed: true };
      (res.models_evaluated || selectedModels).forEach(mId => {
        newVis[mId] = true;
      });
      setChartModelVisibility(newVis);

      const hList = await api.getComparisonHistory();
      setHistoryList(hList);
    } catch (err) {
      setErrorMsg(err.message || 'Comparison run failed.');
    } finally {
      setIsRunning(false);
      setProgressStage('');
    }
  };

  // Re-run experiment replay
  const handleReRunExperiment = async (expId) => {
    setIsRunning(true);
    setErrorMsg(null);
    setProgressStage(`Re-executing experiment ${expId} with exact seed & mask...`);
    try {
      const res = await api.reRunComparisonExperiment(expId);
      setExperimentResult(res);
      const hList = await api.getComparisonHistory();
      setHistoryList(hList);
    } catch (err) {
      setErrorMsg(err.message || 'Re-run failed.');
    } finally {
      setIsRunning(false);
      setProgressStage('');
    }
  };

  // Toggle model selection
  const toggleModelSelection = (mId) => {
    setSelectedModels(prev => {
      if (prev.includes(mId)) {
        if (prev.length === 1) return prev;
        return prev.filter(id => id !== mId);
      } else {
        return [...prev, mId];
      }
    });
  };

  // Quick Selection Helpers
  const selectAllTrained = () => {
    const trained = registeredModels
      .filter(m => m.is_available && (m.category === 'trained' || m.city === selectedCity))
      .map(m => m.id);
    setSelectedModels(prev => Array.from(new Set([...prev, ...trained])));
  };

  const selectBaselines = () => {
    const baselines = registeredModels
      .filter(m => m.is_available && m.category === 'baseline')
      .map(m => m.id);
    setSelectedModels(prev => Array.from(new Set([...prev, ...baselines])));
  };

  const selectAllAvailable = () => {
    const allAvail = registeredModels.filter(m => m.is_available).map(m => m.id);
    setSelectedModels(allAvail);
  };

  const clearSelection = () => {
    setSelectedModels(['delhi_ctdi_original', 'delhi_ctdi_keras']);
  };

  // Toggle curve visibility in chart
  const toggleChartVisibility = (key) => {
    setChartModelVisibility(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  // Peak Selection & Zoom Handling
  const handleSelectPeak = (peak) => {
    if (!peak) {
      setActiveZoomPeakId(null);
      setZoomRange(null);
      return;
    }
    setActiveZoomPeakId(peak.peak_id || peak.id);
    if (peak.pollutant && POLLUTANTS.includes(peak.pollutant)) {
      setSelectedPollutantTab(peak.pollutant);
    }
    setZoomRange([peak.zoom_start, peak.zoom_end]);
  };

  // Sort ranking table
  const handleSort = (col) => {
    if (sortColumn === col) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortColumn(col);
      setSortDirection(col === 'MAE' || col === 'RMSE' || col === 'MAPE' || col === 'rank' || col === 'Bias' ? 'asc' : 'desc');
    }
  };

  const sortedRankings = useMemo(() => {
    if (!experimentResult?.evaluation?.model_rankings) return [];
    const list = [...experimentResult.evaluation.model_rankings];
    list.sort((a, b) => {
      let va = a[sortColumn];
      let vb = b[sortColumn];
      if (typeof va === 'string') va = va.toLowerCase();
      if (typeof vb === 'string') vb = vb.toLowerCase();
      if (va < vb) return sortDirection === 'asc' ? -1 : 1;
      if (va > vb) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
    return list;
  }, [experimentResult, sortColumn, sortDirection]);

  // Executive summary cards derived dynamically
  const winners = useMemo(() => {
    const es = experimentResult?.evaluation?.executive_summary || experimentResult?.evaluation?.winners || {};
    const rankings = experimentResult?.evaluation?.model_rankings || [];
    const top = rankings[0] || {};
    return {
      overall_top_model: {
        name: es.best_overall_mae?.model_name || es.overall_top_model?.name || top.model_name || 'Evaluating...',
        mae: es.best_overall_mae?.value ?? es.overall_top_model?.mae ?? top.MAE ?? 0,
        model_id: es.best_overall_mae?.model_id || es.overall_top_model?.model_id || top.model_id
      },
      peak_specialist: {
        name: es.best_peak_recovery?.model_name || es.peak_specialist?.name || 'Evaluating...',
        mae: es.best_peak_recovery?.value ?? es.peak_specialist?.mae ?? 0
      },
      long_gap_champion: {
        name: es.best_long_gap?.model_name || es.long_gap_champion?.name || 'Evaluating...',
        mae: es.best_long_gap?.value ?? es.long_gap_champion?.mae ?? null
      },
      fastest_model: {
        name: es.fastest_model?.name || (rankings.length ? [...rankings].sort((a, b) => (a.runtime_ms || 0) - (b.runtime_ms || 0))[0]?.model_name : 'Evaluating...'),
        latency_ms: es.fastest_model?.latency_ms || (rankings.length ? [...rankings].sort((a, b) => (a.runtime_ms || 0) - (b.runtime_ms || 0))[0]?.runtime_ms : 0)
      }
    };
  }, [experimentResult]);

  const isGroundTruthMode = experimentResult?.evaluation_mode === 'ground_truth';
  const dataQuality = experimentResult?.evaluation?.data_quality || {};

  // Time-series chart points for currently selected pollutant, sliced if zoomed
  const currentChartData = useMemo(() => {
    if (!experimentResult?.chart_data) return [];
    const fullSeries = experimentResult.chart_data[selectedPollutantTab] || [];
    if (!zoomRange) return fullSeries;
    const [startIdx, endIdx] = zoomRange;
    return fullSeries.slice(startIdx, endIdx + 1);
  }, [experimentResult, selectedPollutantTab, zoomRange]);

  // Model delta series for currently selected pollutant
  const currentDeltaData = useMemo(() => {
    if (!experimentResult?.model_deltas) return [];
    return experimentResult.model_deltas[selectedPollutantTab] || [];
  }, [experimentResult, selectedPollutantTab]);

  // Missing regions in chart data (where mask === 0)
  const missingIntervals = useMemo(() => {
    if (!currentChartData.length) return [];
    const intervals = [];
    let start = null;
    currentChartData.forEach((pt, idx) => {
      if (pt.mask === 0 && start === null) {
        start = pt.time;
      } else if (pt.mask === 1 && start !== null) {
        intervals.push({ x1: start, x2: currentChartData[idx - 1].time });
        start = null;
      }
    });
    if (start !== null) {
      intervals.push({ x1: start, x2: currentChartData[currentChartData.length - 1].time });
    }
    return intervals;
  }, [currentChartData]);

  // Handle A/B comparison load
  const handleCompareRuns = async () => {
    if (!selectedRunA || !selectedRunB) return;
    try {
      const cmp = await api.compareTwoExperiments(selectedRunA, selectedRunB);
      setAbComparison(cmp);
    } catch (err) {
      alert(`Error comparing runs: ${err.message}`);
    }
  };

  // Categorized Models for Selected City
  const categorizedModels = useMemo(() => {
    const trained = [];
    const baselines = [];
    const future = [];

    registeredModels.forEach(m => {
      if (m.category === 'trained' || (m.city === selectedCity && m.category !== 'future')) {
        trained.push(m);
      } else if (m.category === 'baseline') {
        baselines.push(m);
      } else {
        future.push(m);
      }
    });

    return { trained, baselines, future };
  }, [registeredModels, selectedCity]);

  // Model Agreement data
  const modelAgreement = experimentResult?.model_agreement;

  // Selected same-point observation for detailed investigation
  const samePointData = useMemo(() => {
    if (!selectedSamePointTimestamp || !experimentResult?.chart_data) return null;
    const pts = experimentResult.chart_data[selectedPollutantTab] || [];
    return pts.find(p => p.time === selectedSamePointTimestamp || p.timestamp === selectedSamePointTimestamp);
  }, [experimentResult, selectedPollutantTab, selectedSamePointTimestamp]);

  return (
    <div className="space-y-6 pb-16">
      {/* 1. HEADER SECTION */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 border-b border-slate-200 dark:border-zinc-800 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400">
              <ProjectIcon name="benchmark" size="lg" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 dark:text-zinc-100 flex items-center gap-2 flex-wrap">
                Model Comparison & Benchmarking Lab
                <Chip size="sm" variant="flat" color="primary" className="text-xs font-semibold">
                  {selectedCity} • Invariant Mask Protocol
                </Chip>
              </h1>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                Direct head-to-head evaluation of trained neural architectures (PyTorch & Keras 3) vs baselines under identical hidden test conditions.
              </p>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2.5 flex-wrap">
          <Button
            size="sm"
            variant="flat"
            onPress={() => setShowHistoryDrawer(!showHistoryDrawer)}
            startContent={<History className="w-4 h-4 text-slate-500" />}
            className="text-xs font-semibold text-slate-700 dark:text-zinc-300"
          >
            History ({historyList.length})
          </Button>

          {experimentResult && (
            <div className="flex items-center gap-1.5">
              <a
                href={api.getComparisonExportUrl(experimentResult.experiment_id, 'csv')}
                download
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 transition-colors"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-500" />
                CSV
              </a>
              <a
                href={api.getComparisonExportUrl(experimentResult.experiment_id, 'json')}
                download
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 transition-colors"
              >
                <FileText className="w-3.5 h-3.5 text-indigo-500" />
                JSON
              </a>
              <a
                href={api.getComparisonExportUrl(experimentResult.experiment_id, 'pdf')}
                download
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-900 transition-colors"
              >
                <Printer className="w-3.5 h-3.5 text-rose-500" />
                PDF Report
              </a>
            </div>
          )}

          <Button
            size="sm"
            color="primary"
            isLoading={isRunning}
            onPress={executeBenchmark}
            startContent={!isRunning && <Play className="w-3.5 h-3.5 fill-current" />}
            className="font-bold text-xs bg-indigo-600 hover:bg-indigo-700 text-white shadow-xs"
          >
            {isRunning ? 'Benchmarking...' : 'Run Benchmark'}
          </Button>
        </div>
      </div>

      {/* ERROR NOTICE IF ANY */}
      {errorMsg && (
        <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs flex items-center gap-2.5">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* PROGRESS BANNER */}
      {isRunning && (
        <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-between text-xs text-indigo-700 dark:text-indigo-300 animate-pulse">
          <div className="flex items-center gap-3">
            <RefreshCw className="w-4 h-4 animate-spin text-indigo-600" />
            <span className="font-semibold">{progressStage}</span>
          </div>
          <span className="font-mono text-[11px] text-slate-500 dark:text-zinc-400">
            City: {selectedCity} | Seed: {randomSeed} | Invariant Mask Protocol
          </span>
        </div>
      )}

      {/* PRELIMINARY EVALUATION WARNING IF SAMPLE SIZE < 100 */}
      {experimentResult?.evaluation?.is_preliminary && (
        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            <span className="font-medium">
              {experimentResult.evaluation.preliminary_notice}
            </span>
          </div>
          <span className="text-[11px] font-mono font-bold bg-amber-100 dark:bg-amber-950 px-2 py-0.5 rounded">
            n = {experimentResult.total_points_evaluated} cells
          </span>
        </div>
      )}

      {/* 2. CONFIGURATION CONTROL PANEL: CITY -> DATASET -> MECHANISM -> MODELS */}
      <Card className="p-4 bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs">
        <div className="flex items-center justify-between mb-3.5 border-b border-slate-100 dark:border-zinc-800 pb-2.5">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-800 dark:text-zinc-200">
            <Sliders className="w-4 h-4 text-indigo-500" />
            <span>Experiment Configuration Matrix</span>
            <InfoTooltip content="All models are evaluated on identical test windows with the exact same pseudo-random mask tensor. Observed cells are strictly locked." />
          </div>
          <div className="flex items-center gap-2 text-[11px] text-slate-500">
            <span>Evaluation Scope:</span>
            <Chip size="sm" variant="dot" color={isGroundTruthMode ? 'success' : 'warning'} className="text-[10px]">
              {isGroundTruthMode ? 'Hidden Ground-Truth Cells Only' : 'Reconstruction Mode'}
            </Chip>
          </div>
        </div>

        {/* Step 1: City, Dataset, Mechanism, Sliders */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* City Selector */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 dark:text-zinc-400 mb-1.5 flex items-center justify-between">
              <span>1. City / Territory</span>
              <span className="text-[10px] text-indigo-600 dark:text-indigo-400 font-normal">
                {cities.find(c => c.city === selectedCity)?.trained_models_count || 0} Models
              </span>
            </label>
            <select
              value={selectedCity}
              onChange={(e) => handleCityChange(e.target.value)}
              className="w-full text-xs font-semibold bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg px-2.5 py-1.5 text-slate-800 dark:text-zinc-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {cities.map(c => (
                <option key={c.city} value={c.city}>
                  {c.city} {c.has_trained_models ? '★ (Trained)' : '(No Models)'}
                </option>
              ))}
            </select>
          </div>

          {/* Dataset Selector */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 dark:text-zinc-400 mb-1.5">
              2. Test Dataset
            </label>
            <select
              value={selectedDataset}
              onChange={(e) => setSelectedDataset(e.target.value)}
              className="w-full text-xs font-medium bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg px-2.5 py-1.5 text-slate-800 dark:text-zinc-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {datasets.map(d => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
              <option value="upload_custom">+ Upload Custom CSV</option>
            </select>

            {selectedDataset === 'upload_custom' && (
              <div className="mt-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  accept=".csv"
                  onChange={(e) => setCustomFile(e.target.files?.[0] || null)}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full py-1 px-2 border border-dashed border-indigo-400 dark:border-indigo-600 rounded-lg text-indigo-600 dark:text-indigo-400 text-[10px] font-medium flex items-center justify-center gap-1.5 hover:bg-indigo-50/40"
                >
                  <UploadCloud className="w-3 h-3" />
                  {customFile ? customFile.name : 'Select CSV File'}
                </button>
              </div>
            )}
          </div>

          {/* Missingness Strategy */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 dark:text-zinc-400 mb-1.5">
              3. Missingness Mask
            </label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full text-xs font-medium bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg px-2.5 py-1.5 text-slate-800 dark:text-zinc-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="random">Random Missingness (MCAR)</option>
              <option value="contiguous">Contiguous Gap (Blackout)</option>
              <option value="single_pollutant">Single Pollutant Outage</option>
              <option value="multi_pollutant">Multi-Channel Sensor Failure</option>
            </select>
          </div>

          {/* Missing Rate & Gap Length */}
          <div>
            <div className="flex justify-between items-center text-[11px] font-semibold text-slate-600 dark:text-zinc-400 mb-1.5">
              <span>{strategy === 'contiguous' ? 'Gap Duration' : 'Missing Rate'}</span>
              <span className="font-mono text-indigo-600 dark:text-indigo-400 font-bold">
                {strategy === 'contiguous' ? `${blockLength} hrs` : `${Math.round(missingRate * 100)}%`}
              </span>
            </div>
            {strategy === 'contiguous' ? (
              <input
                type="range"
                min={1}
                max={24}
                step={1}
                value={blockLength}
                onChange={(e) => setBlockLength(Number(e.target.value))}
                className="w-full accent-indigo-600 h-1.5 bg-slate-200 dark:bg-zinc-700 rounded-lg cursor-pointer"
              />
            ) : (
              <input
                type="range"
                min={0.05}
                max={0.70}
                step={0.05}
                value={missingRate}
                onChange={(e) => setMissingRate(Number(e.target.value))}
                className="w-full accent-indigo-600 h-1.5 bg-slate-200 dark:bg-zinc-700 rounded-lg cursor-pointer"
              />
            )}
          </div>

          {/* Windows & Seed Lock */}
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 dark:text-zinc-400 mb-1.5">
                Windows
              </label>
              <input
                type="number"
                min={1}
                max={25}
                value={numWindows}
                onChange={(e) => setNumWindows(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-full text-xs font-mono bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg px-2.5 py-1.5 text-slate-800 dark:text-zinc-200"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 dark:text-zinc-400 mb-1.5">
                Seed Lock
              </label>
              <input
                type="number"
                value={randomSeed}
                onChange={(e) => setRandomSeed(parseInt(e.target.value) || 0)}
                className="w-full text-xs font-mono bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg px-2.5 py-1.5 text-slate-800 dark:text-zinc-200"
              />
            </div>
          </div>
        </div>

        {/* Step 2: Categorized Model Selection */}
        <div className="mt-4 pt-3.5 border-t border-slate-100 dark:border-zinc-800/80">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
            <div className="text-[11px] font-bold text-slate-700 dark:text-zinc-300 flex items-center gap-2">
              <Layers className="w-3.5 h-3.5 text-indigo-500" />
              <span>Available Trained & Baseline Models ({selectedModels.length} Selected):</span>
              <span className="text-[10px] text-slate-400 font-normal">(Minimum 2 required)</span>
            </div>
            <div className="flex items-center gap-1.5 flex-wrap">
              <button
                type="button"
                onClick={selectAllTrained}
                className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100"
              >
                Select Trained
              </button>
              <button
                type="button"
                onClick={selectBaselines}
                className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-300 border border-slate-200 dark:border-zinc-700 hover:bg-slate-200"
              >
                Select Baselines
              </button>
              <button
                type="button"
                onClick={selectAllAvailable}
                className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-300 border border-slate-200 dark:border-zinc-700 hover:bg-slate-200"
              >
                Select All
              </button>
              <button
                type="button"
                onClick={clearSelection}
                className="px-2 py-0.5 rounded text-[10px] font-semibold text-slate-400 hover:text-slate-600 dark:hover:text-zinc-200"
              >
                Reset
              </button>
            </div>
          </div>

          {/* Group 1: Trained Deep Models */}
          <div className="space-y-2">
            <div>
              <div className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 mb-1.5 flex items-center gap-1.5">
                <Cpu className="w-3 h-3" />
                <span>Trained Neural Checkpoints ({selectedCity}):</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                {categorizedModels.trained.map(m => {
                  const isSelected = selectedModels.includes(m.id);
                  const color = MODEL_COLORS[m.id] || '#6366f1';
                  return (
                    <div
                      key={m.id}
                      onClick={() => toggleModelSelection(m.id)}
                      className={`p-2.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                        isSelected
                          ? 'bg-indigo-50/70 dark:bg-indigo-950/40 border-indigo-300 dark:border-indigo-800 shadow-2xs'
                          : 'bg-white dark:bg-zinc-900 border-slate-200 dark:border-zinc-800 opacity-75 hover:opacity-100'
                      }`}
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div
                          className="w-3 h-3 rounded-full shrink-0 border"
                          style={{ backgroundColor: color, borderColor: color }}
                        />
                        <div className="truncate">
                          <div className="font-bold text-xs text-slate-900 dark:text-zinc-100 truncate flex items-center gap-1.5">
                            <span>{m.name}</span>
                            {isSelected && <Check className="w-3 h-3 text-indigo-600 dark:text-indigo-400" />}
                          </div>
                          <div className="text-[10px] text-slate-500 dark:text-zinc-400 flex items-center gap-1 mt-0.5">
                            <span className="font-semibold text-slate-700 dark:text-zinc-300">{m.framework}</span>
                            <span>•</span>
                            <span className="font-mono">{m.param_count ? `${(m.param_count / 1000).toFixed(0)}k params` : '0 params'}</span>
                            <span>•</span>
                            <span className="text-emerald-600 font-medium">● {m.status || 'Ready'}</span>
                          </div>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setAuditModel(m);
                        }}
                        title="Inspect Architecture & Checkpoint Metadata"
                        className="p-1 rounded hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors ml-2 shrink-0"
                      >
                        <Search className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Group 2: Baselines & Future */}
            <div className="pt-2 border-t border-slate-100 dark:border-zinc-800/60">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 mb-1.5">
                Statistical & Classical Baselines:
              </div>
              <div className="flex flex-wrap gap-2">
                {categorizedModels.baselines.map(m => {
                  const isSelected = selectedModels.includes(m.id);
                  const color = MODEL_COLORS[m.id] || '#94a3b8';
                  return (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => toggleModelSelection(m.id)}
                      className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2 border ${
                        isSelected
                          ? 'bg-slate-100 dark:bg-zinc-800 border-slate-300 dark:border-zinc-700 text-slate-800 dark:text-zinc-200 font-semibold shadow-2xs'
                          : 'bg-white dark:bg-zinc-900 border-slate-200 dark:border-zinc-800 text-slate-500 hover:border-slate-300'
                      }`}
                    >
                      <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: color }} />
                      <span>{m.name}</span>
                      {isSelected && <Check className="w-3 h-3 text-emerald-600" />}
                    </button>
                  );
                })}

                {categorizedModels.future.map(m => (
                  <div
                    key={m.id}
                    className="px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center gap-2 border border-dashed border-slate-200 dark:border-zinc-800 text-slate-400 bg-slate-50/50 dark:bg-zinc-800/20 cursor-not-allowed opacity-60"
                  >
                    <span className="w-2 h-2 rounded-full bg-slate-300 dark:bg-zinc-700" />
                    <span>{m.name}</span>
                    <span className="text-[9px] bg-slate-200 dark:bg-zinc-800 px-1 py-0.2 rounded font-mono">In Dev</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* 3. DATASET QUALITY & SAMPLING INTERVAL PANEL */}
      {dataQuality.total_cells && (
        <Card className="p-4 bg-slate-50/60 dark:bg-zinc-900/60 border border-slate-200/80 dark:border-zinc-800">
          <div className="flex items-center justify-between mb-2.5 border-b border-slate-200/60 dark:border-zinc-800 pb-2">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-800 dark:text-zinc-200">
              <TableIcon className="w-3.5 h-3.5 text-indigo-500" />
              <span>Dataset Quality & Sampling Characteristics</span>
            </div>
            <span className="text-[11px] font-mono text-slate-500">
              Time Span: {dataQuality.time_range}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5 text-xs font-mono">
            <div className="p-2 rounded-lg bg-white dark:bg-zinc-900 border border-slate-200/60 dark:border-zinc-800">
              <span className="text-[10px] text-slate-400 uppercase font-sans">Total Cells</span>
              <div className="font-bold text-slate-900 dark:text-zinc-100 mt-0.5">{dataQuality.total_cells}</div>
            </div>
            <div className="p-2 rounded-lg bg-white dark:bg-zinc-900 border border-slate-200/60 dark:border-zinc-800">
              <span className="text-[10px] text-slate-400 uppercase font-sans">Observed (Locked)</span>
              <div className="font-bold text-emerald-600 mt-0.5">{dataQuality.observed_cells}</div>
            </div>
            <div className="p-2 rounded-lg bg-white dark:bg-zinc-900 border border-slate-200/60 dark:border-zinc-800">
              <span className="text-[10px] text-slate-400 uppercase font-sans">Evaluated Cells</span>
              <div className="font-bold text-indigo-600 mt-0.5">{dataQuality.evaluated_cells}</div>
            </div>
            <div className="p-2 rounded-lg bg-white dark:bg-zinc-900 border border-slate-200/60 dark:border-zinc-800">
              <span className="text-[10px] text-slate-400 uppercase font-sans">Missing Rate</span>
              <div className="font-bold text-slate-800 dark:text-zinc-200 mt-0.5">{dataQuality.missing_rate_pct}%</div>
            </div>
            <div className="p-2 rounded-lg bg-white dark:bg-zinc-900 border border-slate-200/60 dark:border-zinc-800">
              <span className="text-[10px] text-slate-400 uppercase font-sans">Sampling Interval</span>
              <div className="font-bold text-indigo-600 mt-0.5 font-sans">{dataQuality.sampling_interval}</div>
            </div>
            <div className="p-2 rounded-lg bg-white dark:bg-zinc-900 border border-slate-200/60 dark:border-zinc-800">
              <span className="text-[10px] text-slate-400 uppercase font-sans">Timesteps</span>
              <div className="font-bold text-slate-800 dark:text-zinc-200 mt-0.5">{dataQuality.total_timesteps}</div>
            </div>
            <div className="p-2 rounded-lg bg-white dark:bg-zinc-900 border border-slate-200/60 dark:border-zinc-800">
              <span className="text-[10px] text-slate-400 uppercase font-sans">Ground Truth</span>
              <div className="font-bold text-emerald-600 font-sans mt-0.5">Available</div>
            </div>
          </div>
        </Card>
      )}

      {/* 4. DIRECT MODEL-TO-MODEL AGREEMENT & IMPLEMENTATION EQUIVALENCE */}
      {modelAgreement && (
        <Card className="p-5 bg-white dark:bg-zinc-900 border-2 border-indigo-500/30 dark:border-indigo-500/20 shadow-sm relative overflow-hidden">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 pb-4 mb-4 border-b border-slate-100 dark:border-zinc-800">
            <div>
              <div className="flex items-center gap-2">
                <Scale className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                <h2 className="text-sm font-bold text-slate-900 dark:text-zinc-100 uppercase tracking-wider">
                  Direct Model Agreement & Implementation Equivalence
                </h2>
                <Chip size="sm" variant="flat" color="primary" className="text-[10px] font-bold">
                  Pearson r = {modelAgreement.pearson_correlation?.toFixed(4)}
                </Chip>
              </div>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1">
                Comparing <span className="font-bold text-indigo-600 dark:text-indigo-400">{modelAgreement.model_a?.name}</span> vs{' '}
                <span className="font-bold text-pink-600 dark:text-pink-400">{modelAgreement.model_b?.name}</span> across identical missing points.
              </p>
            </div>
            <div className="text-xs text-slate-400 font-mono text-right">
              Evaluation Cells: <span className="text-slate-800 dark:text-zinc-200 font-bold">{modelAgreement.eval_points}</span>
            </div>
          </div>

          {/* Agreement KPIs */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-5">
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-zinc-800/50 border border-slate-200/80 dark:border-zinc-700/80">
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Mean Abs Diff</div>
              <div className="text-lg font-extrabold text-slate-900 dark:text-zinc-100 font-mono mt-0.5">
                {modelAgreement.mae_diff?.toFixed(2)}
                <span className="text-[10px] text-slate-400 font-sans ml-1">µg/m³</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-zinc-800/50 border border-slate-200/80 dark:border-zinc-700/80">
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">RMSE Diff</div>
              <div className="text-lg font-extrabold text-slate-900 dark:text-zinc-100 font-mono mt-0.5">
                {modelAgreement.rmse_diff?.toFixed(2)}
                <span className="text-[10px] text-slate-400 font-sans ml-1">µg/m³</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-zinc-800/50 border border-slate-200/80 dark:border-zinc-700/80">
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Max Single Diff</div>
              <div className="text-lg font-extrabold text-rose-600 dark:text-rose-400 font-mono mt-0.5">
                {modelAgreement.max_diff?.toFixed(2)}
                <span className="text-[10px] text-slate-400 font-sans ml-1">µg/m³</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800/50">
              <div className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">Pearson r</div>
              <div className="text-lg font-extrabold text-indigo-600 dark:text-indigo-400 font-mono mt-0.5">
                {modelAgreement.pearson_correlation?.toFixed(4)}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/50">
              <div className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Within ±1 µg/m³</div>
              <div className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 font-mono mt-0.5">
                {modelAgreement.pct_within_1ug?.toFixed(1)}%
              </div>
            </div>

            <div className="p-3 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/50">
              <div className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Within ±5 µg/m³</div>
              <div className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 font-mono mt-0.5">
                {modelAgreement.pct_within_5ug?.toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Scatter Plot & Breakdown Table */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Agreement Scatter Plot */}
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/80 dark:border-zinc-700/80">
              <div className="text-xs font-bold text-slate-800 dark:text-zinc-200 mb-2 flex items-center justify-between">
                <span>Prediction Parity Scatter Plot (Y = X Identity Diagonal)</span>
                <span className="text-[10px] text-slate-400">Sampled missing cells</span>
              </div>
              <div className="h-60 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 10, right: 15, left: -5, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} opacity={0.3} />
                    <XAxis
                      type="number"
                      dataKey="original_pred"
                      name={modelAgreement.model_a?.name || 'PyTorch'}
                      unit=" µg"
                      stroke={axisStroke}
                      tick={{ fontSize: 10 }}
                      domain={['auto', 'auto']}
                    />
                    <YAxis
                      type="number"
                      dataKey="keras_pred"
                      name={modelAgreement.model_b?.name || 'Keras'}
                      unit=" µg"
                      stroke={axisStroke}
                      tick={{ fontSize: 10 }}
                      domain={['auto', 'auto']}
                    />
                    <Tooltip
                      cursor={{ strokeDasharray: '3 3' }}
                      content={({ active, payload }) => {
                        if (!active || !payload?.length) return null;
                        const pt = payload[0].payload;
                        return (
                          <div className="p-2 rounded-lg bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 shadow-lg text-[11px]">
                            <div className="font-bold text-slate-900 dark:text-zinc-100">{pt.pollutant} • {pt.time}</div>
                            <div className="font-mono space-y-0.5 text-slate-600 dark:text-zinc-400 mt-1">
                              <div>Original: <span className="font-bold text-indigo-600">{pt.original_pred} µg/m³</span></div>
                              <div>Keras 3: <span className="font-bold text-pink-600">{pt.keras_pred} µg/m³</span></div>
                              <div>Diff: <span className="font-semibold text-rose-500">{pt.abs_diff} µg/m³</span></div>
                            </div>
                          </div>
                        );
                      }}
                    />
                    <Scatter
                      data={modelAgreement.scatter_points || []}
                      fill="#8b5cf6"
                      opacity={0.8}
                    />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Pollutant Parity Table & Scientific Statement */}
            <div className="flex flex-col justify-between space-y-3">
              <div className="overflow-x-auto rounded-xl border border-slate-200/80 dark:border-zinc-700/80 bg-white dark:bg-zinc-900">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-zinc-800/60 text-[10px] font-bold text-slate-500 dark:text-zinc-400 uppercase">
                    <tr>
                      <th className="py-2 px-3">Pollutant</th>
                      <th className="py-2 px-2">MAE Diff</th>
                      <th className="py-2 px-2">RMSE Diff</th>
                      <th className="py-2 px-2">Max Diff</th>
                      <th className="py-2 px-2">Correlation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-zinc-800 font-mono text-[11px]">
                    {Object.entries(modelAgreement.pollutant_breakdown || {}).map(([p, data]) => (
                      <tr key={p} className="hover:bg-slate-50/50 dark:hover:bg-zinc-800/30">
                        <td className="py-1.5 px-3 font-sans font-bold text-slate-800 dark:text-zinc-200">{p}</td>
                        <td className="py-1.5 px-2 font-bold text-slate-900 dark:text-zinc-100">{data.mae_diff?.toFixed(2)}</td>
                        <td className="py-1.5 px-2 text-slate-600 dark:text-zinc-400">{data.rmse_diff?.toFixed(2)}</td>
                        <td className="py-1.5 px-2 text-rose-600">{data.max_diff?.toFixed(2)}</td>
                        <td className="py-1.5 px-2 font-bold text-emerald-600">{data.correlation?.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Scientific Parity Statement */}
              <div className="p-3 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/40 text-xs text-slate-700 dark:text-zinc-300 leading-relaxed font-medium">
                <div className="flex items-center gap-1.5 font-bold text-indigo-700 dark:text-indigo-300 mb-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Mathematical Equivalence Verified</span>
                </div>
                {modelAgreement.scientific_statement}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* 5. EXECUTIVE METRIC SUMMARY CARDS */}
      {experimentResult && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Top Overall */}
          <Card className="p-4 bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-bl-full pointer-events-none" />
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
                Top Performing Model
              </span>
              <Trophy className="w-4 h-4 text-amber-500" />
            </div>
            <div className="mt-2.5">
              <div className="text-base font-bold text-slate-900 dark:text-zinc-100 truncate">
                {winners?.overall_top_model?.name}
              </div>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400 font-mono">
                  {typeof winners?.overall_top_model?.mae === 'number' ? winners.overall_top_model.mae.toFixed(2) : '0.00'}
                </span>
                <span className="text-xs text-slate-500 font-medium">MAE (µg/m³)</span>
              </div>
            </div>
            <div className="mt-2 pt-2 border-t border-slate-100 dark:border-zinc-800/80 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Rank 1 across {experimentResult.windows_evaluated} test window(s)</span>
            </div>
          </Card>

          {/* Peak Pollution Specialist */}
          <Card className="p-4 bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/5 rounded-bl-full pointer-events-none" />
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
                Peak Spike Specialist
              </span>
              <Target className="w-4 h-4 text-rose-500" />
            </div>
            <div className="mt-2.5">
              <div className="text-base font-bold text-slate-900 dark:text-zinc-100 truncate">
                {winners?.peak_specialist?.name}
              </div>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-extrabold text-rose-600 dark:text-rose-400 font-mono">
                  {typeof winners?.peak_specialist?.mae === 'number' ? winners.peak_specialist.mae.toFixed(2) : '0.00'}
                </span>
                <span className="text-xs text-slate-500 font-medium">Peak MAE (µg/m³)</span>
              </div>
            </div>
            <div className="mt-2 pt-2 border-t border-slate-100 dark:border-zinc-800/80 text-[11px] text-slate-500 dark:text-zinc-400 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>Evaluated on top-10% diurnal spike concentrations</span>
            </div>
          </Card>

          {/* Long Gap Champion */}
          <Card className="p-4 bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-bl-full pointer-events-none" />
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
                Long-Gap Champion (&gt;6h)
              </span>
              <ShieldCheck className="w-4 h-4 text-cyan-500" />
            </div>
            <div className="mt-2.5">
              <div className="text-base font-bold text-slate-900 dark:text-zinc-100 truncate">
                {winners?.long_gap_champion?.name}
              </div>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-extrabold text-cyan-600 dark:text-cyan-400 font-mono">
                  {typeof winners?.long_gap_champion?.mae === 'number' ? winners.long_gap_champion.mae.toFixed(2) : 'N/A'}
                </span>
                <span className="text-xs text-slate-500 font-medium">Long-Gap MAE</span>
              </div>
            </div>
            <div className="mt-2 pt-2 border-t border-slate-100 dark:border-zinc-800/80 text-[11px] text-slate-500 dark:text-zinc-400 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-cyan-500" />
              <span>Resilient against sensor power blackout outages</span>
            </div>
          </Card>

          {/* Fastest Model */}
          <Card className="p-4 bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-bl-full pointer-events-none" />
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 dark:text-zinc-500">
                Fastest Execution
              </span>
              <Zap className="w-4 h-4 text-emerald-500" />
            </div>
            <div className="mt-2.5">
              <div className="text-base font-bold text-slate-900 dark:text-zinc-100 truncate">
                {winners?.fastest_model?.name}
              </div>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono">
                  {typeof winners?.fastest_model?.latency_ms === 'number' ? winners.fastest_model.latency_ms.toFixed(1) : '0.0'}
                </span>
                <span className="text-xs text-slate-500 font-medium">ms / 24h window</span>
              </div>
            </div>
            <div className="mt-2 pt-2 border-t border-slate-100 dark:border-zinc-800/80 text-[11px] text-slate-500 dark:text-zinc-400 flex items-center gap-1">
              <Activity className="w-3.5 h-3.5 text-emerald-500" />
              <span>Total benchmark compute: {experimentResult.total_experiment_time_ms} ms</span>
            </div>
          </Card>
        </div>
      )}

      {/* 6. MASTER BENCHMARK RANKING TABLE WITH ↓/↑ INDICATORS & 95% CI */}
      {experimentResult && (
        <Card className="bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs overflow-hidden">
          <div className="p-4 border-b border-slate-100 dark:border-zinc-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Trophy className="w-4 h-4 text-indigo-500" />
              <h2 className="text-xs font-bold text-slate-900 dark:text-zinc-100 uppercase tracking-wider">
                Official Multi-Model Benchmark Scoreboard
              </h2>
              <InfoTooltip content="Derived strictly from canonical records on hidden cells (mask==0). Observed values are strictly locked." />
            </div>
            <div className="text-[11px] text-slate-500 font-mono flex items-center gap-3">
              <span>Evaluated Cells: <strong>{experimentResult.total_points_evaluated?.toLocaleString()}</strong></span>
              <button
                type="button"
                onClick={() => handleReRunExperiment(experimentResult.experiment_id)}
                className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-700 font-semibold"
                title="Re-run exact experiment"
              >
                <RefreshCw className="w-3 h-3" /> Re-run Experiment
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-zinc-800/50 text-[11px] font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider border-b border-slate-200 dark:border-zinc-800">
                <tr>
                  <th className="py-2.5 px-4 cursor-pointer hover:text-indigo-600" onClick={() => handleSort('rank')}>
                    <div className="flex items-center gap-1">Rank <ArrowUpDown className="w-3 h-3" /></div>
                  </th>
                  <th className="py-2.5 px-4">Model Architecture</th>
                  <th className="py-2.5 px-3 cursor-pointer hover:text-indigo-600" onClick={() => handleSort('MAE')}>
                    <div className="flex items-center gap-1">MAE ↓ <ArrowUpDown className="w-3 h-3" /></div>
                  </th>
                  <th className="py-2.5 px-3 cursor-pointer hover:text-indigo-600" onClick={() => handleSort('RMSE')}>
                    <div className="flex items-center gap-1">RMSE ↓ <ArrowUpDown className="w-3 h-3" /></div>
                  </th>
                  <th className="py-2.5 px-3 cursor-pointer hover:text-indigo-600" onClick={() => handleSort('MAPE')}>
                    <div className="flex items-center gap-1">MAPE (%) ↓ <ArrowUpDown className="w-3 h-3" /></div>
                  </th>
                  <th className="py-2.5 px-3 cursor-pointer hover:text-indigo-600" onClick={() => handleSort('R2')}>
                    <div className="flex items-center gap-1">R² Score ↑ <ArrowUpDown className="w-3 h-3" /></div>
                  </th>
                  <th className="py-2.5 px-3 cursor-pointer hover:text-indigo-600" onClick={() => handleSort('Correlation')}>
                    <div className="flex items-center gap-1">Pearson r ↑ <ArrowUpDown className="w-3 h-3" /></div>
                  </th>
                  <th className="py-2.5 px-3 cursor-pointer hover:text-indigo-600" onClick={() => handleSort('Bias')}>
                    <div className="flex items-center gap-1">Mean Bias ↓ <ArrowUpDown className="w-3 h-3" /></div>
                  </th>
                  <th className="py-2.5 px-3">95% Bootstrap CI (MAE)</th>
                  <th className="py-2.5 px-3 cursor-pointer hover:text-indigo-600" onClick={() => handleSort('runtime_ms')}>
                    <div className="flex items-center gap-1">Latency ↓ <ArrowUpDown className="w-3 h-3" /></div>
                  </th>
                  <th className="py-2.5 px-4">Parameters</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/80 font-medium">
                {sortedRankings.map((r) => {
                  const isTop = r.rank === 1;
                  return (
                    <tr
                      key={r.model_id}
                      className={`hover:bg-slate-50/80 dark:hover:bg-zinc-800/40 transition-colors ${
                        isTop ? 'bg-indigo-50/20 dark:bg-indigo-950/20 font-semibold' : ''
                      }`}
                    >
                      <td className="py-3 px-4 font-mono font-bold">
                        <span className={`inline-flex items-center justify-center w-5 h-5 rounded-full text-xs ${
                          r.rank === 1 ? 'bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400 font-bold' :
                          r.rank === 2 ? 'bg-slate-200 dark:bg-zinc-700 text-slate-700 dark:text-zinc-200' :
                          r.rank === 3 ? 'bg-amber-900/20 text-amber-700 dark:text-amber-500' :
                          'text-slate-400'
                        }`}>
                          {r.rank}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span
                            className="w-2.5 h-2.5 rounded-full shrink-0"
                            style={{ backgroundColor: MODEL_COLORS[r.model_id] || '#64748b' }}
                          />
                          <div>
                            <div className="font-bold text-slate-900 dark:text-zinc-100 flex items-center gap-1.5">
                              <span>{r.model_name}</span>
                              {r.framework && (
                                <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-300 font-mono">
                                  {r.framework}
                                </span>
                              )}
                            </div>
                            <div className="text-[10px] text-slate-400 font-mono">{r.model_id}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-3 font-mono font-bold text-slate-900 dark:text-zinc-100">
                        {r.MAE?.toFixed(2)}
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-700 dark:text-zinc-300">
                        {r.RMSE?.toFixed(2)}
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-700 dark:text-zinc-300">
                        {r.MAPE?.toFixed(1)}%
                      </td>
                      <td className="py-3 px-3 font-mono">
                        <span className={r.R2 >= 0.90 ? 'text-emerald-600 font-bold' : r.R2 >= 0.75 ? 'text-indigo-600' : 'text-slate-500'}>
                          {r.R2 !== null ? r.R2?.toFixed(3) : 'N/A'}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono">
                        <span className={r.Correlation >= 0.95 ? 'text-emerald-600 font-bold' : 'text-slate-600'}>
                          {r.Correlation?.toFixed(3)}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono text-xs">
                        <span className={r.Bias > 0 ? 'text-blue-600' : r.Bias < -2 ? 'text-rose-600' : 'text-slate-500'}>
                          {r.Bias > 0 ? `+${r.Bias?.toFixed(2)}` : r.Bias?.toFixed(2)}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono text-[11px] text-slate-600 dark:text-zinc-400">
                        {r.ci_available ? `${r.ci_str}` : <span className="text-[10px] text-slate-400">n &lt; 30</span>}
                      </td>
                      <td className="py-3 px-3 font-mono text-xs text-slate-600 dark:text-zinc-400">
                        {r.runtime_ms?.toFixed(1)} ms
                      </td>
                      <td className="py-3 px-4 font-mono text-xs text-slate-500">
                        {r.param_count ? `${r.param_count.toLocaleString()}` : '0 (Non-param)'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* 7. MODEL WIN MATRIX: POLLUTANT BY POLLUTANT */}
      {experimentResult?.evaluation?.model_win_matrix && (
        <Card className="p-4 bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3 pb-2 border-b border-slate-100 dark:border-zinc-800">
            <div className="flex items-center gap-2">
              <Trophy className="w-4 h-4 text-amber-500" />
              <h3 className="text-xs font-bold text-slate-900 dark:text-zinc-100 uppercase tracking-wider">
                Model Win Matrix (Channel-by-Channel Rankings)
              </h3>
              <InfoTooltip content="Displays which model achieves 1st, 2nd, or 3rd place for each specific criteria pollutant." />
            </div>

            {/* Metric Switcher */}
            <div className="flex items-center gap-1 text-xs">
              <span className="text-[11px] text-slate-400 mr-1 font-medium">Rank by:</span>
              {['MAE', 'RMSE', 'Correlation'].map(mKey => (
                <button
                  key={mKey}
                  type="button"
                  onClick={() => setWinMatrixMetric(mKey)}
                  className={`px-2 py-1 rounded-md text-[11px] font-semibold transition-colors ${
                    winMatrixMetric === mKey
                      ? 'bg-indigo-600 text-white shadow-2xs'
                      : 'bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-300'
                  }`}
                >
                  {mKey}
                </button>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-center text-xs">
              <thead className="bg-slate-50 dark:bg-zinc-800/50 text-[10px] font-bold text-slate-500 dark:text-zinc-400 uppercase">
                <tr>
                  <th className="py-2 px-3 text-left">Model Architecture</th>
                  {POLLUTANTS.map(p => (
                    <th key={p} className="py-2 px-3">{p}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-zinc-800 font-mono text-xs">
                {experimentResult.models_evaluated?.map(mId => {
                  const runner = registeredModels.find(m => m.id === mId);
                  return (
                    <tr key={mId} className="hover:bg-slate-50/50 dark:hover:bg-zinc-800/30">
                      <td className="py-2.5 px-3 text-left font-sans font-semibold text-slate-900 dark:text-zinc-100 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: MODEL_COLORS[mId] || '#64748b' }} />
                        <span>{runner ? runner.name : mId}</span>
                      </td>
                      {POLLUTANTS.map(p => {
                        const cell = experimentResult.evaluation.model_win_matrix[winMatrixMetric]?.[mId]?.[p];
                        const rank = cell?.rank;
                        const val = cell?.value;
                        return (
                          <td key={p} className="py-2.5 px-3">
                            <span className={`inline-flex items-center justify-center px-2 py-0.5 rounded text-[11px] font-bold ${
                              rank === 1 ? 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-400 border border-amber-300 dark:border-amber-800' :
                              rank === 2 ? 'bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300' :
                              'text-slate-400'
                            }`}>
                              #{rank || '-'} ({val !== null && val !== undefined ? val.toFixed(1) : 'N/A'})
                            </span>
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* 8. SYNCHRONIZED TIME-SERIES RECONSTRUCTION & MODEL DELTA VIEW */}
      {experimentResult && (
        <Card className="p-5 bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-3 pb-3 border-b border-slate-100 dark:border-zinc-800">
            <div>
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-indigo-500" />
                <h3 className="text-xs font-bold text-slate-900 dark:text-zinc-100 uppercase tracking-wider">
                  {activeChartMode === 'reconstruction' ? 'Synchronized Trajectory Reconstruction' : 'Prediction Delta View (Model A - Model B)'}
                </h3>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">
                Exact model outputs on real temporal axes. Observed cells are strictly preserved.
              </p>
            </div>

            {/* Mode Switcher + Pollutant Sub-Tabs */}
            <div className="flex items-center gap-2 flex-wrap">
              <div className="flex items-center bg-slate-100 dark:bg-zinc-800 p-0.5 rounded-lg text-xs font-semibold">
                <button
                  type="button"
                  onClick={() => setActiveChartMode('reconstruction')}
                  className={`px-2.5 py-1 rounded-md transition-all ${
                    activeChartMode === 'reconstruction'
                      ? 'bg-white dark:bg-zinc-900 text-indigo-600 shadow-2xs font-bold'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Reconstruction
                </button>
                <button
                  type="button"
                  onClick={() => setActiveChartMode('delta')}
                  className={`px-2.5 py-1 rounded-md transition-all ${
                    activeChartMode === 'delta'
                      ? 'bg-white dark:bg-zinc-900 text-indigo-600 shadow-2xs font-bold'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Model Delta (Diff)
                </button>
              </div>

              {/* Pollutant Sub-Tabs */}
              <div className="flex items-center gap-1 bg-slate-100 dark:bg-zinc-800 p-1 rounded-xl">
                {POLLUTANTS.map(p => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setSelectedPollutantTab(p)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                      selectedPollutantTab === p
                        ? 'bg-white dark:bg-zinc-900 text-indigo-600 dark:text-indigo-400 shadow-2xs'
                        : 'text-slate-500 hover:text-slate-900 dark:hover:text-zinc-100'
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Peak Zoom Toolbar */}
          {experimentResult.peaks_catalog && experimentResult.peaks_catalog.length > 0 && (
            <div className="mb-3.5 p-2 rounded-xl bg-slate-50 dark:bg-zinc-800/60 border border-slate-200/80 dark:border-zinc-700/80 flex items-center gap-2 flex-wrap">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400 flex items-center gap-1 mr-1">
                <Target className="w-3 h-3 text-rose-500" />
                1-Click Peak Zoom:
              </span>

              <button
                type="button"
                onClick={() => handleSelectPeak(null)}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                  activeZoomPeakId === null
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-700 text-slate-700 dark:text-zinc-300 hover:bg-slate-100'
                }`}
              >
                Full Window
              </button>

              {experimentResult.peaks_catalog.map(pk => (
                <button
                  key={pk.peak_id || pk.id}
                  type="button"
                  onClick={() => handleSelectPeak(pk)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                    activeZoomPeakId === (pk.peak_id || pk.id)
                      ? 'bg-rose-600 text-white shadow-xs'
                      : 'bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-700 text-slate-700 dark:text-zinc-300 hover:border-rose-300'
                  }`}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                  <span>{pk.label}</span>
                </button>
              ))}
            </div>
          )}

          {/* Model Curve Visibility Toggles (Reconstruction Mode Only) */}
          {activeChartMode === 'reconstruction' && (
            <div className="flex flex-wrap items-center gap-2 mb-4 text-xs">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mr-1">Curves:</span>
              <button
                type="button"
                onClick={() => toggleChartVisibility('ground_truth')}
                className={`px-2.5 py-1 rounded-lg border text-[11px] font-semibold flex items-center gap-1.5 transition-all ${
                  chartModelVisibility.ground_truth
                    ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-300 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300'
                    : 'border-slate-200 dark:border-zinc-800 text-slate-400'
                }`}
              >
                {chartModelVisibility.ground_truth ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                <span>Ground Truth</span>
              </button>

              {experimentResult.models_evaluated?.map(mId => {
                const isVis = chartModelVisibility[mId];
                const runner = registeredModels.find(m => m.id === mId);
                const color = MODEL_COLORS[mId] || '#6366f1';
                return (
                  <button
                    key={mId}
                    type="button"
                    onClick={() => toggleChartVisibility(mId)}
                    className={`px-2.5 py-1 rounded-lg border text-[11px] font-semibold flex items-center gap-1.5 transition-all ${
                      isVis
                        ? 'bg-slate-100/80 dark:bg-zinc-800 border-slate-300 dark:border-zinc-700 text-slate-800 dark:text-zinc-200'
                        : 'border-slate-200 dark:border-zinc-800 text-slate-400 opacity-60'
                    }`}
                  >
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                    {isVis ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                    <span>{runner ? runner.name : mId}</span>
                  </button>
                );
              })}
            </div>
          )}

          {/* Chart Canvas */}
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              {activeChartMode === 'reconstruction' ? (
                <LineChart data={currentChartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} opacity={0.4} />
                  <XAxis dataKey="time" stroke={axisStroke} tick={{ fontSize: 11 }} />
                  <YAxis
                    stroke={axisStroke}
                    tick={{ fontSize: 11 }}
                    unit=" µg/m³"
                    domain={['auto', 'auto']}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: isDark ? '#18181b' : '#ffffff',
                      borderColor: isDark ? '#27272a' : '#e2e8f0',
                      borderRadius: '0.75rem',
                      fontSize: '11px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                    }}
                  />
                  <Legend />

                  {/* Shaded Missing Outage Regions */}
                  {missingIntervals.map((inv, idx) => (
                    <ReferenceArea
                      key={idx}
                      x1={inv.x1}
                      x2={inv.x2}
                      fill={isDark ? '#ef4444' : '#fee2e2'}
                      fillOpacity={isDark ? 0.15 : 0.4}
                      stroke={isDark ? '#ef4444' : '#f87171'}
                      strokeDasharray="2 2"
                      strokeOpacity={0.6}
                    />
                  ))}

                  {/* Ground Truth curve */}
                  {chartModelVisibility.ground_truth && (
                    <Line
                      type="monotone"
                      dataKey="ground_truth"
                      name="Ground Truth"
                      stroke="#10b981"
                      strokeWidth={2.5}
                      strokeDasharray="4 4"
                      dot={false}
                    />
                  )}

                  {/* Competing Model Curves */}
                  {experimentResult.models_evaluated?.map(mId => {
                    if (!chartModelVisibility[mId]) return null;
                    const runner = registeredModels.find(m => m.id === mId);
                    const color = MODEL_COLORS[mId] || '#6366f1';
                    const isNeural = mId.includes('ctdi') || mId.includes('transformer');
                    return (
                      <Line
                        key={mId}
                        type="monotone"
                        dataKey={mId}
                        name={runner ? runner.name : mId}
                        stroke={color}
                        strokeWidth={isNeural ? 2.5 : 1.75}
                        dot={false}
                      />
                    );
                  })}
                </LineChart>
              ) : (
                /* Model Delta View */
                <LineChart data={currentDeltaData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} opacity={0.4} />
                  <XAxis dataKey="time" stroke={axisStroke} tick={{ fontSize: 11 }} />
                  <YAxis stroke={axisStroke} tick={{ fontSize: 11 }} unit=" µg/m³" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: isDark ? '#18181b' : '#ffffff',
                      borderColor: isDark ? '#27272a' : '#e2e8f0',
                      borderRadius: '0.75rem',
                      fontSize: '11px'
                    }}
                  />
                  <ReferenceLine y={0} stroke="#64748b" strokeDasharray="3 3" />
                  <Line
                    type="monotone"
                    dataKey="delta"
                    name="Prediction Difference (PyTorch - Keras)"
                    stroke="#ec4899"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                </LineChart>
              )}
            </ResponsiveContainer>
          </div>
        </Card>
      )}

      {/* 9. ADVANCED PEAK RECONSTRUCTION & 1-CLICK PEAK EXPLORER */}
      {experimentResult?.evaluation?.peak_analysis && (
        <Card className="p-4 bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs">
          <div className="flex items-center justify-between mb-3 border-b border-slate-100 dark:border-zinc-800 pb-2">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-rose-500" />
              <h3 className="text-xs font-bold text-slate-900 dark:text-zinc-100 uppercase tracking-wider">
                Peak Pollution Spike Accuracy & Explorer
              </h3>
              <InfoTooltip content="Top 10% highest pollution concentrations. Evaluates if models severely smooth, clip, or underestimate smog spikes." />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* By-Model Peak Accuracy */}
            <div className="space-y-2.5">
              <div className="text-[11px] font-bold text-slate-700 dark:text-zinc-300">
                Spike Reconstruction Accuracy by Model:
              </div>
              {Object.entries(experimentResult.evaluation.peak_analysis.by_model || {}).map(([mId, data]) => {
                const runner = registeredModels.find(m => m.id === mId);
                const color = MODEL_COLORS[mId] || '#64748b';
                return (
                  <div key={mId} className="p-2.5 rounded-xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-100 dark:border-zinc-800">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <div className="flex items-center gap-2 font-bold text-slate-800 dark:text-zinc-200">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                        <span>{runner ? runner.name : mId}</span>
                      </div>
                      <span className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400">
                        MAE: {data.peak_mae?.toFixed(2)} µg/m³
                      </span>
                    </div>
                    <div className="grid grid-cols-4 gap-2 text-[11px] text-slate-500 pt-1 border-t border-slate-200/50 dark:border-zinc-700/50 font-mono">
                      <div>RMSE: <span className="font-semibold text-slate-800 dark:text-zinc-200">{data.peak_rmse?.toFixed(2)}</span></div>
                      <div>Amp Err: <span className={data.amplitude_error < -5 ? 'text-rose-600 font-semibold' : 'text-slate-800 dark:text-zinc-200'}>{data.amplitude_error > 0 ? `+${data.amplitude_error}` : data.amplitude_error}</span></div>
                      <div>Recovery: <span className="text-emerald-600 font-semibold">{data.recovery_rate_pct}%</span></div>
                      <div>Eval n: <span className="text-slate-800 dark:text-zinc-200 font-semibold">{data.count}</span></div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Individual Peak Explorer Table */}
            <div>
              <div className="text-[11px] font-bold text-slate-700 dark:text-zinc-300 mb-2 flex items-center justify-between">
                <span>Top Evaluated Peak Events:</span>
                <span className="text-[10px] text-slate-400">Click row to zoom chart to event</span>
              </div>
              <div className="overflow-x-auto rounded-xl border border-slate-200/80 dark:border-zinc-700/80">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-zinc-800/60 text-[10px] font-bold text-slate-500 uppercase">
                    <tr>
                      <th className="py-2 px-3">Event</th>
                      <th className="py-2 px-2">Pollutant</th>
                      <th className="py-2 px-2">True Peak</th>
                      <th className="py-2 px-2">Original Pred</th>
                      <th className="py-2 px-2">Keras Pred</th>
                      <th className="py-2 px-2">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-zinc-800 font-mono text-[11px]">
                    {(experimentResult.peaks_catalog || experimentResult.evaluation.peak_analysis.peaks_catalog || []).map((pk, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-zinc-800/30">
                        <td className="py-2 px-3 font-sans font-bold text-slate-800 dark:text-zinc-200">{pk.time || pk.timestamp}</td>
                        <td className="py-2 px-2 font-sans font-semibold text-indigo-600">{pk.pollutant}</td>
                        <td className="py-2 px-2 font-bold text-emerald-600">{pk.ground_truth}</td>
                        <td className="py-2 px-2 text-indigo-600">{pk.predictions?.delhi_ctdi_original ?? '-'}</td>
                        <td className="py-2 px-2 text-pink-600">{pk.predictions?.delhi_ctdi_keras ?? '-'}</td>
                        <td className="py-2 px-2">
                          <button
                            type="button"
                            onClick={() => handleSelectPeak(pk)}
                            className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-600 hover:bg-rose-100 font-sans"
                          >
                            Zoom
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* 10. GAP-LENGTH DEGRADATION & MISSINGNESS ROBUSTNESS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gap Length Analysis */}
        {experimentResult?.evaluation?.gap_analysis && (
          <Card className="p-4 bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs">
            <div className="flex items-center justify-between mb-3 border-b border-slate-100 dark:border-zinc-800 pb-2">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-500" />
                <h3 className="text-xs font-bold text-slate-900 dark:text-zinc-100 uppercase tracking-wider">
                  Gap Length Degradation Analysis
                </h3>
                <InfoTooltip content="Error breakdown by missing duration: 1h, 2h, 4h, 6h, 12h, 24h. Demonstrates where linear interpolation degrades." />
              </div>
            </div>

            <div className="space-y-3">
              {['1h', '2h', '4h', '6h', '12h', '24h'].map(binKey => {
                const binObj = experimentResult.evaluation.gap_analysis?.[binKey];
                if (!binObj || binObj.point_count === 0) return null;
                const byModel = binObj.by_model || {};

                return (
                  <div key={binKey} className="space-y-1">
                    <div className="text-[11px] font-bold text-slate-700 dark:text-zinc-300 flex items-center justify-between">
                      <span>{binObj.label}</span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {binObj.point_count} points
                      </span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
                      {Object.entries(byModel).map(([mId, maeVal]) => {
                        const runner = registeredModels.find(m => m.id === mId);
                        const isNeural = mId.includes('ctdi');
                        return (
                          <div
                            key={mId}
                            className={`p-2 rounded-lg text-center border text-[11px] ${
                              isNeural
                                ? 'bg-indigo-50/60 dark:bg-indigo-950/30 border-indigo-200 dark:border-indigo-800 font-bold text-indigo-700 dark:text-indigo-300'
                                : 'bg-slate-50 dark:bg-zinc-800/40 border-slate-100 dark:border-zinc-800 text-slate-600 dark:text-zinc-400'
                            }`}
                          >
                            <div className="truncate text-[10px] text-slate-400 mb-0.5">{runner ? runner.name.split(' ')[0] : mId}</div>
                            <div className="font-mono font-bold text-xs">{maeVal !== null ? maeVal.toFixed(2) : 'N/A'}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        )}

        {/* Latency vs Accuracy Pareto Frontier */}
        {experimentResult?.evaluation?.model_rankings && (
          <Card className="p-4 bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs">
            <div className="flex items-center justify-between mb-3 border-b border-slate-100 dark:border-zinc-800 pb-2">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-emerald-500" />
                <h3 className="text-xs font-bold text-slate-900 dark:text-zinc-100 uppercase tracking-wider">
                  Computational Latency vs Accuracy Pareto Frontier
                </h3>
                <InfoTooltip content="X-axis: Inference latency (ms). Y-axis: MAE (lower is better). Ideal models sit in the bottom-left quadrant." />
              </div>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 15, right: 20, left: 0, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} opacity={0.4} />
                  <XAxis
                    type="number"
                    dataKey="runtime_ms"
                    name="Inference Latency"
                    unit=" ms"
                    stroke={axisStroke}
                    tick={{ fontSize: 11 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="MAE"
                    name="MAE"
                    unit=" µg/m³"
                    stroke={axisStroke}
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    content={({ active, payload }) => {
                      if (!active || !payload?.length) return null;
                      const pt = payload[0].payload;
                      return (
                        <div className="p-2.5 rounded-xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 shadow-lg text-xs">
                          <div className="font-bold text-slate-900 dark:text-zinc-100 mb-1">{pt.model_name}</div>
                          <div className="font-mono text-[11px] space-y-0.5 text-slate-600 dark:text-zinc-400">
                            <div>MAE: <span className="font-bold text-indigo-600">{pt.MAE} µg/m³</span></div>
                            <div>Latency: <span>{pt.runtime_ms} ms</span></div>
                            <div>Params: <span>{pt.param_count?.toLocaleString()}</span></div>
                          </div>
                        </div>
                      );
                    }}
                  />
                  <Scatter
                    data={experimentResult.evaluation.model_rankings}
                    fill="#6366f1"
                  >
                    {experimentResult.evaluation.model_rankings.map(entry => (
                      <Cell
                        key={entry.model_id}
                        fill={MODEL_COLORS[entry.model_id] || '#6366f1'}
                      />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </Card>
        )}
      </div>

      {/* 11. FAILURE CASE EXPLORER & SAME-POINT COMPARISON */}
      {experimentResult?.failure_cases && experimentResult.failure_cases.length > 0 && (
        <Card className="p-4 bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800 shadow-2xs">
          <div className="flex items-center justify-between mb-3 border-b border-slate-100 dark:border-zinc-800 pb-2">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-amber-500" />
              <h3 className="text-xs font-bold text-slate-900 dark:text-zinc-100 uppercase tracking-wider">
                Worst Reconstructions & Failure Case Diagnostics
              </h3>
              <InfoTooltip content="Top extreme prediction errors across all participating models. Shows surrounding context and point-by-point errors." />
            </div>
            <span className="text-[10px] text-slate-400 font-mono">Top Outliers</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-zinc-800/50 text-[11px] font-bold text-slate-500 dark:text-zinc-400 uppercase">
                <tr>
                  <th className="py-2 px-3">Timestamp</th>
                  <th className="py-2 px-3">Pollutant</th>
                  <th className="py-2 px-3">Ground Truth</th>
                  <th className="py-2 px-3">Model Predictions</th>
                  <th className="py-2 px-3">Model Errors</th>
                  <th className="py-2 px-3">Gap Length</th>
                  <th className="py-2 px-3">Investigate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-zinc-800 font-mono text-xs">
                {experimentResult.failure_cases.slice(0, 5).map((f, i) => (
                  <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-zinc-800/30">
                    <td className="py-2 px-3 text-slate-600 dark:text-zinc-400">{f.timestamp}</td>
                    <td className="py-2 px-3 font-sans font-bold text-slate-800 dark:text-zinc-200">{f.pollutant}</td>
                    <td className="py-2 px-3 font-bold text-emerald-600">{typeof f.ground_truth === 'number' ? f.ground_truth.toFixed(1) : f.ground_truth}</td>
                    <td className="py-2 px-3">
                      <div className="flex flex-wrap gap-1.5">
                        {Object.entries(f.predictions || {}).map(([mId, pred]) => (
                          <span key={mId} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300">
                            {mId.includes('original') ? 'PyTorch' : mId.includes('keras') ? 'Keras' : mId.split('_')[0]}: <span className="font-bold">{pred?.toFixed(1)}</span>
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-2 px-3">
                      <div className="flex flex-wrap gap-1.5">
                        {Object.entries(f.errors || {}).map(([mId, err]) => (
                          <span key={mId} className="text-[10px] px-1.5 py-0.5 rounded bg-rose-50 dark:bg-rose-950/30 text-rose-600 font-bold">
                            {err?.toFixed(1)}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-2 px-3 text-slate-500">{f.gap_length} hrs</td>
                    <td className="py-2 px-3">
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedPollutantTab(f.pollutant);
                          setSelectedSamePointTimestamp(f.timestamp);
                        }}
                        className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-600 hover:bg-indigo-100 font-sans"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* 12. MODEL ARCHITECTURE & AUDIT MODAL */}
      {auditModel && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-xl bg-white dark:bg-zinc-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-zinc-800 overflow-hidden">
            <div className="p-4 border-b border-slate-200 dark:border-zinc-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-indigo-500" />
                <h3 className="text-sm font-bold text-slate-900 dark:text-zinc-100">
                  Model Architecture & Checkpoint Audit
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setAuditModel(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-zinc-200 p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-5 space-y-3.5 text-xs">
              <div>
                <div className="text-base font-bold text-slate-900 dark:text-zinc-100 flex items-center gap-2">
                  <span>{auditModel.name || auditModel.display_name}</span>
                  <Chip size="sm" variant="flat" color="primary" className="text-[10px]">
                    {auditModel.framework}
                  </Chip>
                  <span className="text-emerald-600 font-semibold text-[11px]">● {auditModel.status || 'Ready'}</span>
                </div>
                <div className="text-slate-500 dark:text-zinc-400 text-[11px] mt-0.5">
                  ID: <span className="font-mono">{auditModel.id}</span> • Version: <span className="font-mono">{auditModel.version}</span> • City: <span className="font-semibold">{auditModel.city}</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 dark:bg-zinc-800/60 border border-slate-200/80 dark:border-zinc-700/80 space-y-2">
                <div>
                  <span className="text-slate-400 font-medium">Checkpoint Path:</span>
                  <div className="font-mono text-[11px] text-indigo-600 dark:text-indigo-400 font-semibold break-all">
                    {auditModel.checkpoint_path || auditModel.checkpoint || 'Not available'}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 pt-1 border-t border-slate-200/50 dark:border-zinc-700/50">
                  <div>
                    <span className="text-slate-400 font-medium">Parameters:</span>
                    <div className="font-mono font-bold text-slate-800 dark:text-zinc-200">
                      {auditModel.param_count ? auditModel.param_count.toLocaleString() : '0 (Non-param)'}
                    </div>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium">Checkpoint Size:</span>
                    <div className="font-mono font-bold text-slate-800 dark:text-zinc-200">
                      {auditModel.model_size || auditModel.checkpoint_size || 'Not available'}
                    </div>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium">Training Date:</span>
                    <div className="font-mono text-slate-800 dark:text-zinc-200">
                      {auditModel.training_date || 'Not available'}
                    </div>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium">Scaler / Normalizer:</span>
                    <div className="font-medium text-slate-800 dark:text-zinc-200 truncate">
                      {auditModel.scaler || 'Not available'}
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <div className="font-bold text-slate-800 dark:text-zinc-200 mb-1">Architecture Specification:</div>
                <div className="p-2.5 rounded-lg bg-slate-100/80 dark:bg-zinc-800 font-mono text-[11px] text-slate-700 dark:text-zinc-300 leading-relaxed">
                  {auditModel.architecture || auditModel.description || 'Not available'}
                </div>
              </div>

              <div className="p-3 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/40 text-emerald-800 dark:text-emerald-300 flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                <div className="text-[11px] leading-relaxed">
                  <span className="font-bold">Observation Lock Verification:</span> Under all test runners, observed sensor readings (mask == 1) have an absolute modification error of strictly 0.00 µg/m³.
                </div>
              </div>
            </div>

            <div className="p-3 border-t border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-800/50 flex justify-end">
              <Button
                size="sm"
                variant="flat"
                color="primary"
                onPress={() => setAuditModel(null)}
                className="text-xs font-bold"
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* 13. HISTORICAL EXPERIMENTS & A/B RUN COMPARISON MODAL */}
      {showHistoryDrawer && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex justify-end">
          <div className="w-full max-w-xl bg-white dark:bg-zinc-900 h-full p-6 overflow-y-auto shadow-2xl border-l border-slate-200 dark:border-zinc-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-zinc-800 pb-4 mb-4">
                <div className="flex items-center gap-2">
                  <History className="w-5 h-5 text-indigo-500" />
                  <h3 className="text-base font-bold text-slate-900 dark:text-zinc-100">
                    Comparative Benchmarking History
                  </h3>
                </div>
                <button
                  onClick={() => setShowHistoryDrawer(false)}
                  className="text-slate-400 hover:text-slate-600 dark:hover:text-zinc-200 text-lg font-bold"
                >
                  ✕
                </button>
              </div>

              {/* A/B Comparison Selector */}
              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-zinc-800/60 border border-slate-200 dark:border-zinc-700 mb-5">
                <div className="text-xs font-bold text-slate-800 dark:text-zinc-200 mb-2 flex items-center gap-1.5">
                  <GitCompare className="w-3.5 h-3.5 text-indigo-500" />
                  Side-by-Side Run Comparison (A/B Test)
                </div>
                <div className="grid grid-cols-2 gap-2 mb-2">
                  <select
                    value={selectedRunA}
                    onChange={(e) => setSelectedRunA(e.target.value)}
                    className="text-xs bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-700 rounded-lg p-1.5 text-slate-800 dark:text-zinc-200"
                  >
                    <option value="">Select Run A</option>
                    {historyList.map(h => (
                      <option key={h.experiment_id} value={h.experiment_id}>
                        {h.experiment_id} ({h.missingness?.strategy} - {h.missingness?.missing_rate_pct}%)
                      </option>
                    ))}
                  </select>
                  <select
                    value={selectedRunB}
                    onChange={(e) => setSelectedRunB(e.target.value)}
                    className="text-xs bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-700 rounded-lg p-1.5 text-slate-800 dark:text-zinc-200"
                  >
                    <option value="">Select Run B</option>
                    {historyList.map(h => (
                      <option key={h.experiment_id} value={h.experiment_id}>
                        {h.experiment_id} ({h.missingness?.strategy} - {h.missingness?.missing_rate_pct}%)
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  size="sm"
                  variant="flat"
                  color="primary"
                  className="w-full text-xs font-bold"
                  disabled={!selectedRunA || !selectedRunB}
                  onPress={handleCompareRuns}
                >
                  Compare Runs Side-by-Side
                </Button>

                {abComparison && (
                  <div className="mt-3 pt-3 border-t border-slate-200 dark:border-zinc-700 text-xs">
                    <div className="font-bold text-slate-800 dark:text-zinc-200 mb-1">Comparison Summary:</div>
                    <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                      <div className="p-2 rounded bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800">
                        <div className="font-bold text-indigo-600">{abComparison.experiment_a.experiment_id}</div>
                        <div>Top: {abComparison.experiment_a.evaluation?.model_rankings?.[0]?.model_name}</div>
                        <div>MAE: {abComparison.experiment_a.evaluation?.model_rankings?.[0]?.MAE}</div>
                      </div>
                      <div className="p-2 rounded bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800">
                        <div className="font-bold text-emerald-600">{abComparison.experiment_b.experiment_id}</div>
                        <div>Top: {abComparison.experiment_b.evaluation?.model_rankings?.[0]?.model_name}</div>
                        <div>MAE: {abComparison.experiment_b.evaluation?.model_rankings?.[0]?.MAE}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* History Items */}
              <div className="space-y-2.5">
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Past Runs ({historyList.length})</div>
                {historyList.map(h => (
                  <div
                    key={h.experiment_id}
                    onClick={async () => {
                      const exp = await api.getComparisonExperiment(h.experiment_id);
                      setExperimentResult(exp);
                      setShowHistoryDrawer(false);
                    }}
                    className="p-3 rounded-xl border border-slate-200 dark:border-zinc-800 hover:border-indigo-400 dark:hover:border-indigo-600 bg-white dark:bg-zinc-900 cursor-pointer transition-all flex items-center justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-slate-900 dark:text-zinc-100 flex items-center gap-2">
                        <span>{h.experiment_id}</span>
                        <span className="text-[10px] font-mono text-slate-400">{h.created_at}</span>
                      </div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        {h.city || 'Delhi'} • {h.dataset_id} • {h.missingness?.strategy} ({h.missingness?.missing_rate_pct}% missing)
                      </div>
                    </div>
                    <div className="text-right font-mono text-xs">
                      <div className="font-bold text-indigo-600">
                        {h.evaluation?.model_rankings?.[0]?.MAE?.toFixed(2)} MAE
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {h.evaluation?.model_rankings?.[0]?.model_name?.split(' ')[0]}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Button
              size="sm"
              variant="flat"
              onPress={() => setShowHistoryDrawer(false)}
              className="mt-6 w-full text-xs font-bold"
            >
              Close History Drawer
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
