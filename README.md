# 🧠 Offline ATS — Applicant Tracking System

> **An offline-first, AI-powered Applicant Tracking System that runs entirely on your local machine — no internet required, no external APIs, 100% private.**

---

## 🌟 Overview

**Offline ATS** is a fully local Applicant Tracking System built for recruiters who need AI-powered resume parsing and candidate ranking without sending any data to external services. All inference runs on-device using local LLMs (GGUF format), local embeddings, and local SQLite storage.

| Feature | Status |
|---|---|
| PDF & Image Resume Upload | ✅ |
| OCR Text Extraction (Tesseract) | ✅ |
| Local LLM Resume Parsing | ✅ |
| SQLite Persistent Storage | ✅ |
| Semantic Embedding Search | ✅ |
| Job Description Matching & Ranking | ✅ |
| Skill-based Filtering | ✅ |
| 100% Offline / No External APIs | ✅ |
| CPU-only Inference | ✅ |

---

## 🎯 Problem Statement

Existing ATS platforms (Greenhouse, Lever, Workday) send candidate data to cloud services, raising **privacy concerns** and requiring **internet connectivity**. Small teams, defense orgs, legal firms, or privacy-conscious companies need a fully local alternative.

**Offline ATS** solves this by:
- Running AI parsing with a local GGUF language model (Phi-3 Mini / Qwen2.5)
- Using `all-MiniLM-L6-v2` for local semantic embeddings
- Storing everything in a local SQLite database
- Providing a clean Streamlit UI for recruiters

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Streamlit UI                         │
└────────────┬─────────────────────────────────┬─────────────┘
             │                                 │
   ┌─────────▼──────────┐           ┌──────────▼──────────┐
   │   Resume Upload     │           │  Job Description    │
   │  (PDF / PNG / JPG) │           │      Input          │
   └─────────┬──────────┘           └──────────┬──────────┘
             │                                 │
   ┌─────────▼──────────┐           ┌──────────▼──────────┐
   │  Text Extraction    │           │  Embedding Model    │
   │ PyMuPDF / Tesseract│           │  all-MiniLM-L6-v2  │
   └─────────┬──────────┘           └──────────┬──────────┘
             │                                 │
   ┌─────────▼──────────┐           ┌──────────▼──────────┐
   │   Local LLM         │           │   Cosine Similarity  │
   │  Phi-3 Mini GGUF   │           │    + Skill Match     │
   │  (llama.cpp)        │           └──────────┬──────────┘
   └─────────┬──────────┘                       │
             │                       ┌──────────▼──────────┐
   ┌─────────▼──────────┐           │   Ranked Candidates  │
   │  SQLite Database    │◄──────────│   (Final Score %)   │
   │  (candidates table)│           └─────────────────────┘
   └────────────────────┘
```

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **Database** | SQLite (via Python `sqlite3`) |
| **PDF Extraction** | PyMuPDF (`fitz`) |
| **OCR (Images)** | Tesseract OCR + `pytesseract` |
| **Local LLM** | Phi-3 Mini GGUF or Qwen2.5-1.5B GGUF via `llama-cpp-python` |
| **Embeddings** | `sentence-transformers` — `all-MiniLM-L6-v2` |
| **Similarity** | Cosine Similarity (`sklearn` / `numpy`) |
| **Language** | Python 3.10+ |

---

## 📂 Project Structure

```
offline_ats/
├── app.py                    # Streamlit main application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── SPEC.md                   # Technical specification
├── ISSUES.md                 # Issue tracker / sprint plan
├── WORK_DIVISION.md          # Team work-division plan
│
├── models/
│   └── phi3-mini.gguf        # Local GGUF model (downloaded separately)
│
├── data/
│   └── ats.db                # SQLite database (auto-created)
│
├── uploads/                  # Uploaded resume files (auto-created)
│
├── src/
│   ├── __init__.py
│   ├── extractor.py          # PDF + OCR text extraction
│   ├── parser.py             # LLM-based JSON resume parser
│   ├── embedder.py           # Sentence-transformer embedding
│   ├── database.py           # SQLite CRUD operations
│   ├── ranker.py             # Cosine similarity + skill match scoring
│   └── utils.py              # Shared helpers
│
└── tests/
    ├── test_extractor.py
    ├── test_parser.py
    ├── test_ranker.py
    └── sample_resumes/       # Sample PDFs for testing
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed and added to PATH
- ~2 GB disk space for the GGUF model

### 1. Clone the repository

```bash
git clone https://code.swecha.org/Jayesh2026/offline_ats.git
cd offline_ats
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the local LLM model

```bash
# Option A: Phi-3 Mini (recommended, ~2.3 GB)
# Download from HuggingFace:
# https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
# Place the .gguf file inside models/

# Option B: Qwen2.5-1.5B (lighter, ~1 GB)
# https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
```

### 5. Run the application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 🖥️ Usage

### Upload Resumes

1. Navigate to the **Upload Resumes** tab
2. Drag-and-drop or browse for PDF/PNG/JPG files
3. Click **Process Resumes** — the app extracts text, parses structured data via LLM, and stores everything locally

### Rank Candidates

1. Navigate to the **Rank Candidates** tab
2. Paste your job description in the text area
3. Click **Find Best Matches**
4. View ranked candidates with match scores

### Search Candidates

1. Navigate to the **Search** tab
2. Type a natural language query (e.g., `Python developers with 3+ years ML experience`)
3. Results are ranked by semantic similarity

---

## 🧮 Scoring Algorithm

The final candidate ranking score is computed as:

$$\text{Final Score} = 0.6 \times \text{Embedding Similarity} + 0.4 \times \text{Skill Match}$$

**Embedding Similarity** — cosine similarity between the job description embedding and the candidate's resume embedding (semantic relevance).

**Skill Match** — fraction of required skills found in candidate's skill list:
$$\text{Skill Match} = \frac{|\text{Candidate Skills} \cap \text{Required Skills}|}{|\text{Required Skills}|}$$

---

## 🗄️ Database Schema

```sql
CREATE TABLE candidates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT,
    email       TEXT,
    phone       TEXT,
    skills      TEXT,          -- JSON array
    education   TEXT,          -- JSON array
    experience  TEXT,          -- JSON array
    projects    TEXT,          -- JSON array
    resume_path TEXT,
    raw_text    TEXT,
    json_data   TEXT,          -- Full parsed JSON
    embedding   BLOB,          -- Serialized numpy float32 array
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📋 LLM Prompt Template

```
You are a resume parser. Extract the following fields from the resume text below and return ONLY valid JSON — no explanation, no markdown, no extra text.

Fields to extract:
- name (string)
- email (string)
- phone (string)
- skills (array of strings)
- education (array of objects: degree, college)
- experience (array of objects: company, role, years)
- projects (array of strings)

Resume Text:
{resume_text}

Return JSON only:
```

---

## 📦 Requirements

```
streamlit>=1.35.0
pymupdf>=1.24.0
pytesseract>=0.3.10
Pillow>=10.0.0
llama-cpp-python>=0.2.0
sentence-transformers>=3.0.0
scikit-learn>=1.4.0
numpy>=1.26.0
```

> Install all with: `pip install -r requirements.txt`

---

## 🔒 Privacy & Offline Guarantees

- **Zero network calls** during inference or storage
- All models run locally via `llama-cpp-python` (GGUF format)
- Embeddings computed locally via `sentence-transformers`
- SQLite database stays on your machine
- Resume files stored in local `uploads/` directory

---

## 🗺️ Roadmap

- [ ] **Phase 1** — Project spec, planning, repo setup *(current)*
- [ ] **Phase 2** — Core pipeline: extraction → parsing → storage
- [ ] **Phase 3** — Embedding + ranking engine
- [ ] **Phase 4** — Streamlit UI with all tabs
- [ ] **Phase 5** — Testing, polish, documentation
- [ ] **Future** — Export to CSV/PDF, bulk import, interview scheduling

---

## 👥 Team

| Name | Role |
|---|---|
| Jayesh | Lead Developer / Backend / LLM Integration |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [llama.cpp](https://github.com/ggerganov/llama.cpp) — GGUF model inference
- [sentence-transformers](https://www.sbert.net/) — Local embeddings
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF text extraction
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) — Image OCR
- [Streamlit](https://streamlit.io/) — Rapid UI development
- [Microsoft Phi-3](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf) — Local LLM
