import json
from pathlib import Path
from threading import Lock

from backend.services.skill_definitions import SKILLS

VALID_SECTIONS = {"summary", "skills", "experience", "activities", "education", "certifications"}

EMPTY_PROFILE = {
    "summary": "",
    "skills": [],
    "experience": [],
    "activities": [],
    "education": [],
    "certifications": [],
}


def _migrate_skills(skills: list) -> list[dict]:
    """Convert plain string skills to typed objects. Drop unknowns."""
    if not skills:
        return []
    if isinstance(skills[0], dict):
        return skills
    result = []
    for s in skills:
        if isinstance(s, str) and s in SKILLS:
            result.append({"name": s, "type": SKILLS[s]})
    return result


class ProfileService:
    def __init__(self, profile_path: Path):
        self.profile_path = profile_path
        self._lock = Lock()

    def get(self) -> dict:
        with self._lock:
            if not self.profile_path.exists():
                self._write(dict(EMPTY_PROFILE))
            profile = json.loads(self.profile_path.read_text())
            profile["skills"] = _migrate_skills(profile.get("skills", []))
            return profile

    def put(self, profile: dict):
        with self._lock:
            self._write(profile)

    def patch(self, section: str, data) -> dict:
        if section not in VALID_SECTIONS:
            raise KeyError(f"Invalid section: {section}")
        with self._lock:
            profile = json.loads(self.profile_path.read_text()) if self.profile_path.exists() else dict(EMPTY_PROFILE)
            profile[section] = data
            self._write(profile)
            return profile

    def _write(self, data: dict):
        self.profile_path.write_text(json.dumps(data, indent=2))
