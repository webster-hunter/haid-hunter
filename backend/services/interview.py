import uuid
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from backend.config import get_api_key
from backend.services.document_reader import read_document_contents

SESSION_TTL = timedelta(minutes=30)
MAX_SESSIONS = 20

_sessions: dict = {}


def cleanup_expired_sessions():
    """Remove sessions that have been inactive longer than SESSION_TTL."""
    cutoff = datetime.now(timezone.utc) - SESSION_TTL
    expired = [sid for sid, s in _sessions.items() if s.get("last_active", s.get("created_at", cutoff)) < cutoff]
    for sid in expired:
        del _sessions[sid]


def get_claude_client():
    import anthropic
    return anthropic.Anthropic(api_key=get_api_key())


SYSTEM_PROMPT = """You are a career profile interview assistant for hAId-hunter, a job application tool.

Your job is to help the user build a comprehensive candidate profile by:
1. Reviewing their uploaded documents (provided below)
2. Asking targeted follow-up questions to fill gaps and add detail
3. Proposing structured updates to their profile

When you want to suggest a profile update, include a JSON block in your response like:
```suggestion
{
  "suggestion_id": "sug_<random>",
  "section": "experience|skills|education|certifications|activities|summary",
  "action": "add|update|remove",
  "target": { ... },
  "original": "...",
  "proposed": "..."
}
```

Focus on:
- Quantifiable accomplishments (numbers, percentages, team sizes)
- Technologies and tools used
- Impact and scope of work
- Leadership and collaboration examples
- Details that differentiate them from other candidates

Be conversational but focused. One question at a time. Base your questions on what you see in their documents and current profile."""


def start_session(profile: dict, doc_contents: str) -> tuple[str, str]:
    cleanup_expired_sessions()
    if len(_sessions) >= MAX_SESSIONS:
        # Evict the oldest session
        oldest_sid = min(_sessions, key=lambda s: _sessions[s].get("last_active", datetime.min.replace(tzinfo=timezone.utc)))
        del _sessions[oldest_sid]

    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    messages = []
    system = f"{SYSTEM_PROMPT}\n\n## Current Profile\n```json\n{json.dumps(profile, indent=2)}\n```\n\n## Document Contents\n{doc_contents}"

    client = get_claude_client()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": "Please review my documents and profile, then start asking me questions to help build out my candidate profile."}],
    )

    assistant_msg = response.content[0].text
    messages.append({"role": "user", "content": "Please review my documents and profile, then start asking me questions to help build out my candidate profile."})
    messages.append({"role": "assistant", "content": assistant_msg})

    _sessions[session_id] = {
        "system": system,
        "messages": messages,
        "suggestions": {},
        "accepted_suggestions": [],
        "rejected_suggestions": [],
        "created_at": now,
        "last_active": now,
    }

    return session_id, assistant_msg


def send_message(session_id: str, user_message: str) -> dict:
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")

    session = _sessions[session_id]
    session["last_active"] = datetime.now(timezone.utc)
    session["messages"].append({"role": "user", "content": user_message})

    client = get_claude_client()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=session["system"],
        messages=session["messages"],
    )

    assistant_msg = response.content[0].text
    session["messages"].append({"role": "assistant", "content": assistant_msg})

    # Parse suggestion if present
    suggestion = None
    if "```suggestion" in assistant_msg:
        try:
            start = assistant_msg.index("```suggestion") + len("```suggestion")
            end = assistant_msg.index("```", start)
            suggestion = json.loads(assistant_msg[start:end].strip())
            session["suggestions"][suggestion["suggestion_id"]] = suggestion
        except (ValueError, json.JSONDecodeError, KeyError):
            pass

    return {"message": assistant_msg, "suggestion": suggestion}


def get_suggestion(session_id: str, suggestion_id: str) -> dict | None:
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")
    return _sessions[session_id]["suggestions"].get(suggestion_id)
