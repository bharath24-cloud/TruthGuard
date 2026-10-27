import os
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.database import get_db
from backend.app.database.models import Document, DocumentChunk
from backend.app.ingestion.parser import DocumentParser, DocumentParsingError
from backend.app.ingestion.chunker import TextChunker
from backend.app.nlp.retriever import retriever
from backend.app.schemas.document import (
    DocumentSchema,
    DocumentChunkSchema,
    DocumentUploadResponse,
    DocumentListResponse
)

router = APIRouter()


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename or "uploaded_file"
    ext = Path(filename).suffix.lower()

    if ext not in [".pdf", ".docx", ".txt", ".md", ".markdown"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported formats: .pdf, .docx, .txt, .md"
        )

    # Read bytes to compute hash and detect duplicates
    file_bytes = await file.read()
    file_size = len(file_bytes)
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes)")

    file_hash = DocumentParser.compute_file_hash(file_bytes)

    # Check for duplicate document
    existing = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing:
        # Check if chunks are indexed in the active retriever index
        indexed_chunk_ids = {meta.get("chunk_id") for meta in retriever.metadata.values()}
        db_chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == existing.id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )
        missing_chunks = [c for c in db_chunks if c.id not in indexed_chunk_ids]
        if missing_chunks:
            faiss_chunks = [{
                "chunk_id": c.id,
                "document_id": existing.id,
                "document_name": existing.filename,
                "page_number": c.page_number or 1,
                "content": c.content
            } for c in missing_chunks]
            retriever.add_chunks(faiss_chunks)
            logger.info(f"Re-indexed {len(faiss_chunks)} missing chunks for existing document '{filename}'.")
            msg = f"Document '{filename}' content was already in library; verified and restored {len(faiss_chunks)} passages to active index."
        else:
            msg = f"Document '{filename}' with identical content is already indexed and active in knowledge base."

        return DocumentUploadResponse(
            document=DocumentSchema.model_validate(existing),
            chunks_created=existing.total_chunks,
            message=msg
        )

    # Save to disk
    save_path = settings.UPLOADS_PATH / f"{file_hash}_{filename}"
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    # Parse document
    try:
        pages, total_pages = DocumentParser.parse_file(str(save_path), filename)
    except DocumentParsingError as e:
        if save_path.exists():
            os.remove(save_path)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        if save_path.exists():
            os.remove(save_path)
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")

    # Chunk text
    chunker = TextChunker()
    raw_chunks = chunker.chunk_pages(pages)

    if not raw_chunks:
        if save_path.exists():
            os.remove(save_path)
        raise HTTPException(status_code=422, detail="No readable text chunks extracted from document.")

    # Create Document DB Record
    doc = Document(
        filename=filename,
        file_type=ext.replace(".", ""),
        file_hash=file_hash,
        file_path=str(save_path),
        file_size=file_size,
        total_pages=total_pages,
        total_chunks=len(raw_chunks)
    )
    db.add(doc)
    db.flush()

    # Create Chunk Records and prepare for FAISS
    faiss_chunks = []
    for c in raw_chunks:
        db_chunk = DocumentChunk(
            document_id=doc.id,
            chunk_index=c["chunk_index"],
            page_number=c["page_number"],
            start_char=c["start_char"],
            end_char=c["end_char"],
            content=c["content"],
            token_count=c["token_count"]
        )
        db.add(db_chunk)
        db.flush()

        faiss_chunks.append({
            "chunk_id": db_chunk.id,
            "document_id": doc.id,
            "document_name": filename,
            "page_number": c["page_number"],
            "content": c["content"]
        })

    # Add to FAISS Vector Index
    retriever.add_chunks(faiss_chunks)

    db.commit()
    db.refresh(doc)
    logger.info(f"Successfully indexed document '{filename}' with {len(raw_chunks)} chunks.")

    return DocumentUploadResponse(
        document=DocumentSchema.model_validate(doc),
        chunks_created=len(raw_chunks),
        message=f"Successfully indexed '{filename}' with {len(raw_chunks)} passages."
    )


@router.get("/documents", response_model=DocumentListResponse)
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(desc(Document.created_at)).all()
    return DocumentListResponse(
        documents=[DocumentSchema.model_validate(d) for d in docs],
        total_count=len(docs)
    )


@router.get("/documents/{document_id}/chunks", response_model=List[DocumentChunkSchema])
def get_document_chunks(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index).all()
    return [DocumentChunkSchema.model_validate(c) for c in chunks]


@router.delete("/documents/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove from FAISS index
    retriever.delete_document(document_id)

    # Delete physical file
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            logger.warning(f"Failed to delete file {doc.file_path}: {e}")

    # Remove from DB (cascades to chunks)
    db.delete(doc)
    db.commit()
    logger.info(f"Deleted document '{doc.filename}' (ID: {document_id}).")

    return {"message": f"Document '{doc.filename}' deleted successfully"}
