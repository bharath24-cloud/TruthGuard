export type VerdictType = "Supported" | "Contradicted" | "Insufficient Evidence" | "Conflicting Evidence";

export interface EvidenceCandidate {
  chunk_id?: string;
  document_name: string;
  page_number?: number;
  passage_text: string;
  similarity_score: number;
  nli_label: "entailment" | "contradiction" | "neutral";
  entailment_prob: number;
  contradiction_prob: number;
  neutral_prob: number;
  source_type?: string;
}

export interface ClaimResult {
  claim_id: string;
  original_text: string;
  normalized_claim: string;
  start_offset: number;
  end_offset: number;
  claim_type: "factual" | "subjective" | "opinion";
  verifiable: boolean;
  verdict: VerdictType;
  confidence?: number | null;
  confidence_calibrated?: boolean;
  inference_reason?: string;
  evidence_source_used?: string;
  explanation: string;
  evidence_list: EvidenceCandidate[];
  investigation_trace?: Array<{
    step_idx: number;
    action: string;
    query: string;
    candidates_found: number;
    max_similarity: number;
    observation: string;
    stop_decision?: string;
  }>;
  adjudication_notes?: string | null;
}

export interface DependencyNode {
  id: string;
  label: string;
  full_text: string;
  verdict: VerdictType;
  confidence?: number | null;
  evidence_sources: string[];
  is_contradicted_premise: boolean;
  flagged_for_reverification: boolean;
  flag_reason?: string | null;
  upstream_dependencies: string[];
  downstream_dependents: string[];
}

export interface DependencyEdge {
  id: string;
  source: string;
  target: string;
  dependency_type: string;
  label: string;
  confidence: number;
  propagated_risk: boolean;
}

export interface DependencyGraphData {
  nodes: DependencyNode[];
  edges: DependencyEdge[];
  total_nodes: number;
  total_edges: number;
  contradicted_premises_count: number;
  affected_downstream_claims: string[];
  propagation_summary: string;
}

export interface InvestigationTimelineStep {
  step_idx: number;
  claim_id: string;
  claim_text?: string;
  action: string;
  query: string;
  candidates_found: number;
  max_similarity: number;
  observation: string;
  stop_decision?: string;
}

export interface VerificationReport {
  id: string;
  question: string;
  original_answer: string;
  corrected_answer?: string | null;
  model_used: string;
  evidence_source?: string;
  total_claims: number;
  verifiable_claims: number;
  supported_claims: number;
  contradicted_claims: number;
  insufficient_claims: number;
  conflicting_claims: number;
  hallucination_score: number;
  unsupported_claim_rate: number;
  contradiction_rate: number;
  verification_coverage: number;
  evidence_availability: number;
  risk_level?: string;
  uncertainty_score?: number;
  abstention_recommended?: boolean;
  abstention_reason?: string | null;
  latency_ms: number;
  created_at: string;
  claims: ClaimResult[];
  dependency_graph?: DependencyGraphData;
  investigation_timeline?: InvestigationTimelineStep[];
}

export interface FEVERStatus {
  is_downloaded: boolean;
  splits_available: string[];
  prepared_samples_count: number;
  prepared_files: string[];
  class_distribution: Record<string, number>;
  evidence_cache_count: number;
  fever_index_vectors: number;
  fever_index_exists: boolean;
  embedding_model: string;
  last_indexed_at?: string | null;
}

export interface HaluEvalTaskInfo {
  available: boolean;
  file_path?: string;
  size_mb?: number;
  total_records?: number;
  context_provided?: boolean;
  error?: string;
}

export interface HaluEvalStatus {
  is_available: boolean;
  total_records: number;
  tasks: Record<string, HaluEvalTaskInfo>;
}

export interface EvaluationPrediction {
  id: string;
  task?: string;
  claim_or_question: string;
  ground_truth: string;
  predicted_label: string;
  is_correct: boolean;
  hallucination_score: number;
  hallucination_detected?: boolean;
  latency_ms?: number;
  evidence_text?: string;
  num_claims?: number;
  abstention?: boolean;
  explanation?: string;
}

export interface CorrectionResponse {
  verification_id: string;
  original_answer: string;
  corrected_answer: string;
  claims_corrected: number;
  unsupported_removed: number;
  reverified_claims: ClaimResult[];
  is_fully_supported: boolean;
  newly_introduced_unsupported: number;
  reduction_in_contradictions?: number;
  reduction_in_unsupported?: number;
  hallucination_reduction_pct?: number;
  citations?: any[];
  explanation: string;
}

export interface ModelPerformanceSummary {
  model_name: string;
  model_type: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  avg_latency_ms: number;
}

export interface ModelDisagreementItem {
  id: string;
  prompt_or_claim: string;
  ground_truth: string;
  nli_verdict: string;
  llm_verdict: string;
  ensemble_verdict: string;
  explanation?: string;
}

export interface MultiModelComparisonResponse {
  benchmark_name: string;
  task: string;
  total_samples: number;
  models: ModelPerformanceSummary[];
  agreement_rate: number;
  disagreements_count: number;
  disagreements: ModelDisagreementItem[];
  created_at: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  total_pages: number;
  total_chunks: number;
  created_at: string;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  page_number?: number;
  start_char: number;
  end_char: number;
  content: string;
  token_count: number;
}

export interface EvaluationExperiment {
  id: string;
  name: string;
  benchmark_name: string;
  model_name: string;
  total_samples: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  retrieval_recall_at_k: number;
  confusion_matrix: Record<string, Record<string, number>>;
  metrics: Record<string, any>;
  latency_per_sample_ms: number;
  created_at: string;
}


export interface SystemHealth {
  status: string;
  project: string;
  version: string;
  ollama: {
    status: string;
    message: string;
    base_url: string;
    default_model: string;
  };
  hardware: {
    cuda_available: boolean;
    device_count: number;
    device_name: string;
    active_device: string;
  };
  system_memory: {
    total_gb: number;
    available_gb: number;
    used_percent: number;
  };
  models: {
    embedding_model: string;
    nli_model: string;
  };
}
