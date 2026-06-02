"""Unit tests for project recommendation utility helpers."""

import pandas as pd

from src.project_recommendation_utils import (
    build_project_skill_matrix,
    create_project_roadmap_text,
    generate_project_recommendation_insights,
    get_available_skills_from_market,
    get_difficulty_distribution,
    get_difficulty_order,
    get_project_template_catalog,
    get_project_type_distribution,
    get_role_based_skill_options,
    normalize_selected_skills,
    recommend_projects,
    score_project_against_skills,
    summarize_project_coverage,
)


def sample_jobs_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "job_id": [1, 2, 3],
            "job_title": ["data scientist", "ml engineer", "bi analyst"],
            "job_type": ["full-time", "full-time", "contract"],
            "extracted_skills": [
                "['python', 'sql', 'pandas', 'scikit-learn']",
                "['python', 'docker', 'fastapi', 'mlflow']",
                "['sql', 'power bi', 'excel']",
            ],
        }
    )


def test_normalize_selected_skills_cleans_and_deduplicates():
    skills = [" Python ", "sql", "SQL", "", None]
    assert normalize_selected_skills(skills) == ["python", "sql"]


def test_get_available_skills_from_market_extracts_and_respects_top_n():
    jobs = sample_jobs_df()

    all_skills = get_available_skills_from_market(jobs, top_n=None)
    assert "python" in all_skills
    assert "sql" in all_skills

    top_2 = get_available_skills_from_market(jobs, top_n=2)
    assert len(top_2) == 2


def test_get_available_skills_from_market_handles_empty_or_missing_column():
    assert get_available_skills_from_market(pd.DataFrame(), top_n=None) == []
    assert get_available_skills_from_market(pd.DataFrame({"job_title": ["x"]}), top_n=None) == []


def test_get_role_based_skill_options_returns_role_based_or_fallback():
    jobs = sample_jobs_df()

    ds_skills = get_role_based_skill_options(jobs, "Data Scientist", top_n=10)
    assert isinstance(ds_skills, list)
    assert len(ds_skills) > 0

    fallback_skills = get_role_based_skill_options(jobs, "AI Engineer", top_n=10)
    assert isinstance(fallback_skills, list)
    assert len(fallback_skills) > 0


def test_get_project_template_catalog_structure_and_minimum_size():
    catalog = get_project_template_catalog()
    assert isinstance(catalog, list)
    assert len(catalog) >= 12

    required_keys = {
        "project_id",
        "title",
        "description",
        "project_type",
        "difficulty",
        "estimated_timeline",
        "core_skills",
        "tech_stack",
        "deliverables",
        "portfolio_value",
        "business_context",
        "github_readme_sections",
    }

    for project in catalog:
        assert required_keys.issubset(project.keys())
        assert isinstance(project["core_skills"], list)
        assert isinstance(project["tech_stack"], list)


def test_score_project_against_skills_computes_expected_fields():
    project = get_project_template_catalog()[0]
    selected = ["python", "sql", "docker"]

    scored = score_project_against_skills(project, selected)

    assert "matched_skills" in scored
    assert "missing_selected_skills" in scored
    assert "coverage_score" in scored
    assert "matched_skill_count" in scored
    assert "selected_skill_count" in scored

    assert scored["selected_skill_count"] == 3
    assert scored["matched_skill_count"] >= 1
    assert scored["coverage_score"] >= 0


def test_score_project_against_skills_handles_empty_selected_skills():
    project = get_project_template_catalog()[0]
    scored = score_project_against_skills(project, [])
    assert scored["coverage_score"] == 0.0
    assert scored["selected_skill_count"] == 0


def test_recommend_projects_returns_dataframe_and_respects_constraints():
    selected = ["python", "sql", "streamlit", "docker"]

    df = recommend_projects(selected_skills=selected, max_projects=5)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) <= 5

    coverage_values = df["coverage_score"].tolist()
    assert coverage_values == sorted(coverage_values, reverse=True)

    beginner_df = recommend_projects(
        selected_skills=selected,
        max_projects=10,
        difficulty_filter=["Beginner"],
    )
    if not beginner_df.empty:
        assert beginner_df["difficulty"].str.lower().eq("beginner").all()

    mlops_df = recommend_projects(
        selected_skills=selected,
        max_projects=10,
        project_type_filter=["MLOps / Deployment"],
    )
    if not mlops_df.empty:
        assert mlops_df["project_type"].eq("MLOps / Deployment").all()


def test_get_difficulty_order_returns_expected_rank():
    assert get_difficulty_order("Beginner") == 1
    assert get_difficulty_order("Intermediate") == 2
    assert get_difficulty_order("Advanced") == 3
    assert get_difficulty_order("Unknown") == 99


def test_build_project_skill_matrix_creates_expected_shape_and_handles_empty():
    selected = ["python", "sql", "docker"]
    rec_df = recommend_projects(selected_skills=selected, max_projects=4)

    matrix = build_project_skill_matrix(rec_df, selected)
    assert isinstance(matrix, pd.DataFrame)
    assert not matrix.empty
    assert set(normalize_selected_skills(selected)).issubset(set(matrix.columns))

    empty_matrix = build_project_skill_matrix(pd.DataFrame(), selected)
    assert empty_matrix.empty


def test_summarize_project_coverage_returns_keys_and_handles_empty():
    selected = ["python", "sql", "docker"]
    rec_df = recommend_projects(selected_skills=selected, max_projects=5)

    summary = summarize_project_coverage(rec_df, selected)
    expected_keys = {
        "recommended_projects",
        "selected_skills",
        "best_project",
        "best_coverage_score",
        "skills_covered_by_any_project",
        "skills_not_covered_by_any_project",
    }
    assert expected_keys.issubset(summary.keys())
    assert summary["recommended_projects"] == len(rec_df)

    empty_summary = summarize_project_coverage(pd.DataFrame(), selected)
    assert empty_summary["recommended_projects"] == 0


def test_generate_project_recommendation_insights_returns_list_and_handles_empty():
    selected = ["python", "sql", "docker"]
    rec_df = recommend_projects(selected_skills=selected, max_projects=5)

    insights = generate_project_recommendation_insights(rec_df, selected)
    assert isinstance(insights, list)
    assert len(insights) > 0

    empty_insights = generate_project_recommendation_insights(pd.DataFrame(), selected)
    assert isinstance(empty_insights, list)
    assert len(empty_insights) > 0


def test_create_project_roadmap_text_contains_required_content():
    selected = ["python", "sql", "docker"]
    rec_df = recommend_projects(selected_skills=selected, max_projects=5)

    report = create_project_roadmap_text(
        target_role="Data Scientist",
        selected_skills=selected,
        recommendations_df=rec_df,
    )

    assert isinstance(report, str)
    assert "Target Role: Data Scientist" in report
    assert "Selected Skills" in report
    assert "This roadmap is generated using a local rule-based recommendation system and does not use paid AI APIs." in report


def test_get_project_type_distribution_counts_project_types():
    rec_df = recommend_projects(selected_skills=["python", "sql"], max_projects=6)
    dist = get_project_type_distribution(rec_df)
    assert set(dist.columns) == {"project_type", "count"}


def test_get_difficulty_distribution_counts_difficulty_levels():
    rec_df = recommend_projects(selected_skills=["python", "sql"], max_projects=6)
    dist = get_difficulty_distribution(rec_df)
    assert set(dist.columns) == {"difficulty", "count"}
