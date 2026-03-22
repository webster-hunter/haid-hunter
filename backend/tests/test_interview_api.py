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


@patch("backend.services.interview.get_claude_client")
def test_accept_suggestion(mock_client, tmp_path):
    """Accept endpoint records acceptance in session state and updates the profile."""
    setup_test_env(tmp_path)

    suggestion_json = """\
```suggestion
{
  "suggestion_id": "sug_test001",
  "section": "skills",
  "action": "add",
  "target": {},
  "original": "",
  "proposed": "Python"
}
```"""

    mock_instance = MagicMock()
    mock_instance.messages.create.side_effect = [
        mock_claude_response("Hello!"),
        mock_claude_response(suggestion_json),
    ]
    mock_client.return_value = mock_instance

    client = TestClient(app)
    start = client.post("/api/interview/start")
    assert start.status_code == 200
    session_id = start.json()["session_id"]

    msg = client.post(
        "/api/interview/message",
        json={"session_id": session_id, "message": "What skills do I have?"},
    )
    assert msg.status_code == 200
    assert msg.json()["suggestion"] is not None

    response = client.post(
        "/api/interview/accept",
        json={"session_id": session_id, "suggestion_id": "sug_test001"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert "profile" in data

    # Verify session state records the acceptance
    import backend.services.interview as svc
    session = svc._sessions[session_id]
    assert "sug_test001" in session["accepted_suggestions"]


@patch("backend.services.interview.get_claude_client")
def test_reject_suggestion(mock_client, tmp_path):
    """Reject endpoint records rejection in session state."""
    setup_test_env(tmp_path)

    suggestion_json = """\
```suggestion
{
  "suggestion_id": "sug_test002",
  "section": "skills",
  "action": "add",
  "target": {},
  "original": "",
  "proposed": "Go"
}
```"""

    mock_instance = MagicMock()
    mock_instance.messages.create.side_effect = [
        mock_claude_response("Hello!"),
        mock_claude_response(suggestion_json),
    ]
    mock_client.return_value = mock_instance

    client = TestClient(app)
    start = client.post("/api/interview/start")
    assert start.status_code == 200
    session_id = start.json()["session_id"]

    msg = client.post(
        "/api/interview/message",
        json={"session_id": session_id, "message": "Any other skills?"},
    )
    assert msg.status_code == 200
    assert msg.json()["suggestion"] is not None

    response = client.post(
        "/api/interview/reject",
        json={"session_id": session_id, "suggestion_id": "sug_test002"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["suggestion_id"] == "sug_test002"

    # Verify session state records the rejection
    import backend.services.interview as svc
    session = svc._sessions[session_id]
    assert "sug_test002" in session["rejected_suggestions"]


def test_accept_invalid_session(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post(
        "/api/interview/accept",
        json={"session_id": "invalid", "suggestion_id": "sug_x"},
    )
    assert response.status_code == 404


def test_reject_invalid_session(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post(
        "/api/interview/reject",
        json={"session_id": "invalid", "suggestion_id": "sug_x"},
    )
    assert response.status_code == 404
