"""Shared utility functions used across the project."""

from pathlib import Path
import json
import re
import pandas as pd


def ensure_directory(path: str | Path) -> Path:
    """
    Create a directory (and any parent directories) if it does not
    already exist.

    Parameters
    ----------
    path : str or Path
        Directory path to create.

    Returns
    -------
    Path
        The resolved Path object for the directory.
    """
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_dataframe(df: pd.DataFrame, path: str | Path) -> None:
    """
    Save a pandas DataFrame to a CSV file.

    Automatically creates parent directories if they do not exist.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to save.
    path : str or Path
        Destination file path (should end with .csv).
    """
    file_path = Path(path)
    if file_path.suffix.lower() != ".csv":
        raise ValueError("save_dataframe currently supports CSV files only.")

    ensure_directory(file_path.parent)
    df.to_csv(file_path, index=False, encoding="utf-8")


def load_dataframe(path: str | Path) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.

    Parameters
    ----------
    path : str or Path
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame, or an empty DataFrame if the file is not found.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    if file_path.suffix.lower() != ".csv":
        raise ValueError("load_dataframe currently supports CSV files only.")

    return pd.read_csv(file_path, encoding="utf-8")


def clean_text(text) -> str:
    """
    Normalise a raw text string for NLP processing.

    Steps applied:
        1. Handle None / non-string input safely
        2. Convert to lowercase
        3. Remove punctuation and special characters
        4. Collapse multiple whitespace characters to a single space
        5. Strip leading and trailing whitespace

    Parameters
    ----------
    text : str or None
        Raw input text.

    Returns
    -------
    str
        Cleaned, normalised string. Returns empty string for None input.
    """
    if text is None:
        return ""

    text = str(text)

    # Lowercase and normalize whitespace/newlines/tabs
    text = text.lower()
    text = text.replace("\n", " ").replace("\t", " ")

    # Keep useful skill characters: +, #, ., /, -
    text = re.sub(r"[^a-z0-9\+\#\./\-\s]", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def load_json(path: str | Path) -> dict:
    """
    Load a JSON file into a dictionary.

    Raises FileNotFoundError if missing and ValueError if JSON is invalid.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {file_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {file_path}.")

    return data


def save_json(data: dict, path: str | Path) -> None:
    """Save a dictionary to a JSON file with pretty formatting."""
    file_path = Path(path)
    ensure_directory(file_path.parent)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
