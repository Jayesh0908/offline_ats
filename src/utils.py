"""
utils.py — Shared Utility Functions

Common helpers used across the Offline ATS modules.
"""

import os
import uuid
import logging
from datetime import datetime


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger for the application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def save_uploaded_file(file_bytes: bytes, filename: str, upload_dir: str) -> str:
    """
    Save uploaded bytes to the uploads directory with a unique filename.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename: Original filename (used for extension detection).
        upload_dir: Directory to save the file in.

    Returns:
        Absolute path to the saved file.
    """
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return file_path


def truncate_text(text: str, max_chars: int = 500) -> str:
    """
    Truncate text for display purposes.

    Args:
        text: Input string.
        max_chars: Maximum characters to keep.

    Returns:
        Truncated string with ellipsis if needed.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def format_experience(experience_list: list) -> str:
    """
    Format a list of experience objects into a readable string.

    Args:
        experience_list: List of dicts with company, role, years keys.

    Returns:
        Formatted multiline string.
    """
    if not experience_list:
        return "No experience listed"
    lines = []
    for exp in experience_list:
        company = exp.get("company", "N/A")
        role = exp.get("role", "N/A")
        years = exp.get("years", "?")
        lines.append(f"• {role} @ {company} ({years} yr{'s' if years != 1 else ''})")
    return "\n".join(lines)


def format_education(education_list: list) -> str:
    """
    Format a list of education objects into a readable string.

    Args:
        education_list: List of dicts with degree, college keys.

    Returns:
        Formatted multiline string.
    """
    if not education_list:
        return "No education listed"
    lines = []
    for edu in education_list:
        degree = edu.get("degree", "N/A")
        college = edu.get("college", "N/A")
        lines.append(f"• {degree} — {college}")
    return "\n".join(lines)


def timestamp_str() -> str:
    """Return current timestamp as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
