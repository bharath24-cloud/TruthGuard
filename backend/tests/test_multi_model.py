import pytest
from unittest.mock import patch, MagicMock
from backend.app.services.ollama_service import OllamaService
from backend.app.services.evaluation_service import evaluation_service


def test_ollama_verify_nli_json_parsing():
    service = OllamaService()

    # Case 1: Standard clean JSON
    with patch.object(service, "generate", return_value='{"verdict": "contradiction", "explanation": "Facts disagree"}'):
        res = service.verify_nli("premise text", "hypothesis text", model="mock-model")
        assert res["nli_label"] == "contradiction"
        assert "Facts disagree" in res["explanation"]

    # Case 2: Markdown code block wrapped JSON
    markdown_json = "```json\n{\n  \"verdict\": \"entailment\",\n  \"explanation\": \"Directly follows\"\n}\n```"
    with patch.object(service, "generate", return_value=markdown_json):
        res = service.verify_nli("premise text", "hypothesis text", model="mock-model")
        assert res["nli_label"] == "entailment"
        assert "Directly follows" in res["explanation"]

    # Case 3: Free-form conversational text fallback
    with patch.object(service, "generate", return_value="Based on the context, this is a clear contradiction of the facts."):
        res = service.verify_nli("premise text", "hypothesis text", model="mock-model")
        assert res["nli_label"] == "contradiction"


def test_multi_model_comparison_pipeline():
    # Test multi-model comparison using FEVER benchmark
    res = evaluation_service.run_multi_model_comparison(
        benchmark_name="FEVER",
        sample_size=3,
        seed=42
    )

    assert res.benchmark_name == "FEVER"
    assert res.total_samples == 3
    assert len(res.models) == 3
    assert 0.0 <= res.agreement_rate <= 1.0
    assert res.disagreements_count >= 0

    model_names = [m.model_name for m in res.models]
    assert any("DeBERTa" in name for name in model_names)
    assert any("Consensus" in name for name in model_names)
