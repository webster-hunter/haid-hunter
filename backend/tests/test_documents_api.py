from fastapi.testclient import TestClient
from backend.main import app
from backend.services.metadata import MetadataService
from backend.config import DOCUMENTS_DIR
import backend.config as config


def setup_test_env(tmp_path):
    """Override config to use temp directory."""
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    config.DOCUMENTS_DIR = docs_dir
    from backend.routers import documents
    documents._metadata_service = MetadataService(docs_dir)
    return docs_dir


def test_list_documents_empty(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert response.json() == []


def test_upload_document(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post(
        "/api/documents/upload",
        files={"files": ("test.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["original_name"] == "test.txt"


def test_list_documents_after_upload(tmp_path):
    docs_dir = setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/documents/upload", files={"files": ("test.txt", b"hello", "text/plain")})
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_document_content(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    upload = client.post("/api/documents/upload", files={"files": ("test.txt", b"hello world", "text/plain")})
    file_id = upload.json()[0]["id"]
    response = client.get(f"/api/documents/{file_id}/content")
    assert response.status_code == 200
    assert response.content == b"hello world"


def test_delete_document(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    upload = client.post("/api/documents/upload", files={"files": ("test.txt", b"hello", "text/plain")})
    file_id = upload.json()[0]["id"]
    response = client.delete(f"/api/documents/{file_id}")
    assert response.status_code == 200
    listing = client.get("/api/documents")
    assert len(listing.json()) == 0


def test_update_document_metadata(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    upload = client.post("/api/documents/upload", files={"files": ("test.txt", b"hello", "text/plain")})
    file_id = upload.json()[0]["id"]
    response = client.put(f"/api/documents/{file_id}", json={"display_name": "My Doc", "tags": ["resume"]})
    assert response.status_code == 200
    assert response.json()["display_name"] == "My Doc"


def test_sync_documents(tmp_path):
    docs_dir = setup_test_env(tmp_path)
    client = TestClient(app)
    (docs_dir / "dropped_file.txt").write_text("dropped in")
    response = client.post("/api/documents/sync")
    assert response.status_code == 200
    assert len(response.json()["added"]) == 1


def test_filter_by_tag(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/documents/upload", files={"files": ("a.txt", b"a", "text/plain")})
    client.post("/api/documents/upload", files={"files": ("b.txt", b"b", "text/plain")})
    docs = client.get("/api/documents").json()
    client.put(f"/api/documents/{docs[0]['id']}", json={"tags": ["resume"]})
    filtered = client.get("/api/documents?tag=resume")
    assert len(filtered.json()) == 1


def test_search_documents(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/documents/upload", files={"files": ("resume.txt", b"a", "text/plain")})
    client.post("/api/documents/upload", files={"files": ("cover.txt", b"b", "text/plain")})
    result = client.get("/api/documents?search=resume")
    assert len(result.json()) == 1


def test_upload_rejected_for_unsupported_type(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/documents/upload", files={"files": ("photo.png", b"img", "image/png")})
    assert response.status_code == 400
