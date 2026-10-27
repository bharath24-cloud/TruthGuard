import pytest
from backend.app.nlp.evidence_aggregator import evidence_aggregator
from backend.app.schemas.verification import EvidenceCandidateSchema


def test_aggregate_supported():
    ev_list = [
        EvidenceCandidateSchema(
            chunk_id="1",
            document_name="doc.txt",
            page_number=1,
            passage_text="Sample text",
            similarity_score=0.8,
            nli_label="entailment",
            entailment_prob=0.88,
            contradiction_prob=0.04,
            neutral_prob=0.08
        )
    ]
    verdict, conf, _ = evidence_aggregator.aggregate_evidence(ev_list, verifiable=True)
    assert verdict == "Supported"
    assert conf == 0.88


def test_aggregate_contradicted():
    ev_list = [
        EvidenceCandidateSchema(
            chunk_id="1",
            document_name="doc.txt",
            page_number=1,
            passage_text="Sample text",
            similarity_score=0.8,
            nli_label="contradiction",
            entailment_prob=0.05,
            contradiction_prob=0.91,
            neutral_prob=0.04
        )
    ]
    verdict, conf, _ = evidence_aggregator.aggregate_evidence(ev_list, verifiable=True)
    assert verdict == "Contradicted"
    assert conf == 0.91


def test_aggregate_conflicting():
    ev_list = [
        EvidenceCandidateSchema(
            chunk_id="1",
            document_name="source_a.txt",
            page_number=1,
            passage_text="Supports claim",
            similarity_score=0.75,
            nli_label="entailment",
            entailment_prob=0.85,
            contradiction_prob=0.05,
            neutral_prob=0.10
        ),
        EvidenceCandidateSchema(
            chunk_id="2",
            document_name="source_b.txt",
            page_number=2,
            passage_text="Contradicts claim",
            similarity_score=0.72,
            nli_label="contradiction",
            entailment_prob=0.06,
            contradiction_prob=0.84,
            neutral_prob=0.10
        )
    ]
    verdict, conf, _ = evidence_aggregator.aggregate_evidence(ev_list, verifiable=True)
    assert verdict == "Conflicting Evidence"


def test_aggregate_insufficient():
    result = evidence_aggregator.aggregate_evidence([], verifiable=True)
    verdict, conf, _ = result
    assert verdict == "Insufficient Evidence"
    assert conf is None
    assert result.confidence_calibrated is False
    assert result.inference_reason == "NO_EVIDENCE_RETRIEVED"


def test_aggregate_no_docs_indexed():
    result = evidence_aggregator.aggregate_evidence([], verifiable=True, empty_reason="NO_DOCUMENTS_INDEXED")
    assert result.verdict == "Insufficient Evidence"
    assert result.confidence is None
    assert result.inference_reason == "NO_DOCUMENTS_INDEXED"


def test_aggregate_non_verifiable():
    result = evidence_aggregator.aggregate_evidence([], verifiable=False)
    assert result.verdict == "Insufficient Evidence"
    assert result.confidence is None
    assert result.inference_reason == "NON_VERIFIABLE_CLAIM"

