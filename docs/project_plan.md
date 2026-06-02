# Project Plan

## Objective

Build a local, open-source data science tool that:
1. Analyses AI and data job descriptions to identify in-demand skills
2. Compares those skills against a user's CV or profile
3. Recommends specific skills and portfolio projects to close the gap

The end product is an interactive Streamlit dashboard deployable to Streamlit Community Cloud.

---

## Target Users

| User | Need |
|---|---|
| Job seekers in AI/Data | Understand what skills the market actually wants |
| Junior data scientists | Know what to learn next and what projects to build |
| Career switchers | Benchmark current skills against job market requirements |
| Students | Build a portfolio that is aligned with real hiring demand |

---

## Core Workflow

```
Load job data
      ↓
Clean and preprocess text
      ↓
Extract skills (keyword matching + NLP)
      ↓
Cluster jobs by skill profile
      ↓
User inputs their CV / skill list
      ↓
Compare user profile vs. market
      ↓
Generate skill gap report
      ↓
Recommend portfolio projects
      ↓
Display on Streamlit dashboard
```

---

## MVP Features

- Load synthetic or CSV-based job postings
- Clean and normalise job descriptions
- Extract skills using keyword matching against a skills dictionary
- Display top skills by frequency in the dataset
- Accept user skill list (manual input)
- Show basic skill gap: skills the user is missing
- Streamlit app with at least one functional page

---

## Advanced Features (Post-MVP)

- Semantic skill matching using sentence-transformers
- PDF CV upload and automatic skill parsing
- Job clustering with KMeans (group jobs into role clusters)
- Skill trend tracking over time
- Project recommendations mapped to specific skill gaps
- Vector similarity search using FAISS
- Exportable PDF skill gap report
- Live job scraping from public sources

---

## Success Criteria

| Criterion | Target |
|---|---|
| Project runs fully locally | No paid APIs or external services required |
| Streamlit app is deployable | Runs on Streamlit Community Cloud |
| Skill extraction accuracy | Correctly identifies ≥80% of skills from sample descriptions |
| Code quality | Passes all unit tests in tests/ |
| Portfolio quality | Clean README, modular code, documented structure |
| Reproducibility | Any user can clone and run with pip install -r requirements.txt |
