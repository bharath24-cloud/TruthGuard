from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.verification import ClaimVerificationResultSchema


class CorrectionRequest(BaseModel):
    verification_id: str = Field(..., description="ID of completed verification run")
    model_name: Optional[str] = Field("qwen3:8b", description="LLM model to use for grounded correction")
    temperature: Optional[float] = Field(0.1, ge=0.0, le=1.0)


class CorrectionResponse(BaseModel):
    verification_id: str
    original_answer: str
    corrected_answer: str
    claims_corrected: int
    unsupported_removed: int
    reverified_claims: List[ClaimVerificationResultSchema]
    is_fully_supported: bool
    newly_introduced_unsupported: int
    reduction_in_contradictions: Optional[int] = 0
    reduction_in_unsupported: Optional[int] = 0
    hallucination_reduction_pct: Optional[float] = 0.0
    citations: Optional[List[Dict[str, Any]]] = []
    explanation: str
