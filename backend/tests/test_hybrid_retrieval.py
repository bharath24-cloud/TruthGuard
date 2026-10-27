import os
import shutil
import pytest
from backend.app.nlp.retriever import BM25Index, SemanticRetriever


def test_bm25_tokenization_and_indexing():
    bm25 = BM25Index()
    tokens = bm25.tokenize("The quick brown fox jumps over 123 lazy dogs!")
    assert "quick" in tokens
    assert "fox" in tokens
    assert "123" in tokens
    assert "lazy" in tokens

    docs = [
        "TruthGuard provides explainable NLP hallucination detection.",
        "Photosynthesis is how green plants convert solar energy into chemical energy.",
        "DeBERTa-v3 cross-encoder validates natural language inference entailment."
    ]
    for idx, doc in enumerate(docs):
        bm25.add_document(idx, doc)

    assert bm25.total_docs == 3
    assert len(bm25.doc_len) == 3

    # Keyword search for specific terms
    scores = bm25.score_query("photosynthesis plants solar")
    assert len(scores) > 0
    # doc 1 should have highest BM25 score
    best_doc_id = max(scores, key=scores.get)
    assert best_doc_id == 1
    assert scores[1] > 0.0

    # Rare technical term search
    scores_tech = bm25.score_query("DeBERTa inference")
    best_tech_id = max(scores_tech, key=scores_tech.get)
    assert best_tech_id == 2


def test_hybrid_retrieval_rrf():
    retriever = SemanticRetriever(index_name="test_hybrid_index")
    retriever.clear()

    chunks = [
        {
            "chunk_id": "doc_alpha",
            "document_id": "d1",
            "document_name": "alpha.txt",
            "page_number": 1,
            "content": "Protocol TX-9002 was activated during the seismic emergency on Mars."
        },
        {
            "chunk_id": "doc_beta",
            "document_id": "d2",
            "document_name": "beta.txt",
            "page_number": 1,
            "content": "General geology and planetary science observations from Martian rovers."
        }
    ]

    added = retriever.add_chunks(chunks)
    assert added == 2
    assert retriever.index.ntotal == 2
    assert retriever.bm25.total_docs == 2

    # Query using exact rare keyword code "TX-9002"
    results = retriever.retrieve("What happened under protocol TX-9002?", top_k=1)
    assert len(results) == 1
    assert results[0]["chunk_id"] == "doc_alpha"
    assert "TX-9002" in results[0]["passage_text"]
    assert results[0]["similarity_score"] > 0.0

    # Clean up
    retriever.clear()
    assert retriever.index.ntotal == 0
    assert retriever.bm25.total_docs == 0
