"""Configuration helpers for the project."""

from pathlib import Path
import yaml


def get_project_root() -> Path:
    """
    Return the project root directory.

    This function resolves the root relative to this file so it works
    regardless of the current working directory.
    """
    return Path(__file__).resolve().parent.parent


def load_config(config_path: str | Path = "config.yaml") -> dict:
    """
    Load YAML configuration as a dictionary.

    Parameters
    ----------
    config_path : str | Path, optional
        Path to the YAML config file. If relative, it is resolved
        against the project root.

    Returns
    -------
    dict
        Loaded configuration values.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    ValueError
        If the YAML file is empty or not a dictionary.
    """
    root = get_project_root()
    candidate_path = Path(config_path)
    resolved_path = candidate_path if candidate_path.is_absolute() else root / candidate_path

    if not resolved_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {resolved_path}. "
            "Create config.yaml at the project root or pass an absolute path."
        )

    with resolved_path.open("r", encoding="utf-8") as file:
        config_data = yaml.safe_load(file)

    if config_data is None:
        raise ValueError(f"Config file is empty: {resolved_path}")

    if not isinstance(config_data, dict):
        raise ValueError(
            f"Config must be a YAML mapping/dictionary, got {type(config_data).__name__}."
        )

    return config_data


CONFIG = load_config()
