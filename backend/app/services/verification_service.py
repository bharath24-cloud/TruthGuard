import time
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.nlp.claim_extractor import claim_extractor
from backend.app.nlp.retriever import retrieve_multi_source, retriever, sync_documents_index
from backend.app.nlp.nli_verifier import nli_verifier
from backend.app.nlp.evidence_aggregator import evidence_aggregator
from backend.app.nlp.hallucination_scorer import hallucination_scorer
from backend.app.nlp.explanation_engine import explanation_engine
from backend.app.nlp.investigation_agent import investigation_agent
from backend.app.nlp.dependency_graph import dependency_graph_builder
from backend.app.services.ollama_service import ollama_service
from backend.app.schemas.verification import (
    EvidenceCandidateSchema,
    ClaimVerificationResultSchema,
    VerificationReportResponse
)
from backend.app.database.models import (
    VerificationRun,
    ExtractedClaim,
    ClaimEvidence,
    Document
)


class VerificationService:
    """
    Coordinates the complete research-grade verification pipeline:
    Answer Generation (Optional) -> Claim Extraction -> Multi-Source Semantic Retrieval ->
    NLI Verification -> Multi-Evidence Aggregation -> Scoring -> Grounded Explanation -> Persistence.
    """

    def run_verification(
        self,
        db: Session,
        question: str,
        answer: Optional[str] = None,
        model_name: Optional[str] = "qwen3:8b",
        document_ids: Optional[List[str]] = None,
        evidence_source: str = "documents",
        top_k: int = 5,
        enable_investigation_agent: bool = True,
        enable_multi_model: bool = False
    ) -> VerificationReportResponse:
        start_time = time.perf_counter()

        # Normalize document filter
        norm_doc_ids = [d for d in document_ids if d] if document_ids else None
        
        # 1. Answer Acquisition
        actual_model = model_name or "manual"
        gen_time = 0.0
        if not answer or not answer.strip():
            logger.info(f"Mode B: Generating answer for question using model '{actual_model}'...")
            gen_start = time.perf_counter()
            mode_b_system = (
                "You are a factual AI assistant. Provide a direct, concise factual answer "
                "in 2 to 3 sentences. State key facts clearly without conversational filler, "
                "speculation, or internal thinking."
            )
            answer = ollama_service.generate(
                prompt=question,
                model=actual_model,
                system_prompt=mode_b_system,
                temperature=0.1,
                max_tokens=settings.MODE_B_MAX_TOKENS,
                timeout=settings.OLLAMA_GENERATION_TIMEOUT,
                think=False
            )
            gen_time = (time.perf_counter() - gen_start) * 1000
            logger.info(f"Mode B: Answer generated in {gen_time:.1f}ms ({len(answer)} chars).")
        else:
            logger.info("Mode A: Verifying user-provided answer...")

        # 2. Atomic Claim Extraction
        extract_start = time.perf_counter()
        raw_claims = claim_extractor.extract_claims(answer, context_question=question)
        extract_time = (time.perf_counter() - extract_start) * 1000
        logger.info(f"Extracted {len(raw_claims)} atomic claims in {extract_time:.1f}ms.")

        verified_claims: List[ClaimVerificationResultSchema] = []
        all_investigation_timeline: List[Dict[str, Any]] = []

        # 3. Process each claim with Autonomous Investigation Agent or Direct Retrieval
        retrieval_nli_start = time.perf_counter()
        for claim_item in raw_claims:
            if not claim_item.verifiable:
                agg_result = evidence_aggregator.aggregate_evidence([], verifiable=False)
                verdict = agg_result.verdict
                confidence = None
                inference_reason = agg_result.inference_reason
                confidence_calibrated = False
                evidence_schemas = []
                timeline_dicts = []
                adjudication_notes = None
            elif enable_investigation_agent:
                agg_result, evidence_schemas, timeline_dicts, adjudication_info = investigation_agent.investigate_claim(
                    claim_id=claim_item.claim_id,
                    normalized_claim=claim_item.normalized_claim,
                    evidence_source=evidence_source,
                    filter_doc_ids=norm_doc_ids,
                    enable_multi_model=enable_multi_model
                )
                verdict = agg_result.verdict
                confidence = agg_result.confidence
                inference_reason = agg_result.inference_reason
                confidence_calibrated = agg_result.confidence_calibrated
                adjudication_notes = adjudication_info.get("adjudication_rationale")
                for s in timeline_dicts:
                    s["claim_id"] = claim_item.claim_id
                    s["claim_text"] = claim_item.normalized_claim
                all_investigation_timeline.extend(timeline_dicts)
            else:
                retrieved_candidates, empty_reason = retrieve_multi_source(
                    query=claim_item.normalized_claim,
                    source=evidence_source,
                    top_k=top_k,
                    filter_doc_ids=norm_doc_ids
                )
                evidence_schemas = []
                if retrieved_candidates:
                    pairs = [(c["passage_text"], claim_item.normalized_claim) for c in retrieved_candidates]
                    nli_outputs = nli_verifier.predict_batch(pairs)
                    for cand, nli_res in zip(retrieved_candidates, nli_outputs):
                        evidence_schemas.append(EvidenceCandidateSchema(
                            chunk_id=cand.get("chunk_id"),
                            document_name=cand.get("document_name", "Unknown"),
                            page_number=cand.get("page_number"),
                            passage_text=cand.get("passage_text", ""),
                            similarity_score=cand.get("similarity_score", 0.0),
                            nli_label=nli_res["nli_label"],
                            entailment_prob=nli_res["entailment_prob"],
                            contradiction_prob=nli_res["contradiction_prob"],
                            neutral_prob=nli_res["neutral_prob"],
                            source_type=cand.get("source_type", "document")
                        ))
                agg_result = evidence_aggregator.aggregate_evidence(
                    evidence_list=evidence_schemas,
                    verifiable=claim_item.verifiable,
                    empty_reason=empty_reason
                )
                verdict = agg_result.verdict
                confidence = agg_result.confidence
                inference_reason = agg_result.inference_reason
                confidence_calibrated = agg_result.confidence_calibrated
                timeline_dicts = []
                adjudication_notes = None

            # Explainability Rationale
            explanation = explanation_engine.generate_explanation(
                claim_text=claim_item.normalized_claim,
                verdict=verdict,
                confidence=confidence,
                evidence_list=evidence_schemas,
                verifiable=claim_item.verifiable,
                inference_reason=inference_reason
            )

            verified_claims.append(ClaimVerificationResultSchema(
                claim_id=claim_item.claim_id,
                original_text=claim_item.original_text,
                normalized_claim=claim_item.normalized_claim,
                start_offset=claim_item.start_offset,
                end_offset=claim_item.end_offset,
                claim_type=claim_item.claim_type,
                verifiable=claim_item.verifiable,
                verdict=verdict,
                confidence=confidence,
                confidence_calibrated=confidence_calibrated,
                inference_reason=inference_reason,
                evidence_source_used=evidence_source,
                explanation=explanation,
                evidence_list=evidence_schemas,
                investigation_trace=timeline_dicts,
                adjudication_notes=adjudication_notes
            ))

        retrieval_nli_time = (time.perf_counter() - retrieval_nli_start) * 1000
        logger.info(f"Evidence retrieval and NLI verification completed in {retrieval_nli_time:.1f}ms across {len(raw_claims)} claims.")

        # 4. Hallucination Risk Scoring
        metrics = hallucination_scorer.calculate_scores(verified_claims)
        total_latency = (time.perf_counter() - start_time) * 1000

        # 5. Hallucination Propagation & Dependency Graph
        dependency_graph = dependency_graph_builder.build_graph(verified_claims)

        # 6. Database Persistence
        db_run = VerificationRun(
            question=question,
            original_answer=answer,
            model_used=actual_model,
            evidence_source=evidence_source,
            total_claims=metrics["total_claims"],
            verifiable_claims=metrics["verifiable_claims"],
            supported_claims=metrics["supported_claims"],
            contradicted_claims=metrics["contradicted_claims"],
            insufficient_claims=metrics["insufficient_claims"],
            conflicting_claims=metrics["conflicting_claims"],
            hallucination_score=metrics["hallucination_score"],
            unsupported_claim_rate=metrics["unsupported_claim_rate"],
            contradiction_rate=metrics["contradiction_rate"],
            verification_coverage=metrics["verification_coverage"],
            evidence_availability=metrics["evidence_availability"],
            risk_level=metrics.get("risk_level", "LOW_RISK"),
            uncertainty_score=metrics.get("uncertainty_score", 0.0),
            abstention_recommended=metrics.get("abstention_recommended", False),
            abstention_reason=metrics.get("abstention_reason"),
            dependency_graph_json=json.dumps(dependency_graph, ensure_ascii=False),
            investigation_timeline_json=json.dumps(all_investigation_timeline, ensure_ascii=False),
            latency_ms=round(total_latency, 2)
        )
        db.add(db_run)
        db.flush()

        for c in verified_claims:
            db_claim = ExtractedClaim(
                verification_id=db_run.id,
                claim_id=c.claim_id,
                original_text=c.original_text,
                normalized_claim=c.normalized_claim,
                start_offset=c.start_offset,
                end_offset=c.end_offset,
                claim_type=c.claim_type,
                verifiable=c.verifiable,
                verdict=c.verdict,
                confidence=c.confidence,
                inference_reason=c.inference_reason,
                explanation=c.explanation,
                investigation_trace_json=json.dumps(c.investigation_trace or [], ensure_ascii=False),
                adjudication_notes=c.adjudication_notes
            )
            db.add(db_claim)
            db.flush()

            for ev in c.evidence_list:
                db_ev = ClaimEvidence(
                    claim_id=db_claim.id,
                    chunk_id=ev.chunk_id,
                    document_name=ev.document_name,
                    page_number=ev.page_number,
                    passage_text=ev.passage_text,
                    similarity_score=ev.similarity_score,
                    nli_label=ev.nli_label,
                    entailment_prob=ev.entailment_prob,
                    contradiction_prob=ev.contradiction_prob,
                    neutral_prob=ev.neutral_prob,
                    source_type=ev.source_type or "document"
                )
                db.add(db_ev)

        db.commit()
        db.refresh(db_run)

        return VerificationReportResponse(
            id=db_run.id,
            question=db_run.question,
            original_answer=db_run.original_answer,
            corrected_answer=db_run.corrected_answer,
            model_used=db_run.model_used,
            evidence_source=db_run.evidence_source,
            total_claims=db_run.total_claims,
            verifiable_claims=db_run.verifiable_claims,
            supported_claims=db_run.supported_claims,
            contradicted_claims=db_run.contradicted_claims,
            insufficient_claims=db_run.insufficient_claims,
            conflicting_claims=db_run.conflicting_claims,
            hallucination_score=db_run.hallucination_score,
            unsupported_claim_rate=db_run.unsupported_claim_rate,
            contradiction_rate=db_run.contradiction_rate,
            verification_coverage=db_run.verification_coverage,
            evidence_availability=db_run.evidence_availability,
            risk_level=db_run.risk_level or "LOW_RISK",
            uncertainty_score=db_run.uncertainty_score or 0.0,
            abstention_recommended=db_run.abstention_recommended or False,
            abstention_reason=db_run.abstention_reason,
            latency_ms=db_run.latency_ms,
            created_at=db_run.created_at,
            claims=verified_claims,
            dependency_graph=dependency_graph,
            investigation_timeline=all_investigation_timeline
        )


verification_service = VerificationService()

