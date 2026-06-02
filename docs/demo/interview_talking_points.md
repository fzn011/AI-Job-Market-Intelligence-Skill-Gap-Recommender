# Interview Talking Points

## 1) 30-second explanation
I built a 6-page Streamlit application that turns job-posting text into practical career guidance. It includes market overview analytics, skill demand patterns, CV skill-gap analysis, project recommendations, role clustering using TF-IDF + KMeans, and a schema-based CSV import pipeline.

## 2) 90-second explanation
The project solves a common problem for AI/Data job seekers: deciding what skills to prioritize and what projects to build. I implemented a modular pipeline that cleans job data, extracts skills with a transparent dictionary-based approach, computes skill demand signals, and powers multiple product features. The app includes CV gap diagnostics, recommendation logic, and unsupervised role clustering for segmentation. I also added safe ingestion through CSV schema validation, packaging for Streamlit deployment, and 99 passing tests for reliability.

## 3) Technical architecture explanation
- `src/`: reusable domain modules (cleaning, extraction, recommendations, clustering, dashboard/data collection utilities)
- `app/`: Streamlit entrypoint + 6 pages
- `scripts/`: health check, import pipeline, final audit
- `tests/`: unit tests across core modules
- `docs/`: recruiter/demo/portfolio packaging assets

## 4) Why this is better than a notebook
- Multi-page user-facing product rather than isolated analysis cells
- Reusable modules and scripts
- Input validation and predictable workflows
- Automated tests and deployment readiness

## 5) Data pipeline explanation
Input CSV → schema validation → standardization/deduplication → text cleaning → skill extraction → processed outputs and skill-frequency tables.

## 6) Skill extraction explanation
Rule-based matching against a curated skill dictionary after text normalization. It is interpretable, deterministic, and easy to validate.

## 7) CV gap analyzer explanation
Extracts skills from pasted CV text, compares against role-filtered market skills, computes match score, and identifies missing skills with recommendations.

## 8) Recommendation engine explanation
Scores predefined project templates against selected/role-based skills and ranks projects by coverage with roadmap-style outputs.

## 9) Role clustering explanation
Uses TF-IDF vectors of job text, applies KMeans for segmentation, and uses SVD to visualize clusters in 2D. Cluster names are heuristic labels derived from top terms/skills.

## 10) Testing explanation
The project includes unit tests across core modules, and the latest run shows 99 passing tests.

## 11) Limitations explanation
Default data is synthetic unless users import custom CSVs. Extraction is rule-based, clustering labels are heuristic, and outputs are decision-support only.

## 12) Future improvements
Add legal public-data connectors, improve skill synonym/entity normalization, introduce trend analysis over larger time windows, and add user progress persistence.

## 13) Interview questions and concise answers

### Q1. Why did you build this project?
To solve the gap between generic career advice and data-backed, role-specific skill planning.

### Q2. What data did you use?
A synthetic demo dataset by default plus support for user-imported CSV data.

### Q3. Why synthetic data?
It keeps the project safe, reproducible, and legally clean while still demonstrating end-to-end capability.

### Q4. How does skill extraction work?
It normalizes text and matches against a curated skills dictionary using rule-based logic.

### Q5. Why rule-based extraction instead of an LLM?
Rule-based extraction is transparent, deterministic, low-cost, and easy to test for an MVP.

### Q6. How does clustering work?
TF-IDF vectorization of job text, KMeans for clustering, and SVD for 2D visualization.

### Q7. How do you evaluate the project quality?
Through functional outputs, reproducible scripts, and a comprehensive test suite (99 passing).

### Q8. What are the main limitations?
Synthetic default data, dictionary coverage limits, and heuristic cluster labels.

### Q9. How would you scale it?
Add robust data sources, improve normalization/entity handling, cache processing, and add persistent storage.

### Q10. How would you add real job data safely?
Use legal public datasets/APIs, respect terms of service, and keep schema validation strict.

### Q11. What would you improve next?
Time-series insights, stronger ontology for skills, and personalized progress tracking.

### Q12. What part are you most proud of?
Turning a full data/ML workflow into a tested, user-facing product with practical career outputs.
