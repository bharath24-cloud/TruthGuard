# TruthGuard

> **An Explainable NLP Framework for Hallucination Detection, Multi-Source Evidence Verification, and Automatic Correction of Large Language Model Responses**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.3-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS v4](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Overview & Core Mission

**TruthGuard** is a research-grade, locally executable NLP framework developed to identify unsupported or fabricated claims in Large Language Model (LLM) responses, retrieve ground truth reference passages from document corpora, perform Natural Language Inference (NLI), provide explainable verification rationales, and execute automatic evidence-grounded corrections.

### Strict Scientific Guarantees
- **Real Pretrained NLP Models:** Uses `cross-encoder/nli-deberta-v3-small` for inference and `sentence-transformers/all-MiniLM-L6-v2` for dense semantic embeddings.
- **Zero Simulation:** Zero fake citations, zero hardcoded hallucination percentages, zero mock verification verdicts.
- **Distinction Between Unsupported and Contradicted:** Unsupported statements (unverified due to missing evidence) are explicitly distinguished from demonstrably false statements (contradicted by evidence).
- **Offline Capable:** Runs entirely locally without mandatory cloud services, paid APIs, or OpenAI dependencies.
- **Hardware-Aware Design:** Optimized for 4 GB VRAM laptops (NVIDIA RTX 3050 Laptop GPU / CPU fallback).

---

## 2. System Architecture

```
User Question / Existing LLM Answer
                   ↓
Input Validation & Mode Selection (Mode A vs Mode B)
                   ↓
Atomic Claim Extraction (Syntactic NLP & LLM decomposition with span tracking)
                   ↓
Semantic Evidence Retrieval (MiniLM-L6 + FAISS IndexFlatIP Cosine Similarity)
                   ↓
Natural Language Inference (Cross-Encoder DeBERTa-v3-small Softmax Probabilities)
                   ↓
Multi-Evidence Aggregator (Threshold arbitration: Supported, Contradicted, Conflicting, Insufficient)
                   ↓
Hallucination Risk Scorer (Documented mathematical risk formula bounded [0.0, 1.0])
                   ↓
Explainability Engine (Grounded citation rationales with document & page provenance)
                   ↓
Evidence-Grounded Correction Engine (Context-constrained LLM generation)
                   ↓
Closed-Loop Reverification (Audit of corrected response to ensure 0 remaining contradictions)
                   ↓
React Modern Dashboard & SQLite Persistence
```

---

## 3. Technology Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic v2, PyTorch, Hugging Face Transformers, Sentence Transformers, FAISS, PyMuPDF, SQLite, SQLAlchemy, Ollama HTTP API, scikit-learn.
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS v4, Lucide Icons, Recharts, TanStack Query.
- **Local Models:**
  - Local LLM: `qwen3:8b` via Ollama (fallback `qwen2.5:3b`).
  - Semantic Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional).
  - Natural Language Inference: `cross-encoder/nli-deberta-v3-small` (Labels: `0: contradiction`, `1: entailment`, `2: neutral`).

---

## 4. FEVER Benchmark Dataset & Knowledge Base Integration

TruthGuard features native, leak-free integration with the official **FEVER** (Fact Extraction and VERification) benchmark dataset ([fever.ai](https://fever.ai/dataset/fever.html)).

### Strict Role Separation & Zero-Leakage Policy
- **Verification Examples:** Stored in `datasets/fever/prepared/`. Claims, gold labels (`SUPPORTED`, `REFUTED`, `NOT_ENOUGH_INFO`), and gold evidence annotations are kept strictly separate from the retrieval corpus.
- **Evidence Corpus:** Stored in the dedicated FAISS index `data/indexes/fever_knowledge_base.faiss` and metadata `data/indexes/fever_knowledge_base.json`. Contains actual Wikipedia article text resolved into atomic sentence chunks.
- **Zero Information Leakage:** Gold labels and gold evidence pointers are strictly withheld from the system during verification. Evidence retrieval is performed purely via semantic vector similarity over the knowledge base, exactly mirroring real-world conditions.

### Label Normalization
FEVER labels are automatically normalized into TruthGuard's verified taxonomy:
- `SUPPORTS` → `SUPPORTED`
- `REFUTES` → `REFUTED`
- `NOT ENOUGH INFO` → `NOT_ENOUGH_INFO`

### Calibration & Honest Failure Handling
When no evidence is retrieved from the knowledge base, TruthGuard returns:
- **Verdict:** `Insufficient Evidence`
- **Confidence:** `null` (displayed as `N/A (No Evidence)`)
- **Calibrated Flag:** `false`
- **Inference Reason:** `NO_EVIDENCE_RETRIEVED` (or `NO_DOCUMENTS_INDEXED`)

No artificial or misleading 0.0% confidence scores are ever presented to the user.

---

## 5. FEVER CLI Tools & Workflow (Windows PowerShell)

All FEVER operations are accessible via modular Python CLI tools:

### 1. Download & Prepare FEVER Dataset
Downloads the official FEVER split (`paper_dev.jsonl` from `https://fever.ai/download/fever/`), validates schema, cleans Wikipedia title encodings, normalizes labels, deduplicates, and generates a reproducible balanced sample:
```powershell
python -m experiments.prepare_fever --split paper_dev --limit 1000 --seed 42
```
*Outputs: `datasets/fever/prepared/fever_paper_dev_1000.jsonl` and metadata summary.*

### 2. Build the FEVER Knowledge Base FAISS Index
Extracts unique Wikipedia article titles from the prepared dataset, downloads verified Wikipedia article texts (with local disk caching in `data/fever_cache/wiki_articles/`), segments text into sentences, computes 384-d MiniLM dense embeddings, and builds a dedicated FAISS index:
```powershell
python -m experiments.index_fever_evidence --sample-file datasets/fever/prepared/fever_paper_dev_1000.jsonl --limit-articles 50 --batch-size 32
```
*Outputs: `data/indexes/fever_knowledge_base.faiss` and `data/indexes/fever_knowledge_base.json`.*

### 3. Run Leak-Free FEVER Evaluation Benchmark
Executes end-to-end evaluation comparing system predictions against gold labels without gold evidence leakage:
```powershell
python -m experiments.evaluate_fever --evidence-source fever --limit 50 --output experiments/fever_eval_results.json
```
*Outputs: Precision, Recall, Macro F1, Accuracy, Latency per sample, and detailed Confusion Matrix.*

---

## 6. Using FEVER in the Web Dashboard

### 1. Dataset & Knowledge Base Manager (`EvaluationLab.tsx`)
Navigate to the **Evaluation Lab** page (`http://localhost:5173/evaluation`):
- View live FEVER status: download status, available splits, sample counts, class distributions, and index vector counts.
- Click **Prepare 1,000 Sample** to automatically ingest and normalize the official FEVER split.
- Click **Build Evidence Index** to build or update the FAISS vector index.
- Run automated benchmarks across user-selectable sample sizes and view live accuracy, F1, and latency breakdowns.

### 2. Multi-Source Evidence Verification (`VerifyAnswer.tsx`)
Navigate to the **Verify Answer** page (`http://localhost:5173/`):
- Use the **Evidence Knowledge Base** selector pill to route retrieval:
  - **Uploaded Documents:** Retrieve strictly from documents uploaded to your private Document Library.
  - **FEVER Knowledge Base:** Retrieve strictly from the indexed FEVER Wikipedia knowledge base.
  - **Both:** Perform hybrid multi-source retrieval, pooling and deduplicating evidence across both sources.
- Visual evidence cards display origin tags: `[FEVER]` or `[Document]` alongside page/sentence provenance and similarity scores.

---

## 7. Empirical Evaluation Benchmark Results

Empirical evaluation executed on local hardware using `cross-encoder/nli-deberta-v3-small` and `sentence-transformers/all-MiniLM-L6-v2`:

### Benchmark: FEVER Validation Set (Zero-Leakage Semantic Retrieval)
| Metric | Measured Score | Explanation |
|---|---|---|
| **Accuracy** | **40.0%** | Multi-class accuracy over 3-class FEVER subset |
| **Precision** | **40.0%** | Macro-averaged precision across all 3 classes |
| **Recall** | **44.4%** | Macro-averaged recall across classes |
| **Macro F1** | **0.1905** | Real measured Macro F1 without gold-passage hints |
| **Average Latency** | **1,288 ms** | Total pipeline latency per sample (retrieval + NLI) |

> **Research Integrity Note:** In real-world zero-leakage evaluation, retrieval is performed over the open knowledge base without injecting gold passages. Performance strictly reflects actual semantic retrieval and NLI inference capabilities.

---

## 8. Hardware Optimization (Target: NVIDIA RTX 3050 4GB Laptop GPU)

To ensure smooth operation on 4 GB VRAM mobile GPUs without CUDA Out-Of-Memory (OOM) errors:
- **Local LLM (`qwen3:8b` via Ollama):** Allocated to GPU (~2.4 GB VRAM footprint).
- **NLI Model (`nli-deberta-v3-small`) & Embedding Model (`all-MiniLM-L6-v2`):** Defaulted to `device="cpu"` (`NLI_DEVICE=cpu`, `EMBEDDING_DEVICE=cpu`).
- This strategic partitioning prevents GPU memory thrashing and eliminates CUDA OOM errors while delivering sub-second inference latencies.

---

## 9. Quickstart Guide (Windows PowerShell)

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Ollama (installed with `qwen3:8b` or `qwen2.5:3b`)

### 1. Clone & Setup Workspace
```powershell
cd c:\Users\sesha\OneDrive\Desktop\TRUTHGUARD
```

### 2. Backend Installation & Startup
```powershell
# Install Python dependencies
python -m pip install -r backend/requirements.txt

# Start FastAPI backend server (Runs on port 8000)
python -u -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

### 3. Frontend Installation & Startup
In a separate PowerShell window:
```powershell
cd c:\Users\sesha\OneDrive\Desktop\TRUTHGUARD\frontend

# Install dependencies
npm install

# Start Vite React dashboard (Runs on port 5173)
npm run dev
```

### 4. Access Application
Open your browser and navigate to:
```
http://localhost:5173/
```
Interactive API documentation is accessible at:
```
http://127.0.0.1:8000/docs
```

---

## 10. End-to-End Automated Validation

To execute the automated end-to-end verification pipeline (document upload, claim extraction, NLI inference, grounded correction, reverification audit, and FEVER benchmark evaluation):

```powershell
python scripts/validate_e2e.py
```

Results are saved to `experiments/validation_run_report.json`.

---

## 7. Project Structure

```
TRUTHGUARD/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & lifecycle
│   │   ├── api/
│   │   │   ├── router.py            # Unified v1 API router
│   │   │   └── v1/                  # Versioned endpoints (health, verify, correct, docs, eval)
│   │   ├── core/                    # Settings (config.py) and logging (logging.py)
│   │   ├── database/                # SQLAlchemy models and SQLite session
│   │   ├── ingestion/               # PyMuPDF PDF parser and recursive chunker
│   │   ├── nlp/                     # Core NLP algorithms
│   │   │   ├── claim_extractor.py   # Atomic claim decomposition & span tracker
│   │   │   ├── embeddings.py        # SentenceTransformer unit-normalized embeddings
│   │   │   ├── retriever.py         # FAISS IndexFlatIP cosine similarity index
│   │   │   ├── nli_verifier.py      # DeBERTa-v3-small cross-encoder inference
│   │   │   ├── evidence_aggregator.py # Multi-evidence conflict arbitration
│   │   │   ├── hallucination_scorer.py # Mathematical risk scoring
│   │   │   ├── explanation_engine.py  # Grounded rationale generator
│   │   │   └── correction_engine.py   # Grounded correction & reverification
│   │   ├── schemas/                 # Pydantic v2 schemas
│   │   └── services/                # Orchestration services (Ollama, Verification, Eval)
│   ├── tests/                       # Unit & integration test suite (pytest)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/Navbar.tsx    # Header & telemetry pills
│   │   ├── pages/                   # 6 Core SaaS Pages
│   │   │   ├── Dashboard.tsx        # Overview & distribution charts
│   │   │   ├── VerifyAnswer.tsx     # Mode A & B, interactive claims, side-by-side correction
│   │   │   ├── DocumentLibrary.tsx  # Drag & drop upload, chunk inspector
│   │   │   ├── VerificationHistory.tsx # Searchable past audits & export
│   │   │   ├── EvaluationLab.tsx    # FEVER / HaluEval / TruthfulQA benchmark runner
│   │   │   └── Settings.tsx         # Hyperparameters & Ollama configuration
│   │   ├── services/api.ts          # Type-safe API client
│   │   └── types/index.ts           # Unified TypeScript definitions
│   ├── vite.config.ts
│   └── package.json
├── datasets/benchmark_samples/      # FEVER, HaluEval, TruthfulQA curated samples
├── experiments/                     # Experimental validation reports
├── docs/                            # In-depth architectural & evaluation docs
├── .env.example
├── pytest.ini
└── README.md
```

---

## 8. Research Limitations & Future Work

1. **Scanned PDF Ingestion:** Scanned image-only PDFs currently require an OCR preprocessing step before ingestion. Future work will integrate an OCR pipeline.
2. **Multi-Hop Reasoning:** When a claim requires synthesizing multiple disparate facts across multiple documents, current evidence retrieval relies on single-step top-$K$ search. Multi-hop iterative retrieval will be explored in version 2.0.
3. **Calibrated Confidence:** While NLI softmax outputs provide strong separation, conformal prediction techniques can be applied for calibrated error bounds.
