# Portfolio Summary

## Elevator Pitch
AI Job Market Intelligence + Skill Gap Recommender is an end-to-end data/AI application that converts job-posting text into actionable career strategy using local, free, open-source tooling.

## Core Features
- Job market overview dashboard
- Skill demand analysis with category/co-occurrence insights
- CV skill-gap analysis against market demand
- Project recommendation engine for portfolio planning
- Role segmentation using unsupervised clustering
- Data import manager for custom CSV workflows

## Skills Demonstrated
- Data ingestion and schema validation
- Data cleaning and NLP-style rule-based extraction
- Unsupervised ML (TF-IDF + KMeans + SVD)
- Feature engineering and reporting
- Streamlit product design and UX consistency
- Testing and modular Python architecture

## Business Value
- Clarifies skill priorities for job seekers
- Helps target projects with higher market relevance
- Supports custom local data workflows without paid APIs

## Tech Stack
Python, Streamlit, Pandas, NumPy, scikit-learn, Plotly, PyYAML, pytest

## Why this is stronger than typical notebook projects
- Multi-page application architecture
- Reusable utility modules
- Automated health check and import scripts
- Explicit schema and validation layer
- Test coverage for core logic

## Limitations
- Default data is synthetic unless user imports custom data
- Skill extraction is rule-based and dictionary-dependent
- Cluster labels are heuristic interpretations
- Streamlit cloud file writes can be temporary

## Future Improvements
- Time-series trend analysis on larger datasets
- Better synonym/entity normalization for skills
- Optional API connectors for legal open datasets
- User profile persistence and progress tracking
