from fastapi.testclient import TestClient
from backend.main import app
from backend.services.profile import ProfileService
import backend.config as config


def setup_test_env(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    config.DOCUMENTS_DIR = docs_dir
    config.PROFILE_PATH = docs_dir / ".profile.json"
    from backend.routers import profile
    profile._profile_service = ProfileService(config.PROFILE_PATH)


def test_get_profile_returns_scaffold(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == ""
    assert data["skills"] == []


def test_put_profile(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    profile = {"summary": "Engineer", "skills": [], "experience": [],
               "education": [], "certifications": [], "objectives": []}
    response = client.put("/api/profile", json=profile)
    assert response.status_code == 200
    get_response = client.get("/api/profile")
    assert get_response.json()["summary"] == "Engineer"


def test_patch_section(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.get("/api/profile")  # init
    response = client.patch("/api/profile/skills", json=[{"name": "Python", "proficiency": "advanced", "category": "technical"}])
    assert response.status_code == 200
    assert len(response.json()["skills"]) == 1


def test_patch_invalid_section(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.patch("/api/profile/invalid", json="data")
    assert response.status_code == 400
