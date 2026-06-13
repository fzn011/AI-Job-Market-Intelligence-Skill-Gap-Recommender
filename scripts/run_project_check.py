"""Run a full local health check for the AI Job Market Intelligence project.

Usage:
    python scripts/run_project_check.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


def _add_project_root_to_path() -> Path:
    """Ensure imports from src/ work when running this script directly."""
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root


PROJECT_ROOT = _add_project_root_to_path()

from src.config import load_config  # noqa: E402
from src.data_cleaning import REQUIRED_JOB_COLUMNS, clean_jobs, validate_job_columns  # noqa: E402
from src.skill_extraction import (  # noqa: E402
    compute_skill_frequency,
    extract_skills_from_dataframe,
    flatten_skill_dictionary,
    load_skill_dictionary,
)
from src.utils import ensure_directory, load_dataframe, save_dataframe  # noqa: E402


def main() -> int:
    """Execute project checks and generate processed outputs."""
    print("Project Health Check")
    print("--------------------")

    try:
        # 1) Load config
        config = load_config(PROJECT_ROOT / "config.yaml")

        # 2) Verify required directories and create missing
        required_dirs = [
            PROJECT_ROOT / "data" / "raw",
            PROJECT_ROOT / "data" / "processed",
            PROJECT_ROOT / "data" / "sample",
            PROJECT_ROOT / "reports" / "figures",
            PROJECT_ROOT / "reports" / "generated_reports",
        ]

        for folder in required_dirs:
            ensure_directory(folder)

        # 3) Load sample files
        sample_jobs_path = PROJECT_ROOT / "data" / "sample" / "sample_jobs.csv"
        skill_dict_path = PROJECT_ROOT / "data" / "sample" / "skills_dictionary.json"

        jobs_df = load_dataframe(sample_jobs_path)
        validate_job_columns(jobs_df, REQUIRED_JOB_COLUMNS)

        skill_dict = load_skill_dictionary(skill_dict_path)
        skill_list = flatten_skill_dictionary(skill_dict)

        # 4) Clean jobs and extract skills
        cleaned_df = clean_jobs(jobs_df)
        processed_df = extract_skills_from_dataframe(
            cleaned_df,
            text_column="cleaned_description",
            skills=skill_list,
        )

        # 5) Ensure required output columns
        for col in ["cleaned_description", "extracted_skills", "skill_count"]:
            if col not in processed_df.columns:
                raise ValueError(f"Expected column '{col}' was not created.")

        # 6) Save processed jobs
        processed_jobs_path = PROJECT_ROOT / "data" / "processed" / "processed_sample_jobs.csv"
        save_dataframe(processed_df, processed_jobs_path)

        # 7) Compute and save frequency table
        frequency_df = compute_skill_frequency(processed_df, skills_column="extracted_skills")
        freq_path = PROJECT_ROOT / "data" / "processed" / "sample_skill_frequency.csv"
        save_dataframe(frequency_df, freq_path)

        # 8) Summary output
        print("Config loaded: Yes")
        print(f"Sample jobs loaded: {len(jobs_df)} rows")
        print("Required columns present: Yes")
        print("Skills dictionary loaded: Yes")
        print(f"Processed jobs saved: {processed_jobs_path.relative_to(PROJECT_ROOT)}")
        print(f"Skill frequency saved: {freq_path.relative_to(PROJECT_ROOT)}")
        print("Top 10 skills:")

        top10 = frequency_df.head(10)
        if top10.empty:
            print("(No skills found in sample descriptions)")
        else:
            for idx, row in enumerate(top10.itertuples(index=False), start=1):
                print(f"{idx}. {row.skill} - {row.frequency}")

        print(
            "To process expanded demo or custom CSV data, run: "
            "python scripts/import_jobs_from_csv.py --demo expanded"
        )

        from src.brand_constants import APP_NAME, APP_VERSION  # noqa: WPS433
        from src.ui_theme import render_app_footer  # noqa: WPS433

        print(f"Brand constants loaded: {APP_NAME} ({APP_VERSION})")
        print(f"UI theme helpers loaded: render_app_footer={callable(render_app_footer)}")

        return 0

    except FileNotFoundError as exc:
        print(f"[ERROR] Missing file: {exc}")
        return 1
    except ValueError as exc:
        print(f"[ERROR] Validation failed: {exc}")
        return 1
    except Exception as exc:
        print(f"[ERROR] Unexpected failure: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
