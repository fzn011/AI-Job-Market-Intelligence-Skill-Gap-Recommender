"""Reusable unsupervised job clustering helpers (TF-IDF + KMeans + SVD)."""

from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

from src.dashboard_utils import parse_extracted_skills
from src.utils import clean_text


def prepare_clustering_text(
    df: pd.DataFrame,
    text_columns: list[str] | None = None,
) -> pd.Series:
    """Create clean combined text for each job row used by clustering."""
    if df.empty:
        return pd.Series(dtype="object")

    default_columns = [
        "job_title",
        "job_type",
        "cleaned_description",
        "description",
        "extracted_skills",
    ]
    candidate_columns = text_columns or default_columns
    available_columns = [col for col in candidate_columns if col in df.columns]
    if not available_columns:
        return pd.Series([""] * len(df), index=df.index, dtype="object")

    def combine_row(row: pd.Series) -> str:
        parts: list[str] = []
        for column in available_columns:
            value = row.get(column)
            if column == "extracted_skills":
                skills = parse_extracted_skills(value)
                if skills:
                    parts.append(" ".join(str(skill) for skill in skills))
                continue

            if value is None:
                continue

            text = str(value).strip()
            if text:
                parts.append(text)

        return clean_text(" ".join(parts))

    return df.apply(combine_row, axis=1)


def vectorize_job_texts(
    texts: pd.Series,
    max_features: int = 500,
    ngram_range: tuple = (1, 2),
    min_df: int = 1,
) -> tuple:
    """Convert cleaned text into TF-IDF vectors."""
    if texts is None or len(texts) == 0:
        raise ValueError("No text data available for vectorization.")

    cleaned_texts = [str(text).strip() for text in texts.tolist() if str(text).strip()]
    if not cleaned_texts:
        raise ValueError("No valid non-empty text found for vectorization.")

    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        stop_words="english",
    )
    tfidf_matrix = vectorizer.fit_transform(cleaned_texts)

    if tfidf_matrix.shape[0] == 0 or tfidf_matrix.shape[1] == 0:
        raise ValueError("TF-IDF vectorization produced an empty matrix.")

    return tfidf_matrix, vectorizer


def choose_safe_cluster_count(
    n_samples: int,
    requested_clusters: int = 5,
) -> int:
    """Return a safe cluster count bounded by available samples."""
    if n_samples <= 1:
        return 1

    safe_requested = max(1, int(requested_clusters))
    return min(safe_requested, int(n_samples))


def cluster_jobs_kmeans(
    tfidf_matrix,
    n_clusters: int = 5,
    random_state: int = 42,
) -> tuple:
    """Cluster TF-IDF vectors using KMeans with safe sample handling."""
    n_samples = int(tfidf_matrix.shape[0])
    n_clusters_safe = choose_safe_cluster_count(n_samples, requested_clusters=n_clusters)

    if n_clusters_safe == 1:
        return np.zeros(n_samples, dtype=int), None

    model = KMeans(
        n_clusters=n_clusters_safe,
        random_state=random_state,
        n_init=10,
    )
    labels = model.fit_predict(tfidf_matrix)
    return labels, model


def reduce_clusters_pca(
    tfidf_matrix,
    n_components: int = 2,
    random_state: int = 42,
) -> pd.DataFrame:
    """Reduce sparse TF-IDF vectors to 2D coordinates for plotting."""
    n_samples = int(tfidf_matrix.shape[0])
    if n_samples == 0:
        return pd.DataFrame(columns=["x", "y"])

    if n_samples == 1:
        return pd.DataFrame({"x": [0.0], "y": [0.0]})

    n_features = int(tfidf_matrix.shape[1])
    max_components = max(1, min(n_components, n_samples - 1, n_features))

    svd = TruncatedSVD(n_components=max_components, random_state=random_state)
    reduced = svd.fit_transform(tfidf_matrix)

    if reduced.shape[1] == 1:
        x = reduced[:, 0]
        y = np.zeros_like(x)
    else:
        x = reduced[:, 0]
        y = reduced[:, 1]

    return pd.DataFrame({"x": x, "y": y})


def get_top_terms_per_cluster(
    tfidf_matrix,
    vectorizer,
    labels,
    top_n: int = 8,
) -> dict:
    """Return top TF-IDF terms per cluster by average weight."""
    labels_arr = np.asarray(labels)
    if labels_arr.size == 0:
        return {}

    feature_names = vectorizer.get_feature_names_out()
    if len(feature_names) == 0:
        return {}

    top_terms: dict[int, list[str]] = {}
    unique_clusters = sorted(set(int(label) for label in labels_arr.tolist()))
    for cluster_id in unique_clusters:
        idx = np.where(labels_arr == cluster_id)[0]
        if len(idx) == 0:
            top_terms[int(cluster_id)] = []
            continue

        cluster_matrix = tfidf_matrix[idx]
        mean_scores = np.asarray(cluster_matrix.mean(axis=0)).ravel()
        if mean_scores.size == 0:
            top_terms[int(cluster_id)] = []
            continue

        top_idx = np.argsort(mean_scores)[::-1][:top_n]
        terms = [feature_names[i] for i in top_idx if mean_scores[i] > 0]
        top_terms[int(cluster_id)] = terms

    return top_terms


def infer_cluster_name(
    top_terms: list[str],
    cluster_skills: list[str] | None = None,
) -> str:
    """Infer human-readable cluster name using term/skill keyword rules."""
    tokens = {str(term).strip().lower() for term in (top_terms or []) if str(term).strip()}
    if cluster_skills:
        tokens.update({str(skill).strip().lower() for skill in cluster_skills if str(skill).strip()})

    if not tokens:
        return "General Data / AI Role"

    analyst_bi = {"power bi", "tableau", "excel", "dashboard", "reporting", "stakeholder", "data visualization"}
    scientist_ml = {"machine learning", "scikit-learn", "model", "classification", "regression", "xgboost", "feature engineering"}
    ai_genai = {"rag", "llm", "generative ai", "nlp", "vector database", "transformers", "large language models"}
    data_eng = {"etl", "pipeline", "airflow", "spark", "postgresql", "data engineering", "data warehouse"}
    risk = {"risk", "credit", "fraud", "compliance"}
    product = {"product", "funnel", "experiment", "user", "conversion", "a/b testing"}

    def contains_any(keyword_set: set[str]) -> bool:
        return any(keyword in tokens for keyword in keyword_set)

    if contains_any(analyst_bi):
        return "Data Analyst / BI"
    if contains_any(scientist_ml):
        return "Data Scientist / ML"
    if contains_any(ai_genai):
        return "AI / GenAI"
    if contains_any(data_eng):
        return "Data Engineering"
    if contains_any(risk):
        return "Risk Analytics"
    if contains_any(product):
        return "Product Analytics"

    return "General Data / AI Role"


def summarize_cluster_skills(
    df: pd.DataFrame,
    cluster_col: str = "cluster",
) -> pd.DataFrame:
    """Count extracted skill frequency per cluster."""
    if df.empty or cluster_col not in df.columns or "extracted_skills" not in df.columns:
        return pd.DataFrame(columns=["cluster", "skill", "frequency"])

    rows: list[dict] = []
    for _, row in df.iterrows():
        cluster = row.get(cluster_col)
        skills = parse_extracted_skills(row.get("extracted_skills"))
        for skill in skills:
            normalized = str(skill).strip().lower()
            if normalized:
                rows.append({"cluster": int(cluster), "skill": normalized})

    if not rows:
        return pd.DataFrame(columns=["cluster", "skill", "frequency"])

    skills_df = pd.DataFrame(rows)
    grouped = skills_df.groupby(["cluster", "skill"]).size().reset_index(name="frequency")
    grouped = grouped.sort_values(["cluster", "frequency", "skill"], ascending=[True, False, True]).reset_index(drop=True)
    return grouped


def create_cluster_summary(
    clustered_df: pd.DataFrame,
    top_terms_by_cluster: dict,
    cluster_skills_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Create one summary row per cluster with interpretable fields."""
    columns = [
        "cluster",
        "cluster_name",
        "job_count",
        "top_terms",
        "top_skills",
        "common_job_titles",
        "common_job_types",
        "common_locations",
    ]
    if clustered_df.empty or "cluster" not in clustered_df.columns:
        return pd.DataFrame(columns=columns)

    summary_rows: list[dict] = []
    for cluster_id in sorted(clustered_df["cluster"].dropna().astype(int).unique().tolist()):
        scoped = clustered_df[clustered_df["cluster"] == cluster_id].copy()
        top_terms = top_terms_by_cluster.get(int(cluster_id), [])

        top_skills_list: list[str] = []
        if cluster_skills_df is not None and not cluster_skills_df.empty:
            scoped_skills = cluster_skills_df[cluster_skills_df["cluster"] == cluster_id]
            top_skills_list = scoped_skills.sort_values("frequency", ascending=False).head(5)["skill"].tolist()

        cluster_name = infer_cluster_name(top_terms=top_terms, cluster_skills=top_skills_list)

        def top_values(column_name: str) -> str:
            if column_name not in scoped.columns:
                return "N/A"
            values = (
                scoped[column_name]
                .dropna()
                .astype(str)
                .str.strip()
                .replace("", pd.NA)
                .dropna()
            )
            if values.empty:
                return "N/A"
            return ", ".join(values.value_counts().head(3).index.tolist())

        summary_rows.append(
            {
                "cluster": int(cluster_id),
                "cluster_name": cluster_name,
                "job_count": int(len(scoped)),
                "top_terms": ", ".join(top_terms[:8]) if top_terms else "N/A",
                "top_skills": ", ".join(top_skills_list[:5]) if top_skills_list else "N/A",
                "common_job_titles": top_values("job_title"),
                "common_job_types": top_values("job_type"),
                "common_locations": top_values("location"),
            }
        )

    return pd.DataFrame(summary_rows, columns=columns)


def run_job_clustering_pipeline(
    jobs_df: pd.DataFrame,
    n_clusters: int = 5,
    random_state: int = 42,
) -> dict:
    """Run full clustering pipeline and return clustered data + summaries."""
    empty_payload = {
        "clustered_jobs": pd.DataFrame(),
        "cluster_summary": pd.DataFrame(),
        "cluster_skills": pd.DataFrame(),
        "top_terms_by_cluster": {},
        "n_clusters_used": 0,
    }

    if jobs_df.empty:
        return empty_payload

    working_df = jobs_df.copy(deep=True).reset_index(drop=True)
    prepared_text = prepare_clustering_text(working_df)

    valid_mask = prepared_text.astype(str).str.strip().ne("")
    if not valid_mask.any():
        return empty_payload

    working_df = working_df.loc[valid_mask].reset_index(drop=True)
    prepared_text = prepared_text.loc[valid_mask].reset_index(drop=True)

    tfidf_matrix, vectorizer = vectorize_job_texts(prepared_text)
    safe_clusters = choose_safe_cluster_count(tfidf_matrix.shape[0], requested_clusters=n_clusters)

    labels, _ = cluster_jobs_kmeans(tfidf_matrix, n_clusters=safe_clusters, random_state=random_state)
    reduced_df = reduce_clusters_pca(tfidf_matrix, n_components=2, random_state=random_state)
    top_terms = get_top_terms_per_cluster(tfidf_matrix, vectorizer, labels, top_n=8)

    working_df["cluster"] = np.asarray(labels, dtype=int)
    working_df["cluster_x"] = reduced_df["x"].values
    working_df["cluster_y"] = reduced_df["y"].values

    cluster_skills = summarize_cluster_skills(working_df, cluster_col="cluster")
    cluster_summary = create_cluster_summary(working_df, top_terms_by_cluster=top_terms, cluster_skills_df=cluster_skills)

    return {
        "clustered_jobs": working_df,
        "cluster_summary": cluster_summary,
        "cluster_skills": cluster_skills,
        "top_terms_by_cluster": top_terms,
        "n_clusters_used": int(safe_clusters),
    }


def generate_cluster_insights(
    cluster_summary: pd.DataFrame,
    clustered_jobs: pd.DataFrame,
) -> list[str]:
    """Generate lightweight rule-based insights from clustering outputs."""
    if cluster_summary.empty or clustered_jobs.empty:
        return [
            "No clustering insights available yet. Run clustering with enough filtered job posts.",
        ]

    insights: list[str] = []
    largest = cluster_summary.sort_values("job_count", ascending=False).iloc[0]
    insights.append(
        f"The largest cluster is {largest['cluster_name']} with {int(largest['job_count'])} jobs."
    )

    joined_names = " ".join(cluster_summary["cluster_name"].astype(str).tolist()).lower()
    if "ai / genai" in joined_names:
        insights.append("AI / GenAI roles are separated by terms such as RAG, LLM, and NLP in this sample.")

    if cluster_summary["job_count"].nunique() > 1:
        insights.append("Cluster sizes are uneven, indicating stronger demand concentration in specific role segments.")
    else:
        insights.append("Clusters are balanced in size for the selected filters.")

    if "job_type" in clustered_jobs.columns and clustered_jobs["job_type"].nunique() > 1:
        insights.append("Some clusters overlap on job type, which is expected in hybrid data and AI roles.")

    insights.append("Cluster names are rule-based interpretations of top terms and skills.")
    return insights


def create_cluster_report_text(
    cluster_summary: pd.DataFrame,
    clustered_jobs: pd.DataFrame,
) -> str:
    """Create downloadable plain-text cluster report."""
    total_jobs = int(len(clustered_jobs)) if not clustered_jobs.empty else 0
    total_clusters = int(cluster_summary["cluster"].nunique()) if not cluster_summary.empty else 0

    lines: list[str] = []
    lines.append("Role Segmentation & Job Clustering Report")
    lines.append("=" * 88)
    lines.append(f"Number of jobs clustered: {total_jobs}")
    lines.append(f"Number of clusters: {total_clusters}")
    lines.append("")

    lines.append("Cluster Summary")
    lines.append("-" * 88)

    if cluster_summary.empty:
        lines.append("No cluster summary available.")
    else:
        for _, row in cluster_summary.sort_values("cluster").iterrows():
            lines.append(f"Cluster {int(row['cluster'])}: {row['cluster_name']}")
            lines.append(f"  - Job count: {int(row['job_count'])}")
            lines.append(f"  - Top terms: {row['top_terms']}")
            lines.append(f"  - Top skills: {row['top_skills']}")
            lines.append(f"  - Common job titles: {row['common_job_titles']}")
            lines.append("")

    lines.append("Disclaimer: Cluster labels are rule-based interpretations of unsupervised clustering results.")
    return "\n".join(lines)
