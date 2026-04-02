import logging
from backend.services.nlp_extraction import extract_from_documents  # noqa: F401

logger = logging.getLogger(__name__)


def merge_suggestions(existing_profile: dict, suggestions: dict) -> dict:
    profile = dict(existing_profile)
    existing_skills = profile.get("skills", [])
    existing_names = {s["name"].lower() for s in existing_skills}
    merged = list(existing_skills)
    for skill in suggestions.get("skills", []):
        if skill["name"].lower() not in existing_names:
            merged.append(skill)
            existing_names.add(skill["name"].lower())
    profile["skills"] = merged
    return profile
