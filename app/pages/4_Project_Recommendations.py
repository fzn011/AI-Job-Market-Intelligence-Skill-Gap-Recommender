"""Project Recommendation Engine dashboard page."""

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
from src.project_recommendation_utils import (  # noqa: E402
    TARGET_ROLES,
    build_project_skill_matrix,
    create_project_roadmap_text,
    generate_project_recommendation_insights,
    get_available_skills_from_market,
    get_difficulty_distribution,
    get_project_template_catalog,
    get_project_type_distribution,
    get_role_based_skill_options,
    normalize_selected_skills,
    recommend_projects,
    summarize_project_coverage,
)
from src.skill_analysis_utils import (  # noqa: E402
    build_skill_category_lookup,
    load_skill_dictionary_for_analysis,
)
from src.ui_theme import apply_global_theme, render_brand_header, style_plotly_figure  # noqa: E402


st.set_page_config(page_title="Project Recommendation Engine", page_icon="🚀", layout="wide")

apply_global_theme()

render_brand_header(
    app_name="EmberScope AI · Project Recommendation Engine",
    subtitle="Turn missing or target skills into practical portfolio project ideas with deliverables, tech stack, and roadmap.",
    logo_mark="◜●◝",
)

jobs_df = load_processed_jobs()
if jobs_df.empty:
    st.warning("Processed job data was not found. Please run: python scripts/run_project_check.py")
    st.stop()

skill_dict = load_skill_dictionary_for_analysis()
category_lookup = build_skill_category_lookup(skill_dict) if skill_dict else {}

template_catalog = get_project_template_catalog()
project_type_options = sorted(
    {
        str(project.get("project_type", "")).strip()
        for project in template_catalog
        if str(project.get("project_type", "")).strip()
    }
)

all_market_skills = get_available_skills_from_market(jobs_df, top_n=None)

st.subheader("Recommendation Controls")
ctrl_1, ctrl_2 = st.columns(2)
with ctrl_1:
    target_role = st.selectbox("Target Role", options=TARGET_ROLES, index=0)
with ctrl_2:
    skill_source = st.selectbox(
        "Skill Source",
        options=["Use role-based market skills", "Manually select skills"],
        index=0,
    )

role_based_skill_options = get_role_based_skill_options(
    jobs_df=jobs_df,
    target_role=target_role,
    top_n=25,
)

if "pr_selected_skills" not in st.session_state:
    st.session_state["pr_selected_skills"] = role_based_skill_options
if "pr_last_source" not in st.session_state:
    st.session_state["pr_last_source"] = skill_source
if "pr_last_role" not in st.session_state:
    st.session_state["pr_last_role"] = target_role

source_or_role_changed = (
    st.session_state["pr_last_source"] != skill_source
    or st.session_state["pr_last_role"] != target_role
)

if skill_source == "Use role-based market skills" and source_or_role_changed:
    st.session_state["pr_selected_skills"] = role_based_skill_options
elif skill_source == "Manually select skills" and st.session_state["pr_last_source"] != skill_source:
    st.session_state["pr_selected_skills"] = []

st.session_state["pr_last_source"] = skill_source
st.session_state["pr_last_role"] = target_role

skill_options = role_based_skill_options if skill_source == "Use role-based market skills" else all_market_skills

selected_skills = st.multiselect(
    "Select Skills",
    options=skill_options,
    key="pr_selected_skills",
    help="Select the skills you want your portfolio projects to demonstrate.",
)

ctrl_3, ctrl_4, ctrl_5 = st.columns([1, 1.3, 1.2])
with ctrl_3:
    difficulty_filter = st.multiselect(
        "Difficulty Filter",
        options=["Beginner", "Intermediate", "Advanced"],
    )
with ctrl_4:
    project_type_filter = st.multiselect(
        "Project Type Filter",
        options=project_type_options,
    )
with ctrl_5:
    number_of_projects = st.slider("Number of Projects", min_value=3, max_value=12, value=8)

generate_clicked = st.button("Generate Project Recommendations", type="primary", use_container_width=True)

run_recommendations = generate_clicked or bool(selected_skills)

if run_recommendations:
    normalized_selected_skills = normalize_selected_skills(selected_skills)
    if not normalized_selected_skills:
        st.warning("Please select at least one skill to generate project recommendations.")
        st.stop()

    recommendations_df = recommend_projects(
        selected_skills=normalized_selected_skills,
        max_projects=number_of_projects,
        difficulty_filter=difficulty_filter or None,
        project_type_filter=project_type_filter or None,
    )

    skill_matrix_df = build_project_skill_matrix(recommendations_df, normalized_selected_skills)
    coverage_summary = summarize_project_coverage(recommendations_df, normalized_selected_skills)
    insights = generate_project_recommendation_insights(recommendations_df, normalized_selected_skills)
    roadmap_text = create_project_roadmap_text(
        target_role=target_role,
        selected_skills=normalized_selected_skills,
        recommendations_df=recommendations_df,
    )

    st.markdown("---")

    metric_cols = st.columns(6)
    metric_cols[0].metric("Recommended Projects", coverage_summary["recommended_projects"])
    metric_cols[1].metric("Selected Skills", coverage_summary["selected_skills"])
    metric_cols[2].metric("Best Project", coverage_summary["best_project"])
    metric_cols[3].metric("Best Coverage Score", f"{coverage_summary['best_coverage_score']:.2f}%")
    metric_cols[4].metric("Skills Covered", coverage_summary["skills_covered_by_any_project"])
    metric_cols[5].metric("Skills Not Covered", len(coverage_summary["skills_not_covered_by_any_project"]))

    st.markdown("---")
    st.subheader("Main Recommendation Table")

    if recommendations_df.empty:
        st.warning("No recommendations found for the selected filters. Try widening filters.")
    else:
        table_df = recommendations_df.copy()
        table_df["coverage_score"] = table_df["coverage_score"].apply(lambda x: f"{float(x):.2f}%")
        st.dataframe(
            table_df[
                [
                    "title",
                    "project_type",
                    "difficulty",
                    "estimated_timeline",
                    "coverage_score",
                    "matched_skill_count",
                    "matched_skills",
                    "portfolio_value",
                ]
            ],
            use_container_width=True,
        )

        st.download_button(
            label="Download Recommendations CSV",
            data=recommendations_df.to_csv(index=False).encode("utf-8"),
            file_name="project_recommendations.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.subheader("Project Recommendation Cards")

    for idx, (_, row) in enumerate(recommendations_df.iterrows(), start=1):
        with st.expander(f"{idx}. {row['title']} · {row['difficulty']} · {row['estimated_timeline']}"):
            st.markdown(f"**Project Type:** {row['project_type']}")
            st.markdown(f"**Coverage Score:** {float(row['coverage_score']):.2f}%")
            st.markdown(f"**Description:** {row['description']}")
            st.markdown(f"**Business Context:** {row['business_context']}")
            st.markdown(f"**Matched Skills:** {', '.join(row['matched_skills']) if row['matched_skills'] else 'None'}")
            st.markdown(f"**Core Skills:** {', '.join(row['core_skills']) if row['core_skills'] else 'None'}")
            st.markdown(f"**Tech Stack:** {', '.join(row['tech_stack']) if row['tech_stack'] else 'None'}")
            st.markdown("**Deliverables:**")
            for item in row["deliverables"]:
                st.markdown(f"- {item}")
            st.markdown(f"**Portfolio Value:** {row['portfolio_value']}")
            st.markdown("**Suggested GitHub README Sections:**")
            for section in row["github_readme_sections"]:
                st.markdown(f"- {section}")

    st.markdown("---")
    st.subheader("Recommendation Visualizations")

    viz_col_1, viz_col_2 = st.columns(2)
    with viz_col_1:
        coverage_chart_df = recommendations_df.sort_values("coverage_score", ascending=True)
        fig_coverage = px.bar(
            coverage_chart_df,
            x="coverage_score",
            y="title",
            orientation="h",
            labels={"coverage_score": "Coverage Score", "title": "Project"},
        )
        style_plotly_figure(fig_coverage)
        st.plotly_chart(fig_coverage, use_container_width=True)

    with viz_col_2:
        difficulty_dist_df = get_difficulty_distribution(recommendations_df)
        fig_diff = px.pie(difficulty_dist_df, names="difficulty", values="count", hole=0.45)
        style_plotly_figure(fig_diff)
        st.plotly_chart(fig_diff, use_container_width=True)

    viz_col_3, viz_col_4 = st.columns(2)
    with viz_col_3:
        project_type_dist_df = get_project_type_distribution(recommendations_df)
        fig_type = px.bar(
            project_type_dist_df,
            x="project_type",
            y="count",
            labels={"project_type": "Project Type", "count": "Count"},
        )
        fig_type.update_layout(xaxis_tickangle=-25)
        style_plotly_figure(fig_type)
        st.plotly_chart(fig_type, use_container_width=True)

    with viz_col_4:
        fig_match_count = px.bar(
            recommendations_df.sort_values("matched_skill_count", ascending=True),
            x="matched_skill_count",
            y="title",
            orientation="h",
            labels={"matched_skill_count": "Matched Skill Count", "title": "Project"},
        )
        style_plotly_figure(fig_match_count)
        st.plotly_chart(fig_match_count, use_container_width=True)

    st.subheader("Project-Skill Coverage Matrix")
    if skill_matrix_df.empty:
        st.info("Project-skill matrix is unavailable for current selections.")
    else:
        matrix_for_plot = skill_matrix_df.copy()
        if len(matrix_for_plot.columns) > 20:
            st.caption("Showing first 20 selected skills for readability.")
            matrix_for_plot = matrix_for_plot.iloc[:, :20]

        fig_matrix = px.imshow(
            matrix_for_plot,
            labels={"x": "Selected Skill", "y": "Project", "color": "Coverage (1/0)"},
            aspect="auto",
        )
        style_plotly_figure(fig_matrix)
        st.plotly_chart(fig_matrix, use_container_width=True)

    st.markdown("---")
    st.subheader("Quick Insights")
    for insight in insights:
        st.markdown(f"- {insight}")

    st.markdown("---")
    st.subheader("Recommended Build Roadmap")

    if recommendations_df.empty:
        st.info("No roadmap available because no recommendations were generated.")
    else:
        roadmap_preview = recommendations_df.head(3).copy()
        for idx, (_, row) in enumerate(roadmap_preview.iterrows(), start=1):
            why_text = ""
            if idx == 1:
                why_text = "Highest overall skill coverage for your current selection."
            elif idx == 2:
                project_type_text = str(row["project_type"]).lower()
                if "deployment" in project_type_text or "mlops" in project_type_text:
                    why_text = "Adds production/deployment depth after core coverage is established."
                else:
                    why_text = "Broadens practical implementation depth across additional skills."
            else:
                if str(row["difficulty"]).lower() == "advanced":
                    why_text = "Adds advanced specialization to differentiate your portfolio."
                else:
                    why_text = "Strengthens breadth with another role-relevant project."

            st.markdown(f"**Project {idx}: {row['title']}**")
            st.markdown(f"- Why this project {'first' if idx == 1 else 'next'}: {why_text}")
            st.markdown(f"- Skills covered: {', '.join(row['matched_skills']) if row['matched_skills'] else 'None'}")
            st.markdown(f"- Expected portfolio value: {row['portfolio_value']}")

    st.download_button(
        label="Download Project Roadmap",
        data=roadmap_text.encode("utf-8"),
        file_name="project_recommendation_roadmap.txt",
        mime="text/plain",
    )

    with st.expander("How this recommendation engine works"):
        st.markdown("- It uses local project templates.")
        st.markdown("- It scores each project against selected skills.")
        st.markdown("- It ranks projects by skill coverage.")
        st.markdown("- It does not use paid AI APIs.")
        st.markdown("- It is meant to guide portfolio planning.")

    with st.expander("How to use these recommendations"):
        st.markdown("- Pick one high-coverage project first.")
        st.markdown("- Make sure the project is end-to-end.")
        st.markdown("- Add README, screenshots, dashboard, and demo video.")
        st.markdown("- Do not claim skills unless the project actually uses them.")
        st.markdown("- Prefer projects that match your target job role.")

    with st.expander("Data Quality Notes"):
        st.markdown(f"- Number of jobs used: **{len(jobs_df)}**")
        st.markdown(f"- Selected target role: **{target_role}**")
        st.markdown(f"- Number of selected skills: **{len(normalized_selected_skills)}**")
        st.markdown(f"- Number of project templates: **{len(template_catalog)}**")
        st.markdown(f"- Skill categories available: **{len(category_lookup)} skill-to-category mappings**")
        st.markdown("- Current limitation: template-based recommendations, not real hiring guarantees")
