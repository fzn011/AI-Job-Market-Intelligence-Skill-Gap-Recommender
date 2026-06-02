"""Recommendation helpers for skill-gap analysis and portfolio ideas."""


def _normalize_skills(skills: list[str]) -> set[str]:
    return {
        str(skill).strip().lower()
        for skill in skills
        if skill is not None and str(skill).strip()
    }


def compute_skill_gap(user_skills: list[str], market_skills: list[str]) -> dict:
    """
    Compute matched/missing skills and match score.

    Returns
    -------
    dict
        {
          "matched_skills": [...],
          "missing_skills": [...],
          "match_score": 0.0-100.0
        }
    """
    user_set = _normalize_skills(user_skills)
    market_set = _normalize_skills(market_skills)

    matched_skills = sorted(user_set.intersection(market_set))
    missing_skills = sorted(market_set - user_set)

    if not market_set:
        match_score = 0.0
    else:
        match_score = round((len(matched_skills) / len(market_set)) * 100, 2)

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": match_score,
    }


def recommend_projects_for_missing_skills(missing_skills: list[str]) -> list[dict]:
    """Return project ideas mapped from missing skills."""
    skill_map = {
        "sql": {
            "project_idea": "Build an end-to-end SQL analytics project with KPI dashboards from a transactional dataset.",
            "difficulty": "Beginner",
        },
        "power bi": {
            "project_idea": "Create an interactive Power BI dashboard for sales and customer cohort analysis.",
            "difficulty": "Beginner",
        },
        "machine learning": {
            "project_idea": "Build a churn prediction pipeline with feature engineering, model evaluation, and explainability.",
            "difficulty": "Intermediate",
        },
        "scikit-learn": {
            "project_idea": "Implement and compare multiple scikit-learn classifiers on a real tabular dataset.",
            "difficulty": "Intermediate",
        },
        "xgboost": {
            "project_idea": "Train and tune an XGBoost model for credit risk scoring with cross-validation.",
            "difficulty": "Intermediate",
        },
        "docker": {
            "project_idea": "Containerize a machine learning inference API and run it locally with Docker Compose.",
            "difficulty": "Intermediate",
        },
        "fastapi": {
            "project_idea": "Develop a FastAPI service that exposes prediction endpoints for a trained ML model.",
            "difficulty": "Intermediate",
        },
        "streamlit": {
            "project_idea": "Create a Streamlit dashboard for model predictions, metrics, and user feedback capture.",
            "difficulty": "Beginner",
        },
        "mlflow": {
            "project_idea": "Track experiments and model versions using MLflow in a reproducible training workflow.",
            "difficulty": "Intermediate",
        },
        "rag": {
            "project_idea": "Build a document question-answering system using open-source embeddings and FAISS.",
            "difficulty": "Intermediate",
        },
        "llm": {
            "project_idea": "Create an LLM-powered assistant that summarizes job descriptions and extracts required skills.",
            "difficulty": "Intermediate",
        },
        "nlp": {
            "project_idea": "Build an NLP pipeline for skill extraction, keyword ranking, and text classification.",
            "difficulty": "Intermediate",
        },
        "pytorch": {
            "project_idea": "Train a PyTorch text classifier and compare it against classical ML baselines.",
            "difficulty": "Advanced",
        },
        "tensorflow": {
            "project_idea": "Develop and deploy a TensorFlow model for image or text classification.",
            "difficulty": "Advanced",
        },
        "aws": {
            "project_idea": "Deploy a lightweight ML API on AWS with automated logging and monitoring.",
            "difficulty": "Advanced",
        },
        "azure": {
            "project_idea": "Build an Azure-based data pipeline and deploy a scored model endpoint.",
            "difficulty": "Advanced",
        },
        "gcp": {
            "project_idea": "Create a GCP pipeline using BigQuery + Vertex AI style workflow for model serving.",
            "difficulty": "Advanced",
        },
    }

    recommendations: list[dict] = []
    normalized_missing = sorted(_normalize_skills(missing_skills))
    for skill in normalized_missing:
        mapping = skill_map.get(skill)
        if mapping:
            recommendations.append(
                {
                    "skill": skill,
                    "project_idea": mapping["project_idea"],
                    "difficulty": mapping["difficulty"],
                }
            )
        else:
            recommendations.append(
                {
                    "skill": skill,
                    "project_idea": (
                        f"Build a focused mini-project that demonstrates practical use of '{skill}' "
                        "in a real data workflow."
                    ),
                    "difficulty": "Intermediate",
                }
            )

    return recommendations


def recommend_projects() -> str:
    """Placeholder for legacy compatibility."""
    return "Recommendation engine module is ready."


def recommend_skills() -> str:
    """Placeholder for legacy compatibility."""
    return "Skill recommendation: not yet implemented."
