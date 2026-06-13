"""CV Skill Gap Analyzer with market and career category modes."""

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
    build_category_skill_dataframe,
    classify_skill_type,
    compute_role_skill_gap,
    extract_skills_from_text,
    generate_career_action_plan,
    get_roles_for_category,
    get_target_role_skills,
    list_career_categories,
    load_category_skill_taxonomy,
    recommend_career_actions,
)
from src.cv_gap_utils import (  # noqa: E402
    build_skill_gap_dataframe,
    classify_match_level,
    compute_cv_market_gap,
    create_cv_gap_report_text,
    extract_cv_skills,
    generate_cv_gap_insights,
    get_market_skills_by_target_role,
    recommend_learning_path,
)
from src.dashboard_utils import get_active_dataset_label, load_active_jobs_dataset, load_processed_jobs  # noqa: E402
from src.skill_analysis_utils import build_skill_category_lookup, load_skill_dictionary_for_analysis  # noqa: E402
from src.ui_theme import apply_global_theme, render_brand_header, render_info_box, style_plotly_figure  # noqa: E402


st.set_page_config(page_title="CV Skill Gap Analyzer", page_icon="📄", layout="wide")
apply_global_theme()

render_brand_header(
    app_name="CareerCompass · CV Skill Gap Analyzer",
    subtitle="Compare your CV against job-market data or curated role profiles across career fields.",
)

analysis_mode = st.radio(
    "Analysis Mode",
    options=["Data-driven market comparison", "Career category comparison"],
    horizontal=True,
    help="Market mode uses imported/sample job data. Career mode uses curated role profiles.",
)

if analysis_mode == "Data-driven market comparison":
    dataset_pref = st.sidebar.selectbox(
        "Dataset source",
        options=["Auto", "Imported", "Sample"],
        key="page3_dataset_source",
    )
    pref_value = dataset_pref.strip().lower()
    jobs_df = load_active_jobs_dataset(preferred=pref_value)
    if jobs_df.empty and pref_value != "auto":
        jobs_df = load_processed_jobs()

    if jobs_df.empty:
        st.warning("Processed job data was not found. Switch to **Career category comparison** or run the data pipeline.")
        st.stop()

    st.caption(f"Active dataset: {get_active_dataset_label(preferred=pref_value)}")

    skill_dictionary = load_skill_dictionary_for_analysis()
    if not skill_dictionary:
        st.warning("Skill dictionary was not found.")
        st.stop()

    category_lookup = build_skill_category_lookup(skill_dictionary)
    target_role_options = [
        "Overall Market", "Data Analyst", "Data Scientist", "Machine Learning Engineer",
        "AI Engineer", "BI Analyst", "Data Engineer", "GenAI Engineer",
        "Risk Data Analyst", "Product Data Analyst", "Junior Data Scientist",
    ]

    ctrl_col_1, ctrl_col_2, ctrl_col_3 = st.columns([1.2, 1, 0.8])
    with ctrl_col_1:
        target_role = st.selectbox("Select Target Role", options=target_role_options, index=0)
    with ctrl_col_2:
        use_top_25 = st.checkbox("Use top 25 market skills only", value=True)
    with ctrl_col_3:
        analyze_clicked = st.button("Analyze Skill Gap", type="primary", use_container_width=True)

    left_col, right_col = st.columns([1.45, 1])
    with left_col:
        cv_text = st.text_area(
            "Paste CV / Resume / Profile Text",
            height=320,
            placeholder="Paste your resume, LinkedIn About section, or project profile here...",
            key="market_cv_text",
        )
    with right_col:
        render_info_box(
            "Market comparison mode",
            "Extracts skills from your CV and compares them to skills found in the active job dataset "
            "for your selected role filter.",
        )

    top_n = 25 if use_top_25 else None
    run_analysis = analyze_clicked or bool(cv_text.strip())

    if run_analysis:
        if not cv_text.strip():
            st.warning("Please paste your CV or profile text first.")
            st.stop()

        cv_skills = extract_cv_skills(cv_text=cv_text, skill_dictionary=skill_dictionary)
        if not cv_skills:
            st.warning("No known skills detected. Add tools, methods, or project keywords from the skill dictionary.")
            st.stop()

        market_skills = get_market_skills_by_target_role(jobs_df=jobs_df, target_role=target_role, top_n=top_n)
        gap_result = compute_cv_market_gap(cv_skills=cv_skills, market_skills=market_skills)
        match_level = classify_match_level(float(gap_result.get("match_score", 0.0)))
        gap_df = build_skill_gap_dataframe(
            matched_skills=gap_result.get("matched_skills", []),
            missing_skills=gap_result.get("missing_skills", []),
            extra_cv_skills=gap_result.get("extra_cv_skills", []),
            category_lookup=category_lookup,
        )
        recommendations = recommend_learning_path(gap_result.get("missing_skills", []))
        insights = generate_cv_gap_insights(gap_result=gap_result, target_role=target_role)
        report_text = create_cv_gap_report_text(
            target_role=target_role,
            cv_skills=cv_skills,
            market_skills=market_skills,
            gap_result=gap_result,
            recommendations=recommendations,
        )

        st.markdown("---")
        metric_cols = st.columns(6)
        metric_cols[0].metric("Match Score", f"{gap_result['match_score']:.2f}%")
        metric_cols[1].metric("Match Level", match_level)
        metric_cols[2].metric("CV Skills Detected", gap_result["total_cv_skills"])
        metric_cols[3].metric("Market Skills Compared", gap_result["total_market_skills"])
        metric_cols[4].metric("Matched Skills", gap_result["matched_count"])
        metric_cols[5].metric("Missing Skills", gap_result["missing_count"])

        tab1, tab2, tab3, tab4 = st.tabs(["Matched", "Missing", "Extra CV Skills", "Full Table"])
        with tab1:
            st.dataframe(pd.DataFrame({"matched_skill": gap_result.get("matched_skills", [])}), use_container_width=True)
        with tab2:
            st.dataframe(pd.DataFrame({"missing_skill": gap_result.get("missing_skills", [])}), use_container_width=True)
        with tab3:
            st.dataframe(pd.DataFrame({"extra_skill": gap_result.get("extra_cv_skills", [])}), use_container_width=True)
        with tab4:
            st.dataframe(gap_df, use_container_width=True)

        if recommendations:
            st.subheader("Recommended Learning Path")
            st.dataframe(pd.DataFrame(recommendations), use_container_width=True)

        st.subheader("Insights")
        for insight in insights:
            st.markdown(f"- {insight}")

        st.download_button(
            label="Download CV Skill Gap Report",
            data=report_text.encode("utf-8"),
            file_name="cv_skill_gap_report.txt",
            mime="text/plain",
        )

else:
    categories = list_career_categories()
    if not categories:
        st.error("Career taxonomies not found. Run `python3 scripts/generate_career_taxonomies.py`.")
        st.stop()

    render_info_box(
        "Career category mode",
        "Uses curated role profiles and skill taxonomies. Useful when you do not have imported job-post data "
        "for a field, or when exploring a new career path.",
    )

    ctrl_a, ctrl_b, ctrl_c = st.columns([1.2, 1.2, 0.8])
    with ctrl_a:
        career_category = st.selectbox("Career Category", options=categories)
    with ctrl_b:
        role_options = get_roles_for_category(career_category)
        target_role = st.selectbox("Target Role", options=role_options or ["No roles found"])
    with ctrl_c:
        analyze_clicked = st.button("Analyze Career Gap", type="primary", use_container_width=True)

    left_col, right_col = st.columns([1.45, 1])
    with left_col:
        cv_text = st.text_area(
            "Paste CV / Resume / Profile Text",
            height=320,
            placeholder="Include skills, tools, projects, certifications, and role-relevant experience...",
            key="career_cv_text",
        )
    with right_col:
        profile_skills = get_target_role_skills(career_category, target_role)
        st.markdown(f"**Target role skills ({len(profile_skills)}):**")
        st.write(", ".join(profile_skills) if profile_skills else "No skills listed.")

    if analyze_clicked or cv_text.strip():
        if not cv_text.strip():
            st.warning("Please paste your CV or profile text first.")
            st.stop()

        cv_skills = extract_skills_from_text(cv_text, career_category)
        if not cv_skills:
            st.warning("No category skills detected. Try adding role-relevant tools, methods, or soft skills.")
            st.stop()

        gap_result = compute_role_skill_gap(cv_skills, career_category, target_role)
        match_level = classify_match_level(float(gap_result.get("match_score", 0.0)))
        taxonomy = load_category_skill_taxonomy(career_category)
        actions_df = recommend_career_actions(
            missing_skills=gap_result.get("missing_skills", []),
            category=career_category,
            max_actions=8,
        )
        action_plan = generate_career_action_plan(
            category=career_category,
            role=target_role,
            missing_skills=gap_result.get("missing_skills", []),
            recommendations_df=actions_df,
        )
        skill_type_df = build_category_skill_dataframe(career_category)

        st.markdown("---")
        metric_cols = st.columns(6)
        metric_cols[0].metric("Core Match Score", f"{gap_result['match_score']:.2f}%")
        metric_cols[1].metric("Match Level", match_level)
        metric_cols[2].metric("CV Skills Found", len(cv_skills))
        metric_cols[3].metric("Missing Core", len(gap_result.get("missing_core_skills", [])))
        metric_cols[4].metric("Missing Helpful", len(gap_result.get("missing_helpful_skills", [])))
        metric_cols[5].metric("Soft Skill Gaps", len(gap_result.get("soft_skill_gaps", [])))

        chart_col_1, chart_col_2 = st.columns(2)
        with chart_col_1:
            status_df = pd.DataFrame(
                {
                    "status": ["Matched", "Missing Core", "Missing Helpful", "Extra in CV"],
                    "count": [
                        len(gap_result.get("matched_skills", [])),
                        len(gap_result.get("missing_core_skills", [])),
                        len(gap_result.get("missing_helpful_skills", [])),
                        len(gap_result.get("extra_cv_skills", [])),
                    ],
                }
            )
            fig = px.bar(status_df, x="status", y="count")
            style_plotly_figure(fig)
            st.plotly_chart(fig, use_container_width=True)

        with chart_col_2:
            matched_types = [
                classify_skill_type(skill, taxonomy) for skill in gap_result.get("matched_skills", [])
            ]
            type_counts = pd.Series(matched_types).value_counts().reset_index()
            type_counts.columns = ["skill_type", "count"]
            fig2 = px.pie(type_counts, names="skill_type", values="count", hole=0.45)
            style_plotly_figure(fig2)
            st.plotly_chart(fig2, use_container_width=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Matched", "Missing Core", "Missing Helpful", "Soft Gaps", "Career Actions"]
        )
        with tab1:
            st.dataframe(pd.DataFrame({"skill": gap_result.get("matched_skills", [])}), use_container_width=True)
        with tab2:
            st.dataframe(pd.DataFrame({"skill": gap_result.get("missing_core_skills", [])}), use_container_width=True)
        with tab3:
            st.dataframe(pd.DataFrame({"skill": gap_result.get("missing_helpful_skills", [])}), use_container_width=True)
        with tab4:
            st.dataframe(pd.DataFrame({"skill": gap_result.get("soft_skill_gaps", [])}), use_container_width=True)
        with tab5:
            if actions_df.empty:
                st.info("No career actions matched. Try selecting a different role or adding more CV detail.")
            else:
                st.dataframe(actions_df, use_container_width=True)

        with st.expander("Category skill taxonomy preview"):
            st.dataframe(skill_type_df.head(30), use_container_width=True)

        st.download_button(
            label="Download Career Action Plan",
            data=action_plan.encode("utf-8"),
            file_name="career_action_plan.txt",
            mime="text/plain",
        )

with st.expander("How this analyzer works"):
    st.markdown("- Rule-based skill extraction from text (no paid LLM APIs).")
    st.markdown("- Market mode compares against job dataset skills.")
    st.markdown("- Career mode compares against curated role profiles.")
    st.markdown("- Results are guidance, not hiring decisions.")

with st.expander("Limitations"):
    st.markdown("- Sample job data is synthetic unless you import your own CSV.")
    st.markdown("- Curated role profiles are simplified and vary by country/company.")
    st.markdown("- Skill detection depends on taxonomy coverage and CV wording.")
