# CareerCompass: Job Market Intelligence & Skill Gap Analyzer

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![scikit--learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikitlearn&logoColor=white)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

A local-first, open-source career intelligence platform that turns job-posting text and curated role profiles into practical guidance: market trends, skill gaps, project recommendations, and career actions.

This project started as a Data/AI job-market analyzer and has been extended into a broader **CareerCompass** platform.

---

## Project pitch

CareerCompass helps job seekers understand demand, assess profile alignment, and decide what to build or learn next — using transparent, free, and reproducible workflows.

## Problem statement

Job seekers often receive generic advice, but need role-specific guidance on which skills to prioritize and what actions to take next.

## Why this project matters

- Converts job text into structured skill signals
- Maps current profile skills vs market demand or curated role profiles
- Recommends portfolio projects and broader career actions
- Supports safe, legal CSV import without paid APIs
- Works even without job data via Career Explorer

---

## Universal Career Support

The app supports **12 career categories** with curated skill taxonomies and role profiles:

- Data & AI
- Software & IT
- Banking & Finance
- Business & Administration
- Marketing & Sales
- Design & Creative
- Education & Teaching
- Healthcare
- Engineering
- Customer Support
- Operations & Project Management
- General Entry-Level Jobs

Users can choose either:

1. **Data-driven analysis** using imported or sample job posts
2. **Career category guidance** using curated role profiles (no job data required)

Career category guidance is rule-based and transparent. No paid AI APIs are used.

---

## Current features

- Job data cleaning and validation pipeline
- Rule-based skill extraction from descriptions with **skill synonym engine** (JS→javascript, PowerBI→power bi)
- Job market overview analytics with **skill demand time-series trends**
- Skill demand and co-occurrence analysis
- CV skill gap analysis (market mode + career category mode + **regional profiles**)
- **Job Match Dashboard** — paste job description + CV for instant fit score
- **Career Toolkit** — progress tracker, multi-CV comparison, interview prep, resume bullets, badges
- Project recommendation engine + career action planner
- Career Explorer for role browsing without job data
- **Learning resource links** for missing skills (free courses/docs)
- **PDF career report export**
- **Public data connectors** (USAJobs with demo fallback)
- **Multilingual UI** (English + Bengali)
- **Career Intelligence Hub** — company prep (Google, bKash, Grameenphone), salary estimator, LinkedIn optimizer, peer benchmark, voice interview simulator, ICS study calendar, semantic skill matching
- **Weekly email progress digest** (optional SMTP)
- **USAJobs live connector** (via `.streamlit/secrets.toml` — see `secrets.example.toml`)
- Role segmentation with unsupervised clustering
- Data Import & Dataset Manager (CSV upload + schema validation)
- Multi-category skill taxonomies and role profiles
- CLI import script for expanded demo and custom CSV
- Active dataset loading (`Auto`, `Imported`, `Sample`)

---

## Dashboard pages

1. `app/pages/1_Job_Market_Overview.py` — Job Market Overview
2. `app/pages/2_Skill_Analysis.py` — Skill Demand Analysis
3. `app/pages/3_CV_Skill_Gap.py` — CV Skill Gap Analyzer
4. `app/pages/4_Project_Recommendations.py` — Project & Career Action Recommendations
5. `app/pages/5_Role_Clustering.py` — Role Segmentation & Job Clustering
6. `app/pages/6_Data_Import.py` — Data Import & Dataset Manager
7. `app/pages/7_Career_Explorer.py` — Career Explorer
8. `app/pages/8_Job_Match_Dashboard.py` — Job Match Dashboard
9. `app/pages/9_Career_Toolkit.py` — Career Toolkit (progress, badges, interview, resume)
10. `app/pages/10_Career_Intelligence_Hub.py` — Career Intelligence Hub

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
Raw/Demo/User CSV Data          Career Taxonomies + Role Profiles
        ↓                                      ↓
Schema Validation + Standardization    Category Skill Matching
        ↓                                      ↓
Data Cleaning                          CV Gap + Career Actions
        ↓                                      ↓
Skill Extraction + Frequency           Career Explorer
        ↓
Processed Datasets
        ↓
Streamlit Analytics Pages (1–7)
```

---

## Job data import

Schema reference:

- `docs/job_data_import_guide.md`

Process expanded synthetic demo data:

- `python3 scripts/import_jobs_from_csv.py --demo expanded`

Process custom CSV data:

- `python3 scripts/import_jobs_from_csv.py --input data/raw/my_jobs.csv`

Default imported outputs:

- `data/processed/processed_imported_jobs.csv`
- `data/processed/imported_skill_frequency.csv`
- `reports/generated_reports/import_summary.json`

---

## Local setup

### Windows (one command)

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # first time only
cd "E:\Projects\AI Job Market Intelligence + Skill Gap Recommender\ai-job-market-intelligence"
git fetch origin main
git reset --hard origin/main
.\setup.ps1 -RunApp
```

After the first successful setup, launch anytime with:

```powershell
.\run_app.ps1
```

This creates `.venv`, installs dependencies, generates career data, runs health checks, verifies imports, and optionally launches Streamlit.

If setup fails on heavy packages (torch / sentence-transformers), use:

```powershell
.\setup.ps1 -SkipHeavyPackages -RunApp
```

To force-sync the repo from GitHub before setup:

```powershell
.\setup.ps1 -RepairRepo
.\setup.ps1 -RunApp
```

#### Windows troubleshooting

**`setup.ps1` not found** or **`generate_career_taxonomies.py` not found**  
Your folder is still on an old commit. `git pull` probably failed because of local edits. Fix it like this:

```powershell
cd "E:\Projects\AI Job Market Intelligence + Skill Gap Recommender\ai-job-market-intelligence"

# See what is blocking the update
git status

# Recommended: discard local edits and match GitHub main exactly
git fetch origin main
git reset --hard origin/main

# Or, keep your edits in a stash instead of deleting them
# git stash push -u -m "backup before CareerCompass upgrade"
# git pull origin main

# Confirm the new files exist
dir setup.ps1
dir scripts\generate_career_taxonomies.py

# Run setup
.\setup.ps1 -RunApp
```

**`git pull` says "Your local changes would be overwritten"**  
You have uncommitted edits in files like `app/streamlit_app.py` or `.streamlit/config.toml`. Use `git reset --hard origin/main` (above) or `git stash` before pulling.

**`python -m venv .venv` fails while venv is active**  
Do not recreate the venv manually if `.venv` already exists. Either run `.\setup.ps1` (it reuses the existing venv) or deactivate first: `deactivate`, delete `.venv`, then recreate.

**App starts but looks like the old version (no CareerCompass pages)**  
Check `git log -1 --oneline`. You should see a recent merge including `setup.ps1`. If not, run the reset + pull steps above.

**`ImportError: cannot import name 'APP_NAME' from 'src.ui_theme'`**  
Your `src/ui_theme.py` is still the old file, or Python is using stale cache from before the upgrade.

```powershell
git fetch origin main
git checkout origin/main -- src/ui_theme.py app/streamlit_app.py
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
.\.venv\Scripts\Activate.ps1
python -c "from src.ui_theme import APP_NAME; print(APP_NAME)"
python -m streamlit run app/streamlit_app.py
```

You should see `CareerCompass` printed. If `Select-String src\ui_theme.py APP_NAME` returns nothing, the file was not updated — run `git reset --hard origin/main`.

### Manual setup (all platforms)

1. Create and activate virtual environment
2. Install dependencies from `requirements.txt`
3. Generate data: `python scripts/generate_career_taxonomies.py` (and advanced/premium scripts)
4. Run health check
5. Optionally import expanded demo data
6. Start Streamlit app

---

## Run commands

- `python3 scripts/run_project_check.py`
- `python3 scripts/import_jobs_from_csv.py --demo expanded`
- `python3 scripts/final_project_audit.py`
- `python3 -m pytest tests/`
- `python3 -m streamlit run app/streamlit_app.py`

---

## Deployment notes

- Streamlit config: `.streamlit/config.toml`
- Python runtime pin: `runtime.txt`
- App is compatible with Streamlit Community Cloud
- Uploaded/generated files may be temporary in cloud environments

---

## Testing status

- Tests cover cleaning, extraction, recommendations, clustering, import utilities, and career taxonomies
- Run: `python3 -m pytest tests/`

---

## Limitations

- Default job data is synthetic unless users import custom CSV
- Curated role profiles are simplified; expectations vary by country, company, and seniority
- Skill extraction is rule-based and dictionary-dependent
- Cluster labels are heuristic
- No paid LLM APIs are used
- Outputs are decision-support, not hiring guarantees

See also: `docs/limitations.md`

---

## Future improvements

- Additional legal public-data connectors
- Better skill synonym normalization
- Time-based trend tracking on larger datasets
- User profile persistence and progress tracking
- Localized role profiles by region

---

## Portfolio & Demo Materials

- Recruiter one-pager: `docs/recruiter_one_pager.md`
- Demo script: `docs/demo/demo_script.md`
- Demo recording checklist: `docs/demo/demo_recording_checklist.md`
- LinkedIn launch post draft: `docs/demo/linkedin_launch_post.md`
- GitHub project description assets: `docs/demo/github_project_description.md`
- Resume bullet options: `docs/demo/resume_bullets.md`
- Interview talking points: `docs/demo/interview_talking_points.md`
- Portfolio website section copy: `docs/demo/portfolio_website_section.md`
- Screenshot checklist: `docs/screenshots/screenshot_checklist.md`

---

## Author

- _Your Name Here_ (replace before final portfolio submission)
