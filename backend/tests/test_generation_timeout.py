import socket
import urllib.error
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.services.ollama_service import OllamaService, GenerationTimeoutError, ollama_service
from backend.app.nlp.correction_engine import CorrectionEngine

client = TestClient(app)


def test_ollama_service_raises_generation_timeout_on_socket_timeout():
    """Verify that socket/urllib timeouts are converted to GenerationTimeoutError."""
    service = OllamaService(base_url="http://localhost:11434")

    with patch("urllib.request.urlopen", side_effect=socket.timeout("The read operation timed out")):
        with pytest.raises(GenerationTimeoutError) as exc_info:
            service.generate("Test prompt", timeout=5.0)
        assert "timed out after 5.0s" in str(exc_info.value)


def test_ollama_service_raises_generation_timeout_on_urlerror():
    """Verify that URLError wrapping a timeout also raises GenerationTimeoutError."""
    service = OllamaService(base_url="http://localhost:11434")

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timed out")):
        with pytest.raises(GenerationTimeoutError) as exc_info:
            service.generate("Test prompt", timeout=10.0)
        assert "timed out" in str(exc_info.value).lower()


def test_verify_mode_b_timeout_returns_504():
    """Verify that Mode B generation timeout returns HTTP 504 Gateway Timeout instead of unhandled 500."""
    with patch.object(
        ollama_service,
        "generate",
        side_effect=GenerationTimeoutError("Model generation timed out after 120.0s.")
    ):
        payload = {
            "question": "What is the annual leave allowance?",
            "evidence_source": "documents"
        }
        response = client.post("/api/v1/verify", json=payload)
        assert response.status_code == 504
        data = response.json()
        assert "detail" in data
        assert "Model generation timed out" in data["detail"]
        assert "Mode A" in data["detail"]


def test_generate_endpoint_timeout_returns_504():
    """Verify that /api/v1/generate returns HTTP 504 Gateway Timeout on generation timeout."""
    with patch.object(
        ollama_service,
        "generate",
        side_effect=GenerationTimeoutError("Model generation timed out after 120.0s.")
    ):
        payload = {
            "prompt": "Summarize the employee leave policy in detail."
        }
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 504
        data = response.json()
        assert "detail" in data
        assert "Model generation timed out" in data["detail"]


def test_verify_mode_b_success_with_think_false_and_budget():
    """Verify Mode B passes think=False, respects token budget, and successfully verifies answer."""
    mock_answer = "Employees are entitled to 25 days of paid annual leave each year."

    with patch.object(ollama_service, "generate", return_value=mock_answer) as mock_gen:
        payload = {
            "question": "How many days of annual leave are employees entitled to?",
            "evidence_source": "documents"
        }
        response = client.post("/api/v1/verify", json=payload)
        assert response.status_code == 200
        data = response.json()

        # Check ollama_service.generate was called with think=False, correct timeout and token limit
        mock_gen.assert_called_once()
        _, kwargs = mock_gen.call_args
        assert kwargs.get("think") is False
        assert kwargs.get("max_tokens") == settings.MODE_B_MAX_TOKENS
        assert kwargs.get("timeout") == settings.OLLAMA_GENERATION_TIMEOUT

        # Check response content
        assert data["question"] == payload["question"]
        assert data["original_answer"] == mock_answer
        assert data["total_claims"] >= 1
        assert "claims" in data


def test_generate_endpoint_passes_think_false():
    """Verify that /api/v1/generate enforces think=False and uses generation timeout."""
    with patch.object(ollama_service, "generate", return_value="Short answer.") as mock_gen:
        payload = {
            "prompt": "What is 2 + 2?",
            "max_tokens": 64
        }
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 200
        mock_gen.assert_called_once()
        _, kwargs = mock_gen.call_args
        assert kwargs.get("think") is False
        assert kwargs.get("timeout") == settings.OLLAMA_GENERATION_TIMEOUT
        assert kwargs.get("max_tokens") == 64


def test_correction_engine_uses_think_false_and_timeout():
    """Verify that CorrectionEngine calls ollama_service.generate with think=False."""
    engine = CorrectionEngine()
    with patch.object(ollama_service, "generate", return_value="Corrected sentence.") as mock_gen:
        res = engine.correct_answer(
            question="What is the fact?",
            original_answer="Wrong text.",
            claims=[]
        )
        assert res["corrected_answer"] == "Corrected sentence."
        mock_gen.assert_called_once()
        _, kwargs = mock_gen.call_args
        assert kwargs.get("think") is False
        assert kwargs.get("timeout") == settings.OLLAMA_GENERATION_TIMEOUT
