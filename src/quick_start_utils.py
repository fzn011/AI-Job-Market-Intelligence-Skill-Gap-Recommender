"""Quick Start wizard helpers — fast 3-click career insights on the landing page."""

from __future__ import annotations

from src.career_taxonomy_utils import (
    compute_role_skill_gap,
    extract_skills_from_text,
    get_roles_for_category,
    list_career_categories,
    recommend_career_actions,
)
from src.cv_gap_utils import classify_match_level, compute_cv_market_gap, extract_cv_skills
from src.job_match_utils import classify_job_match_level, compute_job_match
from src.regional_profiles_utils import get_regional_role_profile, list_regions
from src.skill_analysis_utils import load_skill_dictionary_for_analysis


QUICK_START_GOALS = [
    "Check my skill gap for a role",
    "Match my CV to a job description",
    "Explore a career path",
]

SAMPLE_CV = """Data Analyst with experience in Python, SQL, Excel, and Power BI.
Built dashboards and reports for business stakeholders. Comfortable with pandas
and data visualization. Strong communication and problem solving skills."""

SAMPLE_JOB = """We are hiring a Data Analyst with Python, SQL, Power BI, machine learning,
and Docker experience. You will build dashboards, run SQL analyses, and present insights."""


def get_default_category() -> str:
    categories = list_career_categories()
    if not categories:
        return "Data & AI"
    if "Data & AI" in categories:
        return "Data & AI"
    return categories[0]


def get_default_role(category: str) -> str:
    roles = get_roles_for_category(category)
    if "Data Analyst" in roles:
        return "Data Analyst"
    return roles[0] if roles else "General"


def run_skill_gap_quick_start(
    category: str,
    role: str,
    cv_text: str,
    region: str = "Global",
) -> dict:
    """Run career-category skill gap analysis for the wizard."""
    cv_skills = extract_skills_from_text(cv_text, category)
    if not cv_skills:
        return {
            "success": False,
            "message": "No skills detected. Try the sample CV or add tools like Python, SQL, Excel.",
        }

    gap = compute_role_skill_gap(cv_skills, category, role, region=region)
    actions_df = recommend_career_actions(gap.get("missing_skills", []), category, max_actions=3)
    top_action = actions_df.iloc[0].to_dict() if not actions_df.empty else None

    return {
        "success": True,
        "goal": "skill_gap",
        "category": category,
        "role": role,
        "region": region,
        "match_score": gap.get("match_score", 0.0),
        "match_level": classify_match_level(float(gap.get("match_score", 0.0))),
        "cv_skills": cv_skills,
        "matched_skills": gap.get("matched_skills", []),
        "missing_skills": gap.get("missing_skills", [])[:8],
        "top_action": top_action,
        "next_page": "3_CV_Skill_Gap",
    }


def run_job_match_quick_start(job_text: str, cv_text: str) -> dict:
    """Run job description vs CV match for the wizard."""
    if not job_text.strip() or not cv_text.strip():
        return {"success": False, "message": "Please provide both a job description and CV text."}

    result = compute_job_match(job_text, cv_text)
    if result.get("message") and result.get("job_skill_count", 0) == 0:
        return {"success": False, "message": result["message"]}

    return {
        "success": True,
        "goal": "job_match",
        "match_score": result.get("match_score", 0.0),
        "match_level": classify_job_match_level(float(result.get("match_score", 0.0))),
        "matched_skills": result.get("matched_skills", [])[:8],
        "missing_skills": result.get("missing_skills", [])[:8],
        "cv_skill_count": result.get("cv_skill_count", 0),
        "job_skill_count": result.get("job_skill_count", 0),
        "next_page": "8_Job_Match_Dashboard",
    }


def run_explore_quick_start(category: str, role: str, region: str = "Global") -> dict:
    """Return curated role snapshot for the wizard."""
    from src.regional_profiles_utils import get_regional_target_skills

    profile = get_regional_role_profile(category, role, region)
    target_skills = get_regional_target_skills(category, role, region)

    actions_df = recommend_career_actions(target_skills[:6], category, max_actions=3)
    top_action = actions_df.iloc[0].to_dict() if not actions_df.empty else None

    return {
        "success": True,
        "goal": "explore",
        "category": category,
        "role": role,
        "region": region,
        "level": profile.get("level", "N/A"),
        "core_skills": profile.get("core_skills", [])[:8],
        "helpful_skills": profile.get("helpful_skills", [])[:6],
        "regional_notes": profile.get("regional_notes", ""),
        "top_action": top_action,
        "next_page": "7_Career_Explorer",
    }


def run_market_gap_quick_start(cv_text: str, target_role: str = "Data Analyst") -> dict:
    """Optional market-data gap using processed jobs when available."""
    from src.dashboard_utils import load_active_jobs_dataset
    from src.cv_gap_utils import get_market_skills_by_target_role

    skill_dict = load_skill_dictionary_for_analysis()
    jobs_df = load_active_jobs_dataset()
    if jobs_df.empty or not skill_dict:
        return run_skill_gap_quick_start(get_default_category(), target_role, cv_text)

    cv_skills = extract_cv_skills(cv_text=cv_text, skill_dictionary=skill_dict)
    if not cv_skills:
        return {"success": False, "message": "No skills detected in your CV text."}

    market_skills = get_market_skills_by_target_role(jobs_df, target_role, top_n=20)
    gap = compute_cv_market_gap(cv_skills=cv_skills, market_skills=market_skills)

    return {
        "success": True,
        "goal": "market_gap",
        "role": target_role,
        "match_score": gap.get("match_score", 0.0),
        "match_level": classify_match_level(float(gap.get("match_score", 0.0))),
        "matched_skills": gap.get("matched_skills", [])[:8],
        "missing_skills": gap.get("missing_skills", [])[:8],
        "next_page": "3_CV_Skill_Gap",
    }
