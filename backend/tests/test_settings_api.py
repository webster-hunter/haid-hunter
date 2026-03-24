from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from httpx import AsyncClient, ASGITransport
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


# ===== API Key management tests =====

@pytest.fixture(autouse=False)
def api_key_db(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    settings_mod._db_path = db_path
    yield
    settings_mod._db_path = None


@pytest.mark.asyncio
async def test_get_api_key_status_no_key(api_key_db):
    with patch("backend.routers.settings.get_env_api_key", return_value=None):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/settings/api-key")
            assert resp.status_code == 200
            data = resp.json()
            assert data["configured"] is False
            assert data["source"] is None


@pytest.mark.asyncio
async def test_set_api_key_stores_encrypted(api_key_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.put(
            "/api/settings/api-key",
            json={"api_key": "sk-ant-test-key-12345"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["configured"] is True
        assert data["source"] == "database"


@pytest.mark.asyncio
async def test_get_api_key_shows_db_source_after_set(api_key_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.put(
            "/api/settings/api-key",
            json={"api_key": "sk-ant-test-key-12345"},
        )
        with patch("backend.routers.settings.get_env_api_key", return_value=None):
            resp = await client.get("/api/settings/api-key")
            data = resp.json()
            assert data["configured"] is True
            assert data["source"] == "database"
            assert data["masked"] == "sk-a***2345"


@pytest.mark.asyncio
async def test_get_api_key_shows_env_source_when_env_set(api_key_db):
    with patch("backend.routers.settings.get_env_api_key", return_value="sk-ant-env-key-99999"):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/settings/api-key")
            data = resp.json()
            assert data["configured"] is True
            assert data["source"] == "env"
            assert data["masked"] == "sk-a***9999"


@pytest.mark.asyncio
async def test_db_key_takes_priority_over_env(api_key_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.put(
            "/api/settings/api-key",
            json={"api_key": "sk-ant-db-key-11111"},
        )
        with patch("backend.routers.settings.get_env_api_key", return_value="sk-ant-env-key-99999"):
            resp = await client.get("/api/settings/api-key")
            data = resp.json()
            assert data["source"] == "database"
            assert data["masked"] == "sk-a***1111"


@pytest.mark.asyncio
async def test_delete_api_key(api_key_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.put(
            "/api/settings/api-key",
            json={"api_key": "sk-ant-test-key-12345"},
        )
        resp = await client.delete("/api/settings/api-key")
        assert resp.status_code == 200

        with patch("backend.routers.settings.get_env_api_key", return_value=None):
            resp = await client.get("/api/settings/api-key")
            data = resp.json()
            assert data["configured"] is False


@pytest.mark.asyncio
async def test_test_api_key_valid(api_key_db):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello")]
    mock_client.messages.create.return_value = mock_response

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.put(
            "/api/settings/api-key",
            json={"api_key": "sk-ant-test-key-12345"},
        )
        with patch("backend.routers.settings.build_claude_client", return_value=mock_client):
            resp = await client.post("/api/settings/api-key/test")
            assert resp.status_code == 200
            data = resp.json()
            assert data["valid"] is True


@pytest.mark.asyncio
async def test_test_api_key_no_key_configured(api_key_db):
    with patch("backend.routers.settings.get_env_api_key", return_value=None):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/settings/api-key/test")
            assert resp.status_code == 200
            data = resp.json()
            assert data["valid"] is False
