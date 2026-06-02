"""Role segmentation and job clustering dashboard page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard_utils import load_processed_jobs  # noqa: E402
from src.job_clustering import (  # noqa: E402
    create_cluster_report_text,
    generate_cluster_insights,
    run_job_clustering_pipeline,
)
from src.ui_theme import apply_global_theme, render_brand_header, style_plotly_figure  # noqa: E402


st.set_page_config(page_title="Role Segmentation + Job Clustering", page_icon="🧠", layout="wide")

apply_global_theme()
render_brand_header(
    app_name="EmberScope AI · Role Segmentation + Job Clustering",
    subtitle="Discover natural role segments in job postings using unsupervised clustering.",
    logo_mark="◜●◝",
)

jobs_df = load_processed_jobs()
if jobs_df.empty:
    st.warning("Processed job data was not found. Please run: python scripts/run_project_check.py")
    st.stop()

st.subheader("Clustering Controls")

with st.sidebar:
    st.markdown("### Filter Jobs")

    if "job_type" in jobs_df.columns:
        job_type_options = sorted(jobs_df["job_type"].dropna().astype(str).str.strip().replace("", pd.NA).dropna().unique().tolist())
    else:
        job_type_options = []

    if "location" in jobs_df.columns:
        location_options = sorted(jobs_df["location"].dropna().astype(str).str.strip().replace("", pd.NA).dropna().unique().tolist())
    else:
        location_options = []

    selected_job_types = st.multiselect("Job Types", options=job_type_options)
    selected_locations = st.multiselect("Locations", options=location_options)

    max_clusters_allowed = max(1, min(8, len(jobs_df)))
    min_clusters_allowed = 2 if max_clusters_allowed >= 2 else 1

    selected_clusters = st.slider(
        "Number of Clusters",
        min_value=min_clusters_allowed,
        max_value=max_clusters_allowed,
        value=min(5, max_clusters_allowed),
    )

    run_clicked = st.button("Run Clustering", type="primary", use_container_width=True)

filtered_df = jobs_df.copy()
if selected_job_types and "job_type" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["job_type"].astype(str).isin(selected_job_types)]
if selected_locations and "location" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["location"].astype(str).isin(selected_locations)]

if filtered_df.empty:
    st.warning("No jobs match the selected filters. Try widening the filters.")
    st.stop()

run_now = run_clicked or "role_cluster_results" not in st.session_state

if run_now:
    try:
        st.session_state["role_cluster_results"] = run_job_clustering_pipeline(
            jobs_df=filtered_df,
            n_clusters=selected_clusters,
            random_state=42,
        )
    except Exception as exc:  # pragma: no cover
        st.error(f"Clustering failed: {exc}")
        st.stop()

results = st.session_state.get("role_cluster_results", {})
clustered_jobs = results.get("clustered_jobs", pd.DataFrame())
cluster_summary = results.get("cluster_summary", pd.DataFrame())
cluster_skills = results.get("cluster_skills", pd.DataFrame())
n_clusters_used = int(results.get("n_clusters_used", 0))

if clustered_jobs.empty or cluster_summary.empty:
    st.warning("No clustering output available for current settings.")
    st.stop()

name_map = dict(zip(cluster_summary["cluster"].tolist(), cluster_summary["cluster_name"].tolist()))
clustered_jobs = clustered_jobs.copy()
clustered_jobs["cluster_name"] = clustered_jobs["cluster"].map(name_map).fillna("General Data / AI Role")

largest_cluster = cluster_summary.sort_values("job_count", ascending=False).iloc[0]
avg_jobs_per_cluster = clustered_jobs.groupby("cluster").size().mean() if n_clusters_used > 0 else 0

st.markdown("---")
metric_cols = st.columns(5)
metric_cols[0].metric("Jobs Clustered", int(len(clustered_jobs)))
metric_cols[1].metric("Clusters Used", n_clusters_used)
metric_cols[2].metric("Largest Cluster", str(largest_cluster["cluster_name"]))
metric_cols[3].metric("Avg Jobs per Cluster", f"{float(avg_jobs_per_cluster):.2f}")
metric_cols[4].metric("Unique Job Titles", int(clustered_jobs["job_title"].nunique()) if "job_title" in clustered_jobs.columns else 0)

st.markdown("---")
st.subheader("Clustered Job Table")
display_columns = [
    "job_title",
    "company",
    "location",
    "job_type",
    "cluster",
    "cluster_name",
]
existing_display_columns = [col for col in display_columns if col in clustered_jobs.columns]
st.dataframe(clustered_jobs[existing_display_columns], use_container_width=True)

st.download_button(
    label="Download Clustered Jobs CSV",
    data=clustered_jobs.to_csv(index=False).encode("utf-8"),
    file_name="clustered_jobs.csv",
    mime="text/csv",
)

st.markdown("---")
st.subheader("Cluster Visualization")
fig_scatter = px.scatter(
    clustered_jobs,
    x="cluster_x",
    y="cluster_y",
    color="cluster_name",
    hover_data=[col for col in ["job_title", "company", "location", "job_type"] if col in clustered_jobs.columns],
    title="2D Cluster Map (SVD Projection)",
)
style_plotly_figure(fig_scatter)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")
st.subheader("Cluster Summary")
st.dataframe(cluster_summary, use_container_width=True)

for _, row in cluster_summary.sort_values("cluster").iterrows():
    cluster_id = int(row["cluster"])
    cluster_name = str(row["cluster_name"])
    with st.expander(f"Cluster {cluster_id} · {cluster_name}"):
        st.markdown(f"**Top terms:** {row['top_terms']}")
        st.markdown(f"**Top skills:** {row['top_skills']}")
        st.markdown(f"**Common job titles:** {row['common_job_titles']}")
        st.markdown(f"**Common job types:** {row['common_job_types']}")
        st.markdown(f"**Common locations:** {row['common_locations']}")

        scoped = clustered_jobs[clustered_jobs["cluster"] == cluster_id]
        detail_cols = [c for c in ["job_title", "company", "location", "job_type"] if c in scoped.columns]
        st.dataframe(scoped[detail_cols], use_container_width=True)

st.markdown("---")
st.subheader("Additional Cluster Analysis")

extra_col_1, extra_col_2 = st.columns(2)

with extra_col_1:
    if "job_type" in clustered_jobs.columns and clustered_jobs["job_type"].notna().any():
        heatmap_df = pd.crosstab(clustered_jobs["cluster_name"], clustered_jobs["job_type"])
        fig_heatmap = px.imshow(
            heatmap_df,
            labels={"x": "Job Type", "y": "Cluster", "color": "Job Count"},
            aspect="auto",
            title="Cluster vs Job Type",
        )
        style_plotly_figure(fig_heatmap)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("Job type heatmap unavailable for this dataset.")

with extra_col_2:
    if not cluster_skills.empty:
        top_skill_rows = (
            cluster_skills.sort_values(["cluster", "frequency"], ascending=[True, False])
            .groupby("cluster", as_index=False)
            .head(5)
            .copy()
        )
        top_skill_rows["cluster_name"] = top_skill_rows["cluster"].map(name_map).fillna(top_skill_rows["cluster"].astype(str))
        fig_skills = px.bar(
            top_skill_rows,
            x="frequency",
            y="skill",
            color="cluster_name",
            orientation="h",
            title="Top Skills by Cluster (Top 5)",
        )
        style_plotly_figure(fig_skills)
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.info("Top skills by cluster are unavailable.")

st.subheader("Job Title Distribution by Cluster")
if "job_title" in clustered_jobs.columns:
    title_dist = (
        clustered_jobs.groupby(["cluster_name", "job_title"]).size().reset_index(name="count")
        .sort_values(["cluster_name", "count", "job_title"], ascending=[True, False, True])
    )
    st.dataframe(title_dist, use_container_width=True)
else:
    st.info("Job title distribution is unavailable.")

st.markdown("---")
st.subheader("Quick Insights")
for insight in generate_cluster_insights(cluster_summary, clustered_jobs):
    st.markdown(f"- {insight}")

report_text = create_cluster_report_text(cluster_summary, clustered_jobs)
st.download_button(
    label="Download Cluster Summary Report",
    data=report_text.encode("utf-8"),
    file_name="cluster_summary_report.txt",
    mime="text/plain",
)

with st.expander("How clustering works"):
    st.markdown("- Text is built from titles, descriptions, and extracted skills.")
    st.markdown("- TF-IDF converts text to vectors.")
    st.markdown("- KMeans groups similar roles into clusters.")
    st.markdown("- 2D SVD projection helps visualize separation.")

with st.expander("How to interpret clusters"):
    st.markdown("- Cluster names are heuristic labels, not official role taxonomies.")
    st.markdown("- Use cluster terms and skills to understand segment themes.")
    st.markdown("- Prioritize clusters aligned with your target role roadmap.")

with st.expander("Limitations"):
    st.markdown("- Results depend on dataset size and quality.")
    st.markdown("- Small sample sizes can produce less stable clusters.")
    st.markdown("- Labels are rule-based and should be treated as guidance.")
