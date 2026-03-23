# Home Dashboard — Design Spec

## Overview

The Home Dashboard is the landing page of hAId-hunter. It gives the user an at-a-glance overview of their entire job-search state: profile summary, document inventory, application statistics, referral contacts, and a daily task checklist. No data entry happens here — it is a read-mostly page that links out to the detail pages.

## Design Decisions

- **Single aggregation endpoint** (`GET /api/dashboard`) — avoids the frontend making 4+ requests on mount. The backend queries documents, applications, profile, and tasks in one handler.
- **Tasks table in SQLite** — user-defined recurring and one-time tasks live alongside applications in `data/applications.db`. Built-in goals (e.g., "apply for N positions today") are computed from real application data, not stored.
- **Daily application target is configurable** — stored in a `settings` table (key-value) with a sensible default of 5.
- **Viewport containment** — the dashboard page itself never scrolls. Individual cards (especially Daily Tasks) scroll internally when content overflows, consistent with the app-wide `height: 100vh; overflow: hidden` pattern.
- **Pill badge style** for stat breakdowns — document types and application statuses use rounded pill badges inline within each card.

## Dependencies

- Document Manager (document counts by tag)
- Application Manager (application counts by status, referral list)
- Profile View (summary, skills, current role)
- FastAPI backend (shared with existing routers)
- Existing SQLite database at `./data/applications.db`

## Data Model

### `tasks` Table (new)

| Column         | Type                | Description                                                  |
|----------------|---------------------|--------------------------------------------------------------|
| `id`           | INTEGER PRIMARY KEY | Auto-increment.                                              |
| `title`        | TEXT NOT NULL        | Task description.                                            |
| `recurrence`   | TEXT                 | One of: `daily`, `weekly`, `custom`, or `null` (one-time).   |
| `interval_days`| INTEGER              | Effective repeat interval in days. `daily` = 1, `weekly` = 7, `custom` = user-defined N. Null for one-time tasks. |
| `completed_at` | DATETIME             | When the task was last completed. Null if never.             |
| `created_at`   | DATETIME             | Timestamp when the task was created.                         |

**Recurrence semantics:** All recurrence types map to an integer interval in days. `daily` implies `interval_days = 1`, `weekly` implies `interval_days = 7`, `custom` uses the user-supplied value. The `recurrence` column is a display hint; `interval_days` drives the scheduling logic.

**Completion and due-date logic:** A task is considered "due today" if:
- It has never been completed (`completed_at IS NULL`), OR
- It is recurring and `completed_at` is older than `interval_days` ago (i.e., `date(completed_at) + interval_days <= date('now')`)

A task is "completed today" if `date(completed_at) = date('now')`. One-time tasks with a non-null `completed_at` are never due again (they show as done permanently).

### `settings` Table (new)

| Column  | Type                | Description                          |
|---------|---------------------|--------------------------------------|
| `key`   | TEXT PRIMARY KEY     | Setting name.                        |
| `value` | TEXT NOT NULL        | Setting value (stored as string).    |

Seed row: `key = "daily_application_target"`, `value = "5"`.

### Database Migration

Add `CREATE TABLE IF NOT EXISTS tasks (...)` and `CREATE TABLE IF NOT EXISTS settings (...)` to the `SCHEMA` constant in `backend/services/database.py` alongside the existing `applications` and `application_documents` table definitions. Also add an `INSERT OR IGNORE` statement to seed the default `daily_application_target` setting.

## API

### `GET /api/dashboard`

Returns aggregated dashboard data in a single response.

**Computed fields:**
- `profile.current_role` — derived from the first experience entry in the profile with `end_date: null`. Formatted as `"{role} at {company} ({start_date} - Present)"`. If no current role exists, the field is `null`.
- `applications.referrals.contacts[]` — queried from the `applications` table directly: `SELECT id, referral_name, company FROM applications WHERE has_referral = 1`. The `application_id` in the response is the application's own `id`. There is no separate referrals table; referral data lives on the application row.
- `tasks.statuses_current` — `true` when no applications have `status` of `applied` or `in_progress` with `updated_at` older than 7 days. The `stale_count` field provides the number of applications needing a status update.
- `tasks.applied_today` — count of applications where `date(created_at) = date('now')` and `status != 'bookmarked'`. This counts applications created today in a non-bookmarked state. As a simplification, it does not track status transitions on existing applications.

**Response shape:**

```json
{
  "profile": {
    "summary": "Software Engineer with 8 years...",
    "skills": ["TypeScript", "React", "Python", "Node.js", "AWS", "Docker", "SQL"],
    "current_role": "Senior Developer at Acme Corp (2021 - Present)"
  },
  "documents": {
    "total": 12,
    "by_tag": {
      "resume": 5,
      "cover-letter": 4,
      "cv": 3
    }
  },
  "applications": {
    "total": 23,
    "by_status": {
      "bookmarked": 8,
      "applied": 5,
      "in_progress": 6,
      "offer": 2,
      "closed": 2
    },
    "referrals": {
      "total": 3,
      "contacts": [
        { "name": "Jane Smith", "company": "Google", "application_id": 7 },
        { "name": "Bob Lee", "company": "Meta", "application_id": 12 },
        { "name": "Alice Chen", "company": "Stripe", "application_id": 18 }
      ]
    }
  },
  "tasks": {
    "daily_target": 5,
    "applied_today": 2,
    "statuses_current": true,
    "stale_count": 0,
    "user_tasks": [
      {
        "id": 1,
        "title": "Review LinkedIn connections",
        "recurrence": "custom",
        "interval_days": 3,
        "is_due": true,
        "completed_today": false
      },
      {
        "id": 2,
        "title": "Tailor resume for Google SWE",
        "recurrence": null,
        "interval_days": null,
        "is_due": true,
        "completed_today": false
      }
    ]
  }
}
```

### `GET /api/tasks`

List all user-defined tasks.

### `POST /api/tasks`

Create a new task. Body: `{ "title": "...", "recurrence": "daily"|"weekly"|"custom"|null, "interval_days": N|null }`.

When `recurrence` is `daily`, the backend sets `interval_days = 1`. When `weekly`, the backend sets `interval_days = 7`. When `custom`, the client must provide `interval_days`. When `null`, `interval_days` is stored as null.

### `PATCH /api/tasks/{id}`

Update a task. Body (all fields optional):

```json
{
  "title": "...",
  "recurrence": "daily"|"weekly"|"custom"|null,
  "interval_days": N|null,
  "completed": true|false
}
```

When `completed: true`, the backend sets `completed_at` to the current UTC timestamp. When `completed: false`, the backend sets `completed_at` to null (un-completing a task).

### `DELETE /api/tasks/{id}`

Delete a task.

### `GET /api/settings/{key}`

Get a setting value. Returns `{ "key": "...", "value": "..." }`. Returns 404 if the key does not exist.

### `PUT /api/settings/{key}`

Set a setting value. Body: `{ "value": "..." }`. Upserts the row.

## Frontend Components

### File Structure

```
src/components/home/
  Dashboard.tsx          — Page-level component, fetches /api/dashboard, renders layout
  ProfileBanner.tsx      — Profile summary card
  StatCard.tsx           — Reusable stat card (documents, applications, referrals)
  DailyTasks.tsx         — Task checklist with built-in goals + user tasks
  ReferralPopover.tsx    — Popover showing referral contact details
  PlaceholderCard.tsx    — Phase II placeholder card with "Coming Soon" messaging
```

### Layout

The dashboard uses a single-column flex layout that fills the viewport (minus the navbar). All sections are stacked vertically:

1. **Profile Banner** — full width, fixed height
2. **Stats Row** — CSS grid, 3 equal columns: Documents, Applications, Referrals
3. **Bottom Row** — CSS grid, 2 equal columns: Daily Tasks (left), Phase II placeholder (right)

### Scrolling Behavior

- `.dashboard` container: `height: 100%; overflow: hidden` — no page-level scroll
- Each stat card and the Daily Tasks card: `overflow-y: auto` with `min-height: 0` on flex children so content scrolls within the card if it exceeds available height
- The bottom row gets `flex: 1; min-height: 0` so it fills remaining space and cards can scroll

### States

- **Loading**: The Dashboard component shows a centered loading spinner while `GET /api/dashboard` is in flight.
- **Error**: If the fetch fails, show an error message with a "Retry" button.
- **Empty profile**: ProfileBanner shows "Set up your profile to see a summary here" with a link to `/profile`.
- **Zero documents/applications**: StatCard shows the total as `0` with no pill badges and a subtle message: "No documents yet" / "No applications yet".
- **No user tasks**: DailyTasks shows only the two built-in goals. The user-defined section shows "+ Add Task" with a message: "No custom tasks yet."

### ProfileBanner

Displays:
- Profile summary text (first ~120 chars or first sentence)
- Top skills as pill badges (show first 3, then "+N more")
- Current role and dates

Data source: `dashboard.profile`

### StatCard (reusable)

Props: `title`, `total`, `subtitle`, `breakdowns: Array<{ label, count, color? }>`, optional `action` slot.

- Large number display for total
- Pill badges for each breakdown item
- Application status pills use existing CSS status color variables (bookmarked = `var(--color-muted)`, applied = `var(--color-secondary)`, in_progress = `var(--color-accent)`, offer = `var(--color-success)`, closed = `var(--color-error)`)
- Document tag pills use `var(--color-secondary)` for all tags

### Referrals StatCard

Same StatCard layout for total count, plus:
- "View all referrals" link that opens a popover
- Popover lists each referral: name, company (joined from the parent application), and a link to the application detail

### DailyTasks

Two sections:

**Built-in goals** (computed, not stored):
1. "Apply for positions" — shows `applied_today` of `daily_target`, status pill: done (green) if met, in progress (amber) if partially done, pending (muted) if 0
2. "Update application statuses" — shows "All statuses current" when `statuses_current` is true, or "{stale_count} need update" when false

**User-defined tasks:**
- Each task row: checkbox, title, subtitle (recurrence info), status pill (recurring/one-time/done)
- Completed tasks show strikethrough + reduced opacity
- "+ Add Task" button in the header opens inline form or small modal
- Task recurrence options: daily, weekly, custom (every N days), or one-time (no recurrence)

### PlaceholderCard

Renders a dashed-border card with centered content:
- Section header: "Phase II"
- Title: "Next Steps"
- Subtitle: "Claude-driven suggestions"

Uses muted text and dashed border to distinguish from active cards.

### Routing

- Add `/home` route to `App.tsx` pointing to the `Dashboard` component.
- Change the default redirect from `/documents` to `/home`.
- Add a "Home" NavLink to `NavBar.tsx` as the first navigation item, linking to `/home`.

## Styling

All styles follow the existing design system in `src/index.css`:
- Card background: `var(--bg-secondary)`
- Card border: `1px solid var(--border-color)`
- Card border-radius: `12px`
- Section headers: `11px`, uppercase, `letter-spacing: 0.05em`, `var(--color-muted)`
- Pill badges: `border-radius: 999px`, `padding: 3px 10px`, `font-size: 11-12px`
- Status colors: use existing CSS variables (`--color-muted`, `--color-secondary`, `--color-accent`, `--color-success`, `--color-error`)

## Testing Strategy

- **Backend**: Test the `/api/dashboard` endpoint returns correct aggregated data. Test task due-date logic (never completed, completed today, completed N days ago for recurring). Test CRUD for tasks and settings. Test `statuses_current` computation with fresh and stale applications.
- **Frontend**: Test each component renders correct data from props. Test DailyTasks checkbox toggles. Test ReferralPopover opens/closes. Test loading, error, and empty states. Test that the dashboard fetches data on mount.
