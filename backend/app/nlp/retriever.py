import json
import math
import os
import re
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
import faiss
import numpy as np

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.nlp.embeddings import embedding_engine


class BM25Index:
    """
    In-memory, persistent Okapi BM25 keyword index for document chunks.
    Implements Robertson & Spärck Jones Okapi BM25 with configurable k1 and b.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len: Dict[int, int] = {}
        self.doc_freqs: Dict[str, int] = {}  # term -> document count
        self.doc_term_freqs: Dict[int, Counter] = {}  # doc_id -> Counter(term -> count)
        self.total_docs: int = 0
        self.avg_doc_len: float = 0.0

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Alphanumeric tokenization with lowercasing and punctuation stripping."""
        if not text:
            return []
        return re.findall(r"\b[a-zA-Z0-9_\u00C0-\u017F-]{2,}\b", text.lower())

    def add_document(self, doc_id: int, text: str):
        """Indexes a single document chunk for BM25 keyword matching."""
        tokens = self.tokenize(text)
        length = len(tokens)
        self.doc_len[doc_id] = length
        tf = Counter(tokens)
        self.doc_term_freqs[doc_id] = tf
        for term in tf.keys():
            self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1
        self.total_docs = len(self.doc_len)
        self.avg_doc_len = sum(self.doc_len.values()) / max(1, self.total_docs)

    def remove_document(self, doc_id: int):
        """Removes a document from BM25 stats."""
        if doc_id not in self.doc_len:
            return
        tf = self.doc_term_freqs.pop(doc_id, Counter())
        self.doc_len.pop(doc_id, None)
        for term in tf.keys():
            if term in self.doc_freqs:
                self.doc_freqs[term] -= 1
                if self.doc_freqs[term] <= 0:
                    del self.doc_freqs[term]
        self.total_docs = len(self.doc_len)
        self.avg_doc_len = sum(self.doc_len.values()) / max(1, self.total_docs) if self.total_docs > 0 else 0.0

    def clear(self):
        """Resets all BM25 inverted indices and statistics."""
        self.doc_len.clear()
        self.doc_freqs.clear()
        self.doc_term_freqs.clear()
        self.total_docs = 0
        self.avg_doc_len = 0.0

    def score_query(self, query: str) -> Dict[int, float]:
        """
        Calculates Okapi BM25 scores for all matching documents given a query string.
        Returns a mapping of doc_id -> BM25 score.
        """
        tokens = self.tokenize(query)
        if not tokens or self.total_docs == 0:
            return {}

        scores: Dict[int, float] = {}
        for term in tokens:
            df = self.doc_freqs.get(term, 0)
            if df == 0:
                continue

            # Robertson-Spärck Jones IDF with floor to avoid negative weights
            idf = math.log((self.total_docs - df + 0.5) / (df + 0.5) + 1.0)
            if idf <= 0:
                idf = 0.1

            for doc_id, tf_counter in self.doc_term_freqs.items():
                freq = tf_counter.get(term, 0)
                if freq == 0:
                    continue
                d_len = self.doc_len.get(doc_id, 0)
                denom = freq + self.k1 * (1.0 - self.b + self.b * (d_len / max(1.0, self.avg_doc_len)))
                term_score = idf * (freq * (self.k1 + 1.0)) / denom
                scores[doc_id] = scores.get(doc_id, 0.0) + term_score

        return scores


class SemanticRetriever:
    """
    Hybrid Evidence Retriever combining:
    1. FAISS IndexFlatIP Dense Semantic Vector Search (exact cosine similarity)
    2. Okapi BM25 Sparse Keyword Inverted Index
    3. Reciprocal Rank Fusion (RRF) & Convex Score Combination for hybrid retrieval.
    """

    def __init__(self, index_name: str = "truthguard_evidence", source_type: str = "document"):
        self.index_name = index_name
        self.source_type = source_type
        self.index_path = settings.INDEXES_PATH / f"{index_name}.faiss"
        self.meta_path = settings.INDEXES_PATH / f"{index_name}.json"
        
        self.dimension = settings.EMBEDDING_DIM
        self.index = faiss.IndexFlatIP(self.dimension)
        # Metadata storage: maps faiss_id (int) -> chunk metadata dict
        self.metadata: Dict[int, Dict[str, Any]] = {}
        # BM25 sparse keyword index
        self.bm25 = BM25Index(k1=settings.BM25_K1, b=settings.BM25_B)
        
        self.load_index()

    def get_empty_reason(self, filter_doc_ids: Optional[List[str]] = None) -> str:
        """Determines the exact diagnostic reason why no evidence passages were found."""
        if self.index.ntotal == 0:
            return "NO_DOCUMENTS_INDEXED"
        if filter_doc_ids:
            indexed_doc_ids = {meta.get("document_id") for meta in self.metadata.values()}
            if not any(doc_id in indexed_doc_ids for doc_id in filter_doc_ids):
                return "NO_DOCUMENTS_SELECTED"
        return "NO_EVIDENCE_RETRIEVED"

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Embeds and adds document chunks to both the FAISS dense index and BM25 sparse index.
        """
        if not chunks:
            return 0

        texts = [c["content"] for c in chunks]
        embeddings = embedding_engine.encode(texts, normalize_embeddings=True)

        current_total = self.index.ntotal
        self.index.add(embeddings)

        for i, chunk in enumerate(chunks):
            faiss_id = current_total + i
            chunk_content = chunk.get("content", "")
            self.metadata[faiss_id] = {
                "faiss_id": faiss_id,
                "chunk_id": chunk.get("chunk_id", ""),
                "document_id": chunk.get("document_id", ""),
                "document_name": chunk.get("document_name", "Unknown"),
                "page_number": chunk.get("page_number", 1),
                "content": chunk_content,
                "source_type": chunk.get("source_type", self.source_type)
            }
            # Index into BM25
            self.bm25.add_document(faiss_id, chunk_content)

        self.save_index()
        logger.info(
            f"Added {len(chunks)} chunks to Hybrid index '{self.index_name}'. "
            f"FAISS Total: {self.index.ntotal}, BM25 Total: {self.bm25.total_docs}"
        )
        return len(chunks)

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_doc_ids: Optional[List[str]] = None,
        similarity_threshold: Optional[float] = None,
        mode: str = "hybrid"  # "hybrid" | "dense" | "bm25"
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-k evidence passages for a query using Hybrid RRF, Dense Semantic, or BM25 keyword search.
        
        Returns candidate passages with document provenance, cosine similarity, BM25 score, and composite relevance.
        """
        k = top_k or settings.RETRIEVAL_TOP_K
        threshold = similarity_threshold if similarity_threshold is not None else settings.SIMILARITY_THRESHOLD
        alpha = settings.RETRIEVAL_HYBRID_ALPHA

        if self.index.ntotal == 0 or not query.strip():
            return []

        # Normalize filter_doc_ids: treat empty list or falsy elements as None
        active_filter_ids = set([d for d in filter_doc_ids if d]) if filter_doc_ids else None

        # 1. Dense Semantic Search via FAISS
        dense_results: Dict[int, float] = {}
        dense_ranks: Dict[int, int] = {}
        if mode in ["hybrid", "dense"]:
            query_vec = embedding_engine.encode([query], normalize_embeddings=True)
            fetch_k = min(self.index.ntotal, max(k * 10, 50) if active_filter_ids else max(k * 4, 20))
            scores, indices = self.index.search(query_vec, fetch_k)

            rank = 1
            for score, faiss_id in zip(scores[0], indices[0]):
                if faiss_id == -1 or faiss_id not in self.metadata:
                    continue
                meta = self.metadata[faiss_id]
                if active_filter_ids and meta.get("document_id") not in active_filter_ids:
                    continue
                dense_results[faiss_id] = float(score)
                dense_ranks[faiss_id] = rank
                rank += 1

        # 2. Sparse Keyword Search via Okapi BM25
        bm25_scores = self.bm25.score_query(query)
        bm25_results: Dict[int, float] = {}
        bm25_ranks: Dict[int, int] = {}
        if mode in ["hybrid", "bm25"]:
            sorted_bm25 = sorted(bm25_scores.items(), key=lambda x: x[1], reverse=True)
            rank = 1
            for faiss_id, b_score in sorted_bm25:
                if faiss_id not in self.metadata:
                    continue
                meta = self.metadata[faiss_id]
                if active_filter_ids and meta.get("document_id") not in active_filter_ids:
                    continue
                if b_score >= settings.BM25_MIN_SCORE:
                    bm25_results[faiss_id] = b_score
                    bm25_ranks[faiss_id] = rank
                    rank += 1

        # 3. Fusion & Ranking
        candidate_ids: Set[int] = set(dense_results.keys()) | set(bm25_results.keys())
        if not candidate_ids:
            return []

        scored_candidates = []
        for faiss_id in candidate_ids:
            meta = self.metadata[faiss_id]
            dense_s = dense_results.get(faiss_id, 0.0)
            bm25_s = bm25_results.get(faiss_id, 0.0)

            # RRF (Reciprocal Rank Fusion) with k=60
            dense_r = dense_ranks.get(faiss_id, 999)
            bm25_r = bm25_ranks.get(faiss_id, 999)
            rrf_score = (alpha / (60.0 + dense_r)) + ((1.0 - alpha) / (60.0 + bm25_r))

            # Calibrated composite relevance score in [0.0, 1.0]
            # Dense is already cosine similarity in [-1, 1], clamped to [0, 1]
            clamped_dense = max(0.0, min(1.0, dense_s))
            # BM25 is smooth-bounded via monotonic rational function x / (x + 5.0)
            norm_bm25 = (bm25_s / (bm25_s + 5.0)) if bm25_s > 0 else 0.0

            if mode == "dense":
                final_score = clamped_dense
                sort_key = dense_s
            elif mode == "bm25":
                final_score = norm_bm25
                sort_key = bm25_s
            else:  # hybrid
                final_score = alpha * clamped_dense + (1.0 - alpha) * norm_bm25
                sort_key = rrf_score

            if final_score < threshold and dense_s < threshold and norm_bm25 < threshold:
                continue

            scored_candidates.append({
                "chunk_id": meta.get("chunk_id"),
                "document_id": meta.get("document_id"),
                "document_name": meta.get("document_name"),
                "page_number": meta.get("page_number"),
                "passage_text": meta.get("content"),
                "similarity_score": round(final_score, 4),
                "dense_score": round(dense_s, 4),
                "bm25_score": round(bm25_s, 4),
                "rrf_score": round(rrf_score, 6),
                "source_type": meta.get("source_type", self.source_type),
                "retrieval_method": mode,
                "_sort_key": sort_key
            })

        # Sort descending by sort_key
        scored_candidates.sort(key=lambda x: x["_sort_key"], reverse=True)

        # Remove temporary sort key
        results = []
        for c in scored_candidates[:k]:
            c_dict = dict(c)
            c_dict.pop("_sort_key", None)
            results.append(c_dict)

        return results

    def delete_document(self, document_id: str):
        """Removes all chunks belonging to a document and rebuilds the indexes."""
        remaining_chunks = [
            meta for meta in self.metadata.values()
            if meta.get("document_id") != document_id
        ]
        
        self.clear()
        if remaining_chunks:
            self.add_chunks(remaining_chunks)
        else:
            self.save_index()

    def clear(self):
        """Resets both the FAISS index and BM25 index."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = {}
        self.bm25.clear()
        if self.index_path.exists():
            os.remove(self.index_path)
        if self.meta_path.exists():
            os.remove(self.meta_path)
        logger.info(f"Cleared Hybrid FAISS/BM25 index '{self.index_name}'.")

    def save_index(self):
        """Persists the FAISS index and its metadata to disk."""
        try:
            faiss.write_index(self.index, str(self.index_path))
            with open(self.meta_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")

    def load_index(self):
        """Loads index and metadata from disk and initializes BM25 inverted index."""
        if self.index_path.exists() and self.meta_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    raw_meta = json.load(f)
                    self.metadata = {int(k): v for k, v in raw_meta.items()}
                
                # Reconstruct BM25 index from loaded chunk metadata
                self.bm25.clear()
                for faiss_id, chunk_meta in self.metadata.items():
                    content = chunk_meta.get("content", "")
                    if content:
                        self.bm25.add_document(faiss_id, content)

                logger.info(
                    f"Loaded Hybrid index '{self.index_name}' with {self.index.ntotal} vectors "
                    f"and {self.bm25.total_docs} BM25 documents."
                )
            except Exception as e:
                logger.warning(f"Could not load index: {e}. Initializing fresh index.")
                self.index = faiss.IndexFlatIP(self.dimension)
                self.metadata = {}
                self.bm25.clear()

    def sync_with_db(self, db: Any) -> int:
        """
        Synchronizes this Hybrid FAISS/BM25 index with documents and chunks in SQLite.
        If the index is missing chunks, empty, or out-of-sync, it rebuilds and persists it.
        Returns the total number of active vectors in the index.
        """
        from backend.app.database.models import Document, DocumentChunk

        try:
            docs = db.query(Document).all()
        except Exception as e:
            logger.error(f"Cannot query documents from database for index synchronization: {e}")
            return self.index.ntotal

        if not docs:
            if self.index.ntotal > 0:
                logger.info(f"Database contains 0 documents. Clearing active index '{self.index_name}'.")
                self.clear()
            return 0

        all_db_chunks = []
        for doc in docs:
            chunks = (
                db.query(DocumentChunk)
                .filter(DocumentChunk.document_id == doc.id)
                .order_by(DocumentChunk.chunk_index)
                .all()
            )
            for c in chunks:
                all_db_chunks.append({
                    "chunk_id": c.id,
                    "document_id": doc.id,
                    "document_name": doc.filename,
                    "page_number": c.page_number or 1,
                    "content": c.content,
                    "source_type": self.source_type
                })

        # Check if the current in-memory index already contains all DB chunk IDs
        indexed_chunk_ids = {meta.get("chunk_id") for meta in self.metadata.values()}
        db_chunk_ids = {c["chunk_id"] for c in all_db_chunks}

        if indexed_chunk_ids == db_chunk_ids and self.index.ntotal == len(all_db_chunks):
            logger.debug(
                f"Hybrid index '{self.index_name}' is already fully synchronized with database "
                f"({self.index.ntotal} vectors across {len(docs)} documents)."
            )
            return self.index.ntotal

        # Re-index all chunks from database
        logger.info(
            f"Synchronizing Hybrid index '{self.index_name}' with SQLite: "
            f"found {len(all_db_chunks)} chunks across {len(docs)} documents (current indexed vectors: {self.index.ntotal}). Rebuilding..."
        )
        self.clear()
        if all_db_chunks:
            self.add_chunks(all_db_chunks)
            self.save_index()

        logger.info(
            f"Hybrid index '{self.index_name}' synchronization complete. "
            f"Active FAISS vectors: {self.index.ntotal}, BM25 documents: {self.bm25.total_docs}."
        )
        return self.index.ntotal


# Uploaded documents semantic/keyword retriever
retriever = SemanticRetriever(index_name="truthguard_evidence", source_type="document")

# FEVER Knowledge Base semantic/keyword retriever
fever_retriever = SemanticRetriever(index_name="fever_knowledge_base", source_type="fever")


def sync_documents_index(db: Any) -> int:
    """
    Synchronizes the active Hybrid FAISS/BM25 document index with SQLite.
    Returns total number of indexed vectors.
    """
    return retriever.sync_with_db(db)


def retrieve_multi_source(
    query: str,
    source: str = "documents",
    top_k: int = 5,
    filter_doc_ids: Optional[List[str]] = None,
    mode: str = "hybrid"
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Unified hybrid retrieval across Uploaded Documents, FEVER Knowledge Base, or Both.
    Combines dense semantic vector search with Okapi BM25 keyword matching via RRF.
    
    Returns:
        candidates: List[Dict[str, Any]] sorted by hybrid relevance
        empty_reason: "NO_DOCUMENTS_INDEXED" | "NO_DOCUMENTS_SELECTED" | "NO_EVIDENCE_RETRIEVED" | "EVIDENCE_ENTAILED"
    """
    # Active index metadata diagnostics
    active_index_name = "fever_knowledge_base" if source == "fever" else ("both" if source == "both" else "truthguard_evidence")
    active_vector_count = (
        fever_retriever.index.ntotal if source == "fever"
        else (retriever.index.ntotal + fever_retriever.index.ntotal if source == "both"
              else retriever.index.ntotal)
    )
    indexed_doc_count = len({m.get("document_id") for m in retriever.metadata.values()}) if source != "fever" else 570
    filter_repr = f"[{', '.join(filter_doc_ids)}]" if filter_doc_ids else "ALL"

    logger.info(
        f"[Retrieval Diagnosis] Initiating retrieval | Query: '{query[:80]}...' | "
        f"Corpus: '{source}' | Active Index: '{active_index_name}' | "
        f"Vectors in Index: {active_vector_count} | Indexed Documents: {indexed_doc_count} | "
        f"Document Filter: {filter_repr} | Mode: '{mode}'"
    )

    cands: List[Dict[str, Any]] = []
    reason: str = "NO_EVIDENCE_RETRIEVED"

    if source == "fever":
        cands = fever_retriever.retrieve(query=query, top_k=top_k, mode=mode)
        reason = fever_retriever.get_empty_reason() if not cands else "EVIDENCE_ENTAILED"

    elif source == "both":
        doc_cands = retriever.retrieve(query=query, top_k=top_k, filter_doc_ids=filter_doc_ids, mode=mode)
        fever_cands = fever_retriever.retrieve(query=query, top_k=top_k, mode=mode)
        
        # Merge and deduplicate by passage_text
        seen = set()
        combined = []
        for c in sorted(doc_cands + fever_cands, key=lambda x: x["similarity_score"], reverse=True):
            text_hash = hash(c["passage_text"][:100])
            if text_hash not in seen:
                seen.add(text_hash)
                combined.append(c)
            if len(combined) >= top_k:
                break

        if not combined:
            if retriever.index.ntotal == 0 and fever_retriever.index.ntotal == 0:
                cands, reason = [], "NO_DOCUMENTS_INDEXED"
            else:
                cands, reason = [], "NO_EVIDENCE_RETRIEVED"
        else:
            cands, reason = combined, "EVIDENCE_ENTAILED"

    else:  # "documents"
        cands = retriever.retrieve(query=query, top_k=top_k, filter_doc_ids=filter_doc_ids, mode=mode)
        reason = retriever.get_empty_reason(filter_doc_ids=filter_doc_ids) if not cands else "EVIDENCE_ENTAILED"

    # Diagnostic outcome reporting
    if cands:
        logger.info(
            f"[Retrieval Diagnosis] SUCCESS: Retrieved {len(cands)} passages | "
            f"Top Score: {cands[0]['similarity_score']:.4f} | "
            f"Source Doc: '{cands[0]['document_name']}' (p.{cands[0].get('page_number', 1)})"
        )
    else:
        logger.warning(
            f"[Retrieval Diagnosis] EMPTY: 0 passages retrieved | Reason: '{reason}' | "
            f"Corpus: '{source}' | Active Index: '{active_index_name}' ({active_vector_count} vectors)"
        )

    return cands, reason
