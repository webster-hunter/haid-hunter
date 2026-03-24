import json
import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.fixture
def mock_extraction():
    return {
        "skills": ["Python", "FastAPI"],
        "technologies": ["Docker", "AWS"],
        "experience_keywords": ["led team of 5"],
        "soft_skills": ["collaboration"],
    }


@pytest.fixture
def mock_metadata():
    return {
        "files": {
            "abc123": {
                "original_name": "resume.txt",
                "stored_name": "abc123_resume.txt",
                "mime_type": "text/plain",
                "tags": ["resume"],
            }
        },
        "tags": ["resume"],
    }


@pytest.mark.asyncio
async def test_analyze_returns_suggestions(mock_extraction, mock_metadata):
    mock_meta_svc = MagicMock()
    mock_meta_svc.read.return_value = mock_metadata
    mock_meta_svc.docs_dir = MagicMock()

    with (
        patch("backend.routers.extraction.get_metadata_service", return_value=mock_meta_svc),
        patch("backend.routers.extraction.read_document_contents", return_value="Resume text with Python"),
        patch("backend.routers.extraction.extract_from_documents", return_value=mock_extraction),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/extraction/analyze")
            assert resp.status_code == 200
            data = resp.json()
            assert data["skills"] == ["Python", "FastAPI"]
            assert data["technologies"] == ["Docker", "AWS"]


@pytest.mark.asyncio
async def test_accept_merges_into_profile(mock_extraction):
    existing_profile = {
        "skills": ["SQL"],
        "experience": [],
        "education": [],
        "certifications": [],
        "summary": "",
        "objectives": "",
    }
    mock_profile_svc = MagicMock()
    mock_profile_svc.get.return_value = existing_profile
    mock_profile_svc.put.return_value = None

    with (
        patch("backend.routers.extraction.get_profile_service", return_value=mock_profile_svc),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/extraction/accept",
                json=mock_extraction,
            )
            assert resp.status_code == 200
            # Verify put was called with merged profile
            call_args = mock_profile_svc.put.call_args[0][0]
            assert "SQL" in call_args["skills"]
            assert "Python" in call_args["skills"]
            assert "Docker" in call_args["skills"]


@pytest.mark.asyncio
async def test_accept_partial_suggestions():
    existing_profile = {
        "skills": ["Go"],
        "experience": [],
        "education": [],
        "certifications": [],
        "summary": "",
        "objectives": "",
    }
    mock_profile_svc = MagicMock()
    mock_profile_svc.get.return_value = existing_profile
    mock_profile_svc.put.return_value = None

    partial = {
        "skills": ["Rust"],
        "technologies": [],
        "experience_keywords": [],
        "soft_skills": [],
    }

    with patch("backend.routers.extraction.get_profile_service", return_value=mock_profile_svc):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/extraction/accept", json=partial)
            assert resp.status_code == 200
            call_args = mock_profile_svc.put.call_args[0][0]
            assert "Go" in call_args["skills"]
            assert "Rust" in call_args["skills"]
