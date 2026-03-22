from fastapi.testclient import TestClient
from backend.main import app
from backend.services.database import init_db, get_connection
from backend.services.encryption import EncryptionService
from backend.services.metadata import MetadataService
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
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir(exist_ok=True)
    applications._metadata_service = MetadataService(docs_dir)


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


def test_search_applications(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/applications", json={"company": "Globex Corp", "position": "Data Scientist", "status": "applied"})
    client.post("/api/applications", json={"company": "Initech", "position": "Software Engineer", "status": "applied"})
    client.post("/api/applications", json={"company": "Globex Corp", "position": "ML Engineer", "status": "bookmarked"})

    # Search by company substring
    response = client.get("/api/applications?search=Globex")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert all("Globex" in r["company"] for r in results)

    # Search by position substring
    response = client.get("/api/applications?search=Engineer")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2

    # Search with no matches
    response = client.get("/api/applications?search=Nonexistent")
    assert response.status_code == 200
    assert response.json() == []


def test_filter_by_has_referral(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/applications", json={
        "company": "Acme", "position": "Engineer", "status": "applied",
        "has_referral": True, "referral_name": "Jane Doe"
    })
    client.post("/api/applications", json={
        "company": "Initech", "position": "Analyst", "status": "applied",
        "has_referral": False
    })
    client.post("/api/applications", json={
        "company": "Umbrella", "position": "Researcher", "status": "bookmarked",
        "has_referral": True, "referral_name": "John Smith"
    })

    # Filter for apps with referral
    response = client.get("/api/applications?has_referral=true")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert all(r["has_referral"] for r in results)

    # Filter for apps without referral
    response = client.get("/api/applications?has_referral=false")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert not results[0]["has_referral"]


def test_cascade_delete_via_api(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    # Create an application
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "applied"})
    assert create.status_code == 200
    app_id = create.json()["id"]

    # Link a document to the application
    link = client.post(f"/api/applications/{app_id}/documents", json={"document_id": "doc-cascade-test", "role": "resume"})
    assert link.status_code == 200

    # Verify the document link exists
    docs_before = client.get(f"/api/applications/{app_id}/documents")
    assert len(docs_before.json()) == 1

    # Delete the application via API
    delete_resp = client.delete(f"/api/applications/{app_id}")
    assert delete_resp.status_code == 200

    # Verify the application is gone
    get_resp = client.get(f"/api/applications/{app_id}")
    assert get_resp.status_code == 404

    # Verify the document link is also gone (cascade)
    from backend.routers import applications
    conn = applications.get_db()
    rows = conn.execute(
        "SELECT * FROM application_documents WHERE application_id = ?", (app_id,)
    ).fetchall()
    conn.close()
    assert len(rows) == 0
