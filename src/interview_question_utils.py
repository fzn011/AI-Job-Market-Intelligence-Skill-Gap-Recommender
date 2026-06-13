"""Rule-based interview question generation."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def get_interview_questions_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "interview_questions.json"


def load_interview_question_bank() -> dict:
    path = get_interview_questions_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def generate_interview_questions(
    missing_skills: list[str],
    target_role: str = "",
    max_questions: int = 12,
) -> pd.DataFrame:
    """Generate interview questions based on missing skills and role."""
    bank = load_interview_question_bank()
    rows = []

    normalized_missing = [str(skill).strip().lower() for skill in missing_skills if skill]
    for skill in normalized_missing:
        questions = bank.get(skill, [])
        for question in questions[:2]:
            rows.append(
                {
                    "question": question,
                    "focus_skill": skill,
                    "question_type": "Technical / Skill-based",
                    "priority": "High" if skill in normalized_missing[:5] else "Medium",
                }
            )

    role_questions = bank.get("_role_behavioral", {}).get(target_role, [])
    for question in role_questions:
        rows.append(
            {
                "question": question,
                "focus_skill": target_role or "role",
                "question_type": "Behavioral / Role-based",
                "priority": "High",
            }
        )

    if not rows and normalized_missing:
        for skill in normalized_missing[:5]:
            rows.append(
                {
                    "question": f"Describe a project or experience where you used {skill}. What was the outcome?",
                    "focus_skill": skill,
                    "question_type": "Experience-based",
                    "priority": "Medium",
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.head(max_questions).reset_index(drop=True)


def generate_interview_prep_text(questions_df: pd.DataFrame, target_role: str) -> str:
    """Create downloadable interview prep text."""
    lines = [
        "CareerCompass Interview Preparation",
        "===================================",
        f"Target Role: {target_role or 'General'}",
        "",
    ]
    if questions_df.empty:
        lines.append("No questions generated.")
        return "\n".join(lines)

    for idx, row in questions_df.iterrows():
        lines.append(f"{idx + 1}. [{row['question_type']}] {row['question']}")
        lines.append(f"   Focus: {row['focus_skill']} | Priority: {row['priority']}")
        lines.append("")

    lines.append("Tip: Use STAR method (Situation, Task, Action, Result) for behavioral answers.")
    return "\n".join(lines)
