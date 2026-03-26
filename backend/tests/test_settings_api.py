from fastapi.testclient import TestClient
import pytest
from backend.main import app
from backend.services.database import init_db
import backend.routers.settings as settings_mod


def setup_test_env(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    settings_mod._db_path = db_path


def test_get_seeded_setting(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/settings/daily_application_target")
    assert response.status_code == 200
    assert response.json() == {"key": "daily_application_target", "value": "5"}


def test_get_missing_setting_returns_404(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/settings/nonexistent")
    assert response.status_code == 404


def test_put_setting_creates_new(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.put("/api/settings/theme", json={"value": "dark"})
    assert response.status_code == 200
    get_resp = client.get("/api/settings/theme")
    assert get_resp.json()["value"] == "dark"


def test_put_setting_updates_existing(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.put("/api/settings/daily_application_target", json={"value": "10"})
    response = client.get("/api/settings/daily_application_target")
    assert response.json()["value"] == "10"
