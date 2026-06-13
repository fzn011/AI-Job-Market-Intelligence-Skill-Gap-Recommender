"""Public job data connector utilities (legal free APIs with graceful fallback)."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime

import pandas as pd

from src.secrets_utils import get_usajobs_credentials


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


def get_usajobs_api_key() -> str:
    """Read USAJobs API key from secrets or environment."""
    return get_usajobs_credentials()[0]


def fetch_usajobs_jobs(keyword: str = "data analyst", results_per_page: int = 10) -> tuple[pd.DataFrame, dict]:
    """
    Fetch jobs from USAJobs public API.

    Requires free API key: https://developer.usajobs.gov/
    Set environment variable: USAJOBS_API_KEY
    """
    api_key, email = get_usajobs_credentials()

    if not api_key:
        demo_df = pd.DataFrame(DEMO_CONNECTOR_JOBS)
        return demo_df, {
            "connector": "usajobs",
            "mode": "demo_fallback",
            "message": "USAJOBS_API_KEY not set. Showing demo connector data. Get a free key at developer.usajobs.gov",
            "rows": len(demo_df),
        }

    params = urllib.parse.urlencode({"Keyword": keyword, "ResultsPerPage": results_per_page})
    url = f"{USAJOBS_SEARCH_URL}?{params}"
    request = urllib.request.Request(
        url,
        headers={
            "Host": "data.usajobs.gov",
            "User-Agent": email,
            "Authorization-Key": api_key,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        demo_df = pd.DataFrame(DEMO_CONNECTOR_JOBS)
        return demo_df, {
            "connector": "usajobs",
            "mode": "demo_fallback",
            "message": f"API request failed ({exc}). Showing demo connector data.",
            "rows": len(demo_df),
        }

    items = payload.get("SearchResult", {}).get("SearchResultItems", [])
    rows = []
    for idx, item in enumerate(items):
        matched = item.get("MatchedObjectDescriptor", {})
        rows.append(
            {
                "job_id": f"usajobs_{matched.get('PositionID', idx)}",
                "job_title": matched.get("PositionTitle", "Unknown"),
                "company": matched.get("OrganizationName", "Unknown"),
                "location": matched.get("PositionLocationDisplay", "Unknown"),
                "job_type": matched.get("PositionScheduleType", "Unknown"),
                "description": matched.get("UserArea", {}).get("Details", {}).get("MajorDuties", [""])[0]
                if matched.get("UserArea", {}).get("Details", {}).get("MajorDuties")
                else matched.get("QualificationSummary", ""),
                "date_posted": matched.get("PublicationStartDate", datetime.now(UTC).strftime("%Y-%m-%d"))[:10],
                "source": "usajobs_api",
            }
        )

    if not rows:
        demo_df = pd.DataFrame(DEMO_CONNECTOR_JOBS)
        return demo_df, {
            "connector": "usajobs",
            "mode": "demo_fallback",
            "message": "No results returned. Showing demo connector data.",
            "rows": len(demo_df),
        }

    return pd.DataFrame(rows), {
        "connector": "usajobs",
        "mode": "live_api",
        "message": f"Fetched {len(rows)} jobs from USAJobs API.",
        "rows": len(rows),
    }


def list_available_connectors() -> list[str]:
    return ["usajobs"]
