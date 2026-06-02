# Recruiter One-Pager

## Project Title
AI Job Market Intelligence + Skill Gap Recommender

## One-line Summary
A 6-page Streamlit application that transforms job-posting text into practical career guidance through skill extraction, CV gap analysis, project recommendations, and role clustering.

## Problem Solved
AI/Data job seekers often receive generic advice and lack a structured, evidence-based way to prioritize learning and portfolio projects.

## What the App Does
- Analyzes job-posting trends and skill demand
- Compares CV skills against role-relevant market skills
- Recommends portfolio projects to close skill gaps
- Segments roles with unsupervised clustering
- Supports custom CSV import via a safe schema-first pipeline

## Core Features
- Job Market Overview
- Skill Demand Analysis
- CV Skill Gap Analyzer
- Project Recommendation Engine
- Role Segmentation & Job Clustering (TF-IDF + KMeans)
- Data Import & Dataset Manager

## Technical Skills Demonstrated
- Python application architecture (modular `src/`, `app/`, `scripts/`, `tests/`)
- Data ingestion and schema validation
- Data cleaning and feature extraction
- Rule-based NLP-style matching
- Unsupervised machine learning
- Interactive data visualization in Streamlit/Plotly
- Automated testing and quality checks

## Data/AI Methods Used
- Text normalization and dictionary-based skill extraction
- Skill frequency and co-occurrence analysis
- CV-to-market skill gap logic
- Recommendation scoring against selected skills
- TF-IDF vectorization, KMeans clustering, SVD projection

## Engineering Practices Demonstrated
- Reusable utility modules
- CLI automation scripts (`run_project_check`, import pipeline, final audit)
- Unit tests (99 passing)
- Dataset source control (`Auto`, `Imported`, `Sample`)
- Deployment readiness files for Streamlit Community Cloud

## Business Value
- Helps candidates decide what to learn next
- Improves project selection for stronger portfolios
- Enables transparent, local-first experimentation without paid APIs

## Demo Flow (2 minutes)
1. Show market overview and trend signals
2. Show skill analysis charts and co-occurrence
3. Run CV gap analysis and missing-skill output
4. Generate project recommendations
5. Show role clustering segments
6. Show CSV import and validation workflow

## Limitations (Honest)
- Default dataset is synthetic demo data unless custom CSV is imported
- Skill extraction is rule-based and dictionary-dependent
- Cluster names are heuristic labels
- Outputs are decision-support, not hiring decisions

## Suggested Interview Talking Points
- Why synthetic-first + import-ready was chosen
- How schema validation improves reliability
- Why rule-based extraction was used before LLMs
- How clustering is implemented and interpreted
- How testing and audit scripts improved delivery quality
