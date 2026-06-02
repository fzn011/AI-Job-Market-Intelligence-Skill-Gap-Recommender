# Architecture

## Overview

The system is designed as a layered pipeline where each layer has a single responsibility and passes clean outputs to the next layer.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                         │
│                                                             │
│   Local CSV files  │  Synthetic data  │  (Future: scraper) │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      CLEANING LAYER                         │
│                    src/data_cleaning.py                     │
│                                                             │
│  - Remove duplicates                                        │
│  - Normalise text (lowercase, strip punctuation)           │
│  - Handle missing values                                    │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   NLP SKILL EXTRACTION                      │
│                   src/skill_extraction.py                   │
│                                                             │
│  - Keyword matching vs. skills dictionary                   │
│  - TF-IDF term extraction                                   │
│  - (Future) Semantic matching with sentence-transformers   │
└──────────────────┬──────────────────────────────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
┌──────────────────┐   ┌────────────────────────────────────┐
│  CLUSTERING      │   │         CV INPUT                   │
│  LAYER           │   │         src/cv_analyzer.py         │
│  src/job_        │   │                                    │
│  clustering.py   │   │  - Accept CV text or PDF           │
│                  │   │  - Extract user's current skills   │
│  - KMeans on     │   │  - Return structured skill profile │
│    TF-IDF matrix │   └──────────────┬─────────────────────┘
│  - Group jobs    │                  │
│    by skill type │                  │
└──────────────────┘                  │
          │                           │
          └────────────┬──────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  RECOMMENDATION LAYER                       │
│                src/recommendation_engine.py                 │
│                                                             │
│  - Compare user skills vs. market demand                    │
│  - Rank missing skills by demand frequency                  │
│  - Map skill gaps to recommended portfolio projects         │
│  - (Future) FAISS vector search for semantic similarity    │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     DASHBOARD LAYER                         │
│                    app/streamlit_app.py                     │
│                    app/pages/                               │
│                                                             │
│  Page 1 — Job Market Overview                               │
│  Page 2 — Skill Demand Analysis                             │
│  Page 3 — CV Skill Gap Analyzer                             │
│  Page 4 — Project Recommendation Engine                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer Descriptions

### Data Sources
Raw job postings loaded from CSV files or generated synthetically. The structure is always normalised to the schema defined in `data_dictionary.md` before further processing.

### Cleaning Layer (`src/data_cleaning.py`)
Responsible for all data quality work: removing duplicate postings, handling nulls, and normalising text so downstream NLP is consistent.

### NLP Skill Extraction (`src/skill_extraction.py`)
Extracts structured skill information from unstructured job description text. Uses a skills dictionary for keyword matching and TF-IDF for term importance. Later extended with semantic embeddings.

### Job Clustering (`src/job_clustering.py`)
Groups job postings into role archetypes based on their skill profiles. This allows the system to say "your profile is closest to a Data Analyst cluster, which typically requires X, Y, Z".

### CV Analysis (`src/cv_analyzer.py`)
Mirrors the skill extraction layer but applied to the user's CV or manually entered skill list. Produces a normalised user skill profile in the same format as the market skill profiles.

### Recommendation Engine (`src/recommendation_engine.py`)
The core intelligence layer. Computes the delta between user skills and market demand, ranks missing skills by frequency, and maps them to concrete portfolio project suggestions.

### Dashboard Layer (`app/`)
Streamlit multi-page app that ties everything together in an interactive UI. No business logic lives here — it purely calls `src/` modules and renders results.

---

## Technology Choices

| Component | Technology | Reason |
|---|---|---|
| Data handling | pandas | Industry standard for tabular data |
| NLP vectorisation | scikit-learn TF-IDF | Lightweight, no GPU required |
| Semantic matching | sentence-transformers | State-of-the-art, runs locally, free |
| Vector search | FAISS | Fast similarity search, open-source |
| Clustering | scikit-learn KMeans | Simple, interpretable, no setup cost |
| Dashboard | Streamlit | Fast to build, free deployment tier |
| Config | PyYAML | Human-readable, standard |
