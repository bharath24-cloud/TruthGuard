import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
import torch

# Base project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
INDEXES_DIR = DATA_DIR / "indexes"
DATASETS_DIR = PROJECT_ROOT / "datasets"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
INDEXES_DIR.mkdir(parents=True, exist_ok=True)
DATASETS_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "TruthGuard"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'truthguard.db'}"
    
    # Hardware & Device Execution
    FORCE_CPU: bool = False
    DEVICE: str = "cuda" if torch.cuda.is_available() and not os.environ.get("FORCE_CPU") else "cpu"
    NLI_DEVICE: str = "cpu"  # Keep NLI on CPU to preserve 4GB VRAM for Ollama
    EMBEDDING_DEVICE: str = "cpu"  # Keep MiniLM on CPU to prevent VRAM thrashing
    
    # Ollama Local LLM
    OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    DEFAULT_LLM_MODEL: str = os.environ.get("DEFAULT_LLM_MODEL", "qwen3:8b")
    FALLBACK_LLM_MODEL: str = os.environ.get("FALLBACK_LLM_MODEL", "qwen2.5:3b")
    OLLAMA_TIMEOUT: float = 120.0
    OLLAMA_GENERATION_TIMEOUT: float = 120.0
    OLLAMA_FAST_TIMEOUT: float = 15.0
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 1024
    MODE_B_MAX_TOKENS: int = 200
    OLLAMA_THINK: bool = False
    
    # Embeddings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    EMBEDDING_BATCH_SIZE: int = 32
    
    # NLI Cross-Encoder
    NLI_MODEL_NAME: str = "cross-encoder/nli-deberta-v3-small"
    NLI_BATCH_SIZE: int = 16
    
    # Verification Decision Thresholds
    ENTAILMENT_THRESHOLD: float = 0.55
    CONTRADICTION_THRESHOLD: float = 0.50
    NEUTRAL_AMBIGUITY_MARGIN: float = 0.15
    
    # Retrieval Configuration
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.25
    RETRIEVAL_HYBRID_ALPHA: float = 0.65  # 0.65 dense semantic + 0.35 BM25 keyword
    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    BM25_MIN_SCORE: float = 0.05
    
    # Ingestion & Chunking
    CHUNK_SIZE: int = 500  # characters
    CHUNK_OVERLAP: int = 100  # characters
    
    # Directories
    DATA_PATH: Path = DATA_DIR
    UPLOADS_PATH: Path = UPLOADS_DIR
    INDEXES_PATH: Path = INDEXES_DIR
    DATASETS_PATH: Path = DATASETS_DIR
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
