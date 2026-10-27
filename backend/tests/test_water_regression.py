import pytest
from backend.app.database.database import SessionLocal, init_db
from backend.app.services.verification_service import verification_service
from backend.app.nlp.retriever import retriever, sync_documents_index


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_water_verification_with_and_without_evidence():
    """
    Regression Test for Water Example:
    1. Without evidence:
       Claims about water composition and boiling point must return 'Insufficient Evidence'
       with no fabricated confidence (confidence=None) and abstention recommended.
    2. With indexed evidence:
       Both claims ('Water is composed of hydrogen and oxygen' and 'Its boiling point is 100 degrees Celsius')
       must be retrieved via hybrid search and verified as 'Supported' with high confidence.
    """
    db = SessionLocal()
    question = "What is water composed of and what is its boiling point?"
    answer = "Water is composed of hydrogen and oxygen. Its boiling point is 100 degrees Celsius."

    try:
        # Part 1: Verify WITHOUT any indexed evidence
        retriever.clear()
        report_no_evidence = verification_service.run_verification(
            db=db,
            question=question,
            answer=answer,
            evidence_source="documents"
        )

        assert report_no_evidence.total_claims >= 2
        # Without evidence, TruthGuard MUST NOT fabricate 'Supported'
        assert report_no_evidence.supported_claims == 0
        assert report_no_evidence.insufficient_claims == report_no_evidence.total_claims
        assert report_no_evidence.abstention_recommended is True
        for c in report_no_evidence.claims:
            assert c.verdict == "Insufficient Evidence"
            assert c.confidence is None
            assert c.inference_reason in ["NO_DOCUMENTS_INDEXED", "NO_EVIDENCE_RETRIEVED"]

        # Part 2: Index ground truth water science document
        water_chunks = [
            {
                "chunk_id": "water_chunk_001",
                "document_id": "doc_water_001",
                "document_name": "water_chemistry.txt",
                "page_number": 1,
                "content": "Water is an inorganic chemical compound composed of hydrogen and oxygen. The molecular formula is H2O, consisting of two hydrogen atoms covalently bonded to one oxygen atom."
            },
            {
                "chunk_id": "water_chunk_002",
                "document_id": "doc_water_001",
                "document_name": "water_chemistry.txt",
                "page_number": 1,
                "content": "Under standard atmospheric pressure of 1 atm, pure water has a normal boiling point of 100 degrees Celsius (212 degrees Fahrenheit)."
            }
        ]
        retriever.add_chunks(water_chunks)

        # Verify WITH indexed evidence
        report_with_evidence = verification_service.run_verification(
            db=db,
            question=question,
            answer=answer,
            evidence_source="documents"
        )

        assert report_with_evidence.total_claims >= 2
        assert report_with_evidence.supported_claims == report_with_evidence.total_claims
        assert report_with_evidence.contradicted_claims == 0
        assert report_with_evidence.insufficient_claims == 0
        assert report_with_evidence.hallucination_score < 0.15
        assert report_with_evidence.risk_level == "LOW_RISK"
        assert report_with_evidence.abstention_recommended is False

        for c in report_with_evidence.claims:
            assert c.verdict == "Supported"
            assert c.confidence is not None
            assert c.confidence > 0.60
            assert len(c.evidence_list) > 0
    finally:
        # Restore active library documents so other tests and app state remain consistent
        sync_documents_index(db)
        db.close()
