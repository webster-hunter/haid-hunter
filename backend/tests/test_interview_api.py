import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.profile import ProfileService
from backend.services.metadata import MetadataService
import backend.config as config
import backend.services.interview as interview_svc


class MockSDKClient:
    """Mock ClaudeSDKClient for testing."""

    def __init__(self, responses=None):
        self.responses = responses or ["Hello!"]
        self._call_count = 0
        self.closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.closed = True

    async def query(self, prompt):
        pass

    async def receive_response(self):
        text = (
            self.responses[self._call_count]
            if self._call_count < len(self.responses)
            else "I understand."
        )
        self._call_count += 1
        msg = MagicMock()
        msg.result = text
        yield msg


def setup_test_env(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    config.DOCUMENTS_DIR = docs_dir
    config.PROFILE_PATH = docs_dir / ".profile.json"
    from backend.routers import profile, interview, documents

    documents._metadata_service = MetadataService(docs_dir)
    profile._profile_service = ProfileService(config.PROFILE_PATH)
    interview._profile_service = profile._profile_service
    interview._sessions = {}


def make_mock_client_factory(responses=None):
    """Return a factory that creates MockSDKClient instances with the given responses."""
    def factory(options=None):
        return MockSDKClient(responses=responses)
    return factory


@patch("backend.services.interview.ClaudeSDKClient")
def test_start_interview(mock_sdk_cls, tmp_path):
    setup_test_env(tmp_path)
    mock_sdk_cls.side_effect = make_mock_client_factory(
        responses=["Hello! Let me review your documents."]
    )

    client = TestClient(app)
    response = client.post("/api/interview/start")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "message" in data
    assert "Hello!" in data["message"]


@patch("backend.services.interview.ClaudeSDKClient")
def test_send_message(mock_sdk_cls, tmp_path):
    setup_test_env(tmp_path)
    mock_sdk_cls.side_effect = make_mock_client_factory(
        responses=["Hello! Let me review your documents.", "Great question!"]
    )

    client = TestClient(app)
    start = client.post("/api/interview/start")
    session_id = start.json()["session_id"]

    response = client.post(
        "/api/interview/message",
        json={"session_id": session_id, "message": "Tell me about my skills"},
    )
    assert response.status_code == 200
    assert "message" in response.json()


def test_message_invalid_session(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post(
        "/api/interview/message",
        json={"session_id": "invalid", "message": "hello"},
    )
    assert response.status_code == 404


@patch("backend.services.interview.ClaudeSDKClient")
def test_accept_suggestion(mock_sdk_cls, tmp_path):
    """Accept endpoint records acceptance in session state and updates the profile."""
    setup_test_env(tmp_path)

    suggestion_json = """\
Here is my suggestion:
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

    mock_sdk_cls.side_effect = make_mock_client_factory(
        responses=["Hello!", suggestion_json]
    )

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
    session = interview_svc._sessions[session_id]
    assert "sug_test001" in session["accepted_suggestions"]


@patch("backend.services.interview.ClaudeSDKClient")
def test_reject_suggestion(mock_sdk_cls, tmp_path):
    """Reject endpoint records rejection in session state."""
    setup_test_env(tmp_path)

    suggestion_json = """\
Here is my suggestion:
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

    mock_sdk_cls.side_effect = make_mock_client_factory(
        responses=["Hello!", suggestion_json]
    )

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
    session = interview_svc._sessions[session_id]
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


def test_expired_session_is_cleaned_up(tmp_path):
    """Sessions older than SESSION_TTL are removed on cleanup."""
    setup_test_env(tmp_path)
    old_time = datetime.now(timezone.utc) - timedelta(minutes=60)
    mock_client = MockSDKClient()
    interview_svc._sessions["expired_session"] = {
        "client": mock_client,
        "suggestions": {},
        "accepted_suggestions": [],
        "rejected_suggestions": [],
        "created_at": old_time,
        "last_active": old_time,
    }
    loop = asyncio.new_event_loop()
    loop.run_until_complete(interview_svc.cleanup_expired_sessions())
    loop.close()
    assert "expired_session" not in interview_svc._sessions
    assert mock_client.closed


def test_active_session_not_cleaned_up(tmp_path):
    """Sessions within TTL are kept after cleanup."""
    setup_test_env(tmp_path)
    now = datetime.now(timezone.utc)
    mock_client = MockSDKClient()
    interview_svc._sessions["active_session"] = {
        "client": mock_client,
        "suggestions": {},
        "accepted_suggestions": [],
        "rejected_suggestions": [],
        "created_at": now,
        "last_active": now,
    }
    loop = asyncio.new_event_loop()
    loop.run_until_complete(interview_svc.cleanup_expired_sessions())
    loop.close()
    assert "active_session" in interview_svc._sessions
    assert not mock_client.closed


@patch("backend.services.interview.ClaudeSDKClient")
def test_interview_start_rate_limited(mock_sdk_cls, tmp_path):
    """Starting too many interviews triggers rate limiting."""
    setup_test_env(tmp_path)
    mock_sdk_cls.side_effect = make_mock_client_factory(responses=["Hello!"])

    client = TestClient(app)
    # Send 6 requests — limit is 5/minute
    responses = [client.post("/api/interview/start") for _ in range(6)]
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes, f"Expected at least one 429, got {status_codes}"


@patch("backend.services.interview.ClaudeSDKClient")
def test_accept_rejects_invalid_section(mock_sdk_cls, tmp_path):
    """Accepting a suggestion targeting an invalid section returns 400."""
    setup_test_env(tmp_path)

    suggestion_json = """\
```suggestion
{
  "suggestion_id": "sug_bad_section",
  "section": "__proto__",
  "action": "add",
  "target": {},
  "original": "",
  "proposed": "injected"
}
```"""

    mock_sdk_cls.side_effect = make_mock_client_factory(
        responses=["Hello!", suggestion_json]
    )

    client = TestClient(app)
    start = client.post("/api/interview/start")
    session_id = start.json()["session_id"]
    client.post(
        "/api/interview/message",
        json={"session_id": session_id, "message": "test"},
    )

    response = client.post(
        "/api/interview/accept",
        json={"session_id": session_id, "suggestion_id": "sug_bad_section"},
    )
    assert response.status_code == 400


@patch("backend.services.interview.ClaudeSDKClient")
def test_accept_rejects_out_of_bounds_index(mock_sdk_cls, tmp_path):
    """Accepting a suggestion with an out-of-bounds index returns 400."""
    setup_test_env(tmp_path)

    suggestion_json = """\
```suggestion
{
  "suggestion_id": "sug_oob",
  "section": "skills",
  "action": "update",
  "target": {"index": 999},
  "original": "",
  "proposed": "hacked"
}
```"""

    mock_sdk_cls.side_effect = make_mock_client_factory(
        responses=["Hello!", suggestion_json]
    )

    client = TestClient(app)
    start = client.post("/api/interview/start")
    session_id = start.json()["session_id"]
    client.post(
        "/api/interview/message",
        json={"session_id": session_id, "message": "test"},
    )

    response = client.post(
        "/api/interview/accept",
        json={"session_id": session_id, "suggestion_id": "sug_oob"},
    )
    assert response.status_code == 400
