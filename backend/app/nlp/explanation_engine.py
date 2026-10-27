from typing import List, Optional
from backend.app.schemas.verification import EvidenceCandidateSchema


class ExplanationEngine:
    """
    Generates explainable, grounded textual rationales detailing why a claim was
    classified as Supported, Contradicted, Conflicting, or Insufficient Evidence.
    """

    @classmethod
    def generate_explanation(
        cls,
        claim_text: str,
        verdict: str,
        confidence: Optional[float],
        evidence_list: List[EvidenceCandidateSchema],
        verifiable: bool = True,
        inference_reason: Optional[str] = None
    ) -> str:
        """Constructs an evidence-backed rationale for the claim verdict."""
        if not verifiable or inference_reason == "NON_VERIFIABLE_CLAIM":
            return (
                f"The statement '{claim_text}' is subjective or non-empirical in nature. "
                "Subjective opinions, value judgments, or stylistic commentary cannot be verified against objective factual evidence."
            )

        if not evidence_list:
            if inference_reason == "NO_DOCUMENTS_INDEXED":
                return (
                    f"No reference documents are indexed in the active knowledge base for '{claim_text}'. "
                    "Verification could not be performed until reference texts or benchmark datasets are indexed."
                )
            elif inference_reason == "NO_DOCUMENTS_SELECTED":
                return (
                    f"No active reference documents were selected to verify '{claim_text}'. "
                    "Please select one or more documents or switch the evidence source to the FEVER knowledge base."
                )
            else:
                return (
                    f"No relevant reference passages were retrieved for the claim '{claim_text}'. "
                    "Verification could not be completed because no passages met the semantic similarity threshold."
                )

        if verdict == "Supported":
            best_ev = max(
                (e for e in evidence_list if e.nli_label == "entailment"),
                key=lambda x: x.entailment_prob if x.entailment_prob is not None else 1.0,
                default=evidence_list[0]
            )
            conf_str = f"{(best_ev.entailment_prob * 100):.1f}%" if best_ev.entailment_prob is not None else "High"
            page_info = f", page {best_ev.page_number}" if best_ev.page_number else ""
            source_tag = f" [{best_ev.source_type.upper()}]" if getattr(best_ev, "source_type", None) else ""
            clean_snippet = best_ev.passage_text.strip().replace("\r\n", " ").replace("\n", " ")[:200]
            return (
                f"Claim is Supported (confidence: {conf_str}). "
                f"Verified against reference document '{best_ev.document_name}'{source_tag}{page_info}. "
                f"Retrieved evidence affirms: \"{clean_snippet}...\""
            )

        elif verdict == "Contradicted":
            best_ev = max(
                (e for e in evidence_list if e.nli_label == "contradiction"),
                key=lambda x: x.contradiction_prob if x.contradiction_prob is not None else 1.0,
                default=evidence_list[0]
            )
            conf_str = f"{(best_ev.contradiction_prob * 100):.1f}%" if best_ev.contradiction_prob is not None else "High"
            page_info = f", page {best_ev.page_number}" if best_ev.page_number else ""
            source_tag = f" [{best_ev.source_type.upper()}]" if getattr(best_ev, "source_type", None) else ""
            clean_snippet = best_ev.passage_text.strip().replace("\r\n", " ").replace("\n", " ")[:200]
            return (
                f"Claim is Contradicted (confidence: {conf_str}). "
                f"Directly refuted by document '{best_ev.document_name}'{source_tag}{page_info}. "
                f"Ground truth source states: \"{clean_snippet}...\""
            )

        elif verdict == "Conflicting Evidence":
            supp = [e for e in evidence_list if e.nli_label == "entailment" or (e.entailment_prob and e.entailment_prob >= 0.5)]
            contra = [e for e in evidence_list if e.nli_label == "contradiction" or (e.contradiction_prob and e.contradiction_prob >= 0.5)]
            best_supp = max(supp, key=lambda x: x.entailment_prob if x.entailment_prob is not None else 1.0) if supp else evidence_list[0]
            best_contra = max(contra, key=lambda x: x.contradiction_prob if x.contradiction_prob is not None else 1.0) if contra else evidence_list[0]

            s_doc = best_supp.document_name or "Unknown source"
            c_doc = best_contra.document_name or "Unknown source"
            s_page = f" on page {best_supp.page_number}" if best_supp.page_number else ""
            c_page = f" on page {best_contra.page_number}" if best_contra.page_number else ""
            s_snippet = best_supp.passage_text.strip().replace("\r\n", " ").replace("\n", " ")[:150]
            c_snippet = best_contra.passage_text.strip().replace("\r\n", " ").replace("\n", " ")[:150]

            if s_doc == c_doc:
                return (
                    f"Conflicting evidence detected within reference document '{s_doc}'. "
                    f"Passage{s_page} provides supporting evidence (\"{s_snippet}...\"), "
                    f"whereas passage{c_page} presents contradictory statements (\"{c_snippet}...\"). "
                    "Manual review of the document's provisions is recommended."
                )
            else:
                s_page_str = f" (page {best_supp.page_number})" if best_supp.page_number else ""
                c_page_str = f" (page {best_contra.page_number})" if best_contra.page_number else ""
                return (
                    f"Conflicting evidence identified across reference documents. "
                    f"'{s_doc}'{s_page_str} provides supporting evidence (\"{s_snippet}...\"), "
                    f"whereas '{c_doc}'{c_page_str} presents contradicting statements (\"{c_snippet}...\"). "
                    "Manual reconciliation of conflicting source materials is recommended."
                )

        else:  # Insufficient Evidence
            top_ev = evidence_list[0]
            neutral_conf_str = f"{(top_ev.neutral_prob * 100):.1f}%" if top_ev.neutral_prob is not None else "uncertain"
            sim_str = f"{top_ev.similarity_score:.2f}" if top_ev.similarity_score is not None else "N/A"
            page_info = f", page {top_ev.page_number}" if top_ev.page_number else ""
            return (
                f"Insufficient evidence to verify '{claim_text}'. "
                f"Top retrieved passage from '{top_ev.document_name}'{page_info} has semantic similarity {sim_str}, "
                f"but NLI classified the relationship as neutral ({neutral_conf_str}). "
                "The source does not explicitly confirm or refute the assertion."
            )


explanation_engine = ExplanationEngine()
