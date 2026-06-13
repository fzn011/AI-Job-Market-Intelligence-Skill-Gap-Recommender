"""Regional role profile utilities."""

from __future__ import annotations

import json
from pathlib import Path

from src.career_taxonomy_utils import get_role_core_skills, get_role_helpful_skills, get_role_profile


def get_regional_profiles_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "career_taxonomies" / "regional_profiles.json"


def load_regional_profiles_data() -> dict:
    """Load regional profile overrides."""
    path = get_regional_profiles_path()
    if not path.exists():
        return {"regions": ["Global"], "profiles": {}}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        return {"regions": ["Global"], "profiles": {}}
    return data


def list_regions() -> list[str]:
    """Return supported region names."""
    data = load_regional_profiles_data()
    regions = data.get("regions", ["Global"])
    if "Global" not in regions:
        regions = ["Global"] + list(regions)
    return regions


def get_regional_role_profile(category: str, role: str, region: str = "Global") -> dict:
    """Return role profile merged with regional overrides when available."""
    base = get_role_profile(category, role)
    if region in ("Global", "", None):
        return {**base, "region": "Global", "regional_notes": ""}

    data = load_regional_profiles_data()
    profiles = data.get("profiles", {})
    regional = profiles.get(region, {}).get(category, {}).get(role, {})

    if not regional:
        return {**base, "region": region, "regional_notes": "No regional override; using global profile."}

    merged = {**base}
    if regional.get("core_skills"):
        merged["core_skills"] = regional["core_skills"]
    if regional.get("helpful_skills"):
        merged["helpful_skills"] = regional["helpful_skills"]
    merged["region"] = region
    merged["regional_notes"] = regional.get("notes", "")
    return merged


def get_regional_target_skills(category: str, role: str, region: str = "Global") -> list[str]:
    """Return combined core + helpful skills for a regional role profile."""
    profile = get_regional_role_profile(category, role, region)
    core = [str(s).strip().lower() for s in profile.get("core_skills", []) if s]
    helpful = [str(s).strip().lower() for s in profile.get("helpful_skills", []) if s]
    return sorted(set(core) | set(helpful))


def get_regional_core_skills(category: str, role: str, region: str = "Global") -> list[str]:
    profile = get_regional_role_profile(category, role, region)
    return sorted({str(s).strip().lower() for s in profile.get("core_skills", []) if s})


def get_regional_helpful_skills(category: str, role: str, region: str = "Global") -> list[str]:
    profile = get_regional_role_profile(category, role, region)
    return sorted({str(s).strip().lower() for s in profile.get("helpful_skills", []) if s})
