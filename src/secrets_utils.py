"""Resolve credentials from environment, dotenv, or Streamlit secrets."""

from __future__ import annotations

import os
import re
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


def get_project_root() -> Path:
    """Resolve CareerCompass project root from module location or working tree."""
    module_root = Path(__file__).resolve().parents[1]
    candidates = [module_root, Path.cwd(), *Path.cwd().parents]

    for candidate in candidates:
        if (candidate / "config.yaml").exists():
            return candidate
        if (candidate / "app" / "streamlit_app.py").exists() and (candidate / "src").is_dir():
            return candidate

    return module_root


def secrets_toml_candidates() -> list[Path]:
    """Return possible secrets.toml locations, most reliable first."""
    root = get_project_root()
    paths: list[Path] = [
        root / ".streamlit" / "secrets.toml",
        Path.cwd() / ".streamlit" / "secrets.toml",
    ]

    env_path = os.getenv("STREAMLIT_SECRETS_FILE", "").strip()
    if env_path:
        paths.insert(0, Path(env_path))

    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def _parse_secrets_toml_fallback(text: str) -> dict[str, str]:
    """Parse simple KEY = \"value\" lines when full TOML parsing fails."""
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_]+)\s*=\s*(.+)$", line)
        if not match:
            continue
        key = match.group(1).strip()
        value = _normalize_secret(match.group(2).strip())
        if value:
            result[key] = value
    return result


def _flatten_secrets_data(data: dict) -> dict[str, str]:
    flat: dict[str, str] = {}
    for key, value in data.items():
        if key == "secrets" and isinstance(value, dict):
            for nested_key, nested_value in value.items():
                flat[str(nested_key)] = _normalize_secret(str(nested_value))
        elif not isinstance(value, dict):
            flat[str(key)] = _normalize_secret(str(value))
    return flat


def load_secrets_toml() -> tuple[dict[str, str], Path | None]:
    """Load secrets.toml from the first readable candidate path."""
    for secrets_path in secrets_toml_candidates():
        if not secrets_path.exists():
            continue

        for encoding in ("utf-8", "utf-8-sig", "utf-16", "cp1252"):
            try:
                raw_text = secrets_path.read_text(encoding=encoding)
            except OSError:
                continue

            try:
                try:
                    import tomllib

                    data = tomllib.loads(raw_text)
                except ImportError:
                    import toml

                    data = toml.loads(raw_text)

                if isinstance(data, dict):
                    flattened = _flatten_secrets_data(data)
                    if flattened:
                        return flattened, secrets_path
            except Exception:
                fallback = _parse_secrets_toml_fallback(raw_text)
                if fallback:
                    return fallback, secrets_path

    return {}, None


def get_usajobs_diagnostics() -> dict:
    """Return safe diagnostics for USAJobs credential loading."""
    checked_paths = [str(path) for path in secrets_toml_candidates()]
    secrets_data, loaded_from = load_secrets_toml()
    api_key = secrets_data.get("USAJOBS_API_KEY", "")
    email = secrets_data.get("USAJOBS_USER_EMAIL", "")

    if api_key and email and not _is_placeholder(email):
        return {
            "configured": True,
            "email": email,
            "source": str(loaded_from) if loaded_from else "secrets.toml",
            "checked_paths": checked_paths,
        }

    env_key = _normalize_secret(os.getenv("USAJOBS_API_KEY", ""))
    env_email = _normalize_secret(os.getenv("USAJOBS_USER_EMAIL", ""))
    if env_key and env_email and not _is_placeholder(env_key) and not _is_placeholder(env_email):
        return {
            "configured": True,
            "email": env_email,
            "source": "environment variables",
            "checked_paths": checked_paths,
        }

    hint = "Create `.streamlit/secrets.toml` in the project root (same folder as setup.ps1)."
    if loaded_from:
        hint = f"Found `{loaded_from}` but USAJobs keys are missing or invalid."
    elif any(Path(path).exists() for path in checked_paths):
        hint = "Found a secrets.toml file but could not read USAJobs keys. Quote values that contain + or /."
    elif _is_placeholder(env_key) or _is_placeholder(env_email):
        hint = "Remove placeholder USAJOBS_* environment variables; they override secrets.toml."

    return {
        "configured": False,
        "email": "",
        "source": "",
        "checked_paths": checked_paths,
        "hint": hint,
    }


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(get_project_root() / ".env")
    except ImportError:
        return


def _read_streamlit_secrets_file(key: str) -> str:
    """Read a key from secrets.toml using robust path detection."""
    secrets_data, _ = load_secrets_toml()
    return secrets_data.get(key, "")


def get_secret(key: str, default: str = "") -> str:
    """Read a secret from secrets.toml, Streamlit secrets, env vars, or optional .env."""
    _load_dotenv_if_available()

    candidates: list[str] = []

    file_value = _read_streamlit_secrets_file(key)
    if file_value:
        candidates.append(file_value)

    try:
        import streamlit as st

        if hasattr(st, "secrets") and key in st.secrets:
            candidates.append(str(st.secrets[key]))
    except Exception:
        pass

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
