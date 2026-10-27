import json
import re
import socket
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional, Tuple
from backend.app.core.config import settings
from backend.app.core.logging import logger


class GenerationTimeoutError(TimeoutError):
    """Raised when model generation exceeds the allotted HTTP/socket timeout."""
    pass


class OllamaService:
    """Client for local Ollama HTTP API with health checks, model discovery, and structured generation."""

    def __init__(self, base_url: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")

    def check_health(self) -> Tuple[bool, str]:
        """Returns (is_available, status_message)."""
        url = f"{self.base_url}/api/tags"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    return True, "Ollama service is online"
                return False, f"Ollama returned HTTP status {response.status}"
        except urllib.error.URLError as e:
            return False, f"Cannot connect to Ollama at {self.base_url}: {e.reason}"
        except Exception as e:
            return False, f"Ollama connection error: {str(e)}"

    def list_models(self) -> List[Dict[str, Any]]:
        """Returns list of installed local models."""
        url = f"{self.base_url}/api/tags"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                models = []
                for m in data.get("models", []):
                    models.append({
                        "name": m.get("name"),
                        "size": m.get("size", 0),
                        "modified_at": m.get("modified_at", ""),
                        "parameter_size": m.get("details", {}).get("parameter_size", "unknown"),
                        "quantization": m.get("details", {}).get("quantization_level", "unknown")
                    })
                return models
        except Exception as e:
            logger.warning(f"Failed to list Ollama models: {e}")
            return []

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        think: Optional[bool] = None
    ) -> str:
        """Generates text from the local LLM. Cleans any chain-of-thought blocks if present."""
        target_model = model or settings.DEFAULT_LLM_MODEL
        url = f"{self.base_url}/api/generate"

        payload: Dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "think": think if think is not None else settings.OLLAMA_THINK,
            "options": {
                "temperature": temperature if temperature is not None else settings.LLM_TEMPERATURE,
                "num_predict": max_tokens or settings.LLM_MAX_TOKENS
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        req_timeout = timeout or settings.OLLAMA_TIMEOUT
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=req_timeout) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                raw_text = res_json.get("response", "").strip()
                # If response field is empty but thinking was produced, fallback to thinking block
                if not raw_text and res_json.get("thinking"):
                    raw_text = res_json.get("thinking", "").strip()

                # If the model produced <think> tags (like Qwen3 or DeepSeek), remove internal thinking
                cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
                return cleaned if cleaned else raw_text
        except (TimeoutError, socket.timeout) as e:
            logger.error(f"Ollama generation timed out after {req_timeout:.1f}s: {e}")
            raise GenerationTimeoutError(f"Model generation timed out after {req_timeout:.1f}s.") from e
        except urllib.error.URLError as e:
            # Check if inner reason was a timeout
            reason = getattr(e, "reason", None)
            if isinstance(reason, (TimeoutError, socket.timeout)) or "timed out" in str(e).lower():
                logger.error(f"Ollama request timed out after {req_timeout:.1f}s: {e}")
                raise GenerationTimeoutError(f"Model generation timed out after {req_timeout:.1f}s.") from e
            logger.error(f"Ollama request failed: {e}")
            raise RuntimeError(f"Ollama connection error: {e}") from e
        except Exception as e:
            if "timed out" in str(e).lower():
                logger.error(f"Ollama generation timed out after {req_timeout:.1f}s: {e}")
                raise GenerationTimeoutError(f"Model generation timed out after {req_timeout:.1f}s.") from e
            logger.error(f"Generation error: {e}")
            raise


    def verify_nli(
        self,
        premise: str,
        hypothesis: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Uses local Ollama LLM to perform natural language inference:
        Returns:
            {"nli_label": "entailment" | "contradiction" | "neutral", "explanation": str}
        """
        system_prompt = (
            "You are a factual verification judge. Analyze whether the HYPOTHESIS is entailed, "
            "contradicted, or neutral given the PREMISE. Output ONLY a valid JSON object:\n"
            "{\"verdict\": \"entailment\" | \"contradiction\" | \"neutral\", \"explanation\": \"brief explanation\"}"
        )
        user_prompt = f"PREMISE:\n{premise}\n\nHYPOTHESIS:\n{hypothesis}\n\nJSON Verdict:"
        try:
            resp = self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=model,
                temperature=0.0,
                max_tokens=256,
                timeout=30.0
            )
            # Parse JSON
            match = re.search(r"\{.*?\}", resp, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                verdict = str(data.get("verdict", "neutral")).lower().strip()
                if verdict not in ["entailment", "contradiction", "neutral"]:
                    if "entail" in verdict or "support" in verdict:
                        verdict = "entailment"
                    elif "contra" in verdict or "refut" in verdict:
                        verdict = "contradiction"
                    else:
                        verdict = "neutral"
                return {
                    "nli_label": verdict,
                    "explanation": data.get("explanation", ""),
                    "raw_response": resp
                }
            # Fallback heuristic if not valid JSON
            lower = resp.lower()
            if "entailment" in lower or "supports" in lower:
                lbl = "entailment"
            elif "contradiction" in lower or "refutes" in lower:
                lbl = "contradiction"
            else:
                lbl = "neutral"
            return {"nli_label": lbl, "explanation": resp[:120], "raw_response": resp}
        except Exception as e:
            logger.warning(f"Ollama NLI verification failed: {e}")
            return {"nli_label": "neutral", "explanation": f"LLM error: {str(e)}", "error": str(e)}


ollama_service = OllamaService()
