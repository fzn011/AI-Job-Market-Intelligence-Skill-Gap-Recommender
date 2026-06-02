"""Unit tests for skill analysis utility helpers."""

import pandas as pd

from src.skill_analysis_utils import (
    build_skill_category_lookup,
    categorize_skill,
    explode_skills_dataframe,
    generate_skill_insights,
    get_skill_analysis_metrics,
    get_skill_category_distribution,
    get_skill_cooccurrence,
    get_skills_by_group,
    get_technical_vs_soft_split,
    get_top_skill_combinations,
    get_top_skills,
)


def sample_skill_dict() -> dict:
    return {
        "programming_languages": ["Python", "SQL"],
        "soft_skills": ["Communication"],
    }


def sample_jobs_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "job_id": [1, 2, 3],
            "job_title": ["data analyst", "data scientist", "ml engineer"],
            "company": ["a", "b", "c"],
            "location": ["london", "remote", "london"],
            "job_type": ["full-time", "contract", "full-time"],
            "date_posted": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "extracted_skills": [
                "['python', 'sql', 'communication']",
                "['python', 'docker']",
                "['sql', 'docker']",
            ],
            "skill_count": [3, 2, 2],
        }
    )


def test_build_skill_category_lookup_creates_lookup_and_lowercases():
    lookup = build_skill_category_lookup(sample_skill_dict())
    assert lookup["python"] == "programming_languages"
    assert lookup["sql"] == "programming_languages"
    assert lookup["communication"] == "soft_skills"


def test_build_skill_category_lookup_handles_empty_dict():
    assert build_skill_category_lookup({}) == {}


def test_categorize_skill_known_and_unknown_and_none():
    lookup = {"python": "programming_languages"}
    assert categorize_skill("python", lookup) == "programming_languages"
    assert categorize_skill("unknown", lookup) == "uncategorized"
    assert categorize_skill(None, lookup) == "uncategorized"


def test_explode_skills_dataframe_converts_rows_and_adds_category():
    lookup = build_skill_category_lookup(sample_skill_dict())
    exploded = explode_skills_dataframe(sample_jobs_df(), category_lookup=lookup)

    assert not exploded.empty
    expected_cols = {
        "job_id",
        "job_title",
        "company",
        "location",
        "job_type",
        "date_posted",
        "skill",
        "skill_category",
    }
    assert expected_cols.issubset(exploded.columns)
    assert "programming_languages" in exploded["skill_category"].values


def test_explode_skills_dataframe_handles_missing_extracted_column():
    df = sample_jobs_df().drop(columns=["extracted_skills"])
    exploded = explode_skills_dataframe(df, category_lookup={})
    assert exploded.empty


def test_get_top_skills_counts_and_respects_top_n():
    exploded = explode_skills_dataframe(sample_jobs_df(), category_lookup={})
    top = get_top_skills(exploded, top_n=2)
    assert len(top) == 2
    assert top.iloc[0]["frequency"] >= top.iloc[1]["frequency"]


def test_get_top_skills_handles_empty():
    top = get_top_skills(pd.DataFrame(), top_n=5)
    assert top.empty


def test_get_skill_category_distribution_counts_categories():
    exploded = explode_skills_dataframe(
        sample_jobs_df(), category_lookup=build_skill_category_lookup(sample_skill_dict())
    )
    category_df = get_skill_category_distribution(exploded)
    assert not category_df.empty
    assert "skill_category" in category_df.columns


def test_get_skills_by_group_creates_pivot_matrix():
    exploded = explode_skills_dataframe(sample_jobs_df(), category_lookup={})
    matrix = get_skills_by_group(exploded, "job_type", top_n_skills=5)
    assert not matrix.empty
    assert "full-time" in matrix.index


def test_get_skills_by_group_handles_missing_group_column():
    exploded = explode_skills_dataframe(sample_jobs_df(), category_lookup={})
    matrix = get_skills_by_group(exploded, "missing_col", top_n_skills=5)
    assert matrix.empty


def test_get_skills_by_group_handles_empty_dataframe():
    matrix = get_skills_by_group(pd.DataFrame(), "job_type", top_n_skills=5)
    assert matrix.empty


def test_get_skill_cooccurrence_creates_square_matrix_and_counts_pairs():
    matrix = get_skill_cooccurrence(sample_jobs_df(), top_n_skills=5)
    assert not matrix.empty
    assert matrix.shape[0] == matrix.shape[1]
    if "python" in matrix.index and "sql" in matrix.columns:
        assert matrix.loc["python", "sql"] >= 1


def test_get_skill_cooccurrence_handles_missing_extracted_skills():
    df = sample_jobs_df().drop(columns=["extracted_skills"])
    matrix = get_skill_cooccurrence(df)
    assert matrix.empty


def test_get_top_skill_combinations_finds_pairs():
    combos = get_top_skill_combinations(sample_jobs_df(), combination_size=2, top_n=5)
    assert not combos.empty
    assert "skill_combination" in combos.columns
    assert "frequency" in combos.columns


def test_get_top_skill_combinations_handles_empty_input():
    combos = get_top_skill_combinations(pd.DataFrame(), combination_size=2, top_n=5)
    assert combos.empty


def test_get_technical_vs_soft_split_separates_types():
    exploded = explode_skills_dataframe(
        sample_jobs_df(), category_lookup=build_skill_category_lookup(sample_skill_dict())
    )
    split = get_technical_vs_soft_split(exploded)
    assert not split.empty
    assert "skill_type" in split.columns


def test_get_skill_analysis_metrics_returns_expected_fields():
    jobs = sample_jobs_df()
    exploded = explode_skills_dataframe(jobs, category_lookup={})
    metrics = get_skill_analysis_metrics(exploded, jobs)

    expected_keys = {
        "total_skill_mentions",
        "unique_skills",
        "avg_skills_per_job",
        "top_skill",
        "top_skill_frequency",
        "top_category",
        "top_category_frequency",
    }
    assert expected_keys.issubset(metrics.keys())


def test_get_skill_analysis_metrics_handles_empty_data():
    metrics = get_skill_analysis_metrics(pd.DataFrame(), pd.DataFrame())
    assert metrics["total_skill_mentions"] == 0
    assert metrics["unique_skills"] == 0


def test_generate_skill_insights_returns_list():
    jobs = sample_jobs_df()
    exploded = explode_skills_dataframe(
        jobs, category_lookup=build_skill_category_lookup(sample_skill_dict())
    )
    category_df = get_skill_category_distribution(exploded)
    insights = generate_skill_insights(exploded, jobs, category_df)
    assert isinstance(insights, list)
    assert len(insights) > 0


def test_generate_skill_insights_handles_empty_data():
    insights = generate_skill_insights(pd.DataFrame(), pd.DataFrame())
    assert isinstance(insights, list)
    assert len(insights) > 0
