import uuid
import json
import logging
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk import CLINotFoundError, CLIConnectionError, ProcessError, ClaudeSDKError
from backend.services.schema import generate_profile_schema

logger = logging.getLogger(__name__)

SESSION_TTL = timedelta(minutes=30)
MAX_SESSIONS = 20

_sessions: dict = {}

SYSTEM_PROMPT = """You are a career profile interview assistant for hAId-hunter, a job application tool.

Your job is to help the user build a comprehensive candidate profile by:
1. Reviewing their uploaded documents (provided below)
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

Focus on:
- Quantifiable accomplishments (numbers, percentages, team sizes)
- Technologies and tools used
- Impact and scope of work
- Leadership and collaboration examples
- Details that differentiate them from other candidates

Be conversational but focused. One question at a time. Base your questions on what you see in their documents and current profile.

{schema}

## Current Profile
```json
{profile_json}
```"""


async def start_session(profile: dict, documents_dir: str) -> tuple[str, str]:
    """Create a new interview session with a ClaudeSDKClient."""
    await cleanup_expired_sessions()

    if len(_sessions) >= MAX_SESSIONS:
        # Evict the oldest session
        oldest_sid = min(
            _sessions,
            key=lambda s: _sessions[s].get(
                "last_active", datetime.min.replace(tzinfo=timezone.utc)
            ),
        )
        await _close_session(oldest_sid)

    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    schema = generate_profile_schema()
    system = SYSTEM_PROMPT.format(
        schema=schema, profile_json=json.dumps(profile, indent=2)
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

        initial_prompt = (
            "Please review my documents and profile, then start asking me "
            "questions to help build out my candidate profile."
        )
        await client.query(initial_prompt)
        result_text = ""
        async for msg in client.receive_response():
            if hasattr(msg, "result") and msg.result is not None:
                result_text = msg.result

        _sessions[session_id] = {
            "client": client,
            "suggestions": {},
            "accepted_suggestions": [],
            "rejected_suggestions": [],
            "created_at": now,
            "last_active": now,
        }

        return session_id, result_text

    except CLINotFoundError as exc:
        logger.error("Claude CLI not found: %s", exc)
        raise HTTPException(status_code=503, detail="Claude CLI not found") from exc
    except CLIConnectionError as exc:
        logger.error("Claude CLI connection error: %s", exc)
        raise HTTPException(status_code=503, detail="Claude CLI connection error") from exc
    except ProcessError as exc:
        logger.error("Claude process error: %s", exc)
        raise HTTPException(status_code=502, detail="Claude process error") from exc
    except ClaudeSDKError as exc:
        logger.error("Claude SDK error: %s", exc)
        raise HTTPException(status_code=500, detail="Claude SDK error") from exc


async def send_message(session_id: str, user_message: str) -> dict:
    """Send a message to an existing interview session."""
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")

    session = _sessions[session_id]
    session["last_active"] = datetime.now(timezone.utc)
    client = session["client"]

    try:
        await client.query(user_message)
        result_text = ""
        async for msg in client.receive_response():
            if hasattr(msg, "result") and msg.result is not None:
                result_text = msg.result

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

    except CLINotFoundError as exc:
        logger.error("Claude CLI not found: %s", exc)
        raise HTTPException(status_code=503, detail="Claude CLI not found") from exc
    except CLIConnectionError as exc:
        logger.error("Claude CLI connection error: %s", exc)
        raise HTTPException(status_code=503, detail="Claude CLI connection error") from exc
    except ProcessError as exc:
        logger.error("Claude process error: %s", exc)
        raise HTTPException(status_code=502, detail="Claude process error") from exc
    except ClaudeSDKError as exc:
        logger.error("Claude SDK error: %s", exc)
        raise HTTPException(status_code=500, detail="Claude SDK error") from exc


def get_suggestion(session_id: str, suggestion_id: str) -> dict | None:
    """Look up a suggestion by session and suggestion ID."""
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")
    return _sessions[session_id]["suggestions"].get(suggestion_id)


def accept_suggestion(session_id: str, suggestion_id: str) -> dict | None:
    """Record a suggestion acceptance and return the suggestion."""
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")
    session = _sessions[session_id]
    suggestion = session["suggestions"].get(suggestion_id)
    if suggestion is not None and suggestion_id not in session["accepted_suggestions"]:
        session["accepted_suggestions"].append(suggestion_id)
    return suggestion


def reject_suggestion(session_id: str, suggestion_id: str) -> dict | None:
    """Record a suggestion rejection and return the suggestion."""
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")
    session = _sessions[session_id]
    suggestion = session["suggestions"].get(suggestion_id)
    if suggestion is not None and suggestion_id not in session["rejected_suggestions"]:
        session["rejected_suggestions"].append(suggestion_id)
    return suggestion


async def _close_session(session_id: str):
    """Close a single session's client and remove it."""
    if session_id in _sessions:
        client = _sessions[session_id].get("client")
        if client is not None:
            try:
                await client.__aexit__(None, None, None)
            except Exception:
                logger.warning("Error closing session %s client", session_id)
        del _sessions[session_id]


async def cleanup_expired_sessions():
    """Remove sessions that have been inactive longer than SESSION_TTL."""
    cutoff = datetime.now(timezone.utc) - SESSION_TTL
    expired = [
        sid
        for sid, s in _sessions.items()
        if s.get("last_active", s.get("created_at", cutoff)) < cutoff
    ]
    for sid in expired:
        await _close_session(sid)


async def close_all_sessions():
    """Shutdown handler: close all active sessions."""
    session_ids = list(_sessions.keys())
    for sid in session_ids:
        await _close_session(sid)
