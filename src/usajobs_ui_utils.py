"""USAJobs connector UI helpers."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.secrets_utils import bootstrap_app_secrets, get_usajobs_diagnostics


def render_usajobs_status(project_root: Path | None = None) -> dict:
    """Show a compact USAJobs connection status banner."""
    bootstrap_app_secrets(project_root, force=True)
    status = get_usajobs_diagnostics(project_root)
    if status["configured"]:
        st.success(
            f"USAJobs ready · {status['email']} · key length {status['api_key_length']} · "
            f"{status.get('source', 'secrets.toml')}"
        )
    else:
        st.error("USAJobs credentials were not loaded.")
        hint = status.get("hint")
        if hint:
            st.caption(hint)
        with st.expander("Where CareerCompass looked for secrets"):
            for path in status.get("checked_paths", []):
                marker = "FOUND" if Path(path).exists() else "missing"
                st.write(f"- [{marker}] `{path}`")
    return status
