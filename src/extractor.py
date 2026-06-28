"""
extractor.py — Resume Text Extraction Module

Handles extraction of raw text from PDF and image resume files.
- PDF: PyMuPDF (fitz)
- Images (PNG, JPG): Tesseract OCR via pytesseract
"""

import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image


SUPPORTED_PDF_EXT = {".pdf"}
SUPPORTED_IMAGE_EXT = {".png", ".jpg", ".jpeg"}


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file using PyMuPDF.

    Args:
        file_path: Absolute path to the PDF file.

    Returns:
        Concatenated raw text from all pages.

    Raises:
        FileNotFoundError: If the file does not exist.
        fitz.FileDataError: If the file is not a valid PDF.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    text_parts = []
    with fitz.open(file_path) as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts).strip()


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from an image file using Tesseract OCR.

    Args:
        file_path: Absolute path to the PNG/JPG image.

    Returns:
        OCR-extracted raw text.

    Raises:
        FileNotFoundError: If the file does not exist.
        pytesseract.TesseractNotFoundError: If Tesseract is not installed.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text.strip()


def extract_text(file_path: str) -> str:
    """
    Dispatcher: routes to PDF or image extractor based on file extension.

    Args:
        file_path: Path to any supported resume file (.pdf, .png, .jpg, .jpeg).

    Returns:
        Extracted raw text string.

    Raises:
        ValueError: If file extension is not supported.
    """
    _, ext = os.path.splitext(file_path.lower())

    if ext in SUPPORTED_PDF_EXT:
        return extract_text_from_pdf(file_path)
    elif ext in SUPPORTED_IMAGE_EXT:
        return extract_text_from_image(file_path)
    else:
        raise ValueError(
            f"Unsupported file type: '{ext}'. "
            f"Supported types: {SUPPORTED_PDF_EXT | SUPPORTED_IMAGE_EXT}"
        )
