import logging
from backend.services.nlp_extraction import extract_from_documents  # noqa: F401

logger = logging.getLogger(__name__)


def merge_suggestions(existing_profile: dict, suggestions: dict) -> dict:
    profile = dict(existing_profile)
    existing_skills = set(profile.get("skills", []))
    new_skills = (
        suggestions.get("skills", [])
        + suggestions.get("technologies", [])
        + suggestions.get("soft_skills", [])
    )
    merged = list(profile.get("skills", []))
    for skill in new_skills:
        if skill not in existing_skills:
            merged.append(skill)
            existing_skills.add(skill)
    profile["skills"] = merged
    return profile
