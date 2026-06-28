# 👥 Work Division Plan — Offline ATS

**Project:** Offline Applicant Tracking System  
**Team Size:** 2  
**Members:** Jayesh · Ramya  
**Sprint Duration:** 2026-06-28 → 2026-07-05

---

## Team Responsibilities

| Member | Primary Domain |
|---|---|
| **Jayesh** | Backend pipeline — Text extraction, Local LLM parsing, Embedding generation, Ranking engine |
| **Ramya** | Data & UI — SQLite database, Streamlit frontend, Search feature, Testing & documentation |

The split keeps each person's work largely independent so both can work in parallel without blocking each other.

---

## Daily Work Schedule

### Day 1 — 2026-06-28 (Today) · Planning & Setup
**Goal:** Submit Phase 1 deliverables. Repo ready with all documentation.

| Task | Assigned To | Hours | Issue |
|---|---|---|---|
| Write README.md | Jayesh | 1h | ISSUE-001 |
| Write SPEC.md | Jayesh | 1h | ISSUE-001 |
| Write ISSUES.md | Ramya | 0.5h | ISSUE-001 |
| Write WORK_DIVISION.md | Ramya | 0.5h | ISSUE-001 |
| Create `.gitignore` & `requirements.txt` | Jayesh | 0.5h | ISSUE-002 |
| Document Tesseract + model setup guide | Ramya | 0.5h | ISSUE-002 |
| Set up project directory structure | Jayesh | 0.5h | ISSUE-001 |
| Push to GitLab | Jayesh | 0.5h | ISSUE-001 |
| **Total** | | **5h** | |

**Deliverable:** GitLab repo with full Phase 1 documentation ✅

---

### Day 2 — 2026-06-29 · Core Extraction & Database

**Goal:** Text extraction pipeline + SQLite database both operational. Teams work in parallel.

#### Jayesh — Text Extraction

| Task | Hours | Issue |
|---|---|---|
| Implement `src/extractor.py` (PDF via PyMuPDF) | 2h | ISSUE-003 |
| Implement `extract_text_from_image()` (Tesseract OCR) | 1h | ISSUE-003 |
| Handle error cases (corrupt files, unsupported formats) | 0.5h | ISSUE-003 |
| Test with 3+ sample PDFs and image resumes | 0.5h | ISSUE-003 |
| **Jayesh Total** | **4h** | |

#### Ramya — SQLite Database

| Task | Hours | Issue |
|---|---|---|
| Implement `src/database.py` — schema + `init_db()` | 1h | ISSUE-004 |
| Implement `insert_candidate()` + FTS5 update trigger | 1h | ISSUE-004 |
| Implement `get_all_candidates()`, `get_all_embeddings()` | 0.5h | ISSUE-004 |
| Implement `search_candidates_fts()`, `delete_candidate()` | 0.5h | ISSUE-004 |
| Write integration tests for database round-trips | 1h | ISSUE-004 |
| **Ramya Total** | **4h** | |

**Deliverable:** `extractor.py` and `database.py` fully implemented and tested.

---

### Day 3 — 2026-06-30 · LLM Parser + Embeddings

**Goal:** Local LLM parses resumes → structured JSON. Embeddings generated and stored.

#### Jayesh — LLM Parser

| Task | Hours | Issue |
|---|---|---|
| Download and validate Phi-3 Mini GGUF model | 1h | ISSUE-005 |
| Implement `load_model()` with global cache | 1h | ISSUE-005 |
| Write and tune LLM prompt template | 1h | ISSUE-005 |
| Implement `parse_resume()` with JSON parsing | 1h | ISSUE-005 |
| Implement regex fallback for malformed output | 1h | ISSUE-005 |
| **Jayesh Total** | **5h** | |

#### Ramya — Embedding Module

| Task | Hours | Issue |
|---|---|---|
| Implement `load_embedding_model()` with caching | 1h | ISSUE-006 |
| Implement `embed_text()` — 384-dim float32 vector | 1h | ISSUE-006 |
| Implement `serialize_embedding()` / `deserialize_embedding()` | 0.5h | ISSUE-006 |
| Verify round-trip consistency + write unit tests | 0.5h | ISSUE-006 |
| **Ramya Total** | **3h** | |

**Deliverable:** Full offline pipeline: text → structured JSON → embedding vector.

---

### Day 4 — 2026-07-01 · Ranking Engine + Utilities

**Goal:** Candidate ranking against job descriptions working end-to-end.

#### Jayesh — Ranking Engine (Core Logic)

| Task | Hours | Issue |
|---|---|---|
| Implement `cosine_similarity()` using numpy | 1h | ISSUE-007 |
| Implement `extract_skills_from_jd()` keyword extraction | 1h | ISSUE-007 |
| Implement `rank_candidates()` with weighted formula | 1.5h | ISSUE-007 |
| Write `tests/test_ranker.py` (perfect/partial/zero match) | 1.5h | ISSUE-007 |
| **Jayesh Total** | **5h** | |

#### Ramya — Utils + Search Backend

| Task | Hours | Issue |
|---|---|---|
| Implement `src/utils.py` shared helpers | 1h | — |
| Implement keyword search via SQLite FTS5 | 1h | ISSUE-008 |
| Implement semantic search using embedding similarity | 1h | ISSUE-008 |
| Handle empty results and edge cases | 0.5h | ISSUE-008 |
| **Ramya Total** | **3.5h** | |

**Deliverable:** `ranker.py` producing correct ranked lists. Search backend ready.

---

### Day 5 — 2026-07-02 · Streamlit UI — Upload + Search Tabs

**Goal:** Working UI for uploading resumes and searching candidates.

#### Jayesh — Upload Pipeline Integration

| Task | Hours | Issue |
|---|---|---|
| Create `app.py` skeleton with sidebar navigation | 1h | ISSUE-009 |
| Build Upload Resumes tab — file uploader, progress, status | 2h | ISSUE-009 |
| Wire full pipeline: extract → parse → embed → store | 1h | ISSUE-009 |
| **Jayesh Total** | **4h** | |

#### Ramya — Search UI Tab

| Task | Hours | Issue |
|---|---|---|
| Build Search tab — text input, mode toggle (keyword/semantic) | 2h | ISSUE-011 |
| Display search results as candidate cards | 1h | ISSUE-011 |
| Handle empty results with friendly messaging | 0.5h | ISSUE-011 |
| **Ramya Total** | **3.5h** | |

**Deliverable:** Users can upload resumes and search through them via UI.

---

### Day 6 — 2026-07-03 · Streamlit UI — Ranking + Candidate Management

**Goal:** Full UI for ranking candidates and managing the database.

#### Jayesh — Ranking UI Tab

| Task | Hours | Issue |
|---|---|---|
| Build Rank Candidates tab — JD text area input | 1h | ISSUE-010 |
| Display ranked results with score breakdown + progress bars | 1.5h | ISSUE-010 |
| Highlight matched vs missing skills per candidate | 1h | ISSUE-010 |
| **Jayesh Total** | **3.5h** | |

#### Ramya — Candidate Management + Settings

| Task | Hours | Issue |
|---|---|---|
| Build All Candidates tab — sortable table with delete | 1.5h | ISSUE-011 |
| Build Settings tab — model path, DB path, clear DB | 1h | ISSUE-011 |
| End-to-end manual test of the full user flow | 1h | — |
| **Ramya Total** | **3.5h** | |

**Deliverable:** Complete Streamlit application with all tabs functional.

---

### Day 7 — 2026-07-04–05 · Testing, Polish & Release

**Goal:** Tests written, bugs fixed, documentation updated, v1.0.0 tagged.

#### Jayesh — Testing (Backend)

| Task | Hours | Issue |
|---|---|---|
| Write / complete `tests/test_extractor.py` | 1h | ISSUE-012 |
| Write / complete `tests/test_parser.py` | 1h | ISSUE-012 |
| Run integration test: full pipeline with sample PDF | 1h | ISSUE-012 |
| Fix backend bugs found during testing | 1h | — |
| **Jayesh Total** | **4h** | |

#### Ramya — Documentation & Release

| Task | Hours | Issue |
|---|---|---|
| Write / complete `tests/test_ranker.py` | 1h | ISSUE-012 |
| Run `pytest` with coverage report | 0.5h | ISSUE-012 |
| Add docstrings to all public functions | 1h | ISSUE-013 |
| Add screenshots to README | 0.5h | ISSUE-013 |
| Add `CHANGELOG.md` + tag `v1.0.0` release | 0.5h | ISSUE-013 |
| **Ramya Total** | **3.5h** | |

**Deliverable:** Stable v1.0.0 release with full tests and documentation.

---

## Total Effort Breakdown

| Phase | Days | Jayesh | Ramya | Total |
|---|---|---|---|---|
| Planning & Setup | Day 1 | 3h | 2h | 5h |
| Core Extraction & DB | Day 2 | 4h | 4h | 8h |
| LLM Parser & Embeddings | Day 3 | 5h | 3h | 8h |
| Ranking & Search | Day 4 | 5h | 3.5h | 8.5h |
| Streamlit UI (Upload + Search) | Day 5 | 4h | 3.5h | 7.5h |
| Streamlit UI (Rank + Manage) | Day 6 | 3.5h | 3.5h | 7h |
| Testing, Polish & Release | Day 7 | 4h | 3.5h | 7.5h |
| **Total** | **7 days** | **~28.5h** | **~23h** | **~51.5h** |

---

## Module Ownership

| Module | Owner | Status |
|---|---|---|
| `app.py` | Jayesh + Ramya | 🔲 Not started |
| `src/extractor.py` | Jayesh | 🔲 Not started |
| `src/parser.py` | Jayesh | 🔲 Not started |
| `src/ranker.py` | Jayesh | 🔲 Not started |
| `src/embedder.py` | Ramya | 🔲 Not started |
| `src/database.py` | Ramya | 🔲 Not started |
| `src/utils.py` | Ramya | 🔲 Not started |
| `tests/test_extractor.py` | Jayesh | 🔲 Not started |
| `tests/test_parser.py` | Jayesh | 🔲 Not started |
| `tests/test_ranker.py` | Ramya | 🔲 Not started |
| `README.md` | Jayesh | ✅ Complete |
| `SPEC.md` | Jayesh | ✅ Complete |
| `ISSUES.md` | Ramya | ✅ Complete |
| `WORK_DIVISION.md` | Ramya | ✅ Complete |

---

## Collaboration Rules

1. **Branching:** Each person works on a feature branch (`jayesh/feature-name` or `ramya/feature-name`) and raises a Merge Request to `main`.
2. **Integration point:** End of Day 2 — both `extractor.py` and `database.py` must be merged before Day 3 pipeline work begins.
3. **Code reviews:** Each MR must be reviewed by the other person before merge.
4. **Daily sync:** 15-minute standup at start of each day to report blockers.
5. **Shared DB schema:** Any changes to the SQLite schema must be agreed upon by both before implementation.

---

## Risk Register

| Risk | Likelihood | Impact | Owner | Mitigation |
|---|---|---|---|---|
| LLM too slow on CPU | High | High | Jayesh | Use smaller Qwen2.5-1.5B model as fallback |
| Tesseract not installed | Medium | Medium | Jayesh | Detect at startup, show clear instructions |
| GGUF model parse failure | Medium | High | Jayesh | Implement regex fallback in `parser.py` |
| Large resume causes context overflow | Medium | Medium | Jayesh | Truncate raw text to first 3000 tokens |
| SQLite schema mismatch between members | Medium | High | Ramya | Pin schema in `database.py`, communicate changes |
| Merge conflicts on `app.py` | Medium | Medium | Both | Split tabs into separate functions, merge carefully |

---

## Definition of Done

A feature is **Done** when:
1. Code is implemented and committed to a feature branch
2. MR raised and reviewed by the other team member
3. Unit tests written and passing
4. No crashes for happy-path scenarios
5. Error cases return informative messages (no silent failures)
6. Every public function has a docstring

---

*Work Division Plan v2.0 — 2026-06-28 — Team: Jayesh & Ramya*
