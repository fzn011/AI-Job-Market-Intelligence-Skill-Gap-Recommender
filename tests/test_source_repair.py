"""Tests for automatic source repair."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_brand_constants_import() -> None:
    from src.brand_constants import APP_NAME, APP_VERSION

    assert APP_NAME == "CareerCompass"
    assert APP_VERSION.startswith("v")


def test_ui_theme_helpers_import() -> None:
    from src.ui_theme import (
        render_app_footer,
        render_brand_header,
        render_feature_card,
        render_sidebar_navigation,
    )

    assert callable(render_app_footer)
    assert callable(render_brand_header)
    assert callable(render_feature_card)
    assert callable(render_sidebar_navigation)


def test_partial_ui_theme_is_detected(tmp_path: Path) -> None:
    from src.source_repair import repair_ui_theme_from_backup, ui_theme_is_valid

    backup_src = PROJECT_ROOT / "src" / "_repair" / "ui_theme.py"
    target_dir = tmp_path / "src" / "_repair"
    target_dir.mkdir(parents=True)
    shutil.copy2(backup_src, target_dir / "ui_theme.py")
    shutil.copy2(PROJECT_ROOT / "src" / "brand_constants.py", tmp_path / "src" / "brand_constants.py")

    partial = tmp_path / "src" / "ui_theme.py"
    partial.write_text(
        "\n".join(
            [
                "from src.brand_constants import APP_NAME",
                "def render_app_footer(): pass",
                "def render_brand_header(): pass",
            ]
        ),
        encoding="utf-8",
    )
    assert not ui_theme_is_valid(tmp_path)

    assert repair_ui_theme_from_backup(tmp_path)
    assert ui_theme_is_valid(tmp_path)


def test_backup_repair_restores_ui_theme(tmp_path: Path) -> None:
    from src.source_repair import repair_ui_theme_from_backup, ui_theme_is_valid

    backup_src = PROJECT_ROOT / "src" / "_repair" / "ui_theme.py"
    assert backup_src.exists()

    target_dir = tmp_path / "src" / "_repair"
    target_dir.mkdir(parents=True)
    shutil.copy2(backup_src, target_dir / "ui_theme.py")
    shutil.copy2(PROJECT_ROOT / "src" / "brand_constants.py", tmp_path / "src" / "brand_constants.py")

    stale_ui = tmp_path / "src" / "ui_theme.py"
    stale_ui.write_text("ACCENT = '#FF4433'\n", encoding="utf-8")
    assert not ui_theme_is_valid(tmp_path)

    assert repair_ui_theme_from_backup(tmp_path)
    assert ui_theme_is_valid(tmp_path)

def test_ensure_sources_on_current_repo() -> None:
    from src.source_repair import ensure_careercompass_sources, ui_theme_is_valid

    ensure_careercompass_sources(PROJECT_ROOT)
    assert ui_theme_is_valid(PROJECT_ROOT)


    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "emergency_repair.py")],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Repair complete" in result.stdout
