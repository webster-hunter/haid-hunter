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
    profile = {"summary": "Engineer", "skills": [], "experience": [], "activities": [],
               "education": [], "certifications": []}
    response = client.put("/api/profile", json=profile)
    assert response.status_code == 200
    get_response = client.get("/api/profile")
    assert get_response.json()["summary"] == "Engineer"


def test_patch_section(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.get("/api/profile")  # init
    response = client.patch("/api/profile/skills", json=["Python", "TypeScript"])
    assert response.status_code == 200
    assert len(response.json()["skills"]) == 2


def test_patch_invalid_section(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.patch("/api/profile/invalid", json="data")
    assert response.status_code == 400


def test_patch_skills_rejects_non_list(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.get("/api/profile")  # init
    response = client.patch("/api/profile/skills", json="not a list")
    assert response.status_code == 422


def test_patch_skills_rejects_non_strings(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.get("/api/profile")  # init
    response = client.patch("/api/profile/skills", json=[{"name": "Python"}])
    assert response.status_code == 422


def test_patch_experience_rejects_missing_fields(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.get("/api/profile")  # init
    response = client.patch("/api/profile/experience", json=[{"company": "Acme"}])
    assert response.status_code == 422


def test_patch_experience_accepts_valid_data(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.get("/api/profile")  # init
    response = client.patch("/api/profile/experience", json=[
        {"company": "Acme", "role": "Dev", "start_date": "2020-01", "end_date": None, "accomplishments": []}
    ])
    assert response.status_code == 200
    assert response.json()["experience"][0]["company"] == "Acme"


def test_patch_summary_rejects_non_string(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.get("/api/profile")  # init
    response = client.patch("/api/profile/summary", json=123)
    assert response.status_code == 422


def test_patch_summary_accepts_string(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.get("/api/profile")  # init
    response = client.patch("/api/profile/summary", json="Updated summary")
    assert response.status_code == 200
    assert response.json()["summary"] == "Updated summary"


def test_patch_invalid_section_returns_400(tmp_path):
    from backend.routers import profile as profile_router
    from backend.services.profile import ProfileService
    from backend.main import app
    from fastapi.testclient import TestClient
    profile_router._profile_service = ProfileService(tmp_path / ".profile.json")
    client = TestClient(app)
    response = client.patch("/api/profile/objectives", json=["Get promoted"])
    assert response.status_code == 400
