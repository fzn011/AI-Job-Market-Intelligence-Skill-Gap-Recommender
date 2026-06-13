"""Anonymized peer comparison benchmarking."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.dashboard_utils import load_processed_jobs, parse_extracted_skills
from src.job_match_utils import extract_cv_skills_enhanced


def _synthetic_benchmark_scores(role: str, n: int = 200) -> np.ndarray:
    """Generate reproducible synthetic applicant scores for demo benchmarking."""
    seed = sum(ord(char) for char in role.lower()) % 10000
    rng = np.random.default_rng(seed)
    return rng.beta(2.2, 3.8, size=n) * 100


def compute_peer_benchmark(
    cv_text: str,
    target_role: str,
    jobs_df: pd.DataFrame | None = None,
) -> dict:
    """
    Compare user match score against anonymized peer distribution.

    Uses job dataset when available; otherwise uses reproducible synthetic benchmark.
    """
    cv_skills = extract_cv_skills_enhanced(cv_text)
    if not cv_skills:
        return {"available": False, "message": "No skills detected in CV text."}

    jobs = jobs_df if jobs_df is not None else load_processed_jobs()
    user_score = min(100.0, len(cv_skills) * 7.5)

    if not jobs.empty and "job_title" in jobs.columns:
        role_mask = jobs["job_title"].astype(str).str.contains(target_role.split()[0], case=False, na=False)
        subset = jobs[role_mask] if role_mask.any() else jobs
        peer_scores = []
        for _, row in subset.iterrows():
            job_skills = parse_extracted_skills(row.get("extracted_skills", []))
            if not job_skills:
                continue
            overlap = len(set(cv_skills) & set(job_skills))
            peer_scores.append(min(100.0, (overlap / max(len(job_skills), 1)) * 100))
        if peer_scores:
            distribution = np.array(peer_scores)
            source = "job_dataset"
        else:
            distribution = _synthetic_benchmark_scores(target_role)
            source = "synthetic_fallback"
    else:
        distribution = _synthetic_benchmark_scores(target_role)
        source = "synthetic_benchmark"

    percentile = round(float((distribution < user_score).mean()) * 100, 1)
    median = round(float(np.median(distribution)), 1)

    if percentile >= 70:
        tier = "Top 30% of applicants in sample"
    elif percentile >= 40:
        tier = "Middle tier — room to improve key gaps"
    else:
        tier = "Below median — focus on core missing skills"

    return {
        "available": True,
        "target_role": target_role,
        "user_score_proxy": round(user_score, 1),
        "peer_median": median,
        "percentile": percentile,
        "tier_label": tier,
        "sample_size": len(distribution),
        "source": source,
        "cv_skill_count": len(cv_skills),
    }


def build_peer_benchmark_dataframe(result: dict) -> pd.DataFrame:
    if not result.get("available"):
        return pd.DataFrame()
    return pd.DataFrame(
        [
            {"metric": "Your score (proxy)", "value": result["user_score_proxy"]},
            {"metric": "Peer median", "value": result["peer_median"]},
            {"metric": "Percentile", "value": result["percentile"]},
            {"metric": "Sample size", "value": result["sample_size"]},
        ]
    )
