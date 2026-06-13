"""Tests for career taxonomy utilities."""

from __future__ import annotations

import pandas as pd
import pytest

from src.career_taxonomy_utils import (
    build_category_skill_dataframe,
    classify_skill_type,
    flatten_category_skills,
    generate_career_action_plan,
    get_role_core_skills,
    get_role_profile,
    get_roles_for_category,
    get_target_role_skills,
    list_career_categories,
    load_career_action_templates,
    load_category_skill_taxonomy,
    load_role_profiles,
    recommend_career_actions,
    validate_action_templates,
)


EXPECTED_CATEGORIES = [
    "Data & AI",
    "Software & IT",
    "Banking & Finance",
    "Business & Administration",
    "Marketing & Sales",
    "Design & Creative",
    "Education & Teaching",
    "Healthcare",
    "Engineering",
    "Customer Support",
    "Operations & Project Management",
    "General Entry-Level Jobs",
]


def test_list_career_categories_returns_expected_categories():
    categories = list_career_categories()
    assert categories
    for expected in EXPECTED_CATEGORIES:
        assert expected in categories


def test_load_category_skill_taxonomy_valid_and_invalid():
    taxonomy = load_category_skill_taxonomy("Data & AI")
    assert isinstance(taxonomy, dict)
    assert "technical_skills" in taxonomy
    assert load_category_skill_taxonomy("Invalid Category XYZ") == {}


def test_flatten_category_skills_returns_skills():
    skills = flatten_category_skills("Data & AI")
    assert isinstance(skills, list)
    assert "python" in skills
    assert "sql" in skills


def test_load_role_profiles_returns_dict():
    profiles = load_role_profiles()
    assert isinstance(profiles, dict)
    assert "Data & AI" in profiles


def test_get_roles_for_category_returns_role_list():
    roles = get_roles_for_category("Data & AI")
    assert isinstance(roles, list)
    assert "Data Analyst" in roles
    assert get_roles_for_category("Invalid Category") == []


def test_get_role_profile_returns_expected_data():
    profile = get_role_profile("Data & AI", "Data Analyst")
    assert profile
    assert "core_skills" in profile
    assert "excel" in profile["core_skills"] or "sql" in profile["core_skills"]


def test_get_target_role_skills_combines_core_and_helpful():
    skills = get_target_role_skills("Data & AI", "Data Analyst")
    core = get_role_core_skills("Data & AI", "Data Analyst")
    assert set(core).issubset(set(skills))
    assert len(skills) >= len(core)


def test_load_career_action_templates_has_required_keys():
    templates = load_career_action_templates()
    assert isinstance(templates, list)
    assert templates
    required = {
        "action_id", "title", "category", "action_type", "difficulty",
        "estimated_time", "skills_covered", "description", "deliverables", "portfolio_value",
    }
    for template in templates[:5]:
        assert required.issubset(set(template.keys()))


def test_recommend_career_actions_returns_scored_dataframe():
    missing = ["python", "sql", "power bi"]
    df = recommend_career_actions(missing_skills=missing, category="Data & AI", max_actions=5)
    assert isinstance(df, pd.DataFrame)
    if not df.empty:
        assert "coverage_score" in df.columns
        assert "title" in df.columns
        assert df.iloc[0]["category"] == "Data & AI"


def test_generate_career_action_plan_includes_category_and_role():
    df = recommend_career_actions(["python", "sql"], "Data & AI", max_actions=3)
    plan = generate_career_action_plan("Data & AI", "Data Analyst", ["python", "sql"], df)
    assert "Data & AI" in plan
    assert "Data Analyst" in plan
    assert "rule-based" in plan.lower()


def test_classify_skill_type_returns_correct_type():
    taxonomy = load_category_skill_taxonomy("Data & AI")
    assert classify_skill_type("python", taxonomy) == "technical_skills"
    assert classify_skill_type("communication", taxonomy) == "soft_skills"
    assert classify_skill_type("unknown-skill-xyz", taxonomy) == "uncategorized"


def test_build_category_skill_dataframe_has_expected_columns():
    df = build_category_skill_dataframe("Design & Creative")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["skill", "skill_type", "category"]
    assert (df["category"] == "Design & Creative").all()


def test_validate_action_templates_has_no_errors():
    errors = validate_action_templates()
    assert errors == []
