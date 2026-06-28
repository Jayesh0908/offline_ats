"""
database.py — SQLite Persistence Module

Handles all database operations for the Offline ATS:
- Schema initialization
- Candidate CRUD
- Full-Text Search (FTS5)
- Embedding storage/retrieval
"""

import sqlite3
import json
import os
import numpy as np
from typing import Optional


def init_db(db_path: str) -> sqlite3.Connection:
    """
    Create the SQLite database and initialize tables if they don't exist.

    Args:
        db_path: Path to the SQLite .db file. Created if it doesn't exist.

    Returns:
        sqlite3.Connection instance.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS candidates (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT,
            phone       TEXT,
            skills      TEXT,
            education   TEXT,
            experience  TEXT,
            projects    TEXT,
            resume_path TEXT,
            raw_text    TEXT,
            json_data   TEXT,
            embedding   BLOB,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS candidates_fts
        USING fts5(
            name,
            skills,
            raw_text,
            content='candidates',
            content_rowid='id'
        );
    """)
    conn.commit()
    return conn


def insert_candidate(
    conn: sqlite3.Connection,
    candidate_data: dict,
    resume_path: str,
    raw_text: str,
    json_data: str,
    embedding: bytes
) -> int:
    """
    Insert a parsed candidate into the database.

    Args:
        conn: Active SQLite connection.
        candidate_data: Parsed dict with name, email, phone, skills, etc.
        resume_path: Path to the original resume file.
        raw_text: Raw extracted text from the resume.
        json_data: Full LLM-parsed JSON string.
        embedding: Serialized numpy float32 embedding as bytes.

    Returns:
        The row ID of the newly inserted candidate.
    """
    skills_json = json.dumps(candidate_data.get("skills", []))
    education_json = json.dumps(candidate_data.get("education", []))
    experience_json = json.dumps(candidate_data.get("experience", []))
    projects_json = json.dumps(candidate_data.get("projects", []))

    cursor = conn.execute(
        """
        INSERT INTO candidates
            (name, email, phone, skills, education, experience, projects,
             resume_path, raw_text, json_data, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            candidate_data.get("name", "Unknown"),
            candidate_data.get("email", ""),
            candidate_data.get("phone", ""),
            skills_json,
            education_json,
            experience_json,
            projects_json,
            resume_path,
            raw_text,
            json_data,
            embedding,
        ),
    )

    row_id = cursor.lastrowid

    # Update FTS index
    conn.execute(
        "INSERT INTO candidates_fts(rowid, name, skills, raw_text) VALUES (?, ?, ?, ?)",
        (row_id, candidate_data.get("name", ""), skills_json, raw_text),
    )
    conn.commit()
    return row_id


def get_all_candidates(conn: sqlite3.Connection) -> list[dict]:
    """
    Retrieve all candidates without their embedding blobs.

    Args:
        conn: Active SQLite connection.

    Returns:
        List of candidate dicts.
    """
    rows = conn.execute(
        """
        SELECT id, name, email, phone, skills, education,
               experience, projects, resume_path, created_at
        FROM candidates
        ORDER BY created_at DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def get_all_embeddings(conn: sqlite3.Connection) -> list[tuple[int, np.ndarray]]:
    """
    Retrieve all (candidate_id, embedding) pairs for ranking.

    Args:
        conn: Active SQLite connection.

    Returns:
        List of (id, numpy float32 array) tuples.
    """
    rows = conn.execute("SELECT id, embedding FROM candidates").fetchall()
    result = []
    for row in rows:
        if row["embedding"]:
            vec = np.frombuffer(row["embedding"], dtype=np.float32)
            result.append((row["id"], vec))
    return result


def search_candidates_fts(conn: sqlite3.Connection, query: str) -> list[dict]:
    """
    Full-text search over candidate name, skills, and raw resume text.

    Args:
        conn: Active SQLite connection.
        query: Search terms (e.g., "Python Machine Learning").

    Returns:
        List of matching candidate dicts.
    """
    rows = conn.execute(
        """
        SELECT c.id, c.name, c.email, c.phone, c.skills, c.education,
               c.experience, c.projects, c.resume_path, c.created_at
        FROM candidates c
        JOIN candidates_fts fts ON c.id = fts.rowid
        WHERE candidates_fts MATCH ?
        ORDER BY rank
        """,
        (query,),
    ).fetchall()
    return [dict(row) for row in rows]


def get_candidate_by_id(conn: sqlite3.Connection, candidate_id: int) -> Optional[dict]:
    """
    Retrieve a single candidate by ID.

    Args:
        conn: Active SQLite connection.
        candidate_id: The candidate's row ID.

    Returns:
        Candidate dict or None if not found.
    """
    row = conn.execute(
        "SELECT * FROM candidates WHERE id = ?", (candidate_id,)
    ).fetchone()
    return dict(row) if row else None


def delete_candidate(conn: sqlite3.Connection, candidate_id: int) -> None:
    """
    Delete a candidate and their FTS entry by ID.

    Args:
        conn: Active SQLite connection.
        candidate_id: The candidate's row ID.
    """
    conn.execute("DELETE FROM candidates_fts WHERE rowid = ?", (candidate_id,))
    conn.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
