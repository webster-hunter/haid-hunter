from pathlib import Path
from backend.services.document_reader import read_document_contents


def test_reads_text_file(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    (docs_dir / "abc_resume.txt").write_text("Python developer with 5 years experience")
    metadata = {
        "files": {
            "abc": {
                "original_name": "resume.txt",
                "stored_name": "abc_resume.txt",
                "mime_type": "text/plain",
            }
        }
    }
    result = read_document_contents(docs_dir, metadata)
    assert "resume.txt" in result
    assert "Python developer" in result


def test_skips_path_traversal(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    parent_file = tmp_path / "secret.txt"
    parent_file.write_text("secret data")
    metadata = {
        "files": {
            "xyz": {
                "original_name": "secret.txt",
                "stored_name": "../secret.txt",
                "mime_type": "text/plain",
            }
        }
    }
    result = read_document_contents(docs_dir, metadata)
    assert "secret data" not in result


def test_returns_fallback_when_no_documents(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    result = read_document_contents(docs_dir, {"files": {}})
    assert result == "No previewable documents found."
