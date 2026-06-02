"""Reusable analytics helpers for the Skill Demand Analysis dashboard page."""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from pathlib import Path

import pandas as pd

from src.config import get_project_root
from src.dashboard_utils import parse_extracted_skills
from src.utils import load_json


def load_skill_dictionary_for_analysis(skill_dict_path: str | Path | None = None) -> dict:
    """Load skill dictionary from disk for category-aware analytics."""
    root = get_project_root()
    path = (
        Path(skill_dict_path)
        if skill_dict_path is not None
        else root / "data" / "sample" / "skills_dictionary.json"
    )

    if not path.exists():
        return {}

    try:
        data = load_json(path)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def build_skill_category_lookup(skill_dict: dict) -> dict:
    """Build a skill -> category lookup from the grouped skill dictionary."""
    lookup: dict[str, str] = {}
    if not isinstance(skill_dict, dict):
        return lookup

    for category, skills in skill_dict.items():
        if not isinstance(skills, list):
            continue
        for skill in skills:
            normalized = str(skill).strip().lower()
            if normalized and normalized not in lookup:
                lookup[normalized] = str(category)

    return lookup


def categorize_skill(skill: str, category_lookup: dict) -> str:
    """Return category for a skill or 'uncategorized' if not found."""
    if skill is None:
        return "uncategorized"

    normalized = str(skill).strip().lower()
    if not normalized:
        return "uncategorized"

    return category_lookup.get(normalized, "uncategorized")


def explode_skills_dataframe(
    df: pd.DataFrame,
    category_lookup: dict | None = None,
) -> pd.DataFrame:
    """
    Convert job-level dataframe into one row per job-skill pair.

    Output columns:
    job_id, job_title, company, location, job_type, date_posted, skill, skill_category
    """
    output_columns = [
        "job_id",
        "job_title",
        "company",
        "location",
        "job_type",
        "date_posted",
        "skill",
        "skill_category",
    ]

    if df.empty or "extracted_skills" not in df.columns:
        return pd.DataFrame(columns=output_columns)

    category_lookup = category_lookup or {}
    rows: list[dict] = []

    for _, row in df.iterrows():
        skills = parse_extracted_skills(row.get("extracted_skills"))
        if not skills:
            continue

        for skill in skills:
            normalized_skill = str(skill).strip().lower()
            if not normalized_skill:
                continue

            rows.append(
                {
                    "job_id": row.get("job_id"),
                    "job_title": row.get("job_title"),
                    "company": row.get("company"),
                    "location": row.get("location"),
                    "job_type": row.get("job_type"),
                    "date_posted": row.get("date_posted"),
                    "skill": normalized_skill,
                    "skill_category": categorize_skill(normalized_skill, category_lookup),
                }
            )

    if not rows:
        return pd.DataFrame(columns=output_columns)

    return pd.DataFrame(rows, columns=output_columns)


def get_top_skills(skill_df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Return top skill frequency table."""
    if skill_df.empty or "skill" not in skill_df.columns:
        return pd.DataFrame(columns=["skill", "frequency"])

    top = skill_df["skill"].value_counts().head(top_n).reset_index()
    top.columns = ["skill", "frequency"]
    return top


def get_skill_category_distribution(skill_df: pd.DataFrame) -> pd.DataFrame:
    """Return skill-category frequency table."""
    if skill_df.empty or "skill_category" not in skill_df.columns:
        return pd.DataFrame(columns=["skill_category", "frequency"])

    dist = skill_df["skill_category"].value_counts().reset_index()
    dist.columns = ["skill_category", "frequency"]
    return dist


def get_skills_by_group(
    skill_df: pd.DataFrame,
    group_column: str,
    top_n_skills: int = 15,
) -> pd.DataFrame:
    """Create group-by-skill pivot matrix using top overall skills."""
    if skill_df.empty or group_column not in skill_df.columns or "skill" not in skill_df.columns:
        return pd.DataFrame()

    top_skills = (
        skill_df["skill"].value_counts().head(top_n_skills).index.tolist()
    )
    if not top_skills:
        return pd.DataFrame()

    scoped = skill_df[skill_df["skill"].isin(top_skills)].copy()
    if scoped.empty:
        return pd.DataFrame()

    pivot = (
        scoped.groupby([group_column, "skill"]).size().unstack(fill_value=0)
        .sort_index()
    )

    return pivot


def get_skill_cooccurrence(
    df: pd.DataFrame,
    top_n_skills: int = 12,
) -> pd.DataFrame:
    """Build skill co-occurrence matrix from job-level extracted skills."""
    if df.empty or "extracted_skills" not in df.columns:
        return pd.DataFrame()

    all_skills: list[str] = []
    skills_per_job: list[list[str]] = []
    for value in df["extracted_skills"]:
        skills = sorted(set(parse_extracted_skills(value)))
        if skills:
            skills_per_job.append(skills)
            all_skills.extend(skills)

    if not all_skills:
        return pd.DataFrame()

    top_skills = [skill for skill, _ in Counter(all_skills).most_common(top_n_skills)]
    if not top_skills:
        return pd.DataFrame()

    matrix = pd.DataFrame(0, index=top_skills, columns=top_skills, dtype=int)

    for skills in skills_per_job:
        scoped = sorted(set(skill for skill in skills if skill in top_skills))
        if not scoped:
            continue

        for skill in scoped:
            matrix.loc[skill, skill] += 1

        for skill_a, skill_b in combinations(scoped, 2):
            matrix.loc[skill_a, skill_b] += 1
            matrix.loc[skill_b, skill_a] += 1

    return matrix


def get_top_skill_combinations(
    df: pd.DataFrame,
    combination_size: int = 2,
    top_n: int = 10,
) -> pd.DataFrame:
    """Return most common skill pairs/triples across job posts."""
    if df.empty or "extracted_skills" not in df.columns:
        return pd.DataFrame(columns=["skill_combination", "frequency"])

    combo_counter: Counter = Counter()
    for value in df["extracted_skills"]:
        skills = sorted(set(parse_extracted_skills(value)))
        if len(skills) < combination_size:
            continue

        for combo in combinations(skills, combination_size):
            combo_counter[combo] += 1

    if not combo_counter:
        return pd.DataFrame(columns=["skill_combination", "frequency"])

    records = [
        {
            "skill_combination": " + ".join(combo),
            "frequency": frequency,
        }
        for combo, frequency in combo_counter.most_common(top_n)
    ]

    return pd.DataFrame(records)


def get_technical_vs_soft_split(skill_df: pd.DataFrame) -> pd.DataFrame:
    """Classify skill mentions into Technical / Soft / Uncategorized buckets."""
    if skill_df.empty or "skill_category" not in skill_df.columns:
        return pd.DataFrame(columns=["skill_type", "frequency"])

    def classify(category: str) -> str:
        if category == "soft_skills":
            return "Soft Skills"
        if category == "uncategorized":
            return "Uncategorized"
        return "Technical Skills"

    split_df = skill_df.copy()
    split_df["skill_type"] = split_df["skill_category"].astype(str).apply(classify)
    grouped = split_df["skill_type"].value_counts().reset_index()
    grouped.columns = ["skill_type", "frequency"]
    return grouped


def get_skill_analysis_metrics(skill_df: pd.DataFrame, jobs_df: pd.DataFrame) -> dict:
    """Compute summary metrics for the skill analysis page."""
    if skill_df.empty:
        return {
            "total_skill_mentions": 0,
            "unique_skills": 0,
            "avg_skills_per_job": 0.0,
            "top_skill": "N/A",
            "top_skill_frequency": 0,
            "top_category": "N/A",
            "top_category_frequency": 0,
        }

    total_mentions = int(len(skill_df))
    unique_skills = int(skill_df["skill"].nunique()) if "skill" in skill_df.columns else 0

    if not jobs_df.empty and "skill_count" in jobs_df.columns:
        avg_skills = float(pd.to_numeric(jobs_df["skill_count"], errors="coerce").fillna(0).mean())
    else:
        job_count = int(jobs_df["job_id"].nunique()) if (not jobs_df.empty and "job_id" in jobs_df.columns) else max(1, int(total_mentions > 0))
        avg_skills = float(total_mentions / job_count) if job_count else 0.0

    top_skill = "N/A"
    top_skill_frequency = 0
    if "skill" in skill_df.columns and not skill_df["skill"].empty:
        skill_counts = skill_df["skill"].value_counts()
        top_skill = str(skill_counts.index[0])
        top_skill_frequency = int(skill_counts.iloc[0])

    top_category = "N/A"
    top_category_frequency = 0
    if "skill_category" in skill_df.columns and not skill_df["skill_category"].empty:
        category_counts = skill_df["skill_category"].value_counts()
        top_category = str(category_counts.index[0])
        top_category_frequency = int(category_counts.iloc[0])

    return {
        "total_skill_mentions": total_mentions,
        "unique_skills": unique_skills,
        "avg_skills_per_job": round(avg_skills, 2),
        "top_skill": top_skill,
        "top_skill_frequency": top_skill_frequency,
        "top_category": top_category,
        "top_category_frequency": top_category_frequency,
    }


def generate_skill_insights(
    skill_df: pd.DataFrame,
    jobs_df: pd.DataFrame,
    category_df: pd.DataFrame | None = None,
) -> list[str]:
    """Generate simple rule-based insights for the Skill Demand Analysis page."""
    if skill_df.empty:
        return [
            "No skill-level data is available for the selected filters yet.",
        ]

    insights: list[str] = []
    metrics = get_skill_analysis_metrics(skill_df, jobs_df)

    if metrics["top_skill"] != "N/A":
        insights.append(
            f"{metrics['top_skill'].title()} is the most frequently mentioned skill, appearing {metrics['top_skill_frequency']} times."
        )

    insights.append(
        f"The current filtered dataset has {metrics['unique_skills']} unique skills across {metrics['total_skill_mentions']} total skill mentions."
    )
    insights.append(
        f"The average job post mentions {metrics['avg_skills_per_job']} extracted skills."
    )

    split_df = get_technical_vs_soft_split(skill_df)
    if not split_df.empty:
        split_map = dict(zip(split_df["skill_type"], split_df["frequency"]))
        technical = int(split_map.get("Technical Skills", 0))
        soft = int(split_map.get("Soft Skills", 0))
        if technical > soft:
            insights.append("Technical skills dominate the current sample compared to soft skills.")
        elif soft > technical:
            insights.append("Soft skills appear more frequently than technical skills in the current sample.")

    if category_df is not None and not category_df.empty:
        top_cat = category_df.iloc[0]
        insights.append(
            f"Top skill category is '{top_cat['skill_category']}' with {int(top_cat['frequency'])} mentions."
        )

    return insights
