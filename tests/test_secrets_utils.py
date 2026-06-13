"""Tests for secrets resolution helpers."""

from __future__ import annotations

import os

import pytest

from src.secrets_utils import (  # noqa: E402
    _is_placeholder,
    _normalize_secret,
    _parse_secrets_toml_fallback,
    bootstrap_app_secrets,
    get_project_root,
    get_secret,
    get_usajobs_credentials,
    get_usajobs_diagnostics,
    load_secrets_toml,
)


def test_normalize_secret_strips_quotes():
    assert _normalize_secret('"abc+123="') == "abc+123="
    assert _normalize_secret("'user@example.com'") == "user@example.com"


def test_placeholder_values_are_detected():
    assert _is_placeholder("your-free-key")
    assert _is_placeholder("your@email.com")
    assert not _is_placeholder("faiazzahin@gmail.com")


def test_get_secret_ignores_placeholder_env(monkeypatch):
    monkeypatch.setenv("USAJOBS_API_KEY", "your-free-key")
    monkeypatch.delenv("USAJOBS_USER_EMAIL", raising=False)
    value = get_secret("USAJOBS_API_KEY")
    assert value != "your-free-key"


def test_get_usajobs_credentials_use_overrides():
    key, email = get_usajobs_credentials(
        api_key_override="+test-key=",
        email_override="faiazzahin@gmail.com",
    )
    assert key == "+test-key="
    assert email == "faiazzahin@gmail.com"


def test_parse_secrets_toml_fallback():
    text = """
    # comment
    USAJOBS_API_KEY = "+abc+123="
    USAJOBS_USER_EMAIL = "faiazzahin@gmail.com"
    """
    parsed = _parse_secrets_toml_fallback(text)
    assert parsed["USAJOBS_API_KEY"] == "+abc+123="
    assert parsed["USAJOBS_USER_EMAIL"] == "faiazzahin@gmail.com"


def test_get_project_root_points_to_repo():
    root = get_project_root()
    assert (root / "app" / "streamlit_app.py").exists()
    assert (root / "src" / "secrets_utils.py").exists()


def test_load_secrets_toml_finds_workspace_file():
    data, path = load_secrets_toml()
    if path is not None:
        assert path.name == "secrets.toml"
        assert "USAJOBS_API_KEY" in data or "USAJOBS_USER_EMAIL" in data


def test_usajobs_diagnostics_reports_status():
    bootstrap_app_secrets(force=True)
    status = get_usajobs_diagnostics()
    assert "configured" in status
    assert "checked_paths" in status
    assert isinstance(status["checked_paths"], list)


def test_bootstrap_caches_usajobs_credentials():
    bootstrap_app_secrets(force=True)
    key, email = get_usajobs_credentials()
    if key and email:
        assert len(key) > 10
        assert "@" in email
