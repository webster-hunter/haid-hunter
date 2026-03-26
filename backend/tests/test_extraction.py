import json
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from backend.services.extraction import extract_from_documents, merge_suggestions


def _make_sdk_messages(text: str):
    """Simulate SDK query() yielding messages with a result."""
    async def mock_query(*args, **kwargs):
        msg = MagicMock()
        msg.result = text
        yield msg
    return mock_query


class TestExtractFromDocuments:
    @pytest.mark.asyncio
    async def test_returns_structured_suggestions(self):
        fake_result = json.dumps({
            "skills": ["Python", "FastAPI"],
            "technologies": ["Docker"],
            "experience_keywords": ["led team of 5"],
            "soft_skills": ["collaboration"],
        })
        with patch("backend.services.extraction.query", side_effect=_make_sdk_messages(fake_result)):
            result = await extract_from_documents("/fake/docs/dir")
        assert result["skills"] == ["Python", "FastAPI"]
        assert result["technologies"] == ["Docker"]

    @pytest.mark.asyncio
    async def test_handles_malformed_response(self):
        with patch("backend.services.extraction.query", side_effect=_make_sdk_messages("not json")):
            result = await extract_from_documents("/fake/dir")
        assert result == {"skills": [], "technologies": [], "experience_keywords": [], "soft_skills": []}


class TestMergeSuggestions:
    def test_merges_new_skills_into_existing(self):
        existing = {"skills": ["Python", "SQL"], "experience": [], "education": [], "certifications": [], "summary": "", "objectives": []}
        suggestions = {"skills": ["Python", "FastAPI"], "technologies": ["Docker"], "experience_keywords": [], "soft_skills": ["collaboration"]}
        result = merge_suggestions(existing, suggestions)
        assert result["skills"].count("Python") == 1
        assert "FastAPI" in result["skills"]
        assert "Docker" in result["skills"]

    def test_handles_empty_suggestions(self):
        existing = {"skills": ["Python"], "experience": [], "education": [], "certifications": [], "summary": "", "objectives": []}
        suggestions = {"skills": [], "technologies": [], "experience_keywords": [], "soft_skills": []}
        result = merge_suggestions(existing, suggestions)
        assert result["skills"] == ["Python"]
