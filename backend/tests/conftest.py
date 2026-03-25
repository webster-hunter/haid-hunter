import pytest
from pathlib import Path
from fastapi.testclient import TestClient
import backend.auth as auth_mod
from backend.rate_limit import limiter


@pytest.fixture(autouse=True)
def disable_auth():
    """Disable bearer token auth for all tests."""
    original = auth_mod.API_TOKEN
    auth_mod.API_TOKEN = None
    yield
    auth_mod.API_TOKEN = original


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state between tests to prevent cross-test 429s."""
    yield
    limiter.reset()


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
