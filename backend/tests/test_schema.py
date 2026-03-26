from backend.services.schema import generate_profile_schema


def test_schema_includes_all_sections():
    schema = generate_profile_schema()
    assert "summary: string" in schema
    assert "skills: string[]" in schema
    assert "experience:" in schema
    assert "education:" in schema
    assert "certifications:" in schema
    assert "activities:" in schema
    assert "objectives: string[]" in schema


def test_schema_includes_experience_fields():
    schema = generate_profile_schema()
    assert "company: string" in schema
    assert "role: string" in schema
    assert "start_date:" in schema
    assert "end_date:" in schema
    assert "accomplishments: string[]" in schema


def test_schema_includes_activity_fields():
    schema = generate_profile_schema()
    assert "name: string" in schema
    assert "category: string" in schema
    assert "details: string[]" in schema


def test_schema_includes_education_fields():
    schema = generate_profile_schema()
    assert "institution: string" in schema
    assert "degree: string" in schema
    assert "field:" in schema


def test_schema_includes_certification_fields():
    schema = generate_profile_schema()
    assert "issuer: string" in schema
    assert "date:" in schema
