from backend.services.extraction import extract_from_documents, merge_suggestions


class TestExtractFromDocuments:
    def test_returns_skills_with_typed_objects(self):
        result = extract_from_documents(
            "Python developer with FastAPI experience. "
            "Used PostgreSQL and Docker in production."
        )
        assert "skills" in result
        names = [s["name"] for s in result["skills"]]
        assert "Python" in names
        assert "FastAPI" in names
        assert "PostgreSQL" in names
        assert "Docker" in names
        for s in result["skills"]:
            assert "name" in s
            assert "type" in s

    def test_returns_empty_on_no_documents(self):
        result = extract_from_documents("No previewable documents found.")
        assert result == {"skills": []}

    def test_returns_valid_structure_for_arbitrary_text(self):
        result = extract_from_documents("Some document text without any recognizable keywords")
        assert "skills" in result
        assert isinstance(result["skills"], list)


class TestMergeSuggestions:
    def test_merges_new_typed_skills_into_existing(self):
        existing_profile = {
            "skills": [
                {"name": "Python", "type": "Programming Languages"},
                {"name": "SQL", "type": "Databases"},
            ],
            "experience": [],
            "education": [],
            "certifications": [],
            "summary": "",
        }
        suggestions = {
            "skills": [
                {"name": "Python", "type": "Programming Languages"},
                {"name": "FastAPI", "type": "Backend"},
                {"name": "React", "type": "Frontend"},
            ],
        }
        result = merge_suggestions(existing_profile, suggestions)
        names = [s["name"] for s in result["skills"]]
        assert names.count("Python") == 1
        assert "FastAPI" in names
        assert "React" in names
        assert "SQL" in names

    def test_preserves_existing_profile_fields(self):
        existing_profile = {
            "skills": [{"name": "Go", "type": "Programming Languages"}],
            "experience": [{"company": "Acme", "role": "Dev"}],
            "education": [{"institution": "MIT"}],
            "certifications": [],
            "summary": "Experienced dev",
        }
        suggestions = {
            "skills": [{"name": "Rust", "type": "Programming Languages"}],
        }
        result = merge_suggestions(existing_profile, suggestions)
        assert result["experience"] == [{"company": "Acme", "role": "Dev"}]
        assert result["summary"] == "Experienced dev"
        names = [s["name"] for s in result["skills"]]
        assert "Go" in names
        assert "Rust" in names

    def test_handles_empty_suggestions(self):
        existing = {
            "skills": [{"name": "Python", "type": "Programming Languages"}],
            "experience": [], "education": [], "certifications": [], "summary": "",
        }
        suggestions = {"skills": []}
        result = merge_suggestions(existing, suggestions)
        assert len(result["skills"]) == 1
        assert result["skills"][0]["name"] == "Python"

    def test_deduplicates_case_insensitive(self):
        existing = {
            "skills": [{"name": "Python", "type": "Programming Languages"}],
            "experience": [], "education": [], "certifications": [], "summary": "",
        }
        suggestions = {
            "skills": [{"name": "python", "type": "Programming Languages"}],
        }
        result = merge_suggestions(existing, suggestions)
        names = [s["name"] for s in result["skills"]]
        assert len(names) == 1
