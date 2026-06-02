"""Unit tests for dashboard utility helpers."""

import pandas as pd

from src.dashboard_utils import (
    add_total_extracted_skills_metric,
    get_basic_job_metrics,
    get_top_values,
    parse_extracted_skills,
    prepare_jobs_preview,
)


def test_parse_extracted_skills_with_list_input():
    value = ["python", "sql"]
    assert parse_extracted_skills(value) == ["python", "sql"]


def test_parse_extracted_skills_with_string_list_input():
    value = "['python', 'sql']"
    assert parse_extracted_skills(value) == ["python", "sql"]


def test_parse_extracted_skills_with_comma_separated_string():
    value = "python, sql, power bi"
    assert parse_extracted_skills(value) == ["python", "sql", "power bi"]


def test_parse_extracted_skills_with_none_input():
    assert parse_extracted_skills(None) == []


def test_get_basic_job_metrics_normal_dataframe():
    df = pd.DataFrame(
        {
            "job_title": ["data analyst", "data scientist"],
            "company": ["a", "b"],
            "location": ["london", "remote"],
            "job_type": ["full-time", "contract"],
            "skill_count": [5, 7],
        }
    )
    metrics = get_basic_job_metrics(df)

    assert metrics["total_jobs"] == 2
    assert metrics["unique_job_titles"] == 2
    assert metrics["unique_companies"] == 2
    assert metrics["unique_locations"] == 2
    assert metrics["unique_job_types"] == 2
    assert metrics["avg_skills_per_job"] == 6.0


def test_get_basic_job_metrics_empty_dataframe():
    metrics = get_basic_job_metrics(pd.DataFrame())
    assert metrics == {
        "total_jobs": 0,
        "unique_job_titles": 0,
        "unique_companies": 0,
        "unique_locations": 0,
        "unique_job_types": 0,
        "avg_skills_per_job": 0,
    }


def test_get_basic_job_metrics_without_skill_count():
    df = pd.DataFrame(
        {
            "job_title": ["data analyst"],
            "company": ["a"],
            "location": ["london"],
            "job_type": ["full-time"],
        }
    )
    metrics = get_basic_job_metrics(df)
    assert metrics["avg_skills_per_job"] == 0


def test_get_top_values_valid_column():
    df = pd.DataFrame({"job_type": ["full-time", "full-time", "contract"]})
    top_df = get_top_values(df, "job_type", top_n=2)

    assert list(top_df.columns) == ["value", "count"]
    assert top_df.iloc[0]["value"] == "full-time"
    assert int(top_df.iloc[0]["count"]) == 2


def test_get_top_values_missing_column():
    df = pd.DataFrame({"a": [1, 2]})
    top_df = get_top_values(df, "job_type")
    assert top_df.empty


def test_get_top_values_empty_dataframe():
    top_df = get_top_values(pd.DataFrame(), "job_type")
    assert top_df.empty


def test_prepare_jobs_preview_available_columns_only_and_row_limit():
    df = pd.DataFrame(
        {
            "job_id": [1, 2, 3],
            "job_title": ["a", "b", "c"],
            "company": ["x", "y", "z"],
            "skill_count": [1, 2, 3],
            "extra": [10, 20, 30],
        }
    )
    preview = prepare_jobs_preview(df, max_rows=2)

    assert len(preview) == 2
    assert "job_id" in preview.columns
    assert "job_title" in preview.columns
    assert "company" in preview.columns
    assert "skill_count" in preview.columns
    assert "extra" not in preview.columns


def test_add_total_extracted_skills_metric_counts_string_lists():
    df = pd.DataFrame(
        {
            "extracted_skills": [
                "['python', 'sql']",
                ["docker"],
                None,
            ]
        }
    )
    assert add_total_extracted_skills_metric(df) == 3


def test_add_total_extracted_skills_metric_handles_missing_column():
    df = pd.DataFrame({"job_title": ["data scientist"]})
    assert add_total_extracted_skills_metric(df) == 0
