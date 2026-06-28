"""
Embedding generation using sentence-transformers.
Creates embeddings for resume text and job descriptions.
"""
import numpy as np
from typing import List, Optional, Union
from sentence_transformers import SentenceTransformer
import config


class Embedder:
    """Handles embedding generation for text data."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the sentence-transformers model."""
        try:
            print(f"[Embedder] Loading model: {config.EMBEDDING_MODEL}")
            self._model = SentenceTransformer(
                config.EMBEDDING_MODEL,
                cache_folder=str(config.EMBEDDING_CACHE_DIR)
            )
            print(f"[Embedder] Model loaded successfully. "
                  f"Embedding dimension: {self._model.get_sentence_embedding_dimension()}")
        except Exception as e:
            print(f"[Embedder] Error loading model: {e}")
            self._model = None
    
    def encode(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Numpy array of embedding vector
        """
        if self._model is None:
            print("[Embedder] Model not loaded, returning zero vector")
            return np.zeros(384, dtype=np.float32)
        
        if not text or not text.strip():
            return np.zeros(384, dtype=np.float32)
        
        embedding = self._model.encode(text, normalize_embeddings=True)
        return embedding.astype(np.float32)
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            2D numpy array of embedding vectors
        """
        if self._model is None:
            print("[Embedder] Model not loaded, returning zero vectors")
            return np.zeros((len(texts), 384), dtype=np.float32)
        
        valid_texts = [t if t and t.strip() else " " for t in texts]
        embeddings = self._model.encode(valid_texts, normalize_embeddings=True)
        return embeddings.astype(np.float32)
    
    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding vector
            emb2: Second embedding vector
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        if emb1.ndim == 1:
            emb1 = emb1.reshape(1, -1)
        if emb2.ndim == 1:
            emb2 = emb2.reshape(1, -1)
        
        # Cosine similarity for normalized vectors is just dot product
        similarity = float(np.dot(emb1, emb2.T).flatten()[0])
        return max(0.0, min(1.0, similarity))
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        if self._model is not None:
            return self._model.get_sentence_embedding_dimension()
        return 384  # Default for all-MiniLM-L6-v2


def create_resume_embedding(resume_text: str, skills: List[str] = None) -> np.ndarray:
    """
    Create an embedding for a resume.
    Uses the full resume text combined with skills for better representation.
    
    Args:
        resume_text: Full text of the resume
        skills: List of skills (optional, for enhanced embedding)
        
    Returns:
        Embedding vector
    """
    embedder = Embedder()
    
    # Combine resume text with skills for better representation
    text_for_embedding = resume_text
    if skills:
        skills_text = "Skills: " + ", ".join(skills)
        text_for_embedding = f"{resume_text}\n\n{skills_text}"
    
    return embedder.encode(text_for_embedding)


def create_jd_embedding(job_description: str) -> np.ndarray:
    """
    Create an embedding for a job description.
    
    Args:
        job_description: The job description text
        
    Returns:
        Embedding vector
    """
    embedder = Embedder()
    return embedder.encode(job_description)