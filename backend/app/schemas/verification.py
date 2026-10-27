from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EvidenceCandidateSchema(BaseModel):
    chunk_id: Optional[str] = None
    document_name: str
    page_number: Optional[int] = None
    passage_text: str
    similarity_score: float
    nli_label: Literal["entailment", "contradiction", "neutral"]
    entailment_prob: float
    contradiction_prob: float
    neutral_prob: float
    source_type: Optional[str] = "document"  # "document" | "fever"


class ClaimVerificationResultSchema(BaseModel):
    claim_id: str
    original_text: str
    normalized_claim: str
    start_offset: int
    end_offset: int
    claim_type: str
    verifiable: bool
    verdict: Literal["Supported", "Contradicted", "Insufficient Evidence", "Conflicting Evidence"]
    confidence: Optional[float] = None
    confidence_calibrated: bool = False
    inference_reason: str = "NO_EVIDENCE_RETRIEVED"
    evidence_source_used: Optional[str] = "documents"
    explanation: str
    evidence_list: List[EvidenceCandidateSchema]
    investigation_trace: Optional[List[Dict[str, Any]]] = []
    adjudication_notes: Optional[str] = None


class VerificationRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Original question or prompt")
    answer: Optional[str] = Field(None, description="Existing answer (Mode A) or leave None to generate (Mode B)")
    model_name: Optional[str] = Field("qwen3:8b", description="LLM model name to use if generating")
    document_ids: Optional[List[str]] = Field(default=None, description="Filter retrieval to specific documents")
    evidence_source: Optional[Literal["documents", "fever", "both"]] = Field("documents", description="Knowledge base source for retrieval")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of evidence passages to retrieve per claim")
    enable_investigation_agent: Optional[bool] = Field(True, description="Enable autonomous query reformulation and bounded evidence investigation")
    enable_multi_model: Optional[bool] = Field(False, description="Enable secondary local LLM verification and adjudication for conflicting claims")


class VerificationReportResponse(BaseModel):
    id: str
    question: str
    original_answer: str
    corrected_answer: Optional[str] = None
    model_used: str
    evidence_source: Optional[str] = "documents"
    total_claims: int
    verifiable_claims: int
    supported_claims: int
    contradicted_claims: int
    insufficient_claims: int
    conflicting_claims: int
    
    hallucination_score: float = Field(..., description="Calculated composite risk score [0.0 - 1.0]")
    unsupported_claim_rate: float
    contradiction_rate: float
    verification_coverage: float
    evidence_availability: float
    risk_level: Optional[str] = "LOW_RISK"
    uncertainty_score: Optional[float] = 0.0
    abstention_recommended: Optional[bool] = False
    abstention_reason: Optional[str] = None
    
    latency_ms: float
    created_at: datetime
    claims: List[ClaimVerificationResultSchema]
    dependency_graph: Optional[Dict[str, Any]] = None
    investigation_timeline: Optional[List[Dict[str, Any]]] = []

    class Config:
        from_attributes = True

