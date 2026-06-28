"""
ranker.py — Candidate Ranking Engine

Ranks candidates against a job description using a hybrid score:

    Final Score = 0.6 × Cosine Similarity + 0.4 × Skill Match Ratio

- Cosine Similarity: semantic match between JD and resume embeddings
- Skill Match Ratio: fraction of required skills found in candidate's skills
"""

import json
import numpy as np
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Common tech skills for JD keyword extraction
TECH_SKILLS_VOCABULARY = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring",
    "sql", "mongodb", "postgresql", "mysql", "sqlite", "redis", "elasticsearch",
    "docker", "kubernetes", "aws", "azure", "gcp", "linux", "terraform",
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "scikit-learn",
    "git", "rest", "graphql", "html", "css", "sass", "webpack",
    "microservices", "kafka", "rabbitmq", "spark", "hadoop",
    "react native", "flutter", "swift", "kotlin", "android", "ios",
    "ci/cd", "devops", "agile", "scrum", "jira",
]

EMBEDDING_WEIGHT = 0.6
SKILL_WEIGHT = 0.4


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        vec_a: First vector (e.g., JD embedding).
        vec_b: Second vector (e.g., resume embedding).

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 if either vector has zero norm.
    """
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def extract_skills_from_jd(jd_text: str) -> list[str]:
    """
    Extract skill keywords from a job description.

    Uses vocabulary matching against a known tech skills list.
    Case-insensitive.

    Args:
        jd_text: Raw job description text.

    Returns:
        List of matched skill strings (lowercased).
    """
    jd_lower = jd_text.lower()
    found = [skill for skill in TECH_SKILLS_VOCABULARY if skill in jd_lower]
    return found


def compute_skill_match(candidate_skills: list[str], required_skills: list[str]) -> float:
    """
    Compute the fraction of required skills present in candidate's skill list.

    Args:
        candidate_skills: List of skills the candidate has.
        required_skills: List of skills required by the job description.

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 if required_skills is empty.
    """
    if not required_skills:
        return 0.0

    candidate_lower = {s.lower() for s in candidate_skills}
    matches = sum(1 for skill in required_skills if skill.lower() in candidate_lower)
    return matches / len(required_skills)


def rank_candidates(
    jd_text: str,
    jd_embedding: np.ndarray,
    candidates: list[dict],
    candidate_embeddings: list[tuple[int, np.ndarray]],
) -> list[dict]:
    """
    Score and rank candidates against a job description.

    Scoring formula:
        Final Score = 0.6 × Embedding_Similarity + 0.4 × Skill_Match

    Args:
        jd_text: Raw job description text.
        jd_embedding: 384-dim embedding of the job description.
        candidates: List of candidate dicts from the database.
        candidate_embeddings: List of (candidate_id, embedding_array) tuples.

    Returns:
        List of candidate dicts with added score fields, sorted descending by final_score.
        Each dict includes: embedding_score, skill_score, final_score, final_score_pct.
    """
    required_skills = extract_skills_from_jd(jd_text)
    logger.info(f"Extracted {len(required_skills)} required skills from JD")

    # Build a lookup of id → embedding
    embedding_map = {cid: emb for cid, emb in candidate_embeddings}

    # Build a lookup of id → candidate
    candidate_map = {c["id"]: c for c in candidates}

    results = []

    for cid, candidate in candidate_map.items():
        if cid not in embedding_map:
            continue

        resume_embedding = embedding_map[cid]
        emb_score = cosine_similarity(jd_embedding, resume_embedding)

        # Parse skills from JSON string if needed
        raw_skills = candidate.get("skills", "[]")
        if isinstance(raw_skills, str):
            try:
                candidate_skills = json.loads(raw_skills)
            except json.JSONDecodeError:
                candidate_skills = []
        else:
            candidate_skills = raw_skills

        skill_score = compute_skill_match(candidate_skills, required_skills)
        final_score = EMBEDDING_WEIGHT * emb_score + SKILL_WEIGHT * skill_score

        results.append({
            **candidate,
            "embedding_score": round(emb_score, 4),
            "skill_score": round(skill_score, 4),
            "final_score": round(final_score, 4),
            "final_score_pct": f"{final_score * 100:.1f}%",
            "matched_skills": [
                s for s in candidate_skills
                if s.lower() in {r.lower() for r in required_skills}
            ],
            "missing_skills": [
                s for s in required_skills
                if s.lower() not in {cs.lower() for cs in candidate_skills}
            ],
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)
    logger.info(f"Ranked {len(results)} candidates")
    return results
