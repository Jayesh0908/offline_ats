"""
Text extraction from PDF and image files.
Uses PyMuPDF for PDFs and Tesseract OCR for images.
"""
import os
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from typing import Optional
import config


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    text_parts = []
    try:
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(f"[Page {page_num + 1}]\n{page_text}")
        doc.close()
        
        full_text = "\n\n".join(text_parts)
        print(f"[Extractor] PDF: Extracted {len(full_text)} chars from {pdf_path}")
        return full_text
    except Exception as e:
        print(f"[Extractor] Error extracting PDF {pdf_path}: {e}")
        return ""


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image file using Tesseract OCR.
    
    Args:
        image_path: Path to the image file (PNG, JPG, etc.)
        
    Returns:
        Extracted text as a string
    """
    try:
        # Set Tesseract executable path
        if os.path.exists(config.TESSERACT_CMD):
            pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD
        
        image = Image.open(image_path)
        # Convert to RGB if necessary
        if image.mode not in ("L", "RGB"):
            image = image.convert("RGB")
        
        text = pytesseract.image_to_string(image, lang="eng")
        print(f"[Extractor] Image: Extracted {len(text)} chars from {image_path}")
        return text.strip()
    except Exception as e:
        print(f"[Extractor] Error extracting image {image_path}: {e}")
        return ""


def extract_text(file_path: str) -> str:
    """
    Extract text from a resume file (PDF or image).
    Automatically detects file type by extension.
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        Extracted text as a string
    """
    if not os.path.exists(file_path):
        print(f"[Extractor] File not found: {file_path}")
        return ""
    
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".png", ".jpg", ".jpeg"):
        return extract_text_from_image(file_path)
    else:
        print(f"[Extractor] Unsupported file format: {ext}")
        return ""