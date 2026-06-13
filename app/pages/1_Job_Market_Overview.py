"""Job Market Overview dashboard page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Ensure project root is importable when Streamlit executes pages directly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard_utils import (  # noqa: E402
    add_total_extracted_skills_metric,
    get_active_dataset_label,
    get_basic_job_metrics,
    get_top_values,
    load_active_jobs_dataset,
    load_processed_jobs,
    parse_extracted_skills,
    prepare_jobs_preview,
)
from src.ui_theme import apply_global_theme, render_app_footer, render_brand_header, style_plotly_figure  # noqa: E402


st.set_page_config(page_title="Job Market Overview", page_icon="🗺️", layout="wide")

apply_global_theme()

render_brand_header(
    app_name="CareerCompass · Job Market Overview",
    subtitle="Track demand signals across roles, locations, companies, and skills.",
    logo_mark="◜●◝",
)

dataset_pref = st.sidebar.selectbox(
    "Dataset source",
    options=["Auto", "Imported", "Sample"],
    key="page1_dataset_source",
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

if jobs_df.empty:
    st.warning(
        "Processed job data was not found. Please run: `python scripts/run_project_check.py`"
    )
    st.stop()

original_total = len(jobs_df)
filtered_df = jobs_df.copy()

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
    filter_col_1, filter_col_2, filter_col_3 = st.columns(3)

    with filter_col_1:
        selected_job_type = st.multiselect("Job Type", options=get_filter_options(filtered_df, "job_type"))
    with filter_col_2:
        selected_location = st.multiselect("Location", options=get_filter_options(filtered_df, "location"))
    with filter_col_3:
        selected_company = st.multiselect("Company", options=get_filter_options(filtered_df, "company"))


filtered_df = apply_multiselect_filter(filtered_df, "job_type", selected_job_type)
filtered_df = apply_multiselect_filter(filtered_df, "location", selected_location)
filtered_df = apply_multiselect_filter(filtered_df, "company", selected_company)

st.write(f"Showing **{len(filtered_df)}** of **{original_total}** jobs")

metrics = get_basic_job_metrics(filtered_df)
total_extracted_skills = add_total_extracted_skills_metric(filtered_df)

metric_cols = st.columns(6)
metric_cols[0].metric("Total Jobs", metrics["total_jobs"])
metric_cols[1].metric("Unique Job Titles", metrics["unique_job_titles"])
metric_cols[2].metric("Unique Companies", metrics["unique_companies"])
metric_cols[3].metric("Locations", metrics["unique_locations"])
metric_cols[4].metric("Average Skills / Job", metrics["avg_skills_per_job"])
metric_cols[5].metric("Total Extracted Skills", total_extracted_skills)

st.markdown("---")
st.subheader("Dataset Preview")
preview_df = prepare_jobs_preview(filtered_df, max_rows=20)
st.dataframe(preview_df, use_container_width=True)

st.markdown("---")

chart_col_1, chart_col_2 = st.columns(2)

with chart_col_1:
    st.subheader("Job Titles Distribution")
    top_titles = get_top_values(filtered_df, "job_title", top_n=10)
    if top_titles.empty:
        st.info("No job title data available for selected filters.")
    else:
        fig_titles = px.bar(
            top_titles,
            y="value",
            x="count",
            orientation="h",
            labels={"value": "Job Title", "count": "Count"},
        )
        style_plotly_figure(fig_titles)
        st.plotly_chart(fig_titles, use_container_width=True)

with chart_col_2:
    st.subheader("Location Distribution")
    top_locations = get_top_values(filtered_df, "location", top_n=10)
    if top_locations.empty:
        st.info("No location data available for selected filters.")
    else:
        fig_locations = px.bar(
            top_locations,
            y="value",
            x="count",
            orientation="h",
            labels={"value": "Location", "count": "Count"},
        )
        style_plotly_figure(fig_locations)
        st.plotly_chart(fig_locations, use_container_width=True)

chart_col_3, chart_col_4 = st.columns(2)

with chart_col_3:
    st.subheader("Job Type Distribution")
    top_types = get_top_values(filtered_df, "job_type", top_n=10)
    if top_types.empty:
        st.info("No job type data available for selected filters.")
    else:
        fig_types = px.pie(top_types, values="count", names="value")
        style_plotly_figure(fig_types)
        st.plotly_chart(fig_types, use_container_width=True)

with chart_col_4:
    st.subheader("Skills per Job")
    if "skill_count" not in filtered_df.columns:
        st.info("`skill_count` column not available.")
    else:
        skill_count_series = pd.to_numeric(filtered_df["skill_count"], errors="coerce").fillna(0)
        fig_skill_count = px.histogram(
            x=skill_count_series,
            nbins=min(15, max(5, int(skill_count_series.max()) + 1)),
            labels={"x": "Skill Count", "y": "Number of Jobs"},
        )
        style_plotly_figure(fig_skill_count)
        st.plotly_chart(fig_skill_count, use_container_width=True)

st.subheader("Top Skills Overall")

skill_source_df = filtered_df if "extracted_skills" in filtered_df.columns else pd.DataFrame()
if not skill_source_df.empty and "extracted_skills" in skill_source_df.columns:
    all_skills: list[str] = []
    for value in skill_source_df["extracted_skills"]:
        all_skills.extend(parse_extracted_skills(value))
    if all_skills:
        skill_freq = (
            pd.Series(all_skills)
            .value_counts()
            .head(15)
            .reset_index()
        )
        skill_freq.columns = ["skill", "frequency"]
        fig_skills = px.bar(skill_freq, y="skill", x="frequency", orientation="h")
        style_plotly_figure(fig_skills)
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.info("No extracted skill data available for the selected filters.")
else:
    st.info("No extracted skill data available for the selected filters.")

st.markdown("---")
st.subheader("Quick Insights")

insights: list[str] = []

top_title_df = get_top_values(filtered_df, "job_title", top_n=1)
if not top_title_df.empty:
    insights.append(
        f"Most common job title: **{top_title_df.iloc[0]['value']}** ({int(top_title_df.iloc[0]['count'])} postings)."
    )

top_location_df = get_top_values(filtered_df, "location", top_n=1)
if not top_location_df.empty:
    insights.append(
        f"Most common location: **{top_location_df.iloc[0]['value']}** ({int(top_location_df.iloc[0]['count'])} postings)."
    )

top_type_df = get_top_values(filtered_df, "job_type", top_n=1)
if not top_type_df.empty:
    insights.append(
        f"Most common job type: **{top_type_df.iloc[0]['value']}** ({int(top_type_df.iloc[0]['count'])} postings)."
    )

insights.append(f"Average skills per job: **{metrics['avg_skills_per_job']}**.")

filters_applied = len(filtered_df) != len(jobs_df)
if filters_applied and "extracted_skills" in filtered_df.columns:
    all_skills_for_insight: list[str] = []
    for value in filtered_df["extracted_skills"]:
        all_skills_for_insight.extend(parse_extracted_skills(value))
    if all_skills_for_insight:
        top_skill = pd.Series(all_skills_for_insight).value_counts().index[0]
        top_skill_count = int(pd.Series(all_skills_for_insight).value_counts().iloc[0])
        insights.append(f"Most frequent skill (filtered): **{top_skill}** ({top_skill_count} mentions).")
else:
    all_skills_for_insight = []
    if "extracted_skills" in jobs_df.columns:
        for value in jobs_df["extracted_skills"]:
            all_skills_for_insight.extend(parse_extracted_skills(value))
    if all_skills_for_insight:
        top_counts = pd.Series(all_skills_for_insight).value_counts()
        insights.append(
            f"Most frequent skill overall: **{top_counts.index[0]}** ({int(top_counts.iloc[0])} mentions)."
        )

for insight in insights:
    st.markdown(f"- {insight}")

with st.expander("Data Quality Notes"):
    duplicate_job_ids = 0
    if "job_id" in filtered_df.columns:
        duplicate_job_ids = int(filtered_df["job_id"].duplicated().sum())

    missing_descriptions = 0
    if "description" in filtered_df.columns:
        missing_descriptions = int(
            filtered_df["description"].isna().sum()
            + filtered_df["description"].astype(str).str.strip().eq("").sum()
        )

    missing_job_titles = 0
    if "job_title" in filtered_df.columns:
        missing_job_titles = int(
            filtered_df["job_title"].isna().sum()
            + filtered_df["job_title"].astype(str).str.strip().eq("").sum()
        )

    missing_locations = 0
    if "location" in filtered_df.columns:
        missing_locations = int(
            filtered_df["location"].isna().sum()
            + filtered_df["location"].astype(str).str.strip().eq("").sum()
        )

    st.markdown(f"- Duplicate `job_id` values: **{duplicate_job_ids}**")
    st.markdown(f"- Missing descriptions: **{missing_descriptions}**")
    st.markdown(f"- Missing job titles: **{missing_job_titles}**")
    st.markdown(f"- Missing locations: **{missing_locations}**")
    st.markdown(f"- Available columns: `{', '.join(filtered_df.columns.tolist())}`")

with st.expander("Next Development Steps"):
    st.markdown("- Add real job data collection")
    st.markdown("- Improve skill extraction")
    st.markdown("- Add CV skill-gap analyzer")
    st.markdown("- Add role clustering")
    st.markdown("- Add recommendation engine UI")

render_app_footer(show_tech_line=False)
