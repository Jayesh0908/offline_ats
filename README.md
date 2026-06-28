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
```

---

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