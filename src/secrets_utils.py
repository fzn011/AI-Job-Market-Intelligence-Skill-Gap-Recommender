"""Resolve credentials from environment, dotenv, or Streamlit secrets."""

from __future__ import annotations

import os
from pathlib import Path

_PLACEHOLDER_VALUES = {
    "",
    "your-free-key",
    "your-usajobs-api-key",
    "your@email.com",
    "user@example.com",
}


def _normalize_secret(value: str) -> str:
    cleaned = str(value or "").strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def _is_placeholder(value: str) -> bool:
    normalized = _normalize_secret(value).lower()
    return normalized in _PLACEHOLDER_VALUES


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv

        root = Path(__file__).resolve().parents[1]
        load_dotenv(root / ".env")
    except ImportError:
        return


def _read_streamlit_secrets_file(key: str) -> str:
    """Read key directly from .streamlit/secrets.toml when Streamlit runtime is unavailable."""
    secrets_path = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"
    if not secrets_path.exists():
        return ""

    try:
        try:
            import tomllib
            with secrets_path.open("rb") as fh:
                data = tomllib.load(fh)
        except ImportError:
            import toml

            data = toml.load(secrets_path)

        value = data.get(key, "")
        return _normalize_secret(str(value)) if value is not None else ""
    except Exception:
        return ""


def get_secret(key: str, default: str = "") -> str:
    """Read a secret from Streamlit secrets, secrets.toml, env vars, or optional .env."""
    _load_dotenv_if_available()

    candidates: list[str] = []

    try:
        import streamlit as st

        if hasattr(st, "secrets") and key in st.secrets:
            candidates.append(str(st.secrets[key]))
    except Exception:
        pass

    file_value = _read_streamlit_secrets_file(key)
    if file_value:
        candidates.append(file_value)

    env_value = os.getenv(key, "").strip()
    if env_value:
        candidates.append(env_value)

    for candidate in candidates:
        normalized = _normalize_secret(candidate)
        if normalized and not _is_placeholder(normalized):
            return normalized

    fallback = _normalize_secret(default)
    return "" if _is_placeholder(fallback) else fallback


def get_usajobs_credentials(
    api_key_override: str = "",
    email_override: str = "",
) -> tuple[str, str]:
    """Return USAJobs API key and user email."""
    api_key = _normalize_secret(api_key_override) or get_secret("USAJOBS_API_KEY")
    email = _normalize_secret(email_override) or get_secret("USAJOBS_USER_EMAIL")
    if _is_placeholder(email):
        email = ""
    return api_key, email


def usajobs_credentials_configured(
    api_key_override: str = "",
    email_override: str = "",
) -> bool:
    """Return True when both USAJobs credentials are available."""
    api_key, email = get_usajobs_credentials(api_key_override, email_override)
    return bool(api_key and email and "@" in email)


def get_smtp_settings() -> dict:
    """Return SMTP settings for optional email digest."""
    return {
        "host": get_secret("SMTP_HOST"),
        "port": int(get_secret("SMTP_PORT", "587") or "587"),
        "user": get_secret("SMTP_USER"),
        "password": get_secret("SMTP_PASSWORD"),
        "recipient": get_secret("DIGEST_RECIPIENT"),
    }
