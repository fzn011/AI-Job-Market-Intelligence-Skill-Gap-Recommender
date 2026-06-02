# Demo Recording Checklist (2–3 minutes)

## 1) Before recording
- Close unrelated apps/tabs and notifications.
- Set browser zoom for readability.
- Prepare one short CV sample text for page 3.
- Ensure demo outputs are generated before opening app.
- Keep terminal ready for command evidence screenshots.

## 2) Terminal commands to run first
- `python scripts/run_project_check.py`
- `python scripts/import_jobs_from_csv.py --demo expanded`
- `python scripts/final_project_audit.py`
- `python -m pytest tests/`
- `python -m streamlit run app/streamlit_app.py`

## 3) Demo sequence
1. Landing page + project status
2. Dataset source selector (`Auto/Imported/Sample`)
3. Page 1: Job Market Overview
4. Page 2: Skill Demand Analysis
5. Page 3: CV Skill Gap Analyzer
6. Page 4: Project Recommendation Engine
7. Page 5: Role Segmentation & Job Clustering
8. Page 6: Data Import & Dataset Manager
9. Close with README and repository structure

## 4) What to say on each page
- **Landing:** “This is a 6-page Streamlit product for AI/Data career intelligence.”
- **Dataset selector:** “The app can use sample or imported processed datasets.”
- **Page 1:** “This summarizes role, location, and skill demand at a glance.”
- **Page 2:** “This analyzes top skills, categories, and co-occurrence patterns.”
- **Page 3:** “This compares CV skills to market demand for selected roles.”
- **Page 4:** “This ranks portfolio project ideas by skill coverage.”
- **Page 5:** “This segments roles via TF-IDF + KMeans clustering.”
- **Page 6:** “This validates and processes custom CSV input safely.”
- **Closing:** “Everything is local-first, tested, and deployment-ready.”

## 5) Mistakes to avoid
- Don’t claim default data is real job-board data.
- Don’t overstate model sophistication.
- Don’t skip showing tests/audit evidence.
- Don’t rush charts so labels become unreadable.
- Don’t leave private tabs visible during recording.

## 6) Final checklist before upload
- Video length between 2–3 minutes
- Audio clear and concise
- Key pages visible
- Test and audit outputs captured
- Links ready: GitHub, live demo, LinkedIn post
