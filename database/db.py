"""
SQLite database operations for the Offline ATS.
Stores candidate details, parsed JSON, resume paths, and embeddings.
"""
import sqlite3
import json
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import config


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory enabled."""
    config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(config.DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT DEFAULT '',
            email TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            skills TEXT DEFAULT '[]',
            education TEXT DEFAULT '[]',
            experience TEXT DEFAULT '[]',
            projects TEXT DEFAULT '[]',
            resume_path TEXT DEFAULT '',
            resume_text TEXT DEFAULT '',
            json_data TEXT DEFAULT '{}',
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create FTS5 virtual table for full-text search
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS candidates_fts USING fts5(
            name, email, skills, education, experience, projects,
            content='candidates', content_rowid='id'
        )
    """)

    # Create triggers to keep FTS index in sync
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS candidates_ai AFTER INSERT ON candidates BEGIN
            INSERT INTO candidates_fts(rowid, name, email, skills, education, experience, projects)
            VALUES (new.id, new.name, new.email, new.skills, new.education, new.experience, new.projects);
        END
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS candidates_ad AFTER DELETE ON candidates BEGIN
            INSERT INTO candidates_fts(candidates_fts, rowid, name, email, skills, education, experience, projects)
            VALUES ('delete', old.id, old.name, old.email, old.skills, old.education, old.experience, old.projects);
        END
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS candidates_au AFTER UPDATE ON candidates BEGIN
            INSERT INTO candidates_fts(candidates_fts, rowid, name, email, skills, education, experience, projects)
            VALUES ('delete', old.id, old.name, old.email, old.skills, old.education, old.experience, old.projects);
            INSERT INTO candidates_fts(rowid, name, email, skills, education, experience, projects)
            VALUES (new.id, new.name, new.email, new.skills, new.education, new.experience, new.projects);
        END
    """)

    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at {config.DATABASE_PATH}")


def insert_candidate(
    name: str,
    email: str,
    phone: str,
    skills: List[str],
    education: List[Dict],
    experience: List[Dict],
    projects: List[str],
    resume_path: str,
    resume_text: str,
    json_data: Dict[str, Any],
    embedding: Optional[np.ndarray] = None
) -> int:
    """Insert a new candidate record. Returns the inserted row ID."""
    conn = get_connection()
    cursor = conn.cursor()

    embedding_blob = None
    if embedding is not None:
        embedding_blob = embedding.astype(np.float32).tobytes()

    cursor.execute("""
        INSERT INTO candidates (name, email, phone, skills, education, experience, projects,
                                resume_path, resume_text, json_data, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        email,
        phone,
        json.dumps(skills),
        json.dumps(education),
        json.dumps(experience),
        json.dumps(projects),
        resume_path,
        resume_text,
        json.dumps(json_data),
        embedding_blob
    ))

    candidate_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"[DB] Inserted candidate: {name} (ID: {candidate_id})")
    return candidate_id


def get_all_candidates() -> List[sqlite3.Row]:
    """Retrieve all candidates."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_candidate_by_id(candidate_id: int) -> Optional[sqlite3.Row]:
    """Get a single candidate by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_candidate_count() -> int:
    """Get total number of candidates in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM candidates")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def search_candidates_fts(query: str) -> List[sqlite3.Row]:
    """Search candidates using FTS5 full-text search."""
    conn = get_connection()
    cursor = conn.cursor()
    # Escape special FTS characters and use prefix matching
    sanitized = query.replace("'", "''")
    fts_query = ' OR '.join(f'"{word}"' for word in sanitized.split())
    cursor.execute("""
        SELECT c.* FROM candidates c
        JOIN candidates_fts fts ON c.id = fts.rowid
        WHERE candidates_fts MATCH ?
        ORDER BY rank
    """, (fts_query,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_embeddings() -> List[Tuple[int, np.ndarray]]:
    """Retrieve all candidates that have embeddings stored."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, embedding FROM candidates WHERE embedding IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        if row["embedding"]:
            embedding = np.frombuffer(row["embedding"], dtype=np.float32)
            result.append((row["id"], embedding))
    return result


def update_embedding(candidate_id: int, embedding: np.ndarray):
    """Update the embedding for a specific candidate."""
    conn = get_connection()
    cursor = conn.cursor()
    embedding_blob = embedding.astype(np.float32).tobytes()
    cursor.execute("UPDATE candidates SET embedding = ? WHERE id = ?",
                   (embedding_blob, candidate_id))
    conn.commit()
    conn.close()


def delete_candidate(candidate_id: int):
    """Delete a candidate by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()
    print(f"[DB] Deleted candidate ID: {candidate_id}")


def delete_all_candidates():
    """Delete all candidates from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates")
    conn.commit()
    conn.close()
    print("[DB] Deleted all candidates")