import logging
from fastapi import APIRouter
from pydantic import BaseModel
from backend.config import DOCUMENTS_DIR, PROFILE_PATH
from backend.services.document_reader import read_document_contents
from backend.services.extraction import extract_from_documents, merge_suggestions
from backend.services.metadata import MetadataService
from backend.services.profile import ProfileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/extraction", tags=["extraction"])

_metadata_service: MetadataService | None = None
_profile_service: ProfileService | None = None


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


class AcceptSuggestionsRequest(BaseModel):
    skills: list[str] = []
    technologies: list[str] = []
    experience_keywords: list[str] = []
    soft_skills: list[str] = []


@router.post("/analyze")
async def analyze_documents():
    service = get_metadata_service()
    metadata = service.read()
    doc_contents = read_document_contents(service.docs_dir, metadata)
    logger.info("Running extraction on %d documents", len(metadata.get("files", {})))
    result = extract_from_documents(doc_contents)
    return result


@router.post("/accept")
async def accept_suggestions(body: AcceptSuggestionsRequest):
    profile_svc = get_profile_service()
    existing = profile_svc.get()
    merged = merge_suggestions(existing, body.model_dump())
    profile_svc.put(merged)
    logger.info("Accepted extraction suggestions into profile")
    return profile_svc.get()
