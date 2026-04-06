# Tag Checkbox & Analyze All — Design Spec

**Date:** 2026-03-31
**Status:** Approved

## Overview

Two enhancements to the Documents page:

1. **Tag checkboxes** — A checkbox beside each tag in `TagSidebar` that selects all documents with that tag, adding them to `checkedIds` in `DocumentManager`.
2. **Analyze All** — The "Analyze Selected" button in `DocumentToolbar` is always visible. When nothing is checked it reads "Analyze All" and triggers analysis on all documents; when documents are checked it reads "Analyze Selected (N)" as before.

---

## Components & Changes

### TagSidebar (modified)

New props:

```ts
checkedIds: Set<string>       // passed down from DocumentManager
onCheckTag: (tag: string) => void
```

Each tag row renders a checkbox before the tag name. The "All Documents" row does **not** get a checkbox.

Checkbox checked state: `checked` when **every** document in `allDocuments` that has this tag is present in `checkedIds`. Unchecked otherwise (no indeterminate state).

Clicking the checkbox calls `onCheckTag(tag)`. DocumentManager performs the set arithmetic.

### DocumentToolbar (modified)

The "Analyze Selected" button is made always-visible — the `checkedCount > 0` conditional render is removed.

Label logic (driven by existing `checkedCount` prop):

- `checkedCount === 0` → **"Analyze All"**
- `checkedCount > 0` → **"Analyze Selected (N)"** where N = `checkedCount`

Still disabled and shows **"Analyzing…"** while `extractionLoading` is true. No new props required.

### DocumentManager (modified)

**`handleCheckTag(tag: string)`** — new handler:

```ts
const handleCheckTag = (tag: string) => {
  const tagDocs = allDocuments.filter(d => d.tags.includes(tag))
  const allChecked = tagDocs.every(d => checkedIds.has(d.id))
  setCheckedIds(prev => {
    const next = new Set(prev)
    if (allChecked) {
      tagDocs.forEach(d => next.delete(d.id))
    } else {
      tagDocs.forEach(d => next.add(d.id))
    }
    return next
  })
}
```

Uses `allDocuments` (unfiltered) so tag-checking works even when a search filter is active.

**`handleAnalyze()` update** — when `checkedIds` is empty, calls `analyzeDocuments([])`, which the backend treats as "analyze all documents." When IDs are present, behavior is unchanged.

**New props passed to `TagSidebar`:**

```tsx
<TagSidebar
  ...
  checkedIds={checkedIds}
  onCheckTag={handleCheckTag}
/>
```

---

## Data Flow

1. User clicks a tag checkbox → `onCheckTag(tag)` → `handleCheckTag` adds/removes all docs with that tag from `checkedIds`.
2. `checkedIds` flows down to `DocumentToolbar` as `checkedCount={checkedIds.size}` (unchanged) and to `TagSidebar` as `checkedIds` (new).
3. User clicks "Analyze All" (0 checked) → `handleAnalyze()` → `analyzeDocuments([])` → backend analyzes all docs.
4. User clicks "Analyze Selected (N)" (N > 0) → `handleAnalyze()` → `analyzeDocuments([...checkedIds])` → unchanged backend behavior.

---

## Edge Cases

| Scenario | Behavior |
|---|---|
| Tag has 0 documents | Checkbox renders but clicking is a no-op (no docs to add/remove) |
| Tag checked while search filter active | Uses `allDocuments` (unfiltered), so all docs with that tag are selected regardless of visible list |
| Some docs with tag already checked | Clicking adds the rest (all-or-nothing: only full selection → deselects) |
| All docs with tag checked → click | Removes all docs for that tag from `checkedIds` |
| "Analyze All" while results panel is showing | Re-runs analysis, replaces previous results (existing behavior) |

---

## Testing

### `TagSidebar.test.tsx`

- Checkbox renders for each tag (not for "All Documents")
- Checkbox is checked when all docs for that tag are in `checkedIds`
- Checkbox is unchecked when none or only some docs for that tag are in `checkedIds`
- Clicking checkbox calls `onCheckTag` with the correct tag name
- Clicking checkbox does not call `onSelectTag`

### `DocumentToolbar.test.tsx`

- "Analyze All" button is visible when `checkedCount === 0`
- Button label is "Analyze Selected (2)" when `checkedCount === 2`
- Button is disabled and shows "Analyzing…" when `extractionLoading` is true regardless of `checkedCount`

### `DocumentManager.test.tsx`

- Checking a tag's checkbox adds all docs with that tag to `checkedIds`
- Checking a tag when all its docs are already checked removes them all
- "Analyze All" (0 checked) triggers `analyzeDocuments` with empty array
