import pytest
from backend.app.nlp.evidence_aggregator import evidence_aggregator, are_passages_distinct
from backend.app.nlp.explanation_engine import explanation_engine
from backend.app.schemas.verification import EvidenceCandidateSchema
from backend.app.database.database import SessionLocal, init_db
from backend.app.database.models import Document
from backend.app.nlp.retriever import sync_documents_index
from backend.app.services.verification_service import verification_service


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    db = SessionLocal()
    try:
        sync_documents_index(db)
    finally:
        db.close()


def test_case_1_explicitly_supported_claim_annual_leave():
    """
    Test Case 1: Explicitly supported claim against indexed DCU annual leave policy.
    Claim: 'The annual leave year runs from 1 January to 31 December.'
    Expected: Verdict is Supported, confidence high (> 0.85), explanation quotes the document.
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.filename.like("%annual_leave%")).first()
        assert doc is not None, "Annual leave policy document must exist in database"

        claim = "The annual leave year runs from 1 January to 31 December."
        report = verification_service.run_verification(
            db=db,
            question="What is the leave year period?",
            answer=claim,
            document_ids=[doc.id],
            evidence_source="documents"
        )
        assert report.total_claims >= 1
        res = report.claims[0]

        assert res.verdict == "Supported"
        assert res.confidence is not None
        assert res.confidence > 0.85
        assert len(res.evidence_list) > 0
        assert "Claim is Supported" in res.explanation
        assert doc.filename in res.explanation
    finally:
        db.close()


def test_case_2_explicitly_contradicted_claim_annual_leave():
    """
    Test Case 2: Explicitly contradicted claim against indexed DCU annual leave policy.
    Claim: 'The annual leave year runs from 1 April to 31 March.'
    Expected: Verdict is Contradicted, confidence high (> 0.85), explanation quotes the refute.
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.filename.like("%annual_leave%")).first()
        assert doc is not None

        claim = "The annual leave year runs from 1 April to 31 March."
        report = verification_service.run_verification(
            db=db,
            question="What is the leave year period?",
            answer=claim,
            document_ids=[doc.id],
            evidence_source="documents"
        )
        assert report.total_claims >= 1
        res = report.claims[0]

        assert res.verdict == "Contradicted"
        assert res.confidence is not None
        assert res.confidence > 0.85
        assert "Claim is Contradicted" in res.explanation
        assert doc.filename in res.explanation
    finally:
        db.close()


def test_case_3_unaddressed_claim_insufficient_evidence():
    """
    Test Case 3: Unaddressed claim that is not covered in the document.
    Claim: 'Employees are granted free gourmet coffee every Monday morning.'
    Expected: Verdict is Insufficient Evidence (neutral NLI / no factual basis).
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.filename.like("%annual_leave%")).first()
        assert doc is not None

        claim = "Employees are granted free gourmet coffee every Monday morning."
        report = verification_service.run_verification(
            db=db,
            question="Do employees receive free gourmet coffee?",
            answer=claim,
            document_ids=[doc.id],
            evidence_source="documents"
        )
        assert report.total_claims >= 1
        res = report.claims[0]

        assert res.verdict == "Insufficient Evidence"
        assert res.verdict != "Supported"
        assert res.verdict != "Contradicted"
        assert "Insufficient evidence" in res.explanation or "No relevant reference passages" in res.explanation
    finally:
        db.close()


def test_case_4_genuinely_conflicting_passages_across_documents():
    """
    Test Case 4a: Genuinely conflicting evidence across two distinct documents.
    Passage A (Doc 1) entails the claim.
    Passage B (Doc 2) refutes the claim.
    Expected: Verdict is Conflicting Evidence, explanation distinguishes both documents and quotes both.
    """
    ev_list = [
        EvidenceCandidateSchema(
            chunk_id="c_101",
            document_name="Policy_2022.pdf",
            page_number=2,
            passage_text="Full-time employees are entitled to 25 days of annual leave per year.",
            similarity_score=0.82,
            nli_label="entailment",
            entailment_prob=0.88,
            contradiction_prob=0.04,
            neutral_prob=0.08
        ),
        EvidenceCandidateSchema(
            chunk_id="c_202",
            document_name="Policy_2024_Amendment.pdf",
            page_number=5,
            passage_text="Under the revised framework, full-time employees are entitled to only 20 days of annual leave per year.",
            similarity_score=0.80,
            nli_label="contradiction",
            entailment_prob=0.05,
            contradiction_prob=0.86,
            neutral_prob=0.09
        )
    ]

    agg_res = evidence_aggregator.aggregate_evidence(ev_list, verifiable=True)
    assert agg_res.verdict == "Conflicting Evidence"
    assert agg_res.confidence == 0.87
    assert agg_res.inference_reason == "CONFLICTING_SOURCES"

    explanation = explanation_engine.generate_explanation(
        claim_text="Full-time employees receive 25 days of annual leave.",
        verdict=agg_res.verdict,
        confidence=agg_res.confidence,
        evidence_list=ev_list,
        verifiable=True,
        inference_reason=agg_res.inference_reason
    )

    assert "Conflicting evidence identified across reference documents" in explanation
    assert "Policy_2022.pdf" in explanation
    assert "Policy_2024_Amendment.pdf" in explanation
    assert "page 2" in explanation
    assert "page 5" in explanation
    assert "25 days" in explanation
    assert "20 days" in explanation


def test_case_4_genuinely_conflicting_passages_within_same_document():
    """
    Test Case 4b: Genuinely conflicting evidence within the SAME reference document.
    Passage A (Page 2) entails the claim.
    Passage B (Page 6) contradicts the claim.
    Expected: Verdict is Conflicting Evidence.
    Explanation specifically states conflict is WITHIN the reference document (not between documents)
    and quotes both passage snippets with page numbers.
    """
    doc_name = "8-annual_leave_policy_v2.2.pdf"
    ev_list = [
        EvidenceCandidateSchema(
            chunk_id="chk_p2",
            document_name=doc_name,
            page_number=2,
            passage_text="All permanent academic staff are allocated 32 days annual leave entitlement annually.",
            similarity_score=0.78,
            nli_label="entailment",
            entailment_prob=0.89,
            contradiction_prob=0.03,
            neutral_prob=0.08
        ),
        EvidenceCandidateSchema(
            chunk_id="chk_p6",
            document_name=doc_name,
            page_number=6,
            passage_text="Academic staff appointed after 2014 are allocated a maximum of 27 days annual leave entitlement.",
            similarity_score=0.76,
            nli_label="contradiction",
            entailment_prob=0.04,
            contradiction_prob=0.87,
            neutral_prob=0.09
        )
    ]

    agg_res = evidence_aggregator.aggregate_evidence(ev_list, verifiable=True)
    assert agg_res.verdict == "Conflicting Evidence"
    assert agg_res.confidence == 0.88
    assert agg_res.inference_reason == "CONFLICTING_SOURCES"

    explanation = explanation_engine.generate_explanation(
        claim_text="Permanent academic staff receive 32 days of annual leave.",
        verdict=agg_res.verdict,
        confidence=agg_res.confidence,
        evidence_list=ev_list,
        verifiable=True,
        inference_reason=agg_res.inference_reason
    )

    assert "Conflicting evidence detected within reference document" in explanation
    assert doc_name in explanation
    assert "page 2" in explanation
    assert "page 6" in explanation
    assert "32 days" in explanation
    assert "27 days" in explanation
    # Must NOT say "between indexed documents"
    assert "between indexed documents" not in explanation


def test_case_5_passages_same_document_do_not_disagree():
    """
    Test Case 5: Two passages from the same document that do NOT disagree.
    Passage A entails the claim (0.91).
    Passage B is neutral / unrelated administrative context (neutral=0.96, contradiction=0.02).
    Expected: Verdict is Supported (NOT Conflicting Evidence).
    """
    ev_list = [
        EvidenceCandidateSchema(
            chunk_id="chunk_leave_period",
            document_name="8-annual_leave_policy_v2.2.pdf",
            page_number=2,
            passage_text="The leave year is from 1st January to 31st December and annual leave must be organised within this period.",
            similarity_score=0.85,
            nli_label="entailment",
            entailment_prob=0.94,
            contradiction_prob=0.01,
            neutral_prob=0.05
        ),
        EvidenceCandidateSchema(
            chunk_id="chunk_portal",
            document_name="8-annual_leave_policy_v2.2.pdf",
            page_number=8,
            passage_text="Employees must submit their request for annual leave using the CorePortal system to their Line Manager.",
            similarity_score=0.45,
            nli_label="neutral",
            entailment_prob=0.02,
            contradiction_prob=0.03,
            neutral_prob=0.95
        )
    ]

    agg_res = evidence_aggregator.aggregate_evidence(ev_list, verifiable=True)
    assert agg_res.verdict == "Supported"
    assert agg_res.confidence == 0.94
    assert agg_res.verdict != "Conflicting Evidence"


def test_case_6_repeated_overlapping_references_do_not_produce_conflict():
    """
    Test Case 6: Duplicate or overlapping references to the same passage text.
    Passage A and Passage B have high text overlap (>70% Jaccard) from chunk sliding window.
    They cannot be counted as independent conflicting sources.
    Expected: Resolves to the dominant probability instead of declaring false conflict.
    """
    base_text = "The annual leave allowance for all staff members is 28 standard days per year."
    ev_overlapping_1 = EvidenceCandidateSchema(
        chunk_id="chunk_window_1",
        document_name="hr_policy.pdf",
        page_number=3,
        passage_text=base_text,
        similarity_score=0.75,
        nli_label="entailment",
        entailment_prob=0.62,
        contradiction_prob=0.20,
        neutral_prob=0.18
    )
    ev_overlapping_2 = EvidenceCandidateSchema(
        chunk_id="chunk_window_2",
        document_name="hr_policy.pdf",
        page_number=3,
        passage_text=base_text + " Human resources oversees this policy.",
        similarity_score=0.74,
        nli_label="contradiction",
        entailment_prob=0.22,
        contradiction_prob=0.58,
        neutral_prob=0.20
    )

    # Confirm distinctness check detects near-duplicate / overlapping passage
    assert are_passages_distinct(ev_overlapping_1, ev_overlapping_2) is False

    agg_res = evidence_aggregator.aggregate_evidence([ev_overlapping_1, ev_overlapping_2], verifiable=True)
    # Must NOT be Conflicting Evidence because chunks are duplicates
    assert agg_res.verdict != "Conflicting Evidence"
    assert agg_res.verdict == "Supported"  # 0.62 > 0.58


def test_case_7_semantic_relevance_floor_prevents_spurious_nli_verdicts():
    """
    Test Case 7: Passages below the similarity threshold (e.g. similarity < 0.25)
    must not corrupt verification with false contradictions or entailments.
    Expected: Insufficient Evidence.
    """
    ev_irrelevant = [
        EvidenceCandidateSchema(
            chunk_id="chunk_noise_1",
            document_name="unrelated.pdf",
            page_number=1,
            passage_text="Quantum mechanics describes the physical properties of nature at the scale of atoms.",
            similarity_score=0.08,  # Below threshold 0.25
            nli_label="contradiction",
            entailment_prob=0.02,
            contradiction_prob=0.92,
            neutral_prob=0.06
        )
    ]

    agg_res = evidence_aggregator.aggregate_evidence(ev_irrelevant, verifiable=True)
    assert agg_res.verdict == "Insufficient Evidence"
    assert agg_res.confidence is None
    assert agg_res.inference_reason == "NO_EVIDENCE_RETRIEVED"
