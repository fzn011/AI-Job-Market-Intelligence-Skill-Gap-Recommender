"""Job data ingestion helpers for safe, free, local CSV-based workflows."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import get_project_root
from src.data_cleaning import clean_jobs
from src.skill_extraction import (
    compute_skill_frequency,
    extract_skills_from_dataframe,
    flatten_skill_dictionary,
    load_skill_dictionary,
)
from src.utils import ensure_directory, save_dataframe, save_json


REQUIRED_JOB_COLUMNS = [
    "job_id",
    "job_title",
    "company",
    "location",
    "job_type",
    "description",
    "date_posted",
    "source",
]

OPTIONAL_JOB_COLUMNS = [
    "salary_min",
    "salary_max",
    "currency",
    "experience_level",
    "remote_type",
    "employment_type",
    "industry",
    "country",
    "application_url",
]

STANDARD_JOB_COLUMNS = REQUIRED_JOB_COLUMNS + OPTIONAL_JOB_COLUMNS


def _standardize_column_names(columns: list) -> list[str]:
    """Normalize dataframe column names to snake_case lowercase format."""
    normalized: list[str] = []
    for col in columns:
        text = str(col).strip().lower().replace(" ", "_")
        normalized.append(text)
    return normalized


def get_standard_job_columns() -> list[str]:
    """Return the standard schema columns used by the project."""
    return STANDARD_JOB_COLUMNS.copy()


def create_job_template_csv(output_path: str | Path) -> Path:
    """Create a blank job CSV template containing only standard headers."""
    path = Path(output_path)
    ensure_directory(path.parent)
    pd.DataFrame(columns=get_standard_job_columns()).to_csv(path, index=False, encoding="utf-8")
    return path


def load_job_csv(path: str | Path) -> pd.DataFrame:
    """Load a job CSV file and standardize the column names."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Job CSV file not found: {file_path}. "
            "Provide a valid path or use the demo dataset import option."
        )

    df = pd.read_csv(file_path, encoding="utf-8")
    df.columns = _standardize_column_names(df.columns.tolist())
    return df


def validate_job_schema(df: pd.DataFrame) -> dict:
    """Validate required schema columns and key quality checks for job data."""
    available_columns = [str(col) for col in df.columns.tolist()]
    missing_required = [col for col in REQUIRED_JOB_COLUMNS if col not in df.columns]
    row_count = int(len(df))

    duplicate_job_ids = 0
    if "job_id" in df.columns and not df.empty:
        job_id_series = df["job_id"].astype("string").fillna("").str.strip()
        duplicate_job_ids = int(job_id_series.duplicated().sum())

    def _missing_count(column: str) -> int:
        if column not in df.columns:
            return 0
        series = df[column].astype("string")
        return int(series.isna().sum() + series.fillna("").str.strip().eq("").sum())

    missing_descriptions = _missing_count("description")
    missing_job_titles = _missing_count("job_title")
    missing_companies = _missing_count("company")

    warnings: list[str] = []
    missing_optional = [col for col in OPTIONAL_JOB_COLUMNS if col not in df.columns]
    if missing_optional:
        warnings.append("Missing optional columns: " + ", ".join(missing_optional))
    if duplicate_job_ids > 0:
        warnings.append(f"Duplicate job_id values detected: {duplicate_job_ids}")
    if missing_descriptions > 0:
        warnings.append(f"Rows with missing descriptions: {missing_descriptions}")
    if row_count == 0:
        warnings.append("The input dataframe is empty.")

    return {
        "is_valid": len(missing_required) == 0,
        "missing_required_columns": missing_required,
        "available_columns": available_columns,
        "row_count": row_count,
        "duplicate_job_ids": duplicate_job_ids,
        "missing_descriptions": missing_descriptions,
        "missing_job_titles": missing_job_titles,
        "missing_companies": missing_companies,
        "warnings": warnings,
    }


def standardize_job_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize imported data to project schema and ordering."""
    standardized = df.copy()
    standardized.columns = _standardize_column_names(standardized.columns.tolist())

    for col in get_standard_job_columns():
        if col not in standardized.columns:
            standardized[col] = ""

    key_text_cols = [
        "job_title",
        "company",
        "location",
        "job_type",
        "description",
        "date_posted",
        "source",
    ]
    for col in key_text_cols:
        standardized[col] = standardized[col].astype("string").fillna("").str.strip()

    standardized["job_id"] = standardized["job_id"].astype("string").fillna("").str.strip()

    source_series = standardized["source"].astype("string").fillna("").str.strip()
    standardized["source"] = source_series.mask(source_series.eq(""), "manual_csv")

    standard_cols = get_standard_job_columns()
    extra_cols = [col for col in standardized.columns if col not in standard_cols]
    return standardized[standard_cols + extra_cols]


def deduplicate_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicated jobs by job_id and then exact duplicate rows."""
    deduped = df.copy()
    if deduped.empty:
        return deduped.reset_index(drop=True)

    if "job_id" in deduped.columns:
        normalized_ids = deduped["job_id"].astype("string").fillna("").str.strip()
        non_empty_mask = normalized_ids.ne("")
        with_ids = deduped.loc[non_empty_mask].copy()
        without_ids = deduped.loc[~non_empty_mask].copy()
        with_ids = with_ids.loc[~normalized_ids.loc[non_empty_mask].duplicated()].copy()
        deduped = pd.concat([with_ids, without_ids], ignore_index=True)

    deduped = deduped.drop_duplicates().reset_index(drop=True)
    return deduped


def merge_job_sources(dataframes: list[pd.DataFrame]) -> pd.DataFrame:
    """Merge multiple job dataframes into one standardized, deduplicated set."""
    standardized_frames: list[pd.DataFrame] = []
    for df in dataframes:
        if df is None or df.empty:
            continue
        standardized_frames.append(standardize_job_dataframe(df))

    if not standardized_frames:
        return pd.DataFrame(columns=get_standard_job_columns())

    merged = pd.concat(standardized_frames, ignore_index=True, sort=False)
    merged = deduplicate_jobs(merged)
    return standardize_job_dataframe(merged)


def process_imported_jobs(
    input_csv_path: str | Path,
    skill_dictionary_path: str | Path,
    output_jobs_path: str | Path,
    output_skill_frequency_path: str | Path,
) -> dict:
    """Run full import-processing pipeline for an input job CSV."""
    input_path = Path(input_csv_path)
    output_jobs = Path(output_jobs_path)
    output_freq = Path(output_skill_frequency_path)

    raw_df = load_job_csv(input_path)
    validation = validate_job_schema(raw_df)

    if not validation["is_valid"]:
        missing = validation["missing_required_columns"]
        raise ValueError("Invalid job CSV schema. Missing required columns: " + ", ".join(missing))

    standardized_df = standardize_job_dataframe(raw_df)
    deduplicated_df = deduplicate_jobs(standardized_df)
    cleaned_df = clean_jobs(deduplicated_df)

    skill_dict = load_skill_dictionary(skill_dictionary_path)
    skill_list = flatten_skill_dictionary(skill_dict)

    processed_df = extract_skills_from_dataframe(
        cleaned_df,
        text_column="cleaned_description",
        skills=skill_list,
    )
    skill_frequency_df = compute_skill_frequency(processed_df, skills_column="extracted_skills")

    ensure_directory(output_jobs.parent)
    ensure_directory(output_freq.parent)
    save_dataframe(processed_df, output_jobs)
    save_dataframe(skill_frequency_df, output_freq)

    top_skills = skill_frequency_df.head(10).to_dict(orient="records") if not skill_frequency_df.empty else []

    return {
        "input_path": str(input_path),
        "processed_jobs_path": str(output_jobs),
        "skill_frequency_path": str(output_freq),
        "raw_rows": int(len(raw_df)),
        "processed_rows": int(len(processed_df)),
        "unique_skills": int(skill_frequency_df["skill"].nunique()) if "skill" in skill_frequency_df.columns else 0,
        "top_skills": top_skills,
        "validation": validation,
    }


def load_demo_dataset(expanded: bool = True) -> pd.DataFrame:
    """Load the built-in demo dataset (expanded or small sample)."""
    root = get_project_root()
    if expanded:
        path = root / "data" / "sample" / "expanded_sample_jobs.csv"
    else:
        path = root / "data" / "sample" / "sample_jobs.csv"

    return load_job_csv(path)


def export_import_summary(summary: dict, output_path: str | Path) -> Path:
    """Export import summary payload to JSON file."""
    output = Path(output_path)
    save_json(summary, output)
    return output
