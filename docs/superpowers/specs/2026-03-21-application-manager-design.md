# Application Manager — Design Spec

## Overview

The Application Manager is the third feature of hAId-hunter. It allows users to create, view, and track the state of job applications. Applications are stored in a SQLite database with encrypted portal credentials. Users can toggle between a table view and a kanban board, link documents from the Document Manager to each application, and track referral contacts.

## Design Decisions

CLAUDE.md originally specified PostgreSQL for the Application Manager. During design, SQLite was chosen instead because this is a single-user, locally-hosted application. SQLite requires zero infrastructure and aligns with the project's philosophy of minimal setup. The schema remains the same and could be migrated to PostgreSQL later if needed.

## Dependencies

- Document Manager (for linking documents to applications via UUID)
- FastAPI backend (shared with Document Manager and Profile View)
- `cryptography` Python package (for credential encryption)
- `.env` file with `ENCRYPTION_KEY` (for Fernet symmetric encryption)

## Data Model

### Database

SQLite database at `./data/applications.db`. The `./data/` directory is gitignored. FastAPI creates the directory and database on startup if they do not exist.

### `applications` Table

| Column           | Type              | Description                                                              |
|------------------|-------------------|--------------------------------------------------------------------------|
| `id`             | INTEGER PRIMARY KEY | Auto-increment.                                                        |
| `company`        | TEXT NOT NULL      | Company name.                                                           |
| `position`       | TEXT NOT NULL      | Job title.                                                              |
| `posting_url`    | TEXT               | URL of the job listing.                                                 |
| `login_page_url` | TEXT               | URL of the company's applicant portal.                                  |
| `login_email`    | TEXT               | Email/username for the applicant portal (encrypted at rest).            |
| `login_password` | TEXT               | Password for the applicant portal (encrypted at rest).                  |
| `status`         | TEXT NOT NULL      | One of: `bookmarked`, `applied`, `in_progress`, `offer`, `closed`.      |
| `closed_reason`  | TEXT               | One of: `rejected`, `withdrawn`, `accepted`, `ghosted`. Null unless status is `closed`. |
| `has_referral`   | BOOLEAN DEFAULT FALSE | Whether the user has a referral for this application.                |
| `referral_name`  | TEXT               | Name of the referral contact.                                           |
| `notes`          | TEXT               | Free-text notes about the application.                                  |
| `created_at`     | DATETIME           | Timestamp when the application was created.                             |
| `updated_at`     | DATETIME           | Timestamp of the last modification.                                     |

### `application_documents` Table

| Column           | Type              | Description                                                              |
|------------------|-------------------|--------------------------------------------------------------------------|
| `id`             | INTEGER PRIMARY KEY | Auto-increment.                                                        |
| `application_id` | INTEGER NOT NULL   | Foreign key referencing `applications.id`. Cascade delete.              |
| `document_id`    | TEXT NOT NULL       | UUID from the Document Manager's `.metadata.json`.                      |
| `role`           | TEXT               | Purpose label: `resume`, `cover_letter`, or user-defined string.        |

### Encryption

Login credentials (`login_email`, `login_password`) are encrypted using `cryptography.fernet` with a symmetric key stored in `.env` as `ENCRYPTION_KEY`.

- On create/update: plaintext credentials are encrypted before writing to the database.
- On read: credentials are returned as `"***"` by default. The `reveal_credentials` query parameter triggers decryption.
- If `ENCRYPTION_KEY` is not set in `.env`, the backend generates one on first startup and writes it to `.env`.

## API Endpoints

All endpoints are prefixed with `/api`.

### Applications

| Method  | Path                                 | Description                                                                                     |
|---------|--------------------------------------|-------------------------------------------------------------------------------------------------|
| `GET`   | `/api/applications`                  | List all applications with metadata. Query params: `status` (filter), `search` (company/position substring), `has_referral` (boolean). |
| `GET`   | `/api/applications/{id}`             | Get a single application with linked documents. Credentials masked by default. Add `?reveal_credentials=true` to decrypt. |
| `POST`  | `/api/applications`                  | Create a new application. Accepts plaintext credentials; backend encrypts before storing.       |
| `PUT`   | `/api/applications/{id}`             | Update an application. Accepts plaintext credentials; backend re-encrypts.                      |
| `DELETE`| `/api/applications/{id}`             | Delete an application and its document links (cascade).                                         |
| `PATCH` | `/api/applications/{id}/status`      | Quick status update for kanban drag-and-drop. Body: `{ "status": "...", "closed_reason": "..." }`. |

### Document Linking

| Method  | Path                                          | Description                                              |
|---------|-----------------------------------------------|----------------------------------------------------------|
| `GET`   | `/api/applications/{id}/documents`             | List documents linked to an application.                 |
| `POST`  | `/api/applications/{id}/documents`             | Link a document. Body: `{ "document_id": "...", "role": "..." }`. |
| `DELETE`| `/api/applications/{id}/documents/{link_id}`   | Unlink a document from an application.                   |

### Response Format

Application list response includes linked document count. Single application response includes full linked document details (document UUID, original name from Document Manager metadata, and role).

## Frontend

### Routing

- `/applications` — Application Manager (added to the existing React Router config).

### UI Layout

Single page with a toolbar and a toggleable main view area.

**Toolbar:** Search input, status filter dropdown, "+ Add Application" button, table/kanban view toggle.

**Table View:** Full-width table with sortable columns: Company, Position, Status (color-coded badge), Referral (name badge or dash), Docs (count), Applied (date). Clicking a row opens the application modal in edit mode. Status bar at the bottom with total and per-status counts.

**Kanban View:** Five columns — Bookmarked, Applied, In Progress, Offer, Closed. Each column has a header with status badge and count. Cards show company, position, referral badge, date, and doc count. Closed cards are visually dimmed. Cards are draggable between columns; dropping triggers `PATCH /api/applications/{id}/status`. Clicking a card opens the application modal in edit mode.

**Application Modal:** Used for both creating and editing applications. Sections:

1. **Core info:** Company, Position (side by side), Posting URL.
2. **Status:** Status dropdown, referral checkbox, referral name input (shown when checkbox is checked).
3. **Portal Credentials:** Login page URL, email/username, password. Password field has a show/hide toggle.
4. **Linked Documents:** List of linked documents with role labels and remove buttons. "+ Link Document" button opens a document picker showing files from the Document Manager.
5. **Notes:** Free-text textarea.
6. **Footer:** Cancel and Save buttons.

### Components

| Component            | Responsibility                                                                          |
|----------------------|-----------------------------------------------------------------------------------------|
| `ApplicationManager` | Top-level. Manages application list state, view mode, filters, search.                  |
| `ApplicationToolbar` | Search input, status filter dropdown, Add button, view toggle.                          |
| `TableView`          | Table rendering with sortable columns. Row click opens modal.                           |
| `KanbanView`         | Column-based layout. Manages drag-and-drop state.                                       |
| `KanbanColumn`       | Single status column with header and card list. Drop target.                            |
| `KanbanCard`         | Individual application card. Drag source. Click opens modal.                            |
| `ApplicationModal`   | Add/edit form modal with all fields and sections.                                       |
| `DocumentLinker`     | Sub-component within the modal for linking/unlinking documents from the Document Manager.|
| `DocumentPicker`     | Dropdown or mini-modal listing available documents from the Document Manager for linking.|
| `StatusBadge`        | Reusable color-coded status pill component.                                             |

### Status Badge Colors

| Status       | Color                                    |
|--------------|------------------------------------------|
| Bookmarked   | Muted (gray) — `--color-muted`           |
| Applied      | Primary (blue) — `--color-primary`       |
| In Progress  | Accent (amber) — `--color-accent`        |
| Offer        | Success (green) — `--color-success`      |
| Closed       | Error (red) — `--color-error`            |

### Drag-and-Drop

Kanban drag-and-drop uses HTML5 Drag and Drop API (no external library). On drop:

1. Frontend optimistically updates the card's position.
2. Calls `PATCH /api/applications/{id}/status` with the new status.
3. If the new status is `closed`, prompts for a `closed_reason` before completing the drop.
4. On API failure, reverts the card to its original column.

## Design System

Follows the existing Slate Blue design system from `style/style-guide.md`:

- Table uses `--color-surface` background, `--color-elevated` for header row.
- Kanban columns use `--color-surface` background, cards use `--color-elevated`.
- Modal uses `--color-surface` background with `--color-border` borders.
- Form inputs use `--color-elevated` background, `--color-border` border, `--color-primary` on focus.
- Typography: Inter for all UI text.
- Icons: Lucide Icons.

## Testing Strategy

Test-driven development (TDD) throughout.

### Backend

- Unit tests for encryption/decryption of credentials.
- Unit tests for SQLite database operations (CRUD on applications and document links).
- Integration tests for all API endpoints using FastAPI test client with an in-memory SQLite database.
- Tests verify credential masking in default responses and decryption with `reveal_credentials=true`.
- Tests verify cascade delete behavior (deleting an application removes its document links).

### Frontend

- Component tests using React Testing Library.
- Tests for table view rendering, sorting, and row click behavior.
- Tests for kanban view rendering and card placement in correct columns.
- Tests for drag-and-drop status updates (mock API calls).
- Tests for application modal form validation and submission.
- Tests for document linker interactions.
- Tests for view toggle between table and kanban.
- API calls mocked in frontend tests.

## Out of Scope

- Automated status checking via browser automation (Phase II).
- Temporary email generation for applications (Phase II).
- Direct application submission (Phase III).
- Bulk operations (mass status update, mass delete).
- Application analytics or statistics dashboard.
- Export applications to CSV/spreadsheet.
