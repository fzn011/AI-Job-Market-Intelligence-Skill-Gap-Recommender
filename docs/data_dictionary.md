# Data Dictionary

## File: `data/sample/sample_jobs.csv`

This file contains synthetic job postings used for development and testing.
All entries are fictional and do not represent real companies or individuals.

---

### Schema

| Column | Data Type | Description | Example |
|---|---|---|---|
| `job_id` | Integer | Unique identifier for each job posting | `1` |
| `job_title` | String | Job title as it would appear in a posting | `Data Scientist` |
| `company` | String | Fictional company name | `Meridian AI` |
| `location` | String | Job location, including work arrangement | `London (Hybrid)` |
| `job_type` | String | Employment type | `Full-time`, `Contract` |
| `description` | String | Full job description text including requirements | `We are looking for...` |
| `date_posted` | Date (YYYY-MM-DD) | Date the job was posted | `2024-11-01` |
| `source` | String | Origin of the data | `synthetic` |

---

### Notes

- `job_id` is the primary key. No two rows should share the same `job_id`.
- `description` is the primary field used for NLP skill extraction.
- `location` may contain work arrangement information (e.g., Hybrid, Remote, On-site).
- `source` will be extended when real scraping sources are added (e.g., `indeed`, `linkedin`).
- All `source` values in the sample dataset are set to `synthetic`.

---

## File: `data/sample/skills_dictionary.json`

A structured vocabulary of skills used for keyword-based extraction from job descriptions.

### Schema

```json
{
  "<category_name>": ["skill_1", "skill_2", ...]
}
```

### Categories

| Category Key | Description |
|---|---|
| `programming_languages` | General-purpose programming languages |
| `data_analysis` | Tools and libraries for data wrangling and BI |
| `machine_learning` | Classical ML frameworks, algorithms, and techniques |
| `deep_learning_ai` | Neural networks, LLMs, GenAI, and NLP |
| `data_engineering` | ETL, pipelines, databases, and orchestration tools |
| `mlops_deployment` | Model deployment, versioning, and CI/CD tools |
| `cloud_tools` | Cloud platforms and managed services |
| `soft_skills` | Interpersonal and professional competencies |

### Usage Notes

- All skill strings are stored in **lowercase** to match normalised text.
- Skill phrases with spaces (e.g., `"machine learning"`) are supported.
- This dictionary is the ground truth for keyword matching in `src/skill_extraction.py`.
- New skills and categories can be added by editing the JSON file directly.

---

## Processed Data (Future)

Once the pipeline is fully implemented, the following files will appear in `data/processed/`:

| File | Description |
|---|---|
| `jobs_cleaned.csv` | Deduplicated, text-normalised job postings |
| `jobs_with_skills.csv` | Cleaned jobs with extracted skill columns appended |
| `jobs_clustered.csv` | Jobs with cluster label assigned |
| `skill_frequency.csv` | Skill name → count across all job postings |
