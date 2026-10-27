from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EvaluationRunRequest(BaseModel):
    benchmark_name: str = Field(..., description="FEVER, HaluEval, or TruthfulQA")
    task: Optional[str] = Field("qa", description="Benchmark task (e.g. qa, dialogue, summarization, general for HaluEval)")
    sample_size: Optional[int] = Field(20, ge=5, le=500, description="Number of benchmark test samples")
    seed: Optional[int] = Field(42, description="Random seed for reproducible deterministic sampling")
    sampling_strategy: Optional[str] = Field("balanced_sampled", description="Sampling strategy: 'balanced_sampled' or 'balanced_paired'")
    model_name: Optional[str] = Field("cross-encoder/nli-deberta-v3-small", description="Model name evaluated")
    evidence_source: Optional[str] = Field("context", description="'context', 'fever', 'documents', or 'both'")
    split: Optional[str] = Field("paper_dev", description="Dataset split: 'paper_dev' or 'train'")
    top_k: Optional[int] = Field(3, ge=1, le=10)


class FEVERPrepareRequest(BaseModel):
    split: Optional[str] = "paper_dev"
    limit: Optional[int] = 1000
    seed: Optional[int] = 42
    force_download: Optional[bool] = False


class FEVERIndexRequest(BaseModel):
    split: Optional[str] = "paper_dev"
    limit: Optional[int] = 1000
    max_articles: Optional[int] = None
    rebuild: Optional[bool] = True


class FEVERStatusResponse(BaseModel):
    is_downloaded: bool
    splits_available: List[str]
    prepared_samples_count: int
    prepared_files: List[str]
    class_distribution: Dict[str, int]
    evidence_cache_count: int
    fever_index_vectors: int
    fever_index_exists: bool
    embedding_model: str
    last_indexed_at: Optional[str] = None


class HaluEvalTaskStatus(BaseModel):
    available: bool
    file_path: Optional[str] = None
    size_mb: Optional[float] = None
    total_records: Optional[int] = 0
    context_provided: Optional[bool] = False
    error: Optional[str] = None


class HaluEvalStatusResponse(BaseModel):
    is_available: bool
    total_records: int
    tasks: Dict[str, HaluEvalTaskStatus]


class BenchmarkSampleSchema(BaseModel):
    id: str
    benchmark: str
    claim_or_question: str
    ground_truth_label: str  # Supported, Contradicted, Insufficient
    evidence_text: Optional[str] = None


class EvaluationExperimentSchema(BaseModel):
    id: str
    name: str
    benchmark_name: str
    model_name: str
    total_samples: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    retrieval_recall_at_k: float
    confusion_matrix: Dict[str, Dict[str, int]]
    metrics: Dict[str, Any]
    latency_per_sample_ms: float
    created_at: datetime

    class Config:
        from_attributes = True


class MultiModelComparisonRequest(BaseModel):
    benchmark_name: str = Field("HaluEval", description="HaluEval or FEVER")
    task: Optional[str] = Field("qa", description="Task name for HaluEval (qa, dialogue, summarization, general)")
    sample_size: Optional[int] = Field(10, ge=3, le=50, description="Number of evaluation samples to compare")
    seed: Optional[int] = Field(42, description="Deterministic random seed")
    llm_model: Optional[str] = Field("qwen3:8b", description="Ollama model to evaluate")


class ModelPerformanceSummary(BaseModel):
    model_name: str
    model_type: str  # "cross_encoder" | "local_llm" | "hybrid_ensemble"
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    avg_latency_ms: float


class ModelDisagreementItem(BaseModel):
    id: str
    prompt_or_claim: str
    ground_truth: str
    nli_verdict: str
    llm_verdict: str
    ensemble_verdict: str
    explanation: Optional[str] = None


class MultiModelComparisonResponse(BaseModel):
    benchmark_name: str
    task: str
    total_samples: int
    models: List[ModelPerformanceSummary]
    agreement_rate: float
    disagreements_count: int
    disagreements: List[ModelDisagreementItem]
    created_at: datetime

