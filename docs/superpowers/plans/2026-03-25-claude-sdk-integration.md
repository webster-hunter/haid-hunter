# Claude Code SDK Integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace direct `anthropic` SDK usage with `claude-agent-sdk` Python package for all LLM calls, eliminating API key management and enabling agentic tool use.

**Architecture:** In-process Python SDK integration via FastAPI. One-shot `query()` for extraction and posting analysis. Persistent `ClaudeSDKClient` for multi-turn interview sessions. Schema auto-generated from Pydantic models.

**Tech Stack:** Python 3.11+, FastAPI, claude-agent-sdk, pytest, vitest, React/TypeScript

---

## File Structure

| File | Role | Action |
|---|---|---|
| `backend/services/schema.py` | Auto-generate profile schema string from Pydantic models | Create |
| `backend/services/posting.py` | Job posting analysis via one-shot `query()` with `WebFetch` | Create |
| `backend/routers/posting.py` | `POST /api/posting/analyze` endpoint | Create |
| `backend/services/interview.py` | Multi-turn interview via `ClaudeSDKClient` | Rewrite |
| `backend/services/extraction.py` | Document extraction via one-shot `query()` | Rewrite |
| `backend/config.py` | Remove API key logic | Modify |
| `backend/routers/interview.py` | Remove `read_document_contents`, add service methods for accept/reject | Modify |
| `backend/routers/extraction.py` | Remove `read_document_contents` import | Modify |
| `backend/routers/settings.py` | Remove API key endpoints | Modify |
| `backend/services/profile.py` | Add `objectives` to `VALID_SECTIONS` and `EMPTY_PROFILE` | Modify |
| `backend/routers/profile.py` | Add `objectives` to `ProfileRequest` and validators | Modify |
| `backend/main.py` | Add shutdown handler for session cleanup, add posting router | Modify |
| `backend/requirements.txt` | Swap `anthropic`/`pdfplumber` for `claude-agent-sdk` | Modify |
| `backend/services/document_reader.py` | No longer needed | Delete |
| `src/api/settings.ts` | Remove API key functions | Rewrite |
| `src/api/profile.ts` | Add `objectives` field to `Profile` | Modify |
| `src/api/interview.ts` | Update startInterview response type to include `suggestions[]` | Modify |
| `src/components/settings/SettingsView.tsx` | Remove API key UI | Rewrite |
| `src/__tests__/settings/SettingsView.test.tsx` | Rewrite for simplified settings | Rewrite |
| `backend/tests/test_schema.py` | New tests for schema generation | Create |
| `backend/tests/test_interview_api.py` | Rewrite for SDK mocks | Rewrite |
| `backend/tests/test_extraction.py` | Rewrite for SDK mocks | Rewrite |
| `backend/tests/test_extraction_api.py` | Update mocks | Modify |
| `backend/tests/test_settings_api.py` | Remove API key tests | Modify |
| `backend/tests/test_posting_service.py` | New tests for posting service | Create |
| `backend/tests/test_posting_api.py` | New tests for posting router | Create |
| `backend/tests/test_document_reader.py` | No longer needed | Delete |

---

### Task 1: ~~Add `objectives` field to profile model~~ (REVERSED)

> **Note:** The `objectives` section was deprecated and removed from the profile model. All references to objectives have been removed from code, tests, and specs.

---

### Task 2: Update dependencies

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Update requirements.txt**

Replace `anthropic` and `pdfplumber` with `claude-agent-sdk`:

```
fastapi==0.115.12
uvicorn[standard]==0.34.3
python-multipart==0.0.20
httpx==0.28.1
pytest==8.3.5
pytest-asyncio==0.25.3
claude-agent-sdk>=0.1.50
cryptography==44.0.3
python-dotenv==1.1.0
python-magic-bin>=0.4.14
slowapi>=0.1.9
```

- [ ] **Step 2: Install new dependencies**

Run: `pip install -r backend/requirements.txt`
Expected: `claude-agent-sdk` installs successfully

- [ ] **Step 3: Verify import works**

Run: `python -c "from claude_agent_sdk import query, ClaudeSDKClient, ClaudeAgentOptions; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore: swap anthropic/pdfplumber for claude-agent-sdk"
```

---

### Task 3: Create schema auto-generator

**Files:**
- Create: `backend/services/schema.py`
- Create: `backend/tests/test_schema.py`

- [ ] **Step 1: Write failing test for schema generation**

Create `backend/tests/test_schema.py`:

```python
from backend.services.schema import generate_profile_schema


def test_schema_includes_all_sections():
    schema = generate_profile_schema()
    assert "summary: string" in schema
    assert "skills: string[]" in schema
    assert "experience:" in schema
    assert "education:" in schema
    assert "certifications:" in schema
    assert "activities:" in schema
    assert "objectives: string[]" in schema


def test_schema_includes_experience_fields():
    schema = generate_profile_schema()
    assert "company: string" in schema
    assert "role: string" in schema
    assert "start_date:" in schema
    assert "end_date:" in schema
    assert "accomplishments: string[]" in schema


def test_schema_includes_activity_fields():
    schema = generate_profile_schema()
    assert "name: string" in schema
    assert "category: string" in schema
    assert "details: string[]" in schema


def test_schema_includes_education_fields():
    schema = generate_profile_schema()
    assert "institution: string" in schema
    assert "degree: string" in schema
    assert "field:" in schema


def test_schema_includes_certification_fields():
    schema = generate_profile_schema()
    assert "issuer: string" in schema
    assert "date:" in schema
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest backend/tests/test_schema.py -v`
Expected: FAIL — `backend.services.schema` not found

- [ ] **Step 3: Implement schema generator**

Create `backend/services/schema.py`:

```python
"""Auto-generate profile schema string from Pydantic models for LLM system prompts."""

from backend.routers.profile import (
    ProfileRequest,
    ExperienceEntry,
    ActivityEntry,
    EducationEntry,
    CertificationEntry,
)


def _type_str(annotation) -> str:
    """Convert a Python type annotation to a compact schema string."""
    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", ())

    # Handle Optional (Union with None)
    if origin is type(None):
        return "null"

    # Handle Union types (e.g., str | None)
    import types
    if isinstance(annotation, types.UnionType) or (origin is not None and str(origin) == "typing.Union"):
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return f"{_type_str(non_none[0])} | null"
        return " | ".join(_type_str(a) for a in args)

    if origin is list:
        inner = _type_str(args[0]) if args else "any"
        return f"{inner}[]"

    if annotation is str:
        return "string"
    if annotation is int:
        return "integer"
    if annotation is float:
        return "number"
    if annotation is bool:
        return "boolean"

    return str(annotation)


def _format_model(model_class, indent: int = 2) -> str:
    """Format a Pydantic model's fields as a compact schema block."""
    lines = []
    prefix = " " * indent
    for name, field_info in model_class.model_fields.items():
        type_s = _type_str(field_info.annotation)
        lines.append(f"{prefix}{name}: {type_s}")
    return "\n".join(lines)


def generate_profile_schema() -> str:
    """Generate a human-readable profile schema string from Pydantic models."""
    lines = ["Profile Schema:"]

    for name, field_info in ProfileRequest.model_fields.items():
        annotation = field_info.annotation
        origin = getattr(annotation, "__origin__", None)
        args = getattr(annotation, "__args__", ())

        if origin is list and args:
            inner = args[0]
            # Check if inner type is a Pydantic model
            if hasattr(inner, "model_fields"):
                lines.append(f"  {name}:")
                lines.append(f"    [{_format_model(inner, indent=6)}]")
            else:
                lines.append(f"  {name}: {_type_str(inner)}[]")
        else:
            lines.append(f"  {name}: {_type_str(annotation)}")

    return "\n".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest backend/tests/test_schema.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/schema.py backend/tests/test_schema.py
git commit -m "feat: add schema auto-generator from Pydantic models"
```

---

### Task 4: Rewrite extraction service

**Files:**
- Rewrite: `backend/services/extraction.py`
- Rewrite: `backend/tests/test_extraction.py`
- Modify: `backend/routers/extraction.py`
- Modify: `backend/tests/test_extraction_api.py`

- [ ] **Step 1: Write failing test for SDK-based extraction**

Rewrite `backend/tests/test_extraction.py`:

```python
import json
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from backend.services.extraction import extract_from_documents, merge_suggestions


def _make_sdk_messages(text: str):
    """Simulate SDK query() yielding messages with a result."""
    async def mock_query(*args, **kwargs):
        msg = MagicMock()
        msg.result = text
        msg.__contains__ = lambda self, key: key == "result"
        yield msg
    return mock_query


class TestExtractFromDocuments:
    @pytest.mark.asyncio
    async def test_returns_structured_suggestions(self):
        fake_result = json.dumps({
            "skills": ["Python", "FastAPI"],
            "technologies": ["Docker"],
            "experience_keywords": ["led team of 5"],
            "soft_skills": ["collaboration"],
        })

        with patch("backend.services.extraction.query", side_effect=_make_sdk_messages(fake_result)):
            result = await extract_from_documents("/fake/docs/dir")

        assert result["skills"] == ["Python", "FastAPI"]
        assert result["technologies"] == ["Docker"]

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_documents_dir(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # The SDK will read the directory and find nothing
        with patch("backend.services.extraction.query", side_effect=_make_sdk_messages(json.dumps({
            "skills": [], "technologies": [], "experience_keywords": [], "soft_skills": []
        }))):
            result = await extract_from_documents(str(empty_dir))

        assert result["skills"] == []

    @pytest.mark.asyncio
    async def test_handles_malformed_response(self):
        with patch("backend.services.extraction.query", side_effect=_make_sdk_messages("not json")):
            result = await extract_from_documents("/fake/dir")

        assert result == {"skills": [], "technologies": [], "experience_keywords": [], "soft_skills": []}


class TestMergeSuggestions:
    def test_merges_new_skills_into_existing(self):
        existing = {"skills": ["Python", "SQL"], "experience": [], "education": [], "certifications": [], "summary": "", "objectives": []}
        suggestions = {"skills": ["Python", "FastAPI"], "technologies": ["Docker"], "experience_keywords": [], "soft_skills": ["collaboration"]}
        result = merge_suggestions(existing, suggestions)
        assert result["skills"].count("Python") == 1
        assert "FastAPI" in result["skills"]
        assert "Docker" in result["skills"]
        assert "collaboration" in result["skills"]

    def test_handles_empty_suggestions(self):
        existing = {"skills": ["Python"], "experience": [], "education": [], "certifications": [], "summary": "", "objectives": []}
        suggestions = {"skills": [], "technologies": [], "experience_keywords": [], "soft_skills": []}
        result = merge_suggestions(existing, suggestions)
        assert result["skills"] == ["Python"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest backend/tests/test_extraction.py -v`
Expected: FAIL — `extract_from_documents` is not async, no `query` to patch

- [ ] **Step 3: Rewrite extraction service**

Rewrite `backend/services/extraction.py`:

```python
import json
import logging
from fastapi import HTTPException
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.exceptions import CLINotFoundError, CLIConnectionError, ProcessError, ClaudeSDKError
from backend.services.schema import generate_profile_schema

logger = logging.getLogger(__name__)

EMPTY_RESULT = {
    "skills": [],
    "technologies": [],
    "experience_keywords": [],
    "soft_skills": [],
}

EXTRACTION_PROMPT = """Analyze the documents in the current working directory.
Read all files you can find using the Read and Glob tools.

Return ONLY a JSON object with these keys:
- "skills": Technical skills mentioned (programming languages, frameworks, tools)
- "technologies": Infrastructure, platforms, databases, cloud services
- "experience_keywords": Key accomplishments, metrics, and experience highlights (short phrases)
- "soft_skills": Leadership, communication, teamwork, and other soft skills

Be specific and extract actual terms/phrases from the documents. Do not invent or generalize.

{schema}"""


async def extract_from_documents(documents_dir: str) -> dict:
    schema = generate_profile_schema()
    prompt = EXTRACTION_PROMPT.format(schema=schema)

    result_text = ""
    options = ClaudeAgentOptions(
        system_prompt="You are a document analysis assistant. Read all documents in the working directory and extract structured information.",
        max_turns=5,
        cwd=documents_dir,
        allowed_tools=["Read", "Glob"],
        permission_mode="bypassPermissions",
    )

    try:
        async for message in query(prompt=prompt, options=options):
            if hasattr(message, "result"):
                result_text = message.result
    except (CLINotFoundError, CLIConnectionError):
        raise HTTPException(status_code=503, detail="Claude Code CLI is not available")
    except ProcessError:
        raise HTTPException(status_code=502, detail="Claude SDK process failed")
    except ClaudeSDKError as e:
        raise HTTPException(status_code=500, detail=f"Claude SDK error: {e}")

    # Parse JSON from result
    try:
        # Try to extract JSON from the response (may be wrapped in markdown)
        text = result_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        parsed = json.loads(text.strip())
        return {
            "skills": parsed.get("skills", []),
            "technologies": parsed.get("technologies", []),
            "experience_keywords": parsed.get("experience_keywords", []),
            "soft_skills": parsed.get("soft_skills", []),
        }
    except (json.JSONDecodeError, AttributeError, IndexError):
        logger.warning("Failed to parse extraction response: %s", result_text[:200])
        return dict(EMPTY_RESULT)


def merge_suggestions(existing_profile: dict, suggestions: dict) -> dict:
    profile = dict(existing_profile)
    existing_skills = set(profile.get("skills", []))
    new_skills = (
        suggestions.get("skills", [])
        + suggestions.get("technologies", [])
        + suggestions.get("soft_skills", [])
    )
    merged = list(profile.get("skills", []))
    for skill in new_skills:
        if skill not in existing_skills:
            merged.append(skill)
            existing_skills.add(skill)
    profile["skills"] = merged
    return profile
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest backend/tests/test_extraction.py -v`
Expected: ALL PASS

- [ ] **Step 5: Update extraction router to use async**

Update `backend/routers/extraction.py` — remove `document_reader` import, make `analyze_documents` use the async service:

```python
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from backend.config import DOCUMENTS_DIR, PROFILE_PATH
from backend.services.extraction import extract_from_documents, merge_suggestions
from backend.services.profile import ProfileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/extraction", tags=["extraction"])

_profile_service: ProfileService | None = None


def get_profile_service() -> ProfileService:
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService(PROFILE_PATH)
    return _profile_service


class AcceptSuggestionsRequest(BaseModel):
    skills: list[str] = []
    technologies: list[str] = []
    experience_keywords: list[str] = []
    soft_skills: list[str] = []


@router.post("/analyze")
async def analyze_documents():
    logger.info("Running extraction on documents directory")
    result = await extract_from_documents(str(DOCUMENTS_DIR))
    return result


@router.post("/accept")
async def accept_suggestions(body: AcceptSuggestionsRequest):
    profile_svc = get_profile_service()
    existing = profile_svc.get()
    merged = merge_suggestions(existing, body.model_dump())
    profile_svc.put(merged)
    logger.info("Accepted extraction suggestions into profile")
    return profile_svc.get()
```

- [ ] **Step 6: Update extraction API tests**

Update `backend/tests/test_extraction_api.py` to patch `extract_from_documents` as async:

Replace `patch("backend.routers.extraction.read_document_contents", ...)` with `patch("backend.services.extraction.query", ...)` or patch the service function directly with `AsyncMock`.

- [ ] **Step 7: Run all extraction tests**

Run: `python -m pytest backend/tests/test_extraction.py backend/tests/test_extraction_api.py -v`
Expected: ALL PASS

- [ ] **Step 8: Commit**

```bash
git add backend/services/extraction.py backend/routers/extraction.py backend/tests/test_extraction.py backend/tests/test_extraction_api.py
git commit -m "feat: rewrite extraction service to use claude-agent-sdk query()"
```

---

### Task 5: Rewrite interview service

**Files:**
- Rewrite: `backend/services/interview.py`
- Rewrite: `backend/tests/test_interview_api.py`
- Modify: `backend/routers/interview.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing test for SDK-based interview start**

Rewrite `backend/tests/test_interview_api.py` with SDK mocks. Create a minimal test first:

```python
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.profile import ProfileService
from backend.services.metadata import MetadataService
import backend.config as config
import backend.services.interview as interview_svc


def setup_test_env(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    config.DOCUMENTS_DIR = docs_dir
    config.PROFILE_PATH = docs_dir / ".profile.json"
    from backend.routers import profile, interview
    profile._profile_service = ProfileService(config.PROFILE_PATH)
    interview._profile_service = profile._profile_service
    interview._sessions = {}


class MockSDKClient:
    """Mock ClaudeSDKClient for testing."""
    def __init__(self, responses=None):
        self.responses = responses or ["Hello! Let me review your documents."]
        self._call_count = 0
        self.closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.closed = True

    async def query(self, prompt):
        pass

    async def receive_response(self):
        text = self.responses[self._call_count] if self._call_count < len(self.responses) else "I understand."
        self._call_count += 1
        msg = MagicMock()
        msg.result = text
        yield msg


@patch("backend.services.interview.ClaudeSDKClient")
def test_start_interview(mock_sdk_class, tmp_path):
    setup_test_env(tmp_path)
    mock_client = MockSDKClient()
    mock_sdk_class.return_value = mock_client

    client = TestClient(app)
    response = client.post("/api/interview/start")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "message" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest backend/tests/test_interview_api.py::test_start_interview -v`
Expected: FAIL — interview service still imports `anthropic`

- [ ] **Step 3: Rewrite interview service**

Rewrite `backend/services/interview.py`:

```python
import uuid
import json
import logging
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.exceptions import CLINotFoundError, CLIConnectionError, ProcessError, ClaudeSDKError
from backend.services.schema import generate_profile_schema

logger = logging.getLogger(__name__)

SESSION_TTL = timedelta(minutes=30)
MAX_SESSIONS = 20

_sessions: dict = {}


async def cleanup_expired_sessions():
    """Remove sessions that have been inactive longer than SESSION_TTL."""
    cutoff = datetime.now(timezone.utc) - SESSION_TTL
    expired = [sid for sid, s in _sessions.items() if s.get("last_active", s.get("created_at", cutoff)) < cutoff]
    for sid in expired:
        session = _sessions.pop(sid)
        client = session.get("client")
        if client:
            try:
                await client.__aexit__(None, None, None)
            except Exception:
                logger.warning("Failed to close SDK client for session %s", sid)


SYSTEM_PROMPT = """You are a career profile interview assistant for hAId-hunter, a job application tool.

Your job is to help the user build a comprehensive candidate profile by:
1. Reviewing their uploaded documents (use Read and Glob tools to read files in the working directory)
2. Asking targeted follow-up questions to fill gaps and add detail
3. Proposing structured updates to their profile

When you want to suggest a profile update, include a JSON block in your response like:
```suggestion
{{
  "suggestion_id": "sug_<random>",
  "section": "experience|skills|education|certifications|activities|summary|objectives",
  "action": "add|update|remove",
  "target": {{ ... }},
  "original": "...",
  "proposed": "..."
}}
```

{schema}

Current Profile:
```json
{profile}
```

Focus on:
- Quantifiable accomplishments (numbers, percentages, team sizes)
- Technologies and tools used
- Impact and scope of work
- Leadership and collaboration examples
- Details that differentiate them from other candidates

Be conversational but focused. One question at a time. Base your questions on what you see in their documents and current profile."""


async def start_session(profile: dict, documents_dir: str) -> tuple[str, str]:
    await cleanup_expired_sessions()
    if len(_sessions) >= MAX_SESSIONS:
        oldest_sid = min(_sessions, key=lambda s: _sessions[s].get("last_active", datetime.min.replace(tzinfo=timezone.utc)))
        old_session = _sessions.pop(oldest_sid)
        client = old_session.get("client")
        if client:
            try:
                await client.__aexit__(None, None, None)
            except Exception:
                pass

    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    schema = generate_profile_schema()
    system = SYSTEM_PROMPT.format(
        schema=schema,
        profile=json.dumps(profile, indent=2),
    )

    options = ClaudeAgentOptions(
        system_prompt=system,
        max_turns=3,
        cwd=documents_dir,
        allowed_tools=["Read", "Glob"],
        permission_mode="bypassPermissions",
    )

    try:
        client = ClaudeSDKClient(options=options)
        await client.__aenter__()

        result_text = ""
        await client.query("Please review my documents and profile, then start asking me questions to help build out my candidate profile.")
        async for msg in client.receive_response():
            if hasattr(msg, "result"):
                result_text = msg.result
    except (CLINotFoundError, CLIConnectionError):
        raise HTTPException(status_code=503, detail="Claude Code CLI is not available")
    except ProcessError:
        raise HTTPException(status_code=502, detail="Claude SDK process failed")
    except ClaudeSDKError as e:
        raise HTTPException(status_code=500, detail=f"Claude SDK error: {e}")

    _sessions[session_id] = {
        "client": client,
        "suggestions": {},
        "accepted_suggestions": [],
        "rejected_suggestions": [],
        "created_at": now,
        "last_active": now,
    }

    return session_id, result_text


async def send_message(session_id: str, user_message: str) -> dict:
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")

    session = _sessions[session_id]
    session["last_active"] = datetime.now(timezone.utc)

    client = session["client"]

    try:
        result_text = ""
        await client.query(user_message)
        async for msg in client.receive_response():
            if hasattr(msg, "result"):
                result_text = msg.result
    except (CLINotFoundError, CLIConnectionError):
        raise HTTPException(status_code=503, detail="Claude Code CLI is not available")
    except ProcessError:
        raise HTTPException(status_code=502, detail="Claude SDK process failed")
    except ClaudeSDKError as e:
        raise HTTPException(status_code=500, detail=f"Claude SDK error: {e}")

    # Parse suggestion if present
    suggestion = None
    if "```suggestion" in result_text:
        try:
            start = result_text.index("```suggestion") + len("```suggestion")
            end = result_text.index("```", start)
            suggestion = json.loads(result_text[start:end].strip())
            session["suggestions"][suggestion["suggestion_id"]] = suggestion
        except (ValueError, json.JSONDecodeError, KeyError):
            pass

    return {"message": result_text, "suggestion": suggestion}


def get_suggestion(session_id: str, suggestion_id: str) -> dict | None:
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")
    return _sessions[session_id]["suggestions"].get(suggestion_id)


def accept_suggestion(session_id: str, suggestion_id: str) -> dict | None:
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")
    suggestion = _sessions[session_id]["suggestions"].get(suggestion_id)
    if suggestion:
        _sessions[session_id]["accepted_suggestions"].append(suggestion_id)
    return suggestion


def reject_suggestion(session_id: str, suggestion_id: str) -> dict | None:
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")
    suggestion = _sessions[session_id]["suggestions"].get(suggestion_id)
    if suggestion:
        _sessions[session_id]["rejected_suggestions"].append(suggestion_id)
    return suggestion


async def close_all_sessions():
    """Close all SDK clients. Called on app shutdown."""
    for sid in list(_sessions.keys()):
        session = _sessions.pop(sid)
        client = session.get("client")
        if client:
            try:
                await client.__aexit__(None, None, None)
            except Exception:
                logger.warning("Failed to close SDK client for session %s", sid)
```

- [ ] **Step 4: Update interview router**

Rewrite `backend/routers/interview.py`:

```python
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from backend.config import DOCUMENTS_DIR, PROFILE_PATH
from backend.services.profile import ProfileService, VALID_SECTIONS
from backend.services import interview as interview_service
from backend.rate_limit import limiter

router = APIRouter(prefix="/api/interview", tags=["interview"])

_profile_service: ProfileService | None = None
_sessions: dict | None = None


def get_profile_service() -> ProfileService:
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService(PROFILE_PATH)
    return _profile_service


def _sync_sessions():
    global _sessions
    if _sessions is not None:
        interview_service._sessions = _sessions


class MessageRequest(BaseModel):
    session_id: str
    message: str


class SuggestionRequest(BaseModel):
    session_id: str
    suggestion_id: str


@router.post("/start")
@limiter.limit("5/minute")
async def start_interview(request: Request):
    _sync_sessions()
    profile = get_profile_service().get()
    session_id, message = await interview_service.start_session(profile, str(DOCUMENTS_DIR))
    return {"session_id": session_id, "message": message}


@router.post("/message")
@limiter.limit("20/minute")
async def send_message(request: Request, body: MessageRequest):
    _sync_sessions()
    try:
        result = await interview_service.send_message(body.session_id, body.message)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")


@router.post("/accept")
async def accept_suggestion(body: SuggestionRequest):
    _sync_sessions()
    try:
        suggestion = interview_service.get_suggestion(body.session_id, body.suggestion_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    service = get_profile_service()
    profile = service.get()
    section = suggestion.get("section")
    action = suggestion.get("action")
    target = suggestion.get("target", {})

    if section not in VALID_SECTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid suggestion section: {section}")

    if action not in ("add", "update", "remove"):
        raise HTTPException(status_code=400, detail=f"Invalid suggestion action: {action}")

    if action in ("update", "remove") and isinstance(profile.get(section), list):
        index = target.get("index")
        if section != "summary" and index is not None:
            if not isinstance(index, int) or index < 0 or index >= len(profile.get(section, [])):
                raise HTTPException(status_code=400, detail=f"Index {index} out of bounds for section {section}")

    if action == "add" and isinstance(profile.get(section), list):
        profile[section].append(suggestion["proposed"])
    elif action == "update":
        if section == "summary":
            profile[section] = suggestion["proposed"]
        elif isinstance(profile.get(section), list):
            index = target.get("index")
            field = target.get("field")
            if index is not None and 0 <= index < len(profile[section]):
                if field:
                    item = profile[section][index]
                    if isinstance(item, dict) and field in item:
                        sub_index = target.get("sub_index")
                        if sub_index is not None and isinstance(item[field], list):
                            item[field][sub_index] = suggestion["proposed"]
                        else:
                            item[field] = suggestion["proposed"]
                else:
                    profile[section][index] = suggestion["proposed"]
    elif action == "remove" and isinstance(profile.get(section), list):
        index = target.get("index")
        if index is not None and 0 <= index < len(profile[section]):
            profile[section].pop(index)

    service.put(profile)
    interview_service.accept_suggestion(body.session_id, body.suggestion_id)
    return {"status": "accepted", "profile": profile}


@router.post("/reject")
async def reject_suggestion(body: SuggestionRequest):
    _sync_sessions()
    try:
        suggestion = interview_service.get_suggestion(body.session_id, body.suggestion_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    interview_service.reject_suggestion(body.session_id, body.suggestion_id)
    return {"status": "rejected", "suggestion_id": body.suggestion_id}
```

- [ ] **Step 5: Add shutdown handler in main.py**

In `backend/main.py`, add:

```python
from backend.services import interview as interview_service

@app.on_event("shutdown")
async def shutdown():
    await interview_service.close_all_sessions()
```

- [ ] **Step 6: Write remaining interview tests**

Add tests for: send_message, accept/reject via service methods, session expiry, rate limiting. These follow the same pattern as Step 1 but exercise more paths.

- [ ] **Step 7: Run all interview tests**

Run: `python -m pytest backend/tests/test_interview_api.py -v`
Expected: ALL PASS

- [ ] **Step 8: Commit**

```bash
git add backend/services/interview.py backend/routers/interview.py backend/main.py backend/tests/test_interview_api.py
git commit -m "feat: rewrite interview service to use ClaudeSDKClient"
```

---

### Task 6: Create posting analysis service

**Files:**
- Create: `backend/services/posting.py`
- Create: `backend/routers/posting.py`
- Create: `backend/tests/test_posting_service.py`
- Create: `backend/tests/test_posting_api.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing test for posting service**

Create `backend/tests/test_posting_service.py`:

```python
import json
import pytest
from unittest.mock import patch, MagicMock
from backend.services.posting import analyze_posting


def _make_sdk_messages(text: str):
    async def mock_query(*args, **kwargs):
        msg = MagicMock()
        msg.result = text
        yield msg
    return mock_query


@pytest.mark.asyncio
async def test_analyze_posting_returns_structured_data():
    fake_result = json.dumps({
        "key_requirements": ["5+ years Python", "AWS experience"],
        "emphasis_areas": ["distributed systems"],
        "keywords": ["microservices", "CI/CD"],
    })

    with patch("backend.services.posting.query", side_effect=_make_sdk_messages(fake_result)):
        result = await analyze_posting("https://example.com/job", {})

    assert result["key_requirements"] == ["5+ years Python", "AWS experience"]
    assert result["emphasis_areas"] == ["distributed systems"]
    assert result["keywords"] == ["microservices", "CI/CD"]


@pytest.mark.asyncio
async def test_analyze_posting_handles_malformed_response():
    with patch("backend.services.posting.query", side_effect=_make_sdk_messages("not json")):
        result = await analyze_posting("https://example.com/job", {})

    assert result == {"key_requirements": [], "emphasis_areas": [], "keywords": []}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest backend/tests/test_posting_service.py -v`
Expected: FAIL — `backend.services.posting` not found

- [ ] **Step 3: Implement posting service**

Create `backend/services/posting.py`:

```python
import json
import logging
from fastapi import HTTPException
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.exceptions import CLINotFoundError, CLIConnectionError, ProcessError, ClaudeSDKError
from backend.services.schema import generate_profile_schema

logger = logging.getLogger(__name__)

EMPTY_RESULT = {
    "key_requirements": [],
    "emphasis_areas": [],
    "keywords": [],
}

POSTING_PROMPT = """Fetch and analyze the job posting at this URL: {url}

Based on the posting content and the candidate's current profile, extract:
1. "key_requirements": The most important qualifications and experience required
2. "emphasis_areas": What the employer seems to care about most
3. "keywords": Important terms and phrases from the posting that should appear in a resume

{schema}

Current Profile:
```json
{profile}
```

Return ONLY a JSON object with keys: "key_requirements", "emphasis_areas", "keywords".
Each value should be a list of short strings."""


async def analyze_posting(url: str, profile: dict) -> dict:
    schema = generate_profile_schema()
    prompt = POSTING_PROMPT.format(url=url, schema=schema, profile=json.dumps(profile, indent=2))

    options = ClaudeAgentOptions(
        system_prompt="You are a job posting analyst. Fetch the given URL and analyze the posting content.",
        max_turns=5,
        allowed_tools=["WebFetch"],
        permission_mode="bypassPermissions",
    )

    try:
        result_text = ""
        async for message in query(prompt=prompt, options=options):
            if hasattr(message, "result"):
                result_text = message.result
    except (CLINotFoundError, CLIConnectionError):
        raise HTTPException(status_code=503, detail="Claude Code CLI is not available")
    except ProcessError:
        raise HTTPException(status_code=502, detail="Claude SDK process failed")
    except ClaudeSDKError as e:
        raise HTTPException(status_code=500, detail=f"Claude SDK error: {e}")

    try:
        text = result_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        parsed = json.loads(text.strip())
        return {
            "key_requirements": parsed.get("key_requirements", []),
            "emphasis_areas": parsed.get("emphasis_areas", []),
            "keywords": parsed.get("keywords", []),
        }
    except (json.JSONDecodeError, AttributeError, IndexError):
        logger.warning("Failed to parse posting analysis: %s", result_text[:200])
        return dict(EMPTY_RESULT)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest backend/tests/test_posting_service.py -v`
Expected: ALL PASS

- [ ] **Step 5: Write failing test for posting router**

Create `backend/tests/test_posting_api.py`:

```python
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.profile import ProfileService
import backend.config as config


def setup_test_env(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    config.PROFILE_PATH = docs_dir / ".profile.json"
    from backend.routers import profile, posting
    profile._profile_service = ProfileService(config.PROFILE_PATH)
    posting._profile_service = profile._profile_service


@patch("backend.services.posting.analyze_posting", new_callable=AsyncMock)
def test_analyze_posting_endpoint(mock_analyze, tmp_path):
    setup_test_env(tmp_path)
    mock_analyze.return_value = {
        "key_requirements": ["Python"],
        "emphasis_areas": ["backend"],
        "keywords": ["API"],
    }

    client = TestClient(app)
    response = client.post("/api/posting/analyze", json={"url": "https://example.com/job"})
    assert response.status_code == 200
    data = response.json()
    assert "key_requirements" in data


def test_analyze_posting_missing_url(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/posting/analyze", json={})
    assert response.status_code == 422
```

- [ ] **Step 6: Implement posting router**

Create `backend/routers/posting.py`:

```python
import logging
from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.config import PROFILE_PATH
from backend.services.posting import analyze_posting
from backend.services.profile import ProfileService
from backend.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/posting", tags=["posting"])

_profile_service: ProfileService | None = None


def get_profile_service() -> ProfileService:
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService(PROFILE_PATH)
    return _profile_service


class AnalyzeRequest(BaseModel):
    url: str


@router.post("/analyze")
@limiter.limit("5/minute")
async def analyze(request: Request, body: AnalyzeRequest):
    profile = get_profile_service().get()
    result = await analyze_posting(body.url, profile)
    return result
```

- [ ] **Step 7: Register posting router in main.py**

In `backend/main.py`, add:

```python
from backend.routers.posting import router as posting_router
app.include_router(posting_router)
```

- [ ] **Step 8: Run all posting tests**

Run: `python -m pytest backend/tests/test_posting_service.py backend/tests/test_posting_api.py -v`
Expected: ALL PASS

- [ ] **Step 9: Commit**

```bash
git add backend/services/posting.py backend/routers/posting.py backend/main.py backend/tests/test_posting_service.py backend/tests/test_posting_api.py
git commit -m "feat: add job posting analysis service with WebFetch"
```

---

### Task 7: Remove API key infrastructure

**Files:**
- Modify: `backend/config.py`
- Modify: `backend/routers/settings.py`
- Modify: `backend/tests/test_settings_api.py`
- Rewrite: `src/api/settings.ts`
- Rewrite: `src/components/settings/SettingsView.tsx`
- Rewrite: `src/__tests__/settings/SettingsView.test.tsx`

- [ ] **Step 1: Simplify config.py**

Remove `get_api_key()`, `ANTHROPIC_API_KEY`, and `anthropic`/`encryption` imports from `backend/config.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
DATA_DIR = PROJECT_ROOT / "data"
PROFILE_PATH = DOCUMENTS_DIR / ".profile.json"
METADATA_PATH = DOCUMENTS_DIR / ".metadata.json"
DATABASE_PATH = DATA_DIR / "applications.db"

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".xlsx", ".csv", ".pptx"}

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
```

- [ ] **Step 2: Remove API key endpoints from settings router**

In `backend/routers/settings.py`, remove: `get_api_key_status`, `set_api_key`, `delete_api_key`, `test_api_key`, `_resolve_api_key`, `_mask_key`, `build_claude_client`, `get_encryption`, `get_env_api_key`, `PutApiKeyRequest`, and the `ANTHROPIC_API_KEY` import. Keep generic settings endpoints.

```python
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import DATABASE_PATH
from backend.services.database import get_connection
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])

_db_path: Path | None = None


def get_db():
    global _db_path
    path = _db_path or DATABASE_PATH
    return get_connection(path)


class PutSettingRequest(BaseModel):
    value: str


@router.get("/{key}")
async def get_setting(key: str):
    conn = get_db()
    try:
        row = conn.execute("SELECT key, value FROM settings WHERE key = ?", (key,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Setting not found")
        return dict(row)
    finally:
        conn.close()


@router.put("/{key}")
async def put_setting(key: str, body: PutSettingRequest):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
            (key, body.value, body.value),
        )
        conn.commit()
        row = conn.execute("SELECT key, value FROM settings WHERE key = ?", (key,)).fetchone()
        return dict(row)
    finally:
        conn.close()
```

- [ ] **Step 3: Remove API key tests from settings test file**

In `backend/tests/test_settings_api.py`, remove all API key tests (everything from `api_key_db` fixture onward). Keep generic settings tests.

- [ ] **Step 4: Rewrite frontend settings API**

Rewrite `src/api/settings.ts`:

```typescript
export interface Setting {
  key: string
  value: string
}

export async function getSetting(key: string): Promise<Setting> {
  const res = await fetch(`/api/settings/${key}`)
  if (!res.ok) throw new Error('Setting not found')
  return res.json()
}

export async function putSetting(key: string, value: string): Promise<Setting> {
  const res = await fetch(`/api/settings/${key}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ value }),
  })
  if (!res.ok) throw new Error('Failed to save setting')
  return res.json()
}
```

- [ ] **Step 5: Rewrite SettingsView component**

Rewrite `src/components/settings/SettingsView.tsx` to show a simple status page (no API key management):

```tsx
export default function SettingsView() {
  return (
    <div className="settings-view">
      <h1>Settings</h1>
      <div className="settings-sections">
        <div className="settings-section">
          <h3>Claude Integration</h3>
          <p className="settings-description">
            hAId-hunter uses your Claude Code subscription for AI features.
            No separate API key required.
          </p>
          <div className="api-key-status">
            <span className="api-key-configured">
              <span className="api-key-test-badge valid">Connected via Claude Code</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 6: Rewrite SettingsView test**

Rewrite `src/__tests__/settings/SettingsView.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import SettingsView from '../../components/settings/SettingsView'

describe('SettingsView', () => {
  it('shows Claude Code integration status', () => {
    render(<SettingsView />)
    expect(screen.getByText('Claude Integration')).toBeInTheDocument()
    expect(screen.getByText(/Claude Code/)).toBeInTheDocument()
  })

  it('does not show API key input', () => {
    render(<SettingsView />)
    expect(screen.queryByPlaceholderText('sk-ant-...')).not.toBeInTheDocument()
  })
})
```

- [ ] **Step 7: Update interview API types**

In `src/api/interview.ts`, update `startInterview` return type to include suggestions from the initial response:

```typescript
export async function startInterview(): Promise<{ session_id: string; message: string; suggestions: Suggestion[] }> {
  const res = await fetch('/api/interview/start', { method: 'POST' })
  if (!res.ok) throw new Error('Failed to start interview')
  return res.json()
}
```

- [ ] **Step 8: Run all affected tests**

Run: `python -m pytest backend/tests/test_settings_api.py -v && npx vitest run src/__tests__/settings/`
Expected: ALL PASS

- [ ] **Step 9: Commit**

```bash
git add backend/config.py backend/routers/settings.py backend/tests/test_settings_api.py src/api/settings.ts src/api/interview.ts src/components/settings/SettingsView.tsx src/__tests__/settings/SettingsView.test.tsx
git commit -m "feat: remove API key management, update interview types, use Claude Code subscription"
```

---

### Task 8: Delete document_reader and clean up imports

**Files:**
- Delete: `backend/services/document_reader.py`
- Delete: `backend/tests/test_document_reader.py`

- [ ] **Step 1: Verify no remaining imports of document_reader**

Run: `grep -r "document_reader" backend/ --include="*.py"`

Should only show `document_reader.py` itself and its test file. All other references were already removed in Tasks 4 and 5.

- [ ] **Step 2: Delete files**

```bash
git rm backend/services/document_reader.py backend/tests/test_document_reader.py
```

- [ ] **Step 3: Run full test suite**

Run: `python -m pytest backend/tests/ -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git commit -m "chore: remove document_reader (SDK reads files directly)"
```

---

### Task 9: Run full test suite and fix regressions

**Files:** All

- [ ] **Step 1: Run all backend tests**

Run: `python -m pytest backend/tests/ -v`
Expected: ALL PASS

- [ ] **Step 2: Run all frontend tests**

Run: `npx vitest run`
Expected: ALL PASS

- [ ] **Step 3: Fix any failures**

Address any regressions found. Common issues:
- Import errors from removed modules
- Tests still mocking `get_claude_client` instead of SDK classes
- Async/sync mismatches in tests

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "fix: resolve test regressions from SDK migration"
```

---

## Verification Checklist

```bash
# Backend
python -m pytest backend/tests/ -v

# Frontend
npx vitest run

# Manual smoke test
# 1. Start backend: uvicorn backend.main:app --reload
# 2. Start frontend: npm run dev
# 3. Navigate to /profile → Edit sections → Save
# 4. Navigate to Settings → See "Connected via Claude Code" (no API key form)
# 5. Try extraction (requires Claude Code CLI installed)
# 6. Try interview (requires Claude Code CLI installed)
```
