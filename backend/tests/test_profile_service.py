import json
from backend.services.profile import ProfileService

EMPTY_PROFILE = {
    "summary": "",
    "skills": [],
    "experience": [],
    "activities": [],
    "education": [],
    "certifications": [],
}


def test_get_creates_empty_scaffold(tmp_path):
    profile_path = tmp_path / ".profile.json"
    service = ProfileService(profile_path)
    profile = service.get()
    assert profile == EMPTY_PROFILE
    assert profile_path.exists()


def test_get_loads_existing_profile(tmp_path):
    profile_path = tmp_path / ".profile.json"
    profile_path.write_text(json.dumps({"summary": "Engineer", "skills": [], "experience": [],
                                         "activities": [], "education": [], "certifications": []}))
    service = ProfileService(profile_path)
    assert service.get()["summary"] == "Engineer"


def test_put_replaces_profile(tmp_path):
    profile_path = tmp_path / ".profile.json"
    service = ProfileService(profile_path)
    new_profile = {**EMPTY_PROFILE, "summary": "Updated summary"}
    service.put(new_profile)
    assert service.get()["summary"] == "Updated summary"


def test_patch_section(tmp_path):
    profile_path = tmp_path / ".profile.json"
    service = ProfileService(profile_path)
    service.patch("skills", ["Python", "TypeScript"])
    profile = service.get()
    assert len(profile["skills"]) == 2
    assert profile["skills"][0] == "Python"


def test_patch_invalid_section(tmp_path):
    profile_path = tmp_path / ".profile.json"
    service = ProfileService(profile_path)
    try:
        service.patch("invalid", "data")
        assert False, "Should have raised"
    except KeyError:
        pass
