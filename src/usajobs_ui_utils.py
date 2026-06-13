"""USAJobs connector UI helpers."""

from __future__ import annotations

import streamlit as st

from src.public_data_connectors import get_usajobs_connection_status


def render_usajobs_status() -> dict:
    """Show a compact USAJobs connection status banner."""
    status = get_usajobs_connection_status()
    if status["configured"]:
        st.success(f"USAJobs ready · {status['email']}")
    else:
        st.warning("USAJobs not configured. Add credentials to `.streamlit/secrets.toml`.")
    return status
