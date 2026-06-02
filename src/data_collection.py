"""
data_collection.py — Job data ingestion module.

Responsibilities (planned):
    - Load job postings from local CSV files
    - Scrape publicly available job listings from open sources
    - Normalise raw data into a consistent schema
    - Save raw data to data/raw/ for downstream processing

All data sources used will be free and open. No paid APIs.
"""

import pandas as pd
from pathlib import Path

from src.utils import load_dataframe, save_dataframe


def collect_jobs_from_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Load job postings from a local CSV file.

    Parameters
    ----------
    file_path : str or Path
        Path to the CSV file containing job postings.

    Returns
    -------
    pd.DataFrame
        Raw job postings DataFrame.
    """
    # Placeholder — full validation and schema enforcement to be added
    print(f"[INFO] Loading jobs from: {file_path}")
    return load_dataframe(file_path)


def collect_jobs() -> str:
    """Placeholder for the full job data collection pipeline."""
    return "Job collection module is ready."
