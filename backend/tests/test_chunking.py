import pytest
from backend.app.ingestion.chunker import TextChunker


def test_chunker_basic():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    pages = [
        {
            "page_number": 1,
            "text": "The quick brown fox jumps over the lazy dog. A second sentence is here for length. And a third sentence follows.",
            "char_count": 113
        }
    ]
    chunks = chunker.chunk_pages(pages)
    assert len(chunks) >= 1
    assert chunks[0]["page_number"] == 1
    assert "content" in chunks[0]
    assert chunks[0]["start_char"] >= 0
    assert chunks[0]["end_char"] > chunks[0]["start_char"]


def test_chunker_multipage():
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    pages = [
        {"page_number": 1, "text": "Page one text content that is relatively short."},
        {"page_number": 2, "text": "Page two text content that also provides information."}
    ]
    chunks = chunker.chunk_pages(pages)
    assert len(chunks) == 2
    assert chunks[0]["page_number"] == 1
    assert chunks[1]["page_number"] == 2
