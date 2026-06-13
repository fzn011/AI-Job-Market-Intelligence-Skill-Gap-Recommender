"""Main Streamlit dashboard entry point for CareerCompass."""

import sys
from pathlib import Path
import ast

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.career_taxonomy_utils import list_career_categories, load_role_profiles  # noqa: E402
from src.dashboard_utils import get_active_dataset_label, load_active_jobs_dataset  # noqa: E402
from src.ui_theme import (  # noqa: E402
    APP_NAME,
    APP_TAGLINE,
    APP_VERSION,
    apply_global_theme,
    render_brand_header,
    render_feature_card,
    render_info_box,
    render_path_card,
    render_sidebar_navigation,
    render_status_badge,
)


st.set_page_config(
    page_title=f"{APP_NAME} · Job Market Intelligence",
    page_icon="🧭",
    layout="wide",
)

apply_global_theme()
render_sidebar_navigation()

render_brand_header(
    subtitle="Understand the market. Map your skill gap. Build your next move — for any career path.",
)

categories = list_career_categories()
role_profiles = load_role_profiles()
total_roles = sum(len(roles) for roles in role_profiles.values())

st.markdown("---")

hero_left, hero_right = st.columns([1.35, 1])
with hero_left:
    render_info_box(
        "What CareerCompass does",
        "This project started as a Data/AI job-market analyzer and has been extended into a broader "
        "career intelligence platform. It helps you understand skill demand, compare your CV to target roles, "
        "and get practical next steps — with or without imported job data.",
    )
    st.markdown(
        f"{render_status_badge('12 career categories')} "
        f"{render_status_badge(f'{total_roles} role profiles')} "
        f"{render_status_badge('Rule-based · No paid APIs')}",
        unsafe_allow_html=True,
    )

with hero_right:
    dataset_preference = st.selectbox("Dataset source", options=["Auto", "Imported", "Sample"], index=0)
    preferred_mode = dataset_preference.strip().lower()
    st.caption(f"Active dataset: {get_active_dataset_label(preferred=preferred_mode)}")

st.markdown("---")
st.subheader("Two Ways to Use CareerCompass")

path_col_1, path_col_2 = st.columns(2)
with path_col_1:
    render_path_card(
        "Path 1 · Data-driven analysis",
        "Import or use sample job posts to analyze real market patterns: top skills, gaps, clustering, "
        "and project recommendations grounded in your dataset.",
    )
with path_col_2:
    render_path_card(
        "Path 2 · Career category guidance",
        "No job data? Use curated role profiles and skill taxonomies across Data/AI, Software, Finance, "
        "Marketing, Design, Teaching, Healthcare, Engineering, and more.",
    )

st.markdown("---")
st.subheader("Dashboard Modules")

modules = [
    ("Job Market Overview", "Explore role, company, location, and skill distributions.", "Live", "1_Job_Market_Overview"),
    ("Skill Demand Analysis", "Top skills, categories, co-occurrence, and role-wise demand.", "Live", "2_Skill_Analysis"),
    ("CV Skill Gap Analyzer", "Compare your CV against market data or curated role profiles.", "Live", "3_CV_Skill_Gap"),
    ("Project & Career Actions", "Portfolio projects plus certifications, case studies, and career tasks.", "Live", "4_Project_Recommendations"),
    ("Role Clustering", "Unsupervised job segmentation with TF-IDF + KMeans.", "Live", "5_Role_Clustering"),
    ("Data Import", "Upload CSV job data with schema validation.", "Live", "6_Data_Import"),
    ("Career Explorer", "Browse roles, skills, and preparation plans without job data.", "New", "7_Career_Explorer"),
]

row_a, row_b, row_c = st.columns(3)
for idx, (title, body, badge, _page) in enumerate(modules):
    target = [row_a, row_b, row_c][idx % 3]
    with target:
        render_feature_card(title, body, badge=badge)

st.markdown("---")
st.subheader("Supported Career Fields")

field_cols = st.columns(4)
fields = [
    "Data & AI",
    "Software & IT",
    "Banking & Finance",
    "Business & Admin",
    "Marketing & Sales",
    "Design & Creative",
    "Education & Teaching",
    "Healthcare",
    "Engineering",
    "Customer Support",
    "Operations & PM",
    "Entry-Level Jobs",
]
for idx, field in enumerate(fields):
    with field_cols[idx % 4]:
        st.markdown(f"- {field}")

st.markdown("---")
st.subheader("Dataset Status")

processed_df = load_active_jobs_dataset(preferred=preferred_mode)
status_cols = st.columns(4)
status_cols[0].metric("Jobs Loaded", len(processed_df) if not processed_df.empty else 0)
status_cols[1].metric("Career Categories", len(categories))
status_cols[2].metric("Role Profiles", total_roles)
status_cols[3].metric("Dataset Mode", dataset_preference)

if not processed_df.empty:
    st.success(f"✅ {get_active_dataset_label(preferred=preferred_mode)} is ready for data-driven pages.")
    with st.expander("Preview first 10 job rows"):
        st.dataframe(processed_df.head(10), use_container_width=True)
else:
    st.info(
        "No processed job dataset found for this selection. You can still use **Career Explorer** and "
        "**Career Category mode** on the CV and Recommendations pages. "
        "Run `python3 scripts/run_project_check.py` or import data to enable market analytics."
    )

st.markdown("---")
render_info_box(
    "Honest note",
    "Default demo job posts are synthetic and realistic — not scraped from job boards. "
    "Career category guidance uses curated, rule-based profiles. Results are guidance, not hiring guarantees.",
)

st.markdown(
    f"<div class='cc-footer'>Built with Python · Streamlit · scikit-learn · Plotly · {APP_VERSION}</div>",
    unsafe_allow_html=True,
)
