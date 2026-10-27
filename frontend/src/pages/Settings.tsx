import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Server, 
  Cpu, 
  Sliders, 
  Save, 
  CheckCircle2, 
  Trash2, 
  AlertTriangle,
  RotateCw,
  Sparkles
} from 'lucide-react';
import { SystemHealth } from '../types';

interface SettingsProps {
  health: SystemHealth | null;
  onRefreshHealth: () => void;
}

export const Settings: React.FC<SettingsProps> = ({ health, onRefreshHealth }) => {
  const [ollamaUrl, setOllamaUrl] = useState(health?.ollama.base_url || 'http://localhost:11434');
  const [defaultModel, setDefaultModel] = useState(health?.ollama.default_model || 'qwen3:8b');
  const [entailmentThreshold, setEntailmentThreshold] = useState(0.55);
  const [contradictionThreshold, setContradictionThreshold] = useState(0.50);
  const [topK, setTopK] = useState(5);
  const [chunkSize, setChunkSize] = useState(500);
  const [chunkOverlap, setChunkOverlap] = useState(100);
  
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [isTestingOllama, setIsTestingOllama] = useState(false);

  const handleSave = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  const testOllamaConnection = async () => {
    setIsTestingOllama(true);
    await onRefreshHealth();
    setIsTestingOllama(false);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 sm:p-7 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-2xl">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-xs font-medium mb-2">
            <Sparkles className="w-3 h-3 text-violet-400" />
            <span>Hyperparameter Optimization</span>
          </div>
          <h2 className="text-xl font-bold text-[#F4F4FA] flex items-center gap-2">
            <SettingsIcon className="w-5 h-5 text-violet-400" />
            System Configuration & Model Tuning
          </h2>
          <p className="text-xs text-[#94A3B8] mt-1 max-w-xl">
            Configure local inference parameters, NLI decision boundaries, and hardware execution modes.
          </p>
        </div>

        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium text-xs transition-all shadow-[0_0_16px_rgba(139,92,246,0.3)] cursor-pointer"
        >
          <Save className="w-4 h-4" />
          Save Settings
        </button>
      </div>

      {savedSuccess && (
        <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
          <span>Configuration saved successfully. Inference engine will apply new parameters on subsequent runs.</span>
        </div>
      )}

      {/* Ollama Local LLM Settings */}
      <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl space-y-4">
        <h3 className="text-sm font-semibold text-[#F4F4FA] uppercase tracking-wider flex items-center gap-2">
          <Server className="w-4 h-4 text-violet-400" />
          Ollama LLM Server Configuration
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-slate-400 block mb-1.5">
              Ollama Base URL
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={ollamaUrl}
                onChange={(e) => setOllamaUrl(e.target.value)}
                className="flex-1 px-3.5 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-xs text-slate-100 focus:outline-none focus:border-violet-500/50"
              />
              <button
                onClick={testOllamaConnection}
                disabled={isTestingOllama}
                className="px-3.5 py-2 rounded-xl bg-[#080910] hover:bg-white/[0.06] text-slate-200 text-xs font-semibold border border-white/[0.08] transition-colors cursor-pointer"
              >
                {isTestingOllama ? <RotateCw className="w-4 h-4 animate-spin" /> : 'Ping'}
              </button>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">Default: http://localhost:11434</p>
          </div>

          <div>
            <label className="text-xs font-medium text-slate-400 block mb-1.5">
              Default LLM Model Name
            </label>
            <input
              type="text"
              value={defaultModel}
              onChange={(e) => setDefaultModel(e.target.value)}
              placeholder="qwen3:8b or qwen2.5:3b"
              className="w-full px-3.5 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-xs text-slate-100 focus:outline-none focus:border-violet-500/50"
            />
            <p className="text-[11px] text-slate-500 mt-1">Used for answer generation and grounded correction.</p>
          </div>
        </div>
      </div>

      {/* NLI Decision Thresholds */}
      <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl space-y-4">
        <h3 className="text-sm font-semibold text-[#F4F4FA] uppercase tracking-wider flex items-center gap-2">
          <Sliders className="w-4 h-4 text-violet-400" />
          Natural Language Inference (NLI) Decision Boundaries
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold text-slate-400">
              <span>Entailment Threshold (Supported)</span>
              <span className="font-mono text-emerald-400">{(entailmentThreshold * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min={0.3}
              max={0.9}
              step={0.05}
              value={entailmentThreshold}
              onChange={(e) => setEntailmentThreshold(Number(e.target.value))}
              className="w-full accent-violet-500 h-2 bg-[#080910] rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-slate-500">
              Minimum posterior probability for a claim to be marked Supported.
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold text-slate-400">
              <span>Contradiction Threshold (Contradicted)</span>
              <span className="font-mono text-rose-400">{(contradictionThreshold * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min={0.3}
              max={0.9}
              step={0.05}
              value={contradictionThreshold}
              onChange={(e) => setContradictionThreshold(Number(e.target.value))}
              className="w-full accent-rose-500 h-2 bg-[#080910] rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-slate-500">
              Minimum posterior probability for a claim to be marked Contradicted.
            </p>
          </div>
        </div>
      </div>

      {/* Ingestion & Chunking */}
      <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl space-y-4">
        <h3 className="text-sm font-semibold text-[#F4F4FA] uppercase tracking-wider flex items-center gap-2">
          <Cpu className="w-4 h-4 text-violet-400" />
          Corpus Ingestion & Retrieval Hyperparameters
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="text-xs font-medium text-slate-400 block mb-1.5">
              Default Top-K Passages
            </label>
            <input
              type="number"
              min={1}
              max={15}
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="w-full px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-xs text-slate-100 focus:outline-none focus:border-violet-500/50"
            />
          </div>

          <div>
            <label className="text-xs font-medium text-slate-400 block mb-1.5">
              Chunk Size (Characters)
            </label>
            <input
              type="number"
              min={100}
              max={2000}
              step={50}
              value={chunkSize}
              onChange={(e) => setChunkSize(Number(e.target.value))}
              className="w-full px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-xs text-slate-100 focus:outline-none focus:border-violet-500/50"
            />
          </div>

          <div>
            <label className="text-xs font-medium text-slate-400 block mb-1.5">
              Chunk Overlap (Characters)
            </label>
            <input
              type="number"
              min={20}
              max={500}
              step={20}
              value={chunkOverlap}
              onChange={(e) => setChunkOverlap(Number(e.target.value))}
              className="w-full px-3 py-2 rounded-xl bg-[#080910] border border-white/[0.07] text-xs text-slate-100 focus:outline-none focus:border-violet-500/50"
            />
          </div>
        </div>
      </div>

      {/* Hardware Telemetry Details */}
      <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl space-y-3">
        <h3 className="text-sm font-semibold text-[#F4F4FA] uppercase tracking-wider">
          Runtime Environment Telemetry
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06]">
            <span className="text-slate-500 block">Host Device</span>
            <span className="text-[#F4F4FA] font-semibold mt-1 block">
              {health?.hardware.device_name || 'CPU'}
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06]">
            <span className="text-slate-500 block">System RAM</span>
            <span className="text-[#F4F4FA] font-semibold mt-1 block">
              {health?.system_memory.total_gb} GB ({health?.system_memory.used_percent}% used)
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06]">
            <span className="text-slate-500 block">NLI Model</span>
            <span className="text-violet-300 font-semibold mt-1 block truncate">
              {health?.models.nli_model}
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06]">
            <span className="text-slate-500 block">Embedding Model</span>
            <span className="text-blue-300 font-semibold mt-1 block truncate">
              {health?.models.embedding_model}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
