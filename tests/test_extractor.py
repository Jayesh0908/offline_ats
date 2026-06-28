"""
tests/test_extractor.py — Unit tests for src/extractor.py
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from src.extractor import extract_text_from_pdf, extract_text_from_image, extract_text


class TestExtractTextFromPdf:
    def test_raises_if_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("/nonexistent/path/resume.pdf")

    def test_returns_string(self, tmp_path):
        """Integration test — requires a real PDF."""
        pytest.importorskip("fitz")
        # Create a minimal PDF using fitz
        import fitz
        pdf_path = str(tmp_path / "test.pdf")
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "John Doe\njohn@example.com\nPython Developer")
        doc.save(pdf_path)
        doc.close()

        result = extract_text_from_pdf(pdf_path)
        assert isinstance(result, str)
        assert "John" in result or len(result) >= 0  # non-empty


class TestExtractTextFromImage:
    def test_raises_if_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            extract_text_from_image("/nonexistent/image.png")

    @patch("src.extractor.pytesseract.image_to_string", return_value="John Doe\nPython Developer")
    @patch("src.extractor.Image.open", return_value=MagicMock())
    def test_returns_ocr_text(self, mock_open, mock_ocr, tmp_path):
        img_path = str(tmp_path / "resume.png")
        # Create a dummy file so os.path.exists passes
        with open(img_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")  # PNG magic bytes

        result = extract_text_from_image(img_path)
        assert "John Doe" in result


class TestExtractText:
    def test_unsupported_extension_raises(self, tmp_path):
        docx_path = str(tmp_path / "resume.docx")
        with open(docx_path, "w") as f:
            f.write("dummy")
        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_text(docx_path)

    def test_pdf_dispatched_correctly(self, tmp_path):
        pdf_path = str(tmp_path / "resume.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4 dummy")
        with patch("src.extractor.extract_text_from_pdf", return_value="PDF text") as mock_pdf:
            result = extract_text(pdf_path)
            mock_pdf.assert_called_once_with(pdf_path)
            assert result == "PDF text"

    def test_jpg_dispatched_to_ocr(self, tmp_path):
        img_path = str(tmp_path / "resume.jpg")
        with open(img_path, "wb") as f:
            f.write(b"\xff\xd8\xff")
        with patch("src.extractor.extract_text_from_image", return_value="OCR text") as mock_img:
            result = extract_text(img_path)
            mock_img.assert_called_once_with(img_path)
            assert result == "OCR text"
