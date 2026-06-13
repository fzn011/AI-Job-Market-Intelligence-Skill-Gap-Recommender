"""Tests for document text extraction utilities."""

from __future__ import annotations

import pytest

from src.document_text_utils import extract_text_from_upload, merge_cv_text


def test_merge_cv_text_prefers_upload():
    assert merge_cv_text("uploaded cv", "pasted cv") == "uploaded cv"
    assert merge_cv_text("", "pasted cv") == "pasted cv"


def test_extract_text_from_txt_upload():
    text = extract_text_from_upload(b"Python\nSQL\nPower BI", "resume.txt")
    assert "Python" in text
    assert "Power BI" in text


def test_extract_text_from_empty_upload_raises():
    with pytest.raises(ValueError, match="empty"):
        extract_text_from_upload(b"", "resume.txt")


def test_extract_text_from_unsupported_type_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        extract_text_from_upload(b"data", "resume.xlsx")
