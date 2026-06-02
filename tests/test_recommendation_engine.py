"""Tests for recommendation engine utilities."""

from src.recommendation_engine import compute_skill_gap


def test_compute_skill_gap_returns_matched_and_missing():
    user = ["Python", "SQL", "sql"]
    market = ["python", "sql", "docker"]
    result = compute_skill_gap(user, market)

    assert result["matched_skills"] == ["python", "sql"]
    assert result["missing_skills"] == ["docker"]


def test_compute_skill_gap_score_calculation():
    user = ["python"]
    market = ["python", "sql", "docker", "fastapi"]
    result = compute_skill_gap(user, market)

    assert result["match_score"] == 25.0


def test_compute_skill_gap_empty_market_score_zero():
    result = compute_skill_gap(["python"], [])
    assert result["match_score"] == 0.0
    assert result["missing_skills"] == []
