from typing import List, Dict, Any
from backend.app.schemas.verification import ClaimVerificationResultSchema


class HallucinationScorer:
    """
    Computes rigorous, mathematically grounded verification and hallucination statistics.
    All metrics are computed directly from observed claim-level verdicts without heuristics or simulated values.
    """

    @classmethod
    def calculate_scores(cls, claims: List[ClaimVerificationResultSchema]) -> Dict[str, Any]:
        """
        Calculates verification metrics and documented composite hallucination risk score.
        
        Formula Documentation:
        ----------------------
        - contradiction_rate = contradicted / max(1, verifiable)
        - unsupported_claim_rate = (contradicted + insufficient + conflicting) / max(1, total)
        - verification_coverage = verifiable / max(1, total)
        - evidence_availability = (supported + contradicted + conflicting) / max(1, verifiable)
        - hallucination_risk_score = 0.70 * contradiction_rate + 0.30 * (insufficient + conflicting) / max(1, verifiable)
          (Heuristic composite bounded between [0.0, 1.0], weighted toward demonstrably false claims).
        """
        total = len(claims)
        if total == 0:
            return {
                "total_claims": 0,
                "verifiable_claims": 0,
                "supported_claims": 0,
                "contradicted_claims": 0,
                "insufficient_claims": 0,
                "conflicting_claims": 0,
                "contradiction_rate": 0.0,
                "unsupported_claim_rate": 0.0,
                "verification_coverage": 0.0,
                "evidence_availability": 0.0,
                "hallucination_score": 0.0
            }

        verifiable = sum(1 for c in claims if c.verifiable)
        supported = sum(1 for c in claims if c.verdict == "Supported")
        contradicted = sum(1 for c in claims if c.verdict == "Contradicted")
        insufficient = sum(1 for c in claims if c.verdict == "Insufficient Evidence")
        conflicting = sum(1 for c in claims if c.verdict == "Conflicting Evidence")

        denom_v = max(1, verifiable)
        denom_t = max(1, total)

        contradiction_rate = round(contradicted / denom_v, 4)
        unsupported_rate = round((contradicted + insufficient + conflicting) / denom_t, 4)
        coverage = round(verifiable / denom_t, 4)
        availability = round((supported + contradicted + conflicting) / denom_v, 4)

        # Composite risk score: direct contradictions penalized with weight 0.70, unverified claims with weight 0.30
        risk_score = round(
            min(1.0, 0.70 * contradiction_rate + 0.30 * ((insufficient + conflicting) / denom_v)),
            4
        )

        # Epistemic uncertainty calculation
        if verifiable > 0 and availability == 0.0:
            uncertainty_score = 1.0
            abstention_recommended = True
            abstention_reason = "No reference evidence passages available in active corpus to evaluate claims."
            risk_level = "ABSTAIN"
        elif coverage == 0.0:
            uncertainty_score = 1.0
            abstention_recommended = True
            abstention_reason = "Answer contains exclusively subjective or non-verifiable claims."
            risk_level = "ABSTAIN"
        else:
            unsupported_v = (insufficient + conflicting) / denom_v
            uncertainty_score = round(min(1.0, 0.60 * unsupported_v + 0.40 * (1.0 - coverage)), 4)
            abstention_recommended = False
            abstention_reason = None

            if contradiction_rate >= 0.50 or risk_score >= 0.70:
                risk_level = "CRITICAL_RISK"
            elif contradiction_rate > 0.0 or risk_score >= 0.40:
                risk_level = "HIGH_RISK"
            elif risk_score >= 0.15 or unsupported_v >= 0.25:
                risk_level = "MODERATE_RISK"
            else:
                risk_level = "LOW_RISK"

        return {
            "total_claims": total,
            "verifiable_claims": verifiable,
            "supported_claims": supported,
            "contradicted_claims": contradicted,
            "insufficient_claims": insufficient,
            "conflicting_claims": conflicting,
            "contradiction_rate": contradiction_rate,
            "unsupported_claim_rate": unsupported_rate,
            "verification_coverage": coverage,
            "evidence_availability": availability,
            "hallucination_score": risk_score,
            "risk_level": risk_level,
            "uncertainty_score": uncertainty_score,
            "abstention_recommended": abstention_recommended,
            "abstention_reason": abstention_reason
        }


hallucination_scorer = HallucinationScorer()
