import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport
from backend.main import app


MOCK_ANALYSIS = {
    "key_requirements": ["5+ years Python", "FastAPI experience"],
    "emphasis_areas": ["backend development", "API design"],
    "keywords": ["Python", "REST", "microservices"],
}

MOCK_PROFILE = {
    "summary": "Software engineer",
    "skills": ["Python"],
    "experience": [],
    "education": [],
    "certifications": [],
    "objectives": [],
}


@pytest.mark.asyncio
async def test_analyze_posting_endpoint():
    mock_profile_svc = MagicMock()
    mock_profile_svc.get.return_value = MOCK_PROFILE

    with (
        patch("backend.routers.posting.get_profile_service", return_value=mock_profile_svc),
        patch(
            "backend.routers.posting.analyze_posting",
            new_callable=AsyncMock,
            return_value=MOCK_ANALYSIS,
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/posting/analyze",
                json={"url": "https://example.com/job/123"},
            )
    assert resp.status_code == 200
    data = resp.json()
    assert data["key_requirements"] == ["5+ years Python", "FastAPI experience"]
    assert data["emphasis_areas"] == ["backend development", "API design"]
    assert data["keywords"] == ["Python", "REST", "microservices"]


@pytest.mark.asyncio
async def test_analyze_posting_missing_url():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/posting/analyze",
            json={},
        )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_analyze_posting_passes_profile_to_service():
    mock_profile_svc = MagicMock()
    mock_profile_svc.get.return_value = MOCK_PROFILE
    mock_analyze = AsyncMock(return_value=MOCK_ANALYSIS)

    with (
        patch("backend.routers.posting.get_profile_service", return_value=mock_profile_svc),
        patch("backend.routers.posting.analyze_posting", mock_analyze),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.post(
                "/api/posting/analyze",
                json={"url": "https://example.com/job/456"},
            )

    mock_analyze.assert_called_once_with("https://example.com/job/456", MOCK_PROFILE)
