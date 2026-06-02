"""
3_CV_Skill_Gap.py — CV Skill Gap Analyzer page.

Planned features:
    - Text area for pasting CV content
    - Automatic skill extraction from CV text
    - Side-by-side comparison: user skills vs. market demand
    - Visual skill gap indicator (progress bars / radar chart)
"""

import streamlit as st

st.set_page_config(page_title="CV Skill Gap Analyzer", page_icon="📄", layout="wide")

st.title("📄 CV Skill Gap Analyzer")
st.markdown("_Coming soon — this module is under development._")

st.info(
    """
    **What this page will do:**
    - Accept your CV as pasted text or uploaded PDF
    - Extract your current skills automatically
    - Compare them against the most in-demand market skills
    - Show you exactly which skills you are missing
    """
)
