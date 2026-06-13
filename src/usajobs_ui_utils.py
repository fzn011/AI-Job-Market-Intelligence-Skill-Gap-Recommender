"""USAJobs connector UI helpers."""

from __future__ import annotations

import streamlit as st

from src.secrets_utils import get_usajobs_diagnostics


def render_usajobs_status() -> dict:
    """Show a compact USAJobs connection status banner."""
    status = get_usajobs_diagnostics()
    if status["configured"]:
        source = status.get("source", "secrets.toml")
        st.success(f"USAJobs ready · {status['email']} · loaded from {source}")
    else:
        st.warning("USAJobs not configured.")
        hint = status.get("hint")
        if hint:
            st.caption(hint)
        with st.expander("Where CareerCompass looked for secrets"):
            for path in status.get("checked_paths", []):
                st.code(path)
    return status
