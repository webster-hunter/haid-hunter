import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, TypeAdapter, ValidationError, field_validator
from backend.config import PROFILE_PATH
from backend.services.profile import ProfileService
from backend.services.skill_definitions import SKILL_TYPES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])


class TypedSkillModel(BaseModel):
    name: str
    type: str

    @field_validator("type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        if v not in SKILL_TYPES:
            raise ValueError(f"Invalid skill type: {v}")
        return v


class ExperienceEntry(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: str | None = None
    accomplishments: list[str] = []


class ActivityEntry(BaseModel):
    name: str
    category: str = ""
    url: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    details: list[str] = []


class EducationEntry(BaseModel):
    institution: str
    degree: str
    field: str | None = None
    start_date: str = ""
    end_date: str | None = None
    details: list[str] = []


class CertificationEntry(BaseModel):
    name: str
    issuer: str
    date: str


class ProfileRequest(BaseModel):
    summary: str = ""
    skills: list[TypedSkillModel] = []
    experience: list[ExperienceEntry] = []
    activities: list[ActivityEntry] = []
    education: list[EducationEntry] = []
    certifications: list[CertificationEntry] = []

    @field_validator("summary")
    @classmethod
    def max_text_length(cls, v: str) -> str:
        if len(v) > 5000:
            raise ValueError("Max 5000 characters")
        return v

    @field_validator("skills")
    @classmethod
    def max_skills(cls, v: list) -> list:
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


_SECTION_VALIDATORS = {
    "summary": TypeAdapter(str),
    "skills": TypeAdapter(list[TypedSkillModel]),
    "experience": TypeAdapter(list[ExperienceEntry]),
    "activities": TypeAdapter(list[ActivityEntry]),
    "education": TypeAdapter(list[EducationEntry]),
    "certifications": TypeAdapter(list[CertificationEntry]),
}


@router.patch("/{section}")
async def patch_section(section: str, request: Request):
    if section not in _SECTION_VALIDATORS:
        raise HTTPException(status_code=400, detail=f"Invalid section: {section}")
    body = await request.json()
    validator = _SECTION_VALIDATORS[section]
    try:
        validated = validator.validate_python(body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    # Convert Pydantic models back to dicts for JSON storage
    if hasattr(validated, '__iter__') and not isinstance(validated, str):
        data = [item.model_dump() if isinstance(item, BaseModel) else item for item in validated]
    else:
        data = validated
    try:
        result = get_service().patch(section, data)
        logger.info("Profile section updated: %s", section)
        return result
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid section: {section}")


skills_router = APIRouter(prefix="/api/skills", tags=["skills"])


@skills_router.get("/types")
async def get_skill_types():
    return SKILL_TYPES
