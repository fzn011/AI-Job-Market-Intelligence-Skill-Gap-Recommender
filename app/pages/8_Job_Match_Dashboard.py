"""Job Match Score Dashboard — paste a job description and CV for instant fit scoring."""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.job_match_utils import (  # noqa: E402
    build_job_match_dataframe,
    classify_job_match_level,
    compute_job_match,
    generate_job_match_report,
)
from src.learning_resource_utils import get_resources_for_skills  # noqa: E402
from src.progress_tracker_utils import increment_stat, record_gap_analysis  # noqa: E402
from src.ui_theme import apply_global_theme, render_brand_header, render_info_box, style_plotly_figure  # noqa: E402


st.set_page_config(page_title="Job Match Dashboard", page_icon="🎯", layout="wide")
apply_global_theme()

render_brand_header(
    app_name="CareerCompass · Job Match Dashboard",
    subtitle="Paste any job description and your CV to get an instant, transparent fit score.",
)

render_info_box(
    "How it works",
    "Skills are extracted using the local skill dictionary with synonym expansion (e.g., JS → javascript, PowerBI → power bi). "
    "No paid AI APIs are used.",
)

job_title = st.text_input("Job Title (optional)", placeholder="e.g., Data Analyst, Frontend Developer")
col1, col2 = st.columns(2)
with col1:
    job_description = st.text_area(
        "Job Description",
        height=280,
        placeholder="Paste the full job description here...",
    )
with col2:
    cv_text = st.text_area(
        "Your CV / Profile",
        height=280,
        placeholder="Paste your CV, resume, or LinkedIn About section...",
    )

analyze = st.button("Calculate Job Match Score", type="primary", use_container_width=True)

if analyze:
    if not job_description.strip() or not cv_text.strip():
        st.warning("Please paste both a job description and CV text.")
        st.stop()

    result = compute_job_match(job_description, cv_text)
    if result.get("message"):
        st.info(result["message"])

    increment_stat("job_matches")
    record_gap_analysis(
        mode="job_match",
        target_role=job_title or "Job Match",
        match_score=float(result.get("match_score", 0.0)),
        cv_skills=result.get("cv_skills", []),
        missing_skills=result.get("missing_skills", []),
        matched_skills=result.get("matched_skills", []),
    )

    st.markdown("---")
    metrics = st.columns(5)
    metrics[0].metric("Match Score", f"{result['match_score']:.2f}%")
    metrics[1].metric("Match Level", classify_job_match_level(float(result["match_score"])))
    metrics[2].metric("Job Skills", result.get("job_skill_count", 0))
    metrics[3].metric("CV Skills", result.get("cv_skill_count", 0))
    metrics[4].metric("Missing", result.get("missing_count", 0))

    chart_col1, chart_col2 = st.columns(2)
    match_df = build_job_match_dataframe(result)
    with chart_col1:
        if not match_df.empty:
            status_counts = match_df["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            fig = px.pie(status_counts, names="status", values="count", hole=0.45)
            style_plotly_figure(fig)
            st.plotly_chart(fig, use_container_width=True)
    with chart_col2:
        if not match_df.empty:
            fig2 = px.bar(match_df, x="job_skill", y=[1] * len(match_df), color="status")
            fig2.update_layout(showlegend=True, yaxis_visible=False)
            style_plotly_figure(fig2)
            st.plotly_chart(fig2, use_container_width=True)

    tab1, tab2, tab3 = st.tabs(["Skill Breakdown", "Learning Resources", "Download"])
    with tab1:
        st.dataframe(match_df, use_container_width=True)
    with tab2:
        resources = get_resources_for_skills(result.get("missing_skills", []))
        if resources.empty:
            st.info("No curated resources for these missing skills yet.")
        else:
            st.dataframe(resources, use_container_width=True)
    with tab3:
        report = generate_job_match_report(result, job_title)
        st.download_button("Download Match Report", data=report.encode("utf-8"), file_name="job_match_report.txt")
        try:
            from src.pdf_report_utils import build_gap_pdf_sections, generate_career_pdf_report

            sections = build_gap_pdf_sections(
                target_role=job_title or "Job Match",
                match_score=float(result["match_score"]),
                matched_skills=result.get("matched_skills", []),
                missing_skills=result.get("missing_skills", []),
            )
            pdf_bytes = generate_career_pdf_report("CareerCompass Job Match Report", sections)
            st.download_button("Download PDF Report", data=pdf_bytes, file_name="job_match_report.pdf", mime="application/pdf")
            increment_stat("pdf_exports")
        except ImportError:
            st.caption("Install reportlab for PDF export: pip install reportlab")

with st.expander("Limitations"):
    st.markdown("- Match score depends on skill dictionary coverage.")
    st.markdown("- Synonym expansion helps but cannot capture every job-board wording.")
    st.markdown("- This is guidance, not an official application screening result.")
