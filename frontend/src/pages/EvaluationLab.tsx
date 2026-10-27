import React, { useState, useEffect } from 'react';
import { 
  FlaskConical, 
  Play, 
  RotateCw, 
  CheckCircle2, 
  XCircle,
  BarChart3, 
  Download, 
  Info, 
  Layers, 
  Sparkles, 
  Database, 
  HardDrive, 
  Cpu, 
  BookOpen, 
  Trash2, 
  AlertCircle,
  ChevronDown,
  ChevronUp,
  FileText,
  Sliders,
  Filter,
  GitCompare,
  Bot,
  Users,
  Split
} from 'lucide-react';
import { api } from '../services/api';
import { 
  EvaluationExperiment, 
  FEVERStatus, 
  HaluEvalStatus, 
  EvaluationPrediction,
  MultiModelComparisonResponse
} from '../types';

interface EvaluationLabProps {
  experiments: EvaluationExperiment[];
  onRefresh: () => void;
}

export const EvaluationLab: React.FC<EvaluationLabProps> = ({ experiments, onRefresh }) => {
  const [benchmarkName, setBenchmarkName] = useState<'FEVER' | 'HaluEval' | 'TruthfulQA'>('HaluEval');
  const [sampleSize, setSampleSize] = useState<number>(20);
  const [topK, setTopK] = useState<number>(3);
  const [evalSource, setEvalSource] = useState<'context' | 'fever' | 'documents'>('context');
  const [feverSplit, setFeverSplit] = useState<'paper_dev' | 'train'>('paper_dev');
  const [sampleLimit, setSampleLimit] = useState<number>(1000);

  // HaluEval parameters
  const [haluTask, setHaluTask] = useState<'qa' | 'dialogue' | 'summarization' | 'general'>('qa');
  const [haluStrategy, setHaluStrategy] = useState<'balanced_sampled' | 'balanced_paired'>('balanced_sampled');
  const [seed, setSeed] = useState<number>(42);
  const [activeManagerTab, setActiveManagerTab] = useState<'halueval' | 'fever'>('halueval');
  
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [currentExp, setCurrentExp] = useState<EvaluationExperiment | null>(
    experiments.length > 0 ? experiments[0] : null
  );

  // Prediction inspection state
  const [predictions, setPredictions] = useState<EvaluationPrediction[]>([]);
  const [loadingPredictions, setLoadingPredictions] = useState(false);
  const [expandedPredId, setExpandedPredId] = useState<string | null>(null);
  const [predictionFilter, setPredictionFilter] = useState<'all' | 'errors' | 'hallucinated' | 'faithful'>('all');

  // FEVER Dataset & Knowledge Base Manager State
  const [feverStatus, setFeverStatus] = useState<FEVERStatus | null>(null);
  const [isPreparing, setIsPreparing] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);

  // HaluEval Dataset Manager State
  const [haluStatus, setHaluStatus] = useState<HaluEvalStatus | null>(null);
  const [isLoadingHaluStatus, setIsLoadingHaluStatus] = useState(false);

  // Multi-Model Comparison State
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResult, setComparisonResult] = useState<MultiModelComparisonResponse | null>(null);
  const [compareBenchmark, setCompareBenchmark] = useState<'HaluEval' | 'FEVER'>('HaluEval');
  const [compareTask, setCompareTask] = useState<'qa' | 'dialogue' | 'summarization' | 'general'>('qa');
  const [compareSampleSize, setCompareSampleSize] = useState<number>(10);
  const [compareLlmModel, setCompareLlmModel] = useState<string>('qwen3:8b');
  const [expandedDisagreementId, setExpandedDisagreementId] = useState<string | null>(null);

  const fetchFEVERStatus = async () => {
    try {
      const status = await api.getFEVERStatus();
      setFeverStatus(status);
    } catch (err: any) {
      console.warn("Could not fetch FEVER status:", err);
    }
  };

  const fetchHaluEvalStatus = async () => {
    setIsLoadingHaluStatus(true);
    try {
      const status = await api.getHaluEvalStatus();
      setHaluStatus(status);
    } catch (err: any) {
      console.warn("Could not fetch HaluEval status:", err);
    } finally {
      setIsLoadingHaluStatus(false);
    }
  };

  const fetchPredictions = async (expId: string) => {
    setLoadingPredictions(true);
    try {
      const preds = await api.getEvaluationPredictions(expId);
      setPredictions(preds || []);
    } catch (err: any) {
      console.warn("Could not fetch predictions:", err);
      if (currentExp?.metrics?.predictions) {
        setPredictions(currentExp.metrics.predictions);
      } else {
        setPredictions([]);
      }
    } finally {
      setLoadingPredictions(false);
    }
  };

  useEffect(() => {
    fetchFEVERStatus();
    fetchHaluEvalStatus();
  }, []);

  useEffect(() => {
    if (currentExp?.id) {
      fetchPredictions(currentExp.id);
    } else {
      setPredictions([]);
    }
  }, [currentExp?.id]);

  const handleBenchmarkChange = (name: 'FEVER' | 'HaluEval' | 'TruthfulQA') => {
    setBenchmarkName(name);
    if (name === 'HaluEval') {
      setEvalSource('context');
      setActiveManagerTab('halueval');
    } else if (name === 'FEVER') {
      setEvalSource('fever');
      setActiveManagerTab('fever');
    } else {
      setEvalSource('documents');
    }
  };

  const handlePrepareFEVER = async () => {
    setIsPreparing(true);
    setError(null);
    setActionSuccess(null);
    try {
      const res = await api.prepareFEVER({
        split: feverSplit,
        limit: sampleLimit,
        seed: 42
      });
      setActionSuccess(`FEVER ${feverSplit} sample prepared successfully (${res.summary?.sample_size} records)!`);
      await fetchFEVERStatus();
    } catch (err: any) {
      setError(err.message || "Failed to prepare FEVER dataset");
    } finally {
      setIsPreparing(false);
    }
  };

  const handleIndexFEVER = async () => {
    setIsIndexing(true);
    setError(null);
    setActionSuccess(null);
    try {
      const res = await api.indexFEVER({
        split: feverSplit,
        limit: sampleLimit,
        max_articles: 100,
        rebuild: true
      });
      setActionSuccess(`FEVER Knowledge Base indexed! Vectors: ${res.summary?.total_vectors_indexed}`);
      await fetchFEVERStatus();
    } catch (err: any) {
      setError(err.message || "Failed to build FEVER FAISS index");
    } finally {
      setIsIndexing(false);
    }
  };

  const handleClearIndex = async () => {
    if (!window.confirm("Are you sure you want to clear the FEVER knowledge base index?")) return;
    try {
      await api.clearFEVERIndex();
      setActionSuccess("FEVER FAISS index cleared.");
      await fetchFEVERStatus();
    } catch (err: any) {
      setError(err.message || "Failed to clear index");
    }
  };

  const handleRunEvaluation = async () => {
    setIsRunning(true);
    setError(null);
    setActionSuccess(null);
    try {
      const exp = await api.runEvaluation({
        benchmark_name: benchmarkName,
        task: haluTask,
        sample_size: sampleSize,
        seed: seed,
        sampling_strategy: haluStrategy,
        evidence_source: evalSource,
        split: feverSplit,
        top_k: topK
      });
      setCurrentExp(exp);
      onRefresh();
      setActionSuccess(`Completed ${benchmarkName} evaluation (${exp.total_samples} samples) with ${(exp.accuracy * 100).toFixed(1)}% accuracy!`);
    } catch (err: any) {
      setError(err.message || 'Evaluation experiment failed');
    } finally {
      setIsRunning(false);
    }
  };

  const handleRunComparison = async () => {
    setIsComparing(true);
    setError(null);
    setActionSuccess(null);
    try {
      const res = await api.compareModels({
        benchmark_name: compareBenchmark,
        task: compareTask,
        sample_size: compareSampleSize,
        seed: seed,
        llm_model: compareLlmModel
      });
      setComparisonResult(res);
      setActionSuccess(`Multi-model evaluation complete (${res.total_samples} samples). Agreement rate: ${(res.agreement_rate * 100).toFixed(1)}%`);
    } catch (err: any) {
      setError(err.message || 'Multi-model comparison failed');
    } finally {
      setIsComparing(false);
    }
  };

  const exportExperimentJSON = () => {
    if (!currentExp) return;
    const exportData = {
      ...currentExp,
      predictions: predictions.length > 0 ? predictions : (currentExp.metrics?.predictions || [])
    };
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `truthguard_benchmark_${currentExp.benchmark_name.toLowerCase()}_${currentExp.id.slice(0, 8)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Filter predictions
  const filteredPredictions = predictions.filter(p => {
    if (predictionFilter === 'errors') return !p.is_correct;
    if (predictionFilter === 'hallucinated') return p.predicted_label === 'hallucinated' || p.predicted_label === 'Contradicted';
    if (predictionFilter === 'faithful') return p.predicted_label === 'faithful' || p.predicted_label === 'Supported';
    return true;
  });

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 sm:p-7 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-2xl">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-xs font-medium mb-2">
            <Sparkles className="w-3 h-3 text-violet-400" />
            <span>Academic Benchmarking</span>
          </div>
          <h2 className="text-xl font-bold text-[#F4F4FA] flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-violet-400" />
            Empirical NLP Evaluation Lab
          </h2>
          <p className="text-xs text-[#94A3B8] mt-1 max-w-xl">
            Evaluate verification accuracy, precision, recall, macro-F1, latency, and sample predictions against real HaluEval and FEVER benchmarks without hardcoded or simulated metrics.
          </p>
        </div>

        {currentExp && (
          <button
            onClick={exportExperimentJSON}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#080910] hover:bg-[#1a1d2d] text-slate-200 border border-white/[0.08] text-xs font-semibold transition-all cursor-pointer"
          >
            <Download className="w-4 h-4 text-violet-400" />
            Export Benchmark Run (JSON)
          </button>
        )}
      </div>

      {/* Dataset & Knowledge Base Manager with Tab Switcher */}
      <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.06] pb-3">
          <div className="flex items-center gap-3">
            <h3 className="text-sm font-semibold text-[#F4F4FA] uppercase tracking-wider flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-violet-400" />
              Dataset Repositories & Knowledge Bases
            </h3>
          </div>
          
          <div className="flex items-center gap-2">
            <div className="flex bg-[#080910] p-1 rounded-xl border border-white/[0.06]">
              <button
                onClick={() => setActiveManagerTab('halueval')}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                  activeManagerTab === 'halueval'
                    ? 'bg-violet-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                HaluEval Benchmark (34.5k)
              </button>
              <button
                onClick={() => setActiveManagerTab('fever')}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                  activeManagerTab === 'fever'
                    ? 'bg-violet-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                FEVER Knowledge Base
              </button>
            </div>

            <button
              onClick={() => { fetchFEVERStatus(); fetchHaluEvalStatus(); }}
              className="text-xs text-[#94A3B8] hover:text-white flex items-center gap-1 transition-colors cursor-pointer ml-1"
              title="Refresh dataset status"
            >
              <RotateCw className={`w-3.5 h-3.5 ${isLoadingHaluStatus ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* HaluEval Tab View */}
        {activeManagerTab === 'halueval' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-slate-200">Local Dataset Directory:</span>
                <code className="text-violet-300 bg-[#080910] px-2 py-0.5 rounded border border-white/[0.06] font-mono text-[11px]">
                  HaluEval-main/data/
                </code>
              </div>
              <div className="flex items-center gap-2">
                <span className={`inline-block w-2 h-2 rounded-full ${haluStatus?.is_available ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
                <span className="font-mono text-emerald-400 font-semibold">
                  {haluStatus?.total_records?.toLocaleString() || '34,507'} Total Benchmark Samples
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              {/* QA Task Card */}
              <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06] space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 font-semibold uppercase text-[11px]">QA Task</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                    Available
                  </span>
                </div>
                <div className="text-lg font-bold text-[#F4F4FA]">
                  {haluStatus?.tasks?.qa?.total_records?.toLocaleString() || '10,000'} <span className="text-xs font-normal text-slate-400">records</span>
                </div>
                <div className="text-[11px] text-slate-400">
                  HotpotQA / CoQA multi-hop knowledge with right & hallucinated answers.
                </div>
                <div className="text-[10px] text-violet-300 font-mono pt-1">
                  qa_data.json ({haluStatus?.tasks?.qa?.size_mb || 37.1} MB)
                </div>
              </div>

              {/* Dialogue Task Card */}
              <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06] space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 font-semibold uppercase text-[11px]">Dialogue Task</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                    Available
                  </span>
                </div>
                <div className="text-lg font-bold text-[#F4F4FA]">
                  {haluStatus?.tasks?.dialogue?.total_records?.toLocaleString() || '10,000'} <span className="text-xs font-normal text-slate-400">records</span>
                </div>
                <div className="text-[11px] text-slate-400">
                  Topical-Chat conversation history with topical grounding context.
                </div>
                <div className="text-[10px] text-violet-300 font-mono pt-1">
                  dialogue_data.json ({haluStatus?.tasks?.dialogue?.size_mb || 13.9} MB)
                </div>
              </div>

              {/* Summarization Task Card */}
              <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06] space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 font-semibold uppercase text-[11px]">Summarization</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                    Available
                  </span>
                </div>
                <div className="text-lg font-bold text-[#F4F4FA]">
                  {haluStatus?.tasks?.summarization?.total_records?.toLocaleString() || '10,000'} <span className="text-xs font-normal text-slate-400">records</span>
                </div>
                <div className="text-[11px] text-slate-400">
                  CNN/DailyMail source news articles with faithful & hallucinated summaries.
                </div>
                <div className="text-[10px] text-violet-300 font-mono pt-1">
                  summarization_data.json ({haluStatus?.tasks?.summarization?.size_mb || 18.9} MB)
                </div>
              </div>

              {/* General Task Card */}
              <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06] space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 font-semibold uppercase text-[11px]">General Task</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                    Available
                  </span>
                </div>
                <div className="text-lg font-bold text-[#F4F4FA]">
                  {haluStatus?.tasks?.general?.total_records?.toLocaleString() || '4,507'} <span className="text-xs font-normal text-slate-400">records</span>
                </div>
                <div className="text-[11px] text-slate-400">
                  ChatGPT user queries and responses (815 hallucinated, 3,692 faithful).
                </div>
                <div className="text-[10px] text-violet-300 font-mono pt-1">
                  general_data.json ({haluStatus?.tasks?.general?.size_mb || 5.8} MB)
                </div>
              </div>
            </div>
          </div>
        )}

        {/* FEVER Tab View */}
        {activeManagerTab === 'fever' && feverStatus && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06]">
                <span className="text-slate-400 block mb-1">Download Status</span>
                <span className={`font-semibold ${feverStatus.is_downloaded ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {feverStatus.is_downloaded ? '✓ Cached Locally' : '○ Not Downloaded'}
                </span>
                <span className="text-[10px] text-slate-500 block mt-0.5">
                  Splits: {feverStatus.splits_available.join(', ') || 'None'}
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06]">
                <span className="text-slate-400 block mb-1">Prepared Verification Set</span>
                <span className="text-[#F4F4FA] font-bold text-sm">
                  {feverStatus.prepared_samples_count.toLocaleString()} samples
                </span>
                <div className="flex items-center gap-1.5 mt-1 text-[10px]">
                  {Object.entries(feverStatus.class_distribution).map(([k, v]) => (
                    <span key={k} className="px-1.5 py-0.5 rounded bg-[#11131D] text-slate-300 font-mono border border-white/[0.06]">
                      {k[0]}:{v}
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06]">
                <span className="text-slate-400 block mb-1">Evidence Corpus (Wikipedia)</span>
                <span className="text-[#F4F4FA] font-bold text-sm">
                  {feverStatus.evidence_cache_count} articles cached
                </span>
                <span className="text-[10px] text-slate-500 block mt-0.5">
                  Model: MiniLM-L6-v2
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06]">
                <span className="text-slate-400 block mb-1">FAISS Index Status</span>
                <span className={`font-semibold ${feverStatus.fever_index_exists ? 'text-violet-300' : 'text-slate-400'}`}>
                  {feverStatus.fever_index_vectors.toLocaleString()} vectors
                </span>
                <span className="text-[10px] text-slate-500 block mt-0.5 truncate">
                  {feverStatus.last_indexed_at ? `Updated ${feverStatus.last_indexed_at.slice(0, 10)}` : 'Index not built'}
                </span>
              </div>
            </div>

            {/* FEVER Actions Bar */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <select
                value={feverSplit}
                onChange={(e) => setFeverSplit(e.target.value as any)}
                className="px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-xs text-slate-200 focus:outline-none cursor-pointer"
              >
                <option value="paper_dev">Split: paper_dev (Official Dev Set)</option>
                <option value="train">Split: train (Training Corpus)</option>
              </select>

              <button
                onClick={handlePrepareFEVER}
                disabled={isPreparing || isIndexing || isRunning}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#080910] hover:bg-white/[0.06] disabled:opacity-50 text-slate-200 text-xs font-semibold border border-white/[0.08] transition-all cursor-pointer"
              >
                {isPreparing ? <RotateCw className="w-3.5 h-3.5 animate-spin" /> : <BookOpen className="w-3.5 h-3.5 text-violet-400" />}
                <span>{isPreparing ? 'Preparing Sample...' : 'Prepare Dataset Sample (1,000)'}</span>
              </button>

              <button
                onClick={handleIndexFEVER}
                disabled={isPreparing || isIndexing || isRunning}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#080910] hover:bg-white/[0.06] disabled:opacity-50 text-slate-200 text-xs font-semibold border border-white/[0.08] transition-all cursor-pointer"
              >
                {isIndexing ? <RotateCw className="w-3.5 h-3.5 animate-spin" /> : <Database className="w-3.5 h-3.5 text-blue-400" />}
                <span>{isIndexing ? 'Indexing Evidence Corpus...' : 'Build FAISS Evidence Index'}</span>
              </button>

              {feverStatus?.fever_index_exists && (
                <button
                  onClick={handleClearIndex}
                  disabled={isPreparing || isIndexing || isRunning}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-rose-950/20 hover:bg-rose-950/40 text-rose-300 text-xs font-semibold border border-rose-500/20 transition-all cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Clear Index</span>
                </button>
              )}
            </div>
          </div>
        )}

        {actionSuccess && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 text-xs">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{actionSuccess}</span>
          </div>
        )}
      </div>

      {/* Benchmark Experiment Configuration */}
      <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl space-y-5">
        <h3 className="text-sm font-semibold text-[#F4F4FA] uppercase tracking-wider flex items-center gap-2">
          <Database className="w-4 h-4 text-violet-400" />
          Benchmark Selection & Empirical Evaluation
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Benchmark card selector */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-400 block">Dataset Benchmark</label>
            <select
              value={benchmarkName}
              onChange={(e) => handleBenchmarkChange(e.target.value as any)}
              className="w-full px-3 py-2.5 rounded-xl bg-[#080910] border border-white/[0.07] text-sm text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="HaluEval">HaluEval (Hallucination Detection)</option>
              <option value="FEVER">FEVER (Fact Extraction & Verification)</option>
              <option value="TruthfulQA">TruthfulQA (Factual Misconceptions)</option>
            </select>
          </div>

          {/* Task selector if HaluEval */}
          {benchmarkName === 'HaluEval' ? (
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-400 block">HaluEval Task</label>
              <select
                value={haluTask}
                onChange={(e) => setHaluTask(e.target.value as any)}
                className="w-full px-3 py-2.5 rounded-xl bg-[#080910] border border-white/[0.07] text-sm text-slate-200 focus:outline-none cursor-pointer"
              >
                <option value="qa">QA Task (HotpotQA / CoQA)</option>
                <option value="dialogue">Dialogue Task (Topical-Chat)</option>
                <option value="summarization">Summarization Task (CNN/DM)</option>
                <option value="general">General Task (ChatGPT Queries)</option>
              </select>
            </div>
          ) : (
            /* Evidence source selector for FEVER / others */
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-400 block">
                Evidence Retrieval Source
              </label>
              <select
                value={evalSource}
                onChange={(e) => setEvalSource(e.target.value as any)}
                disabled={benchmarkName !== 'FEVER'}
                className="w-full px-3 py-2.5 rounded-xl bg-[#080910] border border-white/[0.07] text-sm text-slate-200 focus:outline-none disabled:opacity-50 cursor-pointer"
              >
                <option value="fever">FEVER Knowledge Base (Wikipedia)</option>
                <option value="documents">TruthGuard Baseline (Documents)</option>
              </select>
            </div>
          )}

          {/* Sample size */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-slate-400">Sample Size</label>
              <span className="text-xs font-mono text-violet-400 font-semibold">{sampleSize}</span>
            </div>
            <input
              type="range"
              min={5}
              max={50}
              value={sampleSize}
              onChange={(e) => setSampleSize(Number(e.target.value))}
              className="w-full accent-violet-500 h-2 bg-[#080910] rounded-lg cursor-pointer mt-3"
            />
          </div>

          {/* Top-K retrieval */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-slate-400">Retrieval Top-K</label>
              <span className="text-xs font-mono text-violet-400 font-semibold">{topK}</span>
            </div>
            <input
              type="range"
              min={1}
              max={5}
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="w-full accent-violet-500 h-2 bg-[#080910] rounded-lg cursor-pointer mt-3"
            />
          </div>
        </div>

        {/* Extended Settings Row for HaluEval */}
        {benchmarkName === 'HaluEval' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1 border-t border-white/[0.04]">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-400">Sampling Strategy</label>
              <select
                value={haluStrategy}
                onChange={(e) => setHaluStrategy(e.target.value as any)}
                className="w-full px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-xs text-slate-200 focus:outline-none cursor-pointer"
              >
                <option value="balanced_sampled">Balanced Sample (Coin-flip per record)</option>
                <option value="balanced_paired">Balanced Paired (Right + Hallucinated)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-400">Random Seed (Reproducibility)</label>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(Number(e.target.value) || 42)}
                className="w-full px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-xs font-mono text-slate-200 focus:outline-none"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-400">Evidence Source</label>
              <select
                value={evalSource}
                onChange={(e) => setEvalSource(e.target.value as any)}
                className="w-full px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-xs text-slate-200 focus:outline-none cursor-pointer"
              >
                <option value="context">Knowledge Context (Provided in Dataset)</option>
                <option value="documents">TruthGuard Indexed Documents</option>
              </select>
            </div>
          </div>
        )}

        {/* Benchmark Description Note */}
        <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06] text-xs text-[#94A3B8] flex items-start gap-2">
          <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
          <div>
            {benchmarkName === 'HaluEval' && (
              <p>
                <strong className="text-slate-200">HaluEval Benchmark (Authentic Real Inference):</strong> Evaluates model ability to discriminate between faithful responses and hallucinated answers generated by LLMs across QA, Dialogue, Summarization, and General tasks. No fake or hardcoded scores.
              </p>
            )}
            {benchmarkName === 'FEVER' && (
              <p>
                <strong className="text-slate-200">FEVER Benchmark (Zero Data Leakage):</strong> Evaluates claim-level verification using semantic retrieval from the FEVER Knowledge Base and DeBERTa NLI cross-encoder. Gold labels are strictly withheld.
              </p>
            )}
            {benchmarkName === 'TruthfulQA' && (
              <p>
                <strong className="text-slate-200">TruthfulQA:</strong> Tests model resistance to common human misconceptions and fabricated answers across health, science, and history.
              </p>
            )}
          </div>
        </div>

        {error && (
          <div className="text-xs text-rose-300 bg-rose-950/30 border border-rose-500/30 p-3 rounded-xl flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex items-center justify-between pt-2">
          <span className="text-xs text-slate-500">
            Computes authentic scikit-learn metrics on real model inference pairs.
          </span>
          <button
            onClick={handleRunEvaluation}
            disabled={isRunning || isPreparing || isIndexing}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-800 text-white font-medium text-sm transition-all shadow-[0_0_16px_rgba(139,92,246,0.3)] cursor-pointer"
          >
            {isRunning ? (
              <>
                <RotateCw className="w-4 h-4 animate-spin text-white" />
                <span>Evaluating Benchmark Samples...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Run {benchmarkName} Evaluation</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Multi-Model Comparison & Disagreement Analysis Section */}
      <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.06] pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-violet-600/10 border border-violet-500/20 text-violet-400">
              <GitCompare className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#F4F4FA] flex items-center gap-2">
                Multi-Model Verification & Disagreement Lab
              </h3>
              <p className="text-xs text-[#94A3B8]">
                Compare DeBERTa-v3 Cross-Encoder vs Local LLM (Qwen3:8b) vs Hybrid Consensus Ensemble on authentic instances.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#080910] text-violet-300 border border-white/[0.06]">
              Real NLI + Ollama LLM
            </span>
          </div>
        </div>

        {/* Controls row */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
          <div className="space-y-1.5">
            <label className="text-slate-400 font-medium">Benchmark Dataset</label>
            <select
              value={compareBenchmark}
              onChange={(e) => setCompareBenchmark(e.target.value as any)}
              className="w-full px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-slate-200 focus:outline-none"
            >
              <option value="HaluEval">HaluEval Benchmark</option>
              <option value="FEVER">FEVER Benchmark</option>
            </select>
          </div>

          {compareBenchmark === 'HaluEval' ? (
            <div className="space-y-1.5">
              <label className="text-slate-400 font-medium">Benchmark Task</label>
              <select
                value={compareTask}
                onChange={(e) => setCompareTask(e.target.value as any)}
                className="w-full px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-slate-200 focus:outline-none"
              >
                <option value="qa">QA Task</option>
                <option value="dialogue">Dialogue Task</option>
                <option value="summarization">Summarization Task</option>
                <option value="general">General Task</option>
              </select>
            </div>
          ) : (
            <div className="space-y-1.5">
              <label className="text-slate-400 font-medium">Split</label>
              <div className="px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-slate-400">
                paper_dev (Wikipedia)
              </div>
            </div>
          )}

          <div className="space-y-1.5">
            <div className="flex justify-between">
              <label className="text-slate-400 font-medium">Sample Size</label>
              <span className="font-mono text-violet-400">{compareSampleSize}</span>
            </div>
            <input
              type="range"
              min={5}
              max={25}
              value={compareSampleSize}
              onChange={(e) => setCompareSampleSize(Number(e.target.value))}
              className="w-full accent-violet-500 h-2 bg-[#080910] rounded-lg cursor-pointer mt-2"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-slate-400 font-medium">Local LLM</label>
            <select
              value={compareLlmModel}
              onChange={(e) => setCompareLlmModel(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-slate-200 focus:outline-none"
            >
              <option value="qwen3:8b">qwen3:8b (Ollama Local)</option>
              <option value="llama3.1:8b">llama3.1:8b</option>
              <option value="mistral:7b">mistral:7b</option>
            </select>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex items-center justify-between pt-1">
          <span className="text-[11px] text-slate-500">
            Executes DeBERTa and Local LLM independently and runs a consensus voting arbitration.
          </span>
          <button
            onClick={handleRunComparison}
            disabled={isComparing || isRunning}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:bg-slate-800 text-white font-medium text-xs transition-colors shadow-sm cursor-pointer"
          >
            {isComparing ? (
              <>
                <RotateCw className="w-3.5 h-3.5 animate-spin" />
                <span>Running Comparative Inference...</span>
              </>
            ) : (
              <>
                <GitCompare className="w-3.5 h-3.5" />
                <span>Compare DeBERTa vs Qwen3 vs Ensemble</span>
              </>
            )}
          </button>
        </div>

        {/* Comparison Results Card */}
        {comparisonResult && (
          <div className="mt-4 pt-4 border-t border-white/[0.06] space-y-4">
            {/* Agreement & Disagreement Metric Badges */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3 rounded-xl bg-[#080910] border border-white/[0.06] text-center">
                <span className="text-[11px] text-slate-400 block uppercase font-medium">Evaluated Samples</span>
                <span className="text-xl font-bold text-[#F4F4FA] font-mono mt-0.5">
                  {comparisonResult.total_samples}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-[#080910] border border-emerald-500/20 text-center">
                <span className="text-[11px] text-emerald-400 block uppercase font-medium">Inter-Model Agreement</span>
                <span className="text-xl font-bold text-emerald-400 font-mono mt-0.5">
                  {(comparisonResult.agreement_rate * 100).toFixed(1)}%
                </span>
              </div>
              <div className="p-3 rounded-xl bg-[#080910] border border-violet-500/20 text-center">
                <span className="text-[11px] text-violet-300 block uppercase font-medium">Disagreements Identified</span>
                <span className="text-xl font-bold text-violet-300 font-mono mt-0.5">
                  {comparisonResult.disagreements_count}
                </span>
              </div>
            </div>

            {/* Side-by-Side Model Scorecards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {comparisonResult.models.map((m, idx) => (
                <div 
                  key={idx}
                  className={`p-4 rounded-xl border space-y-3 ${
                    m.model_type === 'ensemble'
                      ? 'bg-violet-950/20 border-violet-500/30 shadow-lg'
                      : 'bg-[#080910] border-white/[0.06]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                        {m.model_type}
                      </span>
                      <h4 className="text-xs font-bold text-[#F4F4FA] truncate mt-0.5">
                        {m.model_name}
                      </h4>
                    </div>
                    {m.model_type === 'ensemble' && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-violet-600/30 text-violet-300 border border-violet-500/40">
                        Consensus
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2 rounded-lg bg-[#11131D] border border-white/[0.04]">
                      <span className="text-[10px] text-slate-400 block">Accuracy</span>
                      <span className="font-bold text-emerald-400 font-mono text-sm">
                        {(m.accuracy * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="p-2 rounded-lg bg-[#11131D] border border-white/[0.04]">
                      <span className="text-[10px] text-slate-400 block">Macro F1</span>
                      <span className="font-bold text-violet-300 font-mono text-sm">
                        {(m.f1_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="p-2 rounded-lg bg-[#11131D] border border-white/[0.04]">
                      <span className="text-[10px] text-slate-400 block">Precision</span>
                      <span className="font-mono text-slate-200">
                        {(m.precision * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="p-2 rounded-lg bg-[#11131D] border border-white/[0.04]">
                      <span className="text-[10px] text-slate-400 block">Avg Latency</span>
                      <span className="font-mono text-slate-400">
                        {m.avg_latency_ms.toFixed(0)} ms
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Disagreement Inspector */}
            {comparisonResult.disagreements.length > 0 ? (
              <div className="p-4 rounded-xl bg-[#080910] border border-white/[0.06] space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                    <Split className="w-3.5 h-3.5 text-violet-400" />
                    Model Disagreement Analysis ({comparisonResult.disagreements.length} instances)
                  </h4>
                  <span className="text-[11px] text-slate-500">
                    Cases where DeBERTa NLI and Local LLM reached conflicting verdicts
                  </span>
                </div>

                <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                  {comparisonResult.disagreements.map((dis, dIdx) => {
                    const isExpanded = expandedDisagreementId === dis.id;
                    return (
                      <div
                        key={dis.id || dIdx}
                        className="p-3 rounded-lg bg-[#11131D] border border-white/[0.04] space-y-2 text-xs"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <p className="text-slate-200 font-medium line-clamp-2">
                            "{dis.prompt_or_claim}"
                          </p>
                          <button
                            onClick={() => setExpandedDisagreementId(isExpanded ? null : dis.id)}
                            className="p-1 rounded bg-[#080910] text-slate-400 hover:text-white shrink-0"
                          >
                            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                          </button>
                        </div>

                        <div className="flex flex-wrap items-center gap-2 text-[10px]">
                          <span className="text-slate-500">Ground Truth:</span>
                          <span className="px-1.5 py-0.5 rounded font-mono font-semibold bg-slate-800 text-slate-200">
                            {dis.ground_truth}
                          </span>

                          <span className="text-slate-500 ml-1">DeBERTa:</span>
                          <span className={`px-1.5 py-0.5 rounded font-mono font-semibold ${
                            dis.nli_verdict === dis.ground_truth
                              ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-500/30'
                              : 'bg-rose-950/60 text-rose-300 border border-rose-500/30'
                          }`}>
                            {dis.nli_verdict}
                          </span>

                          <span className="text-slate-500 ml-1">Qwen3:</span>
                          <span className={`px-1.5 py-0.5 rounded font-mono font-semibold ${
                            dis.llm_verdict === dis.ground_truth
                              ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-500/30'
                              : 'bg-rose-950/60 text-rose-300 border border-rose-500/30'
                          }`}>
                            {dis.llm_verdict}
                          </span>

                          <span className="text-slate-500 ml-1">Consensus:</span>
                          <span className="px-1.5 py-0.5 rounded font-mono font-semibold bg-violet-950/60 text-violet-300 border border-violet-500/30">
                            {dis.ensemble_verdict}
                          </span>
                        </div>

                        {isExpanded && dis.explanation && (
                          <div className="p-2 rounded bg-[#080910] text-[11px] text-slate-400 border border-white/[0.03]">
                            <strong className="text-slate-300 block mb-0.5">Disagreement Rationale:</strong>
                            {dis.explanation}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Full Consensus: DeBERTa and Local LLM predictions were in 100% agreement across all evaluated samples.</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Active Experiment Results */}
      {currentExp && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.06] pb-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-violet-300">
                  {currentExp.benchmark_name} Benchmark Results
                </span>
                <h3 className="text-lg font-bold text-[#F4F4FA] mt-0.5">{currentExp.name}</h3>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="px-2.5 py-1 rounded-full bg-[#080910] text-slate-300 font-mono border border-white/[0.06]">
                  {currentExp.total_samples} samples
                </span>
                <span className="px-2.5 py-1 rounded-full bg-[#080910] text-slate-300 font-mono border border-white/[0.06]">
                  {currentExp.latency_per_sample_ms.toFixed(1)} ms/sample
                </span>
              </div>
            </div>

            {/* Performance Metrics Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div className="p-4 rounded-xl bg-[#080910] border border-white/[0.06] text-center">
                <span className="text-xs text-slate-400 uppercase font-semibold">Accuracy</span>
                <div className="text-2xl font-bold text-emerald-400 mt-1">
                  {(currentExp.accuracy * 100).toFixed(1)}%
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[#080910] border border-white/[0.06] text-center">
                <span className="text-xs text-slate-400 uppercase font-semibold">Precision</span>
                <div className="text-2xl font-bold text-blue-400 mt-1">
                  {(currentExp.precision * 100).toFixed(1)}%
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[#080910] border border-white/[0.06] text-center">
                <span className="text-xs text-slate-400 uppercase font-semibold">Recall</span>
                <div className="text-2xl font-bold text-violet-300 mt-1">
                  {(currentExp.recall * 100).toFixed(1)}%
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[#080910] border border-white/[0.06] text-center">
                <span className="text-xs text-slate-400 uppercase font-semibold">Macro F1</span>
                <div className="text-2xl font-bold text-purple-400 mt-1">
                  {(currentExp.f1_score * 100).toFixed(1)}%
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[#080910] border border-white/[0.06] text-center">
                <span className="text-xs text-slate-400 uppercase font-semibold">
                  {currentExp.benchmark_name === 'HaluEval' ? 'Coverage' : 'Recall@K'}
                </span>
                <div className="text-2xl font-bold text-amber-400 mt-1">
                  {(currentExp.retrieval_recall_at_k * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Confusion Matrix Display */}
            {currentExp.confusion_matrix && Object.keys(currentExp.confusion_matrix).length > 0 && (
              <div className="pt-4 border-t border-white/[0.06] space-y-3">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Empirical Confusion Matrix (Rows: Ground Truth, Columns: Model Prediction)
                </h4>
                
                <div className="overflow-x-auto">
                  <table className="w-full text-center text-xs border border-white/[0.08] rounded-xl overflow-hidden">
                    <thead className="bg-[#080910] text-slate-400 font-semibold">
                      <tr>
                        <th className="p-2.5 text-left border-r border-white/[0.08]">Actual \ Predicted</th>
                        {Object.keys(currentExp.confusion_matrix).map(col => (
                          <th key={col} className="p-2.5 border-r border-white/[0.08] last:border-r-0">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/[0.06]">
                      {Object.entries(currentExp.confusion_matrix).map(([rowLabel, cols]) => (
                        <tr key={rowLabel} className="hover:bg-white/[0.02]">
                          <td className="p-2.5 font-semibold text-slate-300 text-left bg-[#080910] border-r border-white/[0.08]">
                            {rowLabel}
                          </td>
                          {Object.entries(cols).map(([colLabel, count]) => {
                            const isDiagonal = rowLabel === colLabel;
                            return (
                              <td
                                key={colLabel}
                                className={`p-2.5 font-mono text-sm border-r border-white/[0.08] last:border-r-0 ${
                                  isDiagonal && count > 0 ? 'bg-violet-950/40 text-violet-300 font-bold' : 'text-slate-400'
                                }`}
                              >
                                {count}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* Sample-by-Sample Prediction Audit & Explainability */}
          {predictions.length > 0 && (
            <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.06] pb-3">
                <div>
                  <h4 className="text-sm font-semibold text-[#F4F4FA] flex items-center gap-2">
                    <FileText className="w-4 h-4 text-violet-400" />
                    Authentic Sample-by-Sample Prediction Audit ({predictions.length} Examples)
                  </h4>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Individual evaluated benchmark instances with ground truth, cross-encoder scores, and context grounding.
                  </p>
                </div>

                {/* Filter buttons */}
                <div className="flex items-center gap-1.5 bg-[#080910] p-1 rounded-xl border border-white/[0.06] text-xs">
                  <button
                    onClick={() => setPredictionFilter('all')}
                    className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                      predictionFilter === 'all' ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    All ({predictions.length})
                  </button>
                  <button
                    onClick={() => setPredictionFilter('errors')}
                    className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                      predictionFilter === 'errors' ? 'bg-rose-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Errors ({predictions.filter(p => !p.is_correct).length})
                  </button>
                  <button
                    onClick={() => setPredictionFilter('hallucinated')}
                    className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                      predictionFilter === 'hallucinated' ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Hallucinated ({predictions.filter(p => p.predicted_label === 'hallucinated' || p.predicted_label === 'Contradicted').length})
                  </button>
                  <button
                    onClick={() => setPredictionFilter('faithful')}
                    className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                      predictionFilter === 'faithful' ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Faithful ({predictions.filter(p => p.predicted_label === 'faithful' || p.predicted_label === 'Supported').length})
                  </button>
                </div>
              </div>

              {/* Prediction Cards */}
              <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
                {filteredPredictions.map((pred, idx) => {
                  const isExpanded = expandedPredId === pred.id;
                  const isHallucinated = pred.predicted_label === 'hallucinated' || pred.predicted_label === 'Contradicted';
                  return (
                    <div
                      key={pred.id || idx}
                      className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06] hover:border-white/[0.12] transition-colors"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3 min-w-0">
                          <span className="text-xs font-mono text-slate-500 mt-0.5 shrink-0">
                            #{idx + 1}
                          </span>
                          <div className="min-w-0">
                            <p className="text-xs font-medium text-slate-200 line-clamp-2">
                              {pred.claim_or_question}
                            </p>
                            <div className="flex flex-wrap items-center gap-2 mt-2">
                              <span className="text-[10px] text-slate-400">Ground Truth:</span>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                                pred.ground_truth === 'faithful' || pred.ground_truth === 'Supported'
                                  ? 'bg-emerald-950/40 text-emerald-300 border border-emerald-500/20'
                                  : 'bg-rose-950/40 text-rose-300 border border-rose-500/20'
                              }`}>
                                {pred.ground_truth}
                              </span>

                              <span className="text-[10px] text-slate-400 ml-1">Model Verdict:</span>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                                !isHallucinated
                                  ? 'bg-emerald-950/40 text-emerald-300 border border-emerald-500/20'
                                  : 'bg-rose-950/40 text-rose-300 border border-rose-500/20'
                              }`}>
                                {pred.predicted_label}
                              </span>

                              <span className="text-[10px] text-slate-400 ml-1">Hallucination:</span>
                              <span className="font-mono text-[10px] text-violet-300 font-semibold">
                                {(pred.hallucination_score * 100).toFixed(1)}%
                              </span>

                              {pred.latency_ms && (
                                <span className="text-[10px] text-slate-500 font-mono">
                                  {pred.latency_ms.toFixed(0)} ms
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          {pred.is_correct ? (
                            <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-400 bg-emerald-950/20 px-2 py-1 rounded-lg border border-emerald-500/20">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>Correct</span>
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-[11px] font-semibold text-rose-400 bg-rose-950/20 px-2 py-1 rounded-lg border border-rose-500/20">
                              <XCircle className="w-3.5 h-3.5" />
                              <span>Error</span>
                            </span>
                          )}

                          <button
                            onClick={() => setExpandedPredId(isExpanded ? null : pred.id)}
                            className="p-1.5 rounded-lg bg-[#11131D] hover:bg-white/[0.06] text-slate-400 hover:text-white transition-colors cursor-pointer"
                            title="Toggle Evidence Details"
                          >
                            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>

                      {/* Expandable Evidence Snippet */}
                      {isExpanded && (
                        <div className="mt-3 pt-3 border-t border-white/[0.06] space-y-2 text-xs">
                          {pred.evidence_text && (
                            <div>
                              <span className="text-slate-400 font-semibold uppercase text-[10px] block mb-1">
                                Reference Context / Evidence Passage
                              </span>
                              <div className="p-2.5 rounded-lg bg-[#11131D] text-slate-300 font-mono text-[11px] leading-relaxed max-h-40 overflow-y-auto border border-white/[0.04]">
                                {pred.evidence_text}
                              </div>
                            </div>
                          )}

                          {pred.explanation && (
                            <div>
                              <span className="text-slate-400 font-semibold uppercase text-[10px] block mb-1">
                                Inference Explanation
                              </span>
                              <p className="text-slate-300 text-xs italic">
                                {pred.explanation}
                              </p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Previous Experiments History Table */}
      {experiments.length > 0 && (
        <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl space-y-4">
          <h3 className="text-base font-semibold text-[#F4F4FA]">
            Experiment Comparison Log ({experiments.length})
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-[#080910] text-slate-400 border-b border-white/[0.06]">
                <tr>
                  <th className="py-3 px-4">Benchmark</th>
                  <th className="py-3 px-4">Samples</th>
                  <th className="py-3 px-4">Accuracy</th>
                  <th className="py-3 px-4">Precision</th>
                  <th className="py-3 px-4">Recall</th>
                  <th className="py-3 px-4">Macro F1</th>
                  <th className="py-3 px-4">Coverage</th>
                  <th className="py-3 px-4 text-right">View</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.05]">
                {experiments.map((exp) => (
                  <tr key={exp.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-[#F4F4FA]">
                      {exp.benchmark_name}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono">{exp.total_samples}</td>
                    <td className="py-3.5 px-4 text-xs font-bold text-emerald-400">
                      {(exp.accuracy * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono">{(exp.precision * 100).toFixed(1)}%</td>
                    <td className="py-3.5 px-4 text-xs font-mono">{(exp.recall * 100).toFixed(1)}%</td>
                    <td className="py-3.5 px-4 text-xs font-bold text-violet-300">
                      {(exp.f1_score * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono text-amber-400">
                      {(exp.retrieval_recall_at_k * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setCurrentExp(exp)}
                        className="px-2.5 py-1 rounded-lg bg-[#080910] hover:bg-violet-600/20 text-xs font-medium text-slate-200 border border-white/[0.08] hover:border-violet-500/40 transition-colors cursor-pointer"
                      >
                        Select
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
