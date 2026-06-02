"""Run a lightweight final project audit for deployment readiness."""

from __future__ import annotations

from pathlib import Path


def exists(path: Path) -> bool:
    return path.exists()


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    pages = [
        root / "app" / "pages" / "1_Job_Market_Overview.py",
        root / "app" / "pages" / "2_Skill_Analysis.py",
        root / "app" / "pages" / "3_CV_Skill_Gap.py",
        root / "app" / "pages" / "4_Project_Recommendations.py",
        root / "app" / "pages" / "5_Role_Clustering.py",
        root / "app" / "pages" / "6_Data_Import.py",
    ]

    core_modules = [
        root / "src" / "data_collection.py",
        root / "src" / "data_cleaning.py",
        root / "src" / "skill_extraction.py",
        root / "src" / "dashboard_utils.py",
        root / "src" / "cv_gap_utils.py",
        root / "src" / "project_recommendation_utils.py",
        root / "src" / "job_clustering.py",
        root / "src" / "ui_theme.py",
    ]

    required_folders = [
        root / "app",
        root / "src",
        root / "data",
        root / "docs",
        root / "tests",
        root / "scripts",
    ]

    required_scripts = [
        root / "scripts" / "run_project_check.py",
        root / "scripts" / "import_jobs_from_csv.py",
        root / "scripts" / "final_project_audit.py",
    ]

    sample_processed = root / "data" / "processed" / "processed_sample_jobs.csv"
    imported_processed = root / "data" / "processed" / "processed_imported_jobs.csv"
    import_guide = root / "docs" / "job_data_import_guide.md"
    readme = root / "README.md"
    requirements = root / "requirements.txt"
    deployment_config = root / ".streamlit" / "config.toml"

    pages_found = sum(1 for p in pages if exists(p))
    modules_found = sum(1 for p in core_modules if exists(p))
    folders_ok = all(exists(p) for p in required_folders)
    scripts_ok = all(exists(p) for p in required_scripts)

    print("Final Project Audit")
    print("-------------------")
    print(f"Streamlit pages found: {pages_found}/{len(pages)}")
    print(f"Core src modules found: {modules_found}/{len(core_modules)}")
    print(f"Processed sample data: {'Yes' if exists(sample_processed) else 'No'}")
    print(f"Processed imported data: {'Yes' if exists(imported_processed) else 'No'}")
    print(f"Import guide: {'Yes' if exists(import_guide) else 'No'}")
    print(f"README: {'Yes' if exists(readme) else 'No'}")
    print(f"Deployment config: {'Yes' if exists(deployment_config) else 'No'}")
    print(f"Requirements file: {'Yes' if exists(requirements) else 'No'}")
    print(f"Required folders ready: {'Yes' if folders_ok else 'No'}")
    print(f"Required scripts ready: {'Yes' if scripts_ok else 'No'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
