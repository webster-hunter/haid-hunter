from fastapi import APIRouter, HTTPException, Request
from backend.config import PROFILE_PATH
from backend.services.profile import ProfileService

router = APIRouter(prefix="/api/profile", tags=["profile"])

_profile_service: ProfileService | None = None


def get_service() -> ProfileService:
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService(PROFILE_PATH)
    return _profile_service


@router.get("")
async def get_profile():
    return get_service().get()


@router.put("")
async def put_profile(request: Request):
    body = await request.json()
    get_service().put(body)
    return get_service().get()


@router.patch("/{section}")
async def patch_section(section: str, request: Request):
    body = await request.json()
    try:
        return get_service().patch(section, body)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid section: {section}")
