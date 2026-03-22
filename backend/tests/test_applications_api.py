from fastapi.testclient import TestClient
from backend.main import app
from backend.services.database import init_db, get_connection
from backend.services.encryption import EncryptionService
import backend.config as config
from cryptography.fernet import Fernet


def setup_test_env(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    key = Fernet.generate_key().decode()
    config.ENCRYPTION_KEY = key
    from backend.routers import applications
    applications._db_path = db_path
    applications._encryption = EncryptionService(key)


def test_list_applications_empty(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/applications")
    assert response.status_code == 200
    assert response.json() == []


def test_create_application(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/applications", json={
        "company": "Acme", "position": "Engineer", "status": "bookmarked"
    })
    assert response.status_code == 200
    assert response.json()["company"] == "Acme"
    assert response.json()["id"] is not None


def test_get_application(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "applied"})
    app_id = create.json()["id"]
    response = client.get(f"/api/applications/{app_id}")
    assert response.status_code == 200
    assert response.json()["company"] == "Acme"


def test_credentials_masked_by_default(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={
        "company": "Acme", "position": "Engineer", "status": "applied",
        "login_email": "user@test.com", "login_password": "secret123"
    })
    app_id = create.json()["id"]
    response = client.get(f"/api/applications/{app_id}")
    assert response.json()["login_email"] == "***"
    assert response.json()["login_password"] == "***"


def test_credentials_revealed(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={
        "company": "Acme", "position": "Engineer", "status": "applied",
        "login_email": "user@test.com", "login_password": "secret123"
    })
    app_id = create.json()["id"]
    response = client.get(f"/api/applications/{app_id}?reveal_credentials=true")
    assert response.json()["login_email"] == "user@test.com"
    assert response.json()["login_password"] == "secret123"


def test_update_application(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "bookmarked"})
    app_id = create.json()["id"]
    response = client.put(f"/api/applications/{app_id}", json={"company": "Acme Corp", "position": "Senior Engineer", "status": "applied"})
    assert response.status_code == 200
    assert response.json()["company"] == "Acme Corp"


def test_delete_application(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "bookmarked"})
    app_id = create.json()["id"]
    response = client.delete(f"/api/applications/{app_id}")
    assert response.status_code == 200
    listing = client.get("/api/applications")
    assert len(listing.json()) == 0


def test_patch_status(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "bookmarked"})
    app_id = create.json()["id"]
    response = client.patch(f"/api/applications/{app_id}/status", json={"status": "applied"})
    assert response.status_code == 200
    assert response.json()["status"] == "applied"


def test_filter_by_status(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/applications", json={"company": "A", "position": "E", "status": "bookmarked"})
    client.post("/api/applications", json={"company": "B", "position": "E", "status": "applied"})
    response = client.get("/api/applications?status=bookmarked")
    assert len(response.json()) == 1


def test_link_document(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "applied"})
    app_id = create.json()["id"]
    response = client.post(f"/api/applications/{app_id}/documents", json={"document_id": "doc123", "role": "resume"})
    assert response.status_code == 200
    docs = client.get(f"/api/applications/{app_id}/documents")
    assert len(docs.json()) == 1


def test_unlink_document(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "applied"})
    app_id = create.json()["id"]
    link = client.post(f"/api/applications/{app_id}/documents", json={"document_id": "doc123", "role": "resume"})
    link_id = link.json()["id"]
    response = client.delete(f"/api/applications/{app_id}/documents/{link_id}")
    assert response.status_code == 200
    docs = client.get(f"/api/applications/{app_id}/documents")
    assert len(docs.json()) == 0
