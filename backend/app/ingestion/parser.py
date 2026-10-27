import hashlib
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pymupdf as fitz
from backend.app.core.logging import logger


class DocumentParsingError(Exception):
    """Raised when document parsing fails."""
    pass


class DocumentParser:
    """Extracts text and page-level metadata from PDF, TXT, and Markdown files."""

    @staticmethod
    def compute_file_hash(file_bytes: bytes) -> str:
        """Computes SHA-256 / MD5 digest for deduplication."""
        return hashlib.sha256(file_bytes).hexdigest()

    @classmethod
    def parse_file(cls, file_path: str, filename: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Parses a document file and returns a list of page objects:
        [{"page_number": int, "text": str, "char_count": int}, ...]
        and total page count.
        """
        path = Path(file_path)
        if not path.exists():
            raise DocumentParsingError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        if ext == ".pdf":
            return cls._parse_pdf(path)
        elif ext == ".docx":
            return cls._parse_docx(path)
        elif ext in [".txt", ".md", ".markdown"]:
            return cls._parse_text(path)
        else:
            raise DocumentParsingError(f"Unsupported file format: {ext}. Supported formats: .pdf, .docx, .txt, .md")

    @classmethod
    def _parse_pdf(cls, path: Path) -> Tuple[List[Dict[str, Any]], int]:
        pages = []
        try:
            doc = fitz.open(str(path))
            total_pages = len(doc)
            if total_pages == 0:
                raise DocumentParsingError("PDF file is empty (0 pages).")

            for page_idx in range(total_pages):
                page = doc.load_page(page_idx)
                text = page.get_text("text").strip()
                pages.append({
                    "page_number": page_idx + 1,
                    "text": text,
                    "char_count": len(text)
                })
            doc.close()
        except Exception as e:
            logger.error(f"Failed to parse PDF {path.name}: {e}")
            raise DocumentParsingError(f"Error reading PDF {path.name}: {str(e)}")

        # Check if all pages are empty (e.g. scanned image-only PDF without OCR)
        all_empty = all(len(p["text"]) == 0 for p in pages)
        if all_empty:
            raise DocumentParsingError(
                f"PDF '{path.name}' contains no readable digital text. "
                "Scanned PDFs without embedded text layers require OCR and are not supported in this version."
            )

        return pages, total_pages

    @classmethod
    def _parse_text(cls, path: Path) -> Tuple[List[Dict[str, Any]], int]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if not text:
                raise DocumentParsingError(f"Text file '{path.name}' is empty.")
            return [{
                "page_number": 1,
                "text": text,
                "char_count": len(text)
            }], 1
        except Exception as e:
            logger.error(f"Failed to read text file {path.name}: {e}")
            raise DocumentParsingError(f"Error reading text file {path.name}: {str(e)}")

    @classmethod
    def _parse_docx(cls, path: Path) -> Tuple[List[Dict[str, Any]], int]:
        try:
            import docx
            doc = docx.Document(str(path))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)
            if not full_text:
                raise DocumentParsingError(f"Word document '{path.name}' contains no readable text.")
            return [{
                "page_number": 1,
                "text": full_text,
                "char_count": len(full_text)
            }], 1
        except Exception as e:
            logger.error(f"Failed to read DOCX file {path.name}: {e}")
            raise DocumentParsingError(f"Error reading Word document {path.name}: {str(e)}")
