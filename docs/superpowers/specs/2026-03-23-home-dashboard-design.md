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
| `interval_days`| INTEGER              | For `custom` recurrence — repeat every N days. Null otherwise.|
| `completed_at` | DATETIME             | When the task was last completed. Null if never.             |
| `created_at`   | DATETIME             | Timestamp when the task was created.                         |

### `settings` Table (new)

| Column  | Type                | Description                          |
|---------|---------------------|--------------------------------------|
| `key`   | TEXT PRIMARY KEY     | Setting name.                        |
| `value` | TEXT NOT NULL        | Setting value (stored as string).    |

Seed row: `key = "daily_application_target"`, `value = "5"`.

## API

### `GET /api/dashboard`

Returns aggregated dashboard data in a single response.

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

### `PATCH /api/tasks/{id}`

Update a task (title, recurrence, or mark completed).

### `DELETE /api/tasks/{id}`

Delete a task.

### `GET /api/settings/{key}`

Get a setting value.

### `PUT /api/settings/{key}`

Set a setting value. Body: `{ "value": "..." }`.

## Frontend Components

### File Structure

```
src/components/home/
  Dashboard.tsx          — Page-level component, fetches /api/dashboard, renders layout
  ProfileBanner.tsx      — Profile summary card
  StatCard.tsx           — Reusable stat card (documents, applications, referrals)
  DailyTasks.tsx         — Task checklist with built-in goals + user tasks
  ReferralPopover.tsx    — Popover showing referral contact details
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
- Application status pills use existing status colors (bookmarked=muted, applied=blue, in_progress=amber, offer=green, closed=red)
- Document tag pills use the secondary/chip color

### Referrals StatCard

Same StatCard layout for total count, plus:
- "View all referrals" link that opens a popover
- Popover lists each referral: name, company, links to the application

### DailyTasks

Two sections:

**Built-in goals** (computed, not stored):
1. "Apply for positions" — shows `applied_today` of `daily_target`, status pill: done (green) if met, in progress (amber) if partially done, pending (muted) if 0
2. "Update application statuses" — shows "All statuses current" or count needing update

**User-defined tasks:**
- Each task row: checkbox, title, subtitle (recurrence info), status pill (recurring/one-time/done)
- Completed tasks show strikethrough + reduced opacity
- "+ Add Task" button in the header opens inline form or small modal
- Task recurrence options: daily, weekly, custom (every N days), or one-time (no recurrence)

### Routing

Add `/home` route to `App.tsx` and change the default redirect from `/documents` to `/home`.

## Styling

All styles follow the existing design system in `src/index.css`:
- Card background: `var(--bg-secondary)` / `#161B2E`
- Card border: `1px solid var(--border-color)` / `#2E3F5C`
- Card border-radius: `12px`
- Section headers: `11px`, uppercase, `letter-spacing: 0.05em`, muted color
- Pill badges: `border-radius: 999px`, `padding: 3px 10px`, `font-size: 11-12px`
- Status colors: bookmarked `#6B7FA3`, applied `#7B93D4`, in_progress `#F59E0B`, offer `#10B981`, closed `#EF4444`

## Testing Strategy

- **Backend**: Test the `/api/dashboard` endpoint returns correct aggregated data. Test CRUD for tasks and settings.
- **Frontend**: Test each component renders correct data from props. Test DailyTasks checkbox toggles. Test ReferralPopover opens/closes. Test that the dashboard fetches data on mount and displays loading/error states.
