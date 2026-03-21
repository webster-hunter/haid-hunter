# Document Manager — Design Spec

## Overview

The Document Manager is the first feature of hAId-hunter, a locally-hosted job application tool. It allows users to manage a knowledge base of career documents (resumes, cover letters, CVs, etc.) that will later be referenced by agents to tailor application materials to job postings.

## Architecture

- **Frontend:** React SPA (Vite + TypeScript) with React Router. Lazy-loaded routes for future features (Profile View, Application Manager).
- **Backend:** FastAPI (Python) serving REST endpoints and static files.
- **Storage:** Local filesystem — flat directory with a JSON metadata file. No database required for this feature.

## Design Decisions

CLAUDE.md originally described documents organized via sub-directories per type. During design, metadata-based tagging was chosen instead to support multi-tag per file. This spec supersedes the sub-directory approach described in CLAUDE.md.

## File Storage

All documents are stored in `./documents/` at the project root.

- The directory is gitignored.
- FastAPI creates the directory on startup if it does not exist.
- Files are stored as `<uuid>_<original-filename>` to prevent name collisions.
- Supported formats: PDF, DOCX, TXT, MD, XLSX, CSV, PPTX.
- Image files are not supported.
- Maximum upload size: 50 MB per file.

## Metadata

A single `./documents/.metadata.json` file tracks all document metadata.

```json
{
  "files": {
    "a1b2c3d4": {
      "original_name": "resume-2024.pdf",
      "stored_name": "a1b2c3d4_resume-2024.pdf",
      "display_name": "resume-2024.pdf",
      "tags": ["resume", "engineering"],
      "uploaded_at": "2026-03-21T10:30:00Z",
      "size_bytes": 245000,
      "mime_type": "application/pdf"
    }
  },
  "tags": ["resume", "cover-letter", "cv"]
}
```

- `files`: map keyed by UUID. Each entry tracks the original filename, stored filename (with UUID prefix), a user-editable display name (defaults to original name), assigned tags, upload timestamp, file size in bytes, and MIME type.
- `tags`: array of all known tags. Seeded with defaults (`resume`, `cover-letter`, `cv`) on first run. Users can add custom tags.

### File System Sync

On startup and on manual trigger, FastAPI scans the `./documents/` directory:

- Files on disk but not in metadata are added with no tags, with size and MIME type detected automatically.
- Files in metadata but missing from disk are removed from metadata.

## API Endpoints

All endpoints are prefixed with `/api`.

### Documents

| Method   | Path                               | Description                                                                 |
|----------|------------------------------------|-----------------------------------------------------------------------------|
| `GET`    | `/api/documents`                   | List all documents with metadata. Query params: `tag` (filter), `search` (filename substring). |
| `GET`    | `/api/documents/{id}`        | Get metadata for a single document.                                         |
| `GET`    | `/api/documents/{id}/content`| Serve raw file content with appropriate `Content-Type` header.              |
| `POST`   | `/api/documents/upload`            | Upload one or more files. Accepts `multipart/form-data` with optional `tags` field. |
| `PUT`    | `/api/documents/{id}`        | Update metadata (display name, tags). Uploads are serialized to prevent concurrent writes to `.metadata.json`. |
| `DELETE` | `/api/documents/{id}`        | Delete file from disk and remove from metadata.                             |
| `POST`   | `/api/documents/sync`              | Trigger file system scan to discover new files and remove stale entries.     |

### Tags

| Method   | Path                    | Description                                              |
|----------|-------------------------|----------------------------------------------------------|
| `GET`    | `/api/tags`             | List all tags.                                           |
| `POST`   | `/api/tags`             | Create a new tag.                                        |
| `DELETE` | `/api/tags/{tag}`       | Delete a tag and remove it from all files.               |

### Cross-Cutting Concerns

- CORS enabled for the Vite dev server origin (`http://localhost:5173`).
- Upload endpoint assigns a UUID prefix, detects MIME type, writes to disk, and updates `.metadata.json`.
- Content endpoint sets `Content-Type` and `Content-Disposition` headers for preview and download.

## Frontend

### Routing

React Router with lazy-loaded routes:

- `/` — Home / landing (future)
- `/documents` — Document Manager
- `/profile` — Profile View (future)
- `/applications` — Application Manager (future)

### UI Layout

Three-panel layout:

1. **Left sidebar (240px):** Tag filter list with document counts per tag. "All Documents" option at top. "+ New Tag" button at bottom. Clicking a tag filters the file list.
2. **Center panel (flexible):** Toolbar (search input, Upload button, Sync button), drag-and-drop zone, scrollable document list, status bar.
3. **Right panel (400px):** Preview pane showing file content or file info, file metadata, editable tags (add/remove), and action buttons (Download, Open External, Delete).

### Components

| Component          | Responsibility                                                                 |
|--------------------|--------------------------------------------------------------------------------|
| `DocumentManager`  | Top-level layout. Manages selected file and active tag filter state.           |
| `TagSidebar`       | Renders tag list with counts. Handles tag selection and tag CRUD.              |
| `DocumentToolbar`  | Search input, Upload button (opens file picker), Sync button.                  |
| `DropZone`         | Drag-and-drop file upload area. Visual feedback on drag-over.                  |
| `DocumentList`     | Scrollable list of `DocumentItem` components. Filtered by active tag/search.   |
| `DocumentItem`     | Single file row: type icon, filename, size, date, tag badges.                  |
| `DocumentPreview`  | Right panel. Renders content for previewable types, file info for others.       |
| `TagBadge`         | Reusable tag pill component.                                                   |

### Document Preview

| Format       | Preview Method                                      |
|--------------|-----------------------------------------------------|
| PDF          | Embedded via `<iframe>` or `<object>` tag            |
| TXT          | Rendered as plain text in a `<pre>` block            |
| MD           | Rendered as HTML using a markdown library             |
| CSV          | Parsed and rendered as an HTML table                  |
| DOCX         | File info card with Download and Open External buttons|
| PPTX         | File info card with Download and Open External buttons|
| XLSX         | File info card with Download and Open External buttons|

### Upload Flow

1. User drags files onto the drop zone or clicks Upload to open a file picker.
2. Frontend sends files as `multipart/form-data` to `POST /api/documents/upload`.
3. Backend assigns UUID prefix, detects MIME type, writes file to `./documents/`, updates `.metadata.json`.
4. Frontend refreshes the document list.
5. User can then add tags to the uploaded files via the preview panel.

## Design System

The UI follows the existing Slate Blue design system defined in `style/style-guide.md`. Key tokens:

- Backgrounds: `--color-bg` (page), `--color-surface` (cards/panels), `--color-elevated` (inputs/dropdowns)
- Text: `--color-text` (body), `--color-muted` (secondary)
- Interactive: `--color-primary` (buttons/links), `--color-secondary` (badges/tags)
- Feedback: `--color-success`, `--color-error`, `--color-accent`
- Typography: Inter for UI, JetBrains Mono for code/file content
- Icons: Lucide Icons, 20px default, 1.5 stroke width

## Testing Strategy

Test-driven development (TDD) throughout. Tests written before implementation.

### Backend (FastAPI)

- Unit tests for metadata read/write operations.
- Unit tests for file system sync logic.
- Integration tests for each API endpoint using FastAPI's test client.
- File system operations tested against a temporary directory.

### Frontend (React)

- Component tests using React Testing Library.
- Tests for tag filtering, search filtering, file selection state.
- Tests for upload flow (mock API calls).
- Tests for preview rendering per file type.

## Out of Scope

- Cloud storage or remote file systems.
- Full-fidelity rendering of DOCX, PPTX, or XLSX in the browser.
- User authentication or multi-user support.
- Profile View and Application Manager features (separate specs).
- Phase II and Phase III features (Next Steps, Seeker).
