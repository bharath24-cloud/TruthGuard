from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.app.core.logging import logger
from backend.app.core.config import settings
from backend.app.services.ollama_service import ollama_service, GenerationTimeoutError

router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    model: Optional[str] = None
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 512


@router.post("/generate")
def generate_response(req: GenerateRequest):
    try:
        response_text = ollama_service.generate(
            prompt=req.prompt,
            model=req.model,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            timeout=settings.OLLAMA_GENERATION_TIMEOUT,
            think=False
        )
        return {
            "prompt": req.prompt,
            "response": response_text,
            "model": req.model or "default"
        }
    except (GenerationTimeoutError, TimeoutError) as e:
        logger.error(f"Generation endpoint timed out: {e}")
        raise HTTPException(
            status_code=504,
            detail=f"Model generation timed out: {str(e)}. Please retry with a shorter prompt or lower max_tokens."
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Generation failed: {str(e)}")
