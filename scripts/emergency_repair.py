"""Emergency repair for broken Windows checkouts. Safe to run anytime."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


MIN_UI_THEME_BYTES = 12000


def _project_root() -> Path:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


def _clear_pycache(root: Path) -> None:
    for cache_dir in root.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)


def _bootstrap_ui_theme(root: Path) -> bool:
    """Restore ui_theme.py from bundled backup without importing src modules."""
    target = root / "src" / "ui_theme.py"
    backup = root / "src" / "_repair" / "ui_theme.py"
    if not backup.exists():
        return False

    needs_restore = True
    if target.exists():
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
            if "render_feature_card" in text and target.stat().st_size >= MIN_UI_THEME_BYTES:
                needs_restore = False
        except OSError:
            needs_restore = True

    if needs_restore:
        shutil.copy2(backup, target)
        print("Bootstrap: restored src/ui_theme.py from src/_repair/ui_theme.py")
        return True
    return False


def _bootstrap_source_repair(root: Path) -> bool:
    """Restore source_repair.py if emergency script cannot import it."""
    target = root / "src" / "source_repair.py"
    backup = root / "src" / "_repair" / "source_repair.py"
    if not backup.exists():
        return False

    needs_restore = True
    if target.exists():
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
            if "file_has_markers" in text and "ui_theme_is_valid" in text:
                needs_restore = False
        except OSError:
            needs_restore = True

    if needs_restore:
        shutil.copy2(backup, target)
        print("Bootstrap: restored src/source_repair.py from src/_repair/source_repair.py")
        return True
    return False


def main() -> int:
    root = _project_root()

    print("CareerCompass Emergency Repair")
    print("==============================")
    print(f"Project: {root}")
    print()

    _clear_pycache(root)
    _bootstrap_ui_theme(root)
    _bootstrap_source_repair(root)
    _clear_pycache(root)

    from src.source_repair import (  # noqa: WPS433
        clear_python_cache,
        ensure_careercompass_sources,
        repair_report,
        repair_ui_theme_from_backup,
        repair_with_git,
        ui_theme_is_valid,
    )

    print("Before repair:")
    for line in repair_report(root):
        print(f"  {line}")
    print()

    clear_python_cache(root)

    if repair_with_git(root):
        print("Git repair: attempted checkout from origin/main")
    else:
        print("Git repair: skipped (no git or fetch failed)")

    clear_python_cache(root)

    if not ui_theme_is_valid(root):
        if repair_ui_theme_from_backup(root):
            print("Backup repair: restored src/ui_theme.py from src/_repair/ui_theme.py")
        else:
            print("Backup repair: FAILED (backup missing)")

    clear_python_cache(root)

    try:
        ensure_careercompass_sources(root)
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        print("\nManual fix:")
        print("  git fetch origin main")
        print("  git reset --hard origin/main")
        print("  .\\setup.ps1 -RunApp")
        return 1

    from src.brand_constants import APP_NAME, APP_VERSION  # noqa: WPS433
    from src.ui_theme import render_app_footer, render_feature_card  # noqa: WPS433

    print()
    print("After repair:")
    for line in repair_report(root):
        print(f"  {line}")
    print()
    print(f"Import check OK: {APP_NAME} ({APP_VERSION})")
    print(f"UI helpers OK: render_feature_card={callable(render_feature_card)}")
    print()
    print("Repair complete. Start the app with:")
    print("  .\\run_app.ps1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
