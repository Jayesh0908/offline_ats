"""
Configuration settings for Offline ATS.
All paths and model configurations are centralized here.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_PATH = BASE_DIR / "database" / "ats.db"

# Uploaded resumes storage
UPLOAD_DIR = BASE_DIR / "uploaded_resumes"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Models directory for GGUF files
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Local LLM Configuration
# Options: "phi3" or "qwen2.5"
LLM_MODEL = "phi3"
# If using Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "phi3:mini"  # or "qwen2.5:1.5b"

# GGUF Model path (if using llama.cpp directly instead of Ollama)
# Download from: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
PHI3_GGUF_PATH = MODELS_DIR / "Phi-3-mini-4k-instruct-q4.gguf"
QWEN_GGUF_PATH = MODELS_DIR / "Qwen2.5-1.5B-Instruct-q4.gguf"

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_CACHE_DIR = BASE_DIR / "models" / "sentence_transformers"

# Tesseract OCR Configuration
# Update this path to where Tesseract is installed on your system
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Scoring weights
EMBEDDING_WEIGHT = 0.6
SKILL_MATCH_WEIGHT = 0.4

# Supported file extensions
SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

# LLM Inference Settings
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 2048
LLM_CONTEXT_SIZE = 4096