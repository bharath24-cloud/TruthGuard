import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from backend.app.database.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(32), nullable=False)  # pdf, txt, md
    file_hash = Column(String(64), nullable=False, unique=True, index=True)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    total_pages = Column(Integer, nullable=False, default=1)
    total_chunks = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    start_char = Column(Integer, nullable=False, default=0)
    end_char = Column(Integer, nullable=False, default=0)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False, default=0)
    faiss_id = Column(Integer, nullable=True, index=True)

    document = relationship("Document", back_populates="chunks")


class VerificationRun(Base):
    __tablename__ = "verification_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question = Column(Text, nullable=False)
    original_answer = Column(Text, nullable=False)
    corrected_answer = Column(Text, nullable=True)
    model_used = Column(String(128), nullable=False, default="manual")
    evidence_source = Column(String(64), nullable=False, default="documents")
    
    total_claims = Column(Integer, nullable=False, default=0)
    verifiable_claims = Column(Integer, nullable=False, default=0)
    supported_claims = Column(Integer, nullable=False, default=0)
    contradicted_claims = Column(Integer, nullable=False, default=0)
    insufficient_claims = Column(Integer, nullable=False, default=0)
    conflicting_claims = Column(Integer, nullable=False, default=0)
    
    hallucination_score = Column(Float, nullable=False, default=0.0)
    unsupported_claim_rate = Column(Float, nullable=False, default=0.0)
    contradiction_rate = Column(Float, nullable=False, default=0.0)
    verification_coverage = Column(Float, nullable=False, default=0.0)
    evidence_availability = Column(Float, nullable=False, default=0.0)
    
    risk_level = Column(String(32), nullable=True, default="LOW_RISK")
    uncertainty_score = Column(Float, nullable=True, default=0.0)
    abstention_recommended = Column(Boolean, nullable=True, default=False)
    abstention_reason = Column(String(255), nullable=True)

    dependency_graph_json = Column(Text, nullable=True, default="{}")
    investigation_timeline_json = Column(Text, nullable=True, default="[]")

    latency_ms = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    claims = relationship("ExtractedClaim", back_populates="verification", cascade="all, delete-orphan")


class ExtractedClaim(Base):
    __tablename__ = "extracted_claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    verification_id = Column(String(36), ForeignKey("verification_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id = Column(String(64), nullable=False)  # e.g., claim_001
    original_text = Column(Text, nullable=False)
    normalized_claim = Column(Text, nullable=False)
    start_offset = Column(Integer, nullable=False, default=0)
    end_offset = Column(Integer, nullable=False, default=0)
    claim_type = Column(String(32), nullable=False, default="factual")  # factual, subjective, opinion
    verifiable = Column(Boolean, nullable=False, default=True)
    
    verdict = Column(String(64), nullable=False, default="Insufficient Evidence")  # Supported, Contradicted, Insufficient Evidence, Conflicting Evidence
    confidence = Column(Float, nullable=True, default=None)
    inference_reason = Column(String(64), nullable=False, default="NO_EVIDENCE_RETRIEVED")
    explanation = Column(Text, nullable=True)
    investigation_trace_json = Column(Text, nullable=True, default="[]")
    adjudication_notes = Column(Text, nullable=True)
    
    verification = relationship("VerificationRun", back_populates="claims")
    evidence_records = relationship("ClaimEvidence", back_populates="claim", cascade="all, delete-orphan")


class ClaimEvidence(Base):
    __tablename__ = "claim_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("extracted_claims.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(String(36), nullable=True)
    document_name = Column(String(255), nullable=False)
    page_number = Column(Integer, nullable=True)
    passage_text = Column(Text, nullable=False)
    similarity_score = Column(Float, nullable=False, default=0.0)
    source_type = Column(String(32), nullable=False, default="document")

    
    nli_label = Column(String(32), nullable=False)  # entailment, contradiction, neutral
    entailment_prob = Column(Float, nullable=False, default=0.0)
    contradiction_prob = Column(Float, nullable=False, default=0.0)
    neutral_prob = Column(Float, nullable=False, default=0.0)

    claim = relationship("ExtractedClaim", back_populates="evidence_records")


class EvaluationExperiment(Base):
    __tablename__ = "evaluation_experiments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    benchmark_name = Column(String(64), nullable=False)  # FEVER, HaluEval, TruthfulQA
    model_name = Column(String(128), nullable=False)
    total_samples = Column(Integer, nullable=False, default=0)
    
    accuracy = Column(Float, nullable=False, default=0.0)
    precision = Column(Float, nullable=False, default=0.0)
    recall = Column(Float, nullable=False, default=0.0)
    f1_score = Column(Float, nullable=False, default=0.0)
    retrieval_recall_at_k = Column(Float, nullable=False, default=0.0)
    
    confusion_matrix_json = Column(Text, nullable=False, default="{}")
    metrics_json = Column(Text, nullable=False, default="{}")
    latency_per_sample_ms = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
