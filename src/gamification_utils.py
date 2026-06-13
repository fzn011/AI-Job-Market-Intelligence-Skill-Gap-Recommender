"""Gamification badges and achievement tracking."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.progress_tracker_utils import load_progress_data, save_progress_data


def get_badges_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "gamification_badges.json"


def load_badge_definitions() -> list[dict]:
    path = get_badges_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else []


def _evaluate_criteria(criteria: str, stats: dict, progress: dict) -> bool:
    if ">=" in criteria:
        key, value = criteria.split(">=", 1)
        key = key.strip()
        threshold = int(value.strip())
        if key == "skill_growth":
            history = progress.get("gap_history", [])
            if len(history) < 2:
                return False
            prev = set(history[-2].get("cv_skills", []))
            curr = set(history[-1].get("cv_skills", []))
            gained = len(curr - prev)
            growth_pct = (gained / len(prev)) * 100 if prev else 0
            return growth_pct >= threshold
        return int(stats.get(key, 0)) >= threshold
    return False


def evaluate_badges(progress: dict | None = None) -> list[dict]:
    """Evaluate which badges are earned."""
    progress_data = progress if progress is not None else load_progress_data()
    stats = progress_data.get("stats", {})
    earned_ids = set(progress_data.get("badges_earned", []))
    badges = []

    for badge in load_badge_definitions():
        badge_id = badge.get("badge_id", "")
        criteria = badge.get("criteria", "")
        earned = badge_id in earned_ids or _evaluate_criteria(criteria, stats, progress_data)
        if earned and badge_id and badge_id not in earned_ids:
            earned_ids.add(badge_id)
        badges.append({**badge, "earned": earned})

    if earned_ids != set(progress_data.get("badges_earned", [])):
        progress_data["badges_earned"] = sorted(earned_ids)
        save_progress_data(progress_data)

    return badges


def get_badges_dataframe() -> pd.DataFrame:
    """Return badges as dataframe with earned status."""
    badges = evaluate_badges()
    if not badges:
        return pd.DataFrame(columns=["badge_id", "title", "description", "earned"])
    return pd.DataFrame(badges)[["badge_id", "title", "description", "earned"]]


def get_earned_badge_count() -> int:
    return sum(1 for badge in evaluate_badges() if badge.get("earned"))
