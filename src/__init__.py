"""
src package initialiser.

Runs a lightweight source-file repair on import so outdated local copies
(for example an old ui_theme.py missing APP_NAME) are fixed automatically.
"""

from __future__ import annotations

try:
    from src.source_repair import ensure_careercompass_sources

    ensure_careercompass_sources()
except Exception:
    # Never block package import in edge environments; verify script will catch issues.
    pass
