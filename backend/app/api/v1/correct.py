import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.database.database import get_db
from backend.app.database.models import VerificationRun
from backend.app.schemas.correction import CorrectionRequest, CorrectionResponse
from backend.app.schemas.verification import ClaimVerificationResultSchema, EvidenceCandidateSchema
from backend.app.nlp.correction_engine import correction_engine
from backend.app.services.verification_service import verification_service

router = APIRouter()


@router.post("/correct", response_model=CorrectionResponse)
def correct_response_endpoint(req: CorrectionRequest, db: Session = Depends(get_db)):
    run = db.query(VerificationRun).filter(VerificationRun.id == req.verification_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Verification run '{req.verification_id}' not found")

    # Reconstruct claims
    claim_objects = []
    for c in run.claims:
        ev_schemas = [
            EvidenceCandidateSchema(
                chunk_id=ev.chunk_id,
                document_name=ev.document_name,
                page_number=ev.page_number,
                passage_text=ev.passage_text,
                similarity_score=ev.similarity_score,
                nli_label=ev.nli_label,
                entailment_prob=ev.entailment_prob,
                contradiction_prob=ev.contradiction_prob,
                neutral_prob=ev.neutral_prob
            )
            for ev in c.evidence_records
        ]
        claim_objects.append(ClaimVerificationResultSchema(
            claim_id=c.claim_id,
            original_text=c.original_text,
            normalized_claim=c.normalized_claim,
            start_offset=c.start_offset,
            end_offset=c.end_offset,
            claim_type=c.claim_type,
            verifiable=c.verifiable,
            verdict=c.verdict,
            confidence=c.confidence,
            explanation=c.explanation or "",
            evidence_list=ev_schemas
        ))

    # Generate correction
    corr_start = time.perf_counter()
    correction_result = correction_engine.correct_answer(
        question=run.question,
        original_answer=run.original_answer,
        claims=claim_objects,
        model_name=req.model_name,
        temperature=req.temperature or 0.1
    )
    corr_time = (time.perf_counter() - corr_start) * 1000
    logger.info(f"Answer correction generated in {corr_time:.1f}ms.")

    corrected_text = correction_result["corrected_answer"]

    # Re-verify the corrected text through the verification service!
    reverif_start = time.perf_counter()
    reverification_report = verification_service.run_verification(
        db=db,
        question=run.question,
        answer=corrected_text,
        model_name=req.model_name
    )
    reverif_time = (time.perf_counter() - reverif_start) * 1000
    logger.info(f"Closed-loop re-verification completed in {reverif_time:.1f}ms.")

    # Update original run with corrected answer
    run.corrected_answer = corrected_text
    db.commit()

    # Check if newly introduced unsupported statements exist
    new_unsupported = sum(
        1 for c in reverification_report.claims if c.verdict in ["Contradicted", "Insufficient Evidence"]
    )
    is_fully_supported = (reverification_report.contradicted_claims == 0) and (reverification_report.hallucination_score == 0.0)

    # Measure whether correction reduced unsupported or contradicted claims
    contra_before = len(contradicted_claims)
    contra_after = reverification_report.contradicted_claims
    reduction_contra = max(0, contra_before - contra_after)

    unsupported_before = len(insufficient_claims) + len(contradicted_claims)
    unsupported_after = reverification_report.insufficient_claims + reverification_report.contradicted_claims
    reduction_unsupported = max(0, unsupported_before - unsupported_after)

    reduction_pct = 0.0
    if unsupported_before > 0:
        reduction_pct = round((reduction_unsupported / unsupported_before) * 100.0, 1)
    elif contra_before > 0:
        reduction_pct = round((reduction_contra / contra_before) * 100.0, 1)

    # Extract unique citations
    citations = []
    seen_cits = set()
    for c in reverification_report.claims:
        for ev in c.evidence_list:
            cit_key = (ev.document_name, ev.page_number)
            if cit_key not in seen_cits:
                seen_cits.add(cit_key)
                citations.append({
                    "claim": c.normalized_claim,
                    "document_name": ev.document_name,
                    "page_number": ev.page_number or 1,
                    "passage_snippet": ev.passage_text[:140] + "..." if len(ev.passage_text) > 140 else ev.passage_text,
                    "nli_label": ev.nli_label,
                    "similarity_score": ev.similarity_score
                })

    explanation = (
        f"Corrected {correction_result['claims_corrected']} contradicted statement(s) using verified evidence. "
        f"Re-verification confirmed {reverification_report.supported_claims} supported claim(s) "
        f"and {reverification_report.contradicted_claims} contradictions (reduced by {reduction_pct}%)."
    )

    return CorrectionResponse(
        verification_id=run.id,
        original_answer=run.original_answer,
        corrected_answer=corrected_text,
        claims_corrected=correction_result["claims_corrected"],
        unsupported_removed=correction_result["unsupported_removed"],
        reverified_claims=reverification_report.claims,
        is_fully_supported=is_fully_supported,
        newly_introduced_unsupported=new_unsupported,
        reduction_in_contradictions=reduction_contra,
        reduction_in_unsupported=reduction_unsupported,
        hallucination_reduction_pct=reduction_pct,
        citations=citations,
        explanation=explanation
    )
