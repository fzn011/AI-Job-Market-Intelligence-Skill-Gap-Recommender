"""Unit tests for job clustering utilities."""

import pandas as pd
import pytest

from src.job_clustering import (
    choose_safe_cluster_count,
    cluster_jobs_kmeans,
    create_cluster_report_text,
    create_cluster_summary,
    generate_cluster_insights,
    get_top_terms_per_cluster,
    infer_cluster_name,
    prepare_clustering_text,
    reduce_clusters_pca,
    run_job_clustering_pipeline,
    summarize_cluster_skills,
    vectorize_job_texts,
)


def sample_jobs_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "job_id": [1, 2, 3, 4, 5, 6],
            "job_title": [
                "data analyst",
                "bi analyst",
                "data scientist",
                "machine learning engineer",
                "ai engineer",
                "data engineer",
            ],
            "company": ["a", "b", "c", "d", "e", "f"],
            "location": ["london", "manchester", "remote", "london", "remote", "edinburgh"],
            "job_type": ["full-time", "full-time", "full-time", "contract", "contract", "full-time"],
            "description": [
                "Build BI dashboards with SQL and Excel.",
                "Power BI reporting and stakeholder communication.",
                "Python model training and feature engineering.",
                "MLOps, Docker, model deployment and monitoring.",
                "RAG pipelines, LLM applications, NLP tasks.",
                "ETL pipelines, Airflow orchestration, warehouse work.",
            ],
            "cleaned_description": [
                "build bi dashboards with sql and excel",
                "power bi reporting and stakeholder communication",
                "python model training and feature engineering",
                "mlops docker model deployment and monitoring",
                "rag pipelines llm applications nlp tasks",
                "etl pipelines airflow orchestration warehouse work",
            ],
            "extracted_skills": [
                "['sql', 'excel', 'power bi']",
                "['power bi', 'communication']",
                "['python', 'scikit-learn', 'feature engineering']",
                "['docker', 'mlflow', 'model deployment']",
                "['rag', 'llm', 'nlp']",
                "['etl', 'airflow', 'data warehouse']",
            ],
        }
    )


def test_prepare_clustering_text_creates_non_empty_series():
    df = sample_jobs_df()
    texts = prepare_clustering_text(df)

    assert isinstance(texts, pd.Series)
    assert len(texts) == len(df)
    assert texts.astype(str).str.len().min() > 0


def test_vectorize_job_texts_returns_matrix_and_vectorizer():
    texts = prepare_clustering_text(sample_jobs_df())
    matrix, vectorizer = vectorize_job_texts(texts, max_features=200)

    assert matrix.shape[0] == len(texts)
    assert matrix.shape[1] > 0
    assert len(vectorizer.get_feature_names_out()) > 0


def test_vectorize_job_texts_raises_for_empty_input():
    with pytest.raises(ValueError):
        vectorize_job_texts(pd.Series(["", " ", "\n"]))


def test_choose_safe_cluster_count_respects_bounds():
    assert choose_safe_cluster_count(10, requested_clusters=5) == 5
    assert choose_safe_cluster_count(3, requested_clusters=8) == 3
    assert choose_safe_cluster_count(1, requested_clusters=5) == 1


def test_cluster_jobs_kmeans_returns_label_per_sample():
    texts = prepare_clustering_text(sample_jobs_df())
    matrix, _ = vectorize_job_texts(texts)

    labels, model = cluster_jobs_kmeans(matrix, n_clusters=4, random_state=42)

    assert len(labels) == matrix.shape[0]
    assert len(set(labels.tolist())) <= 4
    assert model is not None


def test_reduce_clusters_pca_returns_two_columns():
    texts = prepare_clustering_text(sample_jobs_df())
    matrix, _ = vectorize_job_texts(texts)

    reduced = reduce_clusters_pca(matrix)

    assert isinstance(reduced, pd.DataFrame)
    assert list(reduced.columns) == ["x", "y"]
    assert len(reduced) == matrix.shape[0]


def test_get_top_terms_per_cluster_returns_expected_structure():
    texts = prepare_clustering_text(sample_jobs_df())
    matrix, vectorizer = vectorize_job_texts(texts)
    labels, _ = cluster_jobs_kmeans(matrix, n_clusters=3, random_state=42)

    terms = get_top_terms_per_cluster(matrix, vectorizer, labels, top_n=5)

    assert isinstance(terms, dict)
    assert len(terms) > 0
    for value in terms.values():
        assert isinstance(value, list)


def test_summarize_cluster_skills_returns_frequency_table():
    df = sample_jobs_df().copy()
    df["cluster"] = [0, 0, 1, 1, 2, 2]

    skills_df = summarize_cluster_skills(df)

    assert set(skills_df.columns) == {"cluster", "skill", "frequency"}
    assert not skills_df.empty


def test_infer_cluster_name_returns_heuristic_label():
    assert infer_cluster_name(["power bi", "dashboard"], ["excel", "sql"]) == "Data Analyst / BI"
    assert infer_cluster_name(["rag", "llm"], ["nlp"]) == "AI / GenAI"


def test_create_cluster_summary_includes_required_columns():
    pipeline = run_job_clustering_pipeline(sample_jobs_df(), n_clusters=3, random_state=42)

    summary = create_cluster_summary(
        clustered_df=pipeline["clustered_jobs"],
        top_terms_by_cluster=pipeline["top_terms_by_cluster"],
        cluster_skills_df=pipeline["cluster_skills"],
    )

    required = {
        "cluster",
        "cluster_name",
        "job_count",
        "top_terms",
        "top_skills",
        "common_job_titles",
        "common_job_types",
        "common_locations",
    }
    assert required.issubset(summary.columns)
    assert not summary.empty


def test_run_job_clustering_pipeline_returns_expected_payload():
    payload = run_job_clustering_pipeline(sample_jobs_df(), n_clusters=4, random_state=42)

    assert set(payload.keys()) == {
        "clustered_jobs",
        "cluster_summary",
        "cluster_skills",
        "top_terms_by_cluster",
        "n_clusters_used",
    }
    assert not payload["clustered_jobs"].empty
    assert not payload["cluster_summary"].empty
    assert payload["n_clusters_used"] >= 1


def test_generate_cluster_insights_and_report_text_have_core_content():
    payload = run_job_clustering_pipeline(sample_jobs_df(), n_clusters=3, random_state=42)

    insights = generate_cluster_insights(payload["cluster_summary"], payload["clustered_jobs"])
    report = create_cluster_report_text(payload["cluster_summary"], payload["clustered_jobs"])

    assert isinstance(insights, list)
    assert len(insights) > 0
    assert isinstance(report, str)
    assert "Number of jobs clustered" in report
    assert "Disclaimer" in report
