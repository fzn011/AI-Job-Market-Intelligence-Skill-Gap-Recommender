"""Resolve credentials from environment, dotenv, or Streamlit secrets."""

from __future__ import annotations

import os
from pathlib import Path


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
        return str(value).strip() if value is not None else ""
    except Exception:
        return ""


def get_secret(key: str, default: str = "") -> str:
    """Read a secret from env vars, optional .env, Streamlit secrets, or secrets.toml file."""
    _load_dotenv_if_available()
    value = os.getenv(key, "").strip()
    if value:
        return value

    try:
        import streamlit as st

        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key]).strip()
    except Exception:
        pass

    file_value = _read_streamlit_secrets_file(key)
    if file_value:
        return file_value

    return default


def get_usajobs_credentials() -> tuple[str, str]:
    """Return USAJobs API key and user email."""
    return (
        get_secret("USAJOBS_API_KEY"),
        get_secret("USAJOBS_USER_EMAIL", "user@example.com"),
    )


def get_smtp_settings() -> dict:
    """Return SMTP settings for optional email digest."""
    return {
        "host": get_secret("SMTP_HOST"),
        "port": int(get_secret("SMTP_PORT", "587") or "587"),
        "user": get_secret("SMTP_USER"),
        "password": get_secret("SMTP_PASSWORD"),
        "recipient": get_secret("DIGEST_RECIPIENT"),
    }
