# AI Job Market Intelligence + Skill Gap Recommender

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![scikit--learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikitlearn&logoColor=white)
![Tests](https://img.shields.io/badge/tests-99%20passed-brightgreen)

A local-first, open-source AI/Data Science project that turns job-posting text into practical career intelligence: market trends, skill gaps, project recommendations, and role clustering.

---

## Project pitch

This project helps AI/Data job seekers understand demand, assess profile alignment, and decide what to build next using transparent, free, and reproducible workflows.

## Problem statement

Job seekers in AI and data roles often receive generic advice, but need role-specific and market-backed guidance on which skills to prioritize.

## Why this project matters

- Converts job text into structured skill signals
- Maps current profile skills vs market demand
- Recommends project ideas aligned with hiring trends
- Supports safe, legal CSV import without paid APIs

---

## Current features

- Job data cleaning and validation pipeline
- Rule-based skill extraction from descriptions
- Job market overview analytics
- Skill demand and co-occurrence analysis
- CV skill gap analysis and downloadable report
- Project recommendation engine
- Role segmentation with unsupervised clustering
- Data Import & Dataset Manager (CSV upload + schema validation)
- CLI import script for expanded demo and custom CSV
- Active dataset loading (`Auto`, `Imported`, `Sample`)

---

## Dashboard pages

1. `app/pages/1_Job_Market_Overview.py` — Job Market Overview
2. `app/pages/2_Skill_Analysis.py` — Skill Demand Analysis
3. `app/pages/3_CV_Skill_Gap.py` — CV Skill Gap Analyzer
4. `app/pages/4_Project_Recommendations.py` — Project Recommendation Engine
5. `app/pages/5_Role_Clustering.py` — Role Segmentation & Job Clustering
6. `app/pages/6_Data_Import.py` — Data Import & Dataset Manager

---

## Tech stack

- **Language:** Python
- **Data:** Pandas, NumPy
- **ML:** scikit-learn
- **Visualization:** Plotly
- **App:** Streamlit
- **Config/IO:** PyYAML, python-dotenv
- **Testing:** pytest

---

## Architecture overview

```text
Raw/Demo/User CSV Data
        ↓
Schema Validation + Standardization
        ↓
Data Cleaning
        ↓
Skill Extraction + Frequency
        ↓
Processed Datasets
        ↓
Streamlit Analytics Pages (1–6)
```

---

## Job data import

Schema reference:

- `docs/job_data_import_guide.md`

Process expanded synthetic demo data:

- `python scripts/import_jobs_from_csv.py --demo expanded`

Process custom CSV data:

- `python scripts/import_jobs_from_csv.py --input data/raw/my_jobs.csv`

Default imported outputs:

- `data/processed/processed_imported_jobs.csv`
- `data/processed/imported_skill_frequency.csv`
- `reports/generated_reports/import_summary.json`

---

## Local setup

1. Create and activate virtual environment
2. Install dependencies from `requirements.txt`
3. Run health check
4. Optionally import expanded demo data
5. Run test suite
6. Start Streamlit app

---

## Run commands

- `python scripts/run_project_check.py`
- `python scripts/import_jobs_from_csv.py --demo expanded`
- `python -m pytest tests/`
- `python -m streamlit run app/streamlit_app.py`

---

## Deployment notes

- Streamlit config: `.streamlit/config.toml`
- Python runtime pin: `runtime.txt`
- App is compatible with Streamlit Community Cloud
- Uploaded/generated files may be temporary in cloud environments

---

## Testing status

- Current suite status: **99 passed**
- Tests cover cleaning, extraction, recommendations, clustering, and import utilities

---

## Screenshots (placeholders)

Store screenshots in:

- `docs/screenshots/`

Suggested captures:

- Landing page
- Skill analysis heatmap
- CV gap summary
- Project recommendation table
- Clustering scatter view
- Data import validation report

---

## Limitations

- Default data is synthetic unless users import custom CSV
- Skill extraction is rule-based and dictionary-dependent
- Cluster labels are heuristic
- No paid LLM APIs are used
- Outputs are decision-support, not hiring decisions

See also: `docs/limitations.md`

---

## Future improvements

- Additional legal public-data connectors
- Better skill synonym normalization
- Time-based trend tracking on larger datasets
- User profile persistence and progress tracking

---

## Author

- _Your Name Here_ (replace before final portfolio submission)
