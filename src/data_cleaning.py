"""Data cleaning and validation helpers for job datasets."""

import pandas as pd

from src.utils import clean_text


REQUIRED_JOB_COLUMNS = [
    "job_id",
    "job_title",
    "company",
    "location",
    "job_type",
    "description",
    "date_posted",
    "source",
]


def validate_job_columns(df: pd.DataFrame, required_columns: list[str]) -> bool:
    """
    Validate that all required columns are present.

    Raises ValueError listing missing columns when validation fails.
    """
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )
    return True


def drop_duplicates(df: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    """
    Remove duplicate rows from a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    subset : list of str, optional
        Columns to consider when identifying duplicates.
        Defaults to checking all columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with duplicates removed.
    """
    return df.drop_duplicates(subset=subset).reset_index(drop=True)


def clean_descriptions(df: pd.DataFrame, column: str = "description") -> pd.DataFrame:
    """
    Apply text normalisation to a job description column.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing a text column to clean.
    column : str
        Name of the column to clean. Defaults to 'description'.

    Returns
    -------
    pd.DataFrame
        DataFrame with an added 'clean_description' column.
    """
    cleaned_df = df.copy()
    cleaned_df["cleaned_description"] = cleaned_df[column].apply(clean_text)
    return cleaned_df


def clean_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline for a raw jobs DataFrame.

    Applies: duplicate removal → description normalisation.

    Parameters
    ----------
    df : pd.DataFrame
        Raw jobs DataFrame.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame.
    """
    cleaned_df = df.copy()

    # Standardize column names
    cleaned_df.columns = [str(column).strip().lower() for column in cleaned_df.columns]

    # Ensure required columns are present
    validate_job_columns(cleaned_df, REQUIRED_JOB_COLUMNS)

    # Remove duplicate jobs
    cleaned_df = drop_duplicates(cleaned_df, subset=["job_id"])

    # Remove rows where description is missing/blank
    description_series = cleaned_df["description"].astype("string")
    valid_mask = description_series.notna() & description_series.str.strip().ne("")
    cleaned_df = cleaned_df[valid_mask].reset_index(drop=True)

    # Clean text fields safely
    cleaned_df["cleaned_description"] = cleaned_df["description"].apply(clean_text)
    for column in ["job_title", "company", "location", "job_type"]:
        cleaned_df[column] = cleaned_df[column].apply(clean_text)

    return cleaned_df
