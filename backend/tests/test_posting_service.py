import json
from unittest.mock import patch, MagicMock
import pytest
from fastapi import HTTPException
from backend.services.posting import analyze_posting
from claude_agent_sdk import CLINotFoundError, CLIConnectionError, ProcessError, ClaudeSDKError


def _make_sdk_messages(text: str):
    """Simulate SDK query() yielding messages with a result."""
    async def mock_query(*args, **kwargs):
        msg = MagicMock()
        msg.result = text
        yield msg
    return mock_query


FAKE_PROFILE = {
    "summary": "Software engineer with 5 years experience",
    "skills": ["Python", "FastAPI"],
    "experience": [],
    "education": [],
    "certifications": [],
}


class TestAnalyzePosting:
    @pytest.mark.asyncio
    async def test_analyze_posting_returns_structured_data(self):
        fake_result = json.dumps({
            "key_requirements": ["5+ years Python", "FastAPI experience"],
            "emphasis_areas": ["backend development", "API design"],
            "keywords": ["Python", "REST", "microservices"],
        })
        with patch("backend.services.posting.query", side_effect=_make_sdk_messages(fake_result)):
            result = await analyze_posting("https://example.com/job/123", FAKE_PROFILE)
        assert result["key_requirements"] == ["5+ years Python", "FastAPI experience"]
        assert result["emphasis_areas"] == ["backend development", "API design"]
        assert result["keywords"] == ["Python", "REST", "microservices"]

    @pytest.mark.asyncio
    async def test_analyze_posting_handles_malformed_response(self):
        with patch("backend.services.posting.query", side_effect=_make_sdk_messages("not json at all")):
            result = await analyze_posting("https://example.com/job/123", FAKE_PROFILE)
        assert result == {"key_requirements": [], "emphasis_areas": [], "keywords": []}

    @pytest.mark.asyncio
    async def test_analyze_posting_handles_markdown_fenced_json(self):
        inner = json.dumps({
            "key_requirements": ["TypeScript"],
            "emphasis_areas": ["frontend"],
            "keywords": ["React"],
        })
        fenced = f"```json\n{inner}\n```"
        with patch("backend.services.posting.query", side_effect=_make_sdk_messages(fenced)):
            result = await analyze_posting("https://example.com/job/456", FAKE_PROFILE)
        assert result["keywords"] == ["React"]

    @pytest.mark.asyncio
    async def test_analyze_posting_raises_503_on_cli_not_found(self):
        async def raise_cli_not_found(*args, **kwargs):
            raise CLINotFoundError("not found")
            yield  # make it a generator

        with patch("backend.services.posting.query", side_effect=raise_cli_not_found):
            with pytest.raises(HTTPException) as exc_info:
                await analyze_posting("https://example.com/job/123", FAKE_PROFILE)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_analyze_posting_raises_503_on_cli_connection_error(self):
        async def raise_conn_error(*args, **kwargs):
            raise CLIConnectionError("connection failed")
            yield

        with patch("backend.services.posting.query", side_effect=raise_conn_error):
            with pytest.raises(HTTPException) as exc_info:
                await analyze_posting("https://example.com/job/123", FAKE_PROFILE)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_analyze_posting_raises_502_on_process_error(self):
        async def raise_process_error(*args, **kwargs):
            raise ProcessError("process failed")
            yield

        with patch("backend.services.posting.query", side_effect=raise_process_error):
            with pytest.raises(HTTPException) as exc_info:
                await analyze_posting("https://example.com/job/123", FAKE_PROFILE)
        assert exc_info.value.status_code == 502

    @pytest.mark.asyncio
    async def test_analyze_posting_raises_500_on_sdk_error(self):
        async def raise_sdk_error(*args, **kwargs):
            raise ClaudeSDKError("sdk error")
            yield

        with patch("backend.services.posting.query", side_effect=raise_sdk_error):
            with pytest.raises(HTTPException) as exc_info:
                await analyze_posting("https://example.com/job/123", FAKE_PROFILE)
        assert exc_info.value.status_code == 500
