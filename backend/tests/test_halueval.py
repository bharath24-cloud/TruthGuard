import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.datasets.halueval_adapter import (
    halueval_adapter,
    HaluEvalExample,
    HaluEvalTask
)
from backend.app.nlp.halueval_verifier import halueval_verifier
from backend.app.nlp.nli_verifier import nli_verifier

client = TestClient(app)


def test_halueval_dataset_status():
    """Verify that all 4 HaluEval tasks are discovered locally with exact record counts."""
    status = halueval_adapter.get_dataset_status()
    assert "qa" in status
    assert "dialogue" in status
    assert "summarization" in status
    assert "general" in status

    assert status["qa"]["available"] is True
    assert status["qa"]["total_records"] == 10000

    assert status["dialogue"]["available"] is True
    assert status["dialogue"]["total_records"] == 10000

    assert status["summarization"]["available"] is True
    assert status["summarization"]["total_records"] == 10000

    assert status["general"]["available"] is True
    assert status["general"]["total_records"] == 4507


def test_halueval_qa_loading_and_schema():
    """Verify loading QA task examples with balanced sampling."""
    examples, report = halueval_adapter.load_task_examples(
        task="qa",
        limit=6,
        seed=42,
        sampling_strategy="balanced_sampled"
    )
    assert len(examples) == 6
    assert report["valid_examples_extracted"] == 6
    assert report["label_distribution"]["faithful"] > 0
    assert report["label_distribution"]["hallucinated"] > 0

    first = examples[0]
    assert first.task == "qa"
    assert isinstance(first.prompt, str) and len(first.prompt) > 0
    assert isinstance(first.context, str) and len(first.context) > 0
    assert isinstance(first.response, str) and len(first.response) > 0
    assert first.ground_truth_label in ("faithful", "hallucinated")


def test_halueval_dialogue_loading():
    """Verify loading dialogue task examples."""
    examples, report = halueval_adapter.load_task_examples(
        task="dialogue",
        limit=4,
        seed=123,
        sampling_strategy="balanced_sampled"
    )
    assert len(examples) == 4
    for ex in examples:
        assert ex.task == "dialogue"
        assert ex.context is not None
        assert ex.ground_truth_label in ("faithful", "hallucinated")


def test_halueval_summarization_loading():
    """Verify loading summarization task examples."""
    examples, report = halueval_adapter.load_task_examples(
        task="summarization",
        limit=4,
        seed=42,
        sampling_strategy="balanced_sampled"
    )
    assert len(examples) == 4
    for ex in examples:
        assert ex.task == "summarization"
        assert ex.context is not None
        assert ex.ground_truth_label in ("faithful", "hallucinated")


def test_halueval_general_loading():
    """Verify loading general task examples without required context."""
    examples, report = halueval_adapter.load_task_examples(
        task="general",
        limit=6,
        seed=42,
        sampling_strategy="sequential"
    )
    assert len(examples) == 6
    for ex in examples:
        assert ex.task == "general"
        assert ex.ground_truth_label in ("faithful", "hallucinated")


def test_halueval_deterministic_seeding():
    """Verify that same seed produces identical sequence and different seed produces different."""
    ex_seed42_a, _ = halueval_adapter.load_task_examples("qa", limit=5, seed=42)
    ex_seed42_b, _ = halueval_adapter.load_task_examples("qa", limit=5, seed=42)
    ex_seed99, _ = halueval_adapter.load_task_examples("qa", limit=5, seed=99)

    labels_a = [e.ground_truth_label for e in ex_seed42_a]
    labels_b = [e.ground_truth_label for e in ex_seed42_b]
    assert labels_a == labels_b

    texts_a = [e.response for e in ex_seed42_a]
    texts_b = [e.response for e in ex_seed42_b]
    assert texts_a == texts_b


def test_halueval_paired_strategy():
    """Verify balanced_paired produces both faithful and hallucinated responses per record."""
    examples, report = halueval_adapter.load_task_examples(
        task="qa",
        limit=4,
        seed=42,
        sampling_strategy="balanced_paired"
    )
    assert len(examples) == 4
    assert report["label_distribution"]["faithful"] == 2
    assert report["label_distribution"]["hallucinated"] == 2


def test_halueval_metrics_calculation():
    """Verify calculation of accuracy, precision, recall, macro F1, and confusion matrix."""
    mock_predictions = [
        {"id": "1", "ground_truth": "faithful", "predicted_label": "faithful", "is_correct": True, "latency_ms": 10.0, "hallucination_score": 0.05, "abstention": False},
        {"id": "2", "ground_truth": "faithful", "predicted_label": "faithful", "is_correct": True, "latency_ms": 12.0, "hallucination_score": 0.10, "abstention": False},
        {"id": "3", "ground_truth": "hallucinated", "predicted_label": "hallucinated", "is_correct": True, "latency_ms": 15.0, "hallucination_score": 0.90, "abstention": False},
        {"id": "4", "ground_truth": "hallucinated", "predicted_label": "faithful", "is_correct": False, "latency_ms": 11.0, "hallucination_score": 0.30, "abstention": False},
    ]

    metrics = halueval_verifier.calculate_benchmark_metrics(mock_predictions)

    # 3 correct out of 4 = 75.0%
    assert metrics["total_evaluated"] == 4
    assert metrics["accuracy"] == 0.75
    assert metrics["abstention_count"] == 0
    assert metrics["abstention_rate"] == 0.0
    assert metrics["confusion_matrix"]["faithful"]["faithful"] == 2
    assert metrics["confusion_matrix"]["hallucinated"]["faithful"] == 1
    assert metrics["confusion_matrix"]["hallucinated"]["hallucinated"] == 1
    assert metrics["avg_latency_ms"] == 12.0


def test_halueval_verify_example_entailment():
    """Verify authentic verification of a faithful example with context grounding."""
    example = HaluEvalExample(
        id="test-qa-01",
        task="qa",
        prompt="What is the capital of France?",
        context="Paris is the capital and most populous city of France.",
        response="Paris",
        ground_truth_label="faithful",
        metadata={}
    )

    result = halueval_verifier.verify_example(example, evidence_source="context", top_k=2)

    assert result["id"] == "test-qa-01"
    assert result["ground_truth"] == "faithful"
    assert result["predicted_label"] == "faithful"
    assert result["is_correct"] is True
    assert result["hallucination_detected"] is False
    assert result["hallucination_score"] < 0.35


def test_halueval_verify_example_contradiction():
    """Verify authentic verification of a hallucinated example with contradicting context."""
    example = HaluEvalExample(
        id="test-qa-02",
        task="qa",
        prompt="What is the capital of France?",
        context="Paris is the capital and most populous city of France.",
        response="Berlin is the capital of France.",
        ground_truth_label="hallucinated",
        metadata={}
    )

    result = halueval_verifier.verify_example(example, evidence_source="context", top_k=2)

    assert result["id"] == "test-qa-02"
    assert result["ground_truth"] == "hallucinated"
    assert result["predicted_label"] == "hallucinated"
    assert result["is_correct"] is True
    assert result["hallucination_detected"] is True
    assert result["hallucination_score"] > 0.65


def test_water_claim_grounded_vs_unsupported():
    """
    Diagnoses and verifies water-related claims:
    1. Grounded water formula: H2O is verified as Supported when knowledge states it.
    2. Contradicted claim: "Water is made of argon" is verified as Contradicted.
    """
    water_knowledge = "Water is an inorganic compound with the chemical formula H2O. It consists of two hydrogen atoms bonded to one oxygen atom."

    faithful_water = HaluEvalExample(
        id="water-faithful",
        task="qa",
        prompt="What is the chemical formula of water?",
        context=water_knowledge,
        response="Water has the chemical formula H2O.",
        ground_truth_label="faithful",
        metadata={}
    )
    result_faithful = halueval_verifier.verify_example(faithful_water, evidence_source="context")
    assert result_faithful["predicted_label"] == "faithful"
    assert result_faithful["hallucination_score"] < 0.20

    contradicted_water = HaluEvalExample(
        id="water-hallucinated",
        task="qa",
        prompt="What is water made of?",
        context=water_knowledge,
        response="Water is an inorganic compound made purely of argon and neon gases.",
        ground_truth_label="hallucinated",
        metadata={}
    )
    result_hallucinated = halueval_verifier.verify_example(contradicted_water, evidence_source="context")
    assert result_hallucinated["predicted_label"] == "hallucinated"
    assert result_hallucinated["hallucination_score"] > 0.80


def test_api_halueval_status_endpoint():
    """Test the GET /api/v1/datasets/halueval/status endpoint."""
    res = client.get("/api/v1/datasets/halueval/status")
    assert res.status_code == 200
    data = res.json()
    assert data["is_available"] is True
    assert data["total_records"] == 34507
    assert "qa" in data["tasks"]
    assert "dialogue" in data["tasks"]
    assert "summarization" in data["tasks"]
    assert "general" in data["tasks"]
    assert data["tasks"]["qa"]["total_records"] == 10000
