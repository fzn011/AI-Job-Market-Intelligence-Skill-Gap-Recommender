"""Tests for skill extraction utilities."""

import pandas as pd

from src.skill_extraction import (
    compute_skill_frequency,
    extract_skills_from_text,
)


def test_extract_skills_finds_python_sql_power_bi():
    skills = ["python", "sql", "power bi", "r"]
    text = "Need Python programming, SQL queries, and Power BI dashboarding."
    result = extract_skills_from_text(text, skills)
    assert "python" in result
    assert "sql" in result
    assert "power bi" in result


def test_extract_skills_does_not_match_r_inside_words():
    skills = ["r", "python"]
    text = "We focus on robust analytics and platform reliability."
    result = extract_skills_from_text(text, skills)
    assert "r" not in result


def test_extract_skills_finds_multiword_skills():
    skills = ["machine learning", "scikit-learn", "power bi"]
    text = "Hands-on machine learning using scikit-learn and Power BI reporting."
    result = extract_skills_from_text(text, skills)
    assert "machine learning" in result
    assert "scikit-learn" in result
    assert "power bi" in result


def test_compute_skill_frequency_counts_correctly():
    df = pd.DataFrame(
        {
            "extracted_skills": [
                ["python", "sql"],
                ["python", "power bi"],
                ["sql"],
            ]
        }
    )
    freq_df = compute_skill_frequency(df)

    expected = {"python": 2, "sql": 2, "power bi": 1}
    actual = dict(zip(freq_df["skill"], freq_df["frequency"]))
    assert actual == expected
