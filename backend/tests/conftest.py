import pytest
from pathlib import Path
from fastapi.testclient import TestClient


@pytest.fixture
def tmp_documents(tmp_path):
    """Temporary documents directory for testing."""
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    return docs_dir


@pytest.fixture
def tmp_data(tmp_path):
    """Temporary data directory for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir
