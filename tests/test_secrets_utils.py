"""Tests for secrets resolution helpers."""

from __future__ import annotations

import os

import pytest

from src.secrets_utils import _is_placeholder, _normalize_secret, get_secret, get_usajobs_credentials


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
