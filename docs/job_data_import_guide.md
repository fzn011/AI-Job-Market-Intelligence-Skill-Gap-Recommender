# Job Data Import Guide

This project supports safe, legal, free job-data ingestion through local CSV files and synthetic demo datasets.

## Supported import sources

- `manual_csv`
- `synthetic_demo`
- `user_uploaded_csv`
- `public_dataset`

## Standard CSV schema

### Required columns

| Column | Required | Description |
|---|---|---|
| `job_id` | Yes | Unique identifier for each job posting. Must be unique. |
| `job_title` | Yes | Job role title (e.g., Data Analyst, AI Engineer). |
| `company` | Yes | Employer name (for demo data, use synthetic names). |
| `location` | Yes | Job location (city/region/remote style). |
| `job_type` | Yes | Job type label (e.g., Full-time, Contract, Internship). |
| `description` | Yes | Role summary including responsibilities, tools, and skills. |
| `date_posted` | Yes | Posting date. Preferred format: `YYYY-MM-DD`. |
| `source` | Yes | Source tag describing origin (see supported sources above). |

### Optional columns

| Column | Required | Description |
|---|---|---|
| `salary_min` | No | Minimum salary value if available. |
| `salary_max` | No | Maximum salary value if available. |
| `currency` | No | Currency code (e.g., USD, GBP, BDT, AUD, SGD, CAD). |
| `experience_level` | No | Experience band (e.g., Junior, Mid, Senior). |
| `remote_type` | No | Remote mode (Remote, Hybrid, On-site). |
| `employment_type` | No | Employment category if different from job_type. |
| `industry` | No | Industry label (e.g., FinTech, Retail, HealthTech). |
| `country` | No | Country for location normalization/analysis. |
| `application_url` | No | Link to apply (may be blank). |

## Data quality expectations

- `job_id` should be unique across rows.
- `description` should include meaningful role context and likely skills/tools.
- `date_posted` should use `YYYY-MM-DD` where possible.
- `source` should clearly identify data origin.
- No private or sensitive personal data should be included.

## Legal and ethics notes

- Respect the terms of service of any source website or dataset.
- Avoid aggressive scraping.
- Do not redistribute restricted or copyrighted job descriptions if terms do not allow it.
- Prefer manual CSV imports, synthetic demo data, user uploads, and open/public datasets with clear permissions.

## Quick start

- Generate processed outputs from expanded demo data:
  - `python scripts/import_jobs_from_csv.py --demo expanded`

- Process your own CSV:
  - `python scripts/import_jobs_from_csv.py --input data/raw/my_jobs.csv`

- Optional custom output naming:
  - `python scripts/import_jobs_from_csv.py --input data/raw/my_jobs.csv --output-name my_jobs`
