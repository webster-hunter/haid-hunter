# Extraction Panel — Move to Documents Page

**Date:** 2026-03-30
**Status:** Approved

## Overview

Move document extraction (NLP-based skill/tech/keyword analysis) from the Profile page into the Documents page. Users select specific documents via checkboxes, trigger analysis, and review results in the right panel — which already exists for document preview and now serves double duty.

The `ExtractionPanel` component on the Profile page is removed entirely. The `localStorage` hand-off mechanism it used is also dropped.

---

## Components & State

### DocumentManager (extended)

New state fields added to the existing coordinator:

```ts
checkedIds: Set<string>                      // which docs are checked for analysis
extractionResult: ExtractionResult | null    // analysis output; null = show preview
extractionSelection: SelectionState          // chip toggle state (per category)
extractionLoading: boolean                   // true while POST /analyze is in flight
profileSkills: string[]                      // current profile.skills, loaded before analysis
```

Right panel rendering logic:
- `extractionResult !== null` → render `ExtractionResultsPanel`
- otherwise → render `DocumentPreview` (unchanged)

### DocumentList (modified)

- Each item gains a checkbox driven by `checkedIds` + `onCheck(id)` props.
- Single-click row behavior unchanged — still calls `onSelect` for preview.
- Checkbox click is independent of row click (no conflict).

### DocumentToolbar (modified)

- Gains an "Analyze Selected" button.
- Disabled when `checkedIds.size === 0` or `extractionLoading === true`.
- Shows loading state text ("Analyzing…") while in flight.

### ExtractionResultsPanel (new component)

Replaces the right panel slot when `extractionResult` is set. Props-driven (no local state, no localStorage). Contains:

- Chip categories: Skills, Technologies, Experience Keywords, Soft Skills.
- Each chip is compared against `existingSkills: string[]` (the flat `profile.skills` list). Chips already present in the profile are rendered in a distinct "already added" style (grayed, not toggleable, checkmark indicator) and excluded from the Accept payload. Chips not yet in the profile behave normally.
- Chip toggle → calls `onToggle(category, item)` in DocumentManager (only for chips not already in profile).
- "Accept Selected" button → calls `onAccept()`. Only sends chips that are selected AND not already in the profile.
- "Re-analyze" button → calls `onReanalyze()` (re-runs with same `checkedIds`).
- "Done" button → calls `onDismiss()` → sets `extractionResult` to null.
- Empty result state: "No suggestions found." with a Done button. If all found items are already in the profile, show "All suggestions already in your profile." with a Done button.

### ExtractionPanel (deleted)

Removed from `src/components/profile/ExtractionPanel.tsx`. `ProfileView` no longer imports or renders it. The `localStorage` cache (`extraction_result`) is no longer written or read anywhere.

### Auto-analyze on upload (removed)

`DocumentManager.handleUpload` currently calls `analyzeDocuments()` automatically after every upload and stores the result in localStorage. This behavior is removed — analysis is now always user-initiated. The upload status message becomes simply "Upload complete." The `analyzeDocuments` import in `DocumentManager` is removed.

---

## Data Flow

### Analyze

1. User checks documents → `checkedIds` updates.
2. User clicks "Analyze Selected" → `DocumentManager.handleAnalyze()`.
3. Fetches current profile (`GET /api/profile`) to capture `profile.skills` → stored in `profileSkills`.
4. Calls `POST /api/extraction/analyze` with `{ document_ids: [...checkedIds] }`.
5. Backend reads only those documents, runs NLP, returns `ExtractionResult`.
6. `extractionResult`, `extractionSelection`, and `profileSkills` set → right panel swaps to `ExtractionResultsPanel`.

### Accept

1. User toggles chips → `extractionSelection` updates.
2. User clicks "Accept Selected" → `POST /api/extraction/accept` with filtered result.
3. Profile updated on backend.

### Dismiss

- "Done" button → `extractionResult = null` → right panel reverts to `DocumentPreview`.
- Clicking any document in the list → sets `selectedId` as normal AND clears `extractionResult`.

### Re-analyze

- "Re-analyze" re-runs `handleAnalyze()` with current `checkedIds` (still checked).

---

## Backend Changes

`POST /api/extraction/analyze` gains an optional request body:

```python
class AnalyzeRequest(BaseModel):
    document_ids: list[str] = []  # empty list = analyze all documents (backwards compat)
```

When `document_ids` is non-empty, `read_document_contents` is called with only those files. Unknown IDs are skipped silently (not a 404).

Frontend `analyzeDocuments()` in `src/api/extraction.ts` gains an optional `documentIds?: string[]` parameter passed in the request body.

---

## Error Handling & Edge Cases

| Scenario | Behavior |
|---|---|
| Analysis request fails | `extractionLoading` cleared; status bar shows "Analysis failed."; right panel unchanged |
| Profile fetch fails during analyze | Analysis still proceeds; `profileSkills` treated as empty (no items marked "already added") |
| All selected docs have no extractable text | Backend returns empty lists; panel shows "No suggestions found." |
| All found items already in profile | Panel shows "All suggestions already in your profile." with a Done button |
| User deletes a checked document | Its ID removed from `checkedIds` in `handleDelete` |
| User checks docs then searches/filters | `checkedIds` persists (keyed by ID, not position) |
| "Analyze Selected" clicked while results already showing | Re-runs analysis, replaces previous results |
| Profile page after accept | Loads fresh data on mount — no cross-page refresh needed |

---

## Testing

### Backend — `test_extraction_api.py`

- `test_analyze_with_specific_document_ids` — only those docs' content is read
- `test_analyze_with_empty_ids_reads_all_docs` — empty list falls back to all docs
- `test_analyze_with_nonexistent_id_skips_gracefully` — unknown IDs ignored, not 404

### Frontend

| Test file | Coverage |
|---|---|
| `DocumentList.test.tsx` | Checkboxes render; checking calls `onCheck` with correct id; row click still calls `onSelect` |
| `DocumentToolbar.test.tsx` | "Analyze Selected" absent at 0 checked; present when 1+; disabled while loading |
| `ExtractionResultsPanel.test.tsx` | Chips render by category; toggle updates selection; Accept fires with filtered items; Done fires `onDismiss`; empty result state; already-in-profile chips are non-interactive with "already added" style; Accept payload excludes already-in-profile items; all-already-in-profile message |
| `DocumentManager.test.tsx` | Right panel shows `ExtractionResultsPanel` after analysis; clicking doc clears results; delete removes from checked set |
