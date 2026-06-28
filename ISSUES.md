# 📋 Issues & Sprint Plan — Offline ATS

**Project:** Offline Applicant Tracking System  
**Sprint Duration:** 1 week  
**Start Date:** 2026-06-28  
**End Date:** 2026-07-05  
**Team:** Jayesh (Backend / AI Pipeline) · Ramya (Database / UI / Testing)  

---

## Issue Labels

| Label | Meaning |
|---|---|
| `feature` | New functionality |
| `infra` | Setup / DevOps / configuration |
| `bug` | Defect fix |
| `docs` | Documentation |
| `testing` | Test writing |
| `enhancement` | Improvement to existing functionality |

---

## Milestone 1 — Project Setup & Planning
**Due: 2026-06-28** | **Phase 1**

---

### ISSUE-001 · Initialize Git Repository & Project Structure

- **Type:** `infra`
- **Assignee:** Jayesh (README, SPEC, directory structure) · Ramya (ISSUES.md, WORK_DIVISION.md)
- **Estimate:** 1 hour each
- **Due Date:** 2026-06-28
- **Priority:** 🔴 Critical

**Description:**
Set up the GitLab repository with the correct project structure.

**Tasks:**
- [x] Create GitLab repo `offline_ats`
- [x] Write comprehensive `README.md`
- [x] Write `SPEC.md` technical specification
- [x] Write `ISSUES.md` issue tracker
- [x] Write `WORK_DIVISION.md` team plan
- [ ] Create `.gitignore` (Python, models/, uploads/, *.db)
- [ ] Create initial `requirements.txt`
- [ ] Set up `src/` and `tests/` directory structure
- [ ] First commit and push to `main`

**Acceptance Criteria:**
- Repo is publicly accessible on GitLab
- `README.md` renders correctly with all sections
- Directory structure matches specification

---

### ISSUE-002 · Write requirements.txt and Environment Setup Guide

- **Type:** `infra`
- **Assignee:** Jayesh (requirements.txt, .gitignore) · Ramya (Tesseract + model download docs)
- **Estimate:** 1 hour
- **Due Date:** 2026-06-28
- **Priority:** 🔴 Critical

**Description:**
Define all Python dependencies and create a one-command setup guide.

**Tasks:**
- [ ] Pin all library versions in `requirements.txt`
- [ ] Test install on clean Python 3.10 environment
- [ ] Document Tesseract installation steps (Windows/Linux/macOS)
- [ ] Document GGUF model download instructions

**Acceptance Criteria:**
- `pip install -r requirements.txt` succeeds without errors
- Tesseract installation documented for all platforms

---

## Milestone 2 — Core Pipeline
**Due: 2026-07-01** | **Phase 2**

---

### ISSUE-003 · Implement Text Extraction Module

- **Type:** `feature`
- **Assignee:** Jayesh
- **Estimate:** 4 hours
- **Due Date:** 2026-06-29
- **Priority:** 🔴 Critical

**Description:**
Build `src/extractor.py` to handle PDF and image resume text extraction.

**Tasks:**
- [ ] Implement `extract_text_from_pdf()` using PyMuPDF
- [ ] Implement `extract_text_from_image()` using pytesseract
- [ ] Implement `extract_text()` dispatcher
- [ ] Handle corrupt / empty files gracefully
- [ ] Write unit tests in `tests/test_extractor.py`

**Acceptance Criteria:**
- PDF extraction returns non-empty text for standard PDF resumes
- Image OCR returns text from clear scanned resumes
- Corrupt files raise informative exceptions (not crash)
- All tests pass

---

### ISSUE-004 · Implement SQLite Database Module

- **Type:** `feature`
- **Assignee:** Ramya
- **Estimate:** 4 hours
- **Due Date:** 2026-06-29
- **Priority:** 🔴 Critical

**Description:**
Build `src/database.py` with full CRUD and FTS support.

**Tasks:**
- [ ] Create SQLite schema (candidates table)
- [ ] Create FTS5 virtual table for search
- [ ] Implement `init_db()`
- [ ] Implement `insert_candidate()`
- [ ] Implement `get_all_candidates()`
- [ ] Implement `get_all_embeddings()`
- [ ] Implement `search_candidates_fts()`
- [ ] Implement `delete_candidate()`
- [ ] Write integration tests

**Acceptance Criteria:**
- Candidate can be inserted and retrieved with all fields intact
- FTS search returns relevant results
- Embedding blob round-trips correctly (serialize → store → retrieve → deserialize)

---

### ISSUE-005 · Implement LLM Resume Parser

- **Type:** `feature`
- **Assignee:** Jayesh
- **Estimate:** 5 hours
- **Due Date:** 2026-06-30
- **Priority:** 🔴 Critical

**Description:**
Build `src/parser.py` to load a local GGUF model and parse resumes into structured JSON.

**Tasks:**
- [ ] Download and test Phi-3 Mini GGUF model locally
- [ ] Implement `load_model()` with global caching
- [ ] Write and test LLM prompt template
- [ ] Implement `parse_resume()` with JSON output parsing
- [ ] Implement regex fallback for malformed JSON output
- [ ] Test on 5+ different resume styles/formats
- [ ] Write unit tests with mock LLM

**Acceptance Criteria:**
- LLM output is valid JSON for 90%+ of test resumes
- Regex fallback captures name/email/skills when JSON fails
- Model loads only once per session (cached)
- Runs completely offline

---

### ISSUE-006 · Implement Embedding Module

- **Type:** `feature`
- **Assignee:** Ramya
- **Estimate:** 3 hours
- **Due Date:** 2026-06-30
- **Priority:** 🟡 High

**Description:**
Build `src/embedder.py` for generating and managing sentence embeddings.

**Tasks:**
- [ ] Implement `load_embedding_model()` with caching
- [ ] Implement `embed_text()` returning 384-dim float32 numpy array
- [ ] Implement `serialize_embedding()` / `deserialize_embedding()` for SQLite BLOB
- [ ] Verify embedding consistency (same text = same vector)
- [ ] Write unit tests

**Acceptance Criteria:**
- `all-MiniLM-L6-v2` loads and produces correct shape (384,)
- Serialization round-trip preserves vector within float32 tolerance
- Model runs without GPU

---

## Milestone 3 — Ranking & Search
**Due: 2026-07-03** | **Phase 3**

---

### ISSUE-007 · Implement Candidate Ranking Engine

- **Type:** `feature`
- **Assignee:** Jayesh
- **Estimate:** 5 hours
- **Due Date:** 2026-07-01
- **Priority:** 🔴 Critical

**Description:**
Build `src/ranker.py` with hybrid embedding + skill match scoring.

**Tasks:**
- [ ] Implement `cosine_similarity()` using numpy
- [ ] Implement `extract_skills_from_jd()` — keyword extraction from JD text
- [ ] Implement `rank_candidates()` combining embedding + skill scores
- [ ] Apply weighted formula: `0.6 × sim + 0.4 × skill_match`
- [ ] Return sorted results with score breakdown
- [ ] Write unit tests with known expected rankings

**Acceptance Criteria:**
- Ranking is deterministic (same inputs = same output)
- Scores are in [0.0, 1.0] range
- Skill match is case-insensitive
- Performance: ranks 50 candidates in < 5 seconds

---

### ISSUE-008 · Implement Search Feature

- **Type:** `feature`
- **Assignee:** Ramya
- **Estimate:** 3.5 hours
- **Due Date:** 2026-07-01
- **Priority:** 🟡 High

**Description:**
Allow natural-language search over candidates using FTS and/or semantic similarity.

**Tasks:**
- [ ] Implement keyword search via SQLite FTS5
- [ ] Implement semantic search using embedding cosine similarity
- [ ] Create search mode toggle (keyword vs semantic)
- [ ] Handle empty results gracefully

**Acceptance Criteria:**
- FTS search returns results in < 1 second
- Semantic search returns top-N relevant candidates
- Queries like "Python developer with ML experience" return sensible results

---

## Milestone 4 — Streamlit UI
**Due: 2026-07-04** | **Phase 4**

---

### ISSUE-009 · Build Streamlit Upload & Processing UI

- **Type:** `feature`
- **Assignee:** Jayesh
- **Estimate:** 4 hours
- **Due Date:** 2026-07-02
- **Priority:** 🔴 Critical

**Description:**
Build the Upload Resumes tab in Streamlit that orchestrates the full processing pipeline.

**Tasks:**
- [ ] Create multi-file uploader (PDF/PNG/JPG)
- [ ] Show per-file processing progress bar
- [ ] Display extracted text preview
- [ ] Display parsed JSON in expandable section
- [ ] Show success/error status per file
- [ ] Trigger full pipeline: extract → parse → embed → store

**Acceptance Criteria:**
- Multiple files can be uploaded simultaneously
- Each file shows individual processing status
- Errors shown inline (not crashing the entire UI)

---

### ISSUE-010 · Build Candidate Ranking UI Tab

- **Type:** `feature`
- **Assignee:** Jayesh
- **Estimate:** 3.5 hours
- **Due Date:** 2026-07-03
- **Priority:** 🔴 Critical

**Description:**
Build the Rank Candidates tab showing JD input and ranked results.

**Tasks:**
- [ ] Job description text area input
- [ ] Skill filter input (comma-separated required skills)
- [ ] "Find Best Matches" button triggering ranking
- [ ] Ranked results table with: rank, name, email, skills, embedding score, skill score, final score %
- [ ] Highlight matched skills in results
- [ ] Score bar / progress indicator per candidate

**Acceptance Criteria:**
- Ranking results displayed within 10 seconds of button click
- Score breakdown visible per candidate
- Skills are color-coded (matched vs missing)

---

### ISSUE-011 · Build Search & Candidate Management UI Tabs

- **Type:** `feature`
- **Assignee:** Ramya
- **Estimate:** 3.5 hours
- **Due Date:** 2026-07-03
- **Priority:** 🟡 High

**Description:**
Build Search tab and All Candidates tab.

**Tasks:**
- [ ] Search tab with text input and mode selector
- [ ] Results shown as cards with candidate details
- [ ] All Candidates tab with full table view
- [ ] Delete candidate button with confirmation
- [ ] Settings tab: model path, DB path, clear DB

**Acceptance Criteria:**
- Search returns results in < 5 seconds
- Candidates can be deleted from the UI
- Table is sortable by name/date

---

## Milestone 5 — Testing & Polish
**Due: 2026-07-05** | **Phase 5**

---

### ISSUE-012 · Write Unit and Integration Tests

- **Type:** `testing`
- **Assignee:** Jayesh (test_extractor, test_parser, integration) · Ramya (test_ranker, coverage report)
- **Estimate:** 4 hours each
- **Due Date:** 2026-07-04
- **Priority:** 🟡 High

**Tasks:**
- [ ] `test_extractor.py` — 5+ test cases
- [ ] `test_parser.py` — valid JSON, malformed, empty input
- [ ] `test_ranker.py` — perfect match, zero match, partial
- [ ] Integration test: full pipeline with sample PDF
- [ ] `pytest` run with coverage report

**Acceptance Criteria:**
- All tests pass
- Test coverage ≥ 70% for `src/` modules

---

### ISSUE-013 · Final Documentation & Cleanup

- **Type:** `docs`
- **Assignee:** Ramya
- **Estimate:** 3.5 hours
- **Due Date:** 2026-07-05
- **Priority:** 🟢 Medium

**Tasks:**
- [ ] Update README with actual screenshots
- [ ] Add docstrings to all public functions
- [ ] Review and finalize SPEC.md
- [ ] Add CHANGELOG.md
- [ ] Tag `v1.0.0` release on GitLab

---

## Summary Table

| Issue | Title | Assignee | Estimate | Due Date | Priority |
|---|---|---|---|---|---|
| ISSUE-001 | Initialize Repo & Project Structure | Jayesh + Ramya | 1h each | 2026-06-28 | 🔴 Critical |
| ISSUE-002 | requirements.txt & Setup Guide | Jayesh + Ramya | 1h | 2026-06-28 | 🔴 Critical |
| ISSUE-003 | Text Extraction Module | **Jayesh** | 4h | 2026-06-29 | 🔴 Critical |
| ISSUE-004 | SQLite Database Module | **Ramya** | 4h | 2026-06-29 | 🔴 Critical |
| ISSUE-005 | LLM Resume Parser | **Jayesh** | 5h | 2026-06-30 | 🔴 Critical |
| ISSUE-006 | Embedding Module | **Ramya** | 3h | 2026-06-30 | 🟡 High |
| ISSUE-007 | Candidate Ranking Engine | **Jayesh** | 5h | 2026-07-01 | 🔴 Critical |
| ISSUE-008 | Search Feature Backend | **Ramya** | 3.5h | 2026-07-01 | 🟡 High |
| ISSUE-009 | Streamlit Upload UI | **Jayesh** | 4h | 2026-07-02 | 🔴 Critical |
| ISSUE-010 | Ranking UI Tab | **Jayesh** | 3.5h | 2026-07-03 | 🔴 Critical |
| ISSUE-011 | Search & Management UI | **Ramya** | 3.5h | 2026-07-03 | 🟡 High |
| ISSUE-012 | Unit & Integration Tests | Jayesh + Ramya | 4h each | 2026-07-04 | 🟡 High |
| ISSUE-013 | Final Docs & Cleanup | **Ramya** | 3.5h | 2026-07-05 | 🟢 Medium |

**Total Estimated Effort:** ~51.5 hours (~28.5h Jayesh · ~23h Ramya)

---

*Last Updated: 2026-06-28 — Team: Jayesh & Ramya*
