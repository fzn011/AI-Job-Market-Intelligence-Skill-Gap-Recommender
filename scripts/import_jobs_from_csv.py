"""Process demo or custom job CSV into dashboard-ready processed outputs.

Usage examples:
    python scripts/import_jobs_from_csv.py --demo expanded
    python scripts/import_jobs_from_csv.py --demo small
    python scripts/import_jobs_from_csv.py --input data/raw/my_jobs.csv
    python scripts/import_jobs_from_csv.py --input data/raw/my_jobs.csv --output-name my_jobs
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _add_project_root_to_path() -> Path:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root


PROJECT_ROOT = _add_project_root_to_path()

from src.data_collection import (  # noqa: E402
    export_import_summary,
    process_imported_jobs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import and process job CSV data.")
    parser.add_argument(
        "--demo",
        choices=["expanded", "small"],
        help="Use built-in demo dataset source.",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Path to custom input CSV file.",
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default="imported_jobs",
        help="Output name prefix, e.g. imported_jobs or my_jobs.",
    )
    return parser.parse_args()


def resolve_input_path(args: argparse.Namespace) -> Path:
    if args.input:
        return Path(args.input)

    demo_choice = args.demo or "expanded"
    if demo_choice == "small":
        return PROJECT_ROOT / "data" / "sample" / "sample_jobs.csv"

    return PROJECT_ROOT / "data" / "sample" / "expanded_sample_jobs.csv"


def main() -> int:
    args = parse_args()

    try:
        input_path = resolve_input_path(args)
        output_name = str(args.output_name).strip() or "imported_jobs"

        if output_name == "imported_jobs":
            processed_jobs_path = PROJECT_ROOT / "data" / "processed" / "processed_imported_jobs.csv"
            skill_frequency_path = PROJECT_ROOT / "data" / "processed" / "imported_skill_frequency.csv"
            summary_path = PROJECT_ROOT / "reports" / "generated_reports" / "import_summary.json"
        else:
            processed_jobs_path = PROJECT_ROOT / "data" / "processed" / f"processed_{output_name}.csv"
            skill_frequency_path = PROJECT_ROOT / "data" / "processed" / f"{output_name}_skill_frequency.csv"
            summary_path = PROJECT_ROOT / "reports" / "generated_reports" / f"{output_name}_import_summary.json"

        skill_dict_path = PROJECT_ROOT / "data" / "sample" / "skills_dictionary.json"

        summary = process_imported_jobs(
            input_csv_path=input_path,
            skill_dictionary_path=skill_dict_path,
            output_jobs_path=processed_jobs_path,
            output_skill_frequency_path=skill_frequency_path,
        )
        export_import_summary(summary, summary_path)

        print("Job Import Summary")
        print("------------------")
        print(f"Input path: {summary['input_path']}")
        print(f"Raw rows: {summary['raw_rows']}")
        print(f"Processed rows: {summary['processed_rows']}")
        print(f"Unique skills: {summary['unique_skills']}")
        print(f"Processed jobs output: {summary['processed_jobs_path']}")
        print(f"Skill frequency output: {summary['skill_frequency_path']}")
        print(f"Import summary output: {summary_path}")
        print("Top 10 skills:")

        top_skills = summary.get("top_skills", [])
        if not top_skills:
            print("(No extracted skills found)")
        else:
            for idx, row in enumerate(top_skills[:10], start=1):
                print(f"{idx}. {row.get('skill')} - {row.get('frequency')}")

        return 0

    except FileNotFoundError as exc:
        print(f"[ERROR] File not found: {exc}")
        return 1
    except ValueError as exc:
        print(f"[ERROR] Validation failed: {exc}")
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] Unexpected failure: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
