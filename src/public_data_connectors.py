"""Public job data connector utilities (legal free APIs with graceful fallback)."""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import requests

from src.secrets_utils import get_usajobs_credentials, usajobs_credentials_configured


USAJOBS_SEARCH_URL = "https://data.usajobs.gov/api/search"
DEMO_CONNECTOR_JOBS = [
    {
        "job_id": "demo_usajobs_001",
        "job_title": "Data Analyst",
        "company": "Demo Federal Agency",
        "location": "Remote",
        "job_type": "Full-time",
        "description": "Analyze datasets using Python, SQL, Excel, and Power BI. Build dashboards and reports.",
        "date_posted": datetime.now(UTC).strftime("%Y-%m-%d"),
        "source": "usajobs_demo",
    },
    {
        "job_id": "demo_usajobs_002",
        "job_title": "IT Specialist",
        "company": "Demo Federal Agency",
        "location": "Washington, DC",
        "job_type": "Full-time",
        "description": "Support systems using Linux, troubleshooting, documentation, and customer service.",
        "date_posted": datetime.now(UTC).strftime("%Y-%m-%d"),
        "source": "usajobs_demo",
    },
]


def get_usajobs_api_key(api_key_override: str = "", email_override: str = "") -> str:
    """Read USAJobs API key from secrets or overrides."""
    return get_usajobs_credentials(api_key_override, email_override)[0]


def _demo_fallback(message: str) -> tuple[pd.DataFrame, dict]:
    demo_df = pd.DataFrame(DEMO_CONNECTOR_JOBS)
    return demo_df, {
        "connector": "usajobs",
        "mode": "demo_fallback",
        "message": message,
        "rows": len(demo_df),
    }


def fetch_usajobs_jobs(
    keyword: str = "data analyst",
    results_per_page: int = 10,
    api_key_override: str = "",
    email_override: str = "",
) -> tuple[pd.DataFrame, dict]:
    """
    Fetch jobs from USAJobs public API.

    Requires free API key: https://developer.usajobs.gov/
    Configure `.streamlit/secrets.toml` or use the connector settings on Data Import.
    """
    api_key, email = get_usajobs_credentials(api_key_override, email_override)

    if not api_key:
        return _demo_fallback(
            "USAJOBS_API_KEY not configured. Add it to `.streamlit/secrets.toml` in the project root "
            "(same folder as setup.ps1), then restart the app."
        )

    if not email or "@" not in email:
        return _demo_fallback(
            "USAJOBS_USER_EMAIL not configured. Use the same email you registered at developer.usajobs.gov."
        )

    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": email,
        "Authorization-Key": api_key,
    }
    params = {"Keyword": keyword, "ResultsPerPage": results_per_page}

    try:
        response = requests.get(USAJOBS_SEARCH_URL, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        if status == 401:
            return _demo_fallback(
                "USAJobs rejected the credentials (HTTP 401). Use the exact email from your API request, "
                "quote the API key in secrets.toml, and remove placeholder export values like "
                "`your-free-key` / `your@email.com` from your environment."
            )
        return _demo_fallback(f"API request failed (HTTP {status}). Showing demo connector data.")
    except (requests.RequestException, ValueError) as exc:
        return _demo_fallback(f"API request failed ({exc}). Showing demo connector data.")

    items = payload.get("SearchResult", {}).get("SearchResultItems", [])
    rows = []
    for idx, item in enumerate(items):
        matched = item.get("MatchedObjectDescriptor", {})
        major_duties = matched.get("UserArea", {}).get("Details", {}).get("MajorDuties", [])
        description = major_duties[0] if major_duties else matched.get("QualificationSummary", "")
        rows.append(
            {
                "job_id": f"usajobs_{matched.get('PositionID', idx)}",
                "job_title": matched.get("PositionTitle", "Unknown"),
                "company": matched.get("OrganizationName", "Unknown"),
                "location": matched.get("PositionLocationDisplay", "Unknown"),
                "job_type": matched.get("PositionScheduleType", "Unknown"),
                "description": description,
                "date_posted": matched.get("PublicationStartDate", datetime.now(UTC).strftime("%Y-%m-%d"))[:10],
                "source": "usajobs_api",
            }
        )

    if not rows:
        return _demo_fallback("No results returned. Showing demo connector data.")

    return pd.DataFrame(rows), {
        "connector": "usajobs",
        "mode": "live_api",
        "message": f"Fetched {len(rows)} jobs from USAJobs API.",
        "rows": len(rows),
    }


def list_available_connectors() -> list[str]:
    return ["usajobs"]


def get_usajobs_connection_status(
    api_key_override: str = "",
    email_override: str = "",
) -> dict:
    """Return a safe summary of whether USAJobs credentials are configured."""
    configured = usajobs_credentials_configured(api_key_override, email_override)
    _, email = get_usajobs_credentials(api_key_override, email_override)
    return {
        "configured": configured,
        "email": email if configured else "",
    }
