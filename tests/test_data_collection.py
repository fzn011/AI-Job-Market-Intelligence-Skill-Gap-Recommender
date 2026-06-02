"""Unit tests for data collection and import utilities."""

from pathlib import Path

import pandas as pd
import pytest

from src.data_collection import (
    OPTIONAL_JOB_COLUMNS,
    REQUIRED_JOB_COLUMNS,
    create_job_template_csv,
    deduplicate_jobs,
    export_import_summary,
    get_standard_job_columns,
    load_demo_dataset,
    load_job_csv,
    merge_job_sources,
    process_imported_jobs,
    standardize_job_dataframe,
    validate_job_schema,
)


def _valid_jobs_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "job_id": ["1", "2", "3"],
            "job_title": ["Data Analyst", "Data Scientist", "ML Engineer"],
            "company": ["A", "B", "C"],
            "location": ["Dhaka", "Remote", "London"],
            "job_type": ["Full-time", "Full-time", "Contract"],
            "description": [
                "Python SQL Pandas dashboard communication",
                "Python scikit-learn classification regression",
                "Docker FastAPI MLflow model deployment",
            ],
            "date_posted": ["2026-05-01", "2026-05-02", "2026-05-03"],
            "source": ["manual_csv", "manual_csv", "manual_csv"],
        }
    )


def test_get_standard_job_columns_contains_required_and_optional():
    cols = get_standard_job_columns()
    for col in REQUIRED_JOB_COLUMNS:
        assert col in cols
    for col in OPTIONAL_JOB_COLUMNS:
        assert col in cols


def test_create_job_template_csv_creates_file_with_header(tmp_path: Path):
    path = tmp_path / "template.csv"
    out = create_job_template_csv(path)

    assert out.exists()
    loaded = pd.read_csv(out)
    assert list(loaded.columns) == get_standard_job_columns()
    assert loaded.empty


def test_load_job_csv_loads_and_standardizes_columns(tmp_path: Path):
    input_path = tmp_path / "jobs.csv"
    pd.DataFrame(
        {
            "Job ID": [1],
            "Job Title": ["Data Analyst"],
            "Company": ["X"],
            "Location": ["Dhaka"],
            "Job Type": ["Full-time"],
            "Description": ["Python SQL"],
            "Date Posted": ["2026-05-01"],
            "Source": ["manual_csv"],
        }
    ).to_csv(input_path, index=False)

    df = load_job_csv(input_path)
    assert "job_id" in df.columns
    assert "job_title" in df.columns
    assert "date_posted" in df.columns


def test_validate_job_schema_valid_df_returns_true():
    report = validate_job_schema(_valid_jobs_df())
    assert report["is_valid"] is True
    assert report["missing_required_columns"] == []


def test_validate_job_schema_missing_required_returns_false():
    broken = _valid_jobs_df().drop(columns=["description", "source"])
    report = validate_job_schema(broken)
    assert report["is_valid"] is False
    assert "description" in report["missing_required_columns"]
    assert "source" in report["missing_required_columns"]


def test_validate_job_schema_counts_duplicates_and_missing_descriptions():
    df = _valid_jobs_df().copy()
    df.loc[2, "job_id"] = "2"
    df.loc[1, "description"] = ""

    report = validate_job_schema(df)
    assert report["duplicate_job_ids"] >= 1
    assert report["missing_descriptions"] >= 1


def test_standardize_job_dataframe_adds_optional_and_fills_source():
    df = _valid_jobs_df().drop(columns=["source"]).copy()
    standardized = standardize_job_dataframe(df)

    for col in OPTIONAL_JOB_COLUMNS:
        assert col in standardized.columns
    for col in REQUIRED_JOB_COLUMNS:
        assert col in standardized.columns
    assert standardized["source"].eq("manual_csv").all()


def test_deduplicate_jobs_removes_duplicate_job_id_and_exact_duplicates():
    df = pd.concat([_valid_jobs_df(), _valid_jobs_df().iloc[[0]]], ignore_index=True)
    df.loc[3, "job_id"] = "1"

    deduped = deduplicate_jobs(df)
    assert deduped["job_id"].nunique() == len(deduped)


def test_merge_job_sources_merges_and_deduplicates():
    df1 = _valid_jobs_df().iloc[:2].copy()
    df2 = _valid_jobs_df().iloc[1:].copy()
    merged = merge_job_sources([df1, pd.DataFrame(), df2])

    assert not merged.empty
    assert merged["job_id"].nunique() == len(merged)


def test_process_imported_jobs_creates_outputs_and_returns_summary(tmp_path: Path):
    input_csv = tmp_path / "input_jobs.csv"
    output_jobs = tmp_path / "processed_jobs.csv"
    output_freq = tmp_path / "skill_freq.csv"

    _valid_jobs_df().to_csv(input_csv, index=False)

    project_root = Path(__file__).resolve().parents[1]
    skill_dict = project_root / "data" / "sample" / "skills_dictionary.json"

    summary = process_imported_jobs(
        input_csv_path=input_csv,
        skill_dictionary_path=skill_dict,
        output_jobs_path=output_jobs,
        output_skill_frequency_path=output_freq,
    )

    assert output_jobs.exists()
    assert output_freq.exists()
    assert summary["raw_rows"] == 3
    assert summary["processed_rows"] >= 1
    assert "validation" in summary


def test_load_demo_dataset_small_and_expanded():
    small_df = load_demo_dataset(expanded=False)
    expanded_df = load_demo_dataset(expanded=True)

    assert not small_df.empty
    assert not expanded_df.empty
    assert len(expanded_df) >= len(small_df)


def test_export_import_summary_writes_json(tmp_path: Path):
    summary = {"raw_rows": 5, "processed_rows": 4}
    output = tmp_path / "summary.json"

    out_path = export_import_summary(summary, output)
    assert out_path.exists()
    assert "raw_rows" in out_path.read_text(encoding="utf-8")


def test_load_job_csv_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_job_csv("definitely_missing_jobs.csv")
