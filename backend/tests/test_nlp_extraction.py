"""
Tests for NLP-based extraction service with typed skill output.
"""

import pytest
from backend.services.nlp_extraction import extract_skills, extract_from_documents

RESUME_TEXT = """
Senior Software Engineer with 8 years of experience building scalable web applications.

Technical Skills: Python, FastAPI, React, TypeScript, Node.js, GraphQL

Led a cross-functional team of 5 engineers to deliver a microservices migration, reducing
system latency by 40% and cutting infrastructure costs by $200K annually.

Technologies: PostgreSQL, Redis, Docker, Kubernetes, AWS, Terraform

Soft Skills: Strong communication and leadership skills. Proven ability to mentor junior
developers and collaborate across teams. Detail-oriented with excellent problem-solving ability.

Certifications: AWS Solutions Architect, Certified Kubernetes Administrator
"""

JOB_POSTING_TEXT = """
We are looking for a Senior Python Developer to join our growing team.

Requirements:
- 5+ years of experience with Python and Django
- Proficiency in SQL and NoSQL databases (PostgreSQL, MongoDB)
- Experience with Docker and CI/CD pipelines (GitHub Actions, Jenkins)
- Strong understanding of REST APIs and microservices architecture
- Excellent communication and teamwork skills
- Demonstrated ability to lead technical projects
"""


class TestExtractSkills:
    def test_returns_list_of_typed_objects(self):
        result = extract_skills(RESUME_TEXT)
        assert isinstance(result, list)
        for item in result:
            assert "name" in item
            assert "type" in item

    def test_finds_python_with_correct_type(self):
        result = extract_skills(RESUME_TEXT)
        names = [s["name"] for s in result]
        assert "Python" in names
        python_entry = next(s for s in result if s["name"] == "Python")
        assert python_entry["type"] == "Programming Languages"

    def test_finds_react_with_correct_type(self):
        result = extract_skills(RESUME_TEXT)
        names = [s["name"] for s in result]
        assert "React" in names
        react_entry = next(s for s in result if s["name"] == "React")
        assert react_entry["type"] == "Frontend"

    def test_finds_docker_with_correct_type(self):
        result = extract_skills(RESUME_TEXT)
        names = [s["name"] for s in result]
        assert "Docker" in names
        docker_entry = next(s for s in result if s["name"] == "Docker")
        assert docker_entry["type"] == "DevOps & Infrastructure"

    def test_finds_communication(self):
        result = extract_skills(RESUME_TEXT)
        names = [s["name"].lower() for s in result]
        assert "communication" in names

    def test_finds_postgresql(self):
        result = extract_skills(RESUME_TEXT)
        names = [s["name"] for s in result]
        assert "PostgreSQL" in names

    def test_no_duplicates(self):
        text = "Python Python Python developer with Python experience"
        result = extract_skills(text)
        names = [s["name"] for s in result]
        assert names.count("Python") == 1

    def test_empty_text_returns_empty_list(self):
        result = extract_skills("")
        assert result == []

    def test_finds_skills_in_job_posting(self):
        result = extract_skills(JOB_POSTING_TEXT)
        names = [s["name"] for s in result]
        assert "Python" in names
        assert "Django" in names
        assert "Docker" in names


class TestExtractFromDocuments:
    def test_returns_skills_key_with_typed_objects(self):
        result = extract_from_documents(RESUME_TEXT)
        assert "skills" in result
        assert isinstance(result["skills"], list)
        for item in result["skills"]:
            assert "name" in item
            assert "type" in item

    def test_no_technologies_or_soft_skills_keys(self):
        result = extract_from_documents(RESUME_TEXT)
        assert "technologies" not in result
        assert "soft_skills" not in result

    def test_returns_empty_for_no_documents_sentinel(self):
        result = extract_from_documents("No previewable documents found.")
        assert result == {"skills": []}

    def test_finds_skills_across_all_types(self):
        result = extract_from_documents(RESUME_TEXT)
        types_found = {s["type"] for s in result["skills"]}
        assert "Programming Languages" in types_found
        assert "DevOps & Infrastructure" in types_found

    def test_does_not_call_external_api(self):
        import socket
        original_getaddrinfo = socket.getaddrinfo

        def block_network(*args, **kwargs):
            raise OSError("Network access blocked")

        socket.getaddrinfo = block_network
        try:
            result = extract_from_documents(RESUME_TEXT)
            assert isinstance(result, dict)
        finally:
            socket.getaddrinfo = original_getaddrinfo
