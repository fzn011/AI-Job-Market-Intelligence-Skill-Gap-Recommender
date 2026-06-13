"""Multi-CV comparison utilities."""

from __future__ import annotations

import pandas as pd

from src.job_match_utils import extract_cv_skills_enhanced
from src.progress_tracker_utils import compute_skill_growth


def compare_cv_versions(cv_text_a: str, cv_text_b: str, label_a: str = "CV A", label_b: str = "CV B") -> dict:
    """Compare two CV texts and return skill differences."""
    skills_a = extract_cv_skills_enhanced(cv_text_a)
    skills_b = extract_cv_skills_enhanced(cv_text_b)
    growth = compute_skill_growth(skills_b, skills_a)

    only_a = sorted(set(skills_a) - set(skills_b))
    only_b = sorted(set(skills_b) - set(skills_a))
    shared = sorted(set(skills_a) & set(skills_b))

    return {
        "label_a": label_a,
        "label_b": label_b,
        "skills_a": skills_a,
        "skills_b": skills_b,
        "shared_skills": shared,
        "only_in_a": only_a,
        "only_in_b": only_b,
        "growth": growth,
        "count_a": len(skills_a),
        "count_b": len(skills_b),
        "shared_count": len(shared),
    }


def build_cv_comparison_dataframe(comparison: dict) -> pd.DataFrame:
    """Build side-by-side skill comparison table."""
    all_skills = sorted(set(comparison.get("skills_a", [])) | set(comparison.get("skills_b", [])))
    set_a = set(comparison.get("skills_a", []))
    set_b = set(comparison.get("skills_b", []))
    rows = []
    for skill in all_skills:
        in_a = skill in set_a
        in_b = skill in set_b
        if in_a and in_b:
            status = "Both"
        elif in_a:
            status = comparison.get("label_a", "CV A")
        else:
            status = comparison.get("label_b", "CV B")
        rows.append({"skill": skill, "status": status, "in_a": int(in_a), "in_b": int(in_b)})
    return pd.DataFrame(rows)


def generate_cv_comparison_report(comparison: dict) -> str:
    """Generate downloadable comparison report."""
    growth = comparison.get("growth", {})
    lines = [
        "CareerCompass CV Comparison Report",
        "==================================",
        f"{comparison.get('label_a', 'CV A')}: {comparison.get('count_a', 0)} skills",
        f"{comparison.get('label_b', 'CV B')}: {comparison.get('count_b', 0)} skills",
        f"Shared skills: {comparison.get('shared_count', 0)}",
        f"Skill growth: {growth.get('growth_percent', 0.0)}%",
        "",
        "Skills gained in B:",
    ]
    for skill in growth.get("gained_skills", []):
        lines.append(f"- {skill}")
    lines.extend(["", "Skills removed from A:", ""])
    for skill in growth.get("lost_skills", []):
        lines.append(f"- {skill}")
    return "\n".join(lines)
