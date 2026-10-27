import pytest
from backend.app.nlp.claim_extractor import claim_extractor
from backend.app.schemas.claim import AtomicClaimItem


def test_atomic_claim_schema():
    claim = AtomicClaimItem(
        claim_id="claim_001",
        original_text="Marie Curie won two Nobel Prizes.",
        normalized_claim="Marie Curie won two Nobel Prizes.",
        start_offset=0,
        end_offset=34,
        claim_type="factual",
        verifiable=True
    )
    assert claim.claim_id == "claim_001"
    assert claim.verifiable is True
    assert claim.claim_type == "factual"


def test_rule_based_claim_splitting():
    text = "Marie Curie discovered radium in 1898 and won two Nobel Prizes."
    claims = claim_extractor._extract_with_rules(text)
    
    assert len(claims) >= 2
    # Verify offsets correspond to the text
    for c in claims:
        extracted_span = text[c.start_offset:c.end_offset]
        assert c.original_text.strip() == extracted_span.strip()


def test_subjective_claim_classification():
    text = "She was the greatest scientist ever and lived in Paris."
    claims = claim_extractor._extract_with_rules(text)
    
    # Should identify subjective statement
    has_subjective = any(c.claim_type == "subjective" or not c.verifiable for c in claims)
    assert has_subjective is True
