import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from backend.app.core.config import settings
from backend.app.core.logging import logger


class EmbeddingEngine:
    """Manages sentence embedding generation using SentenceTransformer."""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingEngine, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME} on device: {settings.EMBEDDING_DEVICE}")
            try:
                # Attempt offline cache load first to avoid network latency/SSL issues
                cls._model = SentenceTransformer(
                    settings.EMBEDDING_MODEL_NAME,
                    device=settings.EMBEDDING_DEVICE,
                    local_files_only=True
                )
            except Exception:
                try:
                    cls._model = SentenceTransformer(
                        settings.EMBEDDING_MODEL_NAME,
                        device=settings.EMBEDDING_DEVICE
                    )
                except Exception as e:
                    logger.error(f"Failed to load embedding model on {settings.EMBEDDING_DEVICE}: {e}. Retrying on cpu...")
                    cls._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, device="cpu", local_files_only=True)
        return cls._model

    @classmethod
    def unload_model(cls):
        """Frees model from memory when required."""
        if cls._model is not None:
            logger.info("Unloading embedding model to free memory.")
            del cls._model
            cls._model = None

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = None,
        normalize_embeddings: bool = True
    ) -> np.ndarray:
        """
        Generates dense vector embeddings.
        If normalize_embeddings is True, returns L2-normalized vectors so that
        the dot product between vectors equals their cosine similarity.
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, settings.EMBEDDING_DIM), dtype=np.float32)

        model = self.get_model()
        bs = batch_size or settings.EMBEDDING_BATCH_SIZE

        embeddings = model.encode(
            texts,
            batch_size=bs,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=normalize_embeddings
        )

        return embeddings.astype(np.float32)


embedding_engine = EmbeddingEngine()
