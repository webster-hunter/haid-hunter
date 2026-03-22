from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.profile import ProfileService
from backend.services.metadata import MetadataService
import backend.config as config


def setup_test_env(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    config.DOCUMENTS_DIR = docs_dir
    config.PROFILE_PATH = docs_dir / ".profile.json"
    from backend.routers import profile, interview, documents
    documents._metadata_service = MetadataService(docs_dir)
    profile._profile_service = ProfileService(config.PROFILE_PATH)
    interview._metadata_service = documents._metadata_service
    interview._profile_service = profile._profile_service
    interview._sessions = {}


def mock_claude_response(text, suggestion=None):
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text=text)]
    return mock_msg


@patch("backend.services.interview.get_claude_client")
def test_start_interview(mock_client, tmp_path):
    setup_test_env(tmp_path)
    mock_instance = MagicMock()
    mock_instance.messages.create.return_value = mock_claude_response("Hello! Let me review your documents.")
    mock_client.return_value = mock_instance

    client = TestClient(app)
    response = client.post("/api/interview/start")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "message" in data


@patch("backend.services.interview.get_claude_client")
def test_send_message(mock_client, tmp_path):
    setup_test_env(tmp_path)
    mock_instance = MagicMock()
    mock_instance.messages.create.return_value = mock_claude_response("Great question!")
    mock_client.return_value = mock_instance

    client = TestClient(app)
    start = client.post("/api/interview/start")
    session_id = start.json()["session_id"]

    response = client.post("/api/interview/message", json={"session_id": session_id, "message": "Tell me about my skills"})
    assert response.status_code == 200
    assert "message" in response.json()


def test_message_invalid_session(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/interview/message", json={"session_id": "invalid", "message": "hello"})
    assert response.status_code == 404
