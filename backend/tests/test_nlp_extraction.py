"""
TDD tests for NLP-based extraction service.
These tests define the desired behavior BEFORE implementation.
"""

import pytest
from backend.services.nlp_extraction import (
    extract_skills,
    extract_technologies,
    extract_soft_skills,
    extract_from_documents,
)

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
    def test_finds_python_in_resume(self):
        result = extract_skills(RESUME_TEXT)
        assert "Python" in result

    def test_finds_react_in_resume(self):
        result = extract_skills(RESUME_TEXT)
        assert "React" in result

    def test_finds_fastapi_in_resume(self):
        result = extract_skills(RESUME_TEXT)
        assert "FastAPI" in result

    def test_finds_typescript_in_resume(self):
        result = extract_skills(RESUME_TEXT)
        assert "TypeScript" in result

    def test_finds_python_in_job_posting(self):
        result = extract_skills(JOB_POSTING_TEXT)
        assert "Python" in result

    def test_finds_django_in_job_posting(self):
        result = extract_skills(JOB_POSTING_TEXT)
        assert "Django" in result

    def test_returns_list(self):
        result = extract_skills(RESUME_TEXT)
        assert isinstance(result, list)

    def test_no_duplicates(self):
        text = "Python Python Python developer with Python experience"
        result = extract_skills(text)
        assert result.count("Python") == 1

    def test_empty_text_returns_empty_list(self):
        result = extract_skills("")
        assert result == []

    def test_does_not_include_technologies(self):
        """Skills should be languages/frameworks, not infrastructure."""
        result = extract_skills(RESUME_TEXT)
        # Docker and Kubernetes are technologies, not skills
        assert "Docker" not in result
        assert "Kubernetes" not in result


class TestExtractTechnologies:
    def test_finds_postgresql_in_resume(self):
        result = extract_technologies(RESUME_TEXT)
        assert "PostgreSQL" in result

    def test_finds_docker_in_resume(self):
        result = extract_technologies(RESUME_TEXT)
        assert "Docker" in result

    def test_finds_kubernetes_in_resume(self):
        result = extract_technologies(RESUME_TEXT)
        assert "Kubernetes" in result

    def test_finds_aws_in_resume(self):
        result = extract_technologies(RESUME_TEXT)
        assert "AWS" in result

    def test_finds_postgresql_in_job_posting(self):
        result = extract_technologies(JOB_POSTING_TEXT)
        assert "PostgreSQL" in result

    def test_finds_docker_in_job_posting(self):
        result = extract_technologies(JOB_POSTING_TEXT)
        assert "Docker" in result

    def test_returns_list(self):
        result = extract_technologies(RESUME_TEXT)
        assert isinstance(result, list)

    def test_no_duplicates(self):
        text = "Using Docker and Docker containers with Docker Compose"
        result = extract_technologies(text)
        assert result.count("Docker") == 1

    def test_empty_text_returns_empty_list(self):
        result = extract_technologies("")
        assert result == []

    def test_does_not_include_programming_languages(self):
        """Technologies should be infra/platforms, not programming languages."""
        result = extract_technologies(RESUME_TEXT)
        assert "Python" not in result
        assert "React" not in result


class TestExtractSoftSkills:
    def test_finds_communication_in_resume(self):
        result = extract_soft_skills(RESUME_TEXT)
        assert "communication" in [s.lower() for s in result]

    def test_finds_leadership_in_resume(self):
        result = extract_soft_skills(RESUME_TEXT)
        assert "leadership" in [s.lower() for s in result]

    def test_finds_teamwork_in_job_posting(self):
        result = extract_soft_skills(JOB_POSTING_TEXT)
        assert any("teamwork" in s.lower() or "team" in s.lower() for s in result)

    def test_returns_list(self):
        result = extract_soft_skills(RESUME_TEXT)
        assert isinstance(result, list)

    def test_no_duplicates(self):
        text = "communication skills, strong communication, excellent communication"
        result = extract_soft_skills(text)
        lower = [s.lower() for s in result]
        assert lower.count("communication") == 1

    def test_empty_text_returns_empty_list(self):
        result = extract_soft_skills("")
        assert result == []



class TestExtractFromDocuments:
    def test_returns_correct_structure(self):
        result = extract_from_documents(RESUME_TEXT)
        assert "skills" in result
        assert "technologies" in result
        assert "soft_skills" in result

    def test_all_values_are_lists(self):
        result = extract_from_documents(RESUME_TEXT)
        assert isinstance(result["skills"], list)
        assert isinstance(result["technologies"], list)
        assert isinstance(result["soft_skills"], list)

    def test_returns_empty_result_for_no_documents_sentinel(self):
        result = extract_from_documents("No previewable documents found.")
        assert result == {
            "skills": [],
            "technologies": [],
            "soft_skills": [],
        }

    def test_finds_skills_in_resume(self):
        result = extract_from_documents(RESUME_TEXT)
        assert "Python" in result["skills"]

    def test_finds_technologies_in_resume(self):
        result = extract_from_documents(RESUME_TEXT)
        assert "Docker" in result["technologies"]

    def test_finds_soft_skills_in_resume(self):
        result = extract_from_documents(RESUME_TEXT)
        assert any("communication" in s.lower() for s in result["soft_skills"])

    def test_works_on_job_posting(self):
        result = extract_from_documents(JOB_POSTING_TEXT)
        assert "Python" in result["skills"]
        assert "Docker" in result["technologies"]

    def test_does_not_call_external_api(self):
        """
        NLP extraction must work completely offline — no HTTP calls.
        This is the core motivation for switching from Claude.
        """
        import socket
        original_getaddrinfo = socket.getaddrinfo

        def block_network(*args, **kwargs):
            raise OSError("Network access blocked — NLP extraction must be offline")

        socket.getaddrinfo = block_network
        try:
            result = extract_from_documents(RESUME_TEXT)
            assert isinstance(result, dict)
        finally:
            socket.getaddrinfo = original_getaddrinfo
