# Claude Code SDK Integration

## Summary

Replace the direct `anthropic` Python SDK usage with a TypeScript sidecar service powered by `@anthropic-ai/claude-agent-sdk`. This eliminates separate API key management and billing, enables agentic tool use (file reading, web fetching), and uses the existing Claude Code subscription for all LLM calls.

## Architecture

```
Browser (React) --> FastAPI (Python :8000) --> Claude Service (Express :3001) --> Claude Code SDK
```

A new `claude-service/` directory at the project root contains a small Express server that wraps `@anthropic-ai/claude-agent-sdk` `query()` calls. FastAPI delegates all LLM work to this service over localhost HTTP. The frontend is unaffected — it continues to call FastAPI endpoints.

### Why a sidecar over in-process?

- The Agent SDK is a TypeScript/Node package; the backend is Python
- HTTP between the two gives streaming support (SSE), clean error handling, independent lifecycle, and easy independent testing
- The Node service can restart without affecting non-LLM FastAPI routes

## Claude Service

### Directory Structure

```
claude-service/
  package.json
  tsconfig.json
  src/
    index.ts              — Express server startup, route registration
    schema.ts             — Profile type definitions and prompt schema block
    routes/
      interview.ts        — /interview/start, /interview/message handlers
      extract.ts          — /extract handler
      posting.ts          — /analyze-posting handler
    prompts/
      interview.ts        — System prompt for interview sessions
      extraction.ts       — System prompt for document extraction
      posting.ts          — System prompt for job posting analysis
```

### Dependencies

- `@anthropic-ai/claude-agent-sdk`
- `express`
- `@types/express` (dev)
- `tsx` (dev, for hot reload)
- `vitest` (dev)

### Endpoints

#### `GET /health`

Returns `{ status: "ok" }`. Used by FastAPI to verify the service is reachable.

#### `POST /interview/start`

Starts a new interview session.

**Request:**
```json
{
  "profile": { "summary": "...", "skills": [...], ... },
  "documents_path": "/path/to/documents"
}
```

**Behavior:**
- Calls `query()` with the interview system prompt, profile schema, current profile state, and document directory as `cwd`
- `allowedTools: ["Read", "Glob"]`
- `maxTurns: 3`
- `permissionMode: "bypassPermissions"` with `allowDangerouslySkipPermissions: true`
- Captures `session_id` from the `init` system message
- Parses suggestions from Claude's response (JSON blocks with ` ```suggestion ` markers)

**Response:**
```json
{
  "session_id": "...",
  "message": "Claude's opening question",
  "suggestions": [
    {
      "section": "experience",
      "action": "add",
      "target": { ... },
      "original": null,
      "proposed": "..."
    }
  ]
}
```

#### `POST /interview/message`

Continues an existing interview session.

**Request:**
```json
{
  "session_id": "...",
  "message": "User's response"
}
```

**Behavior:**
- Calls `query()` with `resume: session_id`
- Same tool/permission config as start
- Parses suggestions from response

**Response:**
```json
{
  "message": "Claude's follow-up",
  "suggestions": [...]
}
```

#### `POST /extract`

One-shot document extraction.

**Request:**
```json
{
  "profile": { ... },
  "documents_path": "/path/to/documents"
}
```

**Behavior:**
- One-shot `query()` with extraction system prompt, profile schema, current profile state
- `allowedTools: ["Read", "Glob"]`, `cwd: documents_path`
- `maxTurns: 5` (may need multiple reads)
- Claude reads files directly using the `Read` tool
- Parses structured extraction result from response

**Response:**
```json
{
  "skills": ["Python", "React"],
  "technologies": ["AWS", "Docker"],
  "experience_keywords": ["Led migration", "Reduced latency by 40%"],
  "soft_skills": ["Leadership", "Cross-functional collaboration"]
}
```

#### `POST /analyze-posting`

Analyzes a job posting URL (new feature).

**Request:**
```json
{
  "url": "https://example.com/job/12345",
  "profile": { ... }
}
```

**Behavior:**
- One-shot `query()` with posting analysis system prompt and profile schema
- `allowedTools: ["WebFetch"]`
- `maxTurns: 5`
- Claude fetches the page and extracts key information

**Response:**
```json
{
  "key_requirements": ["5+ years Python", "AWS experience"],
  "emphasis_areas": ["distributed systems", "team leadership"],
  "keywords": ["microservices", "CI/CD", "agile"]
}
```

### Schema Injection

A shared schema definition in `claude-service/src/schema.ts` defines the profile data model and exports a formatted string block for injection into system prompts:

```
Profile Schema:
  summary: string
  skills: string[]
  experience: [{ company: string, role: string, start_date: "YYYY-MM", end_date: "YYYY-MM" | null, accomplishments: string[] }]
  activities: [{ name: string, category: "Project"|"Volunteer"|"Interest"|"Other", url?: string, start_date?: "YYYY-MM", end_date?: "YYYY-MM" | null, details: string[] }]
  education: [{ institution: string, degree: string, field?: string, start_date: "YYYY-MM", end_date: "YYYY-MM" | null, details: string[] }]
  certifications: [{ name: string, issuer: string, date: "YYYY-MM" }]
  objectives: string[]
```

Each prompt handler imports this and injects it into the system prompt along with the current profile state (passed from FastAPI in the request body).

### SDK Options Per Feature

| Feature | `allowedTools` | `maxTurns` | Session | `permissionMode` |
|---|---|---|---|---|
| Interview start | `Read`, `Glob` | 3 | new (capture `session_id`) | `bypassPermissions` |
| Interview message | `Read`, `Glob` | 3 | resume via `session_id` | `bypassPermissions` |
| Extract | `Read`, `Glob` | 5 | one-shot | `bypassPermissions` |
| Analyze posting | `WebFetch` | 5 | one-shot | `bypassPermissions` |

### Error Handling

The service returns structured error JSON with appropriate HTTP status codes:

```json
{
  "error": "Session not found",
  "detail": "The session ID provided does not exist or has expired"
}
```

| Scenario | HTTP Status |
|---|---|
| Invalid request body | 400 |
| Session not found | 404 |
| SDK query failure | 502 |
| Timeout | 504 |

## Python Backend Changes

### Removed

- `anthropic` Python package dependency
- `backend/services/interview.py` — LLM logic moves to Node service
- `backend/services/extraction.py` — LLM logic moves to Node service
- `backend/routers/settings.py` API key endpoints (`GET/PUT/DELETE/POST /api/settings/api-key/*`)
- `backend/services/encryption.py` — no longer needed for API key storage
- `config.py` API key resolution logic (`get_api_key`, `build_claude_client`)

### Simplified

- **`backend/routers/interview.py`** — keeps rate limiting, session TTL management (30 min, max 20 sessions), and suggestion accept/reject logic. Delegates LLM calls to `http://localhost:3001/interview/*`
- **`backend/routers/extraction.py`** — proxies to `http://localhost:3001/extract`
- **`backend/config.py`** — adds `CLAUDE_SERVICE_URL` (defaults to `http://localhost:3001`), removes API key config

### New

- **`backend/services/claude_client.py`** — thin async HTTP client (`httpx.AsyncClient`) for calling the Node service. Handles timeouts, connection errors, and maps Node service errors to FastAPI `HTTPException`s.

### Kept As-Is

- Profile service (CRUD on `.profile.json`)
- Document management
- Application manager
- All frontend code and API modules

## Dev Workflow

### Starting All Services

Root `package.json` scripts using `concurrently`:

```json
{
  "dev": "concurrently \"npm run dev:frontend\" \"npm run dev:backend\" \"npm run dev:claude\"",
  "dev:frontend": "vite",
  "dev:backend": "uvicorn backend.main:app --reload --port 8000",
  "dev:claude": "cd claude-service && npm run dev"
}
```

### Claude Service Scripts

```json
{
  "dev": "tsx watch src/index.ts",
  "build": "tsc",
  "start": "node dist/index.js",
  "test": "vitest run"
}
```

### Health Check

The Node service exposes `GET /health`. On startup, FastAPI logs a warning if the Claude service isn't reachable but doesn't block — non-LLM features (profile CRUD, documents, applications) continue to work.

## Testing Strategy

### Claude Service (Node — vitest)

- **Unit tests** for each route handler: verify correct `allowedTools`, `maxTurns`, `permissionMode`, system prompt contains schema block
- Mock `query()` from the Agent SDK — tests verify prompt construction, schema injection, session ID handling, and response parsing
- **Health endpoint** integration test: returns 200

### Python Backend (pytest)

- Existing tests for profile, documents, applications **unchanged**
- Interview router tests mock `httpx.AsyncClient` calls to the Claude service — verify correct proxying, session management, rate limiting, suggestion accept/reject
- Extraction router tests mock the same way
- `claude_client.py` tests verify timeout handling, error mapping (Node 500 → FastAPI 502), connection refused → 503

### What We Don't Test

- Actual SDK `query()` behavior (Anthropic's responsibility)
- LLM output quality (non-deterministic)

### What We Do Test

- Prompts are constructed correctly with schema and profile data
- Session IDs are captured and reused for multi-turn
- Error paths (service down, timeout, malformed response)
- Rate limits and TTL still enforced in FastAPI
- Response parsing extracts suggestions/extraction data correctly

## Migration Path

1. Build the Node service with all four endpoints
2. Create `backend/services/claude_client.py`
3. Refactor Python interview router to proxy through the client
4. Refactor Python extraction router to proxy through the client
5. Remove `anthropic` dependency, API key management, encryption service
6. Update dev scripts for concurrent startup
7. Add the new analyze-posting endpoint (FastAPI route + frontend stub)

## Settings Page Impact

The Settings page currently manages the Anthropic API key. With the SDK handling auth:

- Remove the API key configuration section
- The Settings page retains any other settings (if present) or becomes a simpler page
- If the Settings page has no other purpose, it can be simplified to show service status (Claude service health check) instead
