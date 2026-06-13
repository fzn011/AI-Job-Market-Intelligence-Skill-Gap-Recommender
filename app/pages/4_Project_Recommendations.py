"""Project & Career Action Recommendations page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.career_taxonomy_utils import (  # noqa: E402
    generate_career_action_plan,
    get_roles_for_category,
    get_target_role_skills,
    list_career_categories,
    recommend_career_actions,
)
from src.dashboard_utils import get_active_dataset_label, load_active_jobs_dataset, load_processed_jobs  # noqa: E402
from src.project_recommendation_utils import (  # noqa: E402
    TARGET_ROLES,
    create_project_roadmap_text,
    generate_project_recommendation_insights,
    get_available_skills_from_market,
    get_difficulty_distribution,
    get_project_template_catalog,
    get_role_based_skill_options,
    normalize_selected_skills,
    recommend_projects,
    summarize_project_coverage,
)
from src.ui_theme import apply_global_theme, render_app_footer, render_brand_header, render_info_box, style_plotly_figure  # noqa: E402


st.set_page_config(page_title="Project & Career Action Recommendations", page_icon="🚀", layout="wide")
apply_global_theme()

render_brand_header(
    app_name="CareerCompass · Project & Career Action Recommendations",
    subtitle="Turn missing skills into portfolio projects, case studies, certifications, and practical career actions.",
)

recommendation_mode = st.radio(
    "Recommendation Mode",
    options=["Technical Portfolio Projects", "Career Action Plan"],
    horizontal=True,
)

if recommendation_mode == "Technical Portfolio Projects":
    dataset_pref = st.sidebar.selectbox(
        "Dataset source",
        options=["Auto", "Imported", "Sample"],
        key="page4_dataset_source",
    )
    pref_value = dataset_pref.strip().lower()
    jobs_df = load_active_jobs_dataset(preferred=pref_value)
    if jobs_df.empty and pref_value != "auto":
        jobs_df = load_processed_jobs()

    if jobs_df.empty:
        st.warning("Processed job data not found. Switch to **Career Action Plan** mode or run the data pipeline.")
        st.stop()

    st.caption(f"Active dataset: {get_active_dataset_label(preferred=pref_value)}")

    template_catalog = get_project_template_catalog()
    project_type_options = sorted(
        {
            str(project.get("project_type", "")).strip()
            for project in template_catalog
            if str(project.get("project_type", "")).strip()
        }
    )
    all_market_skills = get_available_skills_from_market(jobs_df, top_n=None)

    ctrl_1, ctrl_2 = st.columns(2)
    with ctrl_1:
        target_role = st.selectbox("Target Role", options=TARGET_ROLES, index=0)
    with ctrl_2:
        skill_source = st.selectbox(
            "Skill Source",
            options=["Use role-based market skills", "Manually select skills"],
            index=0,
        )

    role_based_skill_options = get_role_based_skill_options(jobs_df=jobs_df, target_role=target_role, top_n=25)

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
    selected_skills = st.multiselect("Select Skills", options=skill_options, key="pr_selected_skills")

    ctrl_3, ctrl_4, ctrl_5 = st.columns([1, 1.3, 1.2])
    with ctrl_3:
        difficulty_filter = st.multiselect("Difficulty Filter", options=["Beginner", "Intermediate", "Advanced"])
    with ctrl_4:
        project_type_filter = st.multiselect("Project Type Filter", options=project_type_options)
    with ctrl_5:
        number_of_projects = st.slider("Number of Projects", min_value=3, max_value=12, value=8)

    generate_clicked = st.button("Generate Project Recommendations", type="primary", use_container_width=True)

    if generate_clicked:
        normalized_selected_skills = normalize_selected_skills(selected_skills)
        if not normalized_selected_skills:
            st.warning("Please select at least one skill.")
            st.stop()

        recommendations_df = recommend_projects(
            selected_skills=normalized_selected_skills,
            max_projects=number_of_projects,
            difficulty_filter=difficulty_filter or None,
            project_type_filter=project_type_filter or None,
        )
        coverage_summary = summarize_project_coverage(recommendations_df, normalized_selected_skills)
        insights = generate_project_recommendation_insights(recommendations_df, normalized_selected_skills)
        roadmap_text = create_project_roadmap_text(
            target_role=target_role,
            selected_skills=normalized_selected_skills,
            recommendations_df=recommendations_df,
        )
        st.session_state["pr_results"] = {
            "recommendations_df": recommendations_df,
            "coverage_summary": coverage_summary,
            "insights": insights,
            "roadmap_text": roadmap_text,
        }

    if "pr_results" in st.session_state:
        recommendations_df = st.session_state["pr_results"]["recommendations_df"]
        coverage_summary = st.session_state["pr_results"]["coverage_summary"]
        insights = st.session_state["pr_results"]["insights"]
        roadmap_text = st.session_state["pr_results"]["roadmap_text"]

        st.markdown("---")
        metric_cols = st.columns(5)
        metric_cols[0].metric("Projects", coverage_summary["recommended_projects"])
        metric_cols[1].metric("Selected Skills", coverage_summary["selected_skills"])
        metric_cols[2].metric("Best Project", coverage_summary["best_project"])
        metric_cols[3].metric("Best Coverage", f"{coverage_summary['best_coverage_score']:.2f}%")
        metric_cols[4].metric("Skills Covered", coverage_summary["skills_covered_by_any_project"])

        if recommendations_df.empty:
            st.warning("No recommendations found. Try widening filters.")
        else:
            st.dataframe(recommendations_df, use_container_width=True)
            for idx, (_, row) in enumerate(recommendations_df.iterrows(), start=1):
                with st.expander(f"{idx}. {row['title']} · {row['difficulty']}"):
                    st.markdown(f"**Description:** {row['description']}")
                    st.markdown(f"**Matched Skills:** {', '.join(row['matched_skills']) if row['matched_skills'] else 'None'}")
                    st.markdown(f"**Portfolio Value:** {row['portfolio_value']}")

            viz_col_1, viz_col_2 = st.columns(2)
            with viz_col_1:
                fig = px.bar(recommendations_df.sort_values("coverage_score"), x="coverage_score", y="title", orientation="h")
                style_plotly_figure(fig)
                st.plotly_chart(fig, use_container_width=True)
            with viz_col_2:
                fig2 = px.pie(get_difficulty_distribution(recommendations_df), names="difficulty", values="count", hole=0.45)
                style_plotly_figure(fig2)
                st.plotly_chart(fig2, use_container_width=True)

        for insight in insights:
            st.markdown(f"- {insight}")

        st.download_button(
            label="Download Project Roadmap",
            data=roadmap_text.encode("utf-8"),
            file_name="project_recommendation_roadmap.txt",
            mime="text/plain",
        )

else:
    categories = list_career_categories()
    if not categories:
        st.error("Career taxonomies not found.")
        st.stop()

    render_info_box(
        "Career Action Plan mode",
        "Recommends portfolio projects, case studies, certifications, practice tasks, and interview prep "
        "based on missing skills for any career category — not only Data/AI.",
    )

    ctrl_a, ctrl_b, ctrl_c = st.columns([1.2, 1.2, 0.8])
    with ctrl_a:
        career_category = st.selectbox("Career Category", options=categories, key="ca_category")
    with ctrl_b:
        roles = get_roles_for_category(career_category)
        if not roles:
            st.warning("No roles found for this category.")
            st.stop()
        career_role = st.selectbox("Target Role", options=roles, key="ca_role")
    with ctrl_c:
        max_actions = st.slider("Max Actions", min_value=3, max_value=15, value=8)

    role_skills = get_target_role_skills(career_category, career_role)
    skill_mode = st.radio(
        "Missing skills source",
        options=["Use all target role skills as gaps", "Manually select missing skills"],
        horizontal=True,
    )

    if skill_mode == "Use all target role skills as gaps":
        missing_skills = role_skills
    else:
        missing_skills = st.multiselect("Select missing skills", options=role_skills, default=role_skills[:5])

    generate_clicked = st.button("Generate Career Action Plan", type="primary", use_container_width=True)

    if generate_clicked:
        normalized_missing = normalize_selected_skills(missing_skills)
        if not normalized_missing:
            st.warning("Select at least one missing skill.")
            st.stop()

        actions_df = recommend_career_actions(
            missing_skills=normalized_missing,
            category=career_category,
            max_actions=max_actions,
        )
        action_plan = generate_career_action_plan(
            category=career_category,
            role=career_role,
            missing_skills=normalized_missing,
            recommendations_df=actions_df,
        )
        st.session_state["ca_actions_df"] = actions_df
        st.session_state["ca_action_plan"] = action_plan
        st.session_state["ca_meta"] = {
            "category": career_category,
            "role": career_role,
            "missing_count": len(normalized_missing),
        }

    if "ca_actions_df" in st.session_state:
        actions_df = st.session_state["ca_actions_df"]
        action_plan = st.session_state["ca_action_plan"]
        meta = st.session_state["ca_meta"]

        st.markdown("---")
        metric_cols = st.columns(4)
        metric_cols[0].metric("Category", meta["category"])
        metric_cols[1].metric("Target Role", meta["role"])
        metric_cols[2].metric("Missing Skills", meta["missing_count"])
        metric_cols[3].metric("Actions Recommended", len(actions_df))

        if actions_df.empty:
            st.warning("No actions matched. Try different skills or category.")
        else:
            st.dataframe(actions_df, use_container_width=True)

            for idx, (_, row) in enumerate(actions_df.iterrows(), start=1):
                with st.expander(f"{idx}. {row['title']} · {row['action_type']} · {row['difficulty']}"):
                    st.markdown(f"**Time:** {row['estimated_time']}")
                    st.markdown(f"**Description:** {row['description']}")
                    st.markdown(f"**Matched Skills:** {', '.join(row['matched_skills']) if row['matched_skills'] else 'General'}")
                    st.markdown(f"**Portfolio Value:** {row['portfolio_value']}")
                    st.markdown("**Deliverables:**")
                    for item in row.get("deliverables", []):
                        st.markdown(f"- {item}")

            fig = px.bar(
                actions_df.sort_values("coverage_score"),
                x="coverage_score",
                y="title",
                orientation="h",
                color="action_type",
            )
            style_plotly_figure(fig)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Suggested 30-Day Plan")
        st.markdown("- **Week 1:** Pick one high-coverage action and gather materials.")
        st.markdown("- **Week 2:** Complete deliverables and document outcomes.")
        st.markdown("- **Week 3:** Tackle a second action focused on core missing skills.")
        st.markdown("- **Week 4:** Update CV bullets and prepare interview stories.")

        st.download_button(
            label="Download Career Action Plan",
            data=action_plan.encode("utf-8"),
            file_name="career_action_plan.txt",
            mime="text/plain",
        )

with st.expander("How recommendations work"):
    st.markdown("- Project mode scores local technical project templates against selected skills.")
    st.markdown("- Career Action mode scores action templates by missing skill coverage.")
    st.markdown("- All recommendations are rule-based and transparent.")

render_app_footer(show_tech_line=False)
