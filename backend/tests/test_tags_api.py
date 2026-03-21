from fastapi.testclient import TestClient
from backend.main import app
from backend.services.metadata import MetadataService
import backend.config as config


def setup_test_env(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    config.DOCUMENTS_DIR = docs_dir
    from backend.routers import documents, tags
    documents._metadata_service = MetadataService(docs_dir)
    tags._metadata_service = documents._metadata_service
    return docs_dir


def test_list_tags(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/tags")
    assert response.status_code == 200
    assert set(response.json()) == {"resume", "cover-letter", "cv"}


def test_create_tag(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/tags", json={"name": "engineering"})
    assert response.status_code == 200
    tags_list = client.get("/api/tags").json()
    assert "engineering" in tags_list


def test_delete_tag(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/tags", json={"name": "engineering"})
    response = client.delete("/api/tags/engineering")
    assert response.status_code == 200
    tags_list = client.get("/api/tags").json()
    assert "engineering" not in tags_list
