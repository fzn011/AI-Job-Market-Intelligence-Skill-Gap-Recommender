"""Curated free learning resource lookup by skill."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def get_learning_resources_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "learning_resources.json"


def load_learning_resources() -> dict:
    path = get_learning_resources_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def get_resources_for_skill(skill: str) -> list[dict]:
    """Return learning resources for one skill."""
    resources = load_learning_resources()
    return list(resources.get(str(skill).strip().lower(), []))


def get_resources_for_skills(skills: list[str], max_per_skill: int = 2) -> pd.DataFrame:
    """Return dataframe of learning resources for multiple skills."""
    rows = []
    for skill in skills:
        skill_clean = str(skill).strip().lower()
        for resource in get_resources_for_skill(skill_clean)[:max_per_skill]:
            rows.append(
                {
                    "skill": skill_clean,
                    "title": resource.get("title", ""),
                    "url": resource.get("url", ""),
                    "type": resource.get("type", ""),
                    "provider": resource.get("provider", ""),
                }
            )
    return pd.DataFrame(rows)


def summarize_learning_coverage(skills: list[str]) -> dict:
    """Summarize how many skills have curated resources."""
    covered = [skill for skill in skills if get_resources_for_skill(skill)]
    return {
        "requested_skills": len(skills),
        "skills_with_resources": len(covered),
        "coverage_percent": round((len(covered) / len(skills)) * 100, 2) if skills else 0.0,
        "uncovered_skills": [skill for skill in skills if skill not in covered],
    }
