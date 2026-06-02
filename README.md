# AI Job Market Intelligence + Skill Gap Recommender

> Analyze job descriptions, extract in-demand skills, compare them with your profile, and get actionable recommendations — all locally, with open-source tools.

This repository is designed as a professional, GitHub-ready, end-to-end portfolio project for AI/Data Science career intelligence.

---

## At a Glance

- ✅ **Local-first and free**: no paid APIs, no proprietary services required
- ✅ **Production-style structure**: modular `src/`, `app/`, `tests/`, `docs/`, `scripts/`
- ✅ **Validation workflow included**: one command to verify project health and generate processed data
- ✅ **Beginner-friendly code**: clear functions, typed signatures, readable pipeline steps
- ✅ **Deployment-friendly**: ready to move to Streamlit Community Cloud

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Why This Project Matters](#why-this-project-matters)
- [Key Features (Planned)](#key-features-planned)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Folder Structure](#folder-structure)
- [How to Run Locally](#how-to-run-locally)
- [Project Health Check](#project-health-check)
- [Current Dashboard Pages](#current-dashboard-pages)
- [Recommended Local Run Order](#recommended-local-run-order)

---

## Problem Statement

Job seekers in AI and data science face a consistent challenge: they don't know exactly which skills are most in demand right now, or how their current profile compares to the market. Generic advice like "learn Python" is not useful when you already know Python.

This project addresses that by:

- Scraping or loading real/synthetic job postings
- Extracting the actual skills mentioned in those postings
- Clustering jobs by skill profile
- Comparing a user's CV against those clusters
- Recommending the most impactful skills and projects to work on next

---

## Why This Project Matters

- Job descriptions contain structured signal about what the market wants
- NLP and clustering can turn that signal into actionable intelligence
- A skill gap recommender has real personal and commercial value
- This project is a realistic end-to-end data/AI product pipeline

---

## Key Features (Planned)

| Feature | Description |
|---|---|
| Job data ingestion | Load job posts from CSV or scrape open job boards |
| Skill extraction | NLP-based extraction of skills from job descriptions |
| Job clustering | Group jobs by skill profiles using unsupervised ML |
| CV analyzer | Parse a user's CV/profile and identify their current skills |
| Skill gap engine | Compare user profile against market demand |
| Recommendations | Suggest skills and portfolio projects to close the gap |
| Interactive dashboard | Streamlit UI for exploration and personal use |

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.10+ |
| Data handling | Pandas, NumPy |
| NLP | spaCy, NLTK, sentence-transformers |
| Machine learning | scikit-learn (KMeans, TF-IDF) |
| Vector search | FAISS |
| Visualization | Plotly, Matplotlib |
| Dashboard | Streamlit |
| Config | PyYAML, python-dotenv |
| Testing | pytest |
| Storage | CSV / SQLite |

All tools are free and open-source. No paid APIs required.

---

## Project Architecture

```
Job Data (CSV / Web)
        │
        ▼
  Data Cleaning Layer
        │
        ▼
  NLP Skill Extraction  ◄── Skills Dictionary
        │
        ▼
  Job Clustering Layer
        │
  ┌─────┴──────┐
  │            │
  ▼            ▼
CV Input    Market Overview
  │
  ▼
Skill Gap Analysis
  │
  ▼
Recommendation Engine
  │
  ▼
Streamlit Dashboard
```

---

## Folder Structure

```
ai-job-market-intelligence/
│
├── README.md
├── requirements.txt
├── .gitignore
├── config.yaml
│
├── data/
│   ├── raw/              # Raw job data files
│   ├── processed/        # Cleaned and transformed data
│   └── sample/           # Sample datasets and dictionaries
│
├── notebooks/            # Exploration and prototyping notebooks
│
├── src/                  # Core Python modules
│   ├── config.py
│   ├── data_collection.py
│   ├── data_cleaning.py
│   ├── skill_extraction.py
│   ├── job_clustering.py
│   ├── cv_analyzer.py
│   ├── recommendation_engine.py
│   └── utils.py
│
├── app/                  # Streamlit application
│   ├── streamlit_app.py
│   └── pages/
│
├── reports/              # Generated figures and reports
├── tests/                # Unit tests
└── docs/                 # Project documentation
```

---

## How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-job-market-intelligence.git
cd ai-job-market-intelligence

# 2. Create and activate a virtual environment
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run project health check
python scripts/run_project_check.py

# 5. Run tests
python -m pytest tests/

# 6. Run the Streamlit app
streamlit run app/streamlit_app.py
```

---

## Project Health Check

Before opening the dashboard, run:

```bash
python scripts/run_project_check.py
```

This command:

- validates the sample dataset schema
- cleans job descriptions
- extracts skills from descriptions
- saves processed outputs in `data/processed/`
- prepares data used by the Streamlit dashboard

Expected generated files:

- `data/processed/processed_sample_jobs.csv`
- `data/processed/sample_skill_frequency.csv`

Example terminal summary:

```text
Project Health Check
--------------------
Config loaded: Yes
Sample jobs loaded: 10 rows
Required columns present: Yes
Skills dictionary loaded: Yes
Processed jobs saved: data/processed/processed_sample_jobs.csv
Skill frequency saved: data/processed/sample_skill_frequency.csv
Top 10 skills:
1. python - 10
2. sql - 7
...
```

---

## Current Dashboard Pages

### 1. Job Market Overview

The first working dashboard page is available at:

- `app/pages/1_Job_Market_Overview.py`

Current capabilities:

- KPI metrics
- Dataset preview
- Filters (job type, location, company)
- Job-title distribution chart
- Location distribution chart
- Job-type distribution chart
- Skill-count distribution chart
- Top skills chart
- Quick rule-based insights
- Data quality notes

> Before launching Streamlit, run:
>
> `python scripts/run_project_check.py`

### 2. Skill Demand Analysis

The second working dashboard page is available at:

- `app/pages/2_Skill_Analysis.py`

Current capabilities:

- Top skills overall
- Skill categories
- Technical vs soft skill split
- Role-wise skill heatmaps
- Skill co-occurrence
- Common skill combinations
- Downloadable skill table
- Rule-based insights
- Data quality notes

### 3. CV Skill Gap Analyzer

The third working dashboard page is available at:

- `app/pages/3_CV_Skill_Gap.py`

Current capabilities:

- CV/resume text input
- Target role selection
- CV skill extraction
- Role-based market skill comparison
- Match score
- Matched/missing/extra skills
- Learning and project recommendations
- Downloadable skill-gap report
- Rule-based insights

---

## Recommended Local Run Order

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_project_check.py
python -m pytest tests/
streamlit run app/streamlit_app.py
```

---


