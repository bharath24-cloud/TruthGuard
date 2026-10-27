from fastapi import APIRouter
from backend.app.services.ollama_service import ollama_service
from backend.app.core.config import settings

router = APIRouter()


@router.get("/models")
def list_available_models():
    models = ollama_service.list_models()
    return {
        "models": models,
        "default_model": settings.DEFAULT_LLM_MODEL,
        "fallback_model": settings.FALLBACK_LLM_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "nli_model": settings.NLI_MODEL_NAME
    }
