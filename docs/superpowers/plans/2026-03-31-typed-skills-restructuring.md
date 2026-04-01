# Typed Skills Restructuring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the three flat keyword sets with a single unified dictionary where every skill has a name and type, and use the type to group skills in both the extraction panel and profile page.

**Architecture:** A new `skill_definitions.py` file holds the master `SKILLS` dict (name -> type) and ordered `SKILL_TYPES` list. The extraction service imports from it and builds one PhraseMatcher. The API, profile storage, and frontend all speak in `{name, type}` objects. Profile migration is transparent on-read.

**Tech Stack:** Python/FastAPI (backend), SpaCy (NLP), React/TypeScript (frontend), Vitest (frontend tests), pytest (backend tests)

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `backend/services/skill_definitions.py` | Create | Master `SKILLS` dict + `SKILL_TYPES` list (data only) |
| `backend/services/nlp_extraction.py` | Modify | Delete three keyword sets, import from skill_definitions, single matcher, return typed objects |
| `backend/services/extraction.py` | Modify | Update `merge_suggestions` for typed skills |
| `backend/routers/extraction.py` | Modify | Update request/response models for typed skills |
| `backend/routers/profile.py` | Modify | Update `ProfileRequest.skills` validation, add `/api/skills/types` endpoint |
| `backend/services/profile.py` | Modify | Add on-read migration for untyped skills |
| `src/api/extraction.ts` | Modify | Update types to `TypedSkill`, flatten `SelectionState` |
| `src/api/profile.ts` | Modify | Update `Profile.skills` to `TypedSkill[]`, add `fetchSkillTypes` |
| `src/components/documents/ExtractionResultsPanel.tsx` | Modify | Group by type dynamically, simplify onToggle |
| `src/components/documents/DocumentManager.tsx` | Modify | Flatten selection state, remove CATEGORIES |
| `src/components/profile/SkillChips.tsx` | Modify | Group by type with headings |
| `src/components/profile/SectionEditor.tsx` | Modify | Skills editor with type dropdown |
| `backend/tests/test_nlp_extraction.py` | Modify | Rewrite for single `extract_skills` returning typed objects |
| `backend/tests/test_extraction.py` | Modify | Update for typed merge_suggestions |
| `backend/tests/test_extraction_api.py` | Modify | Update fixtures and assertions for typed format |
| `src/__tests__/documents/ExtractionResultsPanel.test.tsx` | Modify | Update for typed skills, flat selection |
| `src/__tests__/documents/DocumentManager.test.tsx` | Modify | Update mock data and assertions |

---

### Task 1: Create skill_definitions.py with master dict

**Files:**
- Create: `backend/services/skill_definitions.py`
- Test: `backend/tests/test_skill_definitions.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_skill_definitions.py`:

```python
"""Tests for the master skill definitions data."""

from backend.services.skill_definitions import SKILLS, SKILL_TYPES


class TestSkillTypes:
    def test_has_15_types(self):
        assert len(SKILL_TYPES) == 15

    def test_types_are_ordered(self):
        assert SKILL_TYPES[0] == "Programming Languages"
        assert SKILL_TYPES[1] == "Frontend"
        assert SKILL_TYPES[2] == "Backend"
        assert SKILL_TYPES[-1] == "Problem Solving & Process"

    def test_all_types_are_strings(self):
        for t in SKILL_TYPES:
            assert isinstance(t, str)


class TestSkillsDict:
    def test_is_dict(self):
        assert isinstance(SKILLS, dict)

    def test_not_empty(self):
        assert len(SKILLS) > 0

    def test_values_are_valid_types(self):
        for name, skill_type in SKILLS.items():
            assert skill_type in SKILL_TYPES, f"{name!r} has invalid type {skill_type!r}"

    def test_contains_representative_skills(self):
        assert SKILLS["Python"] == "Programming Languages"
        assert SKILLS["React"] == "Frontend"
        assert SKILLS["FastAPI"] == "Backend"
        assert SKILLS["Docker"] == "DevOps & Infrastructure"
        assert SKILLS["PostgreSQL"] == "Databases"
        assert SKILLS["AWS"] == "Cloud Services"
        assert SKILLS["communication"] == "Interpersonal"

    def test_no_duplicate_names(self):
        # Dict enforces uniqueness by construction, but verify count
        assert len(SKILLS) == len(set(SKILLS.keys()))

    def test_all_keys_are_strings(self):
        for k in SKILLS:
            assert isinstance(k, str)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/test_skill_definitions.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'backend.services.skill_definitions'`

- [ ] **Step 3: Write the implementation**

Create `backend/services/skill_definitions.py`. This file contains only data -- no logic.

Migrate all entries from the three keyword sets in `nlp_extraction.py` into a single `SKILLS` dict. Each skill maps to one of 15 types. Use the comment headers in the existing lists to determine the type. Apply the consolidation mapping from the spec:

| Consolidated Type | Absorbs these comment-header categories |
|---|---|
| Programming Languages | Programming Languages |
| Frontend | Frontend Frameworks / Libraries, Frontend Styling |
| Backend | Backend Frameworks, API Standards and Protocols |
| Mobile | Mobile Development |
| Data & ML | Data Science / Analytics, Machine Learning / AI, Data Engineering, Analytics / BI, AI / ML Platforms |
| Databases | Databases -- Concepts, Relational Databases, NoSQL Databases, Data Warehouses / OLAP |
| Cloud Services | Cloud Providers, AWS Services, Azure Services, GCP Services, Cloud Architecture -- Strategies & Patterns |
| DevOps & Infrastructure | DevOps / Development Practices, CI/CD Platforms, Containers and Orchestration, Infrastructure as Code, Monitoring / Logging / Observability, Service Mesh / API Gateway / Networking, CDN / Edge, Storage Services, Data Pipeline / ETL / ELT, Message Queues / Streaming, Operating Systems / Infrastructure |
| Security | Security, Security Platforms |
| Testing & Quality | Testing, Testing / Quality Platforms |
| Developer Tools | Build Tools / Bundlers / Package Managers, Version Control, VCS Hosting / Artifact Registries, IDEs and Development Environments, Documentation, Design Tools |
| Specialty | Game Development, Embedded / Systems, Accessibility, Blockchain / Web3, Low-Code / No-Code / Business Platforms, Communication / Collaboration (tools) |
| Leadership & Management | Leadership, Project Management, Strategy and Vision, Influence and Persuasion |
| Interpersonal | Communication, Team Collaboration, Customer / Client Skills, Teaching / Mentoring, Emotional Intelligence, Diversity Equity and Inclusion, Professional Skills |
| Problem Solving & Process | Problem Solving / Analytical, Organizational / Planning Skills, Agile / Process Skills, Business Skills, Personal Effectiveness |

**Deduplication rules:**
- Each skill appears exactly once. If a skill exists in multiple lists (e.g., "Docker" in both SKILLS_LIST and TECHNOLOGIES_LIST), keep the most specific type. For example, "Docker" -> "DevOps & Infrastructure", not "Programming Languages".
- Resolve overlaps between SKILLS_LIST, TECHNOLOGIES_LIST, and SOFT_SKILLS_LIST. Skills from TECHNOLOGIES_LIST that overlap with SKILLS_LIST (like "ECS", "S3", "Lambda" etc.) should use the type from their comment-header category.
- When the same term appears under different comment headers in different lists, prefer the TECHNOLOGIES_LIST category for infrastructure/platform terms and SKILLS_LIST for development tools/frameworks.

The file structure:

```python
"""
Master skill definitions -- single source of truth for all recognized skills.
Each skill maps to exactly one of 15 consolidated types.
"""

SKILL_TYPES: list[str] = [
    "Programming Languages",
    "Frontend",
    "Backend",
    "Mobile",
    "Data & ML",
    "Databases",
    "Cloud Services",
    "DevOps & Infrastructure",
    "Security",
    "Testing & Quality",
    "Developer Tools",
    "Specialty",
    "Leadership & Management",
    "Interpersonal",
    "Problem Solving & Process",
]

SKILLS: dict[str, str] = {
    # ── Programming Languages ─────────────────────────────────────────────────
    "Python": "Programming Languages",
    "JavaScript": "Programming Languages",
    "TypeScript": "Programming Languages",
    # ... (all entries from SKILLS_LIST "Programming Languages" section)

    # ── Frontend ──────────────────────────────────────────────────────────────
    "React": "Frontend",
    "React.js": "Frontend",
    "Angular": "Frontend",
    # ... (all from "Frontend Frameworks / Libraries" + "Frontend Styling")

    # ── Backend ───────────────────────────────────────────────────────────────
    "FastAPI": "Backend",
    "Django": "Backend",
    # ... (all from "Backend Frameworks" + "API Standards and Protocols")

    # ... continue for all 15 types, migrating every entry from all three lists
}
```

**Critical:** Include EVERY entry from `SKILLS_LIST`, `TECHNOLOGIES_LIST`, and `SOFT_SKILLS_LIST` in `nlp_extraction.py`. The three sets combined have ~900 entries. After deduplication there will be fewer. Do not skip any entries.

To build this file:
1. Read `nlp_extraction.py` lines 13-329 (SKILLS_LIST), 332-609 (TECHNOLOGIES_LIST), 612-797 (SOFT_SKILLS_LIST)
2. For each comment-header section, map it to one of the 15 consolidated types using the table above
3. Add each entry as `"SkillName": "ConsolidatedType"`
4. When a skill appears in multiple lists, keep only one entry with the most appropriate type
5. Preserve the canonical casing from the original lists

- [ ] **Step 4: Run test to verify it passes**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/test_skill_definitions.py -v`
Expected: PASS (all 7 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/services/skill_definitions.py backend/tests/test_skill_definitions.py
git commit -m "feat: add master skill definitions with 15 consolidated types"
```

---

### Task 2: Rewrite nlp_extraction.py for typed output

**Files:**
- Modify: `backend/services/nlp_extraction.py`
- Modify: `backend/tests/test_nlp_extraction.py`

- [ ] **Step 1: Rewrite the tests**

Replace `backend/tests/test_nlp_extraction.py` with:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/test_nlp_extraction.py -v`
Expected: FAIL -- `extract_skills` still returns `list[str]`, and `extract_from_documents` still has three keys.

- [ ] **Step 3: Rewrite nlp_extraction.py**

Replace the entire content of `backend/services/nlp_extraction.py` with:

```python
"""
NLP-based extraction service.
Uses spaCy PhraseMatcher with a unified skill dictionary for offline
keyword extraction. Returns typed skill objects {name, type}.
"""

import logging

import spacy
from spacy.matcher import PhraseMatcher

from backend.services.skill_definitions import SKILLS

logger = logging.getLogger(__name__)

EMPTY_RESULT = {"skills": []}

# Build canonical-lowercase -> (canonical_name, type) lookup
_lower_map: dict[str, tuple[str, str]] = {
    name.lower(): (name, skill_type)
    for name, skill_type in SKILLS.items()
}

# ── SpaCy pipeline (lazy-loaded) ─────────────────────────────────────────────

_nlp = None
_matcher: PhraseMatcher | None = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm", disable=["ner"])
    return _nlp


def _get_matcher() -> PhraseMatcher:
    global _matcher
    if _matcher is None:
        nlp = _get_nlp()
        _matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        patterns = [nlp.make_doc(term.lower()) for term in SKILLS]
        _matcher.add("SKILL", patterns)
    return _matcher


# ── Public API ────────────────────────────────────────────────────────────────

def extract_skills(text: str) -> list[dict]:
    """Return typed skill objects found in text: [{"name": ..., "type": ...}, ...]"""
    if not text or not text.strip():
        return []
    nlp = _get_nlp()
    matcher = _get_matcher()
    doc = nlp(text)
    seen: set[str] = set()
    results: list[dict] = []
    for _match_id, start, end in matcher(doc):
        span_lower = doc[start:end].text.lower()
        entry = _lower_map.get(span_lower)
        if entry and entry[0] not in seen:
            seen.add(entry[0])
            results.append({"name": entry[0], "type": entry[1]})
    return sorted(results, key=lambda s: s["name"])


def extract_from_documents(doc_contents: str) -> dict:
    """
    Main entry point. Returns {"skills": [{"name": ..., "type": ...}, ...]}.
    Works completely offline via spaCy.
    """
    if doc_contents == "No previewable documents found.":
        return dict(EMPTY_RESULT)

    return {"skills": extract_skills(doc_contents)}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/test_nlp_extraction.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add backend/services/nlp_extraction.py backend/tests/test_nlp_extraction.py
git commit -m "feat: rewrite nlp_extraction for typed skill output with single matcher"
```

---

### Task 3: Update extraction service (merge_suggestions)

**Files:**
- Modify: `backend/services/extraction.py`
- Modify: `backend/tests/test_extraction.py`

- [ ] **Step 1: Rewrite the tests**

Replace `backend/tests/test_extraction.py` with:

```python
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
        # Python should not be duplicated
        assert names.count("Python") == 1
        # New skills added
        assert "FastAPI" in names
        assert "React" in names
        # Existing preserved
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/test_extraction.py -v`
Expected: FAIL -- `merge_suggestions` still expects old three-key format.

- [ ] **Step 3: Update extraction.py**

Replace `backend/services/extraction.py` with:

```python
import logging
from backend.services.nlp_extraction import extract_from_documents  # noqa: F401

logger = logging.getLogger(__name__)


def merge_suggestions(existing_profile: dict, suggestions: dict) -> dict:
    profile = dict(existing_profile)
    existing_skills = profile.get("skills", [])
    existing_names = {s["name"].lower() for s in existing_skills}
    merged = list(existing_skills)
    for skill in suggestions.get("skills", []):
        if skill["name"].lower() not in existing_names:
            merged.append(skill)
            existing_names.add(skill["name"].lower())
    profile["skills"] = merged
    return profile
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/test_extraction.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add backend/services/extraction.py backend/tests/test_extraction.py
git commit -m "feat: update merge_suggestions for typed skill objects"
```

---

### Task 4: Update extraction router for typed API

**Files:**
- Modify: `backend/routers/extraction.py`
- Modify: `backend/tests/test_extraction_api.py`

- [ ] **Step 1: Rewrite the API tests**

Replace `backend/tests/test_extraction_api.py` with:

```python
import json
import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.fixture
def mock_extraction():
    return {
        "skills": [
            {"name": "Python", "type": "Programming Languages"},
            {"name": "FastAPI", "type": "Backend"},
            {"name": "Docker", "type": "DevOps & Infrastructure"},
            {"name": "AWS", "type": "Cloud Services"},
            {"name": "collaboration", "type": "Interpersonal"},
        ],
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
async def test_analyze_returns_typed_suggestions(mock_extraction, mock_metadata):
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
            assert "skills" in data
            assert isinstance(data["skills"], list)
            assert data["skills"][0]["name"] == "Python"
            assert data["skills"][0]["type"] == "Programming Languages"
            # No old keys
            assert "technologies" not in data
            assert "soft_skills" not in data


@pytest.mark.asyncio
async def test_accept_merges_typed_skills(mock_extraction):
    existing_profile = {
        "skills": [{"name": "SQL", "type": "Databases"}],
        "experience": [],
        "education": [],
        "certifications": [],
        "summary": "",
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
            call_args = mock_profile_svc.put.call_args[0][0]
            names = [s["name"] for s in call_args["skills"]]
            assert "SQL" in names
            assert "Python" in names
            assert "Docker" in names


@pytest.mark.asyncio
async def test_accept_partial_typed_suggestions():
    existing_profile = {
        "skills": [{"name": "Go", "type": "Programming Languages"}],
        "experience": [],
        "education": [],
        "certifications": [],
        "summary": "",
    }
    mock_profile_svc = MagicMock()
    mock_profile_svc.get.return_value = existing_profile
    mock_profile_svc.put.return_value = None

    partial = {
        "skills": [{"name": "Rust", "type": "Programming Languages"}],
    }

    with patch("backend.routers.extraction.get_profile_service", return_value=mock_profile_svc):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/extraction/accept", json=partial)
            assert resp.status_code == 200
            call_args = mock_profile_svc.put.call_args[0][0]
            names = [s["name"] for s in call_args["skills"]]
            assert "Go" in names
            assert "Rust" in names


@pytest.mark.asyncio
async def test_analyze_with_specific_document_ids(mock_metadata):
    mock_metadata["files"]["xyz789"] = {
        "original_name": "cover.txt",
        "stored_name": "xyz789_cover.txt",
        "mime_type": "text/plain",
        "tags": [],
    }
    mock_meta_svc = MagicMock()
    mock_meta_svc.read.return_value = mock_metadata
    mock_meta_svc.docs_dir = MagicMock()

    read_calls = []
    def capture(docs_dir, meta):
        read_calls.append(meta)
        return "Python developer"

    with (
        patch("backend.routers.extraction.get_metadata_service", return_value=mock_meta_svc),
        patch("backend.routers.extraction.read_document_contents", side_effect=capture),
        patch("backend.routers.extraction.extract_from_documents", return_value={"skills": []}),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/extraction/analyze",
                json={"document_ids": ["abc123"]},
            )
    assert resp.status_code == 200
    passed_meta = read_calls[0]
    assert "abc123" in passed_meta["files"]
    assert "xyz789" not in passed_meta["files"]


@pytest.mark.asyncio
async def test_analyze_with_empty_ids_reads_all_docs(mock_metadata):
    mock_meta_svc = MagicMock()
    mock_meta_svc.read.return_value = mock_metadata
    mock_meta_svc.docs_dir = MagicMock()

    read_calls = []
    def capture(docs_dir, meta):
        read_calls.append(meta)
        return "text"

    with (
        patch("backend.routers.extraction.get_metadata_service", return_value=mock_meta_svc),
        patch("backend.routers.extraction.read_document_contents", side_effect=capture),
        patch("backend.routers.extraction.extract_from_documents", return_value={"skills": []}),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/extraction/analyze",
                json={"document_ids": []},
            )
    assert resp.status_code == 200
    assert list(read_calls[0]["files"].keys()) == list(mock_metadata["files"].keys())


@pytest.mark.asyncio
async def test_analyze_with_nonexistent_id_skips_gracefully(mock_metadata):
    mock_meta_svc = MagicMock()
    mock_meta_svc.read.return_value = mock_metadata
    mock_meta_svc.docs_dir = MagicMock()

    read_calls = []
    def capture(docs_dir, meta):
        read_calls.append(meta)
        return "text"

    with (
        patch("backend.routers.extraction.get_metadata_service", return_value=mock_meta_svc),
        patch("backend.routers.extraction.read_document_contents", side_effect=capture),
        patch("backend.routers.extraction.extract_from_documents", return_value={"skills": []}),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/extraction/analyze",
                json={"document_ids": ["does_not_exist"]},
            )
    assert resp.status_code == 200
    assert read_calls[0]["files"] == {}


@pytest.mark.asyncio
async def test_analyze_with_no_body_reads_all_docs(mock_metadata):
    mock_meta_svc = MagicMock()
    mock_meta_svc.read.return_value = mock_metadata
    mock_meta_svc.docs_dir = MagicMock()

    read_calls = []
    def capture(docs_dir, meta):
        read_calls.append(meta)
        return "text"

    with (
        patch("backend.routers.extraction.get_metadata_service", return_value=mock_meta_svc),
        patch("backend.routers.extraction.read_document_contents", side_effect=capture),
        patch("backend.routers.extraction.extract_from_documents", return_value={"skills": []}),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/extraction/analyze")
    assert resp.status_code == 200
    assert list(read_calls[0]["files"].keys()) == list(mock_metadata["files"].keys())
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/test_extraction_api.py -v`
Expected: FAIL -- `AcceptSuggestionsRequest` still expects old three-key format.

- [ ] **Step 3: Update extraction router**

Replace `backend/routers/extraction.py` with:

```python
import logging
from fastapi import APIRouter, Body
from pydantic import BaseModel
from backend.config import DOCUMENTS_DIR, PROFILE_PATH
from backend.services.document_reader import read_document_contents
from backend.services.extraction import extract_from_documents, merge_suggestions
from backend.services.metadata import MetadataService
from backend.services.profile import ProfileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/extraction", tags=["extraction"])

_metadata_service: MetadataService | None = None
_profile_service: ProfileService | None = None


def get_metadata_service() -> MetadataService:
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = MetadataService(DOCUMENTS_DIR)
    return _metadata_service


def get_profile_service() -> ProfileService:
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService(PROFILE_PATH)
    return _profile_service


class AnalyzeRequest(BaseModel):
    document_ids: list[str] = []


class TypedSkillModel(BaseModel):
    name: str
    type: str


class AcceptSuggestionsRequest(BaseModel):
    skills: list[TypedSkillModel] = []


@router.post("/analyze")
async def analyze_documents(
    body: AnalyzeRequest = Body(default=AnalyzeRequest()),
):
    service = get_metadata_service()
    metadata = service.read()

    if body.document_ids:
        all_files = metadata.get("files", {})
        filtered_files = {
            fid: meta
            for fid, meta in all_files.items()
            if fid in body.document_ids
        }
        filtered_metadata = {**metadata, "files": filtered_files}
    else:
        filtered_metadata = metadata

    doc_contents = read_document_contents(service.docs_dir, filtered_metadata)
    logger.info(
        "Running extraction on %d documents", len(filtered_metadata.get("files", {}))
    )
    result = extract_from_documents(doc_contents)
    return result


@router.post("/accept")
async def accept_suggestions(body: AcceptSuggestionsRequest):
    profile_svc = get_profile_service()
    existing = profile_svc.get()
    merged = merge_suggestions(existing, body.model_dump())
    profile_svc.put(merged)
    logger.info("Accepted extraction suggestions into profile")
    return profile_svc.get()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/test_extraction_api.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add backend/routers/extraction.py backend/tests/test_extraction_api.py
git commit -m "feat: update extraction API for typed skill objects"
```

---

### Task 5: Update profile router and service for typed skills

**Files:**
- Modify: `backend/routers/profile.py`
- Modify: `backend/services/profile.py`
- Test: `backend/tests/test_profile_migration.py` (new)

- [ ] **Step 1: Write migration tests**

Create `backend/tests/test_profile_migration.py`:

```python
"""Tests for profile on-read migration from string skills to typed skills."""

import json
import pytest
from pathlib import Path
from backend.services.profile import ProfileService


@pytest.fixture
def profile_path(tmp_path):
    return tmp_path / ".profile.json"


class TestProfileMigration:
    def test_migrates_string_skills_to_typed(self, profile_path):
        profile_path.write_text(json.dumps({
            "summary": "",
            "skills": ["Python", "React", "Docker"],
            "experience": [],
            "education": [],
            "certifications": [],
        }))
        svc = ProfileService(profile_path)
        result = svc.get()
        assert isinstance(result["skills"], list)
        for s in result["skills"]:
            assert "name" in s
            assert "type" in s
        names = [s["name"] for s in result["skills"]]
        assert "Python" in names
        assert "React" in names
        assert "Docker" in names

    def test_drops_unknown_string_skills(self, profile_path):
        profile_path.write_text(json.dumps({
            "summary": "",
            "skills": ["Python", "TotallyFakeSkill123"],
            "experience": [],
            "education": [],
            "certifications": [],
        }))
        svc = ProfileService(profile_path)
        result = svc.get()
        names = [s["name"] for s in result["skills"]]
        assert "Python" in names
        assert "TotallyFakeSkill123" not in names

    def test_preserves_already_typed_skills(self, profile_path):
        profile_path.write_text(json.dumps({
            "summary": "",
            "skills": [{"name": "Python", "type": "Programming Languages"}],
            "experience": [],
            "education": [],
            "certifications": [],
        }))
        svc = ProfileService(profile_path)
        result = svc.get()
        assert result["skills"] == [{"name": "Python", "type": "Programming Languages"}]

    def test_migration_persists_on_next_write(self, profile_path):
        profile_path.write_text(json.dumps({
            "summary": "",
            "skills": ["Python"],
            "experience": [],
            "education": [],
            "certifications": [],
        }))
        svc = ProfileService(profile_path)
        profile = svc.get()
        svc.put(profile)
        raw = json.loads(profile_path.read_text())
        assert isinstance(raw["skills"][0], dict)
        assert raw["skills"][0]["name"] == "Python"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/test_profile_migration.py -v`
Expected: FAIL -- `ProfileService.get()` does not migrate string skills.

- [ ] **Step 3: Update profile service with migration**

Replace `backend/services/profile.py` with:

```python
import json
from pathlib import Path
from threading import Lock

from backend.services.skill_definitions import SKILLS

VALID_SECTIONS = {"summary", "skills", "experience", "activities", "education", "certifications"}

EMPTY_PROFILE = {
    "summary": "",
    "skills": [],
    "experience": [],
    "activities": [],
    "education": [],
    "certifications": [],
}


def _migrate_skills(skills: list) -> list[dict]:
    """Convert plain string skills to typed objects. Drop unknowns."""
    if not skills:
        return []
    if isinstance(skills[0], dict):
        return skills
    result = []
    for s in skills:
        if isinstance(s, str) and s in SKILLS:
            result.append({"name": s, "type": SKILLS[s]})
    return result


class ProfileService:
    def __init__(self, profile_path: Path):
        self.profile_path = profile_path
        self._lock = Lock()

    def get(self) -> dict:
        with self._lock:
            if not self.profile_path.exists():
                self._write(dict(EMPTY_PROFILE))
            profile = json.loads(self.profile_path.read_text())
            profile["skills"] = _migrate_skills(profile.get("skills", []))
            return profile

    def put(self, profile: dict):
        with self._lock:
            self._write(profile)

    def patch(self, section: str, data) -> dict:
        if section not in VALID_SECTIONS:
            raise KeyError(f"Invalid section: {section}")
        with self._lock:
            profile = json.loads(self.profile_path.read_text()) if self.profile_path.exists() else dict(EMPTY_PROFILE)
            profile[section] = data
            self._write(profile)
            return profile

    def _write(self, data: dict):
        self.profile_path.write_text(json.dumps(data, indent=2))
```

- [ ] **Step 4: Run migration tests to verify they pass**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/test_profile_migration.py -v`
Expected: PASS (all 4 tests)

- [ ] **Step 5: Update profile router**

Replace `backend/routers/profile.py`. Key changes:
- `ProfileRequest.skills` changes from `list[str]` to `list[TypedSkillModel]`
- Add `TypedSkillModel` Pydantic model with validation
- Update `_SECTION_VALIDATORS["skills"]` to use `list[TypedSkillModel]`
- Add `GET /api/skills/types` endpoint

```python
import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, TypeAdapter, ValidationError, field_validator
from backend.config import PROFILE_PATH
from backend.services.profile import ProfileService
from backend.services.skill_definitions import SKILL_TYPES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])


class TypedSkillModel(BaseModel):
    name: str
    type: str

    @field_validator("type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        if v not in SKILL_TYPES:
            raise ValueError(f"Invalid skill type: {v}")
        return v


class ExperienceEntry(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: str | None = None
    accomplishments: list[str] = []


class ActivityEntry(BaseModel):
    name: str
    category: str = ""
    url: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    details: list[str] = []


class EducationEntry(BaseModel):
    institution: str
    degree: str
    field: str | None = None
    start_date: str = ""
    end_date: str | None = None
    details: list[str] = []


class CertificationEntry(BaseModel):
    name: str
    issuer: str
    date: str


class ProfileRequest(BaseModel):
    summary: str = ""
    skills: list[TypedSkillModel] = []
    experience: list[ExperienceEntry] = []
    activities: list[ActivityEntry] = []
    education: list[EducationEntry] = []
    certifications: list[CertificationEntry] = []

    @field_validator("summary")
    @classmethod
    def max_text_length(cls, v: str) -> str:
        if len(v) > 5000:
            raise ValueError("Max 5000 characters")
        return v

    @field_validator("skills")
    @classmethod
    def max_skills(cls, v: list) -> list:
        if len(v) > 100:
            raise ValueError("Max 100 skills")
        return v

    @field_validator("experience")
    @classmethod
    def max_experience(cls, v: list) -> list:
        if len(v) > 50:
            raise ValueError("Max 50 experience entries")
        return v

_profile_service: ProfileService | None = None


def get_service() -> ProfileService:
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService(PROFILE_PATH)
    return _profile_service


@router.get("")
async def get_profile():
    return get_service().get()


@router.put("")
async def put_profile(body: ProfileRequest):
    logger.info("Profile replaced")
    get_service().put(body.model_dump())
    return get_service().get()


_SECTION_VALIDATORS = {
    "summary": TypeAdapter(str),
    "skills": TypeAdapter(list[TypedSkillModel]),
    "experience": TypeAdapter(list[ExperienceEntry]),
    "activities": TypeAdapter(list[ActivityEntry]),
    "education": TypeAdapter(list[EducationEntry]),
    "certifications": TypeAdapter(list[CertificationEntry]),
}


@router.patch("/{section}")
async def patch_section(section: str, request: Request):
    if section not in _SECTION_VALIDATORS:
        raise HTTPException(status_code=400, detail=f"Invalid section: {section}")
    body = await request.json()
    validator = _SECTION_VALIDATORS[section]
    try:
        validated = validator.validate_python(body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    # Convert Pydantic models back to dicts for JSON storage
    if hasattr(validated, '__iter__') and not isinstance(validated, str):
        data = [item.model_dump() if isinstance(item, BaseModel) else item for item in validated]
    else:
        data = validated
    try:
        result = get_service().patch(section, data)
        logger.info("Profile section updated: %s", section)
        return result
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid section: {section}")


skills_router = APIRouter(prefix="/api/skills", tags=["skills"])


@skills_router.get("/types")
async def get_skill_types():
    return SKILL_TYPES
```

**Important:** The new `skills_router` must be registered in `backend/main.py`. Add the import and include:

In `backend/main.py`, add:
```python
from backend.routers.profile import skills_router
app.include_router(skills_router)
```

- [ ] **Step 6: Run all backend tests**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/ -v`
Expected: PASS (all tests)

- [ ] **Step 7: Commit**

```bash
git add backend/routers/profile.py backend/services/profile.py backend/tests/test_profile_migration.py backend/main.py
git commit -m "feat: update profile for typed skills with on-read migration and /api/skills/types"
```

---

### Task 6: Update frontend types

**Files:**
- Modify: `src/api/extraction.ts`
- Modify: `src/api/profile.ts`

- [ ] **Step 1: Update extraction.ts**

Replace `src/api/extraction.ts` with:

```typescript
export interface TypedSkill {
  name: string
  type: string
}

export interface ExtractionResult {
  skills: TypedSkill[]
}

export type SelectionState = Record<string, boolean>

export async function analyzeDocuments(documentIds: string[] = []): Promise<ExtractionResult> {
  const res = await fetch('/api/extraction/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_ids: documentIds }),
  })
  if (!res.ok) throw new Error('Failed to analyze documents')
  return res.json()
}

export async function acceptSuggestions(suggestions: ExtractionResult): Promise<unknown> {
  const res = await fetch('/api/extraction/accept', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(suggestions),
  })
  if (!res.ok) throw new Error('Failed to accept suggestions')
  return res.json()
}
```

- [ ] **Step 2: Update profile.ts**

Replace `src/api/profile.ts` with:

```typescript
import type { TypedSkill } from './extraction'

export interface Experience { company: string; role: string; start_date: string; end_date: string | null; accomplishments: string[] }
export interface Activity { name: string; category: string; url?: string; start_date?: string; end_date?: string | null; details: string[] }
export interface Education { institution: string; degree: string; field?: string; start_date: string; end_date: string | null; details: string[] }
export interface Certification { name: string; issuer: string; date: string }

export interface Profile {
  summary: string
  skills: TypedSkill[]
  experience: Experience[]
  activities: Activity[]
  education: Education[]
  certifications: Certification[]
}

export async function fetchProfile(): Promise<Profile> {
  const res = await fetch('/api/profile')
  if (!res.ok) throw new Error('Failed to fetch profile')
  return res.json()
}

export async function putProfile(profile: Profile): Promise<Profile> {
  const res = await fetch('/api/profile', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(profile) })
  if (!res.ok) throw new Error('Failed to update profile')
  return res.json()
}

export async function patchSection(section: string, data: unknown): Promise<Profile> {
  const res = await fetch(`/api/profile/${section}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
  if (!res.ok) throw new Error('Failed to patch section')
  return res.json()
}

export async function fetchSkillTypes(): Promise<string[]> {
  const res = await fetch('/api/skills/types')
  if (!res.ok) throw new Error('Failed to fetch skill types')
  return res.json()
}
```

- [ ] **Step 3: Commit**

```bash
git add src/api/extraction.ts src/api/profile.ts
git commit -m "feat: update frontend types for typed skills"
```

---

### Task 7: Update ExtractionResultsPanel

**Files:**
- Modify: `src/components/documents/ExtractionResultsPanel.tsx`
- Modify: `src/__tests__/documents/ExtractionResultsPanel.test.tsx`

- [ ] **Step 1: Rewrite the tests**

Replace `src/__tests__/documents/ExtractionResultsPanel.test.tsx` with:

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ExtractionResultsPanel from '../../components/documents/ExtractionResultsPanel'
import type { ExtractionResult, SelectionState } from '../../api/extraction'

const fullResult: ExtractionResult = {
  skills: [
    { name: 'Python', type: 'Programming Languages' },
    { name: 'React', type: 'Frontend' },
    { name: 'Docker', type: 'DevOps & Infrastructure' },
    { name: 'communication', type: 'Interpersonal' },
  ],
}

const allSelected: SelectionState = {
  Python: true,
  React: true,
  Docker: true,
  communication: true,
}

const baseProps = {
  result: fullResult,
  selection: allSelected,
  onToggle: vi.fn(),
  onAccept: vi.fn(),
  onReanalyze: vi.fn(),
  onDismiss: vi.fn(),
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('ExtractionResultsPanel', () => {
  it('renders chips for each skill', () => {
    render(<ExtractionResultsPanel {...baseProps} />)
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Docker')).toBeInTheDocument()
    expect(screen.getByText('communication')).toBeInTheDocument()
  })

  it('renders type headings', () => {
    render(<ExtractionResultsPanel {...baseProps} />)
    expect(screen.getByText('Programming Languages')).toBeInTheDocument()
    expect(screen.getByText('Frontend')).toBeInTheDocument()
    expect(screen.getByText('DevOps & Infrastructure')).toBeInTheDocument()
    expect(screen.getByText('Interpersonal')).toBeInTheDocument()
  })

  it('calls onToggle with skill name when a chip is clicked', () => {
    const onToggle = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onToggle={onToggle} />)
    fireEvent.click(screen.getByText('Python'))
    expect(onToggle).toHaveBeenCalledWith('Python')
  })

  it('applies deselected class to toggled-off chips', () => {
    const selection: SelectionState = {
      Python: false,
      React: true,
      Docker: true,
      communication: true,
    }
    render(<ExtractionResultsPanel {...baseProps} selection={selection} />)
    expect(screen.getByText('Python')).toHaveClass('deselected')
    expect(screen.getByText('React')).not.toHaveClass('deselected')
  })

  it('calls onAccept when Accept Selected is clicked', () => {
    const onAccept = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onAccept={onAccept} />)
    fireEvent.click(screen.getByText('Accept Selected'))
    expect(onAccept).toHaveBeenCalled()
  })

  it('calls onReanalyze when Re-analyze is clicked', () => {
    const onReanalyze = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onReanalyze={onReanalyze} />)
    fireEvent.click(screen.getByText('Re-analyze'))
    expect(onReanalyze).toHaveBeenCalled()
  })

  it('calls onDismiss when Done is clicked', () => {
    const onDismiss = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onDismiss={onDismiss} />)
    fireEvent.click(screen.getByText('Done'))
    expect(onDismiss).toHaveBeenCalled()
  })

  it('shows No suggestions found when result is empty', () => {
    const empty: ExtractionResult = { skills: [] }
    render(<ExtractionResultsPanel {...baseProps} result={empty} selection={{}} />)
    expect(screen.getByText('No suggestions found.')).toBeInTheDocument()
  })

  it('profile items passed as selected=true start without deselected class', () => {
    const selection: SelectionState = {
      Python: true,
      React: false,
      Docker: true,
      communication: true,
    }
    render(<ExtractionResultsPanel {...baseProps} selection={selection} />)
    expect(screen.getByText('Python')).not.toHaveClass('deselected')
  })

  it('profile items (selected=true) are clickable and call onToggle', () => {
    const onToggle = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onToggle={onToggle} />)
    fireEvent.click(screen.getByText('Python'))
    expect(onToggle).toHaveBeenCalledWith('Python')
  })

  it('deselecting a previously-selected item applies deselected class', () => {
    const selection: SelectionState = {
      Python: false,
      React: true,
      Docker: true,
      communication: true,
    }
    render(<ExtractionResultsPanel {...baseProps} selection={selection} />)
    expect(screen.getByText('Python')).toHaveClass('deselected')
    expect(screen.getByText('React')).not.toHaveClass('deselected')
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/whweb/Code/haid-hunter && npx vitest run src/__tests__/documents/ExtractionResultsPanel.test.tsx`
Expected: FAIL -- component still uses old three-key format.

- [ ] **Step 3: Rewrite ExtractionResultsPanel**

Replace `src/components/documents/ExtractionResultsPanel.tsx` with:

```tsx
import type { ExtractionResult, SelectionState } from '../../api/extraction'

interface ExtractionResultsPanelProps {
  result: ExtractionResult
  selection: SelectionState
  onToggle: (name: string) => void
  onAccept: () => void
  onReanalyze: () => void
  onDismiss: () => void
}

export default function ExtractionResultsPanel({
  result,
  selection,
  onToggle,
  onAccept,
  onReanalyze,
  onDismiss,
}: ExtractionResultsPanelProps) {
  if (result.skills.length === 0) {
    return (
      <div className="extraction-panel">
        <p>No suggestions found.</p>
        <button className="btn btn-secondary" onClick={onDismiss}>Done</button>
      </div>
    )
  }

  // Group skills by type
  const grouped: Record<string, typeof result.skills> = {}
  for (const skill of result.skills) {
    if (!grouped[skill.type]) grouped[skill.type] = []
    grouped[skill.type].push(skill)
  }

  return (
    <div className="extraction-panel">
      {Object.entries(grouped).map(([type, skills]) => (
        <div key={type} className="extraction-category">
          <h4>{type}</h4>
          <div className="extraction-chips">
            {skills.map(skill => {
              const selected = selection[skill.name] ?? false
              return (
                <span
                  key={skill.name}
                  className={`extraction-chip${selected ? '' : ' deselected'}`}
                  onClick={() => onToggle(skill.name)}
                >
                  {skill.name}
                </span>
              )
            })}
          </div>
        </div>
      ))}
      <div className="extraction-actions">
        <button className="btn btn-primary" onClick={onAccept}>Accept Selected</button>
        <button className="btn btn-secondary" onClick={onReanalyze}>Re-analyze</button>
        <button className="btn btn-secondary" onClick={onDismiss}>Done</button>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/whweb/Code/haid-hunter && npx vitest run src/__tests__/documents/ExtractionResultsPanel.test.tsx`
Expected: PASS (all 11 tests)

- [ ] **Step 5: Commit**

```bash
git add src/components/documents/ExtractionResultsPanel.tsx src/__tests__/documents/ExtractionResultsPanel.test.tsx
git commit -m "feat: ExtractionResultsPanel groups by skill type"
```

---

### Task 8: Update DocumentManager for typed skills

**Files:**
- Modify: `src/components/documents/DocumentManager.tsx`
- Modify: `src/__tests__/documents/DocumentManager.test.tsx`

- [ ] **Step 1: Update the test fixtures**

In `src/__tests__/documents/DocumentManager.test.tsx`, update the mock data:

Replace the `emptyProfile` and `extractionResult` constants at the top:

```typescript
const emptyProfile = { summary: '', skills: [], experience: [], activities: [], education: [], certifications: [] }
const extractionResult = {
  skills: [
    { name: 'Python', type: 'Programming Languages' },
    { name: 'Docker', type: 'DevOps & Infrastructure' },
  ],
}
```

The rest of the test file stays the same -- the tests check for rendered text ('Python', 'Accept Selected', etc.) which are unchanged.

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/whweb/Code/haid-hunter && npx vitest run src/__tests__/documents/DocumentManager.test.tsx`
Expected: FAIL -- DocumentManager still uses old CATEGORIES and three-key format.

- [ ] **Step 3: Update DocumentManager**

Replace `src/components/documents/DocumentManager.tsx`. Key changes:
- Remove `CATEGORIES` constant
- Change `profileSkills` state from `string[]` to `TypedSkill[]`
- `handleAnalyze`: build flat `SelectionState` keyed by skill name
- `handleToggle`: simplified to `(name: string)`
- `handleAccept`: build typed skill list from selection

```tsx
import { useState, useEffect, useCallback } from 'react'
import { TagSidebar } from './TagSidebar'
import { DocumentToolbar } from './DocumentToolbar'
import { DropZone } from './DropZone'
import { DocumentList } from './DocumentList'
import { DocumentPreview } from './DocumentPreview'
import ExtractionResultsPanel from './ExtractionResultsPanel'
import {
  fetchDocuments,
  fetchDocument,
  uploadDocuments,
  updateDocument,
  deleteDocument,
  syncDocuments,
} from '../../api/documents'
import { analyzeDocuments } from '../../api/extraction'
import type { ExtractionResult, SelectionState, TypedSkill } from '../../api/extraction'
import { fetchProfile, patchSection } from '../../api/profile'
import { fetchTags, createTag, deleteTag } from '../../api/tags'
import type { DocumentMeta } from '../../api/documents'

export default function DocumentManager() {
  const [documents, setDocuments] = useState<DocumentMeta[]>([])
  const [allDocuments, setAllDocuments] = useState<DocumentMeta[]>([])
  const [tags, setTags] = useState<string[]>([])
  const [activeTag, setActiveTag] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [selectedDoc, setSelectedDoc] = useState<DocumentMeta | null>(null)
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(true)

  // Extraction state
  const [checkedIds, setCheckedIds] = useState<Set<string>>(new Set())
  const [extractionResult, setExtractionResult] = useState<ExtractionResult | null>(null)
  const [extractionSelection, setExtractionSelection] = useState<SelectionState>({})
  const [extractionLoading, setExtractionLoading] = useState(false)
  const [profileSkills, setProfileSkills] = useState<TypedSkill[]>([])

  const loadDocuments = useCallback(async () => {
    try {
      const docs = await fetchDocuments(activeTag ?? undefined, search || undefined)
      setDocuments(docs)
    } catch {
      setStatus('Failed to load documents.')
    }
  }, [activeTag, search])

  const loadAllDocuments = useCallback(async () => {
    try {
      const docs = await fetchDocuments()
      setAllDocuments(docs)
    } catch { /* counts will be stale but not break */ }
  }, [])

  const loadTags = useCallback(async () => {
    try {
      const t = await fetchTags()
      setTags(t)
    } catch {
      setStatus('Failed to load tags.')
    }
  }, [])

  useEffect(() => {
    Promise.all([loadDocuments(), loadTags(), loadAllDocuments()]).finally(() => setLoading(false))
  }, [loadDocuments, loadTags, loadAllDocuments])

  useEffect(() => {
    if (!selectedId) { setSelectedDoc(null); return }
    fetchDocument(selectedId).then(setSelectedDoc).catch(() => setSelectedDoc(null))
  }, [selectedId])

  const handleSelectDoc = (id: string) => {
    setSelectedId(id)
    setExtractionResult(null)
  }

  const handleCheck = (id: string) => {
    setCheckedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const handleCheckTag = (tag: string) => {
    const tagDocs = allDocuments.filter(d => d.tags.includes(tag))
    const allChecked = tagDocs.every(d => checkedIds.has(d.id))
    setCheckedIds(prev => {
      const next = new Set(prev)
      if (allChecked) {
        tagDocs.forEach(d => next.delete(d.id))
      } else {
        tagDocs.forEach(d => next.add(d.id))
      }
      return next
    })
  }

  const handleAnalyze = async () => {
    setExtractionLoading(true)
    try {
      let skills: TypedSkill[] = []
      try {
        const profile = await fetchProfile()
        skills = profile.skills ?? []
      } catch { /* proceed without existing skills */ }

      const data = await analyzeDocuments([...checkedIds])
      setProfileSkills(skills)
      setExtractionResult(data)

      const profileNames = new Set(skills.map(s => s.name))
      const sel: SelectionState = {}
      for (const skill of data.skills) {
        sel[skill.name] = profileNames.has(skill.name)
      }
      setExtractionSelection(sel)
    } catch {
      setStatus('Analysis failed.')
    } finally {
      setExtractionLoading(false)
    }
  }

  const handleToggle = (name: string) => {
    setExtractionSelection(prev => ({
      ...prev,
      [name]: !prev[name],
    }))
  }

  const handleAccept = async () => {
    if (!extractionResult) return
    const profileNames = new Set(profileSkills.map(s => s.name))
    const updatedSkills = new Map<string, TypedSkill>()
    // Start with existing profile skills
    for (const s of profileSkills) {
      updatedSkills.set(s.name, s)
    }
    // Add/remove based on selection
    for (const skill of extractionResult.skills) {
      if (extractionSelection[skill.name]) {
        updatedSkills.set(skill.name, skill)
      } else {
        updatedSkills.delete(skill.name)
      }
    }
    await patchSection('skills', [...updatedSkills.values()])
    setExtractionResult(null)
  }

  const handleDismiss = () => {
    setExtractionResult(null)
  }

  const handleUpload = async (files: File[]) => {
    if (!files.length) return
    try {
      setStatus('Uploading...')
      await uploadDocuments(files, activeTag ? [activeTag] : undefined)
      setStatus('Upload complete.')
      await loadDocuments()
      await loadAllDocuments()
      await loadTags()
    } catch {
      setStatus('Upload failed.')
    }
  }

  const handleDrop = (files: File[]) => handleUpload(files)

  const handleSync = async () => {
    try {
      setStatus('Syncing...')
      const result = await syncDocuments()
      setStatus(`Sync complete. Added: ${result.added.length}, Removed: ${result.removed.length}`)
      await loadDocuments()
      await loadAllDocuments()
      await loadTags()
    } catch {
      setStatus('Sync failed.')
    }
  }

  const handleCreateTag = async (name: string) => {
    try {
      await createTag(name)
      await loadTags()
    } catch {
      setStatus('Failed to create tag.')
    }
  }

  const handleDeleteTag = async (name: string) => {
    try {
      await deleteTag(name)
      if (activeTag === name) setActiveTag(null)
      await loadTags()
      await loadDocuments()
      await loadAllDocuments()
    } catch {
      setStatus('Failed to delete tag.')
    }
  }

  const handleUpdate = async (id: string, data: { display_name?: string; tags?: string[] }) => {
    try {
      const updated = await updateDocument(id, data)
      setDocuments(prev => prev.map(d => d.id === id ? updated : d))
      setAllDocuments(prev => prev.map(d => d.id === id ? updated : d))
      if (selectedId === id) setSelectedDoc(updated)
      await loadTags()
    } catch {
      setStatus('Failed to update document.')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id)
      setDocuments(prev => prev.filter(d => d.id !== id))
      setAllDocuments(prev => prev.filter(d => d.id !== id))
      if (selectedId === id) { setSelectedId(null); setSelectedDoc(null) }
      setCheckedIds(prev => { const next = new Set(prev); next.delete(id); return next })
      await loadTags()
    } catch {
      setStatus('Failed to delete document.')
    }
  }

  if (loading) {
    return (
      <div className="document-manager">
        <h1>Documents</h1>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="document-manager">
      <h1>Documents</h1>
      <div className="document-manager-layout">
        <TagSidebar
          tags={tags}
          allDocuments={allDocuments}
          activeTag={activeTag}
          onSelectTag={setActiveTag}
          onCreateTag={handleCreateTag}
          onDeleteTag={handleDeleteTag}
          checkedIds={checkedIds}
          onCheckTag={handleCheckTag}
        />

        <div className="document-list-panel" data-testid="document-list-panel">
          <DocumentToolbar
            search={search}
            onSearchChange={setSearch}
            onUpload={handleUpload}
            onSync={handleSync}
            checkedCount={checkedIds.size}
            onAnalyze={handleAnalyze}
            extractionLoading={extractionLoading}
          />
          <DropZone onDrop={handleDrop} />
          {status && <div className="status-bar">{status}</div>}
          <DocumentList
            documents={documents}
            selectedId={selectedId}
            checkedIds={checkedIds}
            onSelect={handleSelectDoc}
            onCheck={handleCheck}
          />
        </div>

        {extractionResult ? (
          <ExtractionResultsPanel
            result={extractionResult}
            selection={extractionSelection}
            onToggle={handleToggle}
            onAccept={handleAccept}
            onReanalyze={handleAnalyze}
            onDismiss={handleDismiss}
          />
        ) : (
          <DocumentPreview
            document={selectedDoc}
            allTags={tags}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
          />
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/whweb/Code/haid-hunter && npx vitest run src/__tests__/documents/DocumentManager.test.tsx`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add src/components/documents/DocumentManager.tsx src/__tests__/documents/DocumentManager.test.tsx
git commit -m "feat: DocumentManager uses flat typed skills selection"
```

---

### Task 9: Update SkillChips to group by type

**Files:**
- Modify: `src/components/profile/SkillChips.tsx`

- [ ] **Step 1: Rewrite SkillChips**

Replace `src/components/profile/SkillChips.tsx` with:

```tsx
import type { TypedSkill } from '../../api/extraction'

export default function SkillChips({ skills }: { skills: TypedSkill[] }) {
  if (skills.length === 0) return <p>No skills added yet.</p>

  const grouped: Record<string, TypedSkill[]> = {}
  for (const s of skills) {
    if (!grouped[s.type]) grouped[s.type] = []
    grouped[s.type].push(s)
  }

  return (
    <div className="skill-chips">
      {Object.entries(grouped).map(([type, items]) => (
        <div key={type} className="skill-type-group">
          <h5 className="skill-type-heading">{type}</h5>
          <div className="skill-type-chips">
            {items.map((s, i) => (
              <span key={i} className="skill-chip">{s.name}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 2: Verify build compiles**

Run: `cd C:/Users/whweb/Code/haid-hunter && npx tsc --noEmit`
Expected: No type errors

- [ ] **Step 3: Commit**

```bash
git add src/components/profile/SkillChips.tsx
git commit -m "feat: SkillChips groups by skill type with headings"
```

---

### Task 10: Update SectionEditor skills section with type dropdown

**Files:**
- Modify: `src/components/profile/SectionEditor.tsx`

- [ ] **Step 1: Update the skills section in SectionEditor**

In `src/components/profile/SectionEditor.tsx`, update the `section === 'skills'` block (lines 141-161). The skills editor needs to handle `TypedSkill[]` objects with a type dropdown.

Add the import at the top of the file:
```typescript
import type { TypedSkill } from '../../api/extraction'
```

Replace the `if (section === 'skills')` block (lines 141-161) with:

```tsx
  if (section === 'skills') {
    const skills = value as TypedSkill[]
    const skillTypes = [
      "Programming Languages", "Frontend", "Backend", "Mobile",
      "Data & ML", "Databases", "Cloud Services", "DevOps & Infrastructure",
      "Security", "Testing & Quality", "Developer Tools", "Specialty",
      "Leadership & Management", "Interpersonal", "Problem Solving & Process",
    ]
    return (
      <div className="section-editor">
        <div className="editor-chips">
          {skills.map((s, i) => (
            <div key={i} className="editor-chip-row">
              <input
                value={s.name}
                onChange={e => { const next = [...skills]; next[i] = { ...s, name: e.target.value }; setValue(next) }}
                placeholder="Skill name"
                className="editor-chip-input"
              />
              <select
                value={s.type}
                onChange={e => { const next = [...skills]; next[i] = { ...s, type: e.target.value }; setValue(next) }}
                className="editor-type-select"
              >
                <option value="">Select type...</option>
                {skillTypes.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
              <button className="editor-remove" onClick={() => setValue(skills.filter((_, j) => j !== i))}>x</button>
            </div>
          ))}
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => setValue([...skills, { name: '', type: '' }])}>+ Add Skill</button>
        {actions}
      </div>
    )
  }
```

- [ ] **Step 2: Verify build compiles**

Run: `cd C:/Users/whweb/Code/haid-hunter && npx tsc --noEmit`
Expected: No type errors

- [ ] **Step 3: Commit**

```bash
git add src/components/profile/SectionEditor.tsx
git commit -m "feat: skills editor with type dropdown"
```

---

### Task 11: Run full test suite and fix any remaining issues

**Files:**
- All modified files

- [ ] **Step 1: Run all backend tests**

Run: `cd C:/Users/whweb/Code/haid-hunter && python -m pytest backend/tests/ -v`
Expected: PASS (all tests)

- [ ] **Step 2: Run all frontend tests**

Run: `cd C:/Users/whweb/Code/haid-hunter && npx vitest run`
Expected: PASS (all tests)

- [ ] **Step 3: Run TypeScript type check**

Run: `cd C:/Users/whweb/Code/haid-hunter && npx tsc --noEmit`
Expected: No errors

- [ ] **Step 4: Fix any failures**

If any tests or type checks fail, fix the issues. Common things to check:
- Any remaining references to `technologies` or `soft_skills` keys in test files
- Any remaining references to old `SelectionState` shape (nested `Record<string, Record<string, boolean>>`)
- Any remaining references to `skills: string[]` instead of `skills: TypedSkill[]`
- Import paths for `TypedSkill` type

- [ ] **Step 5: Final commit if fixes were needed**

```bash
git add -A
git commit -m "fix: resolve remaining typed skills integration issues"
```
