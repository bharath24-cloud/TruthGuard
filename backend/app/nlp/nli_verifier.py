from typing import List, Tuple, Dict, Any, Union
import numpy as np
from sentence_transformers import CrossEncoder
from backend.app.core.config import settings
from backend.app.core.logging import logger


class NLIVerifier:
    """
    Natural Language Inference (NLI) engine using cross-encoder/nli-deberta-v3-small.
    Classifies relationship between (evidence_premise, claim_hypothesis):
      - 0: contradiction
      - 1: entailment
      - 2: neutral
    """

    _instance = None
    _model = None

    # Verified label mapping for cross-encoder/nli-deberta-v3-small
    LABEL_MAPPING = {
        0: "contradiction",
        1: "entailment",
        2: "neutral"
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NLIVerifier, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_model(cls) -> CrossEncoder:
        if cls._model is None:
            logger.info(f"Loading NLI model: {settings.NLI_MODEL_NAME} on device: {settings.NLI_DEVICE}")
            try:
                # Attempt offline cache load first
                cls._model = CrossEncoder(
                    settings.NLI_MODEL_NAME,
                    device=settings.NLI_DEVICE,
                    max_length=512,
                    local_files_only=True
                )
            except Exception:
                try:
                    cls._model = CrossEncoder(
                        settings.NLI_MODEL_NAME,
                        device=settings.NLI_DEVICE,
                        max_length=512
                    )
                except Exception as e:
                    logger.error(f"Failed to load NLI model on {settings.NLI_DEVICE}: {e}. Retrying on cpu...")
                    cls._model = CrossEncoder(settings.NLI_MODEL_NAME, device="cpu", max_length=512, local_files_only=True)
        return cls._model

    @classmethod
    def unload_model(cls):
        """Unloads model to free memory if needed."""
        if cls._model is not None:
            logger.info("Unloading NLI model to free memory.")
            del cls._model
            cls._model = None

    def predict_pair(self, evidence: str, claim: str) -> Dict[str, Any]:
        """
        Runs NLI inference on a single (evidence, claim) pair.
        Evidence is the premise; Claim is the hypothesis.
        """
        results = self.predict_batch([(evidence, claim)])
        return results[0]

    def predict_batch(self, pairs: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """
        Runs batched NLI inference on a list of [(evidence, claim), ...].
        Returns class probabilities and predicted label for each pair.
        """
        if not pairs:
            return []

        model = self.get_model()
        # Formatted pairs: [[premise, hypothesis], ...]
        formatted_pairs = [[p[0], p[1]] for p in pairs]

        # CrossEncoder outputs raw logits of shape (N, 3)
        logits = model.predict(
            formatted_pairs,
            batch_size=settings.NLI_BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True
        )

        # Apply numerically stable softmax
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)

        results = []
        for i, row in enumerate(probs):
            contradiction_p = float(row[0])
            entailment_p = float(row[1])
            neutral_p = float(row[2])

            # Classify based on thresholds
            if entailment_p >= settings.ENTAILMENT_THRESHOLD and entailment_p > contradiction_p:
                label = "entailment"
                confidence = entailment_p
            elif contradiction_p >= settings.CONTRADICTION_THRESHOLD and contradiction_p > entailment_p:
                label = "contradiction"
                confidence = contradiction_p
            else:
                label = "neutral"
                confidence = neutral_p

            results.append({
                "nli_label": label,
                "confidence": round(confidence, 4),
                "entailment_prob": round(entailment_p, 4),
                "contradiction_prob": round(contradiction_p, 4),
                "neutral_prob": round(neutral_p, 4),
                "model_name": settings.NLI_MODEL_NAME
            })

        return results


nli_verifier = NLIVerifier()
