import json
import pytest
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

from backend.app.datasets.fever_loader import (
    normalize_fever_title,
    LABEL_NORMALIZATION,
    FEVERPreparedExample,
    FEVEREvidenceAnnotation
)
from backend.app.nlp.retriever import SemanticRetriever, retrieve_multi_source
from backend.app.nlp.evidence_aggregator import evidence_aggregator
from backend.app.schemas.verification import EvidenceCandidateSchema


def test_fever_label_normalization():
    assert LABEL_NORMALIZATION["SUPPORTS"] == "SUPPORTED"
    assert LABEL_NORMALIZATION["REFUTES"] == "REFUTED"
    assert LABEL_NORMALIZATION["NOT ENOUGH INFO"] == "NOT_ENOUGH_INFO"


def test_fever_title_normalization():
    assert normalize_fever_title("Soul_Food_-LRB-film-RRB-") == "Soul Food (film)"
    assert normalize_fever_title("Albert_Einstein_-COLON-_Physicist") == "Albert Einstein : Physicist"
    assert normalize_fever_title("Star_Wars_-LSB-film-RSB-") == "Star Wars [film]"
    assert normalize_fever_title("") == ""


def test_fever_schema_validation():
    annotation = FEVEREvidenceAnnotation(
        annotation_id=101,
        evidence_id=202,
        wikipedia_title="Roman_Atwood",
        clean_title="Roman Atwood",
        sentence_id=0
    )
    ex = FEVERPreparedExample(
        id="12345",
        claim="Roman Atwood is a content creator.",
        label="SUPPORTED",
        original_label="SUPPORTS",
        verifiable=True,
        evidence_annotations=[[annotation]],
        wikipedia_titles=["Roman_Atwood"],
        source_dataset="FEVER",
        split="paper_dev"
    )
    assert ex.id == "12345"
    assert ex.label == "SUPPORTED"
    assert len(ex.evidence_annotations) == 1
    assert ex.evidence_annotations[0][0].sentence_id == 0


def test_fever_missing_evidence_handling():
    ex = FEVERPreparedExample(
        id="999",
        claim="Non-verifiable assertion about personal preference.",
        label="NOT_ENOUGH_INFO",
        original_label="NOT ENOUGH INFO",
        verifiable=False,
        evidence_annotations=[],
        wikipedia_titles=[],
        source_dataset="FEVER",
        split="paper_dev"
    )
    assert ex.verifiable is False
    assert len(ex.evidence_annotations) == 0


def test_fever_faiss_indexing_and_retrieval(tmp_path):
    # Test dedicated FAISS instance with synthetic Wikipedia passages
    indexer = SemanticRetriever(index_name="test_fever_kb", source_type="fever")
    # Redirect paths to tmp_path
    indexer.index_path = tmp_path / "test_fever_kb.faiss"
    indexer.meta_path = tmp_path / "test_fever_kb.json"

    chunks = [
        {
            "chunk_id": "fever_marie_curie_s0",
            "document_id": "fever_wiki_marie_curie",
            "document_name": "Wikipedia: Marie Curie",
            "page_number": 1,
            "content": "Marie Skłodowska Curie was a Polish and naturalized-French physicist and chemist who conducted pioneering research on radioactivity.",
            "source_type": "fever"
        },
        {
            "chunk_id": "fever_albert_einstein_s0",
            "document_id": "fever_wiki_albert_einstein",
            "document_name": "Wikipedia: Albert Einstein",
            "page_number": 1,
            "content": "Albert Einstein was a German-born theoretical physicist who is widely held to be one of the greatest and most influential scientists of all time.",
            "source_type": "fever"
        }
    ]

    indexer.add_chunks(chunks)
    assert indexer.index.ntotal == 2

    # Query for Marie Curie
    results = indexer.retrieve("Marie Curie radioactivity research", top_k=1)
    assert len(results) == 1
    assert "Marie Curie" in results[0]["document_name"]
    assert results[0]["source_type"] == "fever"
    assert results[0]["similarity_score"] > 0.4


def test_empty_retrieval_diagnostics():
    indexer = SemanticRetriever(index_name="test_empty_kb")
    indexer.clear()
    assert indexer.get_empty_reason() == "NO_DOCUMENTS_INDEXED"

    agg_res = evidence_aggregator.aggregate_evidence([], verifiable=True, empty_reason="NO_DOCUMENTS_INDEXED")
    assert agg_res.verdict == "Insufficient Evidence"
    assert agg_res.confidence is None
    assert agg_res.inference_reason == "NO_DOCUMENTS_INDEXED"
    assert agg_res.confidence_calibrated is False


def test_evaluation_metrics_computation():
    y_true = ["Supported", "Contradicted", "Supported", "Insufficient Evidence"]
    y_pred = ["Supported", "Contradicted", "Insufficient Evidence", "Insufficient Evidence"]

    acc = accuracy_score(y_true, y_pred)
    assert acc == 0.75  # 3 out of 4 correct

    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    assert f1 > 0.6

    labels = ["Contradicted", "Insufficient Evidence", "Supported"]
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    assert cm.shape == (3, 3)
