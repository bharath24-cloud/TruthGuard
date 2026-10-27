import re
from typing import List, Dict, Any
from backend.app.core.config import settings


class TextChunker:
    """Splits text passages into coherent chunks with overlap and metadata tracking."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def chunk_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunks a list of parsed pages while preserving page numbers and character offsets.
        Input: [{"page_number": int, "text": str, "char_count": int}, ...]
        Returns: [
            {
                "chunk_index": int,
                "page_number": int,
                "start_char": int,
                "end_char": int,
                "content": str,
                "token_count": int
            }, ...
        ]
        """
        chunks = []
        chunk_idx = 0

        for page in pages:
            page_num = page["page_number"]
            text = page["text"]
            if not text.strip():
                continue

            page_chunks = self._chunk_text(text)
            for c in page_chunks:
                c["chunk_index"] = chunk_idx
                c["page_number"] = page_num
                chunks.append(c)
                chunk_idx += 1

        return chunks

    def _chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Splits a single text block into overlapping chunks."""
        if len(text) <= self.chunk_size:
            return [{
                "start_char": 0,
                "end_char": len(text),
                "content": text.strip(),
                "token_count": max(1, len(text.split()))
            }]

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            
            # If not at the end of the text, try to find a natural boundary
            if end < text_len:
                # Look for paragraph break, then sentence end, then whitespace
                sub = text[start:end]
                best_break = -1
                for sep in ["\n\n", "\n", ". ", "? ", "! ", "; ", " "]:
                    idx = sub.rfind(sep)
                    if idx != -1 and idx > self.chunk_size // 3:
                        best_break = idx + len(sep)
                        break
                
                if best_break != -1:
                    end = start + best_break

            chunk_str = text[start:end].strip()
            if chunk_str:
                chunks.append({
                    "start_char": start,
                    "end_char": end,
                    "content": chunk_str,
                    "token_count": max(1, len(chunk_str.split()))
                })

            if end >= text_len:
                break

            # Advance by step size (chunk_size - chunk_overlap)
            step = max(1, (end - start) - self.chunk_overlap)
            start += step

        return chunks
