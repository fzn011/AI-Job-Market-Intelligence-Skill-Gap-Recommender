"""Career taxonomy loading and recommendation utilities for CareerCompass."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
import textwrap

import pandas as pd


CATEGORY_FILE_MAP = {
    "Data & AI": "data_ai_skills.json",
    "Software & IT": "software_it_skills.json",
    "Banking & Finance": "banking_finance_skills.json",
    "Business & Administration": "business_admin_skills.json",
    "Marketing & Sales": "marketing_sales_skills.json",
    "Design & Creative": "design_creative_skills.json",
    "Education & Teaching": "education_teaching_skills.json",
    "Healthcare": "healthcare_skills.json",
    "Engineering": "engineering_skills.json",
    "Customer Support": "customer_support_skills.json",
    "Operations & Project Management": "operations_project_management_skills.json",
    "General Entry-Level Jobs": "general_entry_level_skills.json",
}

REQUIRED_ACTION_KEYS = {
    "action_id",
    "title",
    "category",
    "action_type",
    "difficulty",
    "estimated_time",
    "skills_covered",
    "description",
    "deliverables",
    "portfolio_value",
}


def _load_json_file(path: Path) -> dict | list:
    """Load JSON from disk, returning dict or list."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def get_career_taxonomy_dir() -> Path:
    """Return the career taxonomies directory path."""
    return Path(__file__).resolve().parents[1] / "data" / "career_taxonomies"


def _normalize_skill(skill: str) -> str:
    return str(skill).strip().lower()


def _normalize_skill_list(skills: list[str] | None) -> list[str]:
    if not skills:
        return []
    cleaned = {_normalize_skill(skill) for skill in skills if skill and str(skill).strip()}
    return sorted(cleaned)


def list_career_categories() -> list[str]:
    """Return available career category names."""
    taxonomy_dir = get_career_taxonomy_dir()
    if not taxonomy_dir.exists():
        return []

    categories = []
    for category, filename in CATEGORY_FILE_MAP.items():
        if (taxonomy_dir / filename).exists():
            categories.append(category)

    role_profiles = load_role_profiles()
    for category in role_profiles:
        if category not in categories:
            categories.append(category)

    return sorted(categories, key=lambda name: list(CATEGORY_FILE_MAP.keys()).index(name)
                  if name in CATEGORY_FILE_MAP else len(CATEGORY_FILE_MAP))


def load_category_skill_taxonomy(category: str) -> dict:
    """Load skill taxonomy JSON for a category."""
    if not category or category not in CATEGORY_FILE_MAP:
        return {}

    path = get_career_taxonomy_dir() / CATEGORY_FILE_MAP[category]
    if not path.exists():
        return {}

    data = _load_json_file(path)
    return data if isinstance(data, dict) else {}


def flatten_category_skills(category: str) -> list[str]:
    """Return all skills for a category as a flat sorted list."""
    taxonomy = load_category_skill_taxonomy(category)
    if not taxonomy:
        return []

    skills: set[str] = set()
    for skill_list in taxonomy.values():
        if isinstance(skill_list, list):
            skills.update(_normalize_skill_list(skill_list))
    return sorted(skills)


def load_role_profiles() -> dict:
    """Load role profile definitions."""
    path = get_career_taxonomy_dir() / "role_profiles.json"
    if not path.exists():
        return {}

    data = _load_json_file(path)
    return data if isinstance(data, dict) else {}


def get_roles_for_category(category: str) -> list[str]:
    """Return role names available for a category."""
    profiles = load_role_profiles()
    roles = profiles.get(category, {})
    if not isinstance(roles, dict):
        return []
    return sorted(roles.keys())


def get_role_profile(category: str, role: str) -> dict:
    """Return one role profile dictionary."""
    profiles = load_role_profiles()
    category_profiles = profiles.get(category, {})
    if not isinstance(category_profiles, dict):
        return {}

    profile = category_profiles.get(role, {})
    return profile if isinstance(profile, dict) else {}


def get_role_core_skills(category: str, role: str) -> list[str]:
    """Return core skills for a role."""
    profile = get_role_profile(category, role)
    return _normalize_skill_list(profile.get("core_skills", []))


def get_role_helpful_skills(category: str, role: str) -> list[str]:
    """Return helpful skills for a role."""
    profile = get_role_profile(category, role)
    return _normalize_skill_list(profile.get("helpful_skills", []))


def get_target_role_skills(category: str, role: str) -> list[str]:
    """Return combined core and helpful skills for a role."""
    combined = set(get_role_core_skills(category, role))
    combined.update(get_role_helpful_skills(category, role))
    return sorted(combined)


def load_career_action_templates() -> list[dict]:
    """Load career action templates."""
    path = get_career_taxonomy_dir() / "career_action_templates.json"
    if not path.exists():
        return []

    data = _load_json_file(path)
    if not isinstance(data, list):
        return []

    cleaned: list[dict] = []
    for item in data:
        if isinstance(item, dict):
            cleaned.append(item)
    return cleaned


def classify_skill_type(skill: str, taxonomy: dict) -> str:
    """Classify a skill into technical, domain, soft, or uncategorized."""
    normalized = _normalize_skill(skill)
    if not normalized or not taxonomy:
        return "uncategorized"

    for skill_type, skill_list in taxonomy.items():
        if not isinstance(skill_list, list):
            continue
        normalized_list = {_normalize_skill(value) for value in skill_list}
        if normalized in normalized_list:
            return skill_type

    return "uncategorized"


def build_category_skill_dataframe(category: str) -> pd.DataFrame:
    """Return a dataframe of skills with type and category."""
    taxonomy = load_category_skill_taxonomy(category)
    rows = []
    for skill in flatten_category_skills(category):
        rows.append(
            {
                "skill": skill,
                "skill_type": classify_skill_type(skill, taxonomy),
                "category": category,
            }
        )
    return pd.DataFrame(rows)


def extract_skills_from_text(text: str, category: str) -> list[str]:
    """Extract category skills from free text using boundary-aware matching."""
    import re

    if not text or not str(text).strip():
        return []

    normalized_text = f" {str(text).lower()} "
    found: set[str] = set()

    for skill in flatten_category_skills(category):
        pattern = rf"(?<![a-z0-9]){re.escape(skill)}(?![a-z0-9])"
        if re.search(pattern, normalized_text):
            found.add(skill)

    return sorted(found)


def compute_role_skill_gap(cv_skills: list[str], category: str, role: str) -> dict:
    """Compare CV skills against a role profile."""
    cv_set = set(_normalize_skill_list(cv_skills))
    core_skills = get_role_core_skills(category, role)
    helpful_skills = get_role_helpful_skills(category, role)
    target_skills = get_target_role_skills(category, role)
    target_set = set(target_skills)

    matched = sorted(cv_set & target_set)
    missing_core = sorted(set(core_skills) - cv_set)
    missing_helpful = sorted(set(helpful_skills) - cv_set)
    missing_all = sorted(target_set - cv_set)
    extra = sorted(cv_set - target_set)

    core_total = len(core_skills)
    core_matched = len(set(core_skills) & cv_set)
    match_score = round((core_matched / core_total) * 100, 2) if core_total else 0.0

    taxonomy = load_category_skill_taxonomy(category)
    soft_gaps = [
        skill for skill in missing_all
        if classify_skill_type(skill, taxonomy) == "soft_skills"
    ]

    return {
        "match_score": match_score,
        "matched_skills": matched,
        "missing_core_skills": missing_core,
        "missing_helpful_skills": missing_helpful,
        "missing_skills": missing_all,
        "extra_cv_skills": extra,
        "soft_skill_gaps": sorted(soft_gaps),
        "core_skills_total": core_total,
        "core_skills_matched": core_matched,
        "target_skills_total": len(target_skills),
    }


def recommend_career_actions(
    missing_skills: list[str],
    category: str,
    max_actions: int = 10,
) -> pd.DataFrame:
    """Score and rank career action templates for missing skills."""
    templates = load_career_action_templates()
    if not templates:
        return pd.DataFrame()

    missing_set = set(_normalize_skill_list(missing_skills))
    rows = []

    for template in templates:
        if template.get("category") != category and category != "All Categories":
            continue

        covered = _normalize_skill_list(template.get("skills_covered", []))
        matched = sorted(missing_set & set(covered))
        if not matched and missing_set:
            continue

        coverage_score = round((len(matched) / max(len(missing_set), 1)) * 100, 2)
        rows.append(
            {
                "title": template.get("title", ""),
                "category": template.get("category", ""),
                "action_type": template.get("action_type", ""),
                "difficulty": template.get("difficulty", ""),
                "estimated_time": template.get("estimated_time", ""),
                "matched_skills": matched,
                "coverage_score": coverage_score,
                "description": template.get("description", ""),
                "deliverables": template.get("deliverables", []),
                "portfolio_value": template.get("portfolio_value", ""),
            }
        )

    if not rows and missing_set:
        for template in templates:
            if template.get("category") != category:
                continue
            covered = _normalize_skill_list(template.get("skills_covered", []))
            rows.append(
                {
                    "title": template.get("title", ""),
                    "category": template.get("category", ""),
                    "action_type": template.get("action_type", ""),
                    "difficulty": template.get("difficulty", ""),
                    "estimated_time": template.get("estimated_time", ""),
                    "matched_skills": covered[:3],
                    "coverage_score": 0.0,
                    "description": template.get("description", ""),
                    "deliverables": template.get("deliverables", []),
                    "portfolio_value": template.get("portfolio_value", ""),
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df = df.sort_values(["coverage_score", "title"], ascending=[False, True]).head(max_actions)
    return df.reset_index(drop=True)


def generate_career_action_plan(
    category: str,
    role: str,
    missing_skills: list[str],
    recommendations_df: pd.DataFrame,
) -> str:
    """Generate a downloadable text career action plan."""
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    profile = get_role_profile(category, role)

    lines = [
        "CareerCompass Career Action Plan",
        "================================",
        f"Generated: {timestamp}",
        "",
        f"Category: {category}",
        f"Target Role: {role}",
        f"Level: {profile.get('level', 'N/A')}",
        "",
        "Missing Skills:",
    ]

    if missing_skills:
        lines.extend(f"- {skill}" for skill in missing_skills)
    else:
        lines.append("- None identified")

    lines.extend(["", "Recommended Actions:"])
    if recommendations_df.empty:
        lines.append("- No action templates matched. Explore Career Explorer for role guidance.")
    else:
        for idx, row in recommendations_df.iterrows():
            matched = ", ".join(row.get("matched_skills", [])) or "general role prep"
            lines.append(f"{idx + 1}. {row['title']} ({row['action_type']})")
            lines.append(f"   Skills: {matched}")
            lines.append(f"   Time: {row['estimated_time']} | Difficulty: {row['difficulty']}")
            lines.append(f"   Why: {row['portfolio_value']}")

    lines.extend(
        [
            "",
            "Suggested 30-Day Plan:",
            "Week 1: Pick one high-impact action and gather materials.",
            "Week 2: Execute the action and document deliverables.",
            "Week 3: Add a second action focused on missing core skills.",
            "Week 4: Review outcomes, update CV bullets, and prepare interview stories.",
            "",
            "Note: Recommendations are rule-based guidance, not hiring guarantees.",
            "Role expectations vary by country, company, and seniority level.",
        ]
    )

    return "\n".join(lines)


def generate_role_preparation_plan(category: str, role: str) -> str:
    """Generate a downloadable role preparation plan for Career Explorer."""
    profile = get_role_profile(category, role)
    core = get_role_core_skills(category, role)
    helpful = get_role_helpful_skills(category, role)
    actions = profile.get("recommended_actions", [])

    body = textwrap.dedent(
        f"""
        CareerCompass Role Preparation Plan
        =================================
        Category: {category}
        Role: {role}
        Level: {profile.get('level', 'N/A')}

        Core Skills:
        {chr(10).join(f'- {skill}' for skill in core) or '- None listed'}

        Helpful Skills:
        {chr(10).join(f'- {skill}' for skill in helpful) or '- None listed'}

        Typical Outputs:
        {chr(10).join(f'- {item}' for item in profile.get('typical_outputs', [])) or '- None listed'}

        Recommended Actions:
        {chr(10).join(f'- {item}' for item in actions) or '- Explore career action templates'}

        Note: This plan uses curated role profiles and transparent rule-based guidance.
        """
    ).strip()

    return body


def validate_action_templates() -> list[str]:
    """Return validation errors for action templates."""
    errors = []
    for idx, template in enumerate(load_career_action_templates()):
        missing = REQUIRED_ACTION_KEYS - set(template.keys())
        if missing:
            errors.append(f"Template {idx} missing keys: {sorted(missing)}")
    return errors
