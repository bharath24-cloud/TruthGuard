import pytest
from backend.app.nlp.retriever import SemanticRetriever


def test_retriever_indexing_and_search():
    retriever = SemanticRetriever(index_name="test_index")
    retriever.clear()

    chunks = [
        {
            "chunk_id": "c1",
            "document_id": "doc_1",
            "document_name": "astronomy.txt",
            "page_number": 1,
            "content": "The Earth is the third planet from the Sun and the only astronomical object known to harbor life."
        },
        {
            "chunk_id": "c2",
            "document_id": "doc_2",
            "document_name": "chemistry.txt",
            "page_number": 1,
            "content": "Water is an inorganic compound with the chemical formula H2O consisting of hydrogen and oxygen."
        }
    ]

    added = retriever.add_chunks(chunks)
    assert added == 2
    assert retriever.index.ntotal == 2

    # Query for astronomy
    results = retriever.retrieve("Which planet harbors life?", top_k=1)
    assert len(results) == 1
    assert results[0]["chunk_id"] == "c1"
    assert "Earth" in results[0]["passage_text"]
    assert results[0]["similarity_score"] > 0.40

    # Clean up
    retriever.clear()
    assert retriever.index.ntotal == 0
