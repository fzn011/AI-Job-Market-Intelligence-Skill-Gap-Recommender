"""Career progress tracking and skill growth analytics."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.utils import ensure_directory


def get_progress_file() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "user_progress" / "progress.json"


def _default_progress() -> dict:
    return {
        "gap_history": [],
        "stats": {
            "gap_analyses": 0,
            "job_matches": 0,
            "interview_preps": 0,
            "resume_bullets": 0,
            "cv_comparisons": 0,
            "pdf_exports": 0,
            "completed_actions": 0,
            "data_imports": 0,
            "language_bn_used": 0,
        },
        "completed_actions": [],
        "badges_earned": [],
    }


def load_progress_data() -> dict:
    """Load user progress JSON safely."""
    path = get_progress_file()
    if not path.exists():
        return _default_progress()
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return _default_progress()
        default = _default_progress()
        default.update(data)
        default["stats"] = {**_default_progress()["stats"], **data.get("stats", {})}
        return default
    except (json.JSONDecodeError, OSError):
        return _default_progress()


def save_progress_data(data: dict) -> None:
    """Persist progress data."""
    path = get_progress_file()
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def increment_stat(stat_name: str, amount: int = 1) -> dict:
    """Increment a tracked stat counter."""
    data = load_progress_data()
    stats = data.setdefault("stats", {})
    stats[stat_name] = int(stats.get(stat_name, 0)) + amount
    save_progress_data(data)
    return data


def record_gap_analysis(
    *,
    mode: str,
    target_role: str,
    category: str = "",
    region: str = "Global",
    match_score: float,
    cv_skills: list[str],
    missing_skills: list[str],
    matched_skills: list[str],
) -> dict:
    """Save a gap analysis snapshot and return updated progress data."""
    data = load_progress_data()
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "mode": mode,
        "target_role": target_role,
        "category": category,
        "region": region,
        "match_score": round(float(match_score), 2),
        "cv_skills": sorted(set(cv_skills)),
        "missing_skills": sorted(set(missing_skills)),
        "matched_skills": sorted(set(matched_skills)),
        "cv_skill_count": len(set(cv_skills)),
    }
    data.setdefault("gap_history", []).append(entry)
    stats = data.setdefault("stats", {})
    stats["gap_analyses"] = int(stats.get("gap_analyses", 0)) + 1
    save_progress_data(data)
    return data


def get_gap_history_dataframe() -> pd.DataFrame:
    """Return gap history as a dataframe."""
    data = load_progress_data()
    history = data.get("gap_history", [])
    if not history:
        return pd.DataFrame(
            columns=[
                "timestamp", "mode", "target_role", "category", "region",
                "match_score", "cv_skill_count", "missing_count", "matched_count",
            ]
        )
    rows = []
    for item in history:
        rows.append(
            {
                "timestamp": item.get("timestamp", ""),
                "mode": item.get("mode", ""),
                "target_role": item.get("target_role", ""),
                "category": item.get("category", ""),
                "region": item.get("region", "Global"),
                "match_score": item.get("match_score", 0.0),
                "cv_skill_count": item.get("cv_skill_count", len(item.get("cv_skills", []))),
                "missing_count": len(item.get("missing_skills", [])),
                "matched_count": len(item.get("matched_skills", [])),
            }
        )
    return pd.DataFrame(rows)


def compute_skill_growth(current_skills: list[str], previous_skills: list[str]) -> dict:
    """Compute skill growth metrics between two skill lists."""
    current = set(current_skills)
    previous = set(previous_skills)
    gained = sorted(current - previous)
    lost = sorted(previous - current)
    retained = sorted(current & previous)

    prev_count = len(previous)
    growth_pct = round((len(gained) / prev_count) * 100, 2) if prev_count else 0.0
    retention_pct = round((len(retained) / prev_count) * 100, 2) if prev_count else 0.0

    return {
        "gained_skills": gained,
        "lost_skills": lost,
        "retained_skills": retained,
        "growth_percent": growth_pct,
        "retention_percent": retention_pct,
        "previous_count": prev_count,
        "current_count": len(current),
    }


def compute_progress_skill_growth() -> dict:
    """Compare latest gap analysis to the previous one."""
    data = load_progress_data()
    history = data.get("gap_history", [])
    if len(history) < 2:
        return {"available": False, "message": "Need at least 2 gap analyses to compute growth."}

    previous = history[-2]
    current = history[-1]
    growth = compute_skill_growth(current.get("cv_skills", []), previous.get("cv_skills", []))
    growth["available"] = True
    growth["previous_match_score"] = previous.get("match_score", 0.0)
    growth["current_match_score"] = current.get("match_score", 0.0)
    growth["match_score_delta"] = round(
        float(current.get("match_score", 0.0)) - float(previous.get("match_score", 0.0)), 2
    )
    return growth


def mark_action_completed(action_id: str) -> dict:
    """Mark a career action as completed."""
    data = load_progress_data()
    completed = data.setdefault("completed_actions", [])
    if action_id not in completed:
        completed.append(action_id)
        stats = data.setdefault("stats", {})
        stats["completed_actions"] = len(completed)
        save_progress_data(data)
    return data
