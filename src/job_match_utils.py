"""Job description to CV match scoring utilities."""

from __future__ import annotations

import pandas as pd

from src.cv_gap_utils import compute_cv_market_gap, extract_cv_skills
from src.skill_analysis_utils import load_skill_dictionary_for_analysis
from src.skill_extraction import extract_skills_from_text, flatten_skill_dictionary
from src.skill_synonym_utils import expand_text_with_synonyms, normalize_skill_list


def extract_job_skills(job_description: str, skill_dictionary: dict | None = None) -> list[str]:
    """Extract skills from a job description."""
    skill_dict = skill_dictionary or load_skill_dictionary_for_analysis()
    if not skill_dict:
        return []
    all_skills = flatten_skill_dictionary(skill_dict)
    expanded = expand_text_with_synonyms(job_description)
    extracted = extract_skills_from_text(expanded, all_skills)
    return normalize_skill_list(extracted)


def extract_cv_skills_enhanced(cv_text: str, skill_dictionary: dict | None = None) -> list[str]:
    """Extract CV skills with synonym expansion."""
    skill_dict = skill_dictionary or load_skill_dictionary_for_analysis()
    expanded = expand_text_with_synonyms(cv_text)
    return extract_cv_skills(cv_text=expanded, skill_dictionary=skill_dict)


def compute_job_match(job_description: str, cv_text: str) -> dict:
    """Compute fit score between a job description and CV."""
    skill_dict = load_skill_dictionary_for_analysis()
    job_skills = extract_job_skills(job_description, skill_dict)
    cv_skills = extract_cv_skills_enhanced(cv_text, skill_dict)

    if not job_skills:
        return {
            "match_score": 0.0,
            "job_skills": [],
            "cv_skills": cv_skills,
            "matched_skills": [],
            "missing_skills": [],
            "extra_cv_skills": cv_skills,
            "job_skill_count": 0,
            "cv_skill_count": len(cv_skills),
            "message": "No skills detected in job description. Add more technical keywords.",
        }

    gap = compute_cv_market_gap(cv_skills=cv_skills, market_skills=job_skills)
    return {
        "match_score": gap.get("match_score", 0.0),
        "job_skills": job_skills,
        "cv_skills": cv_skills,
        "matched_skills": gap.get("matched_skills", []),
        "missing_skills": gap.get("missing_skills", []),
        "extra_cv_skills": gap.get("extra_cv_skills", []),
        "job_skill_count": len(job_skills),
        "cv_skill_count": len(cv_skills),
        "matched_count": gap.get("matched_count", 0),
        "missing_count": gap.get("missing_count", 0),
        "message": "",
    }


def build_job_match_dataframe(result: dict) -> pd.DataFrame:
    """Build skill-level match table."""
    rows = []
    matched = set(result.get("matched_skills", []))
    missing = set(result.get("missing_skills", []))
    for skill in result.get("job_skills", []):
        if skill in matched:
            status = "Matched"
        elif skill in missing:
            status = "Missing"
        else:
            status = "Unknown"
        rows.append({"job_skill": skill, "status": status})
    return pd.DataFrame(rows)


def classify_job_match_level(score: float) -> str:
    """Return human-readable match level."""
    if score >= 75:
        return "Strong Match"
    if score >= 50:
        return "Moderate Match"
    if score >= 25:
        return "Partial Match"
    return "Low Match"


def generate_job_match_report(result: dict, job_title: str = "") -> str:
    """Generate text report for job match."""
    lines = [
        "CareerCompass Job Match Report",
        "==============================",
        f"Job Title: {job_title or 'Not specified'}",
        f"Match Score: {result.get('match_score', 0.0):.2f}%",
        f"Match Level: {classify_job_match_level(float(result.get('match_score', 0.0)))}",
        "",
        f"Job skills detected: {result.get('job_skill_count', 0)}",
        f"CV skills detected: {result.get('cv_skill_count', 0)}",
        "",
        "Matched Skills:",
    ]
    for skill in result.get("matched_skills", []):
        lines.append(f"- {skill}")
    lines.extend(["", "Missing Skills:"])
    for skill in result.get("missing_skills", []):
        lines.append(f"- {skill}")
    lines.extend(["", "Extra CV Skills:"])
    for skill in result.get("extra_cv_skills", []):
        lines.append(f"- {skill}")
    return "\n".join(lines)
