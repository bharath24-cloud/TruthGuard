# TruthGuard REST API Reference

All version 1 endpoints are prefixed with `/api/v1`.

## Endpoints

### 1. Health & Telemetry
- `GET /api/v1/health`
  - Returns backend status, Ollama online/offline state, GPU/CPU telemetry, memory usage, and loaded NLP models.

### 2. Model Discovery
- `GET /api/v1/models`
  - Returns installed Ollama models, default model, and NLI/embedding identifiers.

### 3. Text Generation
- `POST /api/v1/generate`
  - Request: `{"prompt": str, "model": Optional[str], "temperature": float, "max_tokens": int}`
  - Response: `{"prompt": str, "response": str, "model": str}`

### 4. Atomic Claim Extraction
- `POST /api/v1/claims/extract`
  - Request: `{"text": str, "context_question": Optional[str]}`
  - Response: `{"total_claims": int, "verifiable_claims": int, "claims": [AtomicClaimItem]}`

### 5. Verification Pipeline
- `POST /api/v1/verify`
  - Request: `{"question": str, "answer": Optional[str], "model_name": Optional[str], "document_ids": Optional[List[str]], "top_k": int}`
  - Response: `VerificationReportResponse` (claims, verdicts, confidence, evidence passages with offsets and pages, hallucination score).
- `GET /api/v1/verifications`
  - List historical verification runs.
- `GET /api/v1/verifications/{id}`
  - Retrieve detailed historical report by ID.

### 6. Evidence-Grounded Correction
- `POST /api/v1/correct`
  - Request: `{"verification_id": str, "model_name": Optional[str], "temperature": float}`
  - Response: `CorrectionResponse` (original vs corrected answer, reverified claims audit, confirmation of 0 contradictions).

### 7. Document Library Management
- `POST /api/v1/documents/upload`
  - Multipart form upload (`.pdf`, `.txt`, `.md`).
  - Chunks text, computes embeddings, indexes in FAISS, and persists metadata.
- `GET /api/v1/documents`
  - Lists all ingested documents.
- `GET /api/v1/documents/{id}/chunks`
  - Inspect indexed chunks with character offsets and page references.
- `DELETE /api/v1/documents/{id}`
  - Removes document from database and FAISS index.

### 8. Benchmark Evaluation Lab
- `POST /api/v1/evaluations/run`
  - Request: `{"benchmark_name": "FEVER" | "HaluEval" | "TruthfulQA", "sample_size": int, "top_k": int}`
  - Response: `EvaluationExperimentSchema` (Accuracy, Precision, Recall, Macro F1, Recall@K, Confusion Matrix).
- `GET /api/v1/evaluations`
  - History of benchmark runs.
