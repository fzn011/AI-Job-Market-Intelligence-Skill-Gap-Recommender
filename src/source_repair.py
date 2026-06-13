"""Repair outdated or corrupted CareerCompass source files on disk."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

_REPAIR_ROOT = Path(__file__).resolve().parent

FILE_CHECKS: dict[str, tuple[str, ...]] = {
    "src/ui_theme.py": ("render_app_footer", "render_brand_header", "brand_constants"),
    "src/brand_constants.py": ("APP_NAME", "CareerCompass"),
    "app/streamlit_app.py": ("CareerCompass", "Quick Start Wizard"),
}

GIT_REPAIR_PATHS = [
    "src/ui_theme.py",
    "src/brand_constants.py",
    "src/source_repair.py",
    "src/__init__.py",
    "app/streamlit_app.py",
]


def project_root(explicit: Path | None = None) -> Path:
    return explicit or _REPAIR_ROOT.parent


def clear_python_cache(root: Path) -> None:
    for cache_dir in root.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)

    for module_name in list(sys.modules):
        if module_name in {"src.ui_theme", "src.brand_constants"} or module_name.startswith(
            ("src.ui_theme.", "src.brand_constants.")
        ):
            del sys.modules[module_name]


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def file_is_valid(root: Path, relative_path: str) -> bool:
    markers = FILE_CHECKS.get(relative_path)
    if not markers:
        return True
    text = _read_text(root / relative_path)
    return bool(text) and all(marker in text for marker in markers)


def repair_with_git(root: Path) -> bool:
    git_dir = root / ".git"
    if not git_dir.exists():
        return False

    try:
        subprocess.run(
            ["git", "fetch", "origin", "main"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
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
    """Ensure critical CareerCompass files exist and are up to date."""
    root = project_root(root)
    clear_python_cache(root)

    needs_repair = any(not file_is_valid(root, rel_path) for rel_path in FILE_CHECKS)
    if not needs_repair:
        return

    repair_with_git(root)
    clear_python_cache(root)

    if not file_is_valid(root, "src/ui_theme.py"):
        repair_ui_theme_from_backup(root)
        clear_python_cache(root)

    if not file_is_valid(root, "src/ui_theme.py"):
        raise RuntimeError(
            "CareerCompass source repair failed for src/ui_theme.py. "
            "Run: python scripts/emergency_repair.py"
        )


def repair_report(root: Path | None = None) -> list[str]:
    """Return human-readable repair status lines."""
    root = project_root(root)
    lines: list[str] = []
    for rel_path, markers in FILE_CHECKS.items():
        ok = file_is_valid(root, rel_path)
        status = "OK" if ok else "OUTDATED"
        lines.append(f"{status}: {rel_path} (needs {', '.join(markers)})")
    return lines
