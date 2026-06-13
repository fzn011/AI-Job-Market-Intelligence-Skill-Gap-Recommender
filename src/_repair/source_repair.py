"""Repair outdated or corrupted CareerCompass source files on disk."""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

_REPAIR_ROOT = Path(__file__).resolve().parent

UI_THEME_EXPORTS: tuple[str, ...] = (
    "apply_global_theme",
    "render_brand_header",
    "render_feature_card",
    "render_info_box",
    "render_path_card",
    "render_sidebar_navigation",
    "render_status_badge",
    "render_app_footer",
    "style_plotly_figure",
)

FILE_CHECKS: dict[str, tuple[str, ...]] = {
    "src/ui_theme.py": UI_THEME_EXPORTS,
    "src/brand_constants.py": ("APP_NAME", "CareerCompass"),
    "app/streamlit_app.py": ("CareerCompass", "Quick Start Wizard", "render_feature_card"),
}

GIT_REPAIR_PATHS = [
    "src/ui_theme.py",
    "src/_repair/ui_theme.py",
    "src/brand_constants.py",
    "src/source_repair.py",
    "src/__init__.py",
    "app/streamlit_app.py",
]

MIN_UI_THEME_BYTES = 12000
_repair_running = False


def project_root(explicit: Path | None = None) -> Path:
    return explicit or _REPAIR_ROOT.parent


def clear_python_cache(root: Path) -> None:
    for cache_dir in root.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)
    for module_name in list(sys.modules):
        if module_name == "src" or module_name.startswith("src."):
            del sys.modules[module_name]


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def file_has_markers(root: Path, relative_path: str) -> bool:
    markers = FILE_CHECKS.get(relative_path)
    if not markers:
        return True
    text = _read_text(root / relative_path)
    return bool(text) and all(marker in text for marker in markers)


def ui_theme_file_large_enough(root: Path) -> bool:
    target = root / "src" / "ui_theme.py"
    return target.exists() and target.stat().st_size >= MIN_UI_THEME_BYTES


def ui_theme_imports_work(root: Path) -> bool:
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    clear_python_cache(root)
    try:
        module = importlib.import_module("src.ui_theme")
    except Exception:
        return False
    return all(hasattr(module, name) for name in UI_THEME_EXPORTS)


def ui_theme_is_valid(root: Path) -> bool:
    return (
        file_has_markers(root, "src/ui_theme.py")
        and ui_theme_file_large_enough(root)
        and ui_theme_imports_work(root)
    )


def repair_with_git(root: Path) -> bool:
    git_dir = root / ".git"
    if not git_dir.exists():
        return False
    try:
        subprocess.run(["git", "fetch", "origin", "main"], cwd=root, capture_output=True, text=True, check=False)
        result = subprocess.run(
            ["git", "checkout", "origin/main", "--", *GIT_REPAIR_PATHS],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def repair_ui_theme_from_backup(root: Path) -> bool:
    target = root / "src" / "ui_theme.py"
    backup = root / "src" / "_repair" / "ui_theme.py"
    if not backup.exists():
        return False
    shutil.copy2(backup, target)
    return True


def ensure_careercompass_sources(root: Path | None = None) -> None:
    global _repair_running
    if _repair_running:
        return
    root = project_root(root)
    if ui_theme_is_valid(root) and file_has_markers(root, "src/brand_constants.py"):
        return
    _repair_running = True
    try:
        clear_python_cache(root)
        repair_with_git(root)
        clear_python_cache(root)
        if not ui_theme_is_valid(root):
            repair_ui_theme_from_backup(root)
            clear_python_cache(root)
        if not ui_theme_is_valid(root):
            raise RuntimeError(
                "CareerCompass source repair failed for src/ui_theme.py "
                "(missing render_feature_card). Run: python scripts/emergency_repair.py"
            )
    finally:
        _repair_running = False


def repair_report(root: Path | None = None) -> list[str]:
    root = project_root(root)
    lines: list[str] = []
    ui_path = root / "src" / "ui_theme.py"
    if ui_path.exists():
        lines.append(f"ui_theme.py size: {ui_path.stat().st_size} bytes (minimum {MIN_UI_THEME_BYTES})")
    else:
        lines.append("ui_theme.py size: MISSING")
    for rel_path in FILE_CHECKS:
        lines.append(f"{'OK' if file_has_markers(root, rel_path) else 'OUTDATED'}: {rel_path}")
    lines.append(f"ui_theme import check: {'OK' if ui_theme_imports_work(root) else 'FAILED'}")
    return lines
