"""Career Intelligence Hub — company prep, salary, LinkedIn, peer benchmark, voice interview, study calendar."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.career_taxonomy_utils import get_roles_for_category, list_career_categories, recommend_career_actions  # noqa: E402
from src.company_prep_utils import (  # noqa: E402
    build_company_prep_summary,
    get_company_pack,
    get_company_skill_overlap,
    list_companies,
)
from src.dashboard_utils import load_active_jobs_dataset  # noqa: E402
from src.job_match_utils import extract_cv_skills_enhanced  # noqa: E402
from src.linkedin_optimizer_utils import optimize_linkedin_about  # noqa: E402
from src.peer_benchmark_utils import build_peer_benchmark_dataframe, compute_peer_benchmark  # noqa: E402
from src.regional_profiles_utils import get_regional_target_skills, list_regions  # noqa: E402
from src.salary_estimator_utils import estimate_salary_band, format_salary_estimate_text, list_salary_regions  # noqa: E402
from src.semantic_skill_utils import get_semantic_match_scores, semantic_model_available  # noqa: E402
from src.skill_analysis_utils import load_skill_dictionary_for_analysis  # noqa: E402
from src.skill_extraction import extract_skills_from_text, flatten_skill_dictionary  # noqa: E402
from src.study_calendar_utils import generate_study_plan_ics  # noqa: E402
from src.ui_theme import apply_global_theme, render_brand_header, render_info_box, style_plotly_figure  # noqa: E402
from src.voice_interview_utils import create_interview_session, format_session_report, score_interview_session  # noqa: E402


st.set_page_config(page_title="Career Intelligence Hub", page_icon="🧠", layout="wide")
apply_global_theme()

render_brand_header(
    app_name="CareerCompass · Career Intelligence Hub",
    subtitle="Company prep packs, salary estimates, LinkedIn optimization, peer benchmarks, voice interview practice, and study calendars.",
)

available, model_info = semantic_model_available()
render_info_box(
    "Semantic skill matching",
    f"Local sentence-transformers model: {'available' if available else 'unavailable'} ({model_info}). "
    "Enable on the Semantic Matching tab — no paid AI APIs.",
)

tabs = st.tabs([
    "Company Prep",
    "Salary Estimator",
    "LinkedIn Optimizer",
    "Peer Benchmark",
    "Voice Interview",
    "Study Calendar",
    "Semantic Matching",
])

with tabs[0]:
    st.subheader("Company-Specific Prep Packs")
    companies = list_companies()
    c1, c2 = st.columns(2)
    with c1:
        company = st.selectbox("Company", options=companies)
    with c2:
        role = st.text_input("Target role", value="Data Analyst")
    cv_for_company = st.text_area("Your CV / profile (optional)", height=120)
    if st.button("Generate Company Prep Pack", type="primary"):
        cv_skills = extract_cv_skills_enhanced(cv_for_company) if cv_for_company.strip() else []
        pack = get_company_pack(company)
        missing = sorted(set(pack.get("hiring_focus", [])) - set(cv_skills))
        summary = build_company_prep_summary(company, role, missing)
        st.text(summary)
        if cv_skills:
            overlap_df = get_company_skill_overlap(company, cv_skills)
            st.dataframe(overlap_df, use_container_width=True)
        st.download_button("Download Prep Pack", data=summary.encode("utf-8"), file_name=f"{company.lower()}_prep.txt")

with tabs[1]:
    st.subheader("Salary Band Estimator")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        salary_role = st.text_input("Role", value="Data Analyst", key="salary_role")
    with s2:
        salary_region = st.selectbox("Region", options=list_salary_regions() or list_regions())
    with s3:
        experience = st.selectbox("Experience", options=["entry", "mid", "senior"])
    with s4:
        match_score = st.slider("Skill match score", 0, 100, 55)
    if st.button("Estimate Salary Band", type="primary"):
        result = estimate_salary_band(salary_role, salary_region, match_score, experience)
        if result.get("available"):
            st.metric("Estimated Range", f"{result['estimated_range']} {result['currency']}")
            st.metric("Market Band", f"{result['market_band']} {result['currency']}")
            st.info(result["positioning"])
        st.text(format_salary_estimate_text(result))

with tabs[2]:
    st.subheader("LinkedIn About Optimizer")
    about = st.text_area("Paste LinkedIn About section", height=200)
    l1, l2 = st.columns(2)
    with l1:
        li_role = st.text_input("Target role", value="Data Analyst", key="li_role")
    with l2:
        li_cat = st.selectbox("Category", options=list_career_categories(), key="li_cat")
    li_roles = get_roles_for_category(li_cat)
    li_role_name = st.selectbox("Role profile", options=li_roles or ["General"], key="li_role_name")
    target_skills = get_regional_target_skills(li_cat, li_role_name, "Global") if li_roles else []
    if st.button("Optimize LinkedIn About", type="primary"):
        result = optimize_linkedin_about(about, li_role, target_skills)
        st.markdown("**Optimized About**")
        st.text_area("Optimized", value=result["optimized_text"], height=220)
        st.markdown("**Suggestions**")
        for tip in result["suggestions"]:
            st.markdown(f"- {tip}")

with tabs[3]:
    st.subheader("Peer Comparison Benchmark")
    peer_cv = st.text_area("Paste CV for benchmark", height=160)
    peer_role = st.text_input("Target role", value="Data Analyst", key="peer_role")
    jobs_df = load_active_jobs_dataset()
    if st.button("Run Peer Benchmark", type="primary") and peer_cv.strip():
        result = compute_peer_benchmark(peer_cv, peer_role, jobs_df)
        if result.get("available"):
            st.metric("Percentile", f"{result['percentile']}%")
            st.success(result["tier_label"])
            st.dataframe(build_peer_benchmark_dataframe(result), use_container_width=True)
            fig = px.bar(x=["You", "Peer Median"], y=[result["user_score_proxy"], result["peer_median"]])
            style_plotly_figure(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(result.get("message", "Benchmark unavailable."))

with tabs[4]:
    st.subheader("Voice Interview Simulator")
    v1, v2, v3 = st.columns(3)
    with v1:
        vi_role = st.text_input("Role", value="Data Analyst", key="vi_role")
    with v2:
        num_q = st.slider("Questions", 3, 8, 5)
    with v3:
        seconds = st.slider("Seconds per question", 60, 300, 120)

    vi_skills = st.multiselect("Focus skills", options=["python", "sql", "communication", "problem solving", "machine learning"])

    if "vi_session" not in st.session_state:
        st.session_state["vi_session"] = None

    if st.button("Start Interview Session", type="primary"):
        st.session_state["vi_session"] = create_interview_session(vi_skills, vi_role, num_q, seconds)
        st.session_state["vi_current"] = 0
        st.session_state["vi_ratings"] = []
        st.session_state["vi_started_at"] = time.time()

    session = st.session_state.get("vi_session")
    if session:
        current = st.session_state.get("vi_current", 0)
        questions = session["questions"]
        if current < len(questions):
            elapsed = int(time.time() - st.session_state.get("vi_started_at", time.time()))
            remaining = max(0, session["seconds_per_question"] - elapsed)
            st.warning(f"Question {current + 1}/{len(questions)} · Time remaining: {remaining}s")
            st.markdown(f"**{questions[current]}**")
            rubric_dims = session.get("rubric_dimensions", [])
            ratings = {}
            cols = st.columns(len(rubric_dims))
            for idx, dim in enumerate(rubric_dims):
                with cols[idx]:
                    ratings[dim] = st.slider(dim.replace("_", " ").title(), 1, 5, 3, key=f"vi_{current}_{dim}")
            if st.button("Next Question"):
                st.session_state["vi_ratings"].append({"question": questions[current], **ratings})
                st.session_state["vi_current"] = current + 1
                st.session_state["vi_started_at"] = time.time()
                st.rerun()
        else:
            score = score_interview_session(questions, st.session_state.get("vi_ratings", []))
            st.metric("Overall Score", f"{score['overall_score']}/5")
            st.success(score["readiness"])
            st.dataframe(pd.DataFrame(score["question_scores"]), use_container_width=True)
            report = format_session_report(session, score)
            st.download_button("Download Session Report", data=report.encode("utf-8"), file_name="voice_interview_report.txt")

with tabs[5]:
    st.subheader("4-Week Study Plan Calendar")
    cat = st.selectbox("Category", options=list_career_categories(), key="cal_cat")
    roles = get_roles_for_category(cat)
    cal_role = st.selectbox("Role", options=roles or ["General"], key="cal_role")
    default_skills = get_regional_target_skills(cat, cal_role, "Global") if roles else []
    missing_skills = st.multiselect("Skills to address", options=default_skills, default=default_skills[:4], key="cal_skills")
    if st.button("Generate ICS Calendar", type="primary"):
        actions_df = recommend_career_actions(missing_skills, cat, max_actions=4)
        actions = actions_df.to_dict("records") if not actions_df.empty else []
        ics = generate_study_plan_ics(actions, f"CareerCompass Plan — {cal_role}")
        st.download_button("Download 4-Week Study Plan (.ics)", data=ics.encode("utf-8"), file_name="career_study_plan.ics", mime="text/calendar")

with tabs[6]:
    st.subheader("Semantic Skill Matching")
    sem_text = st.text_area("Text to analyze", height=140, placeholder="Paste CV or job description...")
    skill_dict = load_skill_dictionary_for_analysis()
    all_skills = flatten_skill_dictionary(skill_dict) if skill_dict else []
    use_both = st.checkbox("Combine regex + semantic extraction", value=True)
    if st.button("Run Semantic Analysis", type="primary") and sem_text.strip():
        regex_skills = extract_skills_from_text(sem_text, all_skills, use_semantic=False)
        sem_skills = extract_skills_from_text(sem_text, all_skills, use_semantic=True) if use_both else []
        scores = get_semantic_match_scores(sem_text, all_skills[:40])
        st.markdown(f"**Regex skills:** {', '.join(regex_skills) or 'None'}")
        st.markdown(f"**Combined skills:** {', '.join(sem_skills) or 'None'}")
        if scores:
            score_df = pd.DataFrame(scores[:15])
            fig = px.bar(score_df, x="semantic_score", y="skill", orientation="h")
            style_plotly_figure(fig)
            st.plotly_chart(fig, use_container_width=True)
