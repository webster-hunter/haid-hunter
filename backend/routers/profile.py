import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, field_validator
from backend.config import PROFILE_PATH
from backend.services.profile import ProfileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])


class ExperienceEntry(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: str | None = None
    highlights: list[str] = []


class EducationEntry(BaseModel):
    institution: str
    degree: str
    field: str | None = None
    year: str | None = None


class CertificationEntry(BaseModel):
    name: str
    issuer: str | None = None
    year: str | None = None


class ProfileRequest(BaseModel):
    summary: str = ""
    skills: list[str] = []
    experience: list[ExperienceEntry] = []
    education: list[EducationEntry] = []
    certifications: list[CertificationEntry] = []
    objectives: str = ""

    @field_validator("summary", "objectives")
    @classmethod
    def max_text_length(cls, v: str) -> str:
        if len(v) > 5000:
            raise ValueError("Max 5000 characters")
        return v

    @field_validator("skills")
    @classmethod
    def max_skills(cls, v: list[str]) -> list[str]:
        if len(v) > 100:
            raise ValueError("Max 100 skills")
        return v

    @field_validator("experience")
    @classmethod
    def max_experience(cls, v: list) -> list:
        if len(v) > 50:
            raise ValueError("Max 50 experience entries")
        return v

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
async def put_profile(body: ProfileRequest):
    logger.info("Profile replaced")
    get_service().put(body.model_dump())
    return get_service().get()


@router.patch("/{section}")
async def patch_section(section: str, request: Request):
    body = await request.json()
    try:
        result = get_service().patch(section, body)
        logger.info("Profile section updated: %s", section)
        return result
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid section: {section}")
