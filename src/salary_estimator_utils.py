"""Rule-based salary band estimation."""

from __future__ import annotations

import json
from pathlib import Path


def get_salary_bands_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "salary_bands.json"


def load_salary_bands() -> dict:
    path = get_salary_bands_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def list_salary_regions() -> list[str]:
    return sorted(load_salary_bands().keys())


def _find_role_band(region_bands: dict, role: str) -> dict | None:
    role = role.strip()
    if role in region_bands:
        return region_bands[role]
    role_lower = role.lower()
    for key, value in region_bands.items():
        if str(key).strip().lower() == role_lower:
            return value
    return None


def estimate_salary_band(
    role: str,
    region: str,
    match_score: float,
    experience_level: str = "entry",
) -> dict:
    """
    Estimate salary band from role, region, match score, and experience level.

    Uses curated bands and adjusts within band based on match score.
    """
    bands = load_salary_bands()
    region_bands = bands.get(region, {})
    role_band = _find_role_band(region_bands, role)

    if not role_band:
        return {
            "available": False,
            "message": f"No salary band data for {role} in {region}.",
            "role": role,
            "region": region,
        }

    level = experience_level.strip().lower()
    if level not in {"entry", "mid", "senior"}:
        level = "entry"

    band_str = role_band.get(level, role_band.get("entry", ""))
    currency = role_band.get("currency", "")

    try:
        low_str, high_str = band_str.split("-")
        low = float(low_str.replace(",", ""))
        high = float(high_str.replace(",", ""))
    except (ValueError, AttributeError):
        return {
            "available": False,
            "message": "Could not parse salary band.",
            "role": role,
            "region": region,
        }

    score_factor = max(0.0, min(1.0, match_score / 100.0))
    adjusted_low = round(low + (high - low) * 0.15 * score_factor, 0)
    adjusted_high = round(low + (high - low) * (0.55 + 0.35 * score_factor), 0)

    positioning = "Lower band"
    if score_factor >= 0.75:
        positioning = "Upper band"
    elif score_factor >= 0.5:
        positioning = "Mid band"

    return {
        "available": True,
        "role": role,
        "region": region,
        "experience_level": level,
        "match_score": round(match_score, 2),
        "market_band": band_str,
        "estimated_range": f"{int(adjusted_low):,}-{int(adjusted_high):,}",
        "currency": currency,
        "positioning": positioning,
        "note": "Rule-based estimate from curated bands. Actual offers vary by company and negotiation.",
    }


def format_salary_estimate_text(result: dict) -> str:
    if not result.get("available"):
        return result.get("message", "Salary estimate unavailable.")

    return (
        f"Role: {result['role']}\n"
        f"Region: {result['region']}\n"
        f"Experience: {result['experience_level']}\n"
        f"Match score: {result['match_score']}%\n"
        f"Market band ({result['experience_level']}): {result['market_band']} {result['currency']}\n"
        f"Estimated range: {result['estimated_range']} {result['currency']}\n"
        f"Positioning: {result['positioning']}\n"
        f"Note: {result['note']}"
    )
