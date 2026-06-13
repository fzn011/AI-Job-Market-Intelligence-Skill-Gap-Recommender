"""Career Explorer — browse roles and skills without job data."""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.career_taxonomy_utils import (  # noqa: E402
    build_category_skill_dataframe,
    generate_career_action_plan,
    generate_role_preparation_plan,
    get_role_profile,
    get_roles_for_category,
    get_target_role_skills,
    list_career_categories,
    load_category_skill_taxonomy,
    recommend_career_actions,
)
from src.regional_profiles_utils import get_regional_role_profile, get_regional_target_skills, list_regions  # noqa: E402
from src.ui_theme import apply_global_theme, render_app_footer, render_brand_header, render_info_box, style_plotly_figure  # noqa: E402


st.set_page_config(page_title="Career Explorer", page_icon="🌍", layout="wide")
apply_global_theme()

render_brand_header(
    app_name="CareerCompass · Career Explorer",
    subtitle="Explore role expectations, core skills, helpful skills, and recommended actions across multiple career paths.",
)

categories = list_career_categories()
if not categories:
    st.error("Career taxonomies not found. Run `python3 scripts/generate_career_taxonomies.py`.")
    st.stop()

render_info_box(
    "Explore without job data",
    "This page uses curated role profiles and skill taxonomies. It is useful when you are exploring a new field "
    "or do not yet have imported job-post data.",
)

ctrl_a, ctrl_b, ctrl_c = st.columns([1, 1, 1])
with ctrl_a:
    selected_category = st.selectbox("Career Category", options=categories)
with ctrl_b:
    roles = get_roles_for_category(selected_category)
    selected_role = st.selectbox("Target Role", options=roles or ["No roles found"])
with ctrl_c:
    selected_region = st.selectbox("Region", options=list_regions())

if not roles:
    st.warning("No roles found for this category.")
    st.stop()

profile = get_regional_role_profile(selected_category, selected_role, selected_region)
core_skills = profile.get("core_skills", [])
helpful_skills = profile.get("helpful_skills", [])
target_skills = get_regional_target_skills(selected_category, selected_role, selected_region)
taxonomy = load_category_skill_taxonomy(selected_category)
skill_df = build_category_skill_dataframe(selected_category)
actions_df = recommend_career_actions(missing_skills=target_skills, category=selected_category, max_actions=6)
prep_plan = generate_role_preparation_plan(selected_category, selected_role)
action_plan = generate_career_action_plan(
    category=selected_category,
    role=selected_role,
    missing_skills=target_skills,
    recommendations_df=actions_df,
)

st.markdown("---")

metric_cols = st.columns(5)
metric_cols[0].metric("Level", profile.get("level", "N/A"))
metric_cols[1].metric("Core Skills", len(core_skills))
metric_cols[2].metric("Helpful Skills", len(helpful_skills))
metric_cols[3].metric("Typical Outputs", len(profile.get("typical_outputs", [])))
metric_cols[4].metric("Recommended Actions", len(profile.get("recommended_actions", [])))

detail_col_1, detail_col_2 = st.columns(2)
with detail_col_1:
    st.subheader("Role Profile")
    st.markdown(f"**Core skills:** {', '.join(core_skills) or 'None listed'}")
    st.markdown(f"**Helpful skills:** {', '.join(helpful_skills) or 'None listed'}")
    if profile.get("regional_notes"):
        st.info(profile["regional_notes"])
    st.markdown("**Typical outputs:**")
    for item in profile.get("typical_outputs", []):
        st.markdown(f"- {item}")
    st.markdown("**Suggested actions:**")
    for item in profile.get("recommended_actions", []):
        st.markdown(f"- {item}")

with detail_col_2:
    st.subheader("Skill Type Breakdown")
    if skill_df.empty:
        st.info("No taxonomy skills available.")
    else:
        type_counts = skill_df["skill_type"].value_counts().reset_index()
        type_counts.columns = ["skill_type", "count"]
        fig = px.pie(type_counts, names="skill_type", values="count", hole=0.45)
        style_plotly_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Recommended Career Actions")

if actions_df.empty:
    st.info("No career action templates matched for this role.")
else:
    st.dataframe(actions_df, use_container_width=True)
    for idx, (_, row) in enumerate(actions_df.iterrows(), start=1):
        with st.expander(f"{idx}. {row['title']} · {row['action_type']}"):
            st.markdown(f"**Difficulty:** {row['difficulty']} · **Time:** {row['estimated_time']}")
            st.markdown(f"**Description:** {row['description']}")
            st.markdown(f"**Skills covered:** {', '.join(row.get('matched_skills', [])) or 'General role prep'}")
            st.markdown(f"**Value:** {row['portfolio_value']}")

st.download_button(
    label="Download Role Preparation Plan",
    data=prep_plan.encode("utf-8"),
    file_name="role_preparation_plan.txt",
    mime="text/plain",
)
st.download_button(
    label="Download Career Action Plan",
    data=action_plan.encode("utf-8"),
    file_name="career_explorer_action_plan.txt",
    mime="text/plain",
)

with st.expander("How this page helps"):
    st.markdown("- Browse expectations for roles across 12 career categories.")
    st.markdown("- Understand core vs helpful skills before applying or studying.")
    st.markdown("- Get actionable next steps even without job-post data.")
    st.markdown("- Use with CV Skill Gap Analyzer for personalized comparison.")

with st.expander("Limitations"):
    st.markdown("- Role profiles are curated simplifications, not live hiring data.")
    st.markdown("- Expectations vary by country, company size, and seniority.")
    st.markdown("- Recommendations are rule-based guidance, not guarantees.")

render_app_footer(show_tech_line=False)
