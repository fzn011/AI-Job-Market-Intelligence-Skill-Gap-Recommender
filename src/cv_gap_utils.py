"""Reusable helpers for CV-to-market skill gap analysis."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

import pandas as pd

from src.dashboard_utils import parse_extracted_skills
from src.recommendation_engine import compute_skill_gap, recommend_projects_for_missing_skills
from src.skill_analysis_utils import categorize_skill
from src.skill_extraction import extract_skills_from_text, flatten_skill_dictionary


ROLE_KEYWORDS: dict[str, list[str]] = {
    "Data Analyst": ["data analyst", "analytics analyst"],
    "Data Scientist": ["data scientist"],
    "Machine Learning Engineer": ["machine learning engineer", "ml engineer"],
    "AI Engineer": ["ai engineer", "artificial intelligence engineer"],
    "BI Analyst": ["bi analyst", "business intelligence analyst"],
    "Data Engineer": ["data engineer"],
    "GenAI Engineer": ["genai engineer", "generative ai engineer", "llm engineer"],
    "Risk Data Analyst": ["risk data analyst", "credit risk analyst"],
    "Product Data Analyst": ["product data analyst"],
    "Junior Data Scientist": ["junior data scientist", "entry-level data scientist"],
    "Overall Market": [],
}

HIGH_PRIORITY_SKILLS = {
    "python",
    "sql",
    "machine learning",
    "pandas",
    "numpy",
    "scikit-learn",
    "power bi",
    "data visualization",
}

MEDIUM_PRIORITY_SKILLS = {
    "docker",
    "fastapi",
    "streamlit",
    "mlflow",
    "rag",
    "llm",
    "nlp",
    "pytorch",
    "tensorflow",
    "xgboost",
    "lightgbm",
    "postgresql",
}


def normalize_skill_list(skills: list[str] | None) -> list[str]:
    """Clean, normalize, deduplicate, and sort a skill list."""
    if not skills:
        return []

    normalized = {
        str(skill).strip().lower()
        for skill in skills
        if skill is not None and str(skill).strip()
    }
    return sorted(normalized)


def get_market_skills_from_jobs(
    jobs_df: pd.DataFrame,
    top_n: int | None = 30,
) -> list[str]:
    """Extract most frequent market-demanded skills from processed jobs."""
    if jobs_df.empty or "extracted_skills" not in jobs_df.columns:
        return []

    counter: Counter[str] = Counter()
    for value in jobs_df["extracted_skills"]:
        parsed_skills = parse_extracted_skills(value)
        normalized_skills = normalize_skill_list(parsed_skills)
        counter.update(normalized_skills)

    if not counter:
        return []

    ordered = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    if top_n is not None:
        ordered = ordered[: max(0, int(top_n))]

    return [skill for skill, _ in ordered]


def _contains_keyword(value: str, keywords: list[str]) -> bool:
    text = str(value).strip().lower()
    if not text:
        return False

    for keyword in keywords:
        pattern = rf"(^|[^a-z0-9]){re.escape(keyword.lower())}([^a-z0-9]|$)"
        if re.search(pattern, text):
            return True
    return False


def get_market_skills_by_target_role(
    jobs_df: pd.DataFrame,
    target_role: str,
    top_n: int | None = 25,
) -> list[str]:
    """Return top market skills for a selected target role, with robust fallback."""
    if jobs_df.empty:
        return []

    normalized_role = str(target_role).strip()
    if normalized_role == "Overall Market":
        return get_market_skills_from_jobs(jobs_df, top_n=top_n)

    role_keywords = ROLE_KEYWORDS.get(normalized_role, [normalized_role.lower()])

    matched_frames: list[pd.DataFrame] = []

    if "job_type" in jobs_df.columns:
        job_type_mask = (
            jobs_df["job_type"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            .eq(normalized_role.lower())
        )
        if job_type_mask.any():
            matched_frames.append(jobs_df[job_type_mask])

    if "job_title" in jobs_df.columns:
        job_title_mask = jobs_df["job_title"].fillna("").apply(
            lambda value: _contains_keyword(value, role_keywords)
        )
        if job_title_mask.any():
            matched_frames.append(jobs_df[job_title_mask])

    if matched_frames:
        role_df = pd.concat(matched_frames, axis=0).drop_duplicates()
    else:
        role_df = pd.DataFrame()

    if role_df.empty:
        return get_market_skills_from_jobs(jobs_df, top_n=top_n)

    return get_market_skills_from_jobs(role_df, top_n=top_n)


def extract_cv_skills(
    cv_text: str,
    skill_dictionary: dict,
) -> list[str]:
    """Extract skills from pasted CV/profile text using existing extraction utilities."""
    if not cv_text or not str(cv_text).strip():
        return []

    if not isinstance(skill_dictionary, dict) or not skill_dictionary:
        return []

    flattened_skills = flatten_skill_dictionary(skill_dictionary)
    if not flattened_skills:
        return []

    extracted = extract_skills_from_text(cv_text, flattened_skills)
    return normalize_skill_list(extracted)


def compute_cv_market_gap(
    cv_skills: list[str],
    market_skills: list[str],
) -> dict:
    """Compare CV skills vs market-demanded skills and compute detailed gap stats."""
    normalized_cv_skills = normalize_skill_list(cv_skills)
    normalized_market_skills = normalize_skill_list(market_skills)

    base_gap = compute_skill_gap(normalized_cv_skills, normalized_market_skills)
    matched_skills = sorted(base_gap.get("matched_skills", []))
    missing_skills = sorted(base_gap.get("missing_skills", []))

    cv_set = set(normalized_cv_skills)
    market_set = set(normalized_market_skills)
    extra_cv_skills = sorted(cv_set - market_set)

    total_market = len(market_set)
    matched_count = len(matched_skills)
    missing_count = len(missing_skills)

    match_score = round((matched_count / total_market) * 100, 2) if total_market else 0.0

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_cv_skills": extra_cv_skills,
        "match_score": match_score,
        "total_cv_skills": len(cv_set),
        "total_market_skills": total_market,
        "matched_count": matched_count,
        "missing_count": missing_count,
    }


def classify_match_level(score: float) -> str:
    """Classify match score into a simple interpretation bucket."""
    if score >= 75:
        return "Strong Match"
    if score >= 55:
        return "Good Match"
    if score >= 35:
        return "Moderate Match"
    return "Low Match"


def build_skill_gap_dataframe(
    matched_skills: list[str],
    missing_skills: list[str],
    extra_cv_skills: list[str],
    category_lookup: dict | None = None,
) -> pd.DataFrame:
    """Build a clean skill status table for rendering and export."""
    records: list[dict] = []
    category_lookup = category_lookup or {}

    for skill in normalize_skill_list(matched_skills):
        category = (
            categorize_skill(skill, category_lookup)
            if category_lookup
            else "uncategorized"
        )
        records.append({"skill": skill, "status": "Matched", "category": category})

    for skill in normalize_skill_list(missing_skills):
        category = (
            categorize_skill(skill, category_lookup)
            if category_lookup
            else "uncategorized"
        )
        records.append({"skill": skill, "status": "Missing", "category": category})

    for skill in normalize_skill_list(extra_cv_skills):
        category = (
            categorize_skill(skill, category_lookup)
            if category_lookup
            else "uncategorized"
        )
        records.append({"skill": skill, "status": "Extra in CV", "category": category})

    if not records:
        return pd.DataFrame(columns=["skill", "status", "category"])

    gap_df = pd.DataFrame(records)
    status_order = pd.CategoricalDtype(
        categories=["Matched", "Missing", "Extra in CV"],
        ordered=True,
    )
    gap_df["status"] = gap_df["status"].astype(status_order)
    gap_df = gap_df.sort_values(["status", "skill"]).reset_index(drop=True)
    gap_df["status"] = gap_df["status"].astype(str)
    return gap_df


def _priority_for_skill(skill: str) -> str:
    if skill in HIGH_PRIORITY_SKILLS:
        return "High"
    if skill in MEDIUM_PRIORITY_SKILLS:
        return "Medium"
    return "Low"


def _recommendation_text_for_priority(priority: str, skill: str) -> str:
    if priority == "High":
        return f"Prioritize learning '{skill}' first and show at least one portfolio project using it."
    if priority == "Medium":
        return f"Add '{skill}' to strengthen production readiness and end-to-end workflow credibility."
    return f"Learn '{skill}' gradually and connect it to your target role through a focused mini-project."


def recommend_learning_path(
    missing_skills: list[str],
) -> list[dict]:
    """Build prioritized learning and project recommendations for missing skills."""
    normalized_missing = normalize_skill_list(missing_skills)
    if not normalized_missing:
        return []

    engine_recommendations = recommend_projects_for_missing_skills(normalized_missing)
    by_skill = {
        str(item.get("skill", "")).strip().lower(): item
        for item in engine_recommendations
        if isinstance(item, dict) and str(item.get("skill", "")).strip()
    }

    output: list[dict] = []
    for skill in normalized_missing:
        priority = _priority_for_skill(skill)
        engine_item = by_skill.get(skill, {})
        project_idea = str(engine_item.get("project_idea", "")).strip()
        difficulty = str(engine_item.get("difficulty", "")).strip() or "Intermediate"

        if not project_idea:
            project_idea = (
                f"Build a practical portfolio mini-project that clearly demonstrates '{skill}' in an end-to-end workflow."
            )

        output.append(
            {
                "skill": skill,
                "priority": priority,
                "recommendation": _recommendation_text_for_priority(priority, skill),
                "project_idea": project_idea,
                "difficulty": difficulty,
            }
        )

    priority_rank = {"High": 0, "Medium": 1, "Low": 2}
    output = sorted(output, key=lambda row: (priority_rank.get(row["priority"], 99), row["skill"]))
    return output


def generate_cv_gap_insights(
    gap_result: dict,
    target_role: str,
) -> list[str]:
    """Generate simple, rule-based insights for CV gap analysis."""
    if not gap_result:
        return ["No gap result is available yet. Paste CV text and run the analysis."]

    score = float(gap_result.get("match_score", 0.0))
    matched = normalize_skill_list(gap_result.get("matched_skills", []))
    missing = normalize_skill_list(gap_result.get("missing_skills", []))
    total_market = int(gap_result.get("total_market_skills", len(missing) + len(matched)))

    insights: list[str] = []
    insights.append(
        f"Your CV matches {score:.1f}% of the top skills for {target_role} roles."
    )

    if matched:
        strengths = ", ".join(skill.title() for skill in matched[:3])
        insights.append(f"You already show strength in {strengths}.")

    if missing:
        top_gaps = ", ".join(skill.title() for skill in missing[:3])
        insights.append(f"Your biggest gaps are {top_gaps}.")

    if total_market > 0:
        improvement_window = min(5, max(3, len(missing))) if missing else 0
        if improvement_window:
            insights.append(
                f"Adding {improvement_window} missing skills to your portfolio could significantly improve your role alignment."
            )

    if score < 35:
        insights.append("Focus on high-priority foundational skills first, then iterate with role-specific projects.")
    elif score < 75:
        insights.append("You are on a promising track—target medium-priority production skills to become interview-ready.")
    else:
        insights.append("Your profile is strongly aligned; focus on depth, measurable outcomes, and portfolio storytelling.")

    return insights


def create_cv_gap_report_text(
    target_role: str,
    cv_skills: list[str],
    market_skills: list[str],
    gap_result: dict,
    recommendations: list[dict],
) -> str:
    """Create a downloadable plain-text CV skill-gap report."""
    score = float(gap_result.get("match_score", 0.0)) if gap_result else 0.0
    match_level = classify_match_level(score)

    normalized_cv = normalize_skill_list(cv_skills)
    normalized_market = normalize_skill_list(market_skills)
    matched = normalize_skill_list(gap_result.get("matched_skills", []) if gap_result else [])
    missing = normalize_skill_list(gap_result.get("missing_skills", []) if gap_result else [])
    extra = normalize_skill_list(gap_result.get("extra_cv_skills", []) if gap_result else [])

    lines: list[str] = []
    lines.append("CV Skill Gap Report")
    lines.append("=" * 80)
    lines.append(f"Target Role: {target_role}")
    lines.append(f"Match Score: {score:.2f}%")
    lines.append(f"Match Level: {match_level}")
    lines.append("")

    lines.append(f"CV Skills Detected ({len(normalized_cv)}):")
    lines.append(", ".join(normalized_cv) if normalized_cv else "None detected")
    lines.append("")

    lines.append(f"Market Skills Compared ({len(normalized_market)}):")
    lines.append(", ".join(normalized_market) if normalized_market else "No market skills available")
    lines.append("")

    lines.append(f"Matched Skills ({len(matched)}):")
    lines.append(", ".join(matched) if matched else "None")
    lines.append("")

    lines.append(f"Missing Skills ({len(missing)}):")
    lines.append(", ".join(missing) if missing else "None")
    lines.append("")

    lines.append(f"Extra CV Skills ({len(extra)}):")
    lines.append(", ".join(extra) if extra else "None")
    lines.append("")

    lines.append("Recommended Learning & Projects:")
    if recommendations:
        for idx, rec in enumerate(recommendations, start=1):
            skill = rec.get("skill", "unknown")
            priority = rec.get("priority", "Low")
            difficulty = rec.get("difficulty", "Intermediate")
            recommendation = rec.get("recommendation", "")
            project_idea = rec.get("project_idea", "")
            lines.append(f"{idx}. {skill} [{priority} | {difficulty}]")
            lines.append(f"   - Recommendation: {recommendation}")
            lines.append(f"   - Project Idea: {project_idea}")
    else:
        lines.append("No missing skills identified for recommendation.")

    lines.append("")
    lines.append("Disclaimer: This is a rule-based portfolio analysis, not a hiring decision.")

    return "\n".join(lines)
