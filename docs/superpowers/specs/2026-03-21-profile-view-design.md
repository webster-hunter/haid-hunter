# Profile View — Design Spec

## Overview

The Profile View is the second feature of hAId-hunter. It provides a structured breakdown of the user's candidate profile — skills, experience, education, certifications, summary, and objectives. A Claude-driven interview chat helps the user build and refine their profile by reviewing their uploaded documents and asking targeted follow-up questions.

## Dependencies

- Document Manager (for reading uploaded documents during the interview)
- FastAPI backend (shared with Document Manager)
- Claude API (for interview functionality)

## Data Model

Profile stored at `./documents/.profile.json` — a dotfile in the documents directory, not tracked in document metadata.

```json
{
  "summary": "Senior full-stack engineer with 6 years of experience...",
  "skills": [
    { "name": "TypeScript", "proficiency": "advanced", "category": "technical" },
    { "name": "Leadership", "proficiency": "intermediate", "category": "soft" }
  ],
  "experience": [
    {
      "company": "Acme Corp",
      "role": "Senior Full-Stack Engineer",
      "start_date": "2023-01",
      "end_date": null,
      "accomplishments": [
        "Led migration to microservices architecture",
        "Reduced API response times by 60%"
      ]
    }
  ],
  "education": [
    {
      "institution": "State University",
      "degree": "B.S. Computer Science",
      "start_date": "2015-08",
      "end_date": "2019-05"
    }
  ],
  "certifications": [
    { "name": "AWS Solutions Architect", "issuer": "Amazon", "date": "2024-06" }
  ],
  "objectives": "Looking for senior/staff engineering roles at mid-size companies..."
}
```

### Field Definitions

- `summary`: free text professional summary / elevator pitch.
- `skills`: array of objects with `name` (string), `proficiency` (enum: beginner, intermediate, advanced, expert), and `category` (enum: technical, soft).
- `experience`: array of objects with `company` (string), `role` (string), `start_date` (string, YYYY-MM), `end_date` (string or null for current), `accomplishments` (array of strings).
- `education`: array of objects with `institution` (string), `degree` (string), `start_date` (string, YYYY-MM), `end_date` (string, YYYY-MM).
- `certifications`: array of objects with `name` (string), `issuer` (string), `date` (string, YYYY-MM).
- `objectives`: free text string. This is the only freeform section — the user writes whatever they want about target roles, career direction, and preferences.

### Initialization

On first access (`GET /api/profile` with no existing file), the backend creates an empty scaffold with all sections present but empty (empty strings, empty arrays).

## API Endpoints

### Profile

| Method  | Path                       | Description                                                       |
|---------|----------------------------|-------------------------------------------------------------------|
| `GET`   | `/api/profile`             | Get the full profile. Returns empty scaffold if none exists.      |
| `PUT`   | `/api/profile`             | Replace the full profile (for manual edits).                      |
| `PATCH` | `/api/profile/{section}`   | Update a single section. `section` is one of: `summary`, `skills`, `experience`, `education`, `certifications`, `objectives`. Body contains the section data only. |

### Interview

| Method  | Path                        | Description                                                                                         |
|---------|-----------------------------|-----------------------------------------------------------------------------------------------------|
| `POST`  | `/api/interview/start`      | Start a new interview session. Backend reads documents and current profile, sends to Claude, returns opening message and `session_id`. |
| `POST`  | `/api/interview/message`    | Send a user message. Body: `{ "session_id": "...", "message": "..." }`. Returns Claude's response and optional `suggestion` object. |
| `POST`  | `/api/interview/accept`     | Accept a suggestion. Body: `{ "session_id": "...", "suggestion_id": "..." }`. Applies change to profile, returns updated section. |
| `POST`  | `/api/interview/reject`     | Reject a suggestion. Body: `{ "session_id": "...", "suggestion_id": "..." }`. Claude acknowledges on next message. |

### Interview Backend Flow

1. **Start:** Reads all previewable documents (TXT, MD, CSV, and extracted text from PDF). Reads current profile. Builds a system prompt containing document content and profile state. Sends to Claude API. Stores conversation history in an in-memory Python dict keyed by `session_id`. Returns Claude's opening message.

2. **Message:** Appends user message to conversation history. Calls Claude API. Parses response for structured suggestions (Claude is prompted to emit suggestions as JSON within its response). Returns the chat message text and any suggestion object.

3. **Accept:** Updates the relevant section of `./documents/.profile.json`. Stores the acceptance in session state so Claude is informed on the next message.

4. **Reject:** Stores the rejection in session state so Claude is informed on the next message.

### Session Management

- Sessions stored in an in-memory Python dict on the FastAPI server.
- Keyed by a generated `session_id` (UUID).
- Sessions expire naturally when the server restarts or the browser is closed.
- No persistence across server restarts — this is intentional (session-based chat).

### Suggestion Object Format

```json
{
  "suggestion_id": "sug_abc123",
  "section": "experience",
  "action": "update",
  "target": { "company": "Acme Corp", "field": "accomplishments", "index": 0 },
  "original": "Led migration of monolithic Rails app to microservices (Node.js + React)",
  "proposed": "Led a team of 6 engineers in decomposing a monolithic Rails application into 12 microservices over 8 months, mentoring 4 junior developers throughout the process"
}
```

- `action`: one of `add`, `update`, `remove`.
- `target`: identifies where in the section the change applies. Structure varies by section.
- `original`: the current value (null for `add`).
- `proposed`: the new value (null for `remove`).

## Frontend

### Routing

- `/profile` — Profile View (added to the existing React Router config alongside `/documents`).

### UI Layout

Split-pane layout:

1. **Left: Profile panel (flexible width)** — scrollable list of profile sections. Each section has a header with title and Edit button. Sections render their content in structured, readable format.
2. **Right: Interview chat (420px, collapsible)** — Claude conversation with suggestion cards inline. Collapse button hides the chat to give the profile full width.

When collapsed, the chat panel reduces to a narrow strip (~48px) with an expand button.

### Components

| Component            | Responsibility                                                                          |
|----------------------|-----------------------------------------------------------------------------------------|
| `ProfileView`        | Top-level layout. Manages chat collapsed/expanded state.                                |
| `ProfilePanel`       | Scrollable container of profile sections.                                               |
| `ProfileSection`     | Generic section wrapper with title and Edit button. Toggles between view and edit mode. |
| `SkillChips`         | Renders skills as chips with proficiency level badges and category labels.               |
| `ExperienceList`     | Renders work experience entries with role, company, dates, accomplishments.              |
| `EducationList`      | Renders education entries with degree, institution, dates.                               |
| `CertificationList`  | Renders certification entries with name, issuer, date.                                  |
| `SectionEditor`      | Inline editor for manually editing a section's data. Submits via `PATCH /api/profile/{section}`. |
| `InterviewChat`      | Chat panel with message history, input area, and collapsible state.                     |
| `ChatMessage`        | Individual message bubble styled for user or assistant.                                 |
| `SuggestionCard`     | Inline card showing proposed profile update with Accept and Reject buttons.             |

### Interview-Driven Questions

Claude's system prompt instructs it to:

1. Review the user's documents and current profile state.
2. Identify gaps, vague descriptions, and missing quantifiable details.
3. Ask targeted questions that help refine resume and cover letter content — e.g., "Can you quantify the impact of X?", "What technologies did you use for Y?", "What was the team size?"
4. Generate freeform follow-up questions derived from the user's documented skills and experience.
5. Propose structured suggestions (add/update/remove) based on the user's answers.
6. Respect accept/reject decisions and adjust follow-up questions accordingly.

### Skill Proficiency Display

| Level         | Badge Color                    |
|---------------|--------------------------------|
| Beginner      | Default / muted                |
| Intermediate  | Accent (amber)                 |
| Advanced      | Success (green)                |
| Expert        | Secondary (blue)               |

### Edit Mode

Each section's Edit button toggles the section into an inline editor:

- **Summary / Objectives:** Text area.
- **Skills:** Editable list with add/remove. Each skill has name input, proficiency dropdown, category dropdown.
- **Experience:** Editable entries with inputs for company, role, dates, and a dynamic list of accomplishment text fields.
- **Education:** Editable entries with inputs for institution, degree, dates.
- **Certifications:** Editable entries with inputs for name, issuer, date.

Save and Cancel buttons at the bottom of each section editor. Save calls `PATCH /api/profile/{section}`.

## Design System

Follows the existing Slate Blue design system from `style/style-guide.md`:

- Profile sections use card styling (`--color-surface` background, `--color-border` border, `lg` radius).
- Chat panel uses the same card styling.
- Suggestion cards use `--color-accent` border to stand out.
- Skill chips use `--color-elevated` background with proficiency-colored badges.
- Chat messages: assistant messages use `--color-elevated`, user messages use `--color-primary`.
- Typography: Inter for all UI text.
- Icons: Lucide Icons.

## Testing Strategy

Test-driven development (TDD) throughout.

### Backend

- Unit tests for profile JSON read/write/patch operations.
- Unit tests for session management (create, retrieve, expire).
- Integration tests for profile CRUD endpoints using FastAPI test client.
- Integration tests for interview endpoints with mocked Claude API responses.
- Document reading tested against fixture files in a temporary directory.

### Frontend

- Component tests using React Testing Library.
- Tests for profile section rendering (each section type).
- Tests for edit mode toggle and form submission.
- Tests for chat message rendering and suggestion card interactions (accept/reject).
- Tests for chat collapse/expand state.
- API calls mocked in frontend tests.

## Out of Scope

- Persistent chat history across server restarts.
- Multiple user profiles.
- AI-generated profile from scratch (without documents).
- Export profile to PDF/DOCX.
- Integration with Application Manager (separate spec).
