"""Resolve credentials from environment, dotenv, or Streamlit secrets."""

from __future__ import annotations

import os
import re
from pathlib import Path

_CACHED_SECRETS: dict[str, str] | None = None
_BOOTSTRAP_DONE = False

_PLACEHOLDER_VALUES = {
    "",
    "your-free-key",
    "your-usajobs-api-key",
    "+your-usajobs-api-key=",
    "your@email.com",
    "user@example.com",
}

_USAJOBS_KEYS = ("USAJOBS_API_KEY", "USAJOBS_USER_EMAIL")


def _normalize_secret(value: str) -> str:
    cleaned = str(value or "").strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def _is_placeholder(value: str) -> bool:
    normalized = _normalize_secret(value).lower()
    return normalized in _PLACEHOLDER_VALUES


def discover_project_roots(explicit_root: Path | None = None) -> list[Path]:
    """Collect likely CareerCompass project roots."""
    roots: list[Path] = []

    if explicit_root is not None:
        roots.append(explicit_root.resolve())

    module_root = Path(__file__).resolve().parents[1]
    roots.append(module_root)

    cwd = Path.cwd()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "config.yaml").exists():
            roots.append(candidate)
            break
        if (candidate / "setup.ps1").exists() and (candidate / "app" / "streamlit_app.py").exists():
            roots.append(candidate)
            break

    unique: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        resolved = root.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def get_project_root(explicit_root: Path | None = None) -> Path:
    roots = discover_project_roots(explicit_root)
    return roots[0] if roots else Path(__file__).resolve().parents[1]


def secrets_toml_candidates(explicit_root: Path | None = None) -> list[Path]:
    """Return possible secrets.toml locations, most reliable first."""
    paths: list[Path] = []

    env_path = os.getenv("STREAMLIT_SECRETS_FILE", "").strip()
    if env_path:
        paths.append(Path(env_path))

    for root in discover_project_roots(explicit_root):
        paths.extend(
            [
                root / ".streamlit" / "secrets.toml",
                root / "app" / ".streamlit" / "secrets.toml",
                root / "secrets.toml",
            ]
        )

    paths.append(Path.cwd() / ".streamlit" / "secrets.toml")

    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        try:
            resolved = path.resolve()
        except OSError:
            continue
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
        if value and not _is_placeholder(value):
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


def _read_secrets_file(secrets_path: Path) -> dict[str, str]:
    if not secrets_path.exists():
        return {}

    for encoding in ("utf-8", "utf-8-sig", "utf-16", "cp1252", "latin-1"):
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
                    return flattened
        except Exception:
            fallback = _parse_secrets_toml_fallback(raw_text)
            if fallback:
                return fallback

    return {}


def load_secrets_toml(explicit_root: Path | None = None) -> tuple[dict[str, str], Path | None]:
    """Load secrets.toml from the first readable candidate path."""
    for secrets_path in secrets_toml_candidates(explicit_root):
        data = _read_secrets_file(secrets_path)
        if data:
            return data, secrets_path
    return {}, None


def _load_dotenv_files(explicit_root: Path | None = None) -> dict[str, str]:
    loaded: dict[str, str] = {}
    try:
        from dotenv import dotenv_values
    except ImportError:
        return loaded

    for root in discover_project_roots(explicit_root):
        env_path = root / ".env"
        if not env_path.exists():
            continue
        values = dotenv_values(env_path)
        for key, value in values.items():
            if value and not _is_placeholder(str(value)):
                loaded[str(key)] = _normalize_secret(str(value))
    return loaded


def bootstrap_app_secrets(explicit_root: Path | None = None, force: bool = False) -> dict[str, str]:
    """Load secrets once per process and cache them in memory + os.environ."""
    global _CACHED_SECRETS, _BOOTSTRAP_DONE

    if _BOOTSTRAP_DONE and not force and _CACHED_SECRETS is not None:
        return _CACHED_SECRETS

    merged: dict[str, str] = {}
    merged.update(_load_dotenv_files(explicit_root))

    file_data, loaded_from = load_secrets_toml(explicit_root)
    merged.update(file_data)

    for key in _USAJOBS_KEYS:
        env_value = _normalize_secret(os.getenv(key, ""))
        if env_value and not _is_placeholder(env_value):
            merged[key] = env_value

    try:
        import streamlit as st

        if hasattr(st, "secrets"):
            for key in _USAJOBS_KEYS:
                if key in st.secrets:
                    value = _normalize_secret(str(st.secrets[key]))
                    if value and not _is_placeholder(value):
                        merged.setdefault(key, value)
    except Exception:
        pass

    for key in _USAJOBS_KEYS:
        value = merged.get(key, "")
        if value and not _is_placeholder(value):
            os.environ[key] = value

    if loaded_from is not None:
        os.environ["STREAMLIT_SECRETS_FILE"] = str(loaded_from)
        os.environ["CC_SECRETS_SOURCE"] = str(loaded_from)
    elif merged:
        os.environ["CC_SECRETS_SOURCE"] = "environment/.env"

    _CACHED_SECRETS = merged
    _BOOTSTRAP_DONE = True
    return merged


def get_usajobs_diagnostics(explicit_root: Path | None = None) -> dict:
    """Return safe diagnostics for USAJobs credential loading."""
    bootstrap_app_secrets(explicit_root)
    checked_paths = [str(path) for path in secrets_toml_candidates(explicit_root)]
    secrets_data = _CACHED_SECRETS or {}
    api_key = secrets_data.get("USAJOBS_API_KEY", "")
    email = secrets_data.get("USAJOBS_USER_EMAIL", "")
    loaded_from = os.getenv("CC_SECRETS_SOURCE", "")

    if api_key and email and not _is_placeholder(email) and not _is_placeholder(api_key):
        return {
            "configured": True,
            "email": email,
            "api_key_length": len(api_key),
            "source": loaded_from or "cached secrets",
            "checked_paths": checked_paths,
        }

    hint = "Create `.streamlit/secrets.toml` in the project root (same folder as setup.ps1)."
    existing_paths = [path for path in checked_paths if Path(path).exists()]
    if existing_paths:
        hint = (
            f"Found secrets file(s) at {existing_paths[0]} but USAJobs keys were not readable. "
            "Use quoted values, save as UTF-8, then restart with .\\run_app.ps1"
        )
    elif _is_placeholder(os.getenv("USAJOBS_API_KEY", "")) or _is_placeholder(os.getenv("USAJOBS_USER_EMAIL", "")):
        hint = "Remove placeholder USAJOBS_* environment variables, then restart with .\\run_app.ps1"

    return {
        "configured": False,
        "email": "",
        "api_key_length": len(api_key),
        "source": loaded_from,
        "checked_paths": checked_paths,
        "hint": hint,
    }


def get_secret(key: str, default: str = "", explicit_root: Path | None = None) -> str:
    """Read a secret from cached bootstrap, secrets.toml, Streamlit secrets, or env vars."""
    bootstrap_app_secrets(explicit_root)

    candidates: list[str] = []
    if _CACHED_SECRETS and key in _CACHED_SECRETS:
        candidates.append(_CACHED_SECRETS[key])

    file_value = load_secrets_toml(explicit_root)[0].get(key, "")
    if file_value:
        candidates.append(file_value)

    env_value = os.getenv(key, "").strip()
    if env_value:
        candidates.append(env_value)

    try:
        import streamlit as st

        if hasattr(st, "secrets") and key in st.secrets:
            candidates.append(str(st.secrets[key]))
    except Exception:
        pass

    for candidate in candidates:
        normalized = _normalize_secret(candidate)
        if normalized and not _is_placeholder(normalized):
            return normalized

    fallback = _normalize_secret(default)
    return "" if _is_placeholder(fallback) else fallback


def get_usajobs_credentials(
    api_key_override: str = "",
    email_override: str = "",
    explicit_root: Path | None = None,
) -> tuple[str, str]:
    """Return USAJobs API key and user email."""
    bootstrap_app_secrets(explicit_root)
    api_key = _normalize_secret(api_key_override) or get_secret("USAJOBS_API_KEY", explicit_root=explicit_root)
    email = _normalize_secret(email_override) or get_secret("USAJOBS_USER_EMAIL", explicit_root=explicit_root)
    if _is_placeholder(email):
        email = ""
    if _is_placeholder(api_key):
        api_key = ""
    return api_key, email


def usajobs_credentials_configured(
    api_key_override: str = "",
    email_override: str = "",
    explicit_root: Path | None = None,
) -> bool:
    """Return True when both USAJobs credentials are available."""
    api_key, email = get_usajobs_credentials(api_key_override, email_override, explicit_root)
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
