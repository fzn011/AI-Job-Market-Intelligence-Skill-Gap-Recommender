"""Emergency repair for broken Windows checkouts. Safe to run anytime.

This script does NOT import src.source_repair first, so it works even when
that module is outdated on disk.
"""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

MIN_UI_THEME_BYTES = 12000
UI_THEME_EXPORTS = (
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


def _project_root() -> Path:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


def _clear_pycache(root: Path) -> None:
    for cache_dir in root.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)
    for name in list(sys.modules):
        if name == "src" or name.startswith("src."):
            del sys.modules[name]


def _restore_from_backup(root: Path, relative_path: str, backup_relative: str, ok_markers: tuple[str, ...]) -> bool:
    target = root / relative_path
    backup = root / backup_relative
    if not backup.exists():
        return False

    needs_restore = True
    if target.exists():
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
            size_ok = target.stat().st_size >= MIN_UI_THEME_BYTES if relative_path.endswith("ui_theme.py") else True
            needs_restore = not (all(marker in text for marker in ok_markers) and size_ok)
        except OSError:
            needs_restore = True

    if needs_restore:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup, target)
        print(f"Restored {relative_path} from {backup_relative}")
        return True
    return False


def _git_restore(root: Path, paths: list[str]) -> bool:
    if not (root / ".git").exists():
        return False
    try:
        subprocess.run(["git", "fetch", "origin", "main"], cwd=root, capture_output=True, text=True, check=False)
        result = subprocess.run(
            ["git", "checkout", "origin/main", "--", *paths],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _ui_theme_imports_ok(root: Path) -> bool:
    _clear_pycache(root)
    try:
        module = importlib.import_module("src.ui_theme")
    except Exception:
        return False
    return all(hasattr(module, name) for name in UI_THEME_EXPORTS)


def main() -> int:
    root = _project_root()

    print("CareerCompass Emergency Repair")
    print("==============================")
    print(f"Project: {root}")
    print()

    _clear_pycache(root)

    git_paths = [
        "src/ui_theme.py",
        "src/_repair/ui_theme.py",
        "src/_repair/source_repair.py",
        "src/source_repair.py",
        "src/brand_constants.py",
        "app/streamlit_app.py",
    ]
    if _git_restore(root, git_paths):
        print("Git repair: restored files from origin/main")
    else:
        print("Git repair: skipped (no git or fetch failed)")

    _clear_pycache(root)

    _restore_from_backup(
        root,
        "src/ui_theme.py",
        "src/_repair/ui_theme.py",
        ("render_feature_card", "render_app_footer", "brand_constants"),
    )
    _restore_from_backup(
        root,
        "src/source_repair.py",
        "src/_repair/source_repair.py",
        ("file_has_markers", "ui_theme_is_valid"),
    )

    _clear_pycache(root)

    if not _ui_theme_imports_ok(root):
        print("\nERROR: ui_theme.py is still broken after repair.")
        print("Check that src/_repair/ui_theme.py exists and re-run:")
        print("  git fetch origin main")
        print("  git reset --hard origin/main")
        print("  python scripts/emergency_repair.py")
        return 1

    from src.brand_constants import APP_NAME, APP_VERSION  # noqa: WPS433
    from src.ui_theme import render_app_footer, render_feature_card  # noqa: WPS433

    ui_path = root / "src" / "ui_theme.py"
    print()
    print(f"ui_theme.py size: {ui_path.stat().st_size} bytes")
    print(f"Import check OK: {APP_NAME} ({APP_VERSION})")
    print(f"UI helpers OK: render_feature_card={callable(render_feature_card)}")
    print()
    print("Repair complete. Start the app with:")
    print("  .\\run_app.ps1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
