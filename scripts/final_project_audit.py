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
        root / "app" / "pages" / "7_Career_Explorer.py",
        root / "app" / "pages" / "8_Job_Match_Dashboard.py",
        root / "app" / "pages" / "9_Career_Toolkit.py",
        root / "app" / "pages" / "10_Career_Intelligence_Hub.py",
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
        root / "src" / "career_taxonomy_utils.py",
        root / "src" / "skill_synonym_utils.py",
        root / "src" / "progress_tracker_utils.py",
        root / "src" / "job_match_utils.py",
        root / "src" / "timeseries_utils.py",
        root / "src" / "gamification_utils.py",
        root / "src" / "i18n_utils.py",
        root / "src" / "public_data_connectors.py",
        root / "src" / "secrets_utils.py",
        root / "src" / "semantic_skill_utils.py",
        root / "src" / "company_prep_utils.py",
        root / "src" / "salary_estimator_utils.py",
        root / "src" / "linkedin_optimizer_utils.py",
        root / "src" / "peer_benchmark_utils.py",
        root / "src" / "voice_interview_utils.py",
        root / "src" / "study_calendar_utils.py",
        root / "src" / "email_digest_utils.py",
        root / "src" / "quick_start_utils.py",
    ]

    career_taxonomy_assets = [
        root / "data" / "career_taxonomies",
        root / "data" / "career_taxonomies" / "role_profiles.json",
        root / "data" / "career_taxonomies" / "career_action_templates.json",
        root / "data" / "career_taxonomies" / "regional_profiles.json",
        root / "data" / "skill_synonyms.json",
        root / "data" / "learning_resources.json",
        root / "data" / "interview_questions.json",
        root / "data" / "gamification_badges.json",
        root / "data" / "i18n" / "en.json",
        root / "data" / "i18n" / "bn.json",
        root / "data" / "company_prep_packs.json",
        root / "data" / "salary_bands.json",
        root / "data" / "voice_interview_rubric.json",
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
        root / "scripts" / "generate_advanced_features_data.py",
        root / "scripts" / "generate_premium_features_data.py",
    ]

    sample_processed = root / "data" / "processed" / "processed_sample_jobs.csv"
    imported_processed = root / "data" / "processed" / "processed_imported_jobs.csv"
    import_guide = root / "docs" / "job_data_import_guide.md"
    readme = root / "README.md"
    requirements = root / "requirements.txt"
    deployment_config = root / ".streamlit" / "config.toml"

    packaging_docs = [
        root / "docs" / "recruiter_one_pager.md",
        root / "docs" / "demo" / "demo_recording_checklist.md",
        root / "docs" / "demo" / "linkedin_launch_post.md",
        root / "docs" / "demo" / "resume_bullets.md",
        root / "docs" / "demo" / "interview_talking_points.md",
        root / "docs" / "screenshots" / "screenshot_checklist.md",
    ]

    pages_found = sum(1 for p in pages if exists(p))
    modules_found = sum(1 for p in core_modules if exists(p))
    taxonomy_assets_found = sum(1 for p in career_taxonomy_assets if exists(p))
    folders_ok = all(exists(p) for p in required_folders)
    scripts_ok = all(exists(p) for p in required_scripts)
    packaging_found = sum(1 for p in packaging_docs if exists(p))

    print("Final Project Audit")
    print("-------------------")
    print(f"Streamlit pages found: {pages_found}/{len(pages)}")
    print(f"Core src modules found: {modules_found}/{len(core_modules)}")
    print(f"Advanced feature assets found: {taxonomy_assets_found}/{len(career_taxonomy_assets)}")
    print(f"Processed sample data: {'Yes' if exists(sample_processed) else 'No'}")
    print(f"Processed imported data: {'Yes' if exists(imported_processed) else 'No'}")
    print(f"Import guide: {'Yes' if exists(import_guide) else 'No'}")
    print(f"README: {'Yes' if exists(readme) else 'No'}")
    print(f"Deployment config: {'Yes' if exists(deployment_config) else 'No'}")
    print(f"Portfolio packaging docs: {packaging_found}/{len(packaging_docs)}")
    print(f"Requirements file: {'Yes' if exists(requirements) else 'No'}")
    print(f"Required folders ready: {'Yes' if folders_ok else 'No'}")
    print(f"Required scripts ready: {'Yes' if scripts_ok else 'No'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
