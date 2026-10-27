from typing import List, Dict, Any, Tuple, Optional
from backend.app.core.config import settings
from backend.app.schemas.verification import EvidenceCandidateSchema


def are_passages_distinct(e1: EvidenceCandidateSchema, e2: EvidenceCandidateSchema) -> bool:
    """
    Returns True if e1 and e2 represent genuinely distinct evidence passages,
    and False if they are duplicates, overlapping chunks, or repeated references.
    """
    if e1.chunk_id and e2.chunk_id and e1.chunk_id == e2.chunk_id:
        return False

    t1 = (e1.passage_text or "").strip().lower()
    t2 = (e2.passage_text or "").strip().lower()
    if not t1 or not t2:
        return False
    if t1 == t2:
        return False

    # Jaccard similarity on word tokens
    words1 = set(t1.split())
    words2 = set(t2.split())
    if not words1 or not words2:
        return False

    intersection = len(words1 & words2)
    union = len(words1 | words2)
    jaccard = intersection / union if union > 0 else 0.0

    if jaccard >= 0.70:
        return False

    # Check substring containment if one is largely contained in the other
    min_len = min(len(t1), len(t2))
    max_len = max(len(t1), len(t2))
    if min_len > 0 and (t1 in t2 or t2 in t1) and (min_len / max_len > 0.70):
        return False

    return True


class AggregationResult(tuple):
    """
    Subclass of 3-tuple (verdict, confidence, summary_rationale) for seamless backward compatibility,
    augmented with structured explainability attributes:
      - inference_reason: explicit classification of the inference/evidence condition
      - confidence_calibrated: boolean indicating if confidence represents real model probability
    """
    def __new__(
        cls,
        verdict: str,
        confidence: Optional[float],
        summary_rationale: str,
        inference_reason: str = "EVIDENCE_ENTAILED",
        confidence_calibrated: bool = True
    ):
        instance = super().__new__(cls, (verdict, confidence, summary_rationale))
        instance.verdict = verdict
        instance.confidence = confidence
        instance.summary_rationale = summary_rationale
        instance.inference_reason = inference_reason
        instance.confidence_calibrated = confidence_calibrated
        return instance


class EvidenceAggregator:
    """
    Synthesizes multiple evidence passages and NLI inference results into a principled claim verdict:
      - Supported
      - Contradicted
      - Conflicting Evidence
      - Insufficient Evidence

    Distinguishes 7 distinct operational & evidence conditions:
      1. NO_DOCUMENTS_INDEXED: Evidence vector index is empty.
      2. NO_DOCUMENTS_SELECTED: Document filter yielded no indexed passages.
      3. NO_EVIDENCE_RETRIEVED: Query semantic retrieval returned 0 passages above threshold.
      4. NEUTRAL_NLI_UNCERTAIN: Passages retrieved, but NLI classified as neutral (unsupported).
      5. CONTRADICTORY_EVIDENCE: Passages directly refute the claim.
      6. CONFLICTING_SOURCES: Multiple sources disagree (both entailment and contradiction).
      7. NON_VERIFIABLE_CLAIM: Statement is subjective, value judgment, or non-empirical.
    """

    @classmethod
    def aggregate_evidence(
        cls,
        evidence_list: List[EvidenceCandidateSchema],
        verifiable: bool = True,
        empty_reason: Optional[str] = None
    ) -> AggregationResult:
        """
        Aggregates multiple evidence passages for a claim.
        Returns:
            AggregationResult tuple (verdict, confidence, summary_rationale) with
            .inference_reason and .confidence_calibrated attributes.
        """
        if not verifiable:
            return AggregationResult(
                verdict="Insufficient Evidence",
                confidence=None,
                summary_rationale="Statement is classified as subjective or non-empirical and cannot be verified with factual evidence.",
                inference_reason="NON_VERIFIABLE_CLAIM",
                confidence_calibrated=False
            )

        if not evidence_list:
            reason = empty_reason or "NO_EVIDENCE_RETRIEVED"
            if reason == "NO_DOCUMENTS_INDEXED":
                msg = "No reference documents are indexed in the active knowledge base."
            elif reason == "NO_DOCUMENTS_SELECTED":
                msg = "No reference documents were selected for verification in this request."
            else:
                msg = "No relevant evidence passages met the semantic similarity threshold."

            return AggregationResult(
                verdict="Insufficient Evidence",
                confidence=None,
                summary_rationale=f"Verification could not be completed: {msg}",
                inference_reason=reason,
                confidence_calibrated=False
            )

        # Relevance filtering: retain candidates meeting similarity threshold
        relevant_evidence = [
            e for e in evidence_list
            if e.similarity_score is None or e.similarity_score >= settings.SIMILARITY_THRESHOLD
        ]

        if not relevant_evidence:
            return AggregationResult(
                verdict="Insufficient Evidence",
                confidence=None,
                summary_rationale="Retrieved passages lack sufficient semantic relevance to verify the claim.",
                inference_reason="NO_EVIDENCE_RETRIEVED",
                confidence_calibrated=False
            )

        # Partition into decisive supporting, contradicting, and neutral passages
        supporting = [
            e for e in relevant_evidence
            if e.nli_label == "entailment" and (e.entailment_prob is None or e.entailment_prob >= settings.ENTAILMENT_THRESHOLD)
        ]
        contradicting = [
            e for e in relevant_evidence
            if e.nli_label == "contradiction" and (e.contradiction_prob is None or e.contradiction_prob >= settings.CONTRADICTION_THRESHOLD)
        ]
        neutral = [e for e in relevant_evidence if e.nli_label == "neutral"]

        # Case 1: Both supporting and contradicting candidate passages exist
        if supporting and contradicting:
            best_supp = max(supporting, key=lambda x: x.entailment_prob if x.entailment_prob is not None else 1.0)
            best_contra = max(contradicting, key=lambda x: x.contradiction_prob if x.contradiction_prob is not None else 1.0)

            # Check if there is at least one genuinely distinct pair of supporting and contradicting passages
            has_distinct_pair = any(
                are_passages_distinct(s, c)
                for s in supporting
                for c in contradicting
            )

            if has_distinct_pair:
                diff = (best_supp.entailment_prob or 0.0) - (best_contra.contradiction_prob or 0.0)
                if diff > settings.NEUTRAL_AMBIGUITY_MARGIN:
                    return AggregationResult(
                        verdict="Supported",
                        confidence=round(best_supp.entailment_prob, 4) if best_supp.entailment_prob is not None else None,
                        summary_rationale=f"Supported by evidence in '{best_supp.document_name}' (p. {best_supp.page_number or 1}).",
                        inference_reason="EVIDENCE_ENTAILED",
                        confidence_calibrated=True
                    )
                elif -diff > settings.NEUTRAL_AMBIGUITY_MARGIN:
                    return AggregationResult(
                        verdict="Contradicted",
                        confidence=round(best_contra.contradiction_prob, 4) if best_contra.contradiction_prob is not None else None,
                        summary_rationale=f"Contradicted by evidence in '{best_contra.document_name}' (p. {best_contra.page_number or 1}).",
                        inference_reason="CONTRADICTORY_EVIDENCE",
                        confidence_calibrated=True
                    )
                else:
                    # Genuinely conflicting evidence between distinct passages
                    s_prob = best_supp.entailment_prob if best_supp.entailment_prob is not None else 0.8
                    c_prob = best_contra.contradiction_prob if best_contra.contradiction_prob is not None else 0.8
                    avg_conf = round((s_prob + c_prob) / 2.0, 4)
                    if best_supp.document_name == best_contra.document_name:
                        rat = (
                            f"Conflicting evidence detected within reference document '{best_supp.document_name}': "
                            f"passage on page {best_supp.page_number or 1} supports the claim, "
                            f"whereas passage on page {best_contra.page_number or 1} contradicts it."
                        )
                    else:
                        rat = (
                            f"Conflicting evidence detected across reference documents: "
                            f"'{best_supp.document_name}' supports the claim, "
                            f"whereas '{best_contra.document_name}' contradicts it."
                        )
                    return AggregationResult(
                        verdict="Conflicting Evidence",
                        confidence=avg_conf,
                        summary_rationale=rat,
                        inference_reason="CONFLICTING_SOURCES",
                        confidence_calibrated=True
                    )
            else:
                # Supporting and contradicting passages are near-duplicates / same passage
                # Resolve to whichever has higher probability
                if (best_supp.entailment_prob or 0.0) >= (best_contra.contradiction_prob or 0.0):
                    return AggregationResult(
                        verdict="Supported",
                        confidence=round(best_supp.entailment_prob, 4) if best_supp.entailment_prob is not None else None,
                        summary_rationale=f"Supported by evidence in '{best_supp.document_name}' (p. {best_supp.page_number or 1}).",
                        inference_reason="EVIDENCE_ENTAILED",
                        confidence_calibrated=True
                    )
                else:
                    return AggregationResult(
                        verdict="Contradicted",
                        confidence=round(best_contra.contradiction_prob, 4) if best_contra.contradiction_prob is not None else None,
                        summary_rationale=f"Contradicted by evidence in '{best_contra.document_name}' (p. {best_contra.page_number or 1}).",
                        inference_reason="CONTRADICTORY_EVIDENCE",
                        confidence_calibrated=True
                    )

        # Case 2: Decisive contradiction only
        if contradicting:
            best_contra = max(contradicting, key=lambda x: x.contradiction_prob if x.contradiction_prob is not None else 1.0)
            return AggregationResult(
                verdict="Contradicted",
                confidence=round(best_contra.contradiction_prob, 4) if best_contra.contradiction_prob is not None else None,
                summary_rationale=f"Contradicted by evidence in '{best_contra.document_name}' (p. {best_contra.page_number or 1}).",
                inference_reason="CONTRADICTORY_EVIDENCE",
                confidence_calibrated=True
            )

        # Case 3: Decisive entailment only
        if supporting:
            best_supp = max(supporting, key=lambda x: x.entailment_prob if x.entailment_prob is not None else 1.0)
            return AggregationResult(
                verdict="Supported",
                confidence=round(best_supp.entailment_prob, 4) if best_supp.entailment_prob is not None else None,
                summary_rationale=f"Supported by evidence in '{best_supp.document_name}' (p. {best_supp.page_number or 1}).",
                inference_reason="EVIDENCE_ENTAILED",
                confidence_calibrated=True
            )

        # Case 4: Insufficient evidence (NLI is neutral or below decisive thresholds)
        best_neutral = max(neutral, key=lambda x: x.neutral_prob if x.neutral_prob is not None else 0.0) if neutral else None
        if best_neutral and best_neutral.neutral_prob is not None:
            neutral_conf = round(best_neutral.neutral_prob, 4)
        else:
            all_max = max((max((e.entailment_prob or 0.0), (e.contradiction_prob or 0.0)) for e in relevant_evidence), default=0.0)
            neutral_conf = round(max(0.0, 1.0 - all_max), 4)

        return AggregationResult(
            verdict="Insufficient Evidence",
            confidence=neutral_conf,
            summary_rationale="Retrieved passages contain related keywords but lack sufficient evidence to either entail or refute the claim.",
            inference_reason="NEUTRAL_NLI_UNCERTAIN",
            confidence_calibrated=True
        )


evidence_aggregator = EvidenceAggregator()
