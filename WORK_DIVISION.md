# 👥 Work Division Plan — Offline ATS

**Project:** Offline Applicant Tracking System  
**Team Size:** 1 (Solo Project)  
**Developer:** Jayesh  
**Sprint Duration:** 2026-06-28 → 2026-07-05

---

## Overview

This is a solo project. The work is divided across logical phases to ensure steady, measurable progress each day. Each day has a clear deliverable and estimated hours.

---

## Daily Work Schedule

### Day 1 — 2026-06-28 (Today) · Planning & Setup
**Goal:** Submit Phase 1 deliverables. Repo ready with all documentation.

| Task | Hours | Issue |
|---|---|---|
| Write README.md | 1h | ISSUE-001 |
| Write SPEC.md | 1h | ISSUE-001 |
| Write ISSUES.md | 0.5h | ISSUE-001 |
| Write WORK_DIVISION.md | 0.5h | ISSUE-001 |
| Create .gitignore & requirements.txt | 1h | ISSUE-002 |
| Set up project directory structure | 0.5h | ISSUE-001 |
| Push to GitLab | 0.5h | ISSUE-001 |
| **Total** | **5h** | |

**Deliverable:** GitLab repo with full Phase 1 documentation ✅

---

### Day 2 — 2026-06-29 · Core Extraction & Database
**Goal:** Resume text extraction working + SQLite database operational.

| Task | Hours | Issue |
|---|---|---|
| Implement `src/extractor.py` (PDF + OCR) | 3h | ISSUE-003 |
| Implement `src/database.py` (schema + CRUD) | 2h | ISSUE-004 |
| Write `tests/test_extractor.py` | 1h | ISSUE-003 |
| Test with 3+ sample PDFs and images | 1h | ISSUE-003 |
| **Total** | **7h** | |

**Deliverable:** `extractor.py` and `database.py` fully implemented and tested.

---

### Day 3 — 2026-06-30 · LLM Parser + Embeddings
**Goal:** Local LLM parsing resumes → JSON. Embeddings generated and stored.

| Task | Hours | Issue |
|---|---|---|
| Download and test Phi-3 Mini GGUF | 1h | ISSUE-005 |
| Implement `src/parser.py` with prompt | 3h | ISSUE-005 |
| Implement regex fallback parser | 1h | ISSUE-005 |
| Implement `src/embedder.py` | 2h | ISSUE-006 |
| Test full extraction → parse → embed pipeline | 1h | ISSUE-005 |
| **Total** | **8h** | |

**Deliverable:** Full offline pipeline (text → structured JSON → embedding vector).

---

### Day 4 — 2026-07-01 · Ranking Engine
**Goal:** Candidate ranking against job descriptions working end-to-end.

| Task | Hours | Issue |
|---|---|---|
| Implement `src/ranker.py` (cosine sim) | 2h | ISSUE-007 |
| Implement skill extraction from JD | 1h | ISSUE-007 |
| Implement hybrid scoring formula | 1h | ISSUE-007 |
| Implement `src/utils.py` helpers | 0.5h | — |
| Write `tests/test_ranker.py` | 1.5h | ISSUE-007 |
| **Total** | **6h** | |

**Deliverable:** `ranker.py` producing correct ranked candidate lists.

---

### Day 5 — 2026-07-02 · Streamlit UI — Upload Tab + Search
**Goal:** Working UI for uploading resumes and searching candidates.

| Task | Hours | Issue |
|---|---|---|
| Create `app.py` skeleton with navigation | 1h | ISSUE-009 |
| Build Upload Resumes tab | 3h | ISSUE-009 |
| Implement Search feature backend | 2h | ISSUE-008 |
| Build Search UI tab | 1h | ISSUE-008 |
| **Total** | **7h** | |

**Deliverable:** Users can upload resumes and search through them via UI.

---

### Day 6 — 2026-07-03 · Streamlit UI — Ranking + Candidate Management
**Goal:** Full UI for ranking candidates and managing the database.

| Task | Hours | Issue |
|---|---|---|
| Build Rank Candidates tab | 3h | ISSUE-010 |
| Build All Candidates tab with delete | 1.5h | ISSUE-011 |
| Build Settings tab | 1h | ISSUE-011 |
| End-to-end manual test of full flow | 0.5h | — |
| **Total** | **6h** | |

**Deliverable:** Complete Streamlit application with all tabs functional.

---

### Day 7 — 2026-07-04–05 · Testing, Polish & Release
**Goal:** Tests written, bugs fixed, documentation updated, v1.0.0 tagged.

| Task | Hours | Issue |
|---|---|---|
| Write remaining unit tests | 2h | ISSUE-012 |
| Run pytest with coverage | 1h | ISSUE-012 |
| Fix bugs discovered in testing | 2h | — |
| Add screenshots to README | 0.5h | ISSUE-013 |
| Add docstrings to all modules | 1h | ISSUE-013 |
| Tag v1.0.0 release on GitLab | 0.5h | ISSUE-013 |
| **Total** | **7h** | |

**Deliverable:** Stable v1.0.0 release with tests and full documentation.

---

## Total Effort Breakdown

| Phase | Days | Est. Hours | Issues |
|---|---|---|---|
| Planning & Setup | Day 1 | 5h | ISSUE-001, 002 |
| Core Pipeline | Days 2–3 | 15h | ISSUE-003, 004, 005, 006 |
| Ranking & Search | Day 4 | 6h | ISSUE-007, 008 |
| Streamlit UI | Days 5–6 | 13h | ISSUE-009, 010, 011 |
| Testing & Polish | Day 7 | 7h | ISSUE-012, 013 |
| **Total** | **7 days** | **~46h** | **13 issues** |

---

## Module Ownership

| Module | Owner | Status |
|---|---|---|
| `app.py` | Jayesh | 🔲 Not started |
| `src/extractor.py` | Jayesh | 🔲 Not started |
| `src/parser.py` | Jayesh | 🔲 Not started |
| `src/embedder.py` | Jayesh | 🔲 Not started |
| `src/database.py` | Jayesh | 🔲 Not started |
| `src/ranker.py` | Jayesh | 🔲 Not started |
| `src/utils.py` | Jayesh | 🔲 Not started |
| `tests/` | Jayesh | 🔲 Not started |
| `README.md` | Jayesh | ✅ Complete |
| `SPEC.md` | Jayesh | ✅ Complete |
| `ISSUES.md` | Jayesh | ✅ Complete |
| `WORK_DIVISION.md` | Jayesh | ✅ Complete |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM too slow on CPU | High | High | Use smaller Qwen2.5-1.5B model as fallback |
| Tesseract not installed | Medium | Medium | Detect at startup, show clear instructions |
| GGUF model parse failure | Medium | High | Implement regex fallback in parser.py |
| Large resume causes context overflow | Medium | Medium | Truncate raw text to first 3000 tokens |
| SQLite corruption | Low | High | Auto-backup on startup |

---

## Definition of Done

A feature is **Done** when:
1. Code is implemented and committed to `main`
2. Unit tests written and passing
3. No crashes for happy-path scenarios
4. Error cases return informative messages (no silent failures)
5. Function has a docstring

---

*Work Division Plan v1.0 — 2026-06-28 — Solo Project: Jayesh*
