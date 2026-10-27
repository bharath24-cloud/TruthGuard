import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ollama" in data
    assert "hardware" in data
    assert "system_memory" in data


def test_models_endpoint():
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "default_model" in data


def test_claim_extraction_endpoint():
    payload = {
        "text": "Marie Curie discovered radium in 1898 and won two Nobel Prizes."
    }
    response = client.post("/api/v1/claims/extract", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_claims"] >= 2
    assert "claims" in data


def test_documents_list_endpoint():
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total_count" in data


def test_verify_endpoint_missing_document():
    payload = {
        "question": "When was Marie Curie born?",
        "answer": "Marie Curie was born in 1867.",
        "document_ids": ["nonexistent-doc-id-12345"]
    }
    response = client.post("/api/v1/verify", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert "Document 'nonexistent-doc-id-12345' was not found" in data["detail"]


def test_verify_endpoint_valid_request():
    payload = {
        "question": "What did Marie Curie discover?",
        "answer": "Marie Curie discovered radium in 1898.",
        "evidence_source": "documents"
    }
    response = client.post("/api/v1/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["question"] == payload["question"]
    assert data["total_claims"] >= 1
    assert "hallucination_score" in data
    assert "claims" in data
