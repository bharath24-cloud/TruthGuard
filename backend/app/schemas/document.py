from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentChunkSchema(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    page_number: Optional[int] = None
    start_char: int
    end_char: int
    content: str
    token_count: int

    class Config:
        from_attributes = True


class DocumentSchema(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    total_pages: int
    total_chunks: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    document: DocumentSchema
    chunks_created: int
    message: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentSchema]
    total_count: int
