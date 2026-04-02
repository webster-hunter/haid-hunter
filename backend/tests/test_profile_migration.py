"""Tests for profile on-read migration from string skills to typed skills."""

import json
import pytest
from pathlib import Path
from backend.services.profile import ProfileService


@pytest.fixture
def profile_path(tmp_path):
    return tmp_path / ".profile.json"


class TestProfileMigration:
    def test_migrates_string_skills_to_typed(self, profile_path):
        profile_path.write_text(json.dumps({
            "summary": "",
            "skills": ["Python", "React", "Docker"],
            "experience": [],
            "education": [],
            "certifications": [],
        }))
        svc = ProfileService(profile_path)
        result = svc.get()
        assert isinstance(result["skills"], list)
        for s in result["skills"]:
            assert "name" in s
            assert "type" in s
        names = [s["name"] for s in result["skills"]]
        assert "Python" in names
        assert "React" in names
        assert "Docker" in names

    def test_drops_unknown_string_skills(self, profile_path):
        profile_path.write_text(json.dumps({
            "summary": "",
            "skills": ["Python", "TotallyFakeSkill123"],
            "experience": [],
            "education": [],
            "certifications": [],
        }))
        svc = ProfileService(profile_path)
        result = svc.get()
        names = [s["name"] for s in result["skills"]]
        assert "Python" in names
        assert "TotallyFakeSkill123" not in names

    def test_preserves_already_typed_skills(self, profile_path):
        profile_path.write_text(json.dumps({
            "summary": "",
            "skills": [{"name": "Python", "type": "Programming Languages"}],
            "experience": [],
            "education": [],
            "certifications": [],
        }))
        svc = ProfileService(profile_path)
        result = svc.get()
        assert result["skills"] == [{"name": "Python", "type": "Programming Languages"}]

    def test_migration_persists_on_next_write(self, profile_path):
        profile_path.write_text(json.dumps({
            "summary": "",
            "skills": ["Python"],
            "experience": [],
            "education": [],
            "certifications": [],
        }))
        svc = ProfileService(profile_path)
        profile = svc.get()
        svc.put(profile)
        raw = json.loads(profile_path.read_text())
        assert isinstance(raw["skills"][0], dict)
        assert raw["skills"][0]["name"] == "Python"
