"""Verify CareerCompass is ready to run. Exit 0 on success, 1 on failure."""

from __future__ import annotations

import sys
from pathlib import Path


def _project_root() -> Path:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


def main() -> int:
    root = _project_root()
    errors: list[str] = []
    warnings: list[str] = []

    required_files = [
        root / "config.yaml",
        root / "src" / "ui_theme.py",
        root / "app" / "streamlit_app.py",
        root / "data" / "sample" / "sample_jobs.csv",
        root / "data" / "sample" / "skills_dictionary.json",
    ]
    for path in required_files:
        if not path.exists():
            errors.append(f"Missing file: {path.relative_to(root)}")

    ui_theme_path = root / "src" / "ui_theme.py"
    if ui_theme_path.exists():
        text = ui_theme_path.read_text(encoding="utf-8")
        if "render_app_footer" not in text and "brand_constants" not in text:
            errors.append(
                "src/ui_theme.py is outdated. Run: python scripts/emergency_repair.py"
            )

    try:
        from src.source_repair import ensure_careercompass_sources  # noqa: WPS433

        ensure_careercompass_sources(root)
    except RuntimeError as exc:
        errors.append(str(exc))

    try:
        from src.brand_constants import APP_NAME, APP_VERSION  # noqa: WPS433

        print(f"Brand constants OK: {APP_NAME} ({APP_VERSION})")
    except Exception as exc:
        errors.append(f"Cannot import src.brand_constants: {exc}")

    try:
        from src.ui_theme import (  # noqa: WPS433
            apply_global_theme,
            render_app_footer,
            render_brand_header,
            render_feature_card,
            render_path_card,
            render_sidebar_navigation,
        )

        print(
            "UI theme helpers OK: "
            f"render_feature_card={callable(render_feature_card)}, "
            f"render_sidebar_navigation={callable(render_sidebar_navigation)}"
        )
    except Exception as exc:
        errors.append(f"Cannot import src.ui_theme helpers: {exc}")

    try:
        from src.career_taxonomy_utils import list_career_categories  # noqa: WPS433

        categories = list_career_categories()
        if not categories:
            errors.append(
                "No career categories found. Run: python scripts/generate_career_taxonomies.py"
            )
        else:
            print(f"Career categories OK: {len(categories)}")
    except Exception as exc:
        errors.append(f"Career taxonomy check failed: {exc}")

    try:
        from src.company_prep_utils import list_companies  # noqa: WPS433

        companies = list_companies()
        if not companies:
            warnings.append(
                "Company prep packs empty. Run: python scripts/generate_premium_features_data.py"
            )
        else:
            print(f"Company prep packs OK: {len(companies)}")
    except Exception as exc:
        warnings.append(f"Company prep check skipped: {exc}")

    try:
        import docx  # noqa: F401
        import pypdf  # noqa: F401

        print("CV upload deps OK: pypdf, python-docx")
    except ImportError as exc:
        errors.append(
            "CV upload packages missing (pypdf, python-docx). "
            "Run: pip install pypdf python-docx  OR  .\\setup.ps1"
        )

    processed_jobs = root / "data" / "processed" / "processed_sample_jobs.csv"
    if not processed_jobs.exists():
        warnings.append(
            "Processed jobs not found. Run: python scripts/run_project_check.py"
        )
    else:
        print(f"Processed jobs OK: {processed_jobs.relative_to(root)}")

    for message in warnings:
        print(f"WARNING: {message}")

    if errors:
        print("\nCareerCompass startup verification FAILED:")
        for message in errors:
            print(f"  - {message}")
        print("\nFix on Windows:")
        print("  git fetch origin main")
        print("  git reset --hard origin/main")
        print("  .\\setup.ps1")
        return 1

    print("\nCareerCompass startup verification PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
