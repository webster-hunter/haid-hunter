import logging
from fastapi import APIRouter, Request
from pydantic import BaseModel, field_validator
from backend.config import PROFILE_PATH
from backend.rate_limit import limiter
from backend.services.posting import analyze_posting
from backend.services.profile import ProfileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/posting", tags=["posting"])

_profile_service: ProfileService | None = None


def get_profile_service() -> ProfileService:
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService(PROFILE_PATH)
    return _profile_service


class AnalyzeRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def url_must_be_http(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


@router.post("/analyze")
@limiter.limit("5/minute")
async def analyze(request: Request, body: AnalyzeRequest):
    logger.info("Analyzing job posting: %s", body.url)
    profile = get_profile_service().get()
    result = await analyze_posting(body.url, profile)
    return result
