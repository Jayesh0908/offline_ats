# 📐 Technical Specification — Offline ATS

**Project:** Offline Applicant Tracking System  
**Version:** 1.0  
**Date:** 2026-06-28  
**Author:** Jayesh  
**Status:** Draft — Phase 1

---

## 1. Introduction

### 1.1 Purpose

This document defines the complete technical specification for the Offline ATS project. It covers system architecture, module design, data models, API contracts (internal), and acceptance criteria for each feature.

### 1.2 Scope

The system must:
- Accept PDF and image resumes from a local Streamlit UI
- Extract raw text using PyMuPDF and Tesseract OCR
- Parse structured candidate data using a locally running GGUF LLM
- Store parsed data and embedding vectors in a local SQLite database
- Rank candidates against a job description using hybrid scoring (embedding similarity + skill match)
- Provide natural language search over stored candidates
- Operate 100% offline with zero external API calls

### 1.3 Definitions

| Term | Definition |
|---|---|
| GGUF | GGML Unified Format — binary format for quantized LLM weights |
| Embedding | A dense numeric vector (384-dim) representing semantic meaning of text |
| Cosine Similarity | A measure of angle between two vectors; 1.0 = identical, 0.0 = unrelated |
| FTS | Full-Text Search — SQLite feature for keyword-based search |
| OCR | Optical Character Recognition — extracting text from images |
| ATS | Applicant Tracking System |

---

## 2. System Architecture

### 2.1 High-Level Components

```
┌──────────────────────────────────────────────────────────────┐
│                       PRESENTATION LAYER                      │
│                    Streamlit (app.py)                         │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │Upload Tab   │  │Rank Candidates   │  │Search Tab      │  │
│  │             │  │Tab               │  │                │  │
│  └──────┬──────┘  └────────┬─────────┘  └───────┬────────┘  │
└─────────┼─────────────────┼──────────────────────┼──────────┘
          │                 │                       │
┌─────────▼─────────────────▼───────────────────────▼──────────┐
│                        BUSINESS LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  extractor   │  │   parser     │  │     ranker        │  │
│  │  .py         │  │   .py        │  │     .py           │  │
│  │  (PyMuPDF    │  │  (llama-cpp  │  │  (cosine sim +   │  │
│  │  + Tesseract)│  │   + prompt)  │  │   skill match)    │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬──────────┘  │
│         │                 │                    │              │
│  ┌──────▼─────────────────▼────────────────────▼──────────┐  │
│  │                     embedder.py                         │  │
│  │              (sentence-transformers)                    │  │
│  └─────────────────────────┬──────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      PERSISTENCE LAYER                        │
│                     database.py + ats.db                      │
│                   (SQLite — local storage)                    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
User uploads PDF/Image
        │
        ▼
extractor.py → raw_text (str)
        │
        ▼
parser.py → LLM prompt → structured JSON
        │
        ▼
embedder.py → numpy float32 vector (384-dim)
        │
        ▼
database.py → INSERT into candidates table
        │
        ▼
[On ranking request]
        │
Job Description → embedder.py → JD embedding
        │
        ▼
ranker.py → cosine_sim(JD_embedding, candidate_embeddings)
          → skill_match(JD_skills, candidate_skills)
          → final_score = 0.6*sim + 0.4*skill_match
        │
        ▼
Sorted list of (candidate, score) → Streamlit display
```

---

## 3. Module Specifications

### 3.1 `src/extractor.py` — Text Extraction

**Responsibility:** Convert uploaded files (PDF/PNG/JPG) into raw plain text.

#### Functions

```python
def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF using PyMuPDF.
    
    Args:
        file_path: Absolute path to the PDF file.
    Returns:
        Concatenated raw text from all pages.
    Raises:
        FileNotFoundError: if file does not exist.
        fitz.FileDataError: if file is not a valid PDF.
    """

def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from a PNG/JPG using Tesseract OCR.
    
    Args:
        file_path: Absolute path to the image file.
    Returns:
        OCR-extracted raw text.
    Raises:
        pytesseract.TesseractNotFoundError: if Tesseract is not installed.
    """

def extract_text(file_path: str) -> str:
    """
    Dispatcher: routes to PDF or image extractor based on file extension.
    
    Args:
        file_path: Path to any supported resume file.
    Returns:
        Extracted raw text.
    """
```

**Dependencies:** `pymupdf`, `pytesseract`, `Pillow`

---

### 3.2 `src/parser.py` — LLM Resume Parser

**Responsibility:** Send raw resume text to a local GGUF model and return structured JSON.

#### LLM Prompt Template

```
You are a resume parser. Extract the following fields from the resume text and return ONLY valid JSON.

Fields:
- name: string
- email: string  
- phone: string
- skills: list of strings
- education: list of {degree: string, college: string}
- experience: list of {company: string, role: string, years: number}
- projects: list of strings

Resume Text:
{resume_text}

Return ONLY valid JSON:
```

#### Functions

```python
def load_model(model_path: str) -> Llama:
    """
    Load GGUF model from disk using llama-cpp-python.
    Cached globally to avoid reloading on every call.
    
    Args:
        model_path: Path to the .gguf model file.
    Returns:
        Llama model instance.
    """

def parse_resume(raw_text: str, model: Llama) -> dict:
    """
    Run LLM inference on raw text and parse JSON output.
    
    Args:
        raw_text: Extracted text from resume.
        model: Loaded Llama model instance.
    Returns:
        Parsed dictionary with candidate fields.
    Raises:
        json.JSONDecodeError: if LLM output is not valid JSON (fallback to empty dict).
    """
```

**LLM Parameters:**

| Parameter | Value |
|---|---|
| `max_tokens` | 1024 |
| `temperature` | 0.1 (low, for deterministic output) |
| `top_p` | 0.95 |
| `n_ctx` | 4096 |
| `n_threads` | `os.cpu_count()` |

**Error Handling:** If JSON parsing fails, fall back to regex-based extraction for `name`, `email`, `phone`, and `skills`.

---

### 3.3 `src/embedder.py` — Embedding Generator

**Responsibility:** Convert text into semantic embedding vectors for storage and similarity search.

#### Functions

```python
def load_embedding_model() -> SentenceTransformer:
    """
    Load all-MiniLM-L6-v2 model (downloaded on first run, cached locally).
    Returns:
        SentenceTransformer instance.
    """

def embed_text(text: str, model: SentenceTransformer) -> np.ndarray:
    """
    Generate a 384-dimensional float32 embedding for input text.
    
    Args:
        text: Any string (resume text or job description).
    Returns:
        numpy float32 array of shape (384,).
    """

def serialize_embedding(embedding: np.ndarray) -> bytes:
    """Serialize numpy array to bytes for SQLite BLOB storage."""

def deserialize_embedding(blob: bytes) -> np.ndarray:
    """Deserialize bytes from SQLite BLOB back to numpy array."""
```

**Model:** `all-MiniLM-L6-v2` — 384 dimensions, ~80 MB, MIT license.

---

### 3.4 `src/database.py` — SQLite Persistence

**Responsibility:** All database creation, read, write, and query operations.

#### Schema

```sql
CREATE TABLE IF NOT EXISTS candidates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT,
    phone       TEXT,
    skills      TEXT,           -- JSON-encoded list: '["React", "Node.js"]'
    education   TEXT,           -- JSON-encoded list of objects
    experience  TEXT,           -- JSON-encoded list of objects
    projects    TEXT,           -- JSON-encoded list
    resume_path TEXT,
    raw_text    TEXT,
    json_data   TEXT,           -- Full LLM output JSON string
    embedding   BLOB,           -- Serialized numpy float32 (384 floats = 1536 bytes)
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Full-Text Search virtual table
CREATE VIRTUAL TABLE IF NOT EXISTS candidates_fts
USING fts5(name, skills, raw_text, content='candidates', content_rowid='id');
```

#### Functions

```python
def init_db(db_path: str) -> sqlite3.Connection:
    """Create database and tables if they don't exist."""

def insert_candidate(conn, candidate_data: dict, resume_path: str,
                     raw_text: str, json_data: str, embedding: bytes) -> int:
    """Insert a candidate row and return the new row ID."""

def get_all_candidates(conn) -> list[dict]:
    """Return all candidates as list of dicts (without embedding blob)."""

def get_all_embeddings(conn) -> list[tuple[int, np.ndarray]]:
    """Return list of (candidate_id, embedding_array) for ranking."""

def search_candidates_fts(conn, query: str) -> list[dict]:
    """Full-text search over name, skills, and raw_text."""

def delete_candidate(conn, candidate_id: int) -> None:
    """Delete a candidate record by ID."""
```

---

### 3.5 `src/ranker.py` — Candidate Ranking Engine

**Responsibility:** Score and rank candidates against a job description.

#### Scoring Formula

```
Final Score = 0.6 × Cosine_Similarity + 0.4 × Skill_Match_Ratio
```

Where:
- **Cosine Similarity** ∈ [0, 1] — semantic match of JD vs resume embeddings
- **Skill Match Ratio** = |candidate_skills ∩ required_skills| / |required_skills|

#### Functions

```python
def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two normalized vectors."""

def extract_skills_from_jd(jd_text: str) -> list[str]:
    """
    Extract skill keywords from job description text.
    Uses simple NLP (lowercased word matching against a known tech skills list).
    """

def rank_candidates(
    jd_text: str,
    jd_embedding: np.ndarray,
    candidates: list[dict],
    candidate_embeddings: list[tuple[int, np.ndarray]]
) -> list[dict]:
    """
    Compute final scores and return candidates sorted by score descending.
    
    Returns list of dicts: {candidate_data, embedding_score, skill_score, final_score}
    """
```

---

### 3.6 `app.py` — Streamlit Application

**Pages / Tabs:**

| Tab | Description |
|---|---|
| 📤 Upload Resumes | Multi-file uploader, processing pipeline trigger, success/error status |
| 🏆 Rank Candidates | JD text input, skill filter, ranked results with score breakdown |
| 🔍 Search | Natural language search, results table |
| 📋 All Candidates | Table view of all stored candidates, delete option |
| ⚙️ Settings | Model path config, DB path, clear database button |

---

## 4. Data Models

### 4.1 Candidate (Python Dict / JSON)

```python
{
  "name": "John Doe",
  "email": "john@gmail.com",
  "phone": "9876543210",
  "skills": ["React", "Node.js", "MongoDB", "Docker"],
  "education": [
    {"degree": "B.Tech CSE", "college": "XYZ University"}
  ],
  "experience": [
    {"company": "ABC Corp", "role": "Software Engineer", "years": 2}
  ],
  "projects": ["E-commerce Web App", "Chat Application"]
}
```

### 4.2 Ranking Result

```python
{
  "id": 1,
  "name": "John Doe",
  "email": "john@gmail.com",
  "skills": ["React", "Node.js", "MongoDB"],
  "embedding_score": 0.91,
  "skill_score": 0.75,
  "final_score": 0.846,
  "final_score_pct": "84.6%"
}
```

---

## 5. External Dependencies

### Python Packages

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥1.35.0 | Web UI |
| `pymupdf` | ≥1.24.0 | PDF text extraction |
| `pytesseract` | ≥0.3.10 | Image OCR wrapper |
| `Pillow` | ≥10.0.0 | Image loading |
| `llama-cpp-python` | ≥0.2.0 | GGUF LLM inference |
| `sentence-transformers` | ≥3.0.0 | Local embeddings |
| `scikit-learn` | ≥1.4.0 | Cosine similarity utilities |
| `numpy` | ≥1.26.0 | Vector operations |

### System Dependencies

| Tool | Purpose | Install |
|---|---|---|
| Tesseract OCR | Image text extraction | `winget install UB-Mannheim.TesseractOCR` |
| Python 3.10+ | Runtime | python.org |

### Model Files (Downloaded Separately)

| Model | Size | Purpose | Source |
|---|---|---|---|
| Phi-3 Mini Q4_K_M GGUF | ~2.3 GB | Resume parsing LLM | HuggingFace |
| all-MiniLM-L6-v2 | ~80 MB | Embeddings | HuggingFace (auto-downloaded) |

---

## 6. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Resume processing time (PDF) | < 60 seconds per resume (LLM dependent) |
| Resume processing time (OCR image) | < 90 seconds per resume |
| Ranking time (50 candidates) | < 5 seconds |
| Database query time | < 500 ms |
| Memory usage (idle) | < 500 MB |
| Memory usage (LLM loaded) | < 4 GB (Phi-3 Mini Q4) |
| Storage (per candidate) | < 10 KB (excluding resume file) |

---

## 7. Error Handling Strategy

| Scenario | Handling |
|---|---|
| Corrupted PDF | Log error, skip file, show warning in UI |
| Tesseract not installed | Show installation instructions, disable image upload |
| LLM JSON parse failure | Regex fallback extraction for key fields |
| Model file missing | Prompt user to download model, disable processing |
| Duplicate resume | Warn user, allow re-process to overwrite |
| Empty extracted text | Mark candidate as "manual review needed" |

---

## 8. Acceptance Criteria

### Feature: Resume Upload
- [ ] User can upload 1–20 PDF files simultaneously
- [ ] User can upload PNG/JPG image files
- [ ] Files are saved to `uploads/` directory with unique filenames
- [ ] Processing status shown per file (✅ success / ❌ error)

### Feature: Text Extraction
- [ ] PDF text extraction works for standard PDFs
- [ ] OCR extraction works for clear scanned images
- [ ] Extraction returns non-empty string for valid files

### Feature: LLM Parsing
- [ ] Parsed output contains at minimum: name and skills
- [ ] Output is valid JSON (with regex fallback)
- [ ] Runs completely offline without internet

### Feature: Database Storage
- [ ] Candidate record inserted on successful parse
- [ ] Embedding stored as binary blob
- [ ] Duplicate check by email/name

### Feature: Candidate Ranking
- [ ] Job description produces ranked list
- [ ] Final scores between 0.0 and 1.0
- [ ] Ranking is stable (same inputs = same order)

### Feature: Search
- [ ] FTS search returns results in < 1 second
- [ ] Semantic search returns results in < 5 seconds
- [ ] Empty results handled gracefully

---

## 9. Testing Plan

| Test Type | Tool | Coverage Target |
|---|---|---|
| Unit Tests | `pytest` | 80% of `src/` modules |
| Integration Tests | `pytest` | Full pipeline (upload → rank) |
| Manual Testing | Human | UI flows, edge cases |

### Test Cases

- `test_extractor.py` — PDF with text, PDF with images only, JPG, PNG, empty PDF
- `test_parser.py` — Valid JSON output, malformed output fallback, empty text input
- `test_ranker.py` — Perfect match, zero match, partial match, missing required fields

---

*Document version 1.0 — Phase 1 Planning*
