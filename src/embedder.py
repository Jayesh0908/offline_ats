"""
embedder.py — Sentence Embedding Module

Generates semantic embeddings for resume text and job descriptions
using the all-MiniLM-L6-v2 model via sentence-transformers.

Embeddings are 384-dimensional float32 vectors stored in SQLite as BLOBs.
"""

import numpy as np
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global model cache
_embedding_model = None
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def load_embedding_model():
    """
    Load the all-MiniLM-L6-v2 sentence-transformers model.

    Model is downloaded on first call (~80 MB) and cached locally.
    Subsequent calls return the cached instance.

    Returns:
        SentenceTransformer model instance.
    """
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    try:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info(f"Embedding model loaded: {EMBEDDING_MODEL_NAME}")
        return _embedding_model
    except ImportError:
        raise ImportError(
            "sentence-transformers is not installed. "
            "Run: pip install sentence-transformers"
        )


def embed_text(text: str, model) -> np.ndarray:
    """
    Generate a 384-dimensional semantic embedding for the input text.

    Args:
        text: Any string — resume text or job description.
        model: Loaded SentenceTransformer model instance.

    Returns:
        numpy float32 array of shape (384,).
    """
    if not text or not text.strip():
        # Return zero vector for empty input
        return np.zeros(384, dtype=np.float32)

    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding.astype(np.float32)


def serialize_embedding(embedding: np.ndarray) -> bytes:
    """
    Serialize a numpy float32 array to bytes for SQLite BLOB storage.

    Args:
        embedding: numpy float32 array of shape (384,).

    Returns:
        Raw bytes (1536 bytes for 384 float32 values).
    """
    return embedding.astype(np.float32).tobytes()


def deserialize_embedding(blob: bytes) -> np.ndarray:
    """
    Deserialize bytes from SQLite BLOB back to a numpy float32 array.

    Args:
        blob: Raw bytes from SQLite BLOB column.

    Returns:
        numpy float32 array of shape (384,).
    """
    return np.frombuffer(blob, dtype=np.float32)
