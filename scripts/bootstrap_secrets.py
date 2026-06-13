#!/usr/bin/env python3
"""Bootstrap secrets and print USAJobs status for run_app.ps1."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from src.secrets_utils import bootstrap_app_secrets, get_usajobs_diagnostics

    bootstrap_app_secrets(root, force=True)
    diag = get_usajobs_diagnostics(root)

    if diag["configured"]:
        print(f"USAJobs credentials OK: {diag['email']} (key length {diag['api_key_length']})")
        print(f"Source: {diag['source']}")
        return 0

    print("USAJobs credentials NOT configured.")
    if diag.get("hint"):
        print(diag["hint"])
    print("Checked paths:")
    for path in diag.get("checked_paths", []):
        exists = Path(path).exists()
        print(f"  - {path} [{'found' if exists else 'missing'}]")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
