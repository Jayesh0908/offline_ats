"""
app.py — Offline ATS Streamlit Application

Main entry point for the Applicant Tracking System.
Runs entirely offline — no external APIs used.

Usage:
    streamlit run app.py
"""

import streamlit as st

# Page config must be first Streamlit call
st.set_page_config(
    page_title="Offline ATS — Applicant Tracking System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

import os
import json
import logging

from src.utils import setup_logging, save_uploaded_file

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "ats.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
MODEL_PATH = os.path.join(BASE_DIR, "models", "phi3-mini.gguf")

# ── Session State Init ──────────────────────────────────────────────────────────
if "db_conn" not in st.session_state:
    from src.database import init_db
    st.session_state.db_conn = init_db(DB_PATH)

if "embedding_model" not in st.session_state:
    st.session_state.embedding_model = None

if "llm_model" not in st.session_state:
    st.session_state.llm_model = None

conn = st.session_state.db_conn


# ── Helpers ─────────────────────────────────────────────────────────────────────
def get_embedding_model():
    if st.session_state.embedding_model is None:
        with st.spinner("Loading embedding model (first time only)..."):
            from src.embedder import load_embedding_model
            st.session_state.embedding_model = load_embedding_model()
    return st.session_state.embedding_model


def get_llm_model():
    if st.session_state.llm_model is None:
        if not os.path.exists(MODEL_PATH):
            st.error(
                f"❌ GGUF model not found at `{MODEL_PATH}`\n\n"
                "Please download Phi-3 Mini GGUF from HuggingFace and place it in the `models/` directory."
            )
            return None
        with st.spinner("Loading LLM model (may take 30–60 seconds)..."):
            from src.parser import load_model
            st.session_state.llm_model = load_model(MODEL_PATH)
    return st.session_state.llm_model


# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/resume.png", width=60)
    st.title("🧠 Offline ATS")
    st.caption("100% local • No internet required")
    st.divider()

    tab_selection = st.radio(
        "Navigate",
        ["📤 Upload Resumes", "🏆 Rank Candidates", "🔍 Search", "📋 All Candidates", "⚙️ Settings"],
        label_visibility="collapsed",
    )
    st.divider()
    from src.database import get_all_candidates
    count = len(get_all_candidates(conn))
    st.metric("Total Candidates", count)


# ── Tab: Upload Resumes ─────────────────────────────────────────────────────────
if tab_selection == "📤 Upload Resumes":
    st.title("📤 Upload Resumes")
    st.write("Upload PDF or image resumes. Each file will be processed through the local AI pipeline.")

    uploaded_files = st.file_uploader(
        "Choose resume files",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Supported formats: PDF, PNG, JPG",
    )

    if uploaded_files and st.button("⚡ Process Resumes", type="primary"):
        from src.extractor import extract_text
        from src.parser import parse_resume
        from src.embedder import embed_text, serialize_embedding
        from src.database import insert_candidate

        llm = get_llm_model()
        embedder = get_embedding_model()

        if llm is None or embedder is None:
            st.stop()

        for uploaded_file in uploaded_files:
            with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                try:
                    # Save file
                    file_bytes = uploaded_file.read()
                    file_path = save_uploaded_file(file_bytes, uploaded_file.name, UPLOAD_DIR)
                    st.write(f"✅ Saved to: `{file_path}`")

                    # Extract text
                    with st.spinner("Extracting text..."):
                        raw_text = extract_text(file_path)
                    st.write(f"📝 Extracted {len(raw_text)} characters")
                    with st.expander("Preview extracted text"):
                        st.text(raw_text[:1000] + ("..." if len(raw_text) > 1000 else ""))

                    # Parse with LLM
                    with st.spinner("Parsing with local LLM..."):
                        parsed = parse_resume(raw_text, llm)
                    st.write("🤖 LLM parsing complete")
                    with st.expander("Parsed JSON"):
                        st.json(parsed)

                    # Generate embedding
                    with st.spinner("Generating embedding..."):
                        embedding = embed_text(raw_text, embedder)
                        embedding_blob = serialize_embedding(embedding)

                    # Store in DB
                    insert_candidate(
                        conn, parsed, file_path, raw_text,
                        json.dumps(parsed), embedding_blob
                    )
                    st.success(f"✅ {parsed.get('name', 'Candidate')} added to database!")

                except Exception as e:
                    st.error(f"❌ Error processing {uploaded_file.name}: {e}")
                    logger.exception(f"Failed to process {uploaded_file.name}")


# ── Tab: Rank Candidates ────────────────────────────────────────────────────────
elif tab_selection == "🏆 Rank Candidates":
    st.title("🏆 Rank Candidates")
    st.write("Enter a job description to find and rank the best-matching candidates.")

    jd_text = st.text_area(
        "Job Description",
        height=200,
        placeholder="e.g. We need a Full Stack Developer with React, Node.js, MongoDB, and Docker. 2+ years of experience required.",
    )

    top_n = st.slider("Show top N candidates", min_value=1, max_value=50, value=10)

    if st.button("🔍 Find Best Matches", type="primary") and jd_text.strip():
        from src.embedder import embed_text
        from src.database import get_all_candidates, get_all_embeddings
        from src.ranker import rank_candidates

        embedder = get_embedding_model()
        if embedder is None:
            st.stop()

        with st.spinner("Computing match scores..."):
            jd_embedding = embed_text(jd_text, embedder)
            candidates = get_all_candidates(conn)
            embeddings = get_all_embeddings(conn)
            ranked = rank_candidates(jd_text, jd_embedding, candidates, embeddings)

        if not ranked:
            st.info("No candidates found. Please upload some resumes first.")
        else:
            st.write(f"**Found {len(ranked)} candidates — showing top {min(top_n, len(ranked))}**")
            st.divider()

            for i, c in enumerate(ranked[:top_n], 1):
                with st.container():
                    cols = st.columns([0.5, 3, 2, 2, 2])
                    cols[0].markdown(f"### #{i}")
                    cols[1].markdown(f"**{c.get('name', 'N/A')}**  \n📧 {c.get('email', '')}")
                    cols[2].markdown(f"**Final Score**  \n### {c['final_score_pct']}")
                    cols[3].markdown(f"Semantic: `{c['embedding_score']:.2%}`  \nSkill: `{c['skill_score']:.2%}`")

                    skills = json.loads(c.get("skills", "[]")) if isinstance(c.get("skills"), str) else c.get("skills", [])
                    skills_str = " · ".join(skills[:8]) if skills else "No skills listed"
                    cols[4].markdown(f"**Skills**  \n{skills_str}")

                    st.progress(c["final_score"])
                    st.divider()


# ── Tab: Search ─────────────────────────────────────────────────────────────────
elif tab_selection == "🔍 Search":
    st.title("🔍 Search Candidates")

    search_mode = st.radio("Search Mode", ["Keyword (Fast)", "Semantic (AI)"], horizontal=True)
    query = st.text_input("Search query", placeholder="e.g. Python developer with machine learning experience")

    if st.button("Search", type="primary") and query.strip():
        from src.database import search_candidates_fts, get_all_candidates, get_all_embeddings
        from src.embedder import embed_text
        from src.ranker import rank_candidates

        if search_mode == "Keyword (Fast)":
            results = search_candidates_fts(conn, query)
            for c in results:
                st.markdown(f"**{c['name']}** — {c['email']}")
                st.caption(f"Skills: {c.get('skills', '')}")
                st.divider()
        else:
            embedder = get_embedding_model()
            q_embedding = embed_text(query, embedder)
            candidates = get_all_candidates(conn)
            embeddings = get_all_embeddings(conn)
            ranked = rank_candidates(query, q_embedding, candidates, embeddings)
            for c in ranked[:20]:
                st.markdown(f"**{c['name']}** — Score: `{c['final_score_pct']}`")
                st.caption(f"Email: {c.get('email', '')} | Skills: {c.get('skills', '')}")
                st.divider()


# ── Tab: All Candidates ─────────────────────────────────────────────────────────
elif tab_selection == "📋 All Candidates":
    st.title("📋 All Candidates")

    from src.database import get_all_candidates, delete_candidate
    candidates = get_all_candidates(conn)

    if not candidates:
        st.info("No candidates in the database yet. Upload some resumes to get started.")
    else:
        for c in candidates:
            with st.expander(f"👤 {c['name']} — {c.get('email', 'No email')}"):
                cols = st.columns([3, 1])
                cols[0].markdown(f"**Phone:** {c.get('phone', 'N/A')}  \n**Added:** {c.get('created_at', '')}")
                skills = json.loads(c.get("skills", "[]")) if isinstance(c.get("skills"), str) else []
                cols[0].markdown(f"**Skills:** {', '.join(skills) if skills else 'None'}")
                if cols[1].button("🗑️ Delete", key=f"del_{c['id']}"):
                    delete_candidate(conn, c["id"])
                    st.rerun()


# ── Tab: Settings ───────────────────────────────────────────────────────────────
elif tab_selection == "⚙️ Settings":
    st.title("⚙️ Settings")

    st.subheader("Model Configuration")
    st.code(f"LLM Model Path: {MODEL_PATH}")
    st.code(f"Embedding Model: all-MiniLM-L6-v2")

    st.subheader("Database")
    st.code(f"Database Path: {DB_PATH}")

    st.subheader("Danger Zone")
    if st.button("🗑️ Clear Entire Database", type="secondary"):
        confirm = st.checkbox("I understand this will delete ALL candidate data")
        if confirm:
            conn.execute("DELETE FROM candidates")
            conn.execute("DELETE FROM candidates_fts")
            conn.commit()
            st.success("Database cleared.")
            st.rerun()
