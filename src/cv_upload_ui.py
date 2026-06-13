"""Streamlit helpers for CV/resume upload inputs."""

from __future__ import annotations

import streamlit as st

from src.document_text_utils import extract_text_from_upload, merge_cv_text


def render_cv_upload_input(
    upload_label: str = "Upload CV / Resume",
    paste_label: str = "Or paste CV text (optional)",
    paste_height: int = 100,
    key_prefix: str = "cv",
) -> str:
    """Render CV upload + optional paste fields and return resolved CV text."""
    uploaded = st.file_uploader(
        upload_label,
        type=["pdf", "docx", "txt"],
        key=f"{key_prefix}_file",
    )
    uploaded_text = ""
    if uploaded is not None:
        try:
            uploaded_text = extract_text_from_upload(uploaded.getvalue(), uploaded.name)
            st.caption(f"Loaded {len(uploaded_text.split())} words from {uploaded.name}")
        except ValueError as exc:
            st.error(str(exc))

    pasted = st.text_area(
        paste_label,
        height=paste_height,
        key=f"{key_prefix}_paste",
        placeholder="Optional if you uploaded a file above...",
    )
    return merge_cv_text(uploaded_text, pasted)
