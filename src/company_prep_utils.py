"""Company-specific interview preparation packs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def get_company_prep_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "company_prep_packs.json"


def load_company_prep_packs() -> dict:
    path = get_company_prep_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def list_companies() -> list[str]:
    return sorted(load_company_prep_packs().keys())


def get_company_pack(company: str) -> dict:
    return load_company_prep_packs().get(company, {})


def build_company_prep_summary(company: str, target_role: str = "", missing_skills: list[str] | None = None) -> str:
    """Generate a text prep summary for a company."""
    pack = get_company_pack(company)
    if not pack:
        return f"No prep pack found for {company}."

    missing = missing_skills or []
    focus = pack.get("hiring_focus", [])
    overlap = sorted(set(missing) & set(focus))

    lines = [
        f"CareerCompass Company Prep Pack — {company}",
        "=" * (32 + len(company)),
        f"Industry: {pack.get('industry', 'N/A')}",
        f"Headquarters: {pack.get('headquarters', 'N/A')}",
        f"Target role: {target_role or 'General'}",
        "",
        "Interview style:",
        pack.get("interview_style", "N/A"),
        "",
        "Core values:",
    ]
    for value in pack.get("core_values", []):
        lines.append(f"- {value}")

    lines.extend(["", "Hiring focus skills:"])
    for skill in focus:
        marker = "★" if skill in overlap else "-"
        lines.append(f"{marker} {skill}")

    if overlap:
        lines.extend(["", "Priority gaps to address for this company:"])
        for skill in overlap:
            lines.append(f"- {skill}")

    lines.extend(["", "Prep tips:"])
    for tip in pack.get("prep_tips", []):
        lines.append(f"- {tip}")

    lines.extend(["", "Sample questions:"])
    for question in pack.get("sample_questions", []):
        lines.append(f"- {question}")

    return "\n".join(lines)


def get_company_skill_overlap(company: str, skills: list[str]) -> pd.DataFrame:
    pack = get_company_pack(company)
    focus = pack.get("hiring_focus", [])
    rows = []
    skill_set = {str(s).strip().lower() for s in skills}
    for skill in focus:
        rows.append({"skill": skill, "in_profile": skill in skill_set, "company_priority": "High"})
    return pd.DataFrame(rows)
