"""Tests for premium CareerCompass features."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.company_prep_utils import build_company_prep_summary, list_companies
from src.linkedin_optimizer_utils import optimize_linkedin_about
from src.peer_benchmark_utils import compute_peer_benchmark
from src.salary_estimator_utils import estimate_salary_band, list_salary_regions
from src.secrets_utils import get_usajobs_credentials
from src.semantic_skill_utils import merge_extraction_results, semantic_model_available
from src.study_calendar_utils import generate_study_plan_ics
from src.voice_interview_utils import create_interview_session, score_interview_session
from src.email_digest_utils import build_weekly_digest_text, send_weekly_digest
from src.public_data_connectors import fetch_usajobs_jobs


def test_company_prep_packs():
    companies = list_companies()
    assert "Google" in companies
    assert "bKash" in companies
    summary = build_company_prep_summary("Google", "Data Scientist", ["machine learning"])
    assert "Google" in summary
    assert "machine learning" in summary


def test_salary_estimator():
    regions = list_salary_regions()
    assert regions
    result = estimate_salary_band("Data Analyst", "Bangladesh", 60.0, "mid")
    assert result["available"] is True
    assert "estimated_range" in result


def test_linkedin_optimizer():
    result = optimize_linkedin_about(
        "I work with data and build reports.",
        "Data Analyst",
        ["python", "sql", "power bi"],
    )
    assert result["optimized_text"]
    assert result["suggestions"]


def test_study_calendar_ics():
    actions = [
        {"title": "Build Dashboard", "action_type": "Project", "difficulty": "Intermediate",
         "estimated_time": "2 weeks", "description": "Create a BI dashboard.", "matched_skills": ["power bi"]},
    ]
    ics = generate_study_plan_ics(actions)
    assert ics.startswith("BEGIN:VCALENDAR")
    assert "Build Dashboard" in ics


def test_voice_interview_session():
    session = create_interview_session(["python", "sql"], "Data Analyst", num_questions=3, seconds_per_question=60)
    assert len(session["questions"]) == 3
    ratings = [{"question": q, "clarity": 4, "structure": 3, "technical_depth": 4, "confidence": 3, "relevance": 4}
               for q in session["questions"]]
    score = score_interview_session(session["questions"], ratings)
    assert score["overall_score"] > 0


def test_peer_benchmark():
    cv = "Python, SQL, pandas, scikit-learn, communication skills"
    result = compute_peer_benchmark(cv, "Data Analyst")
    assert result["available"] is True
    assert 0 <= result["percentile"] <= 100


def test_email_digest_preview():
    text = build_weekly_digest_text()
    assert "CareerCompass Weekly Progress Digest" in text
    result = send_weekly_digest(dry_run=True)
    assert result["preview"]


def test_semantic_merge_fallback():
    merged = merge_extraction_results(["python"], ["sql"])
    assert "python" in merged and "sql" in merged
    available, _ = semantic_model_available()
    assert isinstance(available, bool)


def test_usajobs_credentials_from_secrets():
    key, email = get_usajobs_credentials()
    # secrets.toml should be loaded in dev environment
    assert email


def test_usajobs_live_or_fallback():
    jobs_df, meta = fetch_usajobs_jobs(keyword="data", results_per_page=3)
    assert not jobs_df.empty
    assert meta["connector"] == "usajobs"
    assert meta["mode"] in {"live_api", "demo_fallback"}


def test_premium_data_files_exist():
    root = Path(__file__).resolve().parents[1]
    for rel in ["company_prep_packs.json", "salary_bands.json", "voice_interview_rubric.json"]:
        path = root / "data" / rel
        assert path.exists()
        json.load(path.open())
