from fastapi import APIRouter
from backend.app.schemas.claim import ClaimExtractionRequest, ClaimExtractionResponse
from backend.app.nlp.claim_extractor import claim_extractor

router = APIRouter()


@router.post("/claims/extract", response_model=ClaimExtractionResponse)
def extract_claims_endpoint(req: ClaimExtractionRequest):
    claims = claim_extractor.extract_claims(req.text, context_question=req.context_question)
    verifiable = sum(1 for c in claims if c.verifiable)
    return ClaimExtractionResponse(
        total_claims=len(claims),
        verifiable_claims=verifiable,
        claims=claims
    )
