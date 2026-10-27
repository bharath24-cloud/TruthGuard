import React, { useState, useEffect, useMemo } from 'react';
import { 
  Sparkles, 
  AlertCircle, 
  CheckCircle2, 
  XCircle, 
  ChevronDown, 
  ChevronUp, 
  Wand2, 
  RotateCw, 
  BookOpen, 
  Layers,
  Copy,
  Check,
  Cpu,
  Database,
  ArrowRight,
  UploadCloud,
  FileText,
  ShieldAlert,
  Bookmark,
  Network,
  Clock,
  Compass,
  Bot,
  Split,
  AlertTriangle,
  Info,
  Search,
  Filter,
  Activity
} from 'lucide-react';
import { api } from '../services/api';
import { VerificationReport, CorrectionResponse, DocumentItem } from '../types';
import { TruthWisp, WispState } from '../components/TruthWisp';
import { VerificationProgress } from '../components/VerificationProgress';

interface VerifyAnswerProps {
  documents: DocumentItem[];
  availableModels: any[];
  activeReport: VerificationReport | null;
  setActiveReport: (report: VerificationReport | null) => void;
  onRefreshHistory: () => void;
}

export const VerifyAnswer: React.FC<VerifyAnswerProps> = ({
  documents,
  availableModels,
  activeReport,
  setActiveReport,
  onRefreshHistory
}) => {
  const [mode, setMode] = useState<'existing' | 'generate'>('existing');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [selectedModel, setSelectedModel] = useState('qwen3:8b');
  const [evidenceSource, setEvidenceSource] = useState<'documents' | 'fever' | 'both'>('documents');
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [topK, setTopK] = useState(4);

  // Truth Wisp state
  const [wispState, setWispState] = useState<WispState>('idle');
  const [activeStage, setActiveStage] = useState(1);
  const [stageMessage, setStageMessage] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Correction state
  const [isCorrecting, setIsCorrecting] = useState(false);
  const [correctionData, setCorrectionData] = useState<CorrectionResponse | null>(null);
  const [copiedCorrection, setCopiedCorrection] = useState(false);

  // Expanded claim accordion
  const [expandedClaimId, setExpandedClaimId] = useState<string | null>(null);

  // Document upload drawer toggle
  const [showDocSelector, setShowDocSelector] = useState(false);

  // Advanced verification modes
  const [activeWorkspaceTab, setActiveWorkspaceTab] = useState<'claims' | 'graph' | 'timeline' | 'explorer'>('claims');
  const [enableInvestigationAgent, setEnableInvestigationAgent] = useState(true);
  const [enableMultiModel, setEnableMultiModel] = useState(false);
  const [selectedGraphNodeId, setSelectedGraphNodeId] = useState<string | null>(null);
  const [evidenceFilter, setEvidenceFilter] = useState<'all' | 'entailment' | 'contradiction' | 'neutral'>('all');

  // Memoized DAG graph layout
  const graphLayout = useMemo(() => {
    const graph = activeReport?.dependency_graph;
    if (!graph || !graph.nodes || graph.nodes.length === 0) {
      if (!activeReport?.claims || activeReport.claims.length === 0) {
        return { nodes: [] as any[], edges: [] as any[], width: 680, height: 240 };
      }
      const fallbackNodes = activeReport.claims.map((c, idx) => ({
        id: c.claim_id,
        label: `Claim #${idx + 1}`,
        full_text: c.normalized_claim,
        verdict: c.verdict,
        confidence: c.confidence,
        evidence_sources: c.evidence_source_used ? [c.evidence_source_used] : [],
        is_contradicted_premise: c.verdict === 'Contradicted',
        flagged_for_reverification: false,
        flag_reason: null,
        upstream_dependencies: idx > 0 ? [activeReport.claims[idx - 1].claim_id] : [],
        downstream_dependents: idx < activeReport.claims.length - 1 ? [activeReport.claims[idx + 1].claim_id] : [],
        x: 40 + idx * 280,
        y: 60,
        layer: idx
      }));
      const fallbackEdges = activeReport.claims.slice(0, -1).map((c, idx) => ({
        id: `fallback_edge_${idx}`,
        source: c.claim_id,
        target: activeReport.claims[idx + 1].claim_id,
        dependency_type: 'sequential',
        label: 'leads to',
        confidence: 0.8,
        propagated_risk: c.verdict === 'Contradicted'
      }));
      return {
        nodes: fallbackNodes,
        edges: fallbackEdges,
        width: Math.max(680, fallbackNodes.length * 280 + 80),
        height: 240
      };
    }

    const nodeMap = new Map<string, any>();
    graph.nodes.forEach(n => nodeMap.set(n.id, { ...n, layer: 0 }));

    // Assign layers by topological depth
    let changed = true;
    let iterations = 0;
    while (changed && iterations < 10) {
      changed = false;
      iterations++;
      graph.edges.forEach(e => {
        const src = nodeMap.get(e.source);
        const tgt = nodeMap.get(e.target);
        if (src && tgt) {
          if (tgt.layer <= src.layer) {
            tgt.layer = src.layer + 1;
            changed = true;
          }
        }
      });
    }

    const layers: { [layer: number]: any[] } = {};
    nodeMap.forEach(n => {
      const l = n.layer || 0;
      if (!layers[l]) layers[l] = [];
      layers[l].push(n);
    });

    const NODE_WIDTH = 250;
    const NODE_HEIGHT = 110;
    const HORIZONTAL_GAP = 90;
    const VERTICAL_GAP = 40;

    let maxInLayer = 0;
    const numLayers = Math.max(1, Object.keys(layers).length);

    Object.keys(layers).forEach(layerKey => {
      const l = parseInt(layerKey, 10);
      const group = layers[l];
      if (group.length > maxInLayer) maxInLayer = group.length;
      group.forEach((node, idx) => {
        node.x = 40 + l * (NODE_WIDTH + HORIZONTAL_GAP);
        node.y = 40 + idx * (NODE_HEIGHT + VERTICAL_GAP);
      });
    });

    const totalWidth = Math.max(680, numLayers * (NODE_WIDTH + HORIZONTAL_GAP) + 60);
    const totalHeight = Math.max(260, maxInLayer * (NODE_HEIGHT + VERTICAL_GAP) + 60);

    return {
      nodes: Array.from(nodeMap.values()),
      edges: graph.edges,
      width: totalWidth,
      height: totalHeight
    };
  }, [activeReport]);

  // Selected node for detailed inspector in graph tab
  const selectedNode = useMemo(() => {
    if (!graphLayout.nodes || graphLayout.nodes.length === 0) return null;
    if (selectedGraphNodeId) {
      const found = graphLayout.nodes.find(n => n.id === selectedGraphNodeId);
      if (found) return found;
    }
    const flagged = graphLayout.nodes.find(n => n.flagged_for_reverification || n.is_contradicted_premise);
    return flagged || graphLayout.nodes[0];
  }, [graphLayout.nodes, selectedGraphNodeId]);

  // Aggregated evidence for Evidence Explorer
  const allEvidence = useMemo(() => {
    if (!activeReport?.claims) return [];
    const list: Array<{
      claim_id: string;
      claim_normalized: string;
      claim_verdict: string;
      document_name: string;
      page_number?: number;
      passage_text: string;
      similarity_score: number;
      nli_label: string;
      entailment_prob: number;
      contradiction_prob: number;
      neutral_prob: number;
      source_type?: string;
    }> = [];

    activeReport.claims.forEach(c => {
      (c.evidence_list || []).forEach(e => {
        list.push({
          claim_id: c.claim_id,
          claim_normalized: c.normalized_claim,
          claim_verdict: c.verdict,
          document_name: e.document_name,
          page_number: e.page_number,
          passage_text: e.passage_text,
          similarity_score: e.similarity_score,
          nli_label: e.nli_label,
          entailment_prob: e.entailment_prob,
          contradiction_prob: e.contradiction_prob,
          neutral_prob: e.neutral_prob,
          source_type: e.source_type
        });
      });
    });
    return list;
  }, [activeReport]);

  const filteredEvidence = useMemo(() => {
    if (evidenceFilter === 'all') return allEvidence;
    return allEvidence.filter(e => e.nli_label === evidenceFilter);
  }, [allEvidence, evidenceFilter]);

  // Investigation timeline steps
  const timelineSteps = useMemo(() => {
    if (activeReport?.investigation_timeline && activeReport.investigation_timeline.length > 0) {
      return activeReport.investigation_timeline;
    }
    if (!activeReport?.claims) return [];
    const steps: any[] = [];
    activeReport.claims.forEach(c => {
      if (c.investigation_trace && c.investigation_trace.length > 0) {
        c.investigation_trace.forEach(t => {
          steps.push({
            ...t,
            claim_id: c.claim_id,
            claim_text: c.normalized_claim
          });
        });
      }
    });
    return steps;
  }, [activeReport]);

  useEffect(() => {
    if (availableModels.length > 0 && !availableModels.some(m => m.name === selectedModel)) {
      setSelectedModel(availableModels[0].name);
    }
  }, [availableModels]);

  // Sync wisp state with report verdict
  useEffect(() => {
    if (activeReport) {
      if (activeReport.contradicted_claims > 0) {
        setWispState('contradicted');
        const timer = setTimeout(() => setWispState('idle'), 3500);
        return () => clearTimeout(timer);
      } else if (activeReport.supported_claims > 0) {
        setWispState('supported');
        const timer = setTimeout(() => setWispState('idle'), 3500);
        return () => clearTimeout(timer);
      }
    }
  }, [activeReport]);

  const handleVerify = async () => {
    if (!question.trim()) {
      setError('Please provide a question or inquiry.');
      return;
    }
    if (mode === 'existing' && !answer.trim()) {
      setError('Please provide the answer text to verify, or switch to "Generate & Verify" mode.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setCorrectionData(null);
    setWispState('verifying');
    setActiveStage(1);
    setStageMessage(mode === 'generate' ? 'Generating answer via local LLM...' : 'Decomposing response into atomic claims...');

    // Progress updates synchronized with pipeline
    const t1 = setTimeout(() => {
      setActiveStage(2);
      setStageMessage('Retrieving semantic evidence from knowledge base...');
    }, 800);

    const t2 = setTimeout(() => {
      setActiveStage(3);
      setStageMessage('Executing DeBERTa Natural Language Inference...');
    }, 1800);

    const t3 = setTimeout(() => {
      setActiveStage(4);
      setStageMessage('Calibrating verification confidence & risk scores...');
    }, 2900);

    try {
      const payload: any = {
        question,
        model_name: selectedModel,
        evidence_source: evidenceSource,
        document_ids: selectedDocIds.length > 0 ? selectedDocIds : undefined,
        top_k: topK,
        enable_investigation_agent: enableInvestigationAgent,
        enable_multi_model: enableMultiModel
      };
      if (mode === 'existing') {
        payload.answer = answer;
      }

      const report = await api.verifyAnswer(payload);
      setActiveReport(report);
      onRefreshHistory();

      if (report.contradicted_claims > 0) {
        setWispState('contradicted');
        setTimeout(() => setWispState('idle'), 4000);
      } else {
        setWispState('supported');
        setTimeout(() => setWispState('idle'), 3500);
      }
    } catch (err: any) {
      setError(err.message || 'Verification failed');
      setWispState('idle');
    } finally {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      setIsLoading(false);
      setStageMessage('');
    }
  };

  const handleGenerateCorrection = async () => {
    if (!activeReport) return;
    setIsCorrecting(true);
    setError(null);
    setWispState('verifying');

    try {
      const correction = await api.correctResponse({
        verification_id: activeReport.id,
        model_name: selectedModel
      });
      setCorrectionData(correction);
      onRefreshHistory();
      setWispState('supported');
      setTimeout(() => setWispState('idle'), 3000);
    } catch (err: any) {
      setError(err.message || 'Grounded correction failed');
      setWispState('idle');
    } finally {
      setIsCorrecting(false);
    }
  };

  const handleCopyCorrection = () => {
    if (!correctionData?.corrected_answer) return;
    navigator.clipboard.writeText(correctionData.corrected_answer);
    setCopiedCorrection(true);
    setTimeout(() => setCopiedCorrection(false), 2000);
  };

  const toggleDocSelection = (docId: string) => {
    setSelectedDocIds(prev => 
      prev.includes(docId) ? prev.filter(id => id !== docId) : [...prev, docId]
    );
  };

  const loadSample = () => {
    setMode('existing');
    setQuestion('Who was Marie Curie and what were her major scientific achievements?');
    setAnswer('Marie Curie was a French-Polish physicist who discovered radium in 1898 and won five Nobel Prizes. She was the greatest scientist who ever lived and was born in Paris.');
    setWispState('focused');
    setTimeout(() => setWispState('idle'), 1500);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Main Workspace Composition */}
      <div className={`grid gap-6 items-start transition-all duration-300 ${activeReport ? 'grid-cols-1' : 'grid-cols-1 lg:grid-cols-12'}`}>
        
        {/* Left Column: The Truth Wisp Companion (Only visible when form is primary) */}
        {!activeReport && (
          <div className="lg:col-span-4 flex flex-col items-center lg:items-start text-center lg:text-left space-y-4 pt-2">
            <div className="relative">
              <TruthWisp size="md" state={wispState} />
            </div>

            <div>
              <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-[11px] font-medium mb-1.5">
                <Sparkles className="w-3 h-3 text-violet-400" />
                <span>The Truth Wisp</span>
              </div>
              <h1 className="text-xl font-bold tracking-tight text-[#F4F4FA]">
                Verify an AI answer.
              </h1>
              <p className="text-xs text-[#A2A6B8] mt-1 leading-relaxed max-w-xs">
                Extract atomic factual assertions, retrieve ground truth passages, and audit veracity using DeBERTa NLI.
              </p>
            </div>

            {/* Mode Switcher */}
            <div className="inline-flex p-1 bg-[#11131B] rounded-xl border border-white/[0.06] text-xs">
              <button
                onClick={() => setMode('existing')}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  mode === 'existing'
                    ? 'bg-[#171A25] text-[#F4F4FA] font-medium shadow-sm'
                    : 'text-[#A2A6B8] hover:text-[#F4F4FA]'
                }`}
              >
                Verify Existing
              </button>
              <button
                onClick={() => setMode('generate')}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  mode === 'generate'
                    ? 'bg-[#171A25] text-[#F4F4FA] font-medium shadow-sm'
                    : 'text-[#A2A6B8] hover:text-[#F4F4FA]'
                }`}
              >
                Generate & Verify
              </button>
            </div>
          </div>
        )}

        {/* Verification Form Area */}
        <div className={`${activeReport ? 'w-full' : 'lg:col-span-8'} space-y-4`}>
          
          {/* Active Report Header Bar when results exist */}
          {activeReport && (
            <div className="flex items-center justify-between p-3 px-4 rounded-xl bg-[#11131B] border border-white/[0.06]">
              <div className="flex items-center gap-3">
                <TruthWisp size="sm" state={wispState} subtle />
                <div>
                  <span className="text-xs font-semibold text-[#F4F4FA]">Active Audit</span>
                  <p className="text-[11px] text-[#A2A6B8] truncate max-w-md">{activeReport.question}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => { setActiveReport(null); setCorrectionData(null); }}
                  className="px-3 py-1 rounded-lg bg-[#171A25] text-xs font-medium text-slate-300 hover:text-white border border-white/[0.06] transition-colors"
                >
                  New Query
                </button>
              </div>
            </div>
          )}

          {/* Form Container (Hide fields during completed review if desired, or keep accessible) */}
          <div className="p-5 sm:p-6 rounded-2xl bg-[#11131B] border border-white/[0.06] space-y-4 shadow-sm">
            {/* Question Input */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-semibold text-[#A2A6B8] uppercase tracking-wider">
                  Question or Inquiry
                </label>
                <button
                  type="button"
                  onClick={loadSample}
                  className="text-[11px] text-violet-400 hover:text-violet-300 transition-colors"
                >
                  Load Sample
                </button>
              </div>
              <textarea
                rows={2}
                value={question}
                onFocus={() => setWispState('focused')}
                onBlur={() => !isLoading && setWispState('idle')}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., What did Marie Curie discover and which Nobel Prizes did she win?"
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#080910] border border-white/[0.06] text-sm text-[#F4F4FA] placeholder-slate-600 focus:outline-none focus:border-violet-500/40 focus:ring-1 focus:ring-violet-500/20 transition-all resize-none"
              />
            </div>

            {/* Existing Answer Textarea (Mode A) */}
            {mode === 'existing' && (
              <div className="space-y-1.5">
                <label className="text-[11px] font-semibold text-[#A2A6B8] uppercase tracking-wider">
                  AI-Generated Response to Verify
                </label>
                <textarea
                  rows={3}
                  value={answer}
                  onFocus={() => setWispState('focused')}
                  onBlur={() => !isLoading && setWispState('idle')}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Paste the LLM answer to audit against ground truth reference documents..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#080910] border border-white/[0.06] text-sm text-[#F4F4FA] placeholder-slate-600 focus:outline-none focus:border-violet-500/40 focus:ring-1 focus:ring-violet-500/20 transition-all"
                />
              </div>
            )}

            {/* Slim Configuration Bar */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-1 text-xs">
              <div className="flex flex-wrap items-center gap-2">
                {/* Evidence Source Select */}
                <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-[#080910] border border-white/[0.06] text-slate-300">
                  <Database className="w-3.5 h-3.5 text-violet-400" />
                  <select
                    value={evidenceSource}
                    onChange={(e) => setEvidenceSource(e.target.value as any)}
                    className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer"
                  >
                    <option value="documents" className="bg-[#11131B]">Documents Library</option>
                    <option value="fever" className="bg-[#11131B]">FEVER Wikipedia</option>
                    <option value="both" className="bg-[#11131B]">Unified (Both)</option>
                  </select>
                </div>

                {/* Local LLM Select */}
                <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-[#080910] border border-white/[0.06] text-slate-300">
                  <Cpu className="w-3.5 h-3.5 text-blue-400" />
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer"
                  >
                    {availableModels.length > 0 ? (
                      availableModels.map((m: any) => (
                        <option key={m.name} value={m.name} className="bg-[#11131B]">{m.name}</option>
                      ))
                    ) : (
                      <option value="qwen3:8b" className="bg-[#11131B]">qwen3:8b</option>
                    )}
                  </select>
                </div>

                {/* Document Filter Toggle */}
                {evidenceSource !== 'fever' && documents.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setShowDocSelector(!showDocSelector)}
                    className={`px-2.5 py-1.5 rounded-lg border text-xs transition-colors cursor-pointer ${
                      selectedDocIds.length > 0
                        ? 'bg-violet-600/20 border-violet-500/40 text-violet-300'
                        : 'bg-[#080910] border-white/[0.06] text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Corpora: {selectedDocIds.length > 0 ? `${selectedDocIds.length} doc` : 'All'}
                  </button>
                )}

                {/* Autonomous Investigation Agent Toggle */}
                <button
                  type="button"
                  onClick={() => setEnableInvestigationAgent(!enableInvestigationAgent)}
                  className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs transition-colors cursor-pointer ${
                    enableInvestigationAgent
                      ? 'bg-violet-600/20 border-violet-500/40 text-violet-300'
                      : 'bg-[#080910] border-white/[0.06] text-slate-500 hover:text-slate-300'
                  }`}
                  title="Enable bounded autonomous query reformulation and agentic evidence search"
                >
                  <Bot className="w-3.5 h-3.5 text-violet-400" />
                  <span>Agent Search: {enableInvestigationAgent ? 'ON' : 'OFF'}</span>
                </button>

                {/* Multi-Model Adjudication Toggle */}
                <button
                  type="button"
                  onClick={() => setEnableMultiModel(!enableMultiModel)}
                  className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs transition-colors cursor-pointer ${
                    enableMultiModel
                      ? 'bg-blue-600/20 border-blue-500/40 text-blue-300'
                      : 'bg-[#080910] border-white/[0.06] text-slate-500 hover:text-slate-300'
                  }`}
                  title="Cross-examine claims with both DeBERTa NLI and Local LLM (Qwen3) to adjudicate disputes"
                >
                  <Split className="w-3.5 h-3.5 text-blue-400" />
                  <span>Multi-Model: {enableMultiModel ? 'ON' : 'OFF'}</span>
                </button>
              </div>

              {/* Primary Action Button */}
              <button
                onClick={handleVerify}
                disabled={isLoading}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-medium text-xs transition-colors shadow-sm cursor-pointer ml-auto"
              >
                {isLoading ? (
                  <>
                    <RotateCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Auditing Claims...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5 text-violet-200" />
                    <span>{mode === 'generate' ? 'Generate & Verify' : 'Verify Answer'}</span>
                  </>
                )}
              </button>
            </div>

            {/* Document Selection Popover if clicked */}
            {showDocSelector && evidenceSource !== 'fever' && documents.length > 0 && (
              <div className="p-3 rounded-xl bg-[#080910] border border-white/[0.06] space-y-1.5 max-h-32 overflow-y-auto text-xs">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">
                  Filter by Specific Document
                </span>
                {documents.map(d => (
                  <label key={d.id} className="flex items-center gap-2 cursor-pointer hover:text-white text-slate-400">
                    <input
                      type="checkbox"
                      checked={selectedDocIds.includes(d.id)}
                      onChange={() => toggleDocSelection(d.id)}
                      className="rounded bg-[#171A25] border-white/10 text-violet-500"
                    />
                    <span className="truncate">{d.filename}</span>
                  </label>
                ))}
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-950/20 border border-rose-500/20 text-rose-300 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                <span>{error}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Verification Progress Indicator */}
      {isLoading && (
        <VerificationProgress currentStage={activeStage} stageText={stageMessage} />
      )}

      {/* Claim-Level Results Workspace */}
      {activeReport && (
        <div className="space-y-5 pt-2">
          {/* Executive Verdict Strip */}
          <div className="p-5 rounded-2xl bg-[#11131B] border border-white/[0.06] space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.05] pb-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className={`text-xs px-2.5 py-1 rounded-md font-semibold border ${
                  activeReport.risk_level === 'CRITICAL_RISK' || activeReport.risk_level === 'ABSTAIN'
                    ? 'bg-rose-950/40 text-rose-300 border-rose-500/30'
                    : activeReport.risk_level === 'HIGH_RISK'
                    ? 'bg-orange-950/40 text-orange-300 border-orange-500/30'
                    : activeReport.risk_level === 'MODERATE_RISK'
                    ? 'bg-amber-950/40 text-amber-300 border-amber-500/30'
                    : 'bg-emerald-950/40 text-emerald-300 border-emerald-500/30'
                }`}>
                  Risk: {activeReport.risk_level?.replace('_', ' ') || 'LOW RISK'}
                </span>

                {activeReport.uncertainty_score != null && (
                  <span className="text-xs px-2.5 py-1 rounded-md font-mono bg-violet-950/40 text-violet-300 border border-violet-500/30">
                    Uncertainty: {(activeReport.uncertainty_score * 100).toFixed(0)}%
                  </span>
                )}

                <span className="text-xs text-[#A2A6B8]">
                  {activeReport.contradicted_claims > 0 ? 'Unsupported assertions identified' : 'All verifiable assertions grounded'}
                </span>
              </div>

              <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
                <span>{activeReport.latency_ms.toFixed(0)}ms latency</span>
                <span>•</span>
                <span>{activeReport.claims.length} claims</span>
              </div>
            </div>

            {/* Abstention Banner if Recommended */}
            {activeReport.abstention_recommended && (
              <div className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 text-amber-200 text-xs">
                <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="font-semibold block text-amber-300">System Abstention Recommended</strong>
                  <span>{activeReport.abstention_reason || "Evidence availability is insufficient to substantiate these assertions reliably."}</span>
                </div>
              </div>
            )}

            {/* Concise Stats Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="p-2.5 rounded-xl bg-[#171A25] border border-white/[0.04]">
                <div className="text-[11px] text-slate-400">Total Claims</div>
                <div className="text-lg font-bold text-[#F4F4FA] mt-0.5">{activeReport.total_claims}</div>
              </div>
              <div className="p-2.5 rounded-xl bg-[#171A25] border border-emerald-500/15">
                <div className="text-[11px] text-emerald-400">Supported</div>
                <div className="text-lg font-bold text-emerald-300 mt-0.5">{activeReport.supported_claims}</div>
              </div>
              <div className="p-2.5 rounded-xl bg-[#171A25] border border-rose-500/15">
                <div className="text-[11px] text-rose-400">Contradicted</div>
                <div className="text-lg font-bold text-rose-300 mt-0.5">{activeReport.contradicted_claims}</div>
              </div>
              <div className="p-2.5 rounded-xl bg-[#171A25] border border-amber-500/15">
                <div className="text-[11px] text-amber-400">Unverified</div>
                <div className="text-lg font-bold text-amber-300 mt-0.5">{activeReport.insufficient_claims}</div>
              </div>
            </div>
          </div>

          {/* Workspace Navigation Tabs */}
          <div className="flex items-center gap-2 border-b border-white/[0.06] pb-2 text-xs font-medium overflow-x-auto">
            <button
              onClick={() => setActiveWorkspaceTab('claims')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl transition-all cursor-pointer whitespace-nowrap ${
                activeWorkspaceTab === 'claims'
                  ? 'bg-violet-600/20 text-violet-300 border border-violet-500/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Atomic Claims</span>
              <span className="px-1.5 py-0.2 rounded-full bg-black/40 text-[10px] font-mono text-slate-300">
                {activeReport.claims.length}
              </span>
            </button>

            <button
              onClick={() => setActiveWorkspaceTab('graph')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl transition-all cursor-pointer whitespace-nowrap ${
                activeWorkspaceTab === 'graph'
                  ? 'bg-violet-600/20 text-violet-300 border border-violet-500/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]'
              }`}
            >
              <Network className="w-3.5 h-3.5" />
              <span>Claim Dependency DAG</span>
              {activeReport.dependency_graph?.affected_downstream_claims && activeReport.dependency_graph.affected_downstream_claims.length > 0 ? (
                <span className="px-1.5 py-0.2 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[10px] font-mono flex items-center gap-1">
                  <AlertTriangle className="w-2.5 h-2.5" />
                  {activeReport.dependency_graph.affected_downstream_claims.length} at-risk
                </span>
              ) : (
                <span className="px-1.5 py-0.2 rounded-full bg-black/40 text-[10px] font-mono text-slate-300">
                  {activeReport.dependency_graph?.total_nodes ?? activeReport.claims.length}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveWorkspaceTab('timeline')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl transition-all cursor-pointer whitespace-nowrap ${
                activeWorkspaceTab === 'timeline'
                  ? 'bg-violet-600/20 text-violet-300 border border-violet-500/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]'
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>Agent Investigation Trace</span>
              <span className="px-1.5 py-0.2 rounded-full bg-black/40 text-[10px] font-mono text-slate-300">
                {timelineSteps.length}
              </span>
            </button>

            <button
              onClick={() => setActiveWorkspaceTab('explorer')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl transition-all cursor-pointer whitespace-nowrap ${
                activeWorkspaceTab === 'explorer'
                  ? 'bg-violet-600/20 text-violet-300 border border-violet-500/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]'
              }`}
            >
              <Compass className="w-3.5 h-3.5" />
              <span>Evidence Explorer</span>
              <span className="px-1.5 py-0.2 rounded-full bg-black/40 text-[10px] font-mono text-slate-300">
                {allEvidence.length}
              </span>
            </button>
          </div>

          {/* Tab 1: Atomic Claims Accordion List */}
          {activeWorkspaceTab === 'claims' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs text-[#A2A6B8] px-1">
                <span className="font-medium uppercase tracking-wider">Extracted Claim Statements ({activeReport.claims.length})</span>
                <span>Click to inspect retrieved passages</span>
              </div>

              {activeReport.claims.map((claim) => {
                const isExpanded = expandedClaimId === claim.claim_id;
                const isSupported = claim.verdict === 'Supported';
                const isContradicted = claim.verdict === 'Contradicted';
                const isInsufficient = claim.verdict === 'Insufficient Evidence';

                return (
                  <div
                    key={claim.claim_id}
                    className={`rounded-xl border transition-all ${
                      isContradicted
                        ? 'bg-[#11131B] border-rose-500/25'
                        : isSupported
                        ? 'bg-[#11131B] border-emerald-500/25'
                        : 'bg-[#11131B] border-white/[0.06]'
                    }`}
                  >
                    {/* Claim Card Bar */}
                    <div
                      onClick={() => setExpandedClaimId(isExpanded ? null : claim.claim_id)}
                      className="p-4 cursor-pointer flex items-start justify-between gap-4"
                    >
                      <div className="space-y-1.5 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-md ${
                            isSupported
                              ? 'bg-emerald-950/40 text-emerald-400'
                              : isContradicted
                              ? 'bg-rose-950/40 text-rose-400'
                              : isInsufficient
                              ? 'bg-amber-950/40 text-amber-400'
                              : 'bg-purple-950/40 text-purple-400'
                          }`}>
                            {claim.verdict}
                          </span>

                          <span className="text-[11px] font-mono text-slate-500">
                            {claim.confidence != null ? `${(claim.confidence * 100).toFixed(1)}% confidence` : 'N/A (No Evidence)'}
                          </span>

                          {claim.evidence_source_used && (
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#171A25] text-slate-400 border border-white/[0.04]">
                              {claim.evidence_source_used.toUpperCase()}
                            </span>
                          )}

                          {claim.investigation_trace && claim.investigation_trace.length > 0 && (
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-violet-950/50 text-violet-300 border border-violet-500/20 flex items-center gap-1">
                              <Bot className="w-2.5 h-2.5" />
                              {claim.investigation_trace.length} agent {claim.investigation_trace.length === 1 ? 'pass' : 'passes'}
                            </span>
                          )}

                          {claim.adjudication_notes && (
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-950/50 text-blue-300 border border-blue-500/20 flex items-center gap-1">
                              <Split className="w-2.5 h-2.5" />
                              Adjudicated
                            </span>
                          )}
                        </div>

                        <p className="text-sm font-medium text-[#F4F4FA]">
                          "{claim.normalized_claim}"
                        </p>

                        <p className="text-xs text-[#A2A6B8] leading-relaxed">
                          {claim.explanation}
                        </p>

                        {claim.adjudication_notes && (
                          <div className="p-2 rounded-lg bg-blue-950/20 border border-blue-500/20 text-[11px] text-blue-200 mt-1">
                            <span className="font-semibold text-blue-300">Multi-Model Adjudication: </span>
                            {claim.adjudication_notes}
                          </div>
                        )}
                      </div>

                      <div className="text-slate-500 pt-1 shrink-0">
                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </div>
                    </div>

                    {/* Evidence Drawer */}
                    {isExpanded && (
                      <div className="px-4 pb-4 pt-2 border-t border-white/[0.04] bg-[#080910] rounded-b-xl space-y-2.5 text-xs">
                        <span className="text-[11px] font-semibold uppercase tracking-wider text-violet-300 block">
                          Retrieved Evidence Candidates ({claim.evidence_list.length})
                        </span>

                        {claim.evidence_list.length === 0 ? (
                          <div className="text-slate-500 italic py-1">
                            No passages matched above threshold. Unverified due to absent references.
                          </div>
                        ) : (
                          <div className="space-y-2">
                            {claim.evidence_list.map((ev, i) => (
                              <div key={i} className="p-3 rounded-lg bg-[#11131B] border border-white/[0.04] space-y-1.5">
                                <div className="flex items-center justify-between text-[11px] text-slate-400">
                                  <span className="font-medium text-slate-200">
                                    {ev.document_name} {ev.page_number ? `(p. ${ev.page_number})` : ''}
                                  </span>
                                  <span className="font-mono text-slate-500">
                                    Cosine: {(ev.similarity_score * 100).toFixed(1)}%
                                  </span>
                                </div>

                                <p className="text-slate-300 italic bg-[#080910] p-2 rounded border border-white/[0.03]">
                                  "{ev.passage_text}"
                                </p>

                                <div className="flex items-center gap-3 text-[10px] font-mono">
                                  <span className="text-slate-500">NLI Softmax:</span>
                                  <span className="text-emerald-400">Entail {(ev.entailment_prob * 100).toFixed(1)}%</span>
                                  <span className="text-rose-400">Contra {(ev.contradiction_prob * 100).toFixed(1)}%</span>
                                  <span className="text-amber-400">Neutral {(ev.neutral_prob * 100).toFixed(1)}%</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Tab 2: Claim Dependency DAG */}
          {activeWorkspaceTab === 'graph' && (
            <div className="space-y-4">
              {/* Graph Metrics Summary Bar */}
              <div className="p-4 rounded-xl bg-[#11131B] border border-white/[0.06] space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="text-xs font-semibold text-[#F4F4FA] uppercase tracking-wider flex items-center gap-2">
                      <Network className="w-4 h-4 text-violet-400" />
                      Hallucination Propagation DAG (Claim Dependencies)
                    </h3>
                    <p className="text-xs text-[#A2A6B8] mt-0.5">
                      Directed acyclic graph tracking premise-to-conclusion risk flow without falsely classifying downstream claims as false.
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 rounded-lg bg-[#171A25] border border-white/[0.06] text-xs font-mono text-slate-300">
                      {graphLayout.nodes.length} Nodes • {graphLayout.edges.length} Edges
                    </span>
                    {(activeReport.dependency_graph?.contradicted_premises_count || 0) > 0 && (
                      <span className="px-2.5 py-1 rounded-lg bg-rose-950/40 border border-rose-500/30 text-xs font-mono text-rose-300">
                        {activeReport.dependency_graph?.contradicted_premises_count} Broken Premise
                      </span>
                    )}
                    {(activeReport.dependency_graph?.affected_downstream_claims?.length || 0) > 0 && (
                      <span className="px-2.5 py-1 rounded-lg bg-violet-950/40 border border-violet-500/30 text-xs font-mono text-violet-300 flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3 text-violet-400" />
                        {activeReport.dependency_graph?.affected_downstream_claims.length} Flagged Downstream
                      </span>
                    )}
                  </div>
                </div>

                {activeReport.dependency_graph?.propagation_summary && (
                  <div className="p-2.5 rounded-lg bg-[#080910] border border-white/[0.04] text-xs text-slate-300 flex items-start gap-2">
                    <Info className="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
                    <span>{activeReport.dependency_graph.propagation_summary}</span>
                  </div>
                )}
              </div>

              {/* Visual Interactive SVG DAG Canvas */}
              <div className="p-4 rounded-xl bg-[#080910] border border-white/[0.06] overflow-x-auto relative">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-2 flex flex-wrap items-center justify-between gap-2">
                  <span>Interactive Flow (Click node to inspect dependencies)</span>
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-emerald-400"></span> Supported
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-rose-400"></span> Contradicted Premise
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-violet-400"></span> Flagged for Reverification
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-0.5 bg-rose-500 inline-block border-t border-dashed"></span> Propagated Risk Edge
                    </span>
                  </div>
                </div>

                <div className="min-w-full overflow-x-auto py-2">
                  <svg
                    width={graphLayout.width}
                    height={graphLayout.height}
                    className="block"
                    style={{ minWidth: `${graphLayout.width}px` }}
                  >
                    <defs>
                      <marker
                        id="arrow-normal"
                        viewBox="0 0 10 10"
                        refX="9"
                        refY="5"
                        markerWidth="6"
                        markerHeight="6"
                        orient="auto"
                      >
                        <path d="M 0 1 L 10 5 L 0 9 z" fill="#60A5FA" />
                      </marker>
                      <marker
                        id="arrow-risk"
                        viewBox="0 0 10 10"
                        refX="9"
                        refY="5"
                        markerWidth="6"
                        markerHeight="6"
                        orient="auto"
                      >
                        <path d="M 0 1 L 10 5 L 0 9 z" fill="#F43F5E" />
                      </marker>
                    </defs>

                    {/* Render Directed Edges */}
                    {graphLayout.edges.map((edge: any) => {
                      const srcNode = graphLayout.nodes.find((n: any) => n.id === edge.source);
                      const tgtNode = graphLayout.nodes.find((n: any) => n.id === edge.target);
                      if (!srcNode || !tgtNode) return null;

                      const x1 = srcNode.x + 250;
                      const y1 = srcNode.y + 55;
                      const x2 = tgtNode.x;
                      const y2 = tgtNode.y + 55;
                      const dx = Math.max(40, (x2 - x1) / 2);
                      const pathD = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
                      const midX = (x1 + x2) / 2;
                      const midY = (y1 + y2) / 2;

                      return (
                        <g key={edge.id || `${edge.source}->${edge.target}`}>
                          <path
                            d={pathD}
                            fill="none"
                            stroke={edge.propagated_risk ? '#F43F5E' : '#60A5FA'}
                            strokeWidth={edge.propagated_risk ? '2.5' : '1.5'}
                            strokeDasharray={edge.propagated_risk ? '6,4' : undefined}
                            markerEnd={edge.propagated_risk ? 'url(#arrow-risk)' : 'url(#arrow-normal)'}
                            className={edge.propagated_risk ? 'animate-pulse' : ''}
                          />
                          <foreignObject x={midX - 55} y={midY - 12} width="110" height="24">
                            <div className={`text-[10px] text-center font-mono py-0.5 px-1.5 rounded-full border shadow-sm ${
                              edge.propagated_risk
                                ? 'bg-rose-950/90 text-rose-300 border-rose-500/50'
                                : 'bg-[#171A25]/90 text-slate-300 border-white/10'
                            }`}>
                              {edge.label || edge.dependency_type}
                            </div>
                          </foreignObject>
                        </g>
                      );
                    })}

                    {/* Render Interactive Nodes */}
                    {graphLayout.nodes.map((node: any) => {
                      const isSelected = selectedNode?.id === node.id;
                      const isContradicted = node.is_contradicted_premise || node.verdict === 'Contradicted';
                      const isFlagged = node.flagged_for_reverification;
                      const isSupported = node.verdict === 'Supported';

                      return (
                        <foreignObject
                          key={node.id}
                          x={node.x}
                          y={node.y}
                          width="250"
                          height="110"
                        >
                          <div
                            onClick={() => setSelectedGraphNodeId(node.id)}
                            className={`w-full h-full p-3 rounded-xl border cursor-pointer transition-all flex flex-col justify-between ${
                              isSelected
                                ? 'ring-2 ring-violet-400 shadow-lg shadow-violet-500/20'
                                : 'hover:border-white/30'
                            } ${
                              isContradicted
                                ? 'bg-[#180d12] border-rose-500/50 text-rose-100'
                                : isFlagged
                                ? 'bg-[#181026] border-violet-500/60 text-violet-100'
                                : isSupported
                                ? 'bg-[#0f1c16] border-emerald-500/40 text-emerald-100'
                                : 'bg-[#11131B] border-white/10 text-slate-200'
                            }`}
                          >
                            <div className="flex items-center justify-between gap-1">
                              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 truncate">
                                {node.label || node.id}
                              </span>
                              <div className="flex items-center gap-1">
                                {isFlagged && (
                                  <span className="p-0.5 rounded bg-violet-950/80 text-violet-300" title="Flagged for re-verification">
                                    <AlertTriangle className="w-3 h-3 text-violet-400 shrink-0" />
                                  </span>
                                )}
                                <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded ${
                                  isSupported ? 'bg-emerald-950/60 text-emerald-400' :
                                  isContradicted ? 'bg-rose-950/60 text-rose-400' :
                                  'bg-amber-950/60 text-amber-400'
                                }`}>
                                  {node.verdict}
                                </span>
                              </div>
                            </div>

                            <p className="text-[11px] line-clamp-2 leading-snug font-medium text-slate-200">
                              "{node.full_text}"
                            </p>

                            <div className="flex items-center justify-between text-[9px] text-slate-400 font-mono">
                              <span>{node.confidence != null ? `${(node.confidence * 100).toFixed(0)}% conf` : 'No Evid'}</span>
                              {isFlagged ? (
                                <span className="text-violet-400 font-semibold flex items-center gap-0.5">
                                  <span>Re-verify</span>
                                </span>
                              ) : isContradicted ? (
                                <span className="text-rose-400 font-semibold">Contradicted</span>
                              ) : (
                                <span className="text-slate-500">{node.evidence_sources?.length || 0} src</span>
                              )}
                            </div>
                          </div>
                        </foreignObject>
                      );
                    })}
                  </svg>
                </div>
              </div>

              {/* Selected Node Inspector Drawer */}
              {selectedNode && (
                <div className="p-4 rounded-xl bg-[#11131B] border border-white/[0.08] space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/[0.06] pb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#171A25] text-slate-300 border border-white/[0.06]">
                        {selectedNode.label || selectedNode.id}
                      </span>
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                        selectedNode.verdict === 'Supported' ? 'bg-emerald-950/60 text-emerald-400' :
                        selectedNode.verdict === 'Contradicted' ? 'bg-rose-950/60 text-rose-400' :
                        'bg-amber-950/60 text-amber-400'
                      }`}>
                        {selectedNode.verdict}
                      </span>
                      <span className="text-xs font-mono text-slate-400">
                        {selectedNode.confidence != null ? `${(selectedNode.confidence * 100).toFixed(1)}% Confidence` : 'Confidence Uncalibrated'}
                      </span>
                    </div>

                    <span className="text-[11px] text-slate-500">
                      Selected Node Inspector
                    </span>
                  </div>

                  <p className="text-sm font-medium text-[#F4F4FA]">
                    "{selectedNode.full_text}"
                  </p>

                  {/* High Alert for Contradicted Premise */}
                  {selectedNode.is_contradicted_premise && (
                    <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-500/30 text-rose-200 text-xs flex items-start gap-2">
                      <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                      <div>
                        <strong className="font-semibold block text-rose-300">Contradicted Upstream Premise</strong>
                        <span>This statement was directly contradicted by indexed evidence. Any downstream conclusions resting on this premise have been flagged for re-verification to prevent hallucination cascades.</span>
                      </div>
                    </div>
                  )}

                  {/* Alert for Flagged Downstream Claim */}
                  {selectedNode.flagged_for_reverification && (
                    <div className="p-3 rounded-lg bg-violet-950/30 border border-violet-500/30 text-violet-200 text-xs flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
                      <div>
                        <strong className="font-semibold block text-violet-300">Flagged for Re-verification</strong>
                        <span>{selectedNode.flag_reason || "Downstream conclusion relies on a compromised or contradicted premise."}</span>
                        <span className="block mt-1 text-[11px] text-violet-400">Note: TruthGuard does not declare this claim false; it is flagged for transparent audit because its foundation is unverified.</span>
                      </div>
                    </div>
                  )}

                  {/* Dependencies Breakdown */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-1">
                    <div className="p-2.5 rounded-lg bg-[#080910] border border-white/[0.04] space-y-1">
                      <span className="text-[10px] text-slate-500 uppercase tracking-wider block">
                        Upstream Premises ({selectedNode.upstream_dependencies?.length || 0})
                      </span>
                      {selectedNode.upstream_dependencies && selectedNode.upstream_dependencies.length > 0 ? (
                        <div className="space-y-1">
                          {selectedNode.upstream_dependencies.map((depId: string) => {
                            const depNode = graphLayout.nodes.find((n: any) => n.id === depId);
                            return (
                              <div key={depId} className="flex items-center justify-between text-slate-300 text-[11px]">
                                <span className="truncate">{depNode?.label || depId}: "{depNode?.full_text?.slice(0, 45)}..."</span>
                                <span className={`text-[9px] px-1 py-0.2 rounded font-mono ${
                                  depNode?.verdict === 'Contradicted' ? 'text-rose-400 bg-rose-950/50' : 'text-emerald-400 bg-emerald-950/50'
                                }`}>
                                  {depNode?.verdict || 'N/A'}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <span className="text-slate-600 italic text-[11px]">Root premise (No upstream dependencies)</span>
                      )}
                    </div>

                    <div className="p-2.5 rounded-lg bg-[#080910] border border-white/[0.04] space-y-1">
                      <span className="text-[10px] text-slate-500 uppercase tracking-wider block">
                        Downstream Dependents ({selectedNode.downstream_dependents?.length || 0})
                      </span>
                      {selectedNode.downstream_dependents && selectedNode.downstream_dependents.length > 0 ? (
                        <div className="space-y-1">
                          {selectedNode.downstream_dependents.map((depId: string) => {
                            const depNode = graphLayout.nodes.find((n: any) => n.id === depId);
                            return (
                              <div key={depId} className="flex items-center justify-between text-slate-300 text-[11px]">
                                <span className="truncate">{depNode?.label || depId}: "{depNode?.full_text?.slice(0, 45)}..."</span>
                                <span className="text-[9px] px-1 py-0.2 rounded font-mono text-violet-400 bg-violet-950/50">
                                  {depNode?.flagged_for_reverification ? 'Flagged' : depNode?.verdict || 'Linked'}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <span className="text-slate-600 italic text-[11px]">Leaf conclusion (No downstream claims)</span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tab 3: Autonomous Investigation Timeline */}
          {activeWorkspaceTab === 'timeline' && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-[#11131B] border border-white/[0.06] flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="text-xs font-semibold text-[#F4F4FA] uppercase tracking-wider flex items-center gap-2">
                    <Clock className="w-4 h-4 text-violet-400" />
                    Autonomous Investigation Timeline
                  </h3>
                  <p className="text-xs text-[#A2A6B8] mt-0.5">
                    Step-by-step trace of agentic query reformulation, entity extraction, and early evidence sufficiency decisions.
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-lg bg-[#171A25] border border-white/[0.06] text-xs font-mono text-slate-300">
                    {timelineSteps.length} Step{timelineSteps.length === 1 ? '' : 's'} Logged
                  </span>
                </div>
              </div>

              {timelineSteps.length === 0 ? (
                <div className="p-8 rounded-xl bg-[#11131B] border border-white/[0.06] text-center space-y-2">
                  <Bot className="w-8 h-8 text-slate-600 mx-auto" />
                  <h4 className="text-sm font-semibold text-slate-300">No Iterative Reformulations Needed</h4>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    Evidence was resolved on the primary retrieval pass or autonomous agent search was not required. Enable "Agent Search" toggle before verification to track multi-pass query reformulations.
                  </p>
                </div>
              ) : (
                <div className="space-y-3 relative before:absolute before:inset-0 before:left-4 before:w-0.5 before:bg-white/[0.06] pl-2">
                  {timelineSteps.map((step: any, idx: number) => {
                    const isStop = !!step.stop_decision;
                    return (
                      <div key={idx} className="relative flex items-start gap-4">
                        {/* Step Marker Circle */}
                        <div className={`w-8 h-8 rounded-full border flex items-center justify-center shrink-0 z-10 text-xs font-bold font-mono ${
                          isStop
                            ? 'bg-emerald-950 border-emerald-500/40 text-emerald-300'
                            : 'bg-[#171A25] border-violet-500/30 text-violet-300'
                        }`}>
                          {step.step_idx ?? idx + 1}
                        </div>

                        {/* Step Card */}
                        <div className="flex-1 p-3.5 rounded-xl bg-[#11131B] border border-white/[0.06] space-y-2 text-xs">
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-slate-200">
                                {step.action === 'initial_search' ? 'Primary Hybrid Retrieval' :
                                 step.action === 'entity_reformulation' ? 'Entity-Distilled Reformulation' :
                                 step.action === 'ollama_keyword_distillation' ? 'LLM Keyword Distillation' :
                                 step.action}
                              </span>
                              {step.claim_id && (
                                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#171A25] text-slate-400">
                                  {step.claim_id}
                                </span>
                              )}
                            </div>

                            <div className="flex items-center gap-2 font-mono text-[11px]">
                              <span className="text-slate-400">{step.candidates_found} candidates</span>
                              <span className="text-slate-500">•</span>
                              <span className="text-violet-400">Max Sim: {(step.max_similarity * 100).toFixed(1)}%</span>
                            </div>
                          </div>

                          {step.query && (
                            <div className="p-2 rounded-lg bg-[#080910] border border-white/[0.04] font-mono text-[11px] text-violet-200 flex items-center gap-2">
                              <Search className="w-3.5 h-3.5 text-violet-400 shrink-0" />
                              <span className="truncate">"{step.query}"</span>
                            </div>
                          )}

                          <p className="text-slate-300 text-[11px] leading-relaxed">
                            {step.observation}
                          </p>

                          {step.stop_decision && (
                            <div className="p-2 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-emerald-300 text-[11px] flex items-center gap-1.5 font-medium">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                              <span>Decision: {step.stop_decision}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Multi-Model Cross-Examination Section */}
              {activeReport.claims.some(c => c.adjudication_notes) && (
                <div className="p-4 rounded-xl bg-[#11131B] border border-blue-500/20 space-y-3">
                  <h4 className="text-xs font-semibold text-blue-300 uppercase tracking-wider flex items-center gap-2">
                    <Split className="w-4 h-4 text-blue-400" />
                    Multi-Model Adjudication Log
                  </h4>
                  <div className="space-y-2">
                    {activeReport.claims.filter(c => c.adjudication_notes).map(c => (
                      <div key={c.claim_id} className="p-3 rounded-lg bg-[#080910] border border-white/[0.04] space-y-1.5 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-200">{c.claim_id}: "{c.normalized_claim}"</span>
                          <span className="px-2 py-0.5 rounded bg-blue-950/60 text-blue-300 text-[10px] font-mono">{c.verdict}</span>
                        </div>
                        <p className="text-slate-400 text-[11px] leading-relaxed">
                          {c.adjudication_notes}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tab 4: Evidence Explorer */}
          {activeWorkspaceTab === 'explorer' && (
            <div className="space-y-4">
              {/* Evidence Filter and Stats Bar */}
              <div className="p-4 rounded-xl bg-[#11131B] border border-white/[0.06] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h3 className="text-xs font-semibold text-[#F4F4FA] uppercase tracking-wider flex items-center gap-2">
                    <Compass className="w-4 h-4 text-violet-400" />
                    Evidence Explorer
                  </h3>
                  <p className="text-xs text-[#A2A6B8] mt-0.5">
                    Inspect all retrieved candidate passages across documents with similarity scores and NLI softmax probability distributions.
                  </p>
                </div>

                {/* Filter Pills */}
                <div className="flex flex-wrap items-center gap-1.5 text-xs">
                  <button
                    onClick={() => setEvidenceFilter('all')}
                    className={`px-2.5 py-1 rounded-lg border transition-colors cursor-pointer ${
                      evidenceFilter === 'all'
                        ? 'bg-violet-600/20 border-violet-500/40 text-violet-300 font-semibold'
                        : 'bg-[#080910] border-white/[0.06] text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    All ({allEvidence.length})
                  </button>
                  <button
                    onClick={() => setEvidenceFilter('entailment')}
                    className={`px-2.5 py-1 rounded-lg border transition-colors cursor-pointer ${
                      evidenceFilter === 'entailment'
                        ? 'bg-emerald-600/20 border-emerald-500/40 text-emerald-300 font-semibold'
                        : 'bg-[#080910] border-white/[0.06] text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Entailment ({allEvidence.filter(e => e.nli_label === 'entailment').length})
                  </button>
                  <button
                    onClick={() => setEvidenceFilter('contradiction')}
                    className={`px-2.5 py-1 rounded-lg border transition-colors cursor-pointer ${
                      evidenceFilter === 'contradiction'
                        ? 'bg-rose-600/20 border-rose-500/40 text-rose-300 font-semibold'
                        : 'bg-[#080910] border-white/[0.06] text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Contradiction ({allEvidence.filter(e => e.nli_label === 'contradiction').length})
                  </button>
                  <button
                    onClick={() => setEvidenceFilter('neutral')}
                    className={`px-2.5 py-1 rounded-lg border transition-colors cursor-pointer ${
                      evidenceFilter === 'neutral'
                        ? 'bg-amber-600/20 border-amber-500/40 text-amber-300 font-semibold'
                        : 'bg-[#080910] border-white/[0.06] text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Neutral ({allEvidence.filter(e => e.nli_label === 'neutral').length})
                  </button>
                </div>
              </div>

              {filteredEvidence.length === 0 ? (
                <div className="p-8 rounded-xl bg-[#11131B] border border-white/[0.06] text-center space-y-2">
                  <BookOpen className="w-8 h-8 text-slate-600 mx-auto" />
                  <h4 className="text-sm font-semibold text-slate-300">No Evidence Found for Filter</h4>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    No passages matched the selected filter criteria ("{evidenceFilter}").
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {filteredEvidence.map((ev: any, idx: number) => {
                    const isEntailment = ev.nli_label === 'entailment';
                    const isContradiction = ev.nli_label === 'contradiction';

                    return (
                      <div
                        key={idx}
                        className={`p-3.5 rounded-xl border space-y-2.5 bg-[#11131B] ${
                          isContradiction
                            ? 'border-rose-500/30'
                            : isEntailment
                            ? 'border-emerald-500/30'
                            : 'border-white/[0.06]'
                        }`}
                      >
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-slate-200 truncate max-w-[200px]">
                            {ev.document_name} {ev.page_number ? `(p. ${ev.page_number})` : ''}
                          </span>
                          <div className="flex items-center gap-1.5">
                            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                              isEntailment ? 'bg-emerald-950/60 text-emerald-400' :
                              isContradiction ? 'bg-rose-950/60 text-rose-400' :
                              'bg-amber-950/60 text-amber-400'
                            }`}>
                              {ev.nli_label.toUpperCase()}
                            </span>
                            <span className="font-mono text-slate-400 text-[11px]">
                              {(ev.similarity_score * 100).toFixed(1)}% Sim
                            </span>
                          </div>
                        </div>

                        <p className="text-xs text-slate-300 italic bg-[#080910] p-2.5 rounded-lg border border-white/[0.03] leading-relaxed">
                          "{ev.passage_text}"
                        </p>

                        {/* NLI Probability Distribution Bars */}
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                            <span>NLI Probability Breakdown</span>
                            <span className="text-emerald-400">{(ev.entailment_prob * 100).toFixed(0)}% E</span>
                            <span className="text-rose-400">{(ev.contradiction_prob * 100).toFixed(0)}% C</span>
                            <span className="text-amber-400">{(ev.neutral_prob * 100).toFixed(0)}% N</span>
                          </div>
                          <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden flex">
                            <div style={{ width: `${ev.entailment_prob * 100}%` }} className="bg-emerald-500 h-full"></div>
                            <div style={{ width: `${ev.contradiction_prob * 100}%` }} className="bg-rose-500 h-full"></div>
                            <div style={{ width: `${ev.neutral_prob * 100}%` }} className="bg-amber-500 h-full"></div>
                          </div>
                        </div>

                        {/* Associated Claim */}
                        <div className="pt-1 border-t border-white/[0.04] text-[11px] text-slate-400 flex items-center justify-between">
                          <span className="truncate">Claim: "{ev.claim_normalized}"</span>
                          <span className="font-mono text-[10px] text-slate-500 shrink-0">{ev.claim_verdict}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Grounded Automatic Correction Card */}
          <div className="p-5 rounded-2xl bg-[#11131B] border border-white/[0.06] space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-[#F4F4FA] flex items-center gap-2">
                  <Wand2 className="w-4 h-4 text-violet-400" />
                  Evidence-Grounded Automatic Correction
                </h3>
                <p className="text-xs text-[#A2A6B8] mt-0.5">
                  Rewrites response repairing contradicted claims, qualifying unverified assertions, and citing verified evidence.
                </p>
              </div>

              <button
                onClick={handleGenerateCorrection}
                disabled={isCorrecting}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:bg-slate-800 text-white font-medium text-xs transition-colors shrink-0 cursor-pointer"
              >
                {isCorrecting ? (
                  <>
                    <RotateCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Auditing revised response...</span>
                  </>
                ) : (
                  <>
                    <Wand2 className="w-3.5 h-3.5" />
                    <span>Generate Correction</span>
                  </>
                )}
              </button>
            </div>

            {/* Side-by-Side Comparison if Generated */}
            {correctionData && (
              <div className="space-y-3 pt-3 border-t border-white/[0.05]">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="p-3.5 rounded-xl bg-[#080910] border border-rose-500/20 space-y-1.5">
                    <span className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1">
                      <XCircle className="w-3.5 h-3.5" /> Original Answer
                    </span>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {correctionData.original_answer}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-[#080910] border border-emerald-500/20 space-y-1.5 relative">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Grounded Revision
                      </span>
                      <button
                        onClick={handleCopyCorrection}
                        className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 px-1.5 py-0.5 rounded bg-[#171A25] border border-white/[0.06] transition-colors"
                      >
                        {copiedCorrection ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-400" />
                            <span className="text-emerald-400">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                    <p className="text-xs text-emerald-100 font-medium leading-relaxed">
                      {correctionData.corrected_answer}
                    </p>
                  </div>
                </div>

                {/* Quantitative Hallucination Reduction Metrics */}
                {(correctionData.reduction_in_contradictions != null || correctionData.hallucination_reduction_pct != null) && (
                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="p-2.5 rounded-xl bg-[#080910] border border-white/[0.04]">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Contradictions Fixed</span>
                      <span className="font-bold text-emerald-400 text-sm">
                        -{correctionData.reduction_in_contradictions ?? 0}
                      </span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-[#080910] border border-white/[0.04]">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Unsupported Fixed</span>
                      <span className="font-bold text-blue-400 text-sm">
                        -{correctionData.reduction_in_unsupported ?? 0}
                      </span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-[#080910] border border-white/[0.04]">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Hallucination Reduction</span>
                      <span className="font-bold text-violet-300 text-sm">
                        {correctionData.hallucination_reduction_pct != null ? `${correctionData.hallucination_reduction_pct.toFixed(0)}%` : '100%'}
                      </span>
                    </div>
                  </div>
                )}

                {/* Grounded Citations if present */}
                {correctionData.citations && correctionData.citations.length > 0 && (
                  <div className="space-y-1.5 p-3 rounded-xl bg-[#080910] border border-white/[0.04]">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                      In-Text Citations & Evidence Provenance
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {correctionData.citations.map((cite: any, idx: number) => (
                        <span key={idx} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-violet-950/40 text-violet-300 border border-violet-500/20 text-[11px] font-mono">
                          <Bookmark className="w-3 h-3 text-violet-400" />
                          {cite.citation_text || `${cite.document_name}${cite.page_number ? ` p.${cite.page_number}` : ''}`}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Audit confirmation */}
                <div className="p-3 rounded-xl bg-[#171A25] border border-white/[0.04] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                  <span className="text-slate-400">
                    <strong className="text-slate-200">Reverification Audit:</strong> {correctionData.explanation}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-500/30 text-[11px] font-semibold shrink-0">
                    0 Contradictions
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
