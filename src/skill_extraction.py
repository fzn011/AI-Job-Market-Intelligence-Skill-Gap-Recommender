"""Skill extraction helpers for job descriptions."""

from collections import Counter
from pathlib import Path
import re

import pandas as pd

from src.utils import clean_text, load_json
from src.skill_synonym_utils import expand_text_with_synonyms, normalize_skill_list


def load_skill_dictionary(path: str | Path) -> dict:
    """Load skill dictionary JSON from disk."""
    return load_json(path)


# Backward-compatible alias
load_skills_dictionary = load_skill_dictionary


def flatten_skill_dictionary(skill_dict: dict) -> list[str]:
    """Flatten category-based skill dictionary into unique sorted skills."""
    unique_skills: set[str] = set()

    for skills in skill_dict.values():
        if isinstance(skills, list):
            for skill in skills:
                normalized = clean_text(skill)
                if normalized:
                    unique_skills.add(normalized)

    return sorted(unique_skills)


def _build_skill_pattern(skill: str) -> re.Pattern:
    """
    Build a regex pattern that reduces false positives.

    Uses strict alphanumeric boundaries so:
    - 'python' matches 'python programming'
    - 'r' does not match random words containing 'r'
    - multi-token/special-char skills (e.g., c++, ci/cd, power bi)
      are matched as phrases.
    """
    escaped = re.escape(skill)
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", flags=re.IGNORECASE)


def extract_skills_from_text(text: str, skills: list[str], use_semantic: bool = False) -> list[str]:
    """Extract matched skills from text using boundary-aware matching and optional semantic enrichment."""
    expanded_text = expand_text_with_synonyms(text)
    normalized_text = clean_text(expanded_text)
    if not normalized_text:
        return []

    matched_skills: set[str] = set()
    for raw_skill in skills:
        normalized_skill = clean_text(raw_skill)
        if not normalized_skill:
            continue

        pattern = _build_skill_pattern(normalized_skill)
        if pattern.search(normalized_text):
            matched_skills.add(normalized_skill)

    regex_results = normalize_skill_list(sorted(matched_skills))

    if use_semantic:
        from src.semantic_skill_utils import extract_skills_semantic, merge_extraction_results

        semantic_results = extract_skills_semantic(text, skills)
        return merge_extraction_results(regex_results, semantic_results)

    return regex_results


def extract_skills_from_dataframe(
    df: pd.DataFrame,
    text_column: str,
    skills: list[str],
) -> pd.DataFrame:
    """
    Apply skill extraction to a DataFrame text column.

    Adds:
    - extracted_skills: list[str]
    - skill_count: int
    """
    extracted_df = df.copy()
    extracted_df["extracted_skills"] = extracted_df[text_column].apply(
        lambda value: extract_skills_from_text(value, skills)
    )
    extracted_df["skill_count"] = extracted_df["extracted_skills"].apply(len)
    return extracted_df


def compute_skill_frequency(
    df: pd.DataFrame,
    skills_column: str = "extracted_skills",
) -> pd.DataFrame:
    """Count extracted skills and return frequency table."""
    counter: Counter = Counter()

    for row in df[skills_column]:
        if isinstance(row, list):
            counter.update(row)

    frequency_df = pd.DataFrame(
        [{"skill": skill, "frequency": count} for skill, count in counter.items()]
    )

    if frequency_df.empty:
        return pd.DataFrame(columns=["skill", "frequency"])

    return frequency_df.sort_values(
        by=["frequency", "skill"], ascending=[False, True]
    ).reset_index(drop=True)


def extract_skills() -> str:
    """Placeholder status helper."""
    return "Skill extraction module is ready."
