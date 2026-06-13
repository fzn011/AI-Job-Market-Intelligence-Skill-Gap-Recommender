"""ATS-friendly resume bullet generation from skill gap results."""

from __future__ import annotations

BULLET_TEMPLATES = {
    "matched": [
        "Applied {skill} to deliver {output}, improving {impact}.",
        "Used {skill} in {context} to produce measurable {output}.",
        "Demonstrated {skill} by building {output} with clear {impact}.",
    ],
    "missing": [
        "Currently strengthening {skill} through hands-on projects focused on {output}.",
        "Building practical experience in {skill} via portfolio work and structured practice.",
    ],
}

ROLE_OUTPUTS = {
    "Data Analyst": ("dashboards and KPI reports", "decision speed"),
    "Data Scientist": ("predictive models", "model accuracy"),
    "Software Developer": ("production-ready features", "system reliability"),
    "Credit Analyst": ("credit risk assessments", "risk visibility"),
    "UI/UX Designer": ("user-centered design case studies", "usability"),
    "default": ("portfolio deliverables", "business outcomes"),
}


def _get_role_context(target_role: str) -> tuple[str, str]:
    return ROLE_OUTPUTS.get(target_role, ROLE_OUTPUTS["default"])


def generate_resume_bullets(
    matched_skills: list[str],
    missing_skills: list[str],
    target_role: str = "",
    max_bullets: int = 8,
) -> list[dict]:
    """Generate ATS-friendly resume bullets from skill gap data."""
    output, impact = _get_role_context(target_role)
    bullets: list[dict] = []

    for skill in matched_skills[: max_bullets // 2 + 1]:
        template = BULLET_TEMPLATES["matched"][len(bullets) % len(BULLET_TEMPLATES["matched"])]
        bullets.append(
            {
                "bullet": template.format(skill=skill, output=output, impact=impact, context=target_role or "project work"),
                "skill": skill,
                "bullet_type": "Strength",
                "ats_keywords": [skill, target_role.lower()] if target_role else [skill],
            }
        )

    for skill in missing_skills[: max(1, max_bullets - len(bullets))]:
        template = BULLET_TEMPLATES["missing"][(len(bullets) + 1) % len(BULLET_TEMPLATES["missing"])]
        bullets.append(
            {
                "bullet": template.format(skill=skill, output=output, impact=impact, context=target_role or "self-directed learning"),
                "skill": skill,
                "bullet_type": "Development",
                "ats_keywords": [skill, "learning", "portfolio"],
            }
        )

    return bullets[:max_bullets]


def format_resume_bullets_text(bullets: list[dict], target_role: str = "") -> str:
    """Format bullets for download."""
    lines = [
        "CareerCompass ATS Resume Bullets",
        "================================",
        f"Target Role: {target_role or 'General'}",
        "",
    ]
    for idx, item in enumerate(bullets, start=1):
        lines.append(f"{idx}. {item['bullet']}")
        lines.append(f"   Type: {item['bullet_type']} | Keywords: {', '.join(item['ats_keywords'])}")
        lines.append("")
    lines.append("Note: Customize bullets to reflect your real experience accurately.")
    return "\n".join(lines)
