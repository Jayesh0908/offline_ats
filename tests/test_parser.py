"""
tests/test_parser.py — Unit tests for src/parser.py
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from src.parser import parse_resume, _regex_fallback


class MockLLM:
    """Mock Llama model for testing without loading actual GGUF."""

    def __init__(self, return_text: str):
        self._return_text = return_text

    def __call__(self, prompt: str, **kwargs):
        return {"choices": [{"text": self._return_text}]}


class TestParseResume:
    def test_valid_json_output(self):
        valid_json = json.dumps({
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "skills": ["Python", "React"],
            "education": [{"degree": "B.Tech CSE", "college": "XYZ University"}],
            "experience": [{"company": "ABC", "role": "Developer", "years": 2}],
            "projects": ["E-commerce App"],
        })
        model = MockLLM(return_text=valid_json)
        result = parse_resume("John Doe, Python developer", model)

        assert result["name"] == "John Doe"
        assert "Python" in result["skills"]
        assert result["email"] == "john@example.com"

    def test_malformed_json_falls_back_to_regex(self):
        model = MockLLM(return_text="This is not JSON at all!!!")
        result = parse_resume("Jane Smith jane@example.com Python Django", model)

        # Regex fallback should at least capture email
        assert isinstance(result, dict)
        assert "name" in result
        assert "skills" in result

    def test_empty_text_returns_dict(self):
        model = MockLLM(return_text="{}")
        result = parse_resume("", model)
        assert isinstance(result, dict)

    def test_markdown_fences_stripped(self):
        """LLM sometimes wraps JSON in markdown code fences."""
        json_with_fences = "```json\n{\"name\": \"Alice\", \"email\": \"\", \"phone\": \"\", \"skills\": [], \"education\": [], \"experience\": [], \"projects\": []}\n```"
        model = MockLLM(return_text=json_with_fences)
        result = parse_resume("Alice resume text", model)
        assert result["name"] == "Alice"


class TestRegexFallback:
    def test_extracts_email(self):
        text = "John Doe\njohn.doe@gmail.com\n+91 9876543210"
        result = _regex_fallback(text)
        assert result["email"] == "john.doe@gmail.com"

    def test_extracts_phone(self):
        text = "Jane Smith\njane@example.com\n+1 (555) 123-4567"
        result = _regex_fallback(text)
        assert result["phone"] != ""

    def test_extracts_known_skills(self):
        text = "Skills: Python, React, Docker, AWS"
        result = _regex_fallback(text)
        assert "Python" in result["skills"]
        assert "React" in result["skills"]

    def test_uses_first_line_as_name(self):
        text = "Alice Johnson\nalice@example.com\n"
        result = _regex_fallback(text)
        assert result["name"] == "Alice Johnson"

    def test_empty_text_returns_empty_fields(self):
        result = _regex_fallback("")
        assert result["name"] == ""
        assert result["email"] == ""
        assert result["skills"] == []
