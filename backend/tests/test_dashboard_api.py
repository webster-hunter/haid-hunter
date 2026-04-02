from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.database import init_db, get_connection
from backend.services.encryption import EncryptionService
from backend.services.metadata import MetadataService
from backend.services.profile import ProfileService
import backend.config as config
import backend.routers.dashboard as dashboard_mod
import backend.routers.tasks as tasks_mod
import backend.routers.settings as settings_mod
import backend.routers.applications as apps_mod
from cryptography.fernet import Fernet
from pathlib import Path
import json


def setup_test_env(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    key = Fernet.generate_key().decode()
    config.ENCRYPTION_KEY = key

    docs_dir = tmp_path / "documents"
    docs_dir.mkdir(exist_ok=True)

    profile_path = docs_dir / ".profile.json"
    profile_path.write_text(json.dumps({
        "summary": "Test engineer with 5 years experience",
        "skills": ["Python", "React", "TypeScript", "Go", "Rust"],
        "experience": [
            {"company": "Acme", "role": "Senior Dev", "start_date": "2021", "end_date": None},
            {"company": "OldCo", "role": "Junior Dev", "start_date": "2018", "end_date": "2021"},
        ],
        "education": [],
        "certifications": [],
    }))

    meta_service = MetadataService(docs_dir)
    meta_data = meta_service.read()
    meta_data["files"] = {
        "abc1": {"original_name": "resume1.pdf", "tags": ["resume"]},
        "abc2": {"original_name": "resume2.pdf", "tags": ["resume"]},
        "abc3": {"original_name": "cover.pdf", "tags": ["cover-letter"]},
    }
    meta_service.save(meta_data)

    dashboard_mod._db_path = db_path
    dashboard_mod._profile_service = ProfileService(profile_path)
    dashboard_mod._metadata_service = meta_service
    tasks_mod._db_path = db_path
    settings_mod._db_path = db_path
    apps_mod._db_path = db_path
    apps_mod._encryption = EncryptionService(key)
    apps_mod._metadata_service = meta_service

    return db_path


def test_dashboard_returns_profile(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    profile = response.json()["profile"]
    assert "Test engineer" in profile["summary"]
    skill_names = [s["name"] for s in profile["skills"]]
    assert skill_names == ["Python", "React", "TypeScript", "Go", "Rust"]
    assert "Senior Dev at Acme" in profile["current_role"]


def test_dashboard_returns_document_counts(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/dashboard")
    docs = response.json()["documents"]
    assert docs["total"] == 3
    assert docs["by_tag"]["resume"] == 2
    assert docs["by_tag"]["cover-letter"] == 1


def test_dashboard_returns_application_stats(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/applications", json={"company": "A", "position": "E", "status": "applied"})
    client.post("/api/applications", json={"company": "B", "position": "E", "status": "bookmarked"})
    client.post("/api/applications", json={"company": "C", "position": "E", "status": "applied",
                                            "has_referral": True, "referral_name": "Jane"})
    response = client.get("/api/dashboard")
    apps = response.json()["applications"]
    assert apps["total"] == 3
    assert apps["by_status"]["applied"] == 2
    assert apps["by_status"]["bookmarked"] == 1
    assert apps["referrals"]["total"] == 1
    assert apps["referrals"]["contacts"][0]["name"] == "Jane"
    assert apps["referrals"]["contacts"][0]["company"] == "C"


def test_dashboard_returns_tasks(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/dashboard")
    tasks = response.json()["tasks"]
    assert tasks["daily_target"] == 5
    assert tasks["applied_today"] >= 0
    assert isinstance(tasks["statuses_current"], bool)
    assert isinstance(tasks["user_tasks"], list)


def test_dashboard_applied_today_count(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/applications", json={"company": "X", "position": "E", "status": "applied"})
    client.post("/api/applications", json={"company": "Y", "position": "E", "status": "bookmarked"})
    response = client.get("/api/dashboard")
    assert response.json()["tasks"]["applied_today"] == 1


def test_dashboard_stale_status_detection(tmp_path):
    db_path = setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/applications", json={"company": "Stale", "position": "E", "status": "applied"})
    conn = get_connection(db_path)
    old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    conn.execute("UPDATE applications SET updated_at = ? WHERE company = 'Stale'", (old_date,))
    conn.commit()
    conn.close()
    response = client.get("/api/dashboard")
    tasks = response.json()["tasks"]
    assert tasks["statuses_current"] is False
    assert tasks["stale_count"] == 1


def test_dashboard_task_due_logic(tmp_path):
    db_path = setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/tasks", json={"title": "One-time"})
    create = client.post("/api/tasks", json={"title": "Daily", "recurrence": "daily"})
    task_id = create.json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"completed": True})

    response = client.get("/api/dashboard")
    user_tasks = response.json()["tasks"]["user_tasks"]
    one_time = next(t for t in user_tasks if t["title"] == "One-time")
    daily = next(t for t in user_tasks if t["title"] == "Daily")
    assert one_time["is_due"] is True
    assert one_time["completed_today"] is False
    assert daily["is_due"] is False
    assert daily["completed_today"] is True


def test_dashboard_empty_profile(tmp_path):
    db_path = setup_test_env(tmp_path)
    client = TestClient(app)
    dashboard_mod._profile_service.put({
        "summary": "", "skills": [], "experience": [], "activities": [], "education": [], "certifications": []
    })
    response = client.get("/api/dashboard")
    profile = response.json()["profile"]
    assert profile["summary"] == ""
    assert profile["skills"] == []
    assert profile["current_role"] is None
