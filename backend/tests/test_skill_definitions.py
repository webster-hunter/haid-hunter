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
