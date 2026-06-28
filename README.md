<<<<<<< HEAD
# 📋 Offline ATS (Applicant Tracking System)

An **offline-first** AI-powered Applicant Tracking System that processes resumes, extracts structured candidate information using local AI models, and ranks candidates based on job description relevance. **No external APIs required** — everything runs locally on your CPU.

---

## 🚀 Features

- ✅ **100% Offline** — No internet required after initial setup
- ✅ **CPU-only Inference** — Runs on any modern laptop/desktop
- ✅ **Multiple Resume Formats** — Supports PDF, PNG, JPG
- ✅ **Local LLM Parsing** — Uses Phi-3 Mini or Qwen2.5 via Ollama/llama.cpp
- ✅ **Smart Candidate Ranking** — Combines embedding similarity + skill matching
- ✅ **Semantic Search** — Search candidates using natural language
- ✅ **SQLite Storage** — Persistent local database with FTS5 full-text search
- ✅ **Beautiful UI** — Streamlit-based interface

---

## 📁 Project Structure

```
offline_ats/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── database/
│   ├── __init__.py
│   └── db.py                   # SQLite database operations
├── extraction/
│   ├── __init__.py
│   └── text_extractor.py       # PDF (PyMuPDF) & Image (OCR) text extraction
├── llm/
│   ├── __init__.py
│   └── local_llm.py            # Local LLM interface for resume parsing
├── embeddings/
│   ├── __init__.py
│   └── embedder.py             # sentence-transformers embeddings
├── matching/
│   ├── __init__.py
│   └── matcher.py              # Candidate ranking & search logic
├── utils/
│   └── __init__.py
├── uploaded_resumes/           # Uploaded resume files stored here
├── models/                     # GGUF models & sentence-transformers cache
└── database/ats.db             # SQLite database (auto-created)
=======
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
>>>>>>> 7ae9a8a478eb985e8ef5c6c9eba5787b4ddcfbd9
```

---

<<<<<<< HEAD
## 🛠️ Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Tesseract OCR

**Windows:**
- Download installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- Install and note the installation path (default: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
- Update `TESSERACT_CMD` in `config.py` if needed

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### Step 3: Install Local LLM (Choose One)

#### Option A: Ollama (Recommended - Easier)

1. Download and install [Ollama](https://ollama.com/)
2. Pull a model:
   ```bash
   ollama pull phi3:mini
   # OR
   ollama pull qwen2.5:1.5b
   ```
3. Ensure `config.py` has the correct model name

#### Option B: llama.cpp (Direct GGUF)

1. Download a GGUF model:
   - [Phi-3-mini-4k-instruct-q4.gguf](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf)
   - Place it in the `models/` directory
2. Install [llama.cpp](https://github.com/ggerganov/llama.cpp) and ensure `llama-cli` is in your PATH

### Step 4: Verify Tesseract Path

Update `TESSERACT_CMD` in `config.py` to match your Tesseract installation:

```python
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Windows default
# TESSERACT_CMD = "/usr/bin/tesseract"  # Linux
# TESSERACT_CMD = "/opt/homebrew/bin/tesseract"  # macOS ARM
```

---

## 🏃 Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 📖 Usage Guide

### 1. Upload Resumes
- Go to the **Upload Resumes** tab
- Select one or more PDF/PNG/JPG files
- Click **Process All Resumes**
- The app will:
  1. Extract text (PyMuPDF for PDFs, Tesseract OCR for images)
  2. Parse with local LLM → Structured JSON
  3. Generate embeddings (all-MiniLM-L6-v2)
  4. Store everything in SQLite

### 2. View Database
- See all stored candidates
- View parsed details (skills, education, experience)
- Export data as JSON
- Delete individual or all candidates

### 3. Rank Candidates
- Enter a job description
- The system computes:
  - **Embedding Similarity** (cosine similarity between JD and resume embeddings)
  - **Skill Match** (what percentage of required skills match)
  - **Final Score** = `0.6 × Embedding + 0.4 × Skill Match`
- Results are sorted by final score descending

### 4. Search Candidates
- **Semantic Search** — Uses embedding similarity to find relevant candidates
- **Keyword Search** — Uses SQLite FTS5 for exact keyword matching
- **Hybrid** — Combines both methods

---

## ⚙️ Configuration

Edit `config.py` to customize:

| Setting | Description | Default |
|---------|-------------|---------|
| `LLM_MODEL` | LLM backend ("phi3" or "qwen2.5") | `"phi3"` |
| `OLLAMA_MODEL` | Ollama model name | `"phi3:mini"` |
| `EMBEDDING_MODEL` | sentence-transformers model | `"all-MiniLM-L6-v2"` |
| `EMBEDDING_WEIGHT` | Weight for embedding similarity in scoring | `0.6` |
| `SKILL_MATCH_WEIGHT` | Weight for skill match in scoring | `0.4` |
| `TESSERACT_CMD` | Path to Tesseract executable | Windows default |

---

## 🔧 How It Works

```
Upload Resumes (PDF/PNG/JPG)
        ↓
Extract Text (PyMuPDF / Tesseract OCR)
        ↓
Local LLM Parsing → Structured JSON
        ↓
Store in SQLite + Generate Embeddings
        ↓
User enters Job Description
        ↓
Compute Similarity Scores
        ↓
Rank & Display Candidates
```

### Scoring Formula

```
Final Score = 0.6 × Embedding Similarity + 0.4 × Skill Match Score
```

- **Embedding Similarity**: Cosine similarity between JD and resume embeddings (0 to 1)
- **Skill Match**: Percentage of required skills found in candidate's skills (0 to 1)

---

## 🧠 Models Used

| Purpose | Model | Size |
|---------|-------|------|
| Resume Parsing | Phi-3 Mini (3.8B) / Qwen2.5 1.5B | ~2-4 GB GGUF |
| Text Embeddings | all-MiniLM-L6-v2 | ~80 MB |
| PDF Text Extraction | PyMuPDF | — |
| OCR | Tesseract OCR | — |

---

## 📊 Requirements

- **Python** 3.10+
- **RAM**: 8 GB+ (16 GB recommended for LLM)
- **Disk**: ~5 GB for models
- **OS**: Windows, macOS, or Linux

---

## 🔒 Privacy

This application is **100% offline**. All processing happens on your local machine:
- ✅ No data sent to external servers
- ✅ No API keys required
- ✅ No internet needed after initial setup
- ✅ All candidate data stays in local SQLite database

---

## 🐛 Troubleshooting

**LLM not responding:**
- Ensure Ollama is running (`ollama serve`)
- Check the model is downloaded (`ollama list`)
- Verify `OLLAMA_MODEL` in `config.py`

**OCR not working:**
- Verify Tesseract is installed
- Update `TESSERACT_CMD` in `config.py`
- Test with: `pytesseract.image_to_string(Image.open("test.png"))`

**Embedding model download fails:**
- The model downloads once on first run (~80 MB)
- Ensure internet access for initial download
- After download, it's cached locally

---

## 📝 License

MIT License — feel free to use, modify, and distribute.
=======
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

## ⚙️ CPU & Runtime Declaration

> **Hackathon Compliance:** This project is CPU-first. No GPU, no CUDA, no cloud inference.

| Component | Model | Runtime | CPU Optimisation |
|---|---|---|---|
| **Resume Parser (LLM)** | `Phi-3-mini-4k-instruct` Q4_K_M GGUF | `llama-cpp-python` (llama.cpp backend) | 4-bit quantised — runs on any x86/ARM CPU; uses all cores via `n_threads=os.cpu_count()` |
| **Fallback LLM** | `Qwen2.5-1.5B-Instruct` Q4_K_M GGUF | `llama-cpp-python` | Lighter model (~1 GB) for low-memory devices |
| **Embeddings** | `all-MiniLM-L6-v2` | `sentence-transformers` (PyTorch CPU) | 384-dim model, ~80 MB, no GPU required |
| **OCR** | Tesseract 5.x | `pytesseract` wrapper | Pure CPU; LSTM-based engine |
| **PDF Parsing** | — | `PyMuPDF` (`fitz`) | Native C library, zero ML overhead |

**No external API calls are made at any point.** All inference runs in-process on the local CPU. The app is fully functional with Wi-Fi turned off.

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
| Jayesh | Backend / AI Pipeline — Text Extraction, LLM Parser, Ranking Engine, Upload UI |
| Ramya | Data & Frontend — SQLite DB, Embeddings, Search, Candidate Management UI, Docs |

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0) — see [LICENSE](LICENSE) for details.

This is a **strong copyleft** license: any derivative work must also be distributed under GPL-3.0.

---

## 🙏 Acknowledgements

- [llama.cpp](https://github.com/ggerganov/llama.cpp) — GGUF model inference
- [sentence-transformers](https://www.sbert.net/) — Local embeddings
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF text extraction
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) — Image OCR
- [Streamlit](https://streamlit.io/) — Rapid UI development
- [Microsoft Phi-3](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf) — Local LLM
>>>>>>> 7ae9a8a478eb985e8ef5c6c9eba5787b4ddcfbd9
