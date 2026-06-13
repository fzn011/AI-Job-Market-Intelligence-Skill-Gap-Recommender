"""Skill synonym normalization and text expansion utilities."""

from __future__ import annotations

import json
import re
from pathlib import Path

from src.utils import clean_text


def get_synonyms_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "skill_synonyms.json"


def load_skill_synonyms() -> dict[str, list[str]]:
    """Load canonical skill -> synonym list mapping."""
    path = get_synonyms_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        return {}
    cleaned: dict[str, list[str]] = {}
    for canonical, aliases in data.items():
        canonical_clean = clean_text(canonical)
        if not canonical_clean:
            continue
        alias_list = [clean_text(alias) for alias in aliases if alias]
        alias_list = [alias for alias in alias_list if alias]
        if canonical_clean not in alias_list:
            alias_list.insert(0, canonical_clean)
        cleaned[canonical_clean] = sorted(set(alias_list))
    return cleaned


def build_alias_to_canonical_map(synonyms: dict[str, list[str]] | None = None) -> dict[str, str]:
    """Build alias -> canonical lookup."""
    synonym_data = synonyms if synonyms is not None else load_skill_synonyms()
    mapping: dict[str, str] = {}
    for canonical, aliases in synonym_data.items():
        for alias in aliases:
            mapping[clean_text(alias)] = canonical
        mapping[canonical] = canonical
    return mapping


def normalize_skill_name(skill: str, alias_map: dict[str, str] | None = None) -> str:
    """Normalize a skill string to its canonical form when possible."""
    cleaned = clean_text(skill)
    if not cleaned:
        return ""
    lookup = alias_map if alias_map is not None else build_alias_to_canonical_map()
    return lookup.get(cleaned, cleaned)


def normalize_skill_list(skills: list[str] | None, alias_map: dict[str, str] | None = None) -> list[str]:
    """Normalize and deduplicate a list of skills."""
    if not skills:
        return []
    lookup = alias_map if alias_map is not None else build_alias_to_canonical_map()
    normalized = {normalize_skill_name(skill, lookup) for skill in skills if skill}
    normalized = {skill for skill in normalized if skill}
    return sorted(normalized)


def expand_text_with_synonyms(text: str, synonyms: dict[str, list[str]] | None = None) -> str:
    """Append canonical skill names when aliases appear in text to improve extraction."""
    if not text or not str(text).strip():
        return text

    synonym_data = synonyms if synonyms is not None else load_skill_synonyms()
    expanded_parts = [str(text)]
    lowered = f" {str(text).lower()} "

    for canonical, aliases in synonym_data.items():
        for alias in aliases:
            pattern = rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])"
            if re.search(pattern, lowered):
                expanded_parts.append(canonical)
                break

    return " ".join(expanded_parts)


def enrich_skills_dictionary_with_synonyms(skill_dict: dict) -> dict:
    """Return skill dictionary with synonym aliases added to each category list."""
    alias_map = build_alias_to_canonical_map()
    enriched: dict[str, list[str]] = {}

    for category, skills in skill_dict.items():
        if not isinstance(skills, list):
            continue
        bucket: set[str] = set()
        for skill in skills:
            canonical = normalize_skill_name(skill, alias_map)
            if canonical:
                bucket.add(canonical)
        enriched[category] = sorted(bucket)

    return enriched
