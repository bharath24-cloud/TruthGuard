from fastapi import APIRouter
import torch
import psutil
from backend.app.core.config import settings
from backend.app.services.ollama_service import ollama_service

router = APIRouter()


@router.get("/health")
def get_health_status():
    ollama_ok, ollama_msg = ollama_service.check_health()
    
    cuda_available = torch.cuda.is_available()
    device_info = {
        "cuda_available": cuda_available,
        "device_count": torch.cuda.device_count() if cuda_available else 0,
        "device_name": torch.cuda.get_device_name(0) if cuda_available else "CPU",
        "active_device": settings.DEVICE,
        "nli_device": settings.NLI_DEVICE,
        "embedding_device": settings.EMBEDDING_DEVICE
    }

    mem = psutil.virtual_memory()
    memory_info = {
        "total_gb": round(mem.total / (1024 ** 3), 2),
        "available_gb": round(mem.available / (1024 ** 3), 2),
        "used_percent": mem.percent
    }

    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ollama": {
            "status": "online" if ollama_ok else "offline",
            "message": ollama_msg,
            "base_url": settings.OLLAMA_BASE_URL,
            "default_model": settings.DEFAULT_LLM_MODEL
        },
        "hardware": device_info,
        "system_memory": memory_info,
        "models": {
            "embedding_model": settings.EMBEDDING_MODEL_NAME,
            "nli_model": settings.NLI_MODEL_NAME
        }
    }
