"""Main Streamlit dashboard entry point."""

from pathlib import Path
import ast
import pandas as pd
import streamlit as st

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Job Market Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
)


def _safe_count_extracted_skills(df: pd.DataFrame) -> int:
    """Count total extracted skills from the extracted_skills column safely."""
    if "extracted_skills" not in df.columns:
        return 0

    total = 0
    for value in df["extracted_skills"]:
        if isinstance(value, list):
            total += len(value)
        elif isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                try:
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, list):
                        total += len(parsed)
                except (SyntaxError, ValueError):
                    continue
    return total


project_root = Path(__file__).resolve().parents[1]
processed_path = project_root / "data" / "processed" / "processed_sample_jobs.csv"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 AI Job Market Intelligence")
    st.markdown("---")
    st.markdown(
        """
        **Navigation**

        Use the pages in the sidebar to explore:
        - 🗺️ Job Market Overview
        - 🔬 Skill Demand Analysis
        - 📄 CV Skill Gap Analyzer
        - 🚀 Project Recommendations
        """
    )
    st.markdown("---")
    st.caption("v0.1.0 · Open-source · Free tools only")

# ── Main content ──────────────────────────────────────────────────────────────
st.title("📊 AI Job Market Intelligence Dashboard")
st.markdown(
    """
    **Understand the AI job market. Identify your skill gaps. Get actionable recommendations.**
    """
)

st.markdown("---")

st.subheader("Project Status")

if processed_path.exists():
    try:
        processed_df = pd.read_csv(processed_path)
        st.success("✅ Processed sample data found.")
        st.write(f"**Number of jobs:** {len(processed_df)}")
        st.dataframe(processed_df.head(10), use_container_width=True)

        total_skills = _safe_count_extracted_skills(processed_df)
        if total_skills > 0:
            st.write(f"**Total extracted skills (rows combined):** {total_skills}")
    except Exception as exc:
        st.warning(f"Processed file exists but could not be loaded: {exc}")
else:
    st.info(
        "Processed sample data not found yet. Run `python scripts/run_project_check.py` "
        "from the project root first."
    )

st.markdown("---")

st.markdown(
    """
    This tool analyses job descriptions, extracts in-demand skills, and compares them
    against your profile to recommend exactly what to learn and build next.

    All processing is done locally using open-source Python libraries — no paid APIs required.
    """
)

st.markdown("---")
st.subheader("Planned Modules")

col1, col2 = st.columns(2)

with col1:
    st.info(
        """
        **🗺️ 1. Job Market Overview**

        Explore the current AI and data job market.
        View top job titles, locations, and hiring trends.
        """
    )
    st.info(
        """
        **📄 3. CV Skill Gap Analyzer**

        Paste or upload your CV.
        See exactly which skills you have and which you are missing
        relative to your target roles.
        """
    )

with col2:
    st.info(
        """
        **🔬 2. Skill Demand Analysis**

        See which skills appear most frequently across job postings.
        Drill down by job category or role type.
        """
    )
    st.info(
        """
        **🚀 4. Project Recommendation Engine**

        Get a personalised list of portfolio projects to build
        in order to close your skill gap efficiently.
        """
    )

st.markdown("---")
st.caption("Built with Python · Streamlit · scikit-learn · open-source NLP")
