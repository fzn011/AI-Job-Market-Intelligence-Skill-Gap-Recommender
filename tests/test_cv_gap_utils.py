"""Unit tests for CV gap utility helpers."""

import pandas as pd

from src.cv_gap_utils import (
    build_skill_gap_dataframe,
    classify_match_level,
    compute_cv_market_gap,
    create_cv_gap_report_text,
    extract_cv_skills,
    generate_cv_gap_insights,
    get_market_skills_by_target_role,
    get_market_skills_from_jobs,
    normalize_skill_list,
    recommend_learning_path,
)


def sample_jobs_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "job_id": [1, 2, 3, 4],
            "job_title": [
                "data scientist",
                "machine learning engineer",
                "bi analyst",
                "product data analyst",
            ],
            "job_type": ["full-time", "full-time", "full-time", "contract"],
            "extracted_skills": [
                "['python', 'sql', 'pandas', 'scikit-learn']",
                "['python', 'docker', 'fastapi', 'mlflow']",
                "['sql', 'power bi', 'excel']",
                "['python', 'sql', 'a/b testing', 'tableau']",
            ],
        }
    )


def sample_skill_dictionary() -> dict:
    return {
        "programming_languages": ["python", "sql"],
        "machine_learning": ["machine learning", "scikit-learn"],
        "mlops_deployment": ["docker", "fastapi", "mlflow"],
        "data_analysis": ["power bi", "tableau", "excel"],
        "soft_skills": ["communication"],
    }


def test_normalize_skill_list_deduplicates_cleans_and_sorts():
    skills = ["Python", " python ", "SQL", "", None]
    assert normalize_skill_list(skills) == ["python", "sql"]


def test_get_market_skills_from_jobs_extracts_and_respects_top_n():
    skills_top_2 = get_market_skills_from_jobs(sample_jobs_df(), top_n=2)
    assert len(skills_top_2) == 2
    assert skills_top_2[0] in {"python", "sql"}


def test_get_market_skills_from_jobs_handles_empty_and_missing_column():
    assert get_market_skills_from_jobs(pd.DataFrame(), top_n=5) == []
    assert get_market_skills_from_jobs(pd.DataFrame({"job_title": ["x"]}), top_n=5) == []


def test_get_market_skills_by_target_role_filters_by_role_and_falls_back():
    jobs = sample_jobs_df()

    ds_skills = get_market_skills_by_target_role(jobs, target_role="Data Scientist", top_n=10)
    assert "scikit-learn" in ds_skills

    fallback_skills = get_market_skills_by_target_role(jobs, target_role="AI Engineer", top_n=10)
    overall_skills = get_market_skills_from_jobs(jobs, top_n=10)
    assert fallback_skills == overall_skills

    overall_market_skills = get_market_skills_by_target_role(jobs, target_role="Overall Market", top_n=10)
    assert overall_market_skills == overall_skills


def test_extract_cv_skills_extracts_and_handles_empty_inputs():
    text = "Experienced in Python, SQL, pandas, and Docker deployments."
    skill_dict = sample_skill_dictionary()

    extracted = extract_cv_skills(text, skill_dict)
    assert "python" in extracted
    assert "sql" in extracted

    assert extract_cv_skills("", skill_dict) == []
    assert extract_cv_skills(text, {}) == []


def test_compute_cv_market_gap_returns_counts_and_score():
    cv_skills = ["python", "sql", "docker"]
    market_skills = ["python", "sql", "pandas", "scikit-learn"]

    result = compute_cv_market_gap(cv_skills, market_skills)

    assert result["matched_skills"] == ["python", "sql"]
    assert result["missing_skills"] == ["pandas", "scikit-learn"]
    assert result["extra_cv_skills"] == ["docker"]
    assert result["match_score"] == 50.0


def test_classify_match_level_all_buckets():
    assert classify_match_level(80) == "Strong Match"
    assert classify_match_level(60) == "Good Match"
    assert classify_match_level(40) == "Moderate Match"
    assert classify_match_level(20) == "Low Match"


def test_build_skill_gap_dataframe_status_and_category_and_empty():
    category_lookup = {"python": "programming_languages", "sql": "programming_languages"}
    gap_df = build_skill_gap_dataframe(
        matched_skills=["python"],
        missing_skills=["sql"],
        extra_cv_skills=["docker"],
        category_lookup=category_lookup,
    )

    assert set(gap_df["status"].tolist()) == {"Matched", "Missing", "Extra in CV"}
    assert "category" in gap_df.columns

    empty_df = build_skill_gap_dataframe([], [], [], category_lookup={})
    assert empty_df.empty


def test_recommend_learning_path_priorities_and_generic_fallback():
    recommendations = recommend_learning_path(["python", "sql", "unknownskill"])
    assert recommendations

    by_skill = {row["skill"]: row for row in recommendations}
    assert by_skill["python"]["priority"] == "High"
    assert by_skill["sql"]["priority"] == "High"
    assert by_skill["unknownskill"]["project_idea"]


def test_generate_cv_gap_insights_returns_list_and_handles_empty():
    result = {
        "matched_skills": ["python", "sql"],
        "missing_skills": ["docker", "mlflow"],
        "match_score": 50.0,
        "total_market_skills": 4,
    }
    insights = generate_cv_gap_insights(result, "Data Scientist")
    assert isinstance(insights, list)
    assert len(insights) > 0

    empty_insights = generate_cv_gap_insights({}, "Data Scientist")
    assert isinstance(empty_insights, list)
    assert len(empty_insights) > 0


def test_create_cv_gap_report_text_contains_required_fields():
    gap_result = {
        "matched_skills": ["python", "sql"],
        "missing_skills": ["docker"],
        "extra_cv_skills": ["excel"],
        "match_score": 66.67,
    }
    recommendations = [
        {
            "skill": "docker",
            "priority": "Medium",
            "difficulty": "Intermediate",
            "recommendation": "Build deployment workflows.",
            "project_idea": "Containerize a FastAPI inference service.",
        }
    ]

    report = create_cv_gap_report_text(
        target_role="Data Scientist",
        cv_skills=["python", "sql", "excel"],
        market_skills=["python", "sql", "docker"],
        gap_result=gap_result,
        recommendations=recommendations,
    )

    assert isinstance(report, str)
    assert "Target Role: Data Scientist" in report
    assert "Match Score:" in report
    assert "Disclaimer: This is a rule-based portfolio analysis, not a hiring decision." in report
