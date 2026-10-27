# TruthGuard: Troubleshooting & Operational Guide

## Common Issues & Resolutions

### 1. Ollama Offline or Model Missing
- **Symptom:** Ollama pill shows "Offline" in navbar, or `GET /api/v1/health` reports connection error.
- **Resolution:**
  1. Open a terminal and run `ollama serve` (or ensure the Ollama background daemon is running).
  2. Confirm your installed models: `ollama list`.
  3. If `qwen3:8b` or `qwen2.5:3b` is not installed, run:
     ```powershell
     ollama pull qwen3:8b
     # or fallback
     ollama pull qwen2.5:3b
     ```
  4. Note: Mode A (Verify Existing Answer) functions fully even if Ollama is temporarily offline!

### 2. Port Conflicts (8000 or 5173 in use)
- **Symptom:** `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)`.
- **Resolution:**
  ```powershell
  # Find PID using port 8000
  Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
  # Terminate conflicting PID
  Stop-Process -Id <PID> -Force
  ```

### 3. PyTorch CUDA / Memory Constraints
- **Target Hardware:** NVIDIA RTX 3050 Laptop GPU (4 GB VRAM).
- **Architecture Strategy:**
  - MiniLM (`all-MiniLM-L6-v2`) and DeBERTa (`nli-deberta-v3-small`) run on CPU threads.
  - Local LLM (`qwen3:8b`) runs in Ollama using ~2.4 GB VRAM on GPU.
  - This avoids GPU out-of-memory errors and prevents GPU thrashing.

### 4. PDF Ingestion: Digital vs Scanned PDFs
- TruthGuard uses PyMuPDF (`fitz`) for digital text extraction and page tracking.
- Scanned image-only PDFs without an embedded text layer will be detected and rejected with a clear message: `"PDF contains no readable digital text. Scanned PDFs require an OCR pre-processing step."`
