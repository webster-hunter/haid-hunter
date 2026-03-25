from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from backend.config import DOCUMENTS_DIR, PROFILE_PATH
from backend.services.metadata import MetadataService
from backend.services.profile import ProfileService, VALID_SECTIONS
from backend.services import interview as interview_service
from backend.rate_limit import limiter

router = APIRouter(prefix="/api/interview", tags=["interview"])

_metadata_service: MetadataService | None = None
_profile_service: ProfileService | None = None
_sessions: dict | None = None


def get_metadata_service() -> MetadataService:
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = MetadataService(DOCUMENTS_DIR)
    return _metadata_service


def get_profile_service() -> ProfileService:
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService(PROFILE_PATH)
    return _profile_service


def _sync_sessions():
    """Keep router's _sessions reference in sync with the service's _sessions dict."""
    global _sessions
    if _sessions is not None:
        # Replace the service's sessions dict with the injected one for testing
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
    metadata = get_metadata_service().read()
    doc_contents = interview_service.read_document_contents(DOCUMENTS_DIR, metadata)
    session_id, message = interview_service.start_session(profile, doc_contents)
    return {"session_id": session_id, "message": message}


@router.post("/message")
@limiter.limit("20/minute")
async def send_message(request: Request, body: MessageRequest):
    _sync_sessions()
    try:
        result = interview_service.send_message(body.session_id, body.message)
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

    # Validate section
    if section not in VALID_SECTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid suggestion section: {section}")

    # Validate action
    if action not in ("add", "update", "remove"):
        raise HTTPException(status_code=400, detail=f"Invalid suggestion action: {action}")

    # Validate index bounds for update/remove on list sections
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

    # Record acceptance in session state so Claude is informed on the next turn
    session = interview_service._sessions[body.session_id]
    session["accepted_suggestions"].append(body.suggestion_id)

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

    # Record rejection in session state so Claude is informed on the next turn
    session = interview_service._sessions[body.session_id]
    session["rejected_suggestions"].append(body.suggestion_id)

    return {"status": "rejected", "suggestion_id": body.suggestion_id}
