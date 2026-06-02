"""CV Skill Gap Analyzer dashboard page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
from src.dashboard_utils import load_processed_jobs  # noqa: E402
from src.skill_analysis_utils import (  # noqa: E402
    build_skill_category_lookup,
    load_skill_dictionary_for_analysis,
)


st.set_page_config(page_title="CV Skill Gap Analyzer", page_icon="📄", layout="wide")

st.title("📄 CV Skill Gap Analyzer")
st.caption(
    "Paste your CV or profile text, select a target role, and compare your skills against market demand."
)

jobs_df = load_processed_jobs()
if jobs_df.empty:
    st.warning("Processed job data was not found. Please run: python scripts/run_project_check.py")
    st.stop()

skill_dictionary = load_skill_dictionary_for_analysis()
if not skill_dictionary:
    st.warning("Skill dictionary was not found. Please check data/sample/skills_dictionary.json")
    st.stop()

category_lookup = build_skill_category_lookup(skill_dictionary)

target_role_options = [
    "Overall Market",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "BI Analyst",
    "Data Engineer",
    "GenAI Engineer",
    "Risk Data Analyst",
    "Product Data Analyst",
    "Junior Data Scientist",
]

left_col, right_col = st.columns([1.5, 1])

with left_col:
    cv_text = st.text_area(
        "Paste CV / Resume / Profile Text",
        height=300,
        placeholder="Paste your resume, LinkedIn About section, or project profile here...",
    )

    target_role = st.selectbox("Select Target Role", options=target_role_options, index=0)
    use_top_25 = st.checkbox("Use top 25 market skills only", value=True)
    analyze_clicked = st.button("Analyze Skill Gap", type="primary")

with right_col:
    st.subheader("How to use")
    st.markdown("1. Paste your CV/profile text on the left")
    st.markdown("2. Select your target role")
    st.markdown("3. Click **Analyze Skill Gap**")

    with st.expander("Example CV snippet"):
        st.code(
            """Data Scientist with hands-on experience in Python, SQL, pandas, scikit-learn,
Power BI, and A/B testing. Built machine learning models for churn prediction,
deployed FastAPI endpoints, and tracked experiments with MLflow.""",
            language="text",
        )

    with st.expander("What this analyzer checks"):
        st.markdown("- Skills detected in your CV text")
        st.markdown("- Top skills demanded in current job-market sample")
        st.markdown("- Match score, missing skills, and extra profile strengths")
        st.markdown("- Prioritized learning and project recommendations")

top_n = 25 if use_top_25 else None
run_analysis = analyze_clicked or bool(cv_text.strip())

if run_analysis:
    if not cv_text.strip():
        st.warning("Please paste your CV or profile text first.")
        st.stop()

    cv_skills = extract_cv_skills(cv_text=cv_text, skill_dictionary=skill_dictionary)
    if not cv_skills:
        st.warning(
            "No known skills were detected from the CV text. Try adding technical skills, tools, projects, or coursework."
        )
        st.stop()

    market_skills = get_market_skills_by_target_role(
        jobs_df=jobs_df,
        target_role=target_role,
        top_n=top_n,
    )

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

    st.markdown("---")
    st.subheader("Skill Match Visualizations")

    status_counts_df = pd.DataFrame(
        {
            "status": ["Matched", "Missing", "Extra in CV"],
            "count": [
                gap_result["matched_count"],
                gap_result["missing_count"],
                len(gap_result.get("extra_cv_skills", [])),
            ],
        }
    )

    chart_col_1, chart_col_2 = st.columns(2)
    with chart_col_1:
        fig_status = px.bar(
            status_counts_df,
            x="status",
            y="count",
            labels={"status": "Skill Status", "count": "Count"},
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with chart_col_2:
        matched_missing_df = status_counts_df[status_counts_df["status"].isin(["Matched", "Missing"])]
        fig_donut = px.pie(
            matched_missing_df,
            names="status",
            values="count",
            hole=0.5,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    chart_col_3, chart_col_4 = st.columns(2)
    with chart_col_3:
        if gap_df.empty:
            st.info("No skill gap rows are available to show category breakdown.")
        else:
            category_status_df = (
                gap_df.groupby(["category", "status"], as_index=False).size()
                .rename(columns={"size": "count"})
            )
            fig_category = px.bar(
                category_status_df,
                x="category",
                y="count",
                color="status",
                barmode="group",
                labels={"count": "Count", "category": "Skill Category"},
            )
            fig_category.update_layout(xaxis_tickangle=-25)
            st.plotly_chart(fig_category, use_container_width=True)

    with chart_col_4:
        coverage_rows = [
            {"market_skill": skill, "covered": 1 if skill in set(gap_result["matched_skills"]) else 0}
            for skill in market_skills
        ]
        coverage_df = pd.DataFrame(coverage_rows)
        if coverage_df.empty:
            st.info("No market skills available for coverage view.")
        else:
            fig_coverage = px.bar(
                coverage_df.iloc[::-1],
                x="covered",
                y="market_skill",
                orientation="h",
                labels={"covered": "Coverage (1=Matched, 0=Missing)", "market_skill": "Market Skill"},
            )
            st.plotly_chart(fig_coverage, use_container_width=True)

    st.markdown("---")
    st.subheader("Skill Results")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Matched Skills", "Missing Skills", "Extra CV Skills", "Full Skill Gap Table"]
    )

    with tab1:
        matched = gap_result.get("matched_skills", [])
        if matched:
            st.dataframe(pd.DataFrame({"matched_skill": matched}), use_container_width=True)
        else:
            st.info("No matched skills identified yet.")

    with tab2:
        missing = gap_result.get("missing_skills", [])
        if missing:
            st.dataframe(pd.DataFrame({"missing_skill": missing}), use_container_width=True)
            st.caption("These are the highest-priority opportunities for improving role alignment.")
        else:
            st.success("Great work—no missing skills in the selected market comparison set.")

    with tab3:
        extra = gap_result.get("extra_cv_skills", [])
        if extra:
            st.dataframe(pd.DataFrame({"extra_skill_in_cv": extra}), use_container_width=True)
        else:
            st.info("No extra CV skills relative to the selected market list.")
        st.caption(
            "Extra CV skills are not bad; they may still be valuable, even if not top-demanded in this sample."
        )

    with tab4:
        st.dataframe(gap_df, use_container_width=True)
        st.download_button(
            label="Download Skill Gap Table",
            data=gap_df.to_csv(index=False).encode("utf-8"),
            file_name="cv_skill_gap_table.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.subheader("Recommended Learning and Project Path")

    st.caption(
        "High priority skills are foundational or frequently requested. Medium skills strengthen production readiness. Low priority skills are useful but less urgent."
    )

    if recommendations:
        recommendations_df = pd.DataFrame(recommendations)
        priority_order = pd.CategoricalDtype(categories=["High", "Medium", "Low"], ordered=True)
        recommendations_df["priority"] = recommendations_df["priority"].astype(priority_order)
        recommendations_df = recommendations_df.sort_values(["priority", "skill"]).reset_index(drop=True)
        recommendations_df["priority"] = recommendations_df["priority"].astype(str)
        st.dataframe(
            recommendations_df[["skill", "priority", "difficulty", "recommendation", "project_idea"]],
            use_container_width=True,
        )
    else:
        st.success("No missing skills detected, so no immediate learning gaps were found.")

    st.markdown("---")
    st.subheader("Quick Insights")
    for insight in insights:
        st.markdown(f"- {insight}")

    st.markdown("---")
    st.subheader("Download Report")
    st.download_button(
        label="Download CV Skill Gap Report",
        data=report_text.encode("utf-8"),
        file_name="cv_skill_gap_report.txt",
        mime="text/plain",
    )

    with st.expander("How this analyzer works"):
        st.markdown("- It uses a predefined skill dictionary.")
        st.markdown("- It extracts skills from pasted CV text using rule-based matching.")
        st.markdown("- It compares those skills against extracted job-market skills.")
        st.markdown("- It does not use paid AI APIs.")
        st.markdown("- It is not a hiring decision.")
        st.markdown("- Results depend on the current job dataset and skill dictionary.")

    with st.expander("How to improve your score"):
        st.markdown("- Add missing skills only if you genuinely know them.")
        st.markdown("- Build projects around missing skills.")
        st.markdown("- Add tools and methods clearly in CV bullets.")
        st.markdown("- Use role-specific language.")
        st.markdown("- Keep project links visible.")

    with st.expander("Data Quality Notes"):
        st.markdown(f"- Number of jobs used: **{len(jobs_df)}**")
        st.markdown(f"- Selected target role: **{target_role}**")
        st.markdown(f"- Number of market skills compared: **{len(market_skills)}**")
        st.markdown(f"- Number of categories in dictionary: **{len(skill_dictionary.keys())}**")
        st.markdown("- Current limitation: sample/synthetic data until real job data collection is added")
