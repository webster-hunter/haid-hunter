from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.config import DOCUMENTS_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE
from backend.services.metadata import MetadataService
from pathlib import Path

router = APIRouter(prefix="/api/documents", tags=["documents"])

_metadata_service: MetadataService | None = None


def get_service() -> MetadataService:
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = MetadataService(DOCUMENTS_DIR)
    return _metadata_service


class UpdateDocumentRequest(BaseModel):
    display_name: str | None = None
    tags: list[str] | None = None


@router.get("")
async def list_documents(tag: str | None = None, search: str | None = None):
    service = get_service()
    data = service.read()
    files = []
    for file_id, meta in data["files"].items():
        if tag and tag not in meta["tags"]:
            continue
        if search and search.lower() not in meta["display_name"].lower():
            continue
        files.append({"id": file_id, **meta})
    return files


@router.get("/{file_id}/content")
async def get_document_content(file_id: str):
    service = get_service()
    try:
        meta = service.get_file(file_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")
    file_path = service.docs_dir / meta["stored_name"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(
        file_path,
        media_type=meta["mime_type"],
        filename=meta["original_name"],
    )


@router.get("/{file_id}")
async def get_document(file_id: str):
    service = get_service()
    try:
        meta = service.get_file(file_id)
        return {"id": file_id, **meta}
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")


@router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...), tags: str | None = None):
    service = get_service()
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    results = []

    for file in files:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

        content = await file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large: {file.filename}")

        result = service.add_file(file.filename or "unnamed", content, tags=tag_list)
        results.append(result)

    return results


@router.put("/{file_id}")
async def update_document(file_id: str, body: UpdateDocumentRequest):
    service = get_service()
    try:
        updated = service.update_file(file_id, display_name=body.display_name, tags=body.tags)
        return {"id": file_id, **updated}
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")


@router.delete("/{file_id}")
async def delete_document(file_id: str):
    service = get_service()
    try:
        service.delete_file(file_id)
        return {"status": "deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")


@router.post("/sync")
async def sync_documents():
    service = get_service()
    return service.sync()
