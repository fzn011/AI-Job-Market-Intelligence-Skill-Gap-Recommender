"""Main Streamlit dashboard entry point."""

import sys
from pathlib import Path
import ast
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard_utils import get_active_dataset_label, load_active_jobs_dataset  # noqa: E402
from src.ui_theme import apply_global_theme, render_brand_header  # noqa: E402

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


apply_global_theme()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("EmberScope AI")
    st.markdown("---")
    st.markdown(
        """
        **Navigation**

        Use the pages in the sidebar to explore:
        - 🗺️ Job Market Overview
        - 🔬 Skill Demand Analysis
        - 📄 CV Skill Gap Analyzer
        - 🚀 Project Recommendations
        - 🧠 Role Segmentation + Job Clustering
        - 📥 Data Import & Dataset Manager
        """
    )
    st.markdown("---")
    dataset_preference = st.selectbox("Dataset Source", options=["Auto", "Imported", "Sample"], index=0)
    preferred_mode = dataset_preference.strip().lower()
    st.caption(f"Active dataset: {get_active_dataset_label(preferred=preferred_mode)}")
    st.markdown("---")
    st.caption("v0.1.0 · Open-source · Free tools only")

# ── Main content ──────────────────────────────────────────────────────────────
render_brand_header(
    app_name="EmberScope AI",
    subtitle="Understand the market. Map your skill gap. Build your next move.",
    logo_mark="◜●◝",
)

st.markdown("---")

st.subheader("Project Status")

processed_df = load_active_jobs_dataset(preferred=preferred_mode)
if not processed_df.empty:
    try:
        st.success(f"✅ {get_active_dataset_label(preferred=preferred_mode)} found.")
        st.write(f"**Number of jobs:** {len(processed_df)}")
        st.dataframe(processed_df.head(10), use_container_width=True)

        total_skills = _safe_count_extracted_skills(processed_df)
        if total_skills > 0:
            st.write(f"**Total extracted skills (rows combined):** {total_skills}")
    except Exception as exc:
        st.warning(f"Processed file exists but could not be loaded: {exc}")
else:
    st.info(
        "No processed dataset found for this selection. Run `python scripts/run_project_check.py` "
        "or import data via `python scripts/import_jobs_from_csv.py --demo expanded`."
    )

st.info(
    "✅ The first working dashboard page is **Job Market Overview**. "
    "Open it from the Streamlit sidebar: `Pages -> 1_Job_Market_Overview`."
)

st.info(
    "✅ The second working dashboard page is **Skill Demand Analysis**. "
    "Open it from the Streamlit sidebar: `Pages -> 2_Skill_Analysis`."
)

st.info(
    "✅ The third working dashboard page is **CV Skill Gap Analyzer**. "
    "Open it from the Streamlit sidebar: `Pages -> 3_CV_Skill_Gap`."
)

st.info(
    "✅ The fourth working dashboard page is **Project Recommendation Engine**. "
    "Open it from the Streamlit sidebar: `Pages -> 4_Project_Recommendations`."
)

st.info(
    "✅ The fifth working dashboard page is **Role Segmentation + Job Clustering**. "
    "Open it from the Streamlit sidebar: `Pages -> 5_Role_Clustering`."
)

st.info(
    "✅ The sixth working dashboard page is **Data Import & Dataset Manager**. "
    "Open it from the Streamlit sidebar: `Pages -> 6_Data_Import`."
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

        ✅ **Working now**

        Explore role distributions, company/location patterns,
        skills-per-job, and quick market insights.
        """
    )
    st.info(
        """
        **📄 3. CV Skill Gap Analyzer**

        ✅ **Working now**

        Paste or upload your CV.
        See exactly which skills you have and which you are missing
        relative to your target roles.
        """
    )

with col2:
    st.info(
        """
        **🔬 2. Skill Demand Analysis**

        ✅ **Working now**

        Analyze top skills, category distribution, skill co-occurrence,
        and role-wise skill demand patterns.
        """
    )
    st.info(
        """
        **🚀 4. Project Recommendation Engine**

        ✅ **Working now**

        Get a personalised list of portfolio projects to build
        in order to close your skill gap efficiently.
        """
    )
    st.info(
        """
        **🧠 5. Role Segmentation + Job Clustering**

        ✅ **Working now**

        Group jobs into role segments using unsupervised learning,
        then explore cluster-level themes, skills, and market patterns.
        """
    )
    st.info(
        """
        **📥 6. Data Import & Dataset Manager**

        ✅ **Working now**

        Upload a CSV, validate schema quality, process imported jobs,
        and generate dashboard-ready outputs.
        """
    )

st.markdown("---")
st.caption("Built with Python · Streamlit · scikit-learn · open-source NLP")
