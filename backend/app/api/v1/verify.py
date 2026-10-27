import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database.database import get_db
from backend.app.database.models import VerificationRun, ExtractedClaim, ClaimEvidence, Document
from backend.app.schemas.verification import (
    VerificationRequest,
    VerificationReportResponse,
    ClaimVerificationResultSchema,
    EvidenceCandidateSchema
)
from backend.app.core.logging import logger
from backend.app.core.config import settings
from backend.app.services.ollama_service import GenerationTimeoutError
from backend.app.services.verification_service import verification_service

router = APIRouter()


@router.post("/verify", response_model=VerificationReportResponse)
def verify_answer(req: VerificationRequest, db: Session = Depends(get_db)):
    try:
        if req.document_ids and (req.evidence_source or "documents") != "fever":
            for doc_id in req.document_ids:
                doc = db.query(Document).filter(Document.id == doc_id).first()
                if not doc:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Document '{doc_id}' was not found in the library. Please verify your document selection."
                    )

        report = verification_service.run_verification(
            db=db,
            question=req.question,
            answer=req.answer,
            model_name=req.model_name,
            document_ids=req.document_ids,
            evidence_source=req.evidence_source or "documents",
            top_k=req.top_k or 5,
            enable_investigation_agent=True if req.enable_investigation_agent is None else req.enable_investigation_agent,
            enable_multi_model=bool(req.enable_multi_model)
        )
        return report
    except (GenerationTimeoutError, TimeoutError) as e:
        logger.error(f"Verification timed out during model generation: {e}")
        raise HTTPException(
            status_code=504,
            detail=(
                f"Model generation timed out: {str(e)} "
                f"The local model ('{req.model_name or settings.DEFAULT_LLM_MODEL}') took too long to generate an answer. "
                "Please provide an answer directly to verify (Mode A), or ensure sufficient GPU/CPU compute resources are available."
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification pipeline failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.get("/verifications", response_model=List[VerificationReportResponse])
def list_verifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    runs = db.query(VerificationRun).order_by(desc(VerificationRun.created_at)).offset(skip).limit(limit).all()
    
    results = []
    for r in runs:
        # Load claims and evidence
        claim_schemas = []
        for c in r.claims:
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
                    neutral_prob=ev.neutral_prob,
                    source_type=getattr(ev, "source_type", "document")
                )
                for ev in c.evidence_records
            ]
            trace = []
            if getattr(c, "investigation_trace_json", None):
                try:
                    trace = json.loads(c.investigation_trace_json)
                except Exception:
                    trace = []

            claim_schemas.append(ClaimVerificationResultSchema(
                claim_id=c.claim_id,
                original_text=c.original_text,
                normalized_claim=c.normalized_claim,
                start_offset=c.start_offset,
                end_offset=c.end_offset,
                claim_type=c.claim_type,
                verifiable=c.verifiable,
                verdict=c.verdict,
                confidence=c.confidence,
                confidence_calibrated=(c.confidence is not None),
                inference_reason=getattr(c, "inference_reason", "NO_EVIDENCE_RETRIEVED"),
                evidence_source_used=getattr(r, "evidence_source", "documents"),
                explanation=c.explanation or "",
                evidence_list=ev_schemas,
                investigation_trace=trace,
                adjudication_notes=getattr(c, "adjudication_notes", None)
            ))

        dep_graph = None
        if getattr(r, "dependency_graph_json", None):
            try:
                dep_graph = json.loads(r.dependency_graph_json)
            except Exception:
                dep_graph = None

        timeline = []
        if getattr(r, "investigation_timeline_json", None):
            try:
                timeline = json.loads(r.investigation_timeline_json)
            except Exception:
                timeline = []

        results.append(VerificationReportResponse(
            id=r.id,
            question=r.question,
            original_answer=r.original_answer,
            corrected_answer=r.corrected_answer,
            model_used=r.model_used,
            evidence_source=getattr(r, "evidence_source", "documents"),
            total_claims=r.total_claims,
            verifiable_claims=r.verifiable_claims,
            supported_claims=r.supported_claims,
            contradicted_claims=r.contradicted_claims,
            insufficient_claims=r.insufficient_claims,
            conflicting_claims=r.conflicting_claims,
            hallucination_score=r.hallucination_score,
            unsupported_claim_rate=r.unsupported_claim_rate,
            contradiction_rate=r.contradiction_rate,
            verification_coverage=r.verification_coverage,
            evidence_availability=r.evidence_availability,
            risk_level=getattr(r, "risk_level", "LOW_RISK") or "LOW_RISK",
            uncertainty_score=getattr(r, "uncertainty_score", 0.0) or 0.0,
            abstention_recommended=getattr(r, "abstention_recommended", False) or False,
            abstention_reason=getattr(r, "abstention_reason", None),
            latency_ms=r.latency_ms,
            created_at=r.created_at,
            claims=claim_schemas,
            dependency_graph=dep_graph,
            investigation_timeline=timeline
        ))

    return results


@router.get("/verifications/{verification_id}", response_model=VerificationReportResponse)
def get_verification(verification_id: str, db: Session = Depends(get_db)):
    r = db.query(VerificationRun).filter(VerificationRun.id == verification_id).first()
    if not r:
        raise HTTPException(status_code=404, detail=f"Verification run '{verification_id}' not found")

    claim_schemas = []
    for c in r.claims:
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
                neutral_prob=ev.neutral_prob,
                source_type=getattr(ev, "source_type", "document")
            )
            for ev in c.evidence_records
        ]
        trace = []
        if getattr(c, "investigation_trace_json", None):
            try:
                trace = json.loads(c.investigation_trace_json)
            except Exception:
                trace = []

        claim_schemas.append(ClaimVerificationResultSchema(
            claim_id=c.claim_id,
            original_text=c.original_text,
            normalized_claim=c.normalized_claim,
            start_offset=c.start_offset,
            end_offset=c.end_offset,
            claim_type=c.claim_type,
            verifiable=c.verifiable,
            verdict=c.verdict,
            confidence=c.confidence,
            confidence_calibrated=(c.confidence is not None),
            inference_reason=getattr(c, "inference_reason", "NO_EVIDENCE_RETRIEVED"),
            evidence_source_used=getattr(r, "evidence_source", "documents"),
            explanation=c.explanation or "",
            evidence_list=ev_schemas,
            investigation_trace=trace,
            adjudication_notes=getattr(c, "adjudication_notes", None)
        ))

    dep_graph = None
    if getattr(r, "dependency_graph_json", None):
        try:
            dep_graph = json.loads(r.dependency_graph_json)
        except Exception:
            dep_graph = None

    timeline = []
    if getattr(r, "investigation_timeline_json", None):
        try:
            timeline = json.loads(r.investigation_timeline_json)
        except Exception:
            timeline = []

    return VerificationReportResponse(
        id=r.id,
        question=r.question,
        original_answer=r.original_answer,
        corrected_answer=r.corrected_answer,
        model_used=r.model_used,
        evidence_source=getattr(r, "evidence_source", "documents"),
        total_claims=r.total_claims,
        verifiable_claims=r.verifiable_claims,
        supported_claims=r.supported_claims,
        contradicted_claims=r.contradicted_claims,
        insufficient_claims=r.insufficient_claims,
        conflicting_claims=r.conflicting_claims,
        hallucination_score=r.hallucination_score,
        unsupported_claim_rate=r.unsupported_claim_rate,
        contradiction_rate=r.contradiction_rate,
        verification_coverage=r.verification_coverage,
        evidence_availability=r.evidence_availability,
        risk_level=getattr(r, "risk_level", "LOW_RISK") or "LOW_RISK",
        uncertainty_score=getattr(r, "uncertainty_score", 0.0) or 0.0,
        abstention_recommended=getattr(r, "abstention_recommended", False) or False,
        abstention_reason=getattr(r, "abstention_reason", None),
        latency_ms=r.latency_ms,
        created_at=r.created_at,
        claims=claim_schemas,
        dependency_graph=dep_graph,
        investigation_timeline=timeline
    )

