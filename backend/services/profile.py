import json
from pathlib import Path
from threading import Lock

VALID_SECTIONS = {"summary", "skills", "experience", "activities", "education", "certifications"}

EMPTY_PROFILE = {
    "summary": "",
    "skills": [],
    "experience": [],
    "activities": [],
    "education": [],
    "certifications": [],
}


class ProfileService:
    def __init__(self, profile_path: Path):
        self.profile_path = profile_path
        self._lock = Lock()

    def get(self) -> dict:
        with self._lock:
            if not self.profile_path.exists():
                self._write(dict(EMPTY_PROFILE))
            return json.loads(self.profile_path.read_text())

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
