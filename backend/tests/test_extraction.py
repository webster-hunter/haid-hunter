from backend.services.extraction import extract_from_documents, merge_suggestions


class TestExtractFromDocuments:
    def test_returns_structured_suggestions(self):
        result = extract_from_documents(
            "Python developer with FastAPI experience. "
            "Used PostgreSQL and Docker in production."
        )
        assert "Python" in result["skills"]
        assert "FastAPI" in result["skills"]
        assert "PostgreSQL" in result["technologies"]
        assert "Docker" in result["technologies"]
        assert isinstance(result["soft_skills"], list)

    def test_returns_empty_on_no_documents(self):
        result = extract_from_documents("No previewable documents found.")
        assert result == {
            "skills": [],
            "technologies": [],
            "soft_skills": [],
        }

    def test_returns_valid_structure_for_arbitrary_text(self):
        result = extract_from_documents("Some document text without any recognizable keywords")
        assert "skills" in result
        assert "technologies" in result
        assert "soft_skills" in result
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
        suggestions = {"skills": ["Rust"], "technologies": [], "soft_skills": []}
        result = merge_suggestions(existing_profile, suggestions)
        assert result["experience"] == [{"company": "Acme", "role": "Dev"}]
        assert result["summary"] == "Experienced dev"
        assert "Go" in result["skills"]
        assert "Rust" in result["skills"]

    def test_handles_empty_suggestions(self):
        existing = {"skills": ["Python"], "experience": [], "education": [], "certifications": [], "summary": "", "objectives": ""}
        suggestions = {"skills": [], "technologies": [], "soft_skills": []}
        result = merge_suggestions(existing, suggestions)
        assert result["skills"] == ["Python"]
