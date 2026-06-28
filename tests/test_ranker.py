"""
tests/test_ranker.py — Unit tests for src/ranker.py
"""

import json
import numpy as np
import pytest
from src.ranker import cosine_similarity, compute_skill_match, extract_skills_from_jd, rank_candidates


class TestCosineSimilarity:
    def test_identical_vectors(self):
        vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        assert cosine_similarity(vec, vec) == pytest.approx(1.0, abs=1e-5)

    def test_orthogonal_vectors(self):
        vec_a = np.array([1.0, 0.0], dtype=np.float32)
        vec_b = np.array([0.0, 1.0], dtype=np.float32)
        assert cosine_similarity(vec_a, vec_b) == pytest.approx(0.0, abs=1e-5)

    def test_zero_vector(self):
        vec_a = np.zeros(5, dtype=np.float32)
        vec_b = np.ones(5, dtype=np.float32)
        assert cosine_similarity(vec_a, vec_b) == 0.0


class TestComputeSkillMatch:
    def test_perfect_match(self):
        assert compute_skill_match(["React", "Python", "Docker"], ["React", "Python", "Docker"]) == pytest.approx(1.0)

    def test_partial_match(self):
        score = compute_skill_match(["React", "Node.js"], ["React", "Node.js", "Docker", "MongoDB"])
        assert score == pytest.approx(0.5)

    def test_no_match(self):
        assert compute_skill_match(["Java", "Spring"], ["React", "Node.js"]) == pytest.approx(0.0)

    def test_empty_required_skills(self):
        assert compute_skill_match(["React"], []) == 0.0

    def test_case_insensitive(self):
        score = compute_skill_match(["PYTHON", "react"], ["python", "React"])
        assert score == pytest.approx(1.0)


class TestExtractSkillsFromJd:
    def test_extracts_known_skills(self):
        jd = "We need a developer with React, Node.js, and Docker experience."
        skills = extract_skills_from_jd(jd)
        assert "react" in skills
        assert "docker" in skills

    def test_empty_jd(self):
        assert extract_skills_from_jd("") == []

    def test_no_known_skills(self):
        assert extract_skills_from_jd("We need a good communicator.") == []


class TestRankCandidates:
    def _make_embedding(self, value: float) -> np.ndarray:
        """Make a normalized 3-dim vector."""
        vec = np.array([value, 1 - value, 0.0], dtype=np.float32)
        return vec / np.linalg.norm(vec)

    def test_ranks_by_final_score(self):
        jd_embedding = self._make_embedding(1.0)
        jd_text = "React Node.js MongoDB"

        candidates = [
            {"id": 1, "name": "Alice", "email": "a@a.com", "skills": json.dumps(["React", "Node.js", "MongoDB"])},
            {"id": 2, "name": "Bob", "email": "b@b.com", "skills": json.dumps(["Java"])},
        ]
        embeddings = [
            (1, self._make_embedding(0.95)),
            (2, self._make_embedding(0.1)),
        ]

        ranked = rank_candidates(jd_text, jd_embedding, candidates, embeddings)
        assert ranked[0]["name"] == "Alice"
        assert ranked[1]["name"] == "Bob"
        assert ranked[0]["final_score"] >= ranked[1]["final_score"]

    def test_empty_candidates(self):
        result = rank_candidates("React", np.zeros(384), [], [])
        assert result == []

    def test_scores_in_range(self):
        jd_embedding = self._make_embedding(0.5)
        candidates = [
            {"id": 1, "name": "Test", "email": "t@t.com", "skills": json.dumps(["Python"])},
        ]
        embeddings = [(1, self._make_embedding(0.5))]

        ranked = rank_candidates("Python developer", jd_embedding, candidates, embeddings)
        assert 0.0 <= ranked[0]["final_score"] <= 1.0
