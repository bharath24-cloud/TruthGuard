from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AtomicClaimItem(BaseModel):
    claim_id: str = Field(..., description="Unique claim identifier, e.g. claim_001")
    original_text: str = Field(..., description="Exact substring span from the input text")
    normalized_claim: str = Field(..., description="Self-contained atomic factual assertion")
    start_offset: int = Field(..., description="0-indexed start character offset in original text")
    end_offset: int = Field(..., description="0-indexed end character offset in original text")
    claim_type: Literal["factual", "subjective", "opinion"] = Field(
        default="factual", description="Classification of statement nature"
    )
    verifiable: bool = Field(default=True, description="Whether claim can be verified against evidence")


class ClaimExtractionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Input text to extract claims from")
    context_question: Optional[str] = Field(None, description="Optional question context")


class ClaimExtractionResponse(BaseModel):
    total_claims: int
    verifiable_claims: int
    claims: List[AtomicClaimItem]
