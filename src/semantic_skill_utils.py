"""Local semantic skill matching using sentence-transformers (AI-free API)."""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from src.skill_synonym_utils import normalize_skill_list


DEFAULT_MODEL = "all-MiniLM-L6-v2"
DEFAULT_THRESHOLD = 0.42


@lru_cache(maxsize=1)
def _load_model():
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(DEFAULT_MODEL), None
    except Exception as exc:
        return None, str(exc)


def semantic_model_available() -> tuple[bool, str]:
    model, error = _load_model()
    if model is None:
        return False, error or "Model unavailable"
    return True, DEFAULT_MODEL


def _encode_texts(texts: list[str]) -> np.ndarray | None:
    model, _ = _load_model()
    if model is None or not texts:
        return None
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(embeddings)


def extract_skills_semantic(
    text: str,
    candidate_skills: list[str],
    threshold: float = DEFAULT_THRESHOLD,
    max_matches: int = 30,
) -> list[str]:
    """
    Extract skills using embedding similarity between text and skill phrases.

    Falls back to empty list if sentence-transformers is unavailable.
    """
    if not text or not candidate_skills:
        return []

    skills = normalize_skill_list(candidate_skills)
    text_embedding = _encode_texts([text])
    if text_embedding is None:
        return []

    skill_embeddings = _encode_texts(skills)
    if skill_embeddings is None:
        return []

    scores = (skill_embeddings @ text_embedding[0]).flatten()
    matched = [
        skill
        for skill, score in sorted(zip(skills, scores), key=lambda row: -row[1])
        if score >= threshold
    ]
    return matched[:max_matches]


def merge_extraction_results(regex_skills: list[str], semantic_skills: list[str]) -> list[str]:
    """Merge regex and semantic extraction results."""
    return normalize_skill_list(list(regex_skills) + list(semantic_skills))


def get_semantic_match_scores(text: str, candidate_skills: list[str]) -> list[dict]:
    """Return ranked semantic match scores for debugging/UI."""
    skills = normalize_skill_list(candidate_skills)
    text_embedding = _encode_texts([text])
    skill_embeddings = _encode_texts(skills)
    if text_embedding is None or skill_embeddings is None:
        return []

    scores = (skill_embeddings @ text_embedding[0]).flatten()
    rows = [
        {"skill": skill, "semantic_score": round(float(score), 4)}
        for skill, score in zip(skills, scores)
    ]
    return sorted(rows, key=lambda row: -row["semantic_score"])
