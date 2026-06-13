"""Tests for Quick Start wizard helpers."""

from __future__ import annotations

from src.quick_start_utils import (
    QUICK_START_GOALS,
    SAMPLE_CV,
    run_explore_quick_start,
    run_job_match_quick_start,
    run_skill_gap_quick_start,
)


def test_quick_start_goals_defined():
    assert len(QUICK_START_GOALS) == 3


def test_skill_gap_quick_start_with_sample_cv():
    result = run_skill_gap_quick_start("Data & AI", "Data Analyst", SAMPLE_CV, "Global")
    assert result["success"] is True
    assert result["match_score"] >= 0
    assert result.get("missing_skills") is not None


def test_job_match_quick_start():
    from src.quick_start_utils import SAMPLE_JOB

    result = run_job_match_quick_start(SAMPLE_JOB, SAMPLE_CV)
    assert result["success"] is True
    assert result["match_score"] >= 0


def test_explore_quick_start():
    result = run_explore_quick_start("Data & AI", "Data Analyst", "Bangladesh")
    assert result["success"] is True
    assert result.get("core_skills")


def test_skill_gap_empty_cv_fails():
    result = run_skill_gap_quick_start("Data & AI", "Data Analyst", "hello world only")
    assert result["success"] is False
