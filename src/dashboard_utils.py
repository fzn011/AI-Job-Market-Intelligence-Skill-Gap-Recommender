"""Reusable helper functions for Streamlit dashboard pages."""

from __future__ import annotations

from ast import literal_eval
from pathlib import Path

import pandas as pd

from src.config import get_project_root


def load_processed_jobs(processed_path: str | Path | None = None) -> pd.DataFrame:
    """Load processed jobs data, returning an empty DataFrame if missing."""
    root = get_project_root()
    path = Path(processed_path) if processed_path is not None else root / "data" / "processed" / "processed_sample_jobs.csv"

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def load_skill_frequency(freq_path: str | Path | None = None) -> pd.DataFrame:
    """Load skill frequency data, returning an empty DataFrame if missing."""
    root = get_project_root()
    path = Path(freq_path) if freq_path is not None else root / "data" / "processed" / "sample_skill_frequency.csv"

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def parse_extracted_skills(value) -> list[str]:
    """Parse extracted skills from list/string/empty values into a clean list."""
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []

        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                parsed = literal_eval(stripped)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except (ValueError, SyntaxError):
                pass

        return [part.strip().strip("'\"") for part in stripped.split(",") if part.strip()]

    return []


def add_total_extracted_skills_metric(df: pd.DataFrame) -> int:
    """Return total extracted skills across all rows."""
    if df.empty or "extracted_skills" not in df.columns:
        return 0

    return int(df["extracted_skills"].apply(parse_extracted_skills).apply(len).sum())


def get_basic_job_metrics(df: pd.DataFrame) -> dict:
    """Compute baseline dashboard metrics from jobs DataFrame."""
    if df.empty:
        return {
            "total_jobs": 0,
            "unique_job_titles": 0,
            "unique_companies": 0,
            "unique_locations": 0,
            "unique_job_types": 0,
            "avg_skills_per_job": 0,
        }

    def unique_count(column: str) -> int:
        if column not in df.columns:
            return 0
        return int(df[column].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique())

    avg_skills = 0.0
    if "skill_count" in df.columns:
        numeric = pd.to_numeric(df["skill_count"], errors="coerce")
        avg_skills = float(numeric.fillna(0).mean()) if len(numeric) else 0.0

    return {
        "total_jobs": int(len(df)),
        "unique_job_titles": unique_count("job_title"),
        "unique_companies": unique_count("company"),
        "unique_locations": unique_count("location"),
        "unique_job_types": unique_count("job_type"),
        "avg_skills_per_job": round(avg_skills, 2),
    }


def get_top_values(df: pd.DataFrame, column: str, top_n: int = 10) -> pd.DataFrame:
    """Return top values/counts for a column."""
    if df.empty or column not in df.columns:
        return pd.DataFrame(columns=["value", "count"])

    counts = (
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .head(top_n)
        .reset_index()
    )
    counts.columns = ["value", "count"]
    return counts


def prepare_jobs_preview(df: pd.DataFrame, max_rows: int = 20) -> pd.DataFrame:
    """Prepare clean preview table for dashboard display."""
    if df.empty:
        return pd.DataFrame()

    preferred_columns = [
        "job_id",
        "job_title",
        "company",
        "location",
        "job_type",
        "date_posted",
        "skill_count",
        "extracted_skills",
    ]
    available_columns = [col for col in preferred_columns if col in df.columns]

    preview_df = df[available_columns].copy() if available_columns else df.copy()
    return preview_df.head(max_rows)
