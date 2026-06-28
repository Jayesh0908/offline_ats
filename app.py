"""
<<<<<<< HEAD
Offline ATS (Applicant Tracking System)
Main Streamlit application for resume parsing, storage, and candidate ranking.
"""
import streamlit as st
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any

import config
from database.db import (
    init_db, insert_candidate, get_all_candidates, get_candidate_by_id,
    get_candidate_count, delete_candidate, delete_all_candidates, search_candidates_fts
)
from extraction.text_extractor import extract_text
from llm.local_llm import parse_resume
from embeddings.embedder import Embedder, create_resume_embedding
from matching.matcher import rank_candidates, search_candidates, MatchResult

# Page configuration
st.set_page_config(
    page_title="Offline ATS",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .candidate-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1E88E5;
    }
    .score-high {
        color: #2e7d32;
        font-weight: bold;
    }
    .score-medium {
        color: #f57f17;
        font-weight: bold;
    }
    .score-low {
        color: #c62828;
        font-weight: bold;
    }
    .skill-badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        margin: 0.2rem;
        font-size: 0.85rem;
    }
    .stat-box {
        background-color: #f0f4f8;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #1E88E5;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.uploaded_files = []
        st.session_state.processing = False
        st.session_state.rank_results = []
        st.session_state.search_results = []


def save_uploaded_file(uploaded_file) -> str:
    """
    Save an uploaded file to the uploads directory.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Path to the saved file
    """
    file_path = config.UPLOAD_DIR / uploaded_file.name
    
    # Handle duplicate filenames
    counter = 1
    while file_path.exists():
        stem = file_path.stem
        suffix = file_path.suffix
        file_path = config.UPLOAD_DIR / f"{stem}_{counter}{suffix}"
        counter += 1
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return str(file_path)


def process_resume(file_path: str) -> Dict[str, Any]:
    """
    Process a single resume: extract text, parse with LLM, generate embedding.
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        Dictionary with processing results
    """
    result = {
        "file_path": file_path,
        "success": False,
        "error": None,
        "candidate_id": None
    }
    
    try:
        # Step 1: Extract text
        with st.status(f"📄 Extracting text from {Path(file_path).name}...", expanded=False) as status:
            resume_text = extract_text(file_path)
            if not resume_text.strip():
                status.update(label=f"⚠️ No text extracted from {Path(file_path).name}", state="error")
                result["error"] = "No text could be extracted"
                return result
            status.update(label=f"✅ Text extracted ({len(resume_text)} chars)", state="complete")
        
        # Step 2: Parse with LLM
        with st.status(f"🤖 Parsing resume with local LLM...", expanded=False) as status:
            parsed_data = parse_resume(resume_text)
            if not parsed_data or not parsed_data.get("name"):
                status.update(label=f"⚠️ LLM parsing incomplete, using fallback", state="warning")
            else:
                status.update(label=f"✅ Parsed: {parsed_data.get('name', 'Unknown')}", state="complete")
        
        # Step 3: Generate embedding
        with st.status(f"🔢 Generating embedding...", expanded=False) as status:
            skills = parsed_data.get("skills", [])
            embedding = create_resume_embedding(resume_text, skills)
            status.update(label=f"✅ Embedding generated (dim={len(embedding)})", state="complete")
        
        # Step 4: Store in database
        with st.status(f"💾 Storing in database...", expanded=False) as status:
            candidate_id = insert_candidate(
                name=parsed_data.get("name", ""),
                email=parsed_data.get("email", ""),
                phone=parsed_data.get("phone", ""),
                skills=skills,
                education=parsed_data.get("education", []),
                experience=parsed_data.get("experience", []),
                projects=parsed_data.get("projects", []),
                resume_path=file_path,
                resume_text=resume_text,
                json_data=parsed_data,
                embedding=embedding
            )
            status.update(label=f"✅ Stored in database (ID: {candidate_id})", state="complete")
        
        result["success"] = True
        result["candidate_id"] = candidate_id
        result["name"] = parsed_data.get("name", "Unknown")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"[App] Error processing {file_path}: {e}")
    
    return result


def display_candidate_card(candidate: Dict[str, Any], score: float = None):
    """
    Display a candidate's information in a styled card.
    
    Args:
        candidate: Candidate data dictionary
        score: Optional match score to display
    """
    skills = json.loads(candidate["skills"]) if isinstance(candidate["skills"], str) else candidate.get("skills", [])
    education = json.loads(candidate["education"]) if isinstance(candidate["education"], str) else candidate.get("education", [])
    experience = json.loads(candidate["experience"]) if isinstance(candidate["experience"], str) else candidate.get("experience", [])
    projects = json.loads(candidate["projects"]) if isinstance(candidate["projects"], str) else candidate.get("projects", [])
    
    score_class = ""
    if score is not None:
        if score >= 0.8:
            score_class = "score-high"
        elif score >= 0.5:
            score_class = "score-medium"
        else:
            score_class = "score-low"
    
    with st.container():
        st.markdown(f'<div class="candidate-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"**{candidate.get('name', 'Unknown')}**")
            if candidate.get("email"):
                st.markdown(f"📧 {candidate['email']}")
            if candidate.get("phone"):
                st.markdown(f"📞 {candidate['phone']}")
        
        with col2:
            if skills:
                skills_html = " ".join(
                    f'<span class="skill-badge">{s}</span>' for s in skills[:8]
                )
                st.markdown(f"**Skills:** {skills_html}", unsafe_allow_html=True)
                if len(skills) > 8:
                    st.markdown(f"*+{len(skills) - 8} more*")
        
        with col3:
            if score is not None:
                st.markdown(f'<div style="text-align: center;">', unsafe_allow_html=True)
                st.markdown(f'<span class="{score_class}" style="font-size: 1.5rem;">{score:.0%}</span>', unsafe_allow_html=True)
                st.markdown(f'</div>', unsafe_allow_html=True)
        
        # Expandable details
        with st.expander("View Full Details"):
            if education:
                st.markdown("**🎓 Education**")
                for edu in education:
                    degree = edu.get("degree", "")
                    college = edu.get("college", "")
                    st.markdown(f"- {degree} at {college}" if degree and college else f"- {degree or college}")
            
            if experience:
                st.markdown("**💼 Experience**")
                for exp in experience:
                    company = exp.get("company", "")
                    role = exp.get("role", "")
                    years = exp.get("years", "")
                    years_str = f" ({years} years)" if years else ""
                    st.markdown(f"- {role} at {company}{years_str}" if role and company else f"- {role or company}{years_str}")
            
            if projects:
                st.markdown("**🚀 Projects**")
                for proj in projects:
                    st.markdown(f"- {proj}")
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_upload_tab():
    """Render the Resume Upload tab."""
    st.markdown('<p class="sub-header">Upload resumes in PDF, PNG, or JPG format</p>', unsafe_allow_html=True)
    
=======
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

>>>>>>> 7ae9a8a478eb985e8ef5c6c9eba5787b4ddcfbd9
    uploaded_files = st.file_uploader(
        "Choose resume files",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
<<<<<<< HEAD
        help="Supported formats: PDF, PNG, JPG"
    )
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) selected")
        
        if st.button("🚀 Process All Resumes", type="primary", use_container_width=True):
            st.session_state.processing = True
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name} ({i + 1}/{len(uploaded_files)})...")
                
                # Save file
                file_path = save_uploaded_file(uploaded_file)
                
                # Process resume
                result = process_resume(file_path)
                results.append(result)
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            st.session_state.processing = False
            
            # Show summary
            success_count = sum(1 for r in results if r["success"])
            fail_count = sum(1 for r in results if not r["success"])
            
            if success_count > 0:
                st.success(f"✅ Successfully processed {success_count} resume(s)")
            if fail_count > 0:
                st.error(f"❌ Failed to process {fail_count} resume(s)")
            
            # Show details
            for result in results:
                if result["success"]:
                    st.markdown(f"✅ **{result.get('name', 'Unknown')}** - ID: {result['candidate_id']}")
                else:
                    st.markdown(f"❌ **{Path(result['file_path']).name}** - {result.get('error', 'Unknown error')}")
            
            st.rerun()
    
    # Show existing candidates count
    count = get_candidate_count()
    if count > 0:
        st.markdown("---")
        st.markdown(f"📊 **{count} candidate(s)** in database")


def render_database_tab():
    """Render the Database tab showing all candidates."""
    st.markdown('<p class="sub-header">View and manage stored candidates</p>', unsafe_allow_html=True)
    
    candidates = get_all_candidates()
    
    if not candidates:
        st.info("No candidates in database. Upload resumes to get started.")
        return
    
    # Stats row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(candidates)}</div>
            <div class="stat-label">Total Candidates</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        with_embeddings = sum(1 for c in candidates if c["embedding"])
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{with_embeddings}</div>
            <div class="stat-label">With Embeddings</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
            delete_all_candidates()
            st.success("All candidates deleted!")
            st.rerun()
    
    st.markdown("---")
    
    # Display candidates
    for candidate in candidates:
        candidate_dict = dict(candidate)
        display_candidate_card(candidate_dict)
    
    # Download data option
    st.markdown("---")
    if st.button("📥 Export as JSON", use_container_width=True):
        export_data = []
        for c in candidates:
            c_dict = dict(c)
            # Remove binary embedding data from export
            c_dict.pop("embedding", None)
            c_dict.pop("resume_text", None)
            export_data.append(c_dict)
        
        st.download_button(
            label="Download JSON",
            data=json.dumps(export_data, indent=2, default=str),
            file_name="candidates_export.json",
            mime="application/json"
        )


def render_ranking_tab():
    """Render the Candidate Ranking tab."""
    st.markdown('<p class="sub-header">Enter a job description to rank candidates</p>', unsafe_allow_html=True)
    
    count = get_candidate_count()
    if count == 0:
        st.warning("No candidates in database. Upload resumes first.")
        return
    
    st.info(f"📊 {count} candidate(s) available for ranking")
    
    jd_text = st.text_area(
        "Job Description",
        height=250,
        placeholder="""Example:
Need a Full Stack Developer.

Skills:
- React
- Node.js
- MongoDB
- Docker

Experience:
2+ years

Responsibilities:
- Build and maintain web applications
- Work with cross-functional teams
- Write clean, scalable code""",
        help="Enter the job description to find the best matching candidates"
    )
    
    if st.button("🔍 Rank Candidates", type="primary", use_container_width=True):
        if not jd_text.strip():
            st.error("Please enter a job description")
            return
        
        with st.spinner("Ranking candidates..."):
            results = rank_candidates(jd_text)
            st.session_state.rank_results = results
        
        if not results:
            st.warning("No candidates to rank")
            return
        
        st.success(f"Ranked {len(results)} candidate(s)")
    
    # Display ranking results
    if st.session_state.rank_results:
        st.markdown("---")
        st.markdown("## 📊 Ranking Results")
        
        # Top candidates summary
        top_n = min(3, len(st.session_state.rank_results))
        if top_n > 0:
            st.markdown("### 🏆 Top Candidates")
            cols = st.columns(top_n)
            for i, result in enumerate(st.session_state.rank_results[:top_n]):
                with cols[i]:
                    score_pct = result.final_score * 100
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-number">{score_pct:.0f}%</div>
                        <div class="stat-label">{result.name}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Full ranking table
        st.markdown("### Full Ranking")
        
        for i, result in enumerate(st.session_state.rank_results):
            candidate = get_candidate_by_id(result.candidate_id)
            if candidate:
                candidate_dict = dict(candidate)
                display_candidate_card(candidate_dict, result.final_score)
                
                # Show score breakdown
                with st.expander("Score Breakdown"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Embedding Similarity", f"{result.embedding_score:.1%}")
                    with col2:
                        st.metric("Skill Match", f"{result.skill_score:.1%}")
                    with col3:
                        st.metric("Final Score", f"{result.final_score:.1%}")
                    
                    st.markdown(f"""
                    **Formula:** `0.6 × {result.embedding_score:.3f} + 0.4 × {result.skill_score:.3f} = {result.final_score:.3f}`
                    """)


def render_search_tab():
    """Render the Search tab."""
    st.markdown('<p class="sub-header">Search candidates by skills, experience, or keywords</p>', unsafe_allow_html=True)
    
    count = get_candidate_count()
    if count == 0:
        st.warning("No candidates in database. Upload resumes first.")
        return
    
    search_query = st.text_input(
        "Search Query",
        placeholder="e.g., Candidates with React and Node experience",
        help="Search using natural language or keywords"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        search_type = st.selectbox("Method", ["Hybrid", "Semantic", "Keyword"])
    
    if st.button("🔍 Search", type="primary", use_container_width=True):
        if not search_query.strip():
            st.error("Please enter a search query")
            return
        
        with st.spinner("Searching..."):
            if search_type == "Keyword":
                results = [dict(r) for r in search_candidates_fts(search_query)]
                for r in results:
                    r["search_score"] = 0.5
                st.session_state.search_results = results
            else:
                results = search_candidates(search_query)
                st.session_state.search_results = results
        
        if not st.session_state.search_results:
            st.warning("No matching candidates found")
        else:
            st.success(f"Found {len(st.session_state.search_results)} matching candidate(s)")
    
    # Display search results
    if st.session_state.search_results:
        st.markdown("---")
        st.markdown("## 🔍 Search Results")
        
        for candidate in st.session_state.search_results:
            score = candidate.get("search_score")
            display_candidate_card(candidate, score)


def main():
    """Main application entry point."""
    init_session_state()
    
    # Initialize database
    init_db()
    
    # Header
    st.markdown('<h1 class="main-header">📋 Offline ATS</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">AI-powered Applicant Tracking System — 100% offline, no external APIs</p>',
        unsafe_allow_html=True
    )
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Upload Resumes",
        "🗄️ Database",
        "🏆 Rank Candidates",
        "🔍 Search"
    ])
    
    with tab1:
        render_upload_tab()
    
    with tab2:
        render_database_tab()
    
    with tab3:
        render_ranking_tab()
    
    with tab4:
        render_search_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #999; font-size: 0.8rem;">'
        'Offline ATS | Built with Streamlit + SQLite + Local LLM | '
        'All processing is done locally on your machine 🔒</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
=======
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
>>>>>>> 7ae9a8a478eb985e8ef5c6c9eba5787b4ddcfbd9
