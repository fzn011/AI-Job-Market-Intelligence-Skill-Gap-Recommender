"""Main Streamlit dashboard entry point for CareerCompass."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.source_repair import ensure_careercompass_sources  # noqa: E402

ensure_careercompass_sources(PROJECT_ROOT)

from src.career_taxonomy_utils import get_roles_for_category, list_career_categories, load_role_profiles  # noqa: E402
from src.dashboard_utils import get_active_dataset_label, load_active_jobs_dataset  # noqa: E402
from src.progress_tracker_utils import record_gap_analysis  # noqa: E402
from src.quick_start_utils import (  # noqa: E402
    QUICK_START_GOALS,
    SAMPLE_CV,
    SAMPLE_JOB,
    get_default_category,
    run_explore_quick_start,
    run_job_match_quick_start,
    run_skill_gap_quick_start,
)
from src.regional_profiles_utils import list_regions  # noqa: E402
from src.brand_constants import APP_NAME, APP_TAGLINE, APP_VERSION  # noqa: E402
from src.ui_theme import (  # noqa: E402
    apply_global_theme,
    render_brand_header,
    render_feature_card,
    render_info_box,
    render_path_card,
    render_sidebar_navigation,
    render_status_badge,
    render_app_footer,
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

if not categories:
    st.error(
        "Career data files are missing. From the project folder run "
        "`python scripts/generate_career_taxonomies.py` or `.\setup.ps1`."
    )
    st.stop()

default_category = get_default_category()
default_category_index = categories.index(default_category) if default_category in categories else 0

# ── Quick Start Wizard (3 clicks to first result) ───────────────────────────
st.markdown(
    """
    <div class="cc-wizard-box">
        <div style="font-size:1.25rem; font-weight:800; margin-bottom:0.35rem;">Quick Start Wizard</div>
        <div style="color:rgba(255,255,255,0.75); font-size:0.95rem;">
            Three clicks to your first career insight — no need to hunt through pages.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "qs_goal" not in st.session_state:
    st.session_state["qs_goal"] = QUICK_START_GOALS[0]
if "qs_result" not in st.session_state:
    st.session_state["qs_result"] = None

step_cols = st.columns(3)
step_cols[0].markdown("<span class='cc-wizard-step cc-wizard-step-active'>① Choose goal</span>", unsafe_allow_html=True)
step_cols[1].markdown("<span class='cc-wizard-step cc-wizard-step-active'>② Add details</span>", unsafe_allow_html=True)
step_cols[2].markdown("<span class='cc-wizard-step cc-wizard-step-active'>③ Get result</span>", unsafe_allow_html=True)

wiz1, wiz2, wiz3 = st.columns([1.2, 1.3, 0.8])

with wiz1:
    st.markdown("**Click 1 — Choose your goal**")
    goal = st.radio("Goal", options=QUICK_START_GOALS, key="qs_goal_radio", label_visibility="collapsed")
    st.session_state["qs_goal"] = goal

with wiz2:
    st.markdown("**Click 2 — Add details**")
    if goal == "Check my skill gap for a role":
        qs_category = st.selectbox("Category", options=categories, index=default_category_index, key="qs_cat")
        qs_roles = get_roles_for_category(qs_category)
        qs_role = st.selectbox("Target role", options=qs_roles or ["Data Analyst"], key="qs_role")
        qs_region = st.selectbox("Region", options=list_regions(), key="qs_region")
        cv_text = st.text_area("Paste CV (or use sample)", value=SAMPLE_CV, height=100, key="qs_cv_gap")
    elif goal == "Match my CV to a job description":
        cv_text = st.text_area("Your CV", value=SAMPLE_CV, height=80, key="qs_cv_job")
        job_text = st.text_area("Job description", value=SAMPLE_JOB, height=80, key="qs_job")
    else:
        qs_category = st.selectbox("Category", options=categories, index=default_category_index, key="qs_cat_explore")
        qs_roles = get_roles_for_category(qs_category)
        qs_role = st.selectbox("Role to explore", options=qs_roles or ["Data Analyst"], key="qs_role_explore")
        qs_region = st.selectbox("Region", options=list_regions(), key="qs_region_explore")

with wiz3:
    st.markdown("**Click 3 — Get result**")
    st.caption("Runs instantly on this page.")
    analyze_quick = st.button("Get My Result", type="primary", use_container_width=True)
    if st.button("Reset", use_container_width=True):
        st.session_state["qs_result"] = None
        st.rerun()

if analyze_quick:
    if goal == "Check my skill gap for a role":
        result = run_skill_gap_quick_start(qs_category, qs_role, cv_text, qs_region)
    elif goal == "Match my CV to a job description":
        result = run_job_match_quick_start(job_text, cv_text)
    else:
        result = run_explore_quick_start(qs_category, qs_role, qs_region)

    st.session_state["qs_result"] = result
    if result.get("success"):
        record_gap_analysis(
            mode=f"quick_start_{result.get('goal', 'unknown')}",
            target_role=result.get("role", result.get("goal", "Quick Start")),
            category=result.get("category", ""),
            region=result.get("region", "Global"),
            match_score=float(result.get("match_score", 0.0)),
            cv_skills=result.get("cv_skills", result.get("matched_skills", [])),
            missing_skills=result.get("missing_skills", []),
            matched_skills=result.get("matched_skills", result.get("core_skills", [])),
        )

result = st.session_state.get("qs_result")
if result:
    st.markdown("---")
    st.subheader("Your Quick Start Result")

    if not result.get("success"):
        st.warning(result.get("message", "Analysis could not be completed."))
    elif result.get("goal") == "explore":
        st.success(f"**{result['role']}** ({result['category']}) · Level: {result.get('level', 'N/A')}")
        if result.get("regional_notes"):
            st.caption(result["regional_notes"])
        m1, m2 = st.columns(2)
        with m1:
            st.markdown("**Core skills**")
            st.write(", ".join(result.get("core_skills", [])) or "None listed")
        with m2:
            st.markdown("**Helpful skills**")
            st.write(", ".join(result.get("helpful_skills", [])) or "None listed")
        if result.get("top_action"):
            action = result["top_action"]
            st.info(f"**Next action:** {action.get('title', 'Explore Career Explorer')} ({action.get('action_type', '')})")
        st.caption("Open **Career Explorer** in the sidebar for the full role breakdown.")
    else:
        score = float(result.get("match_score", 0.0))
        m1, m2, m3 = st.columns(3)
        m1.metric("Match Score", f"{score:.1f}%")
        m2.metric("Match Level", result.get("match_level", "N/A"))
        m3.metric("Missing Skills", len(result.get("missing_skills", [])))

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Matched**")
            st.write(", ".join(result.get("matched_skills", [])) or "None")
        with c2:
            st.markdown("**Missing (priority)**")
            st.write(", ".join(result.get("missing_skills", [])) or "None")

        if result.get("top_action"):
            action = result["top_action"]
            st.success(
                f"**Recommended next step:** {action.get('title', 'See Career Actions')} "
                f"({action.get('estimated_time', 'flexible')})"
            )

        page_hint = result.get("next_page", "")
        page_names = {
            "3_CV_Skill_Gap": "CV Skill Gap Analyzer",
            "8_Job_Match_Dashboard": "Job Match Dashboard",
            "7_Career_Explorer": "Career Explorer",
        }
        st.caption(f"For full analysis, open **{page_names.get(page_hint, 'the sidebar pages')}**.")

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
    ("Skill Demand Analysis", "Top skills, categories, co-occurrence, and time-series trends.", "Live", "2_Skill_Analysis"),
    ("CV Skill Gap Analyzer", "Compare your CV against market data or curated role profiles.", "Live", "3_CV_Skill_Gap"),
    ("Project & Career Actions", "Portfolio projects plus certifications, case studies, and career tasks.", "Live", "4_Project_Recommendations"),
    ("Job Match Dashboard", "Paste any job description + CV for instant fit scoring.", "New", "8_Job_Match_Dashboard"),
    ("Career Toolkit", "Progress tracker, multi-CV compare, interview prep, resume bullets, badges.", "New", "9_Career_Toolkit"),
    ("Career Intelligence Hub", "Company prep, salary, LinkedIn, peer benchmark, voice interview, ICS calendar.", "New", "10_Career_Intelligence_Hub"),
    ("Role Clustering", "Unsupervised job segmentation with TF-IDF + KMeans.", "Live", "5_Role_Clustering"),
    ("Data Import", "Upload CSV job data or fetch from public connectors.", "Live", "6_Data_Import"),
    ("Career Explorer", "Browse roles, skills, and regional profiles without job data.", "Live", "7_Career_Explorer"),
]

row_a, row_b, row_c = st.columns(3)
for idx, (title, body, badge, _page) in enumerate(modules):
    target = [row_a, row_b, row_c][idx % 3]
    with target:
        render_feature_card(title, body, badge=badge)

st.markdown("---")
st.subheader("Advanced Features")
feat_col1, feat_col2, feat_col3 = st.columns(3)
with feat_col1:
    render_feature_card("Skill Synonym Engine", "Maps JS→javascript, PowerBI→power bi for smarter extraction.", badge="Built-in")
    render_feature_card("Learning Resources", "Curated free courses and docs for missing skills.", badge="Built-in")
with feat_col2:
    render_feature_card("Regional Profiles", "Bangladesh, UK, US, and Remote role expectations.", badge="Built-in")
    render_feature_card("PDF Reports", "Download polished career and job-match PDF reports.", badge="Built-in")
with feat_col3:
    render_feature_card("Multilingual UI", "English and Bengali interface toggle in the sidebar.", badge="Built-in")
    render_feature_card("Gamification", "Earn badges for analyses, actions, and milestones.", badge="Built-in")

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

render_app_footer()
