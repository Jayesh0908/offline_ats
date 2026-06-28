"""
parser.py — LLM-based Resume Parser

Uses a local GGUF model (Phi-3 Mini / Qwen2.5) via llama-cpp-python
to parse raw resume text into structured JSON fields.

Falls back to regex extraction if LLM output is not valid JSON.
"""

import json
import re
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global model cache — loaded once per session
_llm_instance = None

PROMPT_TEMPLATE = """You are a resume parser. Extract the following fields from the resume text below and return ONLY valid JSON — no explanation, no markdown code blocks, no extra text.

Fields to extract:
- name: string (full name of the candidate)
- email: string (email address)
- phone: string (phone number)
- skills: list of strings (technical and soft skills)
- education: list of objects with keys: degree (string), college (string)
- experience: list of objects with keys: company (string), role (string), years (number)
- projects: list of strings (project names or descriptions)

Resume Text:
{resume_text}

Return ONLY valid JSON:"""


def load_model(model_path: str):
    """
    Load and cache the GGUF model using llama-cpp-python.

    Args:
        model_path: Absolute path to the .gguf model file.

    Returns:
        Llama model instance.

    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    global _llm_instance

    if _llm_instance is not None:
        return _llm_instance

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"GGUF model not found at: {model_path}\n"
            "Please download Phi-3 Mini from:\n"
            "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf"
        )

    try:
        from llama_cpp import Llama
        _llm_instance = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=os.cpu_count(),
            verbose=False,
        )
        logger.info(f"GGUF model loaded from: {model_path}")
        return _llm_instance
    except ImportError:
        raise ImportError(
            "llama-cpp-python is not installed. Run: pip install llama-cpp-python"
        )


def parse_resume(raw_text: str, model) -> dict:
    """
    Parse raw resume text into structured JSON using the local LLM.

    Args:
        raw_text: Extracted text from a resume file.
        model: Loaded Llama model instance.

    Returns:
        Dictionary with parsed candidate fields.
        Falls back to regex extraction if JSON parsing fails.
    """
    # Truncate very long resumes to avoid context overflow
    max_chars = 6000
    if len(raw_text) > max_chars:
        raw_text = raw_text[:max_chars] + "\n[truncated]"

    prompt = PROMPT_TEMPLATE.format(resume_text=raw_text)

    try:
        response = model(
            prompt,
            max_tokens=1024,
            temperature=0.1,
            top_p=0.95,
            stop=["```", "\n\n\n"],
        )
        output_text = response["choices"][0]["text"].strip()

        # Strip markdown code fences if present
        output_text = re.sub(r"^```json?\s*", "", output_text)
        output_text = re.sub(r"\s*```$", "", output_text)

        parsed = json.loads(output_text)
        logger.info("LLM JSON parsing successful")
        return parsed

    except (json.JSONDecodeError, KeyError, Exception) as e:
        logger.warning(f"LLM JSON parsing failed: {e}. Falling back to regex.")
        return _regex_fallback(raw_text)


def _regex_fallback(raw_text: str) -> dict:
    """
    Regex-based fallback extractor for key resume fields.

    Args:
        raw_text: Raw resume text.

    Returns:
        Partially populated candidate dict from regex patterns.
    """
    result = {
        "name": "",
        "email": "",
        "phone": "",
        "skills": [],
        "education": [],
        "experience": [],
        "projects": [],
    }

    # Email
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", raw_text, re.I)
    if email_match:
        result["email"] = email_match.group(0)

    # Phone
    phone_match = re.search(r"(\+?\d[\d\s\-().]{8,14}\d)", raw_text)
    if phone_match:
        result["phone"] = phone_match.group(0).strip()

    # Name (first non-empty line, assumed to be name)
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    if lines:
        result["name"] = lines[0]

    # Skills (look for common tech keywords)
    KNOWN_SKILLS = [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI",
        "SQL", "MongoDB", "PostgreSQL", "MySQL", "SQLite", "Redis",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux",
        "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch",
        "Git", "REST", "GraphQL", "HTML", "CSS",
    ]
    found_skills = [skill for skill in KNOWN_SKILLS if skill.lower() in raw_text.lower()]
    result["skills"] = found_skills

    return result
