"""Skill Demand Analysis dashboard page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard_utils import (  # noqa: E402
    get_active_dataset_label,
    load_active_jobs_dataset,
    load_processed_jobs,
    load_skill_frequency,
)
from src.skill_analysis_utils import (  # noqa: E402
    build_skill_category_lookup,
    explode_skills_dataframe,
    generate_skill_insights,
    get_skill_analysis_metrics,
    get_skill_category_distribution,
    get_skill_cooccurrence,
    get_skills_by_group,
    get_technical_vs_soft_split,
    get_top_skill_combinations,
    get_top_skills,
    load_skill_dictionary_for_analysis,
)
from src.ui_theme import apply_global_theme, render_brand_header, style_plotly_figure  # noqa: E402
from src.timeseries_utils import build_skill_timeseries, get_timeseries_summary  # noqa: E402


st.set_page_config(page_title="Skill Demand Analysis", page_icon="🔬", layout="wide")

apply_global_theme()

render_brand_header(
    app_name="CareerCompass · Skill Demand Analysis",
    subtitle="Discover which skills dominate the market and how they connect by role.",
    logo_mark="◜●◝",
)

dataset_pref = st.sidebar.selectbox(
    "Dataset source",
    options=["Auto", "Imported", "Sample"],
    key="page2_dataset_source",
)
pref_value = dataset_pref.strip().lower()

jobs_df = load_active_jobs_dataset(preferred=pref_value)
if jobs_df.empty and pref_value != "auto":
    st.info(
        "Selected dataset was not found. Falling back to auto-detection. "
        "Use Data Import page or CLI import to create imported outputs."
    )
    jobs_df = load_processed_jobs()

st.caption(f"Active dataset: {get_active_dataset_label(preferred=pref_value)}")

skill_freq_df = load_skill_frequency()
skill_dict = load_skill_dictionary_for_analysis()
category_lookup = build_skill_category_lookup(skill_dict)

if jobs_df.empty:
    st.warning(
        "Processed job data was not found. Please run: `python scripts/run_project_check.py`"
    )
    st.stop()

total_jobs = len(jobs_df)
filtered_jobs_df = jobs_df.copy()


def get_filter_options(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df.columns:
        return []
    return sorted(
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
        .tolist()
    )


def apply_multiselect_filter(df: pd.DataFrame, column: str, selected: list[str]) -> pd.DataFrame:
    if selected:
        return df[df[column].astype(str).isin(selected)].copy()
    return df


with st.container():
    st.subheader("Explore Filters")
    filter_col_1, filter_col_2 = st.columns(2)
    filter_col_3, filter_col_4 = st.columns(2)

    with filter_col_1:
        selected_job_type = st.multiselect("Job Type", options=get_filter_options(filtered_jobs_df, "job_type"))
    with filter_col_2:
        selected_job_title = st.multiselect("Job Title", options=get_filter_options(filtered_jobs_df, "job_title"))
    with filter_col_3:
        selected_location = st.multiselect("Location", options=get_filter_options(filtered_jobs_df, "location"))
    with filter_col_4:
        selected_company = st.multiselect("Company", options=get_filter_options(filtered_jobs_df, "company"))


filtered_jobs_df = apply_multiselect_filter(filtered_jobs_df, "job_type", selected_job_type)
filtered_jobs_df = apply_multiselect_filter(filtered_jobs_df, "job_title", selected_job_title)
filtered_jobs_df = apply_multiselect_filter(filtered_jobs_df, "location", selected_location)
filtered_jobs_df = apply_multiselect_filter(filtered_jobs_df, "company", selected_company)

st.write(f"Showing **{len(filtered_jobs_df)}** of **{total_jobs}** jobs after filters")

skill_df = explode_skills_dataframe(filtered_jobs_df, category_lookup=category_lookup)

if skill_df.empty:
    st.warning(
        "No extracted skills were found. Please check the skill extraction pipeline."
    )
    st.stop()

metrics = get_skill_analysis_metrics(skill_df, filtered_jobs_df)

metric_cols = st.columns(6)
metric_cols[0].metric("Total Skill Mentions", metrics["total_skill_mentions"])
metric_cols[1].metric("Unique Skills", metrics["unique_skills"])
metric_cols[2].metric("Average Skills / Job", metrics["avg_skills_per_job"])
metric_cols[3].metric("Top Skill", metrics["top_skill"])
metric_cols[4].metric("Top Skill Frequency", metrics["top_skill_frequency"])
metric_cols[5].metric("Top Skill Category", metrics["top_category"])

st.markdown("---")

top_skills_df = get_top_skills(skill_df, top_n=20)
category_df = get_skill_category_distribution(skill_df)
split_df = get_technical_vs_soft_split(skill_df)

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Top Skills Overall")
    if top_skills_df.empty:
        st.info("No skill frequency data available.")
    else:
        fig_top_skills = px.bar(
            top_skills_df.sort_values("frequency", ascending=True),
            x="frequency",
            y="skill",
            orientation="h",
            labels={"frequency": "Frequency", "skill": "Skill"},
        )
        style_plotly_figure(fig_top_skills)
        st.plotly_chart(fig_top_skills, use_container_width=True)

with right_col:
    st.subheader("Skill Category Distribution")
    if category_df.empty:
        st.info("Skill category distribution unavailable.")
    else:
        fig_category = px.bar(
            category_df,
            x="skill_category",
            y="frequency",
            labels={"skill_category": "Skill Category", "frequency": "Frequency"},
        )
        fig_category.update_layout(xaxis_tickangle=-25)
        style_plotly_figure(fig_category)
        st.plotly_chart(fig_category, use_container_width=True)

split_col, _ = st.columns(2)
with split_col:
    st.subheader("Technical vs Soft Skill Split")
    if split_df.empty:
        st.info("Skill-type split unavailable.")
    else:
        fig_split = px.pie(split_df, names="skill_type", values="frequency")
        style_plotly_figure(fig_split)
        st.plotly_chart(fig_split, use_container_width=True)

st.markdown("---")

st.subheader("Skills by Job Type Heatmap")
job_type_matrix = get_skills_by_group(skill_df, "job_type", top_n_skills=15)
if job_type_matrix.empty:
    st.info("Job-type skill heatmap unavailable for current filters.")
else:
    fig_job_type_heatmap = px.imshow(
        job_type_matrix,
        labels={"x": "Skill", "y": "Job Type", "color": "Frequency"},
        aspect="auto",
    )
    style_plotly_figure(fig_job_type_heatmap)
    st.plotly_chart(fig_job_type_heatmap, use_container_width=True)

st.subheader("Skills by Job Title Heatmap")
job_title_matrix = get_skills_by_group(skill_df, "job_title", top_n_skills=15)
if job_title_matrix.empty:
    st.info("Job-title skill heatmap unavailable for current filters.")
else:
    if len(job_title_matrix.index) > 10:
        title_order = (
            skill_df["job_title"].value_counts().head(10).index.tolist()
        )
        job_title_matrix = job_title_matrix.loc[
            [title for title in title_order if title in job_title_matrix.index]
        ]

    fig_job_title_heatmap = px.imshow(
        job_title_matrix,
        labels={"x": "Skill", "y": "Job Title", "color": "Frequency"},
        aspect="auto",
    )
    style_plotly_figure(fig_job_title_heatmap)
    st.plotly_chart(fig_job_title_heatmap, use_container_width=True)

st.subheader("Skill Co-occurrence Heatmap")
cooccurrence_df = get_skill_cooccurrence(filtered_jobs_df, top_n_skills=12)
if cooccurrence_df.empty or len(cooccurrence_df) < 2:
    st.info("Not enough skill diversity to build co-occurrence heatmap.")
else:
    fig_cooccurrence = go.Figure(
        data=go.Heatmap(
            z=cooccurrence_df.values,
            x=cooccurrence_df.columns,
            y=cooccurrence_df.index,
            colorbar_title="Co-occurrence",
        )
    )
    fig_cooccurrence.update_layout(xaxis_title="Skill", yaxis_title="Skill")
    style_plotly_figure(fig_cooccurrence)
    st.plotly_chart(fig_cooccurrence, use_container_width=True)

st.subheader("Top Skill Combinations")
combination_df = get_top_skill_combinations(
    filtered_jobs_df,
    combination_size=2,
    top_n=10,
)

if combination_df.empty:
    st.info("No skill combinations found for current filters.")
else:
    fig_combinations = px.bar(
        combination_df.sort_values("frequency", ascending=True),
        x="frequency",
        y="skill_combination",
        orientation="h",
        labels={"frequency": "Frequency", "skill_combination": "Skill Combination"},
    )
    style_plotly_figure(fig_combinations)
    st.plotly_chart(fig_combinations, use_container_width=True)
    st.dataframe(combination_df, use_container_width=True)

st.markdown("---")
st.subheader("Detailed Skill Table")

detailed_skill_df = get_top_skills(skill_df, top_n=200)
if not detailed_skill_df.empty:
    detailed_skill_df["category"] = detailed_skill_df["skill"].apply(
        lambda skill: category_lookup.get(skill, "uncategorized")
    )
    detailed_skill_df["skill_type"] = detailed_skill_df["category"].apply(
        lambda cat: "Soft Skills" if cat == "soft_skills" else ("Uncategorized" if cat == "uncategorized" else "Technical Skills")
    )
    st.dataframe(detailed_skill_df, use_container_width=True)

    st.download_button(
        label="Download Skill Analysis CSV",
        data=detailed_skill_df.to_csv(index=False).encode("utf-8"),
        file_name="skill_analysis_table.csv",
        mime="text/csv",
    )
else:
    st.info("Skill table not available.")

st.markdown("---")
st.subheader("Skill Demand Over Time")

ts_summary = get_timeseries_summary(filtered_jobs_df)
if not ts_summary.get("available"):
    st.info(ts_summary.get("message", "Time-series unavailable."))
else:
    st.caption(f"Date range: {ts_summary['min_date']} → {ts_summary['max_date']} ({ts_summary['date_count']} jobs with dates)")
    ts_df = build_skill_timeseries(filtered_jobs_df, top_n_skills=8)
    if ts_df.empty:
        st.info("Not enough dated job rows to plot skill trends.")
    else:
        fig_ts = px.line(
            ts_df,
            x="period",
            y="job_count",
            color="skill",
            markers=True,
            labels={"period": "Period", "job_count": "Job Count", "skill": "Skill"},
        )
        style_plotly_figure(fig_ts)
        st.plotly_chart(fig_ts, use_container_width=True)

st.markdown("---")
st.subheader("Quick Insights")
insights = generate_skill_insights(skill_df, filtered_jobs_df, category_df=category_df)
for insight in insights:
    st.markdown(f"- {insight}")

with st.expander("How to read this page"):
    st.markdown("- Skill mentions are counted from extracted job-description skills.")
    st.markdown("- One job post can contain multiple skills.")
    st.markdown("- Co-occurrence means two skills appeared in the same job post.")
    st.markdown("- Current data is sample/synthetic until real job collection is added.")

with st.expander("Data Quality Notes"):
    uncategorized_mentions = 0
    if "skill_category" in skill_df.columns:
        uncategorized_mentions = int((skill_df["skill_category"] == "uncategorized").sum())

    available_categories = sorted(skill_df["skill_category"].dropna().astype(str).unique().tolist()) if "skill_category" in skill_df.columns else []

    st.markdown(f"- Number of jobs used: **{len(filtered_jobs_df)}**")
    st.markdown(f"- Number of exploded skill rows: **{len(skill_df)}**")
    st.markdown(f"- Number of uncategorized skill mentions: **{uncategorized_mentions}**")
    st.markdown(f"- Available skill categories: `{', '.join(available_categories)}`")
    st.markdown(f"- Available columns: `{', '.join(skill_df.columns.tolist())}`")

with st.expander("Next Development Steps"):
    st.markdown("- Improve skill dictionary")
    st.markdown("- Add semantic skill extraction")
    st.markdown("- Add real job data")
    st.markdown("- Add CV skill-gap analyzer")
    st.markdown("- Add role clustering")
    st.markdown("- Add skill trend analysis when date-based real data is available")

# Optional fallback note for frequency file availability
if skill_freq_df.empty:
    st.info("`sample_skill_frequency.csv` is not available. Run health-check to regenerate it.")
