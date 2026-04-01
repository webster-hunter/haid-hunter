# Typed Skills Restructuring

## Goal

Replace the three flat keyword sets (`SKILLS_LIST`, `TECHNOLOGIES_LIST`, `SOFT_SKILLS_LIST`) with a single unified dictionary where every skill has a name and a type. Use the type to group skills in both the extraction panel and the profile page.

## Architecture

The master skill data moves to a new file `backend/services/skill_definitions.py`. It exports a single `SKILLS` dict (name → type) and an ordered `SKILL_TYPES` list. The extraction service (`nlp_extraction.py`) imports from it and builds one PhraseMatcher instead of three. The API, profile storage, and both frontend panels all speak in `{name, type}` objects.

## Consolidated Skill Types (15)

| # | Type | Absorbs |
|---|---|---|
| 1 | Programming Languages | Programming Languages |
| 2 | Frontend | Frontend Frameworks / Libraries, Frontend Styling |
| 3 | Backend | Backend Frameworks, API Standards and Protocols |
| 4 | Mobile | Mobile Development |
| 5 | Data & ML | Data Science / Analytics, Machine Learning / AI, Data Engineering, Analytics / BI, AI / ML Platforms |
| 6 | Databases | Databases – Concepts, Relational Databases, NoSQL Databases, Data Warehouses / OLAP |
| 7 | Cloud Services | Cloud Providers, AWS Services, Azure Services, GCP Services, Cloud Architecture — Strategies & Patterns |
| 8 | DevOps & Infrastructure | DevOps / Development Practices, CI/CD Platforms, Containers and Orchestration, Infrastructure as Code, Monitoring / Logging / Observability, Service Mesh / API Gateway / Networking, CDN / Edge, Storage Services, Data Pipeline / ETL / ELT, Operating Systems / Infrastructure |
| 9 | Security | Security, Security Platforms |
| 10 | Testing & Quality | Testing, Testing / Quality Platforms |
| 11 | Developer Tools | Build Tools / Bundlers / Package Managers, Version Control, VCS Hosting / Artifact Registries, IDEs and Development Environments, Documentation, Design Tools |
| 12 | Specialty | Game Development, Embedded / Systems, Accessibility, Blockchain / Web3, Low-Code / No-Code / Business Platforms, Communication / Collaboration (tools) |
| 13 | Leadership & Management | Leadership, Project Management, Strategy and Vision, Influence and Persuasion |
| 14 | Interpersonal | Communication, Team Collaboration, Customer / Client Skills, Teaching / Mentoring, Emotional Intelligence, Diversity Equity and Inclusion, Professional Skills |
| 15 | Problem Solving & Process | Problem Solving / Analytical, Organizational / Planning Skills, Agile / Process Skills, Business Skills, Personal Effectiveness |

## Data Structures

### Master skill dict (`backend/services/skill_definitions.py`)

New file containing only data — no logic.

```python
SKILL_TYPES: list[str] = [
    "Programming Languages", "Frontend", "Backend", "Mobile",
    "Data & ML", "Databases", "Cloud Services", "DevOps & Infrastructure",
    "Security", "Testing & Quality", "Developer Tools", "Specialty",
    "Leadership & Management", "Interpersonal", "Problem Solving & Process",
]

SKILLS: dict[str, str] = {
    "Python": "Programming Languages",
    "React": "Frontend",
    "FastAPI": "Backend",
    "AWS": "Cloud Services",
    "communication": "Interpersonal",
    # ... ~900 entries, one per skill, deduped
}
```

Cross-list duplicates are resolved: each skill appears exactly once with its most appropriate type.

### Extraction output

Single key, typed objects:

```python
{"skills": [{"name": "Python", "type": "Programming Languages"}, ...]}
```

Replaces the old three-key format (`skills`, `technologies`, `soft_skills`).

### Profile storage (`.profile.json`)

```json
{
  "skills": [
    {"name": "Python", "type": "Programming Languages"},
    {"name": "React", "type": "Frontend"}
  ]
}
```

### Frontend TypeScript types

```typescript
interface TypedSkill { name: string; type: string }
interface ExtractionResult { skills: TypedSkill[] }
interface Profile { skills: TypedSkill[]; /* ...rest unchanged */ }
```

### SelectionState

Changes from `Record<string, Record<string, boolean>>` (category → name → bool) to `Record<string, boolean>` (name → bool). Category key is no longer needed since there is only one flat list.

## API Changes

### `POST /api/extraction/analyze`

Response body changes to:
```json
{"skills": [{"name": "Python", "type": "Programming Languages"}, ...]}
```

### `POST /api/extraction/accept`

Request body changes to:
```json
{"skills": [{"name": "Python", "type": "Programming Languages"}, ...]}
```

### `GET /api/profile`, `PUT /api/profile`, `PATCH /api/profile/skills`

The `skills` field becomes `TypedSkill[]` (array of `{name, type}` objects) instead of `string[]`. Backend validates that each object has a `name` (string) and `type` (string, must be in `SKILL_TYPES`).

### `GET /api/skills/types` (new)

Returns the ordered `SKILL_TYPES` list so the frontend does not hardcode it.

## Backend Changes

### `nlp_extraction.py`

- Imports `SKILLS` and `SKILL_TYPES` from `skill_definitions.py`
- Deletes `SKILLS_LIST`, `TECHNOLOGIES_LIST`, `SOFT_SKILLS_LIST`
- Builds one `PhraseMatcher` from `SKILLS.keys()` instead of three
- `extract_from_documents` returns `{"skills": [{"name": ..., "type": ...}, ...]}` — looks up type via `SKILLS[matched_name]`
- Functions `extract_skills`, `extract_technologies`, `extract_soft_skills` are replaced by a single `extract_skills` that returns typed objects

### `extraction.py` (router)

- `AcceptSuggestionsRequest` changes to `skills: list[TypedSkillModel]`
- `merge_suggestions` merges typed skill objects, deduplicating by name (case-insensitive)

### `profile.py` (router + service)

- `ProfileRequest.skills` changes from `list[str]` to `list[TypedSkillModel]` where `TypedSkillModel` has `name: str` and `type: str` with validation against `SKILL_TYPES`
- `ProfileService.get()` auto-migrates: if skills on disk are plain strings, looks each up in the master dict and returns typed objects

### Profile migration

Transparent, on-read migration in `ProfileService.get()`:
1. Read `.profile.json`
2. If `skills` contains strings, convert each: look up in `SKILLS` dict → `{"name": skill, "type": SKILLS.get(skill)}`
3. Skills not found in the dict are dropped (the user can re-add them with a type via the profile page)
4. On next write, typed format is persisted

## Frontend Changes

### Extraction Panel (`ExtractionResultsPanel.tsx`)

- Removes hardcoded `CATEGORIES` constant
- Groups chips dynamically by `skill.type`, rendering a section with heading per type
- Toggle/select behavior unchanged — just grouped by type instead of the old three-bucket split

### Document Manager (`DocumentManager.tsx`)

- Removes `CATEGORIES` constant
- `handleAnalyze`: initializes `SelectionState` as `Record<string, boolean>` keyed by skill name
- `handleAccept`: builds typed skill list from selection, calls `patchSection('skills', ...)`
- `handleToggle`: simplified — just `(name: string)` instead of `(category, name)`

### Profile Page — Skills Section

- Groups chips by type with section headings (same visual treatment as extraction panel)
- Add-skill UI: text input for name + dropdown for type (populated from `GET /api/skills/types`)
- Type is required — user must select one

### `src/api/extraction.ts`

```typescript
interface TypedSkill { name: string; type: string }
interface ExtractionResult { skills: TypedSkill[] }
```

### `src/api/profile.ts`

```typescript
interface Profile { skills: TypedSkill[]; /* ...rest unchanged */ }
```

## Files Changed

| File | Change |
|---|---|
| `backend/services/skill_definitions.py` | **New** — master `SKILLS` dict + `SKILL_TYPES` list |
| `backend/services/nlp_extraction.py` | Delete three keyword sets, import from skill_definitions, single matcher, return typed objects |
| `backend/services/extraction.py` | Update `merge_suggestions` for typed skills |
| `backend/routers/extraction.py` | Update request/response models |
| `backend/routers/profile.py` | Update `ProfileRequest.skills` validation, add `/api/skills/types` endpoint |
| `backend/services/profile.py` | Add on-read migration for untyped skills |
| `src/api/extraction.ts` | Update `ExtractionResult` interface |
| `src/api/profile.ts` | Update `Profile` interface, add `fetchSkillTypes` |
| `src/components/documents/ExtractionResultsPanel.tsx` | Group by type dynamically |
| `src/components/documents/DocumentManager.tsx` | Simplify selection state, remove CATEGORIES |
| `src/components/profile/SkillChips.tsx` | Group by type with headings, add-skill form with type dropdown |
| Tests | All extraction and profile tests updated for typed format |
