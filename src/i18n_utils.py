"""Multilingual UI translation utilities."""

from __future__ import annotations

import json
from pathlib import Path

SUPPORTED_LANGUAGES = {
    "English": "en",
    "Bengali": "bn",
}


def get_i18n_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "i18n"


def load_translations(language_code: str = "en") -> dict:
    """Load translation dictionary for a language code."""
    path = get_i18n_dir() / f"{language_code}.json"
    if not path.exists():
        path = get_i18n_dir() / "en.json"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def translate(key: str, language_code: str = "en", default: str | None = None) -> str:
    """Translate a key to the selected language."""
    translations = load_translations(language_code)
    if key in translations:
        return translations[key]
    if default is not None:
        return default
    en = load_translations("en")
    return en.get(key, key)


def t(key: str, language_code: str = "en", default: str | None = None) -> str:
    """Short alias for translate()."""
    return translate(key, language_code, default)


def get_language_code(language_label: str) -> str:
    return SUPPORTED_LANGUAGES.get(language_label, "en")
