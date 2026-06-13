"""Voice-style interview simulator with timed prompts and self-rating rubric."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.interview_question_utils import generate_interview_questions


def load_voice_rubric() -> dict:
    path = Path(__file__).resolve().parents[1] / "data" / "voice_interview_rubric.json"
    if not path.exists():
        return {"dimensions": ["clarity", "structure", "technical_depth", "confidence", "relevance"], "scale": {}}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def create_interview_session(
    missing_skills: list[str],
    target_role: str,
    num_questions: int = 5,
    seconds_per_question: int = 120,
) -> dict:
    """Create a timed interview session payload."""
    questions_df = generate_interview_questions(missing_skills, target_role, max_questions=num_questions)
    questions = questions_df["question"].tolist() if not questions_df.empty else [
        f"Tell me about your experience with {skill}." for skill in missing_skills[:num_questions]
    ]

    return {
        "session_id": datetime.now(UTC).strftime("%Y%m%d%H%M%S"),
        "target_role": target_role,
        "seconds_per_question": seconds_per_question,
        "questions": questions,
        "rubric_dimensions": load_voice_rubric().get("dimensions", []),
        "created_at": datetime.now(UTC).isoformat(),
    }


def score_interview_session(
    questions: list[str],
    ratings: list[dict],
) -> dict:
    """
    Score a completed session from self-ratings.

    ratings: list of dicts with keys question, clarity, structure, technical_depth, confidence, relevance
    """
    rubric = load_voice_rubric()
    dimensions = rubric.get("dimensions", [])
    rows = []

    for idx, question in enumerate(questions):
        rating = ratings[idx] if idx < len(ratings) else {}
        dim_scores = [float(rating.get(dim, 0)) for dim in dimensions]
        avg = round(sum(dim_scores) / len(dim_scores), 2) if dim_scores else 0.0
        rows.append({"question": question, "average_score": avg, **{dim: rating.get(dim, 0) for dim in dimensions}})

    df = pd.DataFrame(rows)
    overall = round(float(df["average_score"].mean()), 2) if not df.empty else 0.0

    if overall >= 4.0:
        readiness = "Strong interview readiness"
    elif overall >= 3.0:
        readiness = "Developing — practice weak dimensions"
    else:
        readiness = "Needs more preparation"

    return {
        "overall_score": overall,
        "readiness": readiness,
        "question_scores": rows,
        "dimensions": dimensions,
    }


def format_session_report(session: dict, score_result: dict) -> str:
    lines = [
        "CareerCompass Voice Interview Simulator Report",
        "=============================================",
        f"Role: {session.get('target_role', 'General')}",
        f"Overall score: {score_result.get('overall_score', 0.0)}/5",
        f"Readiness: {score_result.get('readiness', 'N/A')}",
        "",
    ]
    for idx, row in enumerate(score_result.get("question_scores", []), start=1):
        lines.append(f"{idx}. {row.get('question', '')}")
        lines.append(f"   Average: {row.get('average_score', 0.0)}/5")
    return "\n".join(lines)
