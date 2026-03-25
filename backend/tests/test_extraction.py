import json
from unittest.mock import patch, MagicMock
from backend.services.extraction import extract_from_documents, merge_suggestions


def _mock_claude_response(suggestions: dict) -> MagicMock:
    response = MagicMock()
    response.content = [MagicMock(text=json.dumps(suggestions))]
    return response


class TestExtractFromDocuments:
    def test_returns_structured_suggestions(self):
        fake_suggestions = {
            "skills": ["Python", "FastAPI", "React"],
            "technologies": ["PostgreSQL", "Docker"],
            "experience_keywords": ["led team of 5", "reduced latency by 40%"],
            "soft_skills": ["cross-functional collaboration"],
        }
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_claude_response(fake_suggestions)

        with patch("backend.services.extraction.get_claude_client", return_value=mock_client):
            result = extract_from_documents("Resume text here with Python and FastAPI")

        assert result["skills"] == ["Python", "FastAPI", "React"]
        assert result["technologies"] == ["PostgreSQL", "Docker"]
        assert result["experience_keywords"] == ["led team of 5", "reduced latency by 40%"]
        assert result["soft_skills"] == ["cross-functional collaboration"]

    def test_returns_empty_on_no_documents(self):
        result = extract_from_documents("No previewable documents found.")
        assert result == {
            "skills": [],
            "technologies": [],
            "experience_keywords": [],
            "soft_skills": [],
        }

    def test_handles_malformed_claude_response(self):
        mock_client = MagicMock()
        bad_response = MagicMock()
        bad_response.content = [MagicMock(text="not valid json at all")]
        mock_client.messages.create.return_value = bad_response

        with patch("backend.services.extraction.get_claude_client", return_value=mock_client):
            result = extract_from_documents("Some document text")

        assert "skills" in result
        assert isinstance(result["skills"], list)


class TestMergeSuggestions:
    def test_merges_new_skills_into_existing(self):
        existing_profile = {
            "skills": ["Python", "SQL"],
            "experience": [],
            "education": [],
            "certifications": [],
            "summary": "",
            "objectives": "",
        }
        suggestions = {
            "skills": ["Python", "FastAPI", "React"],
            "technologies": ["Docker"],
            "experience_keywords": ["led team of 5"],
            "soft_skills": ["collaboration"],
        }
        result = merge_suggestions(existing_profile, suggestions)
        # Python should not be duplicated
        assert "Python" in result["skills"]
        assert result["skills"].count("Python") == 1
        # New skills should be added
        assert "FastAPI" in result["skills"]
        assert "React" in result["skills"]
        assert "Docker" in result["skills"]
        assert "collaboration" in result["skills"]

    def test_preserves_existing_profile_fields(self):
        existing_profile = {
            "skills": ["Go"],
            "experience": [{"company": "Acme", "role": "Dev"}],
            "education": [{"institution": "MIT"}],
            "certifications": [],
            "summary": "Experienced dev",
            "objectives": "Lead role",
        }
        suggestions = {"skills": ["Rust"], "technologies": [], "experience_keywords": [], "soft_skills": []}
        result = merge_suggestions(existing_profile, suggestions)
        assert result["experience"] == [{"company": "Acme", "role": "Dev"}]
        assert result["summary"] == "Experienced dev"
        assert "Go" in result["skills"]
        assert "Rust" in result["skills"]

    def test_handles_empty_suggestions(self):
        existing = {"skills": ["Python"], "experience": [], "education": [], "certifications": [], "summary": "", "objectives": ""}
        suggestions = {"skills": [], "technologies": [], "experience_keywords": [], "soft_skills": []}
        result = merge_suggestions(existing, suggestions)
        assert result["skills"] == ["Python"]
