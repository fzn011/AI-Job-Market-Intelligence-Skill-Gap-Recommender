"""
1_Job_Market_Overview.py — Job Market Overview page.

Planned features:
    - Display job count by title and category
    - Map of job locations
    - Trend chart of jobs posted over time
    - Filter by job type (full-time, contract, remote)
"""

import streamlit as st

st.set_page_config(page_title="Job Market Overview", page_icon="🗺️", layout="wide")

st.title("🗺️ Job Market Overview")
st.markdown("_Coming soon — this module is under development._")

st.info(
    """
    **What this page will show:**
    - Number of jobs by title and category
    - Geographic distribution of roles
    - Posting trends over time
    - Breakdown by job type (full-time, remote, contract)
    """
)
