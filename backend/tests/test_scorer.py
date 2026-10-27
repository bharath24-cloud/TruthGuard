import pytest
from backend.app.nlp.hallucination_scorer import hallucination_scorer
from backend.app.schemas.verification import ClaimVerificationResultSchema


def test_scorer_all_supported():
    claims = [
        ClaimVerificationResultSchema(
            claim_id="c1",
            original_text="Fact 1",
            normalized_claim="Fact 1",
            start_offset=0,
            end_offset=6,
            claim_type="factual",
            verifiable=True,
            verdict="Supported",
            confidence=0.9,
            explanation="Verified",
            evidence_list=[]
        ),
        ClaimVerificationResultSchema(
            claim_id="c2",
            original_text="Fact 2",
            normalized_claim="Fact 2",
            start_offset=7,
            end_offset=13,
            claim_type="factual",
            verifiable=True,
            verdict="Supported",
            confidence=0.85,
            explanation="Verified",
            evidence_list=[]
        )
    ]
    scores = hallucination_scorer.calculate_scores(claims)
    assert scores["total_claims"] == 2
    assert scores["supported_claims"] == 2
    assert scores["contradicted_claims"] == 0
    assert scores["contradiction_rate"] == 0.0
    assert scores["hallucination_score"] == 0.0


def test_scorer_with_contradictions():
    claims = [
        ClaimVerificationResultSchema(
            claim_id="c1",
            original_text="True claim",
            normalized_claim="True claim",
            start_offset=0,
            end_offset=10,
            claim_type="factual",
            verifiable=True,
            verdict="Supported",
            confidence=0.9,
            explanation="Verified",
            evidence_list=[]
        ),
        ClaimVerificationResultSchema(
            claim_id="c2",
            original_text="False claim",
            normalized_claim="False claim",
            start_offset=11,
            end_offset=22,
            claim_type="factual",
            verifiable=True,
            verdict="Contradicted",
            confidence=0.95,
            explanation="Refuted",
            evidence_list=[]
        )
    ]
    scores = hallucination_scorer.calculate_scores(claims)
    assert scores["total_claims"] == 2
    assert scores["contradicted_claims"] == 1
    assert scores["contradiction_rate"] == 0.50
    assert scores["hallucination_score"] > 0.30
    assert scores["risk_level"] in ["HIGH_RISK", "CRITICAL_RISK"]
    assert "uncertainty_score" in scores
    assert isinstance(scores["abstention_recommended"], bool)


def test_scorer_epistemic_uncertainty_and_abstention():
    # Test case where evidence is absent or all claims unverified
    claims = [
        ClaimVerificationResultSchema(
            claim_id=f"c{i}",
            original_text=f"Unverified claim {i}",
            normalized_claim=f"Unverified claim {i}",
            start_offset=0,
            end_offset=10,
            claim_type="factual",
            verifiable=True,
            verdict="Insufficient Evidence",
            confidence=0.0,
            explanation="No evidence retrieved",
            evidence_list=[]
        )
        for i in range(4)
    ]
    scores = hallucination_scorer.calculate_scores(claims)
    assert scores["insufficient_claims"] == 4
    assert scores["unsupported_claim_rate"] == 1.0
    assert scores["evidence_availability"] == 0.0
    assert scores["uncertainty_score"] > 0.50
    assert scores["risk_level"] in ["CRITICAL_RISK", "ABSTAIN"]
    assert scores["abstention_recommended"] is True
    assert scores["abstention_reason"] is not None

