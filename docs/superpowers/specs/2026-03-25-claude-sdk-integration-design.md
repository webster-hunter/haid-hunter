# Claude Code SDK Integration

## Summary

Replace the direct `anthropic` Python SDK usage with the `claude-agent-sdk` Python package. This eliminates separate API key management and billing, enables agentic tool use (file reading, web fetching), and uses the existing Claude Code subscription for all LLM calls. No architectural changes — the SDK is called in-process from the existing FastAPI services.

## Architecture

```
Browser (React) --> FastAPI (Python :8000) --> claude-agent-sdk query() / ClaudeSDKClient
```

The `anthropic` SDK calls in `backend/services/interview.py` and `backend/services/extraction.py` are replaced with `claude_agent_sdk` calls. No new services or runtimes. **Note:** The SDK spawns CLI subprocesses internally — this is not truly "zero processes" but the subprocess lifecycle is managed by the SDK, not by us.

### Why in-process over a sidecar?

- The `claude-agent-sdk` Python package has full feature parity with the TypeScript SDK
- Zero accidental complexity: no HTTP proxying, no timeout tuning, no error code mapping, no health checks, no second process to manage
- Session state stays in a single process — no split between Python sessions and SDK sessions
- For a locally-hosted single-developer app, operational complexity should be minimized

## SDK API Surface

### One-shot calls: `query()`

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    system_prompt="...",
    max_turns=5,
    cwd="/path/to/documents",
    allowed_tools=["Read", "Glob"],
    permission_mode="bypassPermissions",
)

async for message in query(prompt="Extract skills from these documents", options=options):
    # process messages
```

Used for: extraction, job posting analysis.

### Multi-turn sessions: `ClaudeSDKClient`

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

options = ClaudeAgentOptions(
    system_prompt="...",
    max_turns=3,
    cwd="/path/to/documents",
    allowed_tools=["Read", "Glob"],
    permission_mode="bypassPermissions",
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Tell me about yourself")
    async for msg in client.receive_response():
        # first turn response

    await client.query("I worked at Acme Corp for 5 years")
    async for msg in client.receive_response():
        # second turn response, full context preserved
```

Used for: interview sessions. The client object is kept alive in the session dict for the TTL duration (30 min).

## Changes by File

### `backend/services/interview.py` — Rewrite

**Current:** Creates `anthropic.Anthropic()` client, manages message history manually, sends full conversation context on each turn.

**New:** Manages `ClaudeSDKClient` instances per session. Each session holds a live client that maintains conversation state automatically.

**Session structure changes from:**
```python
_sessions[session_id] = {
    "messages": [...],       # manual message history
    "suggestions": {...},
    "created_at": ...,
}
```

**To:**
```python
_sessions[session_id] = {
    "client": ClaudeSDKClient,       # live SDK client, maintains own context
    "suggestions": {...},             # indexed by suggestion_id for accept/reject
    "accepted_suggestions": [],       # list of accepted suggestion_ids
    "rejected_suggestions": [],       # list of rejected suggestion_ids
    "created_at": ...,
}
```

**System prompt:** Includes the profile schema (see Schema Injection below), the current profile state, and instructions for reading uploaded documents and proposing structured suggestions.

**Suggestion parsing:** Unchanged — Claude returns suggestions as JSON blocks with ` ```suggestion ` markers. The service parses these from the SDK response text, assigns `suggestion_id`s, and stores them for accept/reject.

**Session cleanup:** `ClaudeSDKClient` holds a CLI subprocess. Cleanup must be handled carefully to avoid orphaned processes, especially on Windows where child processes are not automatically killed when the parent dies.

**Chosen strategy:** `cleanup_expired_sessions()` becomes async. It is called as a FastAPI dependency on every interview endpoint request (lightweight — just checks timestamps and evicts expired entries). Each eviction calls `await client.__aexit__(None, None, None)` to properly shut down the subprocess.

**Shutdown handler:** A `@app.on_event("shutdown")` handler iterates all remaining sessions and closes their clients. As a belt-and-suspenders fallback, it also sends `SIGTERM` (or `taskkill` on Windows) to any subprocess PID still alive after `__aexit__`.

**Process restart:** Sessions are ephemeral and non-recoverable across server restarts. The frontend must handle a "session expired" response gracefully rather than showing a confusing error.

### `backend/services/extraction.py` — Rewrite

**Current:** Creates `anthropic.Anthropic()` client, pre-reads documents via `document_reader.py`, sends content in a single message.

**New:** Uses one-shot `query()` with `allowed_tools=["Read", "Glob"]` and `cwd` set to the documents directory. Claude reads the files itself using the built-in Read tool.

**`merge_suggestions()` is preserved** — it is pure business logic unrelated to LLM calls. It stays in this file.

**`document_reader.py` disposition:** No longer needed for LLM features since the SDK reads documents directly. The file is removed unless other non-LLM features depend on it (currently none do).

### `backend/config.py` — Simplify

**Remove:** `get_api_key()`, `build_claude_client()`, API key resolution logic (database lookup, env var fallback).

**Keep:** `DOCUMENTS_DIR`, `PROFILE_PATH`, database config.

**Add:** No new config needed — the SDK uses Claude Code's built-in auth.

### `backend/routers/interview.py` — Moderate changes

Rate limiting, session TTL enforcement, and suggestion accept/reject endpoints remain. The router calls the rewritten `interview.py` service which now uses the SDK internally. Router contract is unchanged.

**Remove:** The `read_document_contents` call and `MetadataService` dependency. The SDK reads documents directly via `Read`/`Glob` tools — the router no longer needs to pre-read documents before starting a session.

**Fix encapsulation:** The router currently reaches directly into `interview_service._sessions` for accept/reject. Add proper service-layer methods (`accept_suggestion(session_id, suggestion_id)`, `reject_suggestion(session_id, suggestion_id)`) instead of accessing the private dict from the router.

### `backend/routers/extraction.py` — Minor changes

Proxies to the rewritten `extraction.py` service. Router contract is unchanged.

### `backend/routers/settings.py` — Remove API key endpoints

**Remove:** `GET/PUT/DELETE/POST /api/settings/api-key/*` endpoints and `_resolve_api_key()`, `_mask_key()`, `build_claude_client()` helpers.

**Keep:** Any non-API-key settings endpoints (if present).

### `backend/services/encryption.py` — Keep

**Cannot be removed.** `EncryptionService` is used by `backend/routers/applications.py` to encrypt/decrypt job application credentials (`login_email`, `login_password`). It is also instantiated in `backend/main.py` at startup. Only the API-key-specific usage in `config.py` and `settings.py` is removed.

### `backend/services/document_reader.py` — Remove

The SDK reads documents directly via built-in Read/Glob tools. No other features depend on this module.

## New: Posting Analysis

### `backend/services/posting.py` — New

One-shot `query()` with `allowed_tools=["WebFetch"]`. Claude fetches the job posting page and extracts structured data.

**System prompt:** Includes the profile schema so Claude can map posting requirements to profile sections.

**Returns:**
```python
{
    "key_requirements": ["5+ years Python", "AWS experience"],
    "emphasis_areas": ["distributed systems", "team leadership"],
    "keywords": ["microservices", "CI/CD", "agile"]
}
```

### `backend/routers/posting.py` — New

**`POST /api/posting/analyze`**
- Request: `{ "url": "https://..." }`
- Reads current profile, passes URL + profile to posting service
- Rate limited: 5 requests/minute
- Response: `{ "key_requirements": [...], "emphasis_areas": [...], "keywords": [...] }`

## Schema Injection

A shared schema definition in `backend/services/schema.py` exports a formatted string for injection into all LLM system prompts:

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

**Note:** The `objectives` field exists in the frontend (`SectionEditor.tsx` has an objectives editor) but is not yet in the Python profile model. As part of this work, add `objectives: list[str]` to `VALID_SECTIONS`, `EMPTY_PROFILE`, and the Pydantic `ProfileRequest` model.

Each service imports the schema string and injects it along with the current profile state into the system prompt.

**Schema drift mitigation:** Rather than maintaining a hand-crafted string, `schema.py` should auto-generate the prompt schema from the Pydantic models in `profile.py`. A small function (~20 lines) walks the model fields and produces the compact format shown above. This eliminates a class of bugs where the schema and model diverge.

## SDK Options Per Feature

| Feature | Function | `allowed_tools` | `max_turns` | `cwd` | Session |
|---|---|---|---|---|---|
| Interview start | `ClaudeSDKClient` | `Read`, `Glob` | 3 | documents dir | new client |
| Interview message | `ClaudeSDKClient` | `Read`, `Glob` | 3 | documents dir | existing client |
| Extract | `query()` | `Read`, `Glob` | 5 | documents dir | one-shot |
| Analyze posting | `query()` | `WebFetch` | 5 | N/A | one-shot |

All use `permission_mode="bypassPermissions"` since this is a headless backend with no interactive user. Tool access is explicitly scoped via `allowed_tools` per call, and `cwd` is set to the documents directory.

**`cwd` scope caveat:** `cwd` sets the working directory for relative paths but may not prevent the Read tool from accessing absolute paths outside it. This is low severity for a localhost-only app where the user owns all local files, but the system prompts should instruct Claude to only read files within the documents directory. This is a defense-in-depth measure, not a hard security boundary.

## Frontend Changes

Most frontend code is unaffected. These files require updates:

- **`src/api/settings.ts`** — remove API key management functions (`getApiKeyStatus`, `setApiKey`, `deleteApiKey`, `testApiKey`). Replace with a service health check or remove entirely.
- **`src/components/settings/SettingsView.tsx`** — remove API key configuration UI. Simplify to show other settings or service status.
- **`src/__tests__/settings/SettingsView.test.tsx`** — rewrite to match simplified Settings page.
- **`src/api/interview.ts`** — update `startInterview` response type to include `suggestions[]`. Currently returns `{ session_id: string; message: string }`. The new interview service will return suggestions from the initial response, so the type becomes `{ session_id: string; message: string; suggestions: Suggestion[] }`.

## Dependency Changes

### Remove
- `anthropic` (pip)
- `pdfplumber` (pip) — only used by `document_reader.py`, which is being removed. The SDK's built-in `Read` tool handles file reading. **Note:** Verify that the SDK's Read tool can extract text from PDFs; if not, keep `pdfplumber` as a fallback for document preview.

### Add
- `claude-agent-sdk` (pip)

### No Change
- `cryptography` stays (used by `encryption.py` for application credential encryption)
- `httpx` stays (used in async test client harness)
- `python-magic-bin` stays (used for MIME type detection in document uploads, unaffected)
- All npm dependencies unchanged

## Error Handling

The SDK provides typed exceptions:

| Exception | Meaning | FastAPI mapping |
|---|---|---|
| `CLINotFoundError` | Claude Code not installed | 503 Service Unavailable |
| `CLIConnectionError` | Can't connect to CLI | 503 Service Unavailable |
| `ProcessError` | SDK process failed | 502 Bad Gateway |
| `ClaudeSDKError` | General SDK error | 500 Internal Server Error |

Each service wraps SDK calls in try/except and raises `HTTPException` with appropriate status codes.

## Testing Strategy

### Python Backend (pytest)

**Existing tests unchanged:** profile, documents, applications.

**Rewritten service tests:**
- `backend/tests/test_interview_service.py` — mock `ClaudeSDKClient` and `query()`. Verify:
  - System prompt includes schema and profile state
  - `allowed_tools` and `max_turns` are correct
  - Session client is created on start and reused on message
  - Suggestions are parsed from response text
  - Session cleanup exits the client context manager
- `backend/tests/test_extraction_service.py` — mock `query()`. Verify:
  - System prompt includes schema and profile state
  - `cwd` is set to documents directory
  - Response is parsed into structured extraction result
  - `merge_suggestions()` still works (pure logic, no mock needed)
- `backend/tests/test_posting_service.py` — new. Mock `query()`. Verify:
  - `allowed_tools` includes `WebFetch`
  - URL is passed in prompt
  - Response is parsed into requirements/keywords structure

**Router tests:**
- Interview router tests verify rate limiting, session TTL, suggestion accept/reject — mock the service layer
- Extraction router tests verify proxying to service — mock the service layer
- Posting router tests — new, verify rate limiting and request validation

**What we don't test:** Actual SDK behavior, LLM output quality.

**What we do test:** Prompt construction, option configuration, response parsing, error handling, session lifecycle, rate limits.

**SDK smoke test:** One manual (or CI-excluded) test that calls the real SDK with a trivial prompt to verify import paths, function signatures, and response shapes are correct. This catches API shape mismatches early. Marked `@pytest.mark.skip(reason="requires Claude Code CLI")` in normal test runs.

### Frontend (vitest)

- Settings page tests rewritten for simplified UI
- Other frontend tests unchanged

## Migration Path

0. Run SDK smoke test — verify `claude_agent_sdk` imports, `query()` signature, and response shape
1. Add `objectives: list[str]` to profile model (`VALID_SECTIONS`, `EMPTY_PROFILE`, Pydantic `ProfileRequest`)
2. Install `claude-agent-sdk`, remove `anthropic` and `pdfplumber` (keep `cryptography` — used by applications)
3. Create `backend/services/schema.py` — auto-generate prompt schema from Pydantic models
4. Rewrite `backend/services/interview.py` using `ClaudeSDKClient`, add `accept_suggestion`/`reject_suggestion` methods, implement async cleanup with subprocess fallback
5. Rewrite `backend/services/extraction.py` using `query()`, preserve `merge_suggestions()`
6. Create `backend/services/posting.py` and `backend/routers/posting.py`
7. Remove `backend/services/document_reader.py` (keep `encryption.py`)
8. Simplify `backend/config.py` (remove API key logic only)
9. Update `backend/routers/interview.py` — remove `read_document_contents` call, use service-layer methods for accept/reject
10. Remove API key endpoints from `backend/routers/settings.py`
11. Update frontend settings page and interview API types
12. Update all affected tests
