"""Rule-based LinkedIn About section optimizer (no paid LLM APIs)."""

from __future__ import annotations

import re

from src.job_match_utils import extract_cv_skills_enhanced
from src.skill_synonym_utils import normalize_skill_list


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"[.\n]+", text)
    return [part.strip() for part in parts if part.strip()]


def optimize_linkedin_about(
    about_text: str,
    target_role: str = "",
    target_skills: list[str] | None = None,
) -> dict:
    """
    Rewrite LinkedIn About text to be more ATS-friendly and role-aligned.

    Rule-based: adds role headline, groups skills, adds CTA — no external AI API.
    """
    if not about_text or not str(about_text).strip():
        return {"optimized_text": "", "suggestions": ["Paste your LinkedIn About section first."]}

    detected = extract_cv_skills_enhanced(about_text)
    desired = normalize_skill_list(target_skills or [])
    missing = sorted(set(desired) - set(detected)) if desired else []
    matched = sorted(set(desired) & set(detected)) if desired else detected[:8]

    role_line = f"{target_role} | " if target_role else ""
    skill_line = ", ".join(matched[:10]) if matched else "key technical and soft skills"

    sentences = _split_sentences(about_text)
    body = ". ".join(sentences[:4])
    if body and not body.endswith("."):
        body += "."

    optimized_parts = [
        f"{role_line}{skill_line}.",
        body,
    ]

    if missing:
        optimized_parts.append(
            f"Currently expanding expertise in {', '.join(missing[:5])} through projects and continuous learning."
        )

    optimized_parts.append("Open to opportunities where I can deliver measurable impact. Let's connect.")

    suggestions = []
    if len(about_text) < 200:
        suggestions.append("Add 2-3 quantified achievements (metrics, %, time saved).")
    if missing:
        suggestions.append(f"Mention these target skills if true: {', '.join(missing[:5])}.")
    if not any(char.isdigit() for char in about_text):
        suggestions.append("Include at least one number to show measurable impact.")
    suggestions.append("Use short paragraphs and front-load role keywords in the first 2 lines.")

    return {
        "optimized_text": "\n\n".join(part for part in optimized_parts if part),
        "detected_skills": detected,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions,
    }
