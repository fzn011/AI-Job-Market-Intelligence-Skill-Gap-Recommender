"""Streamlit helpers for CV/resume upload inputs."""

from __future__ import annotations

import streamlit as st

from src.document_text_utils import extract_text_from_upload


def render_cv_upload_input(
    upload_label: str = "Upload CV / Resume",
    key_prefix: str = "cv",
) -> str:
    """Render CV upload field and return extracted text."""
    uploaded = st.file_uploader(
        upload_label,
        type=["pdf", "docx", "txt"],
        key=f"{key_prefix}_file",
    )
    if uploaded is None:
        return ""

    try:
        uploaded_text = extract_text_from_upload(uploaded.getvalue(), uploaded.name)
        st.caption(f"Loaded {len(uploaded_text.split())} words from {uploaded.name}")
        return uploaded_text
    except ValueError as exc:
        st.error(str(exc))
        return ""
