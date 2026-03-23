from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.database import init_db, get_connection
import backend.routers.tasks as tasks_mod


def setup_test_env(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    tasks_mod._db_path = db_path
    return db_path


def test_list_tasks_empty(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task_one_time(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/tasks", json={"title": "Tailor resume"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Tailor resume"
    assert data["recurrence"] is None
    assert data["interval_days"] is None
    assert data["id"] is not None


def test_create_task_daily(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/tasks", json={"title": "Check email", "recurrence": "daily"})
    data = response.json()
    assert data["recurrence"] == "daily"
    assert data["interval_days"] == 1


def test_create_task_weekly(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/tasks", json={"title": "Review connections", "recurrence": "weekly"})
    data = response.json()
    assert data["recurrence"] == "weekly"
    assert data["interval_days"] == 7


def test_create_task_custom(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/tasks", json={"title": "Network", "recurrence": "custom", "interval_days": 3})
    data = response.json()
    assert data["recurrence"] == "custom"
    assert data["interval_days"] == 3


def test_patch_task_complete(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/tasks", json={"title": "Do thing"})
    task_id = create.json()["id"]
    response = client.patch(f"/api/tasks/{task_id}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["completed_at"] is not None


def test_patch_task_uncomplete(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/tasks", json={"title": "Do thing"})
    task_id = create.json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"completed": True})
    response = client.patch(f"/api/tasks/{task_id}", json={"completed": False})
    assert response.json()["completed_at"] is None


def test_patch_task_title(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/tasks", json={"title": "Old title"})
    task_id = create.json()["id"]
    response = client.patch(f"/api/tasks/{task_id}", json={"title": "New title"})
    assert response.json()["title"] == "New title"


def test_delete_task(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/tasks", json={"title": "Temp"})
    task_id = create.json()["id"]
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    listing = client.get("/api/tasks")
    assert len(listing.json()) == 0


def test_delete_nonexistent_task_returns_404(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.delete("/api/tasks/999")
    assert response.status_code == 404
