import re
import time
from typing import List, Dict, Any, Optional, Tuple, Set

from backend.app.core.logging import logger
from backend.app.core.config import settings
from backend.app.nlp.retriever import retrieve_multi_source
from backend.app.nlp.nli_verifier import nli_verifier
from backend.app.nlp.evidence_aggregator import evidence_aggregator, AggregationResult
from backend.app.services.ollama_service import ollama_service
from backend.app.schemas.verification import EvidenceCandidateSchema


class InvestigationStep:
    """Represents a discrete, auditable step in the autonomous investigation timeline."""
    def __init__(
        self,
        step_idx: int,
        action: str,
        query: str,
        candidates_found: int,
        max_similarity: float,
        observation: str,
        stop_decision: Optional[str] = None
    ):
        self.step_idx = step_idx
        self.action = action
        self.query = query
        self.candidates_found = candidates_found
        self.max_similarity = max_similarity
        self.observation = observation
        self.stop_decision = stop_decision

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_idx": self.step_idx,
            "action": self.action,
            "query": self.query,
            "candidates_found": self.candidates_found,
            "max_similarity": round(self.max_similarity, 4),
            "observation": self.observation,
            "stop_decision": self.stop_decision
        }


class AutonomousInvestigationAgent:
    """
    Bounded, explainable autonomous investigation agent for claims with ambiguous,
    conflicting, or insufficient initial evidence.

    Capabilities:
      1. Inspects initial retrieval results.
      2. Identifies missing evidence and ambiguous terms.
      3. Reformulates search queries (entity extraction, conversational stripping, LLM keyword distillation).
      4. Executes targeted secondary search over the available knowledge corpus.
      5. Deduplicates passages while preserving provenance metadata.
      6. Compares supporting and contradictory passages.
      7. Performs multi-model adjudication when NLI and LLM reach conflicting verdicts.
      8. Strictly bounds iterations (max 2 reformulations), execution time, and model calls.
    """

    MAX_REFORMULATION_BUDGET = 2
    MAX_CANDIDATES_PER_STEP = 5

    @classmethod
    def reformulate_query(cls, claim_text: str, step_num: int) -> str:
        """
        Synthesizes a targeted search reformulation to recover from vocabulary mismatch.
        Employs deterministic entity/noun-phrase distillation with LLM assistance when available.
        """
        # Strategy A: Strip conversational qualifiers and epistemic preambles
        cleaned = re.sub(
            r"^(it is\s+(?:widely\s+|commonly\s+|often\s+)?(?:known|said|reported|believed|accepted|claimed|argued)\s+that\s*|"
            r"according to (?:sources|research|studies|reports),?\s*|"
            r"in fact,\s*|studies show that\s*|scientists believe that\s*|"
            r"as of \d{4},?\s*)",
            "",
            claim_text,
            flags=re.IGNORECASE
        ).strip()

        # Strategy B: If step 2, extract core noun chunks and entity keywords
        if step_num >= 2:
            # Try Ollama fast query distillation if online
            try:
                is_online, _ = ollama_service.check_health()
                if is_online:
                    prompt = (
                        f"Extract 3 to 6 essential keyword search terms to verify this claim in an encyclopedia: "
                        f"\"{cleaned}\". Respond with ONLY the space-separated keywords."
                    )
                    llm_kw = ollama_service.generate(
                        prompt=prompt,
                        temperature=0.0,
                        max_tokens=32,
                        timeout=settings.OLLAMA_FAST_TIMEOUT,
                        think=False
                    ).strip()
                    # Keep if valid concise keywords
                    clean_kw = re.sub(r'["\n\r]', '', llm_kw).strip()
                    if clean_kw and len(clean_kw.split()) <= 8:
                        return clean_kw
            except Exception as e:
                logger.debug(f"LLM query reformulation fallback: {e}")

            # Deterministic linguistic fallback: extract capitalized words, numbers, and long tokens
            tokens = re.findall(r"\b[A-Z0-9][a-zA-Z0-9_-]+\b|\b[a-zA-Z]{5,}\b", cleaned)
            if tokens:
                return " ".join(tokens[:6])

        return cleaned

    @classmethod
    def investigate_claim(
        cls,
        claim_id: str,
        normalized_claim: str,
        evidence_source: str = "documents",
        filter_doc_ids: Optional[List[str]] = None,
        enable_multi_model: bool = False
    ) -> Tuple[AggregationResult, List[EvidenceCandidateSchema], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes bounded, auditable investigation for a single claim.
        
        Returns:
            - agg_result: AggregationResult (verdict, confidence, rationale, inference_reason)
            - final_evidence: deduplicated list of EvidenceCandidateSchema
            - timeline_steps: list of dicts documenting each investigation step
            - adjudication_info: multi-model comparison and dispute resolution metadata
        """
        timeline: List[InvestigationStep] = []
        collected_chunks: Dict[str, Dict[str, Any]] = {}
        seen_queries: Set[str] = set()

        norm_filter_doc_ids = [d for d in filter_doc_ids if d] if filter_doc_ids else None
        current_query = normalized_claim
        step_idx = 1
        stop_reason = "SEARCH_BUDGET_EXHAUSTED"

        # --- PHASE 1: Bounded Iterative Investigation Loop ---
        while step_idx <= cls.MAX_REFORMULATION_BUDGET + 1:
            query_key = current_query.strip().lower()
            if query_key in seen_queries:
                break
            seen_queries.add(query_key)

            action_name = "initial_retrieval" if step_idx == 1 else f"reformulated_retrieval_step_{step_idx - 1}"
            
            # Execute retrieval
            raw_cands, empty_reason = retrieve_multi_source(
                query=current_query,
                source=evidence_source,
                top_k=cls.MAX_CANDIDATES_PER_STEP,
                filter_doc_ids=norm_filter_doc_ids
            )

            max_sim = max((c.get("similarity_score", 0.0) for c in raw_cands), default=0.0)
            
            # Record candidates (deduplicated by chunk_id or text snippet)
            newly_added = 0
            for c in raw_cands:
                chunk_key = c.get("chunk_id") or hash(c.get("passage_text", "")[:80])
                if chunk_key not in collected_chunks:
                    collected_chunks[chunk_key] = c
                    newly_added += 1

            # Early sufficiency check: evaluate NLI on current highest candidate
            sufficient = False
            best_nli_label = None
            if raw_cands:
                test_pair = [(raw_cands[0]["passage_text"], normalized_claim)]
                test_out = nli_verifier.predict_batch(test_pair)[0]
                best_nli_label = test_out["nli_label"]
                # Sufficient if strong entailment or direct contradiction above threshold
                if test_out["entailment_prob"] >= 0.70 or test_out["contradiction_prob"] >= 0.70:
                    sufficient = True

            if empty_reason == "NO_DOCUMENTS_INDEXED":
                timeline.append(InvestigationStep(
                    step_idx=step_idx,
                    action=action_name,
                    query=current_query,
                    candidates_found=0,
                    max_similarity=0.0,
                    observation="Corpus contains 0 indexed documents. Cannot proceed.",
                    stop_decision="CORPUS_EMPTY"
                ))
                stop_reason = "CORPUS_EMPTY"
                break
            elif empty_reason == "NO_DOCUMENTS_SELECTED":
                timeline.append(InvestigationStep(
                    step_idx=step_idx,
                    action=action_name,
                    query=current_query,
                    candidates_found=0,
                    max_similarity=0.0,
                    observation="Document filter does not match any indexed documents in library.",
                    stop_decision="NO_DOCUMENTS_SELECTED"
                ))
                stop_reason = "NO_DOCUMENTS_SELECTED"
                break

            if sufficient:
                timeline.append(InvestigationStep(
                    step_idx=step_idx,
                    action=action_name,
                    query=current_query,
                    candidates_found=len(raw_cands),
                    max_similarity=max_sim,
                    observation=f"Found conclusive evidence ({best_nli_label.upper()} with prob >= 0.70).",
                    stop_decision="SUFFICIENT_EVIDENCE_FOUND"
                ))
                stop_reason = "SUFFICIENT_EVIDENCE_FOUND"
                break

            # If not sufficient and budget remains, reformulate
            if step_idx <= cls.MAX_REFORMULATION_BUDGET:
                next_query = cls.reformulate_query(normalized_claim, step_num=step_idx)
                timeline.append(InvestigationStep(
                    step_idx=step_idx,
                    action=action_name,
                    query=current_query,
                    candidates_found=len(raw_cands),
                    max_similarity=max_sim,
                    observation=f"Evidence ambiguous or low similarity ({max_sim:.2f}). Reformulating search.",
                    stop_decision=f"REFORMULATE_QUERY -> '{next_query[:40]}...'"
                ))
                current_query = next_query
                step_idx += 1
            else:
                timeline.append(InvestigationStep(
                    step_idx=step_idx,
                    action=action_name,
                    query=current_query,
                    candidates_found=len(raw_cands),
                    max_similarity=max_sim,
                    observation="Maximum search reformulation budget reached.",
                    stop_decision="BUDGET_EXHAUSTED"
                ))
                stop_reason = "SEARCH_BUDGET_EXHAUSTED"
                break

        # --- PHASE 2: Aggregated NLI Verification ---
        all_candidates = list(collected_chunks.values())
        evidence_schemas: List[EvidenceCandidateSchema] = []

        if all_candidates:
            # Sort by similarity
            all_candidates.sort(key=lambda x: x.get("similarity_score", 0.0), reverse=True)
            top_passages = all_candidates[:settings.RETRIEVAL_TOP_K]

            pairs = [(c["passage_text"], normalized_claim) for c in top_passages]
            nli_outputs = nli_verifier.predict_batch(pairs)

            for cand, nli_res in zip(top_passages, nli_outputs):
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

        # --- PHASE 3: Multi-Model Adjudication (if enabled) ---
        adjudication_info: Dict[str, Any] = {
            "multi_model_enabled": enable_multi_model,
            "nli_verdict": None,
            "llm_verdict": None,
            "disagreement_detected": False,
            "adjudication_rationale": None
        }

        # Baseline aggregation from NLI
        agg_empty_reason = (
            "NO_DOCUMENTS_INDEXED" if stop_reason == "CORPUS_EMPTY"
            else "NO_DOCUMENTS_SELECTED" if stop_reason == "NO_DOCUMENTS_SELECTED"
            else "NO_EVIDENCE_RETRIEVED"
        )
        agg_result = evidence_aggregator.aggregate_evidence(
            evidence_list=evidence_schemas,
            verifiable=True,
            empty_reason=agg_empty_reason
        )
        adjudication_info["nli_verdict"] = agg_result.verdict

        if enable_multi_model and evidence_schemas:
            try:
                is_online, _ = ollama_service.check_health()
                if is_online:
                    top_evidence_text = evidence_schemas[0].passage_text
                    llm_eval = ollama_service.verify_nli(
                        premise=top_evidence_text,
                        hypothesis=normalized_claim,
                        model=settings.DEFAULT_LLM_MODEL
                    )
                    llm_label = llm_eval.get("nli_label", "neutral")
                    llm_verdict = (
                        "Supported" if llm_label == "entailment"
                        else "Contradicted" if llm_label == "contradiction"
                        else "Insufficient Evidence"
                    )
                    adjudication_info["llm_verdict"] = llm_verdict

                    # Disagreement resolution
                    if llm_verdict != agg_result.verdict:
                        adjudication_info["disagreement_detected"] = True
                        
                        # Targeted evidence check: check softmax margin
                        best_nli_cand = evidence_schemas[0]
                        nli_margin = abs(best_nli_cand.entailment_prob - best_nli_cand.contradiction_prob)
                        
                        if nli_margin > 0.40:
                            # NLI is mathematically decisive from fine-tuned cross-encoder
                            adjudication_info["adjudication_rationale"] = (
                                f"DeBERTa cross-encoder demonstrated high probability margin ({nli_margin:.2f}) "
                                f"confirming '{agg_result.verdict}' over LLM opinion."
                            )
                        elif llm_label == "neutral":
                            # LLM was cautious; resolve to Insufficient Evidence
                            agg_result = AggregationResult(
                                verdict="Insufficient Evidence",
                                confidence=None,
                                summary_rationale="Cross-model adjudication found insufficient conclusive evidence between DeBERTa and Local LLM.",
                                inference_reason="CROSS_MODEL_DISAGREEMENT",
                                confidence_calibrated=False
                            )
                            adjudication_info["adjudication_rationale"] = "Resolved to Insufficient Evidence due to model disagreement without decisive evidence."
                        else:
                            adjudication_info["adjudication_rationale"] = (
                                f"Models diverged (NLI: {agg_result.verdict}, LLM: {llm_verdict}). Retained evidence-grounded NLI verdict."
                            )
            except Exception as e:
                logger.warning(f"Multi-model adjudication skipped: {e}")

        timeline_dicts = [step.to_dict() for step in timeline]
        return agg_result, evidence_schemas, timeline_dicts, adjudication_info


investigation_agent = AutonomousInvestigationAgent()
