"""Tests for utility cleaning and job cleaning pipeline."""

import pandas as pd
import pytest

from src.data_cleaning import clean_jobs
from src.utils import clean_text


@pytest.fixture
def sample_jobs_df():
    return pd.DataFrame(
        {
            "job_id": [1, 2, 2, 3],
            "job_title": ["Data Analyst", "Data Scientist", "Data Scientist", "ML Engineer"],
            "company": ["A Corp", "B Corp", "B Corp", "C Corp"],
            "location": ["London", "Remote", "Remote", "Manchester"],
            "job_type": ["Full-time", "Full-time", "Full-time", "Contract"],
            "description": [
                "Python, SQL, Power BI",
                "Machine Learning, scikit-learn",
                "Machine Learning, scikit-learn",
                "Docker,   FastAPI,  Python!",
            ],
            "date_posted": ["2024-11-01", "2024-11-02", "2024-11-02", "2024-11-03"],
            "source": ["synthetic", "synthetic", "synthetic", "synthetic"],
        }
    )


def test_clean_text_handles_none():
    assert clean_text(None) == ""


def test_clean_text_uppercase_and_whitespace():
    text = "  PYTHON\n\tSQL   "
    assert clean_text(text) == "python sql"


def test_clean_text_keeps_skill_characters():
    text = "C++ C# CI/CD"
    assert clean_text(text) == "c++ c# ci/cd"


def test_clean_jobs_creates_cleaned_description_and_removes_duplicates(sample_jobs_df):
    cleaned = clean_jobs(sample_jobs_df)
    assert "cleaned_description" in cleaned.columns
    assert cleaned["job_id"].nunique() == len(cleaned)
    assert len(cleaned) == 3


def test_clean_jobs_raises_for_missing_columns(sample_jobs_df):
    broken_df = sample_jobs_df.drop(columns=["source", "company"])
    with pytest.raises(ValueError, match="Missing required columns"):
        clean_jobs(broken_df)
