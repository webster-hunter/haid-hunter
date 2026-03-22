import uuid
import json
from pathlib import Path
from backend.config import ANTHROPIC_API_KEY

_sessions: dict = {}


def get_claude_client():
    import anthropic
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


SYSTEM_PROMPT = """You are a career profile interview assistant for hAId-hunter, a job application tool.

Your job is to help the user build a comprehensive candidate profile by:
1. Reviewing their uploaded documents (provided below)
2. Asking targeted follow-up questions to fill gaps and add detail
3. Proposing structured updates to their profile

When you want to suggest a profile update, include a JSON block in your response like:
```suggestion
{
  "suggestion_id": "sug_<random>",
  "section": "experience|skills|education|certifications|summary|objectives",
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


def read_document_contents(docs_dir: Path, metadata: dict) -> str:
    contents = []
    for file_id, meta in metadata.get("files", {}).items():
        mime = meta.get("mime_type", "")
        if mime in ("text/plain", "text/markdown", "text/csv"):
            file_path = docs_dir / meta["stored_name"]
            if file_path.exists():
                text = file_path.read_text(errors="ignore")
                contents.append(f"--- {meta['original_name']} ---\n{text[:5000]}")
        elif mime == "application/pdf":
            file_path = docs_dir / meta["stored_name"]
            if file_path.exists():
                try:
                    import pdfplumber
                    with pdfplumber.open(file_path) as pdf:
                        pages_text = []
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                pages_text.append(page_text)
                        extracted = "\n".join(pages_text)[:5000]
                    contents.append(f"--- {meta['original_name']} ---\n{extracted}")
                except ImportError:
                    contents.append(
                        f"--- {meta['original_name']} ---\n"
                        f"[PDF file - text extraction not available]"
                    )
    return "\n\n".join(contents) if contents else "No previewable documents found."


def start_session(profile: dict, doc_contents: str) -> tuple[str, str]:
    session_id = str(uuid.uuid4())

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
    }

    return session_id, assistant_msg


def send_message(session_id: str, user_message: str) -> dict:
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")

    session = _sessions[session_id]
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
