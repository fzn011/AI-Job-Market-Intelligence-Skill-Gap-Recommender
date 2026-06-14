"""Data Import & Dataset Manager page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_collection import (  # noqa: E402
    create_job_template_csv,
    export_import_summary,
    load_job_csv,
    process_imported_jobs,
    validate_job_schema,
)
from src.dashboard_utils import get_active_dataset_label  # noqa: E402
from src.ui_theme import apply_global_theme, render_app_footer, render_brand_header, render_info_box  # noqa: E402
from src.public_data_connectors import fetch_usajobs_jobs, list_available_connectors  # noqa: E402
from src.usajobs_ui_utils import render_usajobs_status  # noqa: E402
from src.progress_tracker_utils import increment_stat  # noqa: E402


st.set_page_config(page_title="Data Import & Dataset Manager", page_icon="📥", layout="wide")

apply_global_theme(PROJECT_ROOT)
render_brand_header(
    app_name="CareerCompass · Data Import & Dataset Manager",
    subtitle="Validate and process local CSV job data for dashboard analysis — or use Career Explorer without job data.",
)

sample_processed_path = PROJECT_ROOT / "data" / "processed" / "processed_sample_jobs.csv"
imported_processed_path = PROJECT_ROOT / "data" / "processed" / "processed_imported_jobs.csv"
expanded_source_path = PROJECT_ROOT / "data" / "sample" / "expanded_sample_jobs.csv"

col_a, col_b, col_c = st.columns(3)
col_a.metric("Sample Processed Data", "Available" if sample_processed_path.exists() else "Missing")
col_b.metric("Imported Processed Data", "Available" if imported_processed_path.exists() else "Missing")
col_c.metric("Expanded Demo Source", "Available" if expanded_source_path.exists() else "Missing")

st.info(f"Active dataset preference (auto): **{get_active_dataset_label('auto')}**")

render_info_box(
    "Two paths for career guidance",
    "1. Import your own job-post CSV for data-driven market analysis. "
    "2. Use Career Explorer or Career Category mode on the CV and Recommendations pages for curated guidance without job data.",
)

st.markdown("---")
st.subheader("Upload Job CSV")

uploaded = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded is not None:
    try:
        temp_upload_path = PROJECT_ROOT / "data" / "raw" / "uploaded_jobs.csv"
        temp_upload_path.parent.mkdir(parents=True, exist_ok=True)
        temp_upload_path.write_bytes(uploaded.getvalue())

        loaded_df = load_job_csv(temp_upload_path)
        validation = validate_job_schema(loaded_df)

        st.markdown("### Validation Report")
        st.json(validation)

        if validation.get("is_valid", False):
            if st.button("Process Uploaded CSV", type="primary"):
                skill_dict_path = PROJECT_ROOT / "data" / "sample" / "skills_dictionary.json"
                output_jobs_path = PROJECT_ROOT / "data" / "processed" / "processed_imported_jobs.csv"
                output_skill_frequency_path = PROJECT_ROOT / "data" / "processed" / "imported_skill_frequency.csv"
                summary_path = PROJECT_ROOT / "reports" / "generated_reports" / "import_summary.json"

                summary = process_imported_jobs(
                    input_csv_path=temp_upload_path,
                    skill_dictionary_path=skill_dict_path,
                    output_jobs_path=output_jobs_path,
                    output_skill_frequency_path=output_skill_frequency_path,
                )
                export_import_summary(summary, summary_path)

                st.success("Uploaded CSV processed successfully.")
                st.write(f"Processed rows: **{summary['processed_rows']}**")
                st.write(f"Unique skills: **{summary['unique_skills']}**")

                top_skills = pd.DataFrame(summary.get("top_skills", []))
                if not top_skills.empty:
                    st.markdown("### Top Skills")
                    st.dataframe(top_skills, use_container_width=True)

                st.markdown("### Output Files")
                st.markdown(f"- `{output_jobs_path}`")
                st.markdown(f"- `{output_skill_frequency_path}`")
                st.markdown(f"- `{summary_path}`")
        else:
            st.warning("Uploaded CSV schema is invalid. Please fix missing required columns and re-upload.")

    except Exception as exc:  # pragma: no cover
        st.error(f"Failed to validate/process uploaded CSV: {exc}")

st.markdown("---")
st.subheader("Public Data Connectors")

render_usajobs_status(PROJECT_ROOT)

connectors = list_available_connectors()
connector = st.selectbox("Connector", options=connectors)
keyword = st.text_input("Search keyword", value="data analyst")

if st.button("Fetch Jobs from Connector", type="primary"):
    if connector == "usajobs":
        jobs_df, meta = fetch_usajobs_jobs(keyword=keyword, results_per_page=10)
        increment_stat("data_imports")
        if meta.get("mode") == "live_api":
            st.success(meta.get("message", "Fetch complete"))
        else:
            st.warning(meta.get("message", "Fetch complete"))
        st.dataframe(jobs_df, use_container_width=True)
        st.caption(f"Mode: {meta.get('mode', 'unknown')} · Rows: {meta.get('rows', 0)}")
        if meta.get("mode") == "live_api":
            st.info("To import into the dashboard, save this data as CSV matching the job schema and upload above.")

st.markdown("---")
st.subheader("Download CSV Template")

template_path = PROJECT_ROOT / "data" / "raw" / "job_posts_template.csv"
create_job_template_csv(template_path)

st.download_button(
    label="Download Job Posts Template",
    data=template_path.read_bytes(),
    file_name="job_posts_template.csv",
    mime="text/csv",
)

st.markdown("---")
with st.expander("Import guide notes"):
    st.markdown("- Follow schema from `docs/job_data_import_guide.md`.")
    st.markdown("- Required columns: job_id, job_title, company, location, job_type, description, date_posted, source.")
    st.markdown("- Preferred date format: YYYY-MM-DD.")
    st.markdown("- Use `source` values like manual_csv, synthetic_demo, user_uploaded_csv, public_dataset.")
    st.markdown("- Do not include private personal data.")

render_app_footer(show_tech_line=False)
