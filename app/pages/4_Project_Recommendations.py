"""
4_Project_Recommendations.py — Project Recommendation Engine page.

Planned features:
    - Display personalised project recommendations based on skill gaps
    - Map each recommended project to the skills it demonstrates
    - Rank projects by market impact (demand frequency)
    - Provide GitHub-ready project ideas with brief descriptions
"""

import streamlit as st

st.set_page_config(
    page_title="Project Recommendations", page_icon="🚀", layout="wide"
)

st.title("🚀 Project Recommendation Engine")
st.markdown("_Coming soon — this module is under development._")

st.info(
    """
    **What this page will do:**
    - Based on your skill gap, suggest concrete portfolio projects to build
    - Rank recommendations by how many job postings demand those skills
    - Link each project to the specific skills it demonstrates
    - Help you close your skill gap as efficiently as possible
    """
)
