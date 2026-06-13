"""Tests for advanced CareerCompass features."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.cv_comparison_utils import compare_cv_versions
from src.gamification_utils import evaluate_badges, load_badge_definitions
from src.i18n_utils import translate
from src.interview_question_utils import generate_interview_questions
from src.job_match_utils import classify_job_match_level, compute_job_match
from src.learning_resource_utils import get_resources_for_skills, summarize_learning_coverage
from src.progress_tracker_utils import (
    compute_skill_growth,
    get_gap_history_dataframe,
    load_progress_data,
    record_gap_analysis,
    save_progress_data,
)
from src.public_data_connectors import fetch_usajobs_jobs, list_available_connectors
from src.regional_profiles_utils import get_regional_role_profile, list_regions
from src.resume_bullet_utils import generate_resume_bullets
from src.skill_extraction import extract_skills_from_text
from src.skill_synonym_utils import expand_text_with_synonyms, normalize_skill_name, normalize_skill_list
from src.timeseries_utils import build_skill_timeseries, get_timeseries_summary


@pytest.fixture
def temp_progress_file(tmp_path, monkeypatch):
    progress_file = tmp_path / "progress.json"
    monkeypatch.setattr("src.progress_tracker_utils.get_progress_file", lambda: progress_file)
    save_progress_data({"gap_history": [], "stats": {}, "completed_actions": [], "badges_earned": []})
    return progress_file


def test_skill_synonym_normalization():
    assert normalize_skill_name("JS") == "javascript"
    assert normalize_skill_name("powerbi") == "power bi"
    expanded = expand_text_with_synonyms("Experienced with JS and PowerBI")
    assert "javascript" in expanded
    assert "power bi" in expanded


def test_skill_extraction_with_synonyms():
    skills = ["python", "javascript", "sql", "power bi"]
    extracted = extract_skills_from_text("Built apps with JS, py, and PowerBI dashboards", skills)
    assert "javascript" in extracted
    assert "python" in extracted
    assert "power bi" in extracted


def test_progress_tracker_record_and_history(temp_progress_file):
    record_gap_analysis(
        mode="market",
        target_role="Data Analyst",
        match_score=55.0,
        cv_skills=["python", "sql"],
        missing_skills=["power bi"],
        matched_skills=["python", "sql"],
    )
    df = get_gap_history_dataframe()
    assert len(df) == 1
    assert df.iloc[0]["match_score"] == 55.0


def test_skill_growth_calculation():
    growth = compute_skill_growth(["python", "sql", "docker"], ["python", "sql"])
    assert "docker" in growth["gained_skills"]
    assert growth["growth_percent"] == 50.0


def test_regional_profiles():
    regions = list_regions()
    assert "Bangladesh" in regions
    profile = get_regional_role_profile("Data & AI", "Data Analyst", "Bangladesh")
    assert profile.get("core_skills")
    assert profile.get("region") == "Bangladesh"


def test_interview_question_generator():
    df = generate_interview_questions(["python", "sql"], "Data Analyst", max_questions=8)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "question" in df.columns


def test_resume_bullet_generator():
    bullets = generate_resume_bullets(["python", "sql"], ["docker"], "Data Analyst", max_bullets=4)
    assert bullets
    assert any(item["bullet_type"] == "Strength" for item in bullets)


def test_job_match_scoring():
    job_desc = "We need Python, SQL, Power BI, and machine learning experience."
    cv_text = "I know Python, SQL, pandas, and scikit-learn."
    result = compute_job_match(job_desc, cv_text)
    assert result["match_score"] >= 0
    assert classify_job_match_level(result["match_score"]) in {
        "Strong Match", "Moderate Match", "Partial Match", "Low Match"
    }


def test_learning_resources():
    df = get_resources_for_skills(["python", "sql"])
    summary = summarize_learning_coverage(["python", "sql", "unknown-skill-xyz"])
    assert summary["requested_skills"] == 3
    assert summary["skills_with_resources"] >= 2
    assert not df.empty


def test_cv_comparison():
    cv_a = "Python, SQL, Excel experience"
    cv_b = "Python, SQL, Power BI, Docker experience"
    comparison = compare_cv_versions(cv_a, cv_b)
    assert comparison["count_b"] >= comparison["count_a"]
    assert comparison["growth"]["growth_percent"] >= 0


def test_timeseries_utils():
    df = pd.DataFrame(
        {
            "date_posted": ["2024-01-15", "2024-02-10", "2024-02-20"],
            "extracted_skills": [["python", "sql"], ["python"], ["sql", "python"]],
        }
    )
    summary = get_timeseries_summary(df)
    assert summary["available"] is True
    ts = build_skill_timeseries(df, top_n_skills=2)
    assert not ts.empty
    assert set(ts.columns) == {"period", "skill", "job_count"}


def test_gamification_badges():
    badges = load_badge_definitions()
    assert badges
    evaluated = evaluate_badges({"gap_history": [], "stats": {"gap_analyses": 1}, "badges_earned": [], "completed_actions": []})
    earned = [b for b in evaluated if b.get("earned")]
    assert any(b["badge_id"] == "first_gap_analysis" for b in earned)


def test_i18n_translate():
    assert translate("app_name", "en") == "CareerCompass"
    bn_name = translate("app_name", "bn")
    assert bn_name != "CareerCompass"


def test_public_connectors_demo_fallback():
    assert "usajobs" in list_available_connectors()
    jobs_df, meta = fetch_usajobs_jobs(keyword="data analyst")
    assert not jobs_df.empty
    assert meta["connector"] == "usajobs"


def test_pdf_report_generation():
    from src.pdf_report_utils import generate_career_pdf_report

    pdf_bytes = generate_career_pdf_report(
        "Test Report",
        [("Summary", "Match score: 75%"), ("Skills", "- python\n- sql")],
    )
    assert pdf_bytes.startswith(b"%PDF")


def test_advanced_data_files_exist():
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "data" / "skill_synonyms.json",
        root / "data" / "interview_questions.json",
        root / "data" / "learning_resources.json",
        root / "data" / "gamification_badges.json",
        root / "data" / "career_taxonomies" / "regional_profiles.json",
        root / "data" / "i18n" / "en.json",
        root / "data" / "i18n" / "bn.json",
    ]
    for path in required:
        assert path.exists(), f"Missing {path}"
        with path.open("r", encoding="utf-8") as fh:
            json.load(fh)
