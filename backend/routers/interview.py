from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import DOCUMENTS_DIR, PROFILE_PATH
from backend.services.metadata import MetadataService
from backend.services.profile import ProfileService
from backend.services import interview as interview_service

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
async def start_interview():
    _sync_sessions()
    profile = get_profile_service().get()
    metadata = get_metadata_service().read()
    doc_contents = interview_service.read_document_contents(DOCUMENTS_DIR, metadata)
    session_id, message = interview_service.start_session(profile, doc_contents)
    return {"session_id": session_id, "message": message}


@router.post("/message")
async def send_message(body: MessageRequest):
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
    section = suggestion["section"]
    action = suggestion["action"]
    target = suggestion.get("target", {})

    if action == "add" and isinstance(profile.get(section), list):
        profile[section].append(suggestion["proposed"])
    elif action == "update":
        if section in ("summary", "objectives"):
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
    return {"status": "accepted", "profile": profile}


@router.post("/reject")
async def reject_suggestion(body: SuggestionRequest):
    return {"status": "rejected"}
