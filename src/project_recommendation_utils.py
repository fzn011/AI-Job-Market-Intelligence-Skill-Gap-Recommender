"""Reusable helpers for project recommendation and roadmap generation."""

from __future__ import annotations

from ast import literal_eval
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
import textwrap

import pandas as pd

from src.cv_gap_utils import get_market_skills_by_target_role
from src.dashboard_utils import parse_extracted_skills


TARGET_ROLES = [
    "Overall Market",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "BI Analyst",
    "Data Engineer",
    "GenAI Engineer",
    "Risk Data Analyst",
    "Product Data Analyst",
    "Junior Data Scientist",
]


def normalize_selected_skills(skills: list[str] | None) -> list[str]:
    """Normalize selected skills into a sorted unique lowercase list."""
    if not skills:
        return []

    cleaned = {
        str(skill).strip().lower()
        for skill in skills
        if skill is not None and str(skill).strip()
    }
    return sorted(cleaned)


def get_available_skills_from_market(
    jobs_df: pd.DataFrame,
    top_n: int | None = None,
) -> list[str]:
    """Extract available market skills from processed jobs by frequency."""
    if jobs_df.empty or "extracted_skills" not in jobs_df.columns:
        return []

    counter: Counter[str] = Counter()
    for value in jobs_df["extracted_skills"]:
        parsed = parse_extracted_skills(value)
        normalized = normalize_selected_skills(parsed)
        counter.update(normalized)

    if not counter:
        return []

    ordered = [skill for skill, _ in sorted(counter.items(), key=lambda row: (-row[1], row[0]))]
    if top_n is None:
        return ordered

    return ordered[: max(0, int(top_n))]


def get_role_based_skill_options(
    jobs_df: pd.DataFrame,
    target_role: str,
    top_n: int = 25,
) -> list[str]:
    """Return role-based skill options with fallback to overall market skills."""
    role_skills = get_market_skills_by_target_role(
        jobs_df=jobs_df,
        target_role=target_role,
        top_n=top_n,
    )
    role_skills = normalize_selected_skills(role_skills)

    if role_skills:
        return role_skills

    fallback_skills = get_available_skills_from_market(jobs_df=jobs_df, top_n=top_n)
    return normalize_selected_skills(fallback_skills)


def get_project_template_catalog() -> list[dict]:
    """Return a local built-in portfolio project template catalog."""
    return [
        {
            "project_id": "P001",
            "title": "AI Job Market Intelligence Dashboard",
            "description": "Build an end-to-end analytics app that ingests job descriptions, extracts skills, and visualizes market demand patterns.",
            "project_type": "Analytics Dashboard",
            "difficulty": "Intermediate",
            "estimated_timeline": "2-3 weeks",
            "core_skills": ["python", "pandas", "sql", "data visualization", "streamlit", "nlp"],
            "tech_stack": ["python", "pandas", "plotly", "streamlit", "sql"],
            "deliverables": ["interactive dashboard", "cleaned dataset", "skill frequency report", "deployment-ready app"],
            "portfolio_value": "Shows full-cycle analytics + product thinking.",
            "business_context": "Used by career teams to identify in-demand skills and trends.",
            "github_readme_sections": ["Problem", "Dataset", "Method", "Dashboard", "Results", "How to Run"],
        },
        {
            "project_id": "P002",
            "title": "Customer Churn Prediction System",
            "description": "Predict churn risk with robust feature engineering, model evaluation, and explainability artifacts.",
            "project_type": "Machine Learning",
            "difficulty": "Intermediate",
            "estimated_timeline": "2-4 weeks",
            "core_skills": ["python", "pandas", "machine learning", "scikit-learn", "classification", "data visualization"],
            "tech_stack": ["python", "pandas", "scikit-learn", "plotly"],
            "deliverables": ["trained model", "model comparison notebook", "evaluation report", "prediction app"],
            "portfolio_value": "Demonstrates ML fundamentals with business impact framing.",
            "business_context": "Helps subscription businesses retain high-risk customers.",
            "github_readme_sections": ["Business Objective", "Data", "Modeling", "Metrics", "Insights", "Next Steps"],
        },
        {
            "project_id": "P003",
            "title": "Credit Risk Scoring Dashboard",
            "description": "Develop a risk scoring workflow and dashboard for credit approval support.",
            "project_type": "Risk Analytics",
            "difficulty": "Intermediate",
            "estimated_timeline": "3 weeks",
            "core_skills": ["python", "sql", "machine learning", "classification", "xgboost", "streamlit"],
            "tech_stack": ["python", "xgboost", "sql", "streamlit", "plotly"],
            "deliverables": ["risk scoring pipeline", "streamlit dashboard", "model documentation", "threshold policy notes"],
            "portfolio_value": "Strong evidence of finance-ready analytical problem solving.",
            "business_context": "Supports risk teams in reducing default rates.",
            "github_readme_sections": ["Use Case", "Data Prep", "Model", "Risk Policy", "Dashboard", "Deployment"],
        },
        {
            "project_id": "P004",
            "title": "Document Intelligence RAG Validator",
            "description": "Create a RAG workflow that retrieves context from documents and validates response quality.",
            "project_type": "GenAI Application",
            "difficulty": "Advanced",
            "estimated_timeline": "3-5 weeks",
            "core_skills": ["python", "nlp", "rag", "llm", "vector database", "streamlit"],
            "tech_stack": ["python", "streamlit", "faiss", "rag", "llm"],
            "deliverables": ["ingestion pipeline", "retrieval module", "quality evaluation sheet", "demo interface"],
            "portfolio_value": "Highlights practical GenAI engineering beyond prompt demos.",
            "business_context": "Useful for enterprise document search and Q&A reliability checks.",
            "github_readme_sections": ["Architecture", "Retrieval Strategy", "Evaluation", "Demo", "Limitations", "Roadmap"],
        },
        {
            "project_id": "P005",
            "title": "Sales Analytics BI Dashboard",
            "description": "Build executive-ready BI dashboards for revenue trends, cohorts, and regional performance.",
            "project_type": "Business Intelligence",
            "difficulty": "Beginner",
            "estimated_timeline": "1-2 weeks",
            "core_skills": ["sql", "power bi", "excel", "data visualization", "stakeholder management"],
            "tech_stack": ["sql", "power bi", "excel"],
            "deliverables": ["power bi file", "kpi dictionary", "stakeholder walkthrough", "insight summary"],
            "portfolio_value": "Shows communication of insights to business stakeholders.",
            "business_context": "Supports sales teams in pipeline and target monitoring.",
            "github_readme_sections": ["Business Questions", "KPIs", "Dashboard Tour", "Insights", "Recommendations"],
        },
        {
            "project_id": "P006",
            "title": "End-to-End ML API with FastAPI",
            "description": "Serve ML predictions through a production-style API with validation and containerization.",
            "project_type": "ML Engineering",
            "difficulty": "Intermediate",
            "estimated_timeline": "2-3 weeks",
            "core_skills": ["python", "machine learning", "fastapi", "docker", "model deployment"],
            "tech_stack": ["python", "fastapi", "docker", "pydantic"],
            "deliverables": ["trained model", "api endpoints", "docker image", "postman collection"],
            "portfolio_value": "Demonstrates engineering maturity beyond notebooks.",
            "business_context": "Allows product teams to integrate predictive models into apps.",
            "github_readme_sections": ["API Design", "Model Serving", "Docker", "Testing", "Usage"],
        },
        {
            "project_id": "P007",
            "title": "MLOps Experiment Tracking Project",
            "description": "Build reproducible model experiments with tracking, versioning, and deployment notes.",
            "project_type": "MLOps",
            "difficulty": "Intermediate",
            "estimated_timeline": "2-3 weeks",
            "core_skills": ["python", "mlflow", "scikit-learn", "model deployment", "docker"],
            "tech_stack": ["python", "mlflow", "scikit-learn", "docker"],
            "deliverables": ["experiment tracking setup", "model registry sample", "reproducible training script", "ops checklist"],
            "portfolio_value": "Signals production readiness and lifecycle thinking.",
            "business_context": "Improves reliability and traceability in ML workflows.",
            "github_readme_sections": ["Experiment Setup", "Tracking", "Registry", "Reproducibility", "Operations"],
        },
        {
            "project_id": "P008",
            "title": "Data Pipeline and ETL Automation",
            "description": "Design automated ETL jobs to clean, transform, and store analytics-ready data.",
            "project_type": "Data Engineering",
            "difficulty": "Intermediate",
            "estimated_timeline": "2-4 weeks",
            "core_skills": ["python", "sql", "etl", "data pipeline", "postgresql"],
            "tech_stack": ["python", "sql", "postgresql", "airflow"],
            "deliverables": ["etl scripts", "data model", "scheduler config", "data quality checks"],
            "portfolio_value": "Strong proof of backend data reliability skills.",
            "business_context": "Feeds downstream BI and ML systems with trusted data.",
            "github_readme_sections": ["Pipeline Design", "Data Model", "Orchestration", "Quality Checks", "Monitoring"],
        },
        {
            "project_id": "P009",
            "title": "NLP Resume Skill Extractor",
            "description": "Build an NLP-based skill extractor for resumes with confidence and category outputs.",
            "project_type": "NLP Application",
            "difficulty": "Intermediate",
            "estimated_timeline": "2-3 weeks",
            "core_skills": ["python", "nlp", "machine learning", "scikit-learn", "streamlit"],
            "tech_stack": ["python", "scikit-learn", "streamlit", "nltk"],
            "deliverables": ["text preprocessing pipeline", "extractor model", "interactive app", "error analysis"],
            "portfolio_value": "Showcases NLP pipeline design with user-facing experience.",
            "business_context": "Useful for HR-tech profile analysis workflows.",
            "github_readme_sections": ["NLP Pipeline", "Model", "App Demo", "Validation", "Limitations"],
        },
        {
            "project_id": "P010",
            "title": "Computer Vision Defect Detection Demo",
            "description": "Train a CV model for defect detection and expose visual predictions with confidence scores.",
            "project_type": "Computer Vision",
            "difficulty": "Advanced",
            "estimated_timeline": "4-6 weeks",
            "core_skills": ["python", "computer vision", "deep learning", "pytorch", "tensorflow"],
            "tech_stack": ["python", "pytorch", "tensorflow", "opencv"],
            "deliverables": ["training pipeline", "inference notebook", "visual defect demo", "model comparison"],
            "portfolio_value": "Demonstrates advanced model development depth.",
            "business_context": "Supports quality assurance in manufacturing environments.",
            "github_readme_sections": ["Dataset", "Model Architecture", "Training", "Inference", "Results", "Future Work"],
        },
        {
            "project_id": "P011",
            "title": "Product Analytics Funnel Dashboard",
            "description": "Build funnel and retention analytics to identify user drop-off and growth opportunities.",
            "project_type": "Product Analytics",
            "difficulty": "Beginner",
            "estimated_timeline": "1-2 weeks",
            "core_skills": ["python", "sql", "pandas", "data visualization", "product analytics"],
            "tech_stack": ["python", "sql", "pandas", "plotly"],
            "deliverables": ["funnel dashboard", "retention cohort analysis", "kpi definitions", "growth recommendations"],
            "portfolio_value": "Signals business + product impact orientation.",
            "business_context": "Helps product teams improve conversion and activation.",
            "github_readme_sections": ["Metrics Framework", "Funnel", "Cohorts", "Insights", "Action Plan"],
        },
        {
            "project_id": "P012",
            "title": "GenAI Knowledge Base Assistant",
            "description": "Create a role-focused assistant over internal knowledge docs with retrieval and grounding checks.",
            "project_type": "GenAI Application",
            "difficulty": "Advanced",
            "estimated_timeline": "3-5 weeks",
            "core_skills": ["python", "rag", "llm", "nlp", "vector database", "streamlit"],
            "tech_stack": ["python", "streamlit", "faiss", "transformers"],
            "deliverables": ["knowledge ingestion", "retrieval app", "prompt evaluation report", "demo workflow"],
            "portfolio_value": "High market relevance for modern AI engineering roles.",
            "business_context": "Reduces search time in support and knowledge-heavy teams.",
            "github_readme_sections": ["System Design", "Knowledge Indexing", "Prompting", "Evaluation", "Demo"],
        },
        {
            "project_id": "P013",
            "title": "Time Series Forecasting Dashboard",
            "description": "Forecast demand or revenue with time-series features and visualize uncertainty bands.",
            "project_type": "Forecasting",
            "difficulty": "Intermediate",
            "estimated_timeline": "2-3 weeks",
            "core_skills": ["python", "pandas", "machine learning", "time series", "data visualization"],
            "tech_stack": ["python", "pandas", "statsmodels", "plotly"],
            "deliverables": ["forecast pipeline", "model backtest", "interactive forecast dashboard", "business recommendation memo"],
            "portfolio_value": "Adds forecasting competency often requested in analytics roles.",
            "business_context": "Supports planning and inventory/resource decisions.",
            "github_readme_sections": ["Forecast Objective", "Features", "Backtesting", "Dashboard", "Decisions"],
        },
        {
            "project_id": "P014",
            "title": "Fraud Detection Analytics System",
            "description": "Develop a fraud detection workflow with class imbalance strategies and alert logic.",
            "project_type": "Risk Analytics",
            "difficulty": "Advanced",
            "estimated_timeline": "3-5 weeks",
            "core_skills": ["python", "sql", "machine learning", "classification", "anomaly detection"],
            "tech_stack": ["python", "sql", "scikit-learn", "xgboost"],
            "deliverables": ["fraud model", "alert thresholds", "risk dashboard", "model monitoring notes"],
            "portfolio_value": "Shows handling of complex, high-impact modeling problems.",
            "business_context": "Reduces financial losses in payment and banking systems.",
            "github_readme_sections": ["Risk Context", "Data Imbalance", "Modeling", "Alerting", "Monitoring"],
        },
        {
            "project_id": "P015",
            "title": "Cloud-Ready Data App Deployment",
            "description": "Package and deploy a data app with containerization, API integration, and CI-friendly workflows.",
            "project_type": "Deployment Engineering",
            "difficulty": "Intermediate",
            "estimated_timeline": "2-3 weeks",
            "core_skills": ["docker", "streamlit", "fastapi", "github", "model deployment"],
            "tech_stack": ["docker", "streamlit", "fastapi", "github actions"],
            "deliverables": ["deployable app", "docker setup", "ci workflow", "deployment guide"],
            "portfolio_value": "Strong hiring signal for real-world delivery readiness.",
            "business_context": "Bridges analytics prototypes into production-ready assets.",
            "github_readme_sections": ["Deployment Architecture", "Container Setup", "CI/CD", "Runbook", "Demo"],
        },
    ]


def _to_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip().lower() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                parsed = literal_eval(stripped)
                if isinstance(parsed, list):
                    return [str(item).strip().lower() for item in parsed if str(item).strip()]
            except (ValueError, SyntaxError):
                pass
        if stripped:
            return [part.strip().lower() for part in stripped.split(",") if part.strip()]
    return []


def score_project_against_skills(
    project: dict,
    selected_skills: list[str],
) -> dict:
    """Score one project template against selected skills."""
    normalized_selected = normalize_selected_skills(selected_skills)
    project_core = _to_list(project.get("core_skills", []))
    project_stack = _to_list(project.get("tech_stack", []))
    project_skill_bank = set(project_core + project_stack)

    matched = sorted(skill for skill in normalized_selected if skill in project_skill_bank)
    missing = sorted(skill for skill in normalized_selected if skill not in project_skill_bank)

    selected_count = len(normalized_selected)
    matched_count = len(matched)
    coverage_score = round((matched_count / selected_count) * 100, 2) if selected_count else 0.0

    scored = dict(project)
    scored.update(
        {
            "matched_skills": matched,
            "missing_selected_skills": missing,
            "coverage_score": coverage_score,
            "matched_skill_count": matched_count,
            "selected_skill_count": selected_count,
        }
    )
    return scored


def get_difficulty_order(difficulty: str) -> int:
    """Return sortable order for difficulty labels."""
    mapping = {"beginner": 1, "intermediate": 2, "advanced": 3}
    return mapping.get(str(difficulty).strip().lower(), 99)


def recommend_projects(
    selected_skills: list[str],
    max_projects: int = 8,
    difficulty_filter: list[str] | None = None,
    project_type_filter: list[str] | None = None,
) -> pd.DataFrame:
    """Recommend projects ranked by skill coverage and relevance."""
    templates = get_project_template_catalog()
    normalized_selected = normalize_selected_skills(selected_skills)

    scored_rows = [score_project_against_skills(project, normalized_selected) for project in templates]
    df = pd.DataFrame(scored_rows)
    if df.empty:
        return pd.DataFrame(
            columns=[
                "project_id",
                "title",
                "project_type",
                "difficulty",
                "estimated_timeline",
                "coverage_score",
                "matched_skill_count",
                "selected_skill_count",
                "matched_skills",
                "missing_selected_skills",
                "core_skills",
                "tech_stack",
                "deliverables",
                "portfolio_value",
                "business_context",
                "description",
            ]
        )

    if difficulty_filter:
        allowed_difficulty = {str(item).strip().lower() for item in difficulty_filter if str(item).strip()}
        df = df[df["difficulty"].astype(str).str.lower().isin(allowed_difficulty)].copy()

    if project_type_filter:
        allowed_types = {str(item).strip().lower() for item in project_type_filter if str(item).strip()}
        df = df[df["project_type"].astype(str).str.lower().isin(allowed_types)].copy()

    if df.empty:
        return pd.DataFrame(
            columns=[
                "project_id",
                "title",
                "project_type",
                "difficulty",
                "estimated_timeline",
                "coverage_score",
                "matched_skill_count",
                "selected_skill_count",
                "matched_skills",
                "missing_selected_skills",
                "core_skills",
                "tech_stack",
                "deliverables",
                "portfolio_value",
                "business_context",
                "description",
            ]
        )

    df["difficulty_order"] = df["difficulty"].apply(get_difficulty_order)
    df = df.sort_values(
        by=["coverage_score", "matched_skill_count", "difficulty_order"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

    df = df.head(max(0, int(max_projects))).copy()

    output_columns = [
        "project_id",
        "title",
        "project_type",
        "difficulty",
        "estimated_timeline",
        "coverage_score",
        "matched_skill_count",
        "selected_skill_count",
        "matched_skills",
        "missing_selected_skills",
        "core_skills",
        "tech_stack",
        "deliverables",
        "portfolio_value",
        "business_context",
        "description",
        "github_readme_sections",
    ]

    return df[output_columns]


def build_project_skill_matrix(
    recommendations_df: pd.DataFrame,
    selected_skills: list[str],
) -> pd.DataFrame:
    """Build project x skill binary coverage matrix."""
    normalized_selected = normalize_selected_skills(selected_skills)
    if recommendations_df.empty or not normalized_selected:
        return pd.DataFrame()

    matrix_rows: list[dict] = []
    for _, row in recommendations_df.iterrows():
        title = str(row.get("title", "Untitled Project"))
        covered = set(_to_list(row.get("core_skills", [])) + _to_list(row.get("tech_stack", [])))

        row_record = {"project_title": title}
        for skill in normalized_selected:
            row_record[skill] = 1 if skill in covered else 0
        matrix_rows.append(row_record)

    if not matrix_rows:
        return pd.DataFrame()

    matrix_df = pd.DataFrame(matrix_rows).set_index("project_title")
    return matrix_df


def summarize_project_coverage(
    recommendations_df: pd.DataFrame,
    selected_skills: list[str],
) -> dict:
    """Summarize recommendation quality and uncovered skill gaps."""
    normalized_selected = normalize_selected_skills(selected_skills)

    if recommendations_df.empty:
        return {
            "recommended_projects": 0,
            "selected_skills": len(normalized_selected),
            "best_project": "N/A",
            "best_coverage_score": 0.0,
            "skills_covered_by_any_project": 0,
            "skills_not_covered_by_any_project": normalized_selected,
        }

    best_row = recommendations_df.sort_values("coverage_score", ascending=False).iloc[0]
    covered_any: set[str] = set()
    for value in recommendations_df["matched_skills"]:
        covered_any.update(_to_list(value))

    not_covered = sorted(skill for skill in normalized_selected if skill not in covered_any)

    return {
        "recommended_projects": int(len(recommendations_df)),
        "selected_skills": len(normalized_selected),
        "best_project": str(best_row.get("title", "N/A")),
        "best_coverage_score": float(best_row.get("coverage_score", 0.0)),
        "skills_covered_by_any_project": len([skill for skill in normalized_selected if skill in covered_any]),
        "skills_not_covered_by_any_project": not_covered,
    }


def generate_project_recommendation_insights(
    recommendations_df: pd.DataFrame,
    selected_skills: list[str],
) -> list[str]:
    """Generate rule-based recommendation insights without LLM usage."""
    normalized_selected = normalize_selected_skills(selected_skills)
    if recommendations_df.empty:
        return [
            "No projects were recommended for the current filters. Try selecting more skills or relaxing filters.",
        ]

    insights: list[str] = []
    top_row = recommendations_df.sort_values("coverage_score", ascending=False).iloc[0]
    insights.append(
        f"The strongest project match is {top_row['title']}, covering {int(top_row['matched_skill_count'])} selected skills."
    )

    difficulty_counts = recommendations_df["difficulty"].astype(str).value_counts()
    if not difficulty_counts.empty:
        dominant_difficulty = str(difficulty_counts.index[0])
        insights.append(f"Your selected skills are mostly covered by {dominant_difficulty}-level projects.")

    joined_text = " ".join(
        [
            " ".join(_to_list(row.get("tech_stack", [])) + _to_list(row.get("core_skills", [])))
            for _, row in recommendations_df.iterrows()
        ]
    )
    if "docker" in joined_text and "fastapi" in joined_text:
        insights.append("Docker and FastAPI appear in production-focused project recommendations.")

    project_types = recommendations_df["project_type"].astype(str).str.lower().tolist()
    if any("dashboard" in pt or "analytics" in pt for pt in project_types) and any(
        "deployment" in pt or "mlops" in pt or "engineering" in pt for pt in project_types
    ):
        insights.append("Build one dashboard project and one deployment-focused project to show both analytics and engineering ability.")

    summary = summarize_project_coverage(recommendations_df, normalized_selected)
    missing_any = summary["skills_not_covered_by_any_project"]
    if missing_any:
        insights.append(
            f"These selected skills are not fully covered yet: {', '.join(missing_any[:5])}. Consider adding a custom capstone project."
        )

    return insights


def _suggested_build_order(recommendations_df: pd.DataFrame) -> list[pd.Series]:
    if recommendations_df.empty:
        return []

    ranked = recommendations_df.sort_values(
        ["coverage_score", "matched_skill_count"],
        ascending=[False, False],
    ).reset_index(drop=True)

    selected_indexes: list[int] = []

    # 1) Highest coverage project first
    selected_indexes.append(int(ranked.index[0]))

    # 2) Then production/deployment project
    deployment_mask = ranked.apply(
        lambda row: (
            "deployment" in str(row.get("project_type", "")).lower()
            or "mlops" in str(row.get("project_type", "")).lower()
            or "docker" in " ".join(_to_list(row.get("core_skills", [])) + _to_list(row.get("tech_stack", [])))
            or "fastapi" in " ".join(_to_list(row.get("core_skills", [])) + _to_list(row.get("tech_stack", [])))
        ),
        axis=1,
    )
    deployment_candidates = ranked[deployment_mask].index.tolist()
    for idx in deployment_candidates:
        if int(idx) not in selected_indexes:
            selected_indexes.append(int(idx))
            break

    # 3) Then advanced AI/ML project if available
    advanced_ai_mask = ranked.apply(
        lambda row: (
            str(row.get("difficulty", "")).lower() == "advanced"
            or any(
                token in " ".join(_to_list(row.get("core_skills", [])) + _to_list(row.get("tech_stack", [])))
                for token in ["llm", "rag", "deep learning", "pytorch", "tensorflow", "machine learning"]
            )
        ),
        axis=1,
    )
    advanced_candidates = ranked[advanced_ai_mask].index.tolist()
    for idx in advanced_candidates:
        if int(idx) not in selected_indexes:
            selected_indexes.append(int(idx))
            break

    # Fill remainder in sorted order
    for idx in ranked.index.tolist():
        if int(idx) not in selected_indexes:
            selected_indexes.append(int(idx))

    return [ranked.loc[idx] for idx in selected_indexes]


def create_project_roadmap_text(
    target_role: str,
    selected_skills: list[str],
    recommendations_df: pd.DataFrame,
) -> str:
    """Create a plain-text downloadable project roadmap."""
    normalized_selected = normalize_selected_skills(selected_skills)
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    source_hint = Path(__file__).name

    lines: list[str] = []
    lines.append("Project Recommendation Roadmap")
    lines.append("=" * 88)
    lines.append(f"Generated at: {generated_at}")
    lines.append(f"Target Role: {target_role}")
    lines.append(f"Selected Skills ({len(normalized_selected)}): {', '.join(normalized_selected) if normalized_selected else 'None'}")
    lines.append("")

    ordered_rows = _suggested_build_order(recommendations_df)
    lines.append("Suggested Build Order:")
    lines.append("1) Highest coverage project first")
    lines.append("2) Then production/deployment project")
    lines.append("3) Then advanced AI/ML project if available")
    lines.append("")

    if not ordered_rows:
        lines.append("No projects available for the current selection.")
    else:
        for idx, row in enumerate(ordered_rows, start=1):
            title = str(row.get("title", "Untitled Project"))
            difficulty = str(row.get("difficulty", "Unknown"))
            timeline = str(row.get("estimated_timeline", "N/A"))
            matched = ", ".join(_to_list(row.get("matched_skills", []))) or "None"
            tech_stack = ", ".join(_to_list(row.get("tech_stack", []))) or "N/A"
            deliverables = ", ".join(_to_list(row.get("deliverables", []))) or "N/A"
            readme_sections = ", ".join(_to_list(row.get("github_readme_sections", []))) or "N/A"
            description = str(row.get("description", ""))

            lines.append(f"{idx}. {title}")
            lines.append(f"   - Difficulty: {difficulty}")
            lines.append(f"   - Estimated Timeline: {timeline}")
            lines.append(f"   - Skills Covered: {matched}")
            lines.append(f"   - Tech Stack: {tech_stack}")
            lines.append(f"   - Key Deliverables: {deliverables}")
            lines.append(f"   - Suggested GitHub README Sections: {readme_sections}")
            lines.append(f"   - Project Scope: {textwrap.fill(description, width=84, subsequent_indent='     ')}")
            lines.append("")

    lines.append("Final Note:")
    lines.append(
        "This roadmap is generated using a local rule-based recommendation system and does not use paid AI APIs."
    )
    lines.append(f"(generated by {source_hint})")

    return "\n".join(lines)


def get_project_type_distribution(
    recommendations_df: pd.DataFrame,
) -> pd.DataFrame:
    """Return project type distribution."""
    if recommendations_df.empty or "project_type" not in recommendations_df.columns:
        return pd.DataFrame(columns=["project_type", "count"])

    dist = recommendations_df["project_type"].astype(str).value_counts().reset_index()
    dist.columns = ["project_type", "count"]
    return dist


def get_difficulty_distribution(
    recommendations_df: pd.DataFrame,
) -> pd.DataFrame:
    """Return difficulty distribution with canonical ordering."""
    if recommendations_df.empty or "difficulty" not in recommendations_df.columns:
        return pd.DataFrame(columns=["difficulty", "count"])

    dist = recommendations_df["difficulty"].astype(str).value_counts().reset_index()
    dist.columns = ["difficulty", "count"]
    dist["order"] = dist["difficulty"].apply(get_difficulty_order)
    dist = dist.sort_values(["order", "difficulty"]).drop(columns=["order"]).reset_index(drop=True)
    return dist
