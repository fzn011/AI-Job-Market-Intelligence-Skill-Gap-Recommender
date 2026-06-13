"""Career Toolkit — progress tracking, multi-CV comparison, interview prep, resume bullets, badges."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.career_taxonomy_utils import get_roles_for_category, list_career_categories  # noqa: E402
from src.cv_comparison_utils import build_cv_comparison_dataframe, compare_cv_versions, generate_cv_comparison_report  # noqa: E402
from src.gamification_utils import evaluate_badges, get_badges_dataframe, get_earned_badge_count  # noqa: E402
from src.interview_question_utils import generate_interview_prep_text, generate_interview_questions  # noqa: E402
from src.progress_tracker_utils import compute_progress_skill_growth, get_gap_history_dataframe, increment_stat  # noqa: E402
from src.regional_profiles_utils import list_regions  # noqa: E402
from src.resume_bullet_utils import format_resume_bullets_text, generate_resume_bullets  # noqa: E402
from src.email_digest_utils import build_weekly_digest_text, send_weekly_digest, smtp_configured  # noqa: E402
from src.ui_theme import apply_global_theme, render_app_footer, render_brand_header, render_info_box, style_plotly_figure  # noqa: E402


st.set_page_config(page_title="Career Toolkit", page_icon="🛠️", layout="wide")
apply_global_theme()

render_brand_header(
    app_name="CareerCompass · Career Toolkit",
    subtitle="Track progress, compare CVs, prepare for interviews, rewrite resume bullets, and earn badges.",
)

tool_tab = st.tabs([
    "Progress Tracker",
    "Multi-CV Comparison",
    "Interview Prep",
    "Resume Bullets",
    "Email Digest",
    "Badges",
])

with tool_tab[0]:
    st.subheader("Career Progress Tracker")
    history_df = get_gap_history_dataframe()
    growth = compute_progress_skill_growth()

    metric_cols = st.columns(4)
    metric_cols[0].metric("Analyses Saved", len(history_df))
    metric_cols[1].metric("Badges Earned", get_earned_badge_count())
    if growth.get("available"):
        metric_cols[2].metric("Skill Growth", f"{growth.get('growth_percent', 0.0)}%")
        metric_cols[3].metric("Match Score Δ", f"{growth.get('match_score_delta', 0.0):+.2f}%")
    else:
        metric_cols[2].metric("Skill Growth", "N/A")
        metric_cols[3].caption(growth.get("message", ""))

    if history_df.empty:
        st.info("No gap analyses saved yet. Run analyses on CV Gap or Job Match pages.")
    else:
        st.dataframe(history_df.sort_values("timestamp", ascending=False), use_container_width=True)
        fig = px.line(
            history_df.sort_values("timestamp"),
            x="timestamp",
            y="match_score",
            markers=True,
            labels={"match_score": "Match Score", "timestamp": "Analysis Time"},
        )
        style_plotly_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

        if growth.get("available"):
            st.markdown("**Latest skill growth**")
            st.markdown(f"- Gained: {', '.join(growth.get('gained_skills', [])) or 'None'}")
            st.markdown(f"- Lost: {', '.join(growth.get('lost_skills', [])) or 'None'}")

with tool_tab[1]:
    st.subheader("Multi-CV Comparison")
    render_info_box("Compare versions", "Paste two CV versions to see gained/lost skills side-by-side.")
    c1, c2 = st.columns(2)
    with c1:
        label_a = st.text_input("Label A", value="Original CV")
        cv_a = st.text_area("CV Version A", height=220, key="cv_a")
    with c2:
        label_b = st.text_input("Label B", value="Updated CV")
        cv_b = st.text_area("CV Version B", height=220, key="cv_b")

    if st.button("Compare CV Versions", type="primary", key="compare_cv_btn"):
        if not cv_a.strip() or not cv_b.strip():
            st.warning("Paste both CV versions.")
        else:
            comparison = compare_cv_versions(cv_a, cv_b, label_a, label_b)
            increment_stat("cv_comparisons")
            st.session_state["cv_comparison"] = comparison

    if "cv_comparison" in st.session_state:
        comparison = st.session_state["cv_comparison"]
        comp_df = build_cv_comparison_dataframe(comparison)
        st.dataframe(comp_df, use_container_width=True)
        st.download_button(
            "Download Comparison Report",
            data=generate_cv_comparison_report(comparison).encode("utf-8"),
            file_name="cv_comparison_report.txt",
        )

with tool_tab[2]:
    st.subheader("Interview Question Generator")
    categories = list_career_categories()
    if not categories:
        st.error("Career taxonomies not found. Run: python scripts/generate_career_taxonomies.py or .\\setup.ps1")
        categories = ["Data & AI"]
    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        category = st.selectbox("Category", options=categories, key="interview_cat")
    with ic2:
        roles = get_roles_for_category(category)
        role = st.selectbox("Target Role", options=roles or ["General"], key="interview_role")
    with ic3:
        region = st.selectbox("Region", options=list_regions(), key="interview_region")

    from src.regional_profiles_utils import get_regional_target_skills

    default_missing = get_regional_target_skills(category, role, region)[:8]
    missing = st.multiselect("Focus skills / gaps", options=default_missing, default=default_missing[:5])

    if st.button("Generate Interview Questions", type="primary", key="interview_btn"):
        q_df = generate_interview_questions(missing, role)
        increment_stat("interview_preps")
        st.session_state["interview_questions"] = q_df
        st.session_state["interview_role"] = role

    if "interview_questions" in st.session_state:
        q_df = st.session_state["interview_questions"]
        role = st.session_state.get("interview_role", role)
        st.dataframe(q_df, use_container_width=True)
        st.download_button(
            "Download Interview Prep",
            data=generate_interview_prep_text(q_df, role).encode("utf-8"),
            file_name="interview_prep.txt",
        )

with tool_tab[3]:
    st.subheader("Resume Bullet Rewriter")
    rc1, rc2 = st.columns(2)
    with rc1:
        r_role = st.text_input("Target Role", value="Data Analyst")
        matched = st.text_area("Matched skills (comma-separated)", value="python, sql, power bi")
    with rc2:
        missing_input = st.text_area("Missing skills (comma-separated)", value="docker, machine learning")

    if st.button("Generate ATS Resume Bullets", type="primary", key="resume_btn"):
        matched_list = [s.strip().lower() for s in matched.split(",") if s.strip()]
        missing_list = [s.strip().lower() for s in missing_input.split(",") if s.strip()]
        bullets = generate_resume_bullets(matched_list, missing_list, r_role)
        increment_stat("resume_bullets")
        st.session_state["resume_bullets"] = bullets
        st.session_state["resume_role"] = r_role

    if "resume_bullets" in st.session_state:
        bullets = st.session_state["resume_bullets"]
        r_role = st.session_state.get("resume_role", r_role)
        for item in bullets:
            st.markdown(f"- **{item['bullet_type']}:** {item['bullet']}")
        st.download_button(
            "Download Resume Bullets",
            data=format_resume_bullets_text(bullets, r_role).encode("utf-8"),
            file_name="resume_bullets.txt",
        )

with tool_tab[4]:
    st.subheader("Weekly Email Progress Digest")
    render_info_box(
        "Optional SMTP",
        "Configure SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, and DIGEST_RECIPIENT in `.streamlit/secrets.toml`. "
        "Use an app password for Gmail. Digest sends a summary of your analyses and badges.",
    )
    preview = build_weekly_digest_text()
    st.text_area("Digest preview", value=preview, height=220)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Send Weekly Digest", type="primary"):
            result = send_weekly_digest(dry_run=not smtp_configured())
            if result.get("sent"):
                st.success(result["message"])
            else:
                st.info(result["message"])
    with c2:
        st.caption(f"SMTP configured: {'Yes' if smtp_configured() else 'No — preview only'}")

with tool_tab[5]:
    st.subheader("Gamification Badges")
    badges_df = get_badges_dataframe()
    evaluate_badges()
    earned = int(badges_df["earned"].sum()) if not badges_df.empty else 0
    st.metric("Badges Earned", f"{earned}/{len(badges_df)}")
    if badges_df.empty:
        st.info("No badges configured.")
    else:
        st.dataframe(badges_df, use_container_width=True)
        earned_badges = badges_df[badges_df["earned"]]
        for _, row in earned_badges.iterrows():
            st.success(f"🏅 {row['title']} — {row['description']}")

render_app_footer(show_tech_line=False)
