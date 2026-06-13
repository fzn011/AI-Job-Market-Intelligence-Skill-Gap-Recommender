"""Time-series skill demand analytics."""

from __future__ import annotations

import pandas as pd

from src.dashboard_utils import parse_extracted_skills


def _parse_date_series(jobs_df: pd.DataFrame) -> pd.Series:
    if "date_posted" not in jobs_df.columns:
        return pd.Series(dtype="datetime64[ns]")
    return pd.to_datetime(jobs_df["date_posted"], errors="coerce")


def build_skill_timeseries(
    jobs_df: pd.DataFrame,
    top_n_skills: int = 8,
    freq: str = "M",
) -> pd.DataFrame:
    """
    Build skill demand over time from date_posted and extracted_skills.

    Returns long-format dataframe: period, skill, job_count
    """
    if jobs_df.empty or "extracted_skills" not in jobs_df.columns:
        return pd.DataFrame(columns=["period", "skill", "job_count"])

    dates = _parse_date_series(jobs_df)
    working = jobs_df.copy()
    working["parsed_date"] = dates
    working = working.dropna(subset=["parsed_date"])
    if working.empty:
        return pd.DataFrame(columns=["period", "skill", "job_count"])

    skill_counts: dict[str, int] = {}
    for value in working["extracted_skills"]:
        for skill in parse_extracted_skills(value):
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

    top_skills = [
        skill for skill, _ in sorted(skill_counts.items(), key=lambda row: (-row[1], row[0]))[:top_n_skills]
    ]
    if not top_skills:
        return pd.DataFrame(columns=["period", "skill", "job_count"])

    rows = []
    working["period"] = working["parsed_date"].dt.to_period(freq).astype(str)
    for period, group in working.groupby("period"):
        period_skill_counts = {skill: 0 for skill in top_skills}
        for value in group["extracted_skills"]:
            skills = set(parse_extracted_skills(value))
            for skill in top_skills:
                if skill in skills:
                    period_skill_counts[skill] += 1
        for skill, count in period_skill_counts.items():
            rows.append({"period": period, "skill": skill, "job_count": count})

    return pd.DataFrame(rows)


def get_timeseries_summary(jobs_df: pd.DataFrame) -> dict:
    """Return summary stats for time-series availability."""
    dates = _parse_date_series(jobs_df)
    valid_dates = dates.dropna()
    if valid_dates.empty:
        return {"available": False, "message": "No valid date_posted values found."}
    return {
        "available": True,
        "min_date": str(valid_dates.min().date()),
        "max_date": str(valid_dates.max().date()),
        "date_count": int(valid_dates.count()),
    }
