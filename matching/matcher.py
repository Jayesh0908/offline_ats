"""
Candidate matching and ranking logic.
Computes embedding similarity and skill match scores.
"""
import json
import numpy as np
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import config
from embeddings.embedder import Embedder, create_jd_embedding
import database.db as db


@dataclass
class MatchResult:
    """Represents the matching result for a single candidate."""
    candidate_id: int
    name: str
    email: str
    skills: List[str]
    embedding_score: float
    skill_score: float
    final_score: float


def compute_skill_match(jd_skills: List[str], candidate_skills: List[str]) -> float:
    """
    Compute skill match score between job description skills and candidate skills.
    
    Args:
        jd_skills: List of skills required in the job description
        candidate_skills: List of skills the candidate has
        
    Returns:
        Skill match score (0.0 to 1.0)
    """
    if not jd_skills:
        return 1.0  # No skills specified, full score
    
    if not candidate_skills:
        return 0.0
    
    # Normalize both lists to lowercase for comparison
    jd_skills_lower = [s.strip().lower() for s in jd_skills if s.strip()]
    candidate_skills_lower = [s.strip().lower() for s in candidate_skills if s.strip()]
    
    if not jd_skills_lower:
        return 1.0
    
    # Count matching skills
    match_count = 0
    for jd_skill in jd_skills_lower:
        for cand_skill in candidate_skills_lower:
            # Check exact match or substring match
            if jd_skill == cand_skill or jd_skill in cand_skill or cand_skill in jd_skill:
                match_count += 1
                break
    
    return match_count / len(jd_skills_lower)


def extract_skills_from_jd(jd_text: str) -> List[str]:
    """
    Extract skills mentioned in a job description.
    Uses keyword matching against a list of common tech skills.
    
    Args:
        jd_text: Job description text
        
    Returns:
        List of identified skills
    """
    common_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "Go", "Rust",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring", "Express",
        "SQL", "MongoDB", "PostgreSQL", "MySQL", "Redis", "Docker", "Kubernetes",
        "AWS", "Azure", "GCP", "Git", "Linux", "REST", "GraphQL", "HTML", "CSS",
        "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning", "NLP",
        "Data Science", "Data Analysis", "Tableau", "Power BI",
        "Agile", "Scrum", "JIRA", "CI/CD", "Jenkins", "Terraform",
        "Full Stack", "Frontend", "Backend", "DevOps", "Mobile", "iOS", "Android",
        "Flutter", "React Native", "Swift", "Kotlin", "R", "MATLAB", "SAS",
        "Hadoop", "Spark", "Kafka", "RabbitMQ", "Elasticsearch", "Nginx",
        "Microservices", "API", "RESTful", "OOP", "Design Patterns",
        "Testing", "Unit Testing", "Integration Testing", "Selenium", "Cypress",
        "Leadership", "Team Management", "Project Management", "Communication"
    ]
    
    found_skills = []
    jd_lower = jd_text.lower()
    
    for skill in common_skills:
        skill_lower = skill.lower()
        if re.search(rf"(?<![\w+#.]){re.escape(skill_lower)}(?![\w+#.])", jd_lower):
            found_skills.append(skill)
    
    # Also check lines starting with dash, bullet, or after "Skills:" 
    skills_section = re.search(
        r'(?:skills|requirements|qualifications|technologies)[:\s]*(.+?)(?:\n\n|\Z)',
        jd_text, re.IGNORECASE | re.DOTALL
    )
    if skills_section:
        raw_skills = skills_section.group(1)
        for s in re.split(r'[,;•\n]', raw_skills):
            s = s.strip().strip('•-').strip()
            if s and len(s) < 50 and not s.startswith(('http', 'www')):
                found_skills.append(s)
    
    return list(set(found_skills))


def rank_candidates(jd_text: str) -> List[MatchResult]:
    """
    Rank all candidates based on job description match.
    
    Args:
        jd_text: Job description text
        
    Returns:
        List of MatchResult objects sorted by final score (descending)
    """
    # Get all candidates
    candidates = db.get_all_candidates()
    if not candidates:
        return []
    
    # Generate JD embedding
    jd_embedding = create_jd_embedding(jd_text)
    
    # Extract skills from JD
    jd_skills = extract_skills_from_jd(jd_text)
    print(f"[Matcher] Extracted {len(jd_skills)} skills from JD: {jd_skills}")
    
    # Initialize embedder for similarity computation
    embedder = Embedder()
    
    results = []
    
    for candidate in candidates:
        candidate_id = candidate["id"]
        name = candidate["name"] or "Unknown"
        email = candidate["email"] or ""
        skills = json.loads(candidate["skills"]) if candidate["skills"] else []
        
        # 1. Compute embedding similarity
        embedding_score = 0.0
        if candidate["embedding"]:
            candidate_embedding = np.frombuffer(candidate["embedding"], dtype=np.float32)
            embedding_score = embedder.compute_similarity(jd_embedding, candidate_embedding)
        
        # 2. Compute skill match score
        skill_score = compute_skill_match(jd_skills, skills)
        
        # 3. Compute final weighted score
        final_score = (
            config.EMBEDDING_WEIGHT * embedding_score +
            config.SKILL_MATCH_WEIGHT * skill_score
        )
        
        results.append(MatchResult(
            candidate_id=candidate_id,
            name=name,
            email=email,
            skills=skills,
            embedding_score=embedding_score,
            skill_score=skill_score,
            final_score=final_score
        ))
    
    # Sort by final score descending
    results.sort(key=lambda r: r.final_score, reverse=True)
    
    print(f"[Matcher] Ranked {len(results)} candidates")
    return results


def search_candidates(query: str) -> List[Dict[str, Any]]:
    """
    Search candidates using FTS or embedding similarity.
    
    Args:
        query: Search query string
        
    Returns:
        List of candidate dictionaries
    """
    # Try embedding-based search first
    embedder = Embedder()
    query_embedding = embedder.encode(query)
    
    # Get all candidates with embeddings
    candidates_with_embeddings = db.get_all_embeddings()
    
    scored_candidates = []
    for candidate_id, candidate_embedding in candidates_with_embeddings:
        similarity = embedder.compute_similarity(query_embedding, candidate_embedding)
        candidate = db.get_candidate_by_id(candidate_id)
        if candidate:
            scored_candidates.append((similarity, dict(candidate)))
    
    # Sort by similarity
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    
    # Also perform FTS search
    fts_results = db.search_candidates_fts(query)
    fts_ids = {r["id"] for r in fts_results}
    
    # Merge results: embedding-based first, then FTS results not already included
    seen_ids = set()
    merged_results = []
    
    for score, candidate in scored_candidates:
        if candidate["id"] not in seen_ids:
            candidate["search_score"] = round(float(score), 3)
            merged_results.append(candidate)
            seen_ids.add(candidate["id"])
    
    for row in fts_results:
        candidate = dict(row)
        if candidate["id"] not in seen_ids:
            candidate["search_score"] = 0.5  # Default score for FTS-only matches
            merged_results.append(candidate)
            seen_ids.add(candidate["id"])
    
    return merged_results
