import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.database import SessionLocal, init_db
from backend.app.database.models import Document, DocumentChunk
from backend.app.nlp.retriever import retriever, fever_retriever, sync_documents_index, retrieve_multi_source
from backend.app.services.verification_service import verification_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_db_synced():
    """Ensures database is initialized and document library index is synced before each test."""
    init_db()
    db = SessionLocal()
    try:
        sync_documents_index(db)
    finally:
        db.close()


def test_document_library_sync_and_persistence():
    """Verify that sync_documents_index properly synchronizes all SQLite chunks into FAISS and BM25."""
    db = SessionLocal()
    try:
        # Document count from DB
        leave_doc = db.query(Document).filter(Document.filename.like("%annual_leave%")).first()
        assert leave_doc is not None, "Annual leave policy document should exist in database"
        
        # Test synchronization
        synced_count = sync_documents_index(db)
        assert synced_count >= leave_doc.total_chunks
        assert retriever.index.ntotal == synced_count
        assert retriever.bm25.total_docs == synced_count

        # Metadata provenance check
        indexed_doc_ids = {meta.get("document_id") for meta in retriever.metadata.values()}
        assert leave_doc.id in indexed_doc_ids

        # Ensure source filenames and chunk metadata are preserved
        sample_meta = next(m for m in retriever.metadata.values() if m.get("document_id") == leave_doc.id)
        assert sample_meta["document_name"] == leave_doc.filename
        assert "page_number" in sample_meta
        assert len(sample_meta["content"]) > 0
    finally:
        db.close()


def test_verify_annual_leave_supported_claim():
    """
    Acceptance Test 1: Supported claim
    'The annual leave year runs from 1 January to 31 December.'
    Must retrieve evidence from the uploaded annual leave policy and return 'Supported'.
    """
    db = SessionLocal()
    try:
        leave_doc = db.query(Document).filter(Document.filename.like("%annual_leave%")).first()
        assert leave_doc is not None

        claim_text = "The annual leave year runs from 1 January to 31 December."
        report = verification_service.run_verification(
            db=db,
            question="What is the annual leave year period?",
            answer=claim_text,
            document_ids=[leave_doc.id],
            evidence_source="documents"
        )

        assert report.total_claims >= 1
        claim_result = report.claims[0]

        assert claim_result.verdict == "Supported"
        assert claim_result.confidence is not None
        assert claim_result.confidence > 0.85
        assert len(claim_result.evidence_list) > 0

        # Verify source provenance
        top_ev = claim_result.evidence_list[0]
        assert top_ev.document_name == leave_doc.filename
        assert top_ev.page_number in [2, 3]
        assert "1st January to 31st December" in top_ev.passage_text or "1 January" in top_ev.passage_text
        assert "Claim is Supported" in claim_result.explanation
    finally:
        db.close()


def test_verify_annual_leave_contradicted_claim():
    """
    Acceptance Test 2: Contradicted claim
    'The annual leave year runs from 1 April to 31 March.'
    Must retrieve the 1 Jan - 31 Dec passage and return 'Contradicted'.
    """
    db = SessionLocal()
    try:
        leave_doc = db.query(Document).filter(Document.filename.like("%annual_leave%")).first()
        assert leave_doc is not None

        claim_text = "The annual leave year runs from 1 April to 31 March."
        report = verification_service.run_verification(
            db=db,
            question="What is the annual leave year period?",
            answer=claim_text,
            document_ids=[leave_doc.id],
            evidence_source="documents"
        )

        assert report.total_claims >= 1
        claim_result = report.claims[0]

        assert claim_result.verdict == "Contradicted"
        assert claim_result.confidence is not None
        assert claim_result.confidence > 0.85
        assert len(claim_result.evidence_list) > 0

        # Verify refuting evidence provenance
        contra_ev = next((e for e in claim_result.evidence_list if e.nli_label == "contradiction"), None)
        assert contra_ev is not None, "Contradicting evidence passage must be present in retrieved evidence"
        assert contra_ev.document_name == leave_doc.filename
        assert "1st January to 31st December" in contra_ev.passage_text
        assert "Directly refuted by document" in claim_result.explanation
    finally:
        db.close()


def test_verify_annual_leave_unaddressed_claim():
    """
    Acceptance Test 3: Unaddressed claim
    'Employees receive a free lunch voucher every Friday.'
    Policy does not address this; TruthGuard must return 'Insufficient Evidence' and NOT fabricate 'Supported'.
    """
    db = SessionLocal()
    try:
        leave_doc = db.query(Document).filter(Document.filename.like("%annual_leave%")).first()
        assert leave_doc is not None

        claim_text = "Employees receive a free lunch voucher every Friday."
        report = verification_service.run_verification(
            db=db,
            question="Do employees get free lunch vouchers?",
            answer=claim_text,
            document_ids=[leave_doc.id],
            evidence_source="documents"
        )

        assert report.total_claims >= 1
        claim_result = report.claims[0]

        # Must be Insufficient Evidence
        assert claim_result.verdict == "Insufficient Evidence"
        assert claim_result.verdict != "Supported"
        assert "Insufficient evidence" in claim_result.explanation or "No relevant reference passages" in claim_result.explanation
    finally:
        db.close()


def test_fever_benchmark_separate_index_preservation():
    """
    Verify that FEVER index remains separate and functional without interference from uploaded documents.
    """
    # FEVER index should contain its 570 benchmark passages
    assert fever_retriever.index_name == "fever_knowledge_base"
    assert fever_retriever.index.ntotal == 570
    assert fever_retriever.bm25.total_docs == 570

    # Test retrieval from FEVER
    cands, reason = retrieve_multi_source(
        query="Roman Atwood is a person who creates vlogs on YouTube.",
        source="fever",
        top_k=2
    )
    assert len(cands) > 0
    assert reason == "EVIDENCE_ENTAILED"
    assert cands[0]["source_type"] == "fever"
    assert "fever_knowledge_base" in fever_retriever.index_name


def test_verify_endpoint_via_http_client():
    """
    Integration Test: Test verification via FastAPI test client against uploaded document.
    """
    db = SessionLocal()
    try:
        leave_doc = db.query(Document).filter(Document.filename.like("%annual_leave%")).first()
        assert leave_doc is not None

        payload = {
            "question": "What is the annual leave year period?",
            "answer": "The annual leave year runs from 1 January to 31 December.",
            "document_ids": [leave_doc.id],
            "evidence_source": "documents"
        }
        response = client.post("/api/v1/verify", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["total_claims"] >= 1
        assert data["supported_claims"] >= 1
        assert data["claims"][0]["verdict"] == "Supported"
        assert data["claims"][0]["evidence_list"][0]["document_name"] == leave_doc.filename
    finally:
        db.close()
