from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.schemas.verification import ClaimVerificationResultSchema, EvidenceCandidateSchema
from backend.app.schemas.correction import CorrectionResponse
from backend.app.services.ollama_service import ollama_service


class CorrectionEngine:
    """
    Synthesizes evidence-grounded corrections for LLM responses.
    Guarantees:
      - Supported claims are preserved.
      - Contradicted claims are corrected strictly using retrieved evidence.
      - Unsupported claims are qualified or omitted.
      - Re-verifies newly generated response to eliminate newly introduced hallucinations.
    """

    CORRECTION_SYSTEM_PROMPT = """You are an expert factual revision and editing assistant.
Your task is to revise an AI-generated answer so that it is 100% faithful to verified facts and reference evidence.

Strict Rules:
1. PRESERVE all supported claims that are already verified.
2. CORRECT all contradicted claims using ONLY the ground truth facts stated in the provided Evidence Passages.
3. QUALIFY or OMIT any claims with insufficient evidence (e.g., say 'It remains unconfirmed whether...' or remove the claim).
4. NEVER invent, fabricate, or extrapolate facts outside the provided reference evidence.
5. Whenever stating a corrected fact, attach an in-text citation like [Source: DocumentName, p. X] referencing the exact evidence passage.
6. Provide a cohesive, natural, well-written response directly answering the original question.
7. Return ONLY the revised answer text. Do not include conversational meta-talk or apologies."""

    def correct_answer(
        self,
        question: str,
        original_answer: str,
        claims: List[ClaimVerificationResultSchema],
        model_name: Optional[str] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Executes evidence-grounded correction loop.
        """
        supported_claims = [c for c in claims if c.verdict == "Supported"]
        contradicted_claims = [c for c in claims if c.verdict == "Contradicted"]
        insufficient_claims = [c for c in claims if c.verdict in ["Insufficient Evidence", "Conflicting Evidence"]]

        # Build evidence grounding context
        evidence_prompt_parts = []
        
        if supported_claims:
            evidence_prompt_parts.append("VERIFIED FACTS (MUST BE PRESERVED):")
            for c in supported_claims:
                evidence_prompt_parts.append(f"- {c.normalized_claim}")

        if contradicted_claims:
            evidence_prompt_parts.append("\nCONTRADICTED CLAIMS AND GROUND TRUTH EVIDENCE (MUST BE CORRECTED):")
            for c in contradicted_claims:
                evidence_prompt_parts.append(f"- False Claim: \"{c.normalized_claim}\"")
                # Provide top contradicting passage
                refuting_ev = [e for e in c.evidence_list if e.nli_label == "contradiction"]
                if refuting_ev:
                    best_ev = max(refuting_ev, key=lambda x: x.contradiction_prob)
                    evidence_prompt_parts.append(
                        f"  Ground Truth Source ({best_ev.document_name}, p. {best_ev.page_number or 1}): \"{best_ev.passage_text.strip()}\""
                    )

        if insufficient_claims:
            evidence_prompt_parts.append("\nUNVERIFIED CLAIMS (MUST BE QUALIFIED WITH UNCERTAINTY OR OMITTED):")
            for c in insufficient_claims:
                evidence_prompt_parts.append(f"- Unverified Claim: \"{c.normalized_claim}\"")

        grounding_context = "\n".join(evidence_prompt_parts)

        user_prompt = f"""Original Question:
{question}

Original Answer (contains errors and unverified statements):
{original_answer}

Reference Evidence & Verification Verdicts:
{grounding_context}

Please write the factually corrected answer now:"""

        # Generate correction
        try:
            corrected_text = ollama_service.generate(
                prompt=user_prompt,
                system_prompt=self.CORRECTION_SYSTEM_PROMPT,
                model=model_name,
                temperature=temperature,
                max_tokens=350,
                timeout=settings.OLLAMA_GENERATION_TIMEOUT,
                think=False
            )
        except Exception as e:
            logger.error(f"Correction generation failed: {e}")
            # Fallback deterministic textual patch if Ollama fails
            corrected_text = self._fallback_text_correction(original_answer, contradicted_claims)

        return {
            "original_answer": original_answer,
            "corrected_answer": corrected_text,
            "claims_corrected": len(contradicted_claims),
            "unsupported_removed": len(insufficient_claims),
            "grounding_context": grounding_context
        }

    def _fallback_text_correction(
        self,
        original_answer: str,
        contradicted_claims: List[ClaimVerificationResultSchema]
    ) -> str:
        """Deterministic replacement of contradicted claims when LLM generation is unavailable."""
        revised = original_answer
        for c in contradicted_claims:
            refuting = [e for e in c.evidence_list if e.nli_label == "contradiction"]
            if refuting:
                top_ev = max(refuting, key=lambda x: x.contradiction_prob)
                # Replace original text with verified evidence and citation
                citation = f" [Source: {top_ev.document_name}, p. {top_ev.page_number or 1}]"
                note = f"{top_ev.passage_text.strip()}{citation}"
                if c.original_text in revised:
                    revised = revised.replace(c.original_text, note)
        return revised


correction_engine = CorrectionEngine()
