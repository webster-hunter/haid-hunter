import json
from pathlib import Path
from backend.services.metadata import MetadataService


def test_init_creates_default_metadata(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    data = service.read()
    assert data["files"] == {}
    assert set(data["tags"]) == {"resume", "cover-letter", "cv"}


def test_init_loads_existing_metadata(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    meta_path = docs_dir / ".metadata.json"
    meta_path.write_text(json.dumps({
        "files": {"abc123": {"original_name": "test.pdf", "stored_name": "abc123_test.pdf",
                             "display_name": "test.pdf", "tags": ["resume"],
                             "uploaded_at": "2026-01-01T00:00:00Z",
                             "size_bytes": 100, "mime_type": "application/pdf"}},
        "tags": ["resume", "cover-letter", "cv", "custom"]
    }))
    service = MetadataService(docs_dir)
    data = service.read()
    assert "abc123" in data["files"]
    assert "custom" in data["tags"]


def test_add_file(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    result = service.add_file("test.txt", b"hello world", tags=["resume"])
    assert result["original_name"] == "test.txt"
    assert result["tags"] == ["resume"]
    assert result["size_bytes"] == 11
    assert (docs_dir / result["stored_name"]).exists()


def test_delete_file(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    result = service.add_file("test.txt", b"hello")
    file_id = result["id"]
    service.delete_file(file_id)
    data = service.read()
    assert file_id not in data["files"]


def test_update_file(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    result = service.add_file("test.txt", b"hello")
    file_id = result["id"]
    updated = service.update_file(file_id, display_name="My Resume", tags=["resume", "engineering"])
    assert updated["display_name"] == "My Resume"
    assert updated["tags"] == ["resume", "engineering"]


def test_sync_discovers_new_files(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    # Drop a file manually
    (docs_dir / "manual_file.txt").write_text("manual content")
    result = service.sync()
    assert len(result["added"]) == 1
    data = service.read()
    assert any(f["original_name"] == "manual_file.txt" for f in data["files"].values())


def test_sync_removes_stale_entries(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    result = service.add_file("test.txt", b"hello")
    # Delete file from disk manually
    stored = docs_dir / result["stored_name"]
    stored.unlink()
    sync_result = service.sync()
    assert len(sync_result["removed"]) == 1


def test_add_and_delete_tag(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    service.add_tag("engineering")
    assert "engineering" in service.get_tags()
    service.delete_tag("engineering")
    assert "engineering" not in service.get_tags()


def test_delete_tag_removes_from_files(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    service.add_tag("engineering")
    result = service.add_file("test.txt", b"hello", tags=["engineering"])
    service.delete_tag("engineering")
    data = service.read()
    assert "engineering" not in data["files"][result["id"]]["tags"]


def test_add_file_sanitizes_path_traversal(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    result = service.add_file("../../evil.txt", b"malicious", tags=[])
    assert result["original_name"] == "evil.txt"
    assert "evil.txt" in result["stored_name"]
    assert "../" not in result["stored_name"]
    # File should be stored inside docs_dir
    stored_path = docs_dir / result["stored_name"]
    assert stored_path.exists()
    assert stored_path.resolve().is_relative_to(docs_dir.resolve())
