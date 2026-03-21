from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import DOCUMENTS_DIR
from backend.services.metadata import MetadataService

router = APIRouter(prefix="/api/tags", tags=["tags"])

_metadata_service: MetadataService | None = None


def get_service() -> MetadataService:
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = MetadataService(DOCUMENTS_DIR)
    return _metadata_service


class CreateTagRequest(BaseModel):
    name: str


@router.get("")
async def list_tags():
    return get_service().get_tags()


@router.post("")
async def create_tag(body: CreateTagRequest):
    get_service().add_tag(body.name)
    return {"status": "created", "tag": body.name}


@router.delete("/{tag}")
async def delete_tag(tag: str):
    get_service().delete_tag(tag)
    return {"status": "deleted", "tag": tag}
