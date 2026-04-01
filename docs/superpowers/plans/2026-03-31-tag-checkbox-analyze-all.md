# Tag Checkbox & Analyze All Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add per-tag checkboxes to select all documents with that tag, and make the Analyze button always visible (showing "Analyze All" when nothing is checked, "Analyze Selected (N)" otherwise).

**Architecture:** Three component changes — `TagSidebar` gains `checkedIds`/`onCheckTag` props and renders checkboxes; `DocumentToolbar`'s analyze button becomes always-visible with a dynamic label; `DocumentManager` adds `handleCheckTag` and passes new props down to `TagSidebar`. No backend changes needed — `analyzeDocuments([])` already means "analyze all" on the backend.

**Tech Stack:** React + TypeScript, vitest + @testing-library/react

---

## File Map

| Action | File |
|--------|------|
| Modify | `src/components/documents/TagSidebar.tsx` |
| Modify | `src/__tests__/documents/TagSidebar.test.tsx` |
| Modify | `src/components/documents/DocumentToolbar.tsx` |
| Modify | `src/__tests__/documents/DocumentToolbar.test.tsx` |
| Modify | `src/components/documents/DocumentManager.tsx` |
| Modify | `src/__tests__/documents/DocumentManager.test.tsx` |
| Modify | `src/index.css` |

---

## Task 1: TagSidebar — add per-tag checkboxes

**Files:**
- Modify: `src/components/documents/TagSidebar.tsx`
- Modify: `src/__tests__/documents/TagSidebar.test.tsx`

- [ ] **Step 1: Write the failing tests**

Replace `src/__tests__/documents/TagSidebar.test.tsx` with:

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { TagSidebar } from '../../components/documents/TagSidebar'
import type { DocumentMeta } from '../../api/documents'

const mockDocs: DocumentMeta[] = [
  { id: '1', original_name: 'a.txt', stored_name: '1_a.txt', display_name: 'a.txt', tags: ['resume'], uploaded_at: '', size_bytes: 10, mime_type: 'text/plain' },
  { id: '2', original_name: 'b.txt', stored_name: '2_b.txt', display_name: 'b.txt', tags: ['resume', 'cv'], uploaded_at: '', size_bytes: 20, mime_type: 'text/plain' },
]

const baseProps = {
  tags: ['resume', 'cv'],
  allDocuments: mockDocs,
  activeTag: null,
  onSelectTag: () => {},
  onCreateTag: () => {},
  onDeleteTag: () => {},
  checkedIds: new Set<string>(),
  onCheckTag: () => {},
}

describe('TagSidebar', () => {
  it('shows All Documents with total count', () => {
    render(<TagSidebar {...baseProps} />)
    expect(screen.getByText('All Documents')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('shows tag counts', () => {
    render(<TagSidebar {...baseProps} />)
    const resumeItem = screen.getByText('resume').closest('[data-testid]')
    expect(resumeItem).toBeInTheDocument()
  })

  it('calls onSelectTag when tag is clicked', async () => {
    const onSelect = vi.fn()
    render(<TagSidebar {...baseProps} onSelectTag={onSelect} />)
    await userEvent.click(screen.getByText('resume'))
    expect(onSelect).toHaveBeenCalledWith('resume')
  })

  it('shows correct tag counts even when a tag is active', () => {
    render(<TagSidebar {...baseProps} activeTag="resume" />)
    expect(screen.getByText('(2)')).toBeInTheDocument()
    expect(screen.getByText('(1)')).toBeInTheDocument()
  })

  it('renders a checkbox for each tag but not for All Documents', () => {
    render(<TagSidebar {...baseProps} />)
    const checkboxes = screen.getAllByRole('checkbox')
    // Two tags → two checkboxes; "All Documents" row has none
    expect(checkboxes).toHaveLength(2)
  })

  it('checkbox is checked when all docs for that tag are in checkedIds', () => {
    // resume tag has docs '1' and '2'
    render(<TagSidebar {...baseProps} checkedIds={new Set(['1', '2'])} />)
    const checkboxes = screen.getAllByRole('checkbox')
    expect(checkboxes[0]).toBeChecked() // resume: both docs checked
  })

  it('checkbox is unchecked when only some docs for that tag are in checkedIds', () => {
    render(<TagSidebar {...baseProps} checkedIds={new Set(['1'])} />)
    const checkboxes = screen.getAllByRole('checkbox')
    expect(checkboxes[0]).not.toBeChecked() // resume: only doc '1' checked, not '2'
  })

  it('calls onCheckTag with tag name when checkbox is clicked', () => {
    const onCheckTag = vi.fn()
    render(<TagSidebar {...baseProps} onCheckTag={onCheckTag} />)
    const checkboxes = screen.getAllByRole('checkbox')
    fireEvent.click(checkboxes[0])
    expect(onCheckTag).toHaveBeenCalledWith('resume')
  })

  it('clicking tag checkbox does not call onSelectTag', () => {
    const onSelectTag = vi.fn()
    const onCheckTag = vi.fn()
    render(<TagSidebar {...baseProps} onSelectTag={onSelectTag} onCheckTag={onCheckTag} />)
    const checkboxes = screen.getAllByRole('checkbox')
    fireEvent.click(checkboxes[0])
    expect(onSelectTag).not.toHaveBeenCalled()
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /c/Users/whweb/Code/haid-hunter && npx vitest run src/__tests__/documents/TagSidebar.test.tsx 2>&1 | tail -15
```

Expected: FAIL — `checkedIds` and `onCheckTag` props missing, no checkboxes rendered yet.

- [ ] **Step 3: Update `src/components/documents/TagSidebar.tsx`**

Replace the file with:

```typescript
import { useState } from 'react'
import type { DocumentMeta } from '../../api/documents'

interface TagSidebarProps {
  tags: string[]
  allDocuments: DocumentMeta[]
  activeTag: string | null
  onSelectTag: (tag: string | null) => void
  onCreateTag: (name: string) => void
  onDeleteTag: (name: string) => void
  checkedIds: Set<string>
  onCheckTag: (tag: string) => void
}

export function TagSidebar({
  tags,
  allDocuments,
  activeTag,
  onSelectTag,
  onCreateTag,
  onDeleteTag,
  checkedIds,
  onCheckTag,
}: TagSidebarProps) {
  const [showInput, setShowInput] = useState(false)
  const [newTagName, setNewTagName] = useState('')

  const totalCount = allDocuments.length
  const getTagCount = (tag: string) => allDocuments.filter(d => d.tags.includes(tag)).length
  const isTagChecked = (tag: string) => {
    const tagDocs = allDocuments.filter(d => d.tags.includes(tag))
    return tagDocs.length > 0 && tagDocs.every(d => checkedIds.has(d.id))
  }

  const handleCreateTag = () => {
    const trimmed = newTagName.trim()
    if (trimmed) {
      onCreateTag(trimmed)
      setNewTagName('')
      setShowInput(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleCreateTag()
    if (e.key === 'Escape') {
      setShowInput(false)
      setNewTagName('')
    }
  }

  return (
    <aside className="tag-sidebar" data-testid="tag-sidebar">
      <div className="tag-sidebar-title">Tags</div>

      <div
        className={`tag-item${activeTag === null ? ' active' : ''}`}
        data-testid="tag-all"
        onClick={() => onSelectTag(null)}
      >
        <span>All Documents</span>
        <span className="tag-count">{totalCount}</span>
      </div>

      {tags.map(tag => (
        <div
          key={tag}
          className={`tag-item${activeTag === tag ? ' active' : ''}`}
          data-testid={`tag-item-${tag}`}
          onClick={() => onSelectTag(tag)}
        >
          <input
            type="checkbox"
            className="tag-checkbox"
            checked={isTagChecked(tag)}
            onChange={() => onCheckTag(tag)}
            onClick={e => e.stopPropagation()}
            aria-label={`Select all ${tag} documents`}
          />
          <span>{tag}</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span className="tag-count">({getTagCount(tag)})</span>
            <button
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', opacity: 0.5, padding: '0 2px', fontSize: 12 }}
              onClick={e => { e.stopPropagation(); onDeleteTag(tag) }}
              aria-label={`Delete tag ${tag}`}
            >
              ×
            </button>
          </div>
        </div>
      ))}

      {showInput ? (
        <div className="tag-input-row">
          <input
            className="form-input"
            value={newTagName}
            onChange={e => setNewTagName(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Tag name..."
            autoFocus
          />
          <button className="btn btn-primary btn-sm" onClick={handleCreateTag}>Add</button>
          <button className="btn btn-secondary btn-sm" onClick={() => { setShowInput(false); setNewTagName('') }}>✕</button>
        </div>
      ) : (
        <div className="add-tag-btn" onClick={() => setShowInput(true)}>
          + New Tag
        </div>
      )}
    </aside>
  )
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /c/Users/whweb/Code/haid-hunter && npx vitest run src/__tests__/documents/TagSidebar.test.tsx 2>&1 | tail -10
```

Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /c/Users/whweb/Code/haid-hunter && git add src/components/documents/TagSidebar.tsx src/__tests__/documents/TagSidebar.test.tsx && git commit -m "feat: add per-tag checkboxes to TagSidebar"
```

---

## Task 2: DocumentToolbar — always-visible analyze button with dynamic label

**Files:**
- Modify: `src/components/documents/DocumentToolbar.tsx`
- Modify: `src/__tests__/documents/DocumentToolbar.test.tsx`

- [ ] **Step 1: Write the failing tests**

Replace `src/__tests__/documents/DocumentToolbar.test.tsx` with:

```typescript
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { DocumentToolbar } from '../../components/documents/DocumentToolbar'

const baseProps = {
  search: '',
  onSearchChange: () => {},
  onUpload: () => {},
  onSync: () => {},
  checkedCount: 0,
  onAnalyze: () => {},
  extractionLoading: false,
}

describe('DocumentToolbar', () => {
  it('renders search input', () => {
    render(<DocumentToolbar {...baseProps} />)
    expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument()
  })

  it('calls onSearchChange when typing', async () => {
    const onChange = vi.fn()
    render(<DocumentToolbar {...baseProps} onSearchChange={onChange} />)
    await userEvent.type(screen.getByPlaceholderText(/search/i), 'test')
    expect(onChange).toHaveBeenCalled()
  })

  it('has upload and sync buttons', () => {
    render(<DocumentToolbar {...baseProps} />)
    expect(screen.getByText(/upload/i)).toBeInTheDocument()
    expect(screen.getByText(/sync/i)).toBeInTheDocument()
  })

  it('shows Analyze All button when checkedCount is 0', () => {
    render(<DocumentToolbar {...baseProps} checkedCount={0} />)
    expect(screen.getByText('Analyze All')).toBeInTheDocument()
  })

  it('shows Analyze Selected (N) button when checkedCount > 0', () => {
    render(<DocumentToolbar {...baseProps} checkedCount={2} />)
    expect(screen.getByText('Analyze Selected (2)')).toBeInTheDocument()
  })

  it('analyze button calls onAnalyze when clicked', async () => {
    const onAnalyze = vi.fn()
    render(<DocumentToolbar {...baseProps} checkedCount={0} onAnalyze={onAnalyze} />)
    await userEvent.click(screen.getByText('Analyze All'))
    expect(onAnalyze).toHaveBeenCalled()
  })

  it('analyze button is disabled and shows Analyzing… while extractionLoading', () => {
    render(<DocumentToolbar {...baseProps} checkedCount={0} extractionLoading={true} />)
    expect(screen.getByText(/analyzing/i)).toBeDisabled()
  })

  it('analyze button is disabled while loading even when docs are checked', () => {
    render(<DocumentToolbar {...baseProps} checkedCount={3} extractionLoading={true} />)
    expect(screen.getByText(/analyzing/i)).toBeDisabled()
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /c/Users/whweb/Code/haid-hunter && npx vitest run src/__tests__/documents/DocumentToolbar.test.tsx 2>&1 | tail -15
```

Expected: FAIL — "Analyze All" not rendered (button hidden at 0 checked), "Analyze Selected (2)" label doesn't match existing "Analyze Selected".

- [ ] **Step 3: Update `src/components/documents/DocumentToolbar.tsx`**

Replace the file with:

```typescript
import { useRef } from 'react'

interface DocumentToolbarProps {
  search: string
  onSearchChange: (value: string) => void
  onUpload: (files: File[]) => void
  onSync: () => void
  checkedCount: number
  onAnalyze: () => void
  extractionLoading: boolean
}

export function DocumentToolbar({
  search,
  onSearchChange,
  onUpload,
  onSync,
  checkedCount,
  onAnalyze,
  extractionLoading,
}: DocumentToolbarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? [])
    if (files.length) {
      onUpload(files)
      e.target.value = ''
    }
  }

  const analyzeLabel = extractionLoading
    ? 'Analyzing…'
    : checkedCount === 0
      ? 'Analyze All'
      : `Analyze Selected (${checkedCount})`

  return (
    <div className="document-toolbar">
      <input
        className="form-input toolbar-search"
        placeholder="Search documents..."
        value={search}
        onChange={e => onSearchChange(e.target.value)}
      />
      <input
        ref={fileInputRef}
        type="file"
        multiple
        style={{ display: 'none' }}
        onChange={handleFileChange}
        aria-label="Upload files"
      />
      <button
        className="btn btn-primary"
        onClick={() => fileInputRef.current?.click()}
      >
        Upload
      </button>
      <button className="btn btn-secondary" onClick={onSync}>
        Sync
      </button>
      <button
        className="btn btn-accent"
        onClick={onAnalyze}
        disabled={extractionLoading}
      >
        {analyzeLabel}
      </button>
    </div>
  )
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /c/Users/whweb/Code/haid-hunter && npx vitest run src/__tests__/documents/DocumentToolbar.test.tsx 2>&1 | tail -10
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /c/Users/whweb/Code/haid-hunter && git add src/components/documents/DocumentToolbar.tsx src/__tests__/documents/DocumentToolbar.test.tsx && git commit -m "feat: make analyze button always visible with dynamic label"
```

---

## Task 3: DocumentManager — wire handleCheckTag and update tests

**Files:**
- Modify: `src/components/documents/DocumentManager.tsx`
- Modify: `src/__tests__/documents/DocumentManager.test.tsx`

**Context:** `handleAnalyze` already calls `analyzeDocuments([...checkedIds])`. When `checkedIds` is empty, this spreads to `[]`, which the backend already treats as "analyze all". No change needed to `handleAnalyze`. Only changes are: add `handleCheckTag`, pass `checkedIds`/`onCheckTag` to `TagSidebar`, and update tests to match new toolbar labels.

- [ ] **Step 1: Write the failing tests**

Replace `src/__tests__/documents/DocumentManager.test.tsx` with:

```typescript
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import DocumentManager from '../../components/documents/DocumentManager'

const emptyProfile = { summary: '', skills: [], experience: [], activities: [], education: [], certifications: [] }
const extractionResult = {
  skills: ['Python'],
  technologies: ['Docker'],
  experience_keywords: [],
  soft_skills: [],
}

function makeFetch(overrides: Record<string, unknown> = {}) {
  return vi.fn().mockImplementation((url: string) => {
    if (url === '/api/tags') return Promise.resolve({ ok: true, json: async () => [] })
    if (url === '/api/profile') return Promise.resolve({ ok: true, json: async () => emptyProfile })
    if (url === '/api/extraction/analyze') return Promise.resolve({ ok: true, json: async () => extractionResult })
    if (/^\/api\/documents(\?.*)?$/.test(url) && overrides['/api/documents'] !== undefined) {
      return Promise.resolve({ ok: true, json: async () => overrides['/api/documents'] })
    }
    if (/^\/api\/documents\/[^/]+$/.test(url) && overrides['/api/documents'] !== undefined) {
      const docs = overrides['/api/documents'] as unknown[]
      return Promise.resolve({ ok: true, json: async () => (Array.isArray(docs) ? docs[0] : docs) })
    }
    return Promise.resolve({ ok: true, json: async () => [] })
  })
}

beforeEach(() => {
  vi.stubGlobal('fetch', makeFetch())
})

describe('DocumentManager', () => {
  it('renders the three-panel layout', async () => {
    render(<DocumentManager />)
    await waitFor(() => {
      expect(screen.getByTestId('tag-sidebar')).toBeInTheDocument()
    })
    expect(screen.getByTestId('document-list-panel')).toBeInTheDocument()
  })

  it('renders the page title', () => {
    render(<DocumentManager />)
    expect(screen.getByText('Documents')).toBeInTheDocument()
  })

  it('shows Analyze All button when nothing is checked', async () => {
    render(<DocumentManager />)
    await waitFor(() => expect(screen.getByTestId('tag-sidebar')).toBeInTheDocument())
    expect(screen.getByText('Analyze All')).toBeInTheDocument()
  })

  it('shows ExtractionResultsPanel in right panel after analysis', async () => {
    const docs = [
      { id: '1', original_name: 'r.pdf', stored_name: '1_r.pdf', display_name: 'r.pdf', tags: [], uploaded_at: '2026-01-01T00:00:00Z', size_bytes: 100, mime_type: 'application/pdf' },
    ]
    vi.stubGlobal('fetch', makeFetch({ '/api/documents': docs }))
    render(<DocumentManager />)

    await waitFor(() => expect(screen.getByText('r.pdf')).toBeInTheDocument())

    // Check the document — button changes to "Analyze Selected (1)"
    const checkboxes = screen.getAllByRole('checkbox')
    fireEvent.click(checkboxes[0])
    await waitFor(() => expect(screen.getByText('Analyze Selected (1)')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Analyze Selected (1)'))

    await waitFor(() => expect(screen.getByText('Accept Selected')).toBeInTheDocument())
    expect(screen.getByText('Python')).toBeInTheDocument()
  })

  it('clicking a document clears extraction results', async () => {
    const docs = [
      { id: '1', original_name: 'r.pdf', stored_name: '1_r.pdf', display_name: 'r.pdf', tags: [], uploaded_at: '2026-01-01T00:00:00Z', size_bytes: 100, mime_type: 'application/pdf' },
    ]
    vi.stubGlobal('fetch', makeFetch({ '/api/documents': docs }))
    render(<DocumentManager />)

    await waitFor(() => expect(screen.getByText('r.pdf')).toBeInTheDocument())

    const checkboxes = screen.getAllByRole('checkbox')
    fireEvent.click(checkboxes[0])
    await waitFor(() => expect(screen.getByText('Analyze Selected (1)')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Analyze Selected (1)'))
    await waitFor(() => expect(screen.getByText('Accept Selected')).toBeInTheDocument())

    fireEvent.click(screen.getByText('r.pdf'))
    await waitFor(() => expect(screen.queryByText('Accept Selected')).not.toBeInTheDocument())
  })

  it('deleting a checked document removes it from checkedIds', async () => {
    const docs = [
      { id: '1', original_name: 'r.pdf', stored_name: '1_r.pdf', display_name: 'r.pdf', tags: [], uploaded_at: '2026-01-01T00:00:00Z', size_bytes: 100, mime_type: 'application/pdf' },
    ]
    const mockFetch = makeFetch({ '/api/documents': docs })
    mockFetch.mockImplementation((url: string, opts?: RequestInit) => {
      if (url === '/api/tags') return Promise.resolve({ ok: true, json: async () => [] })
      if (url === '/api/profile') return Promise.resolve({ ok: true, json: async () => emptyProfile })
      if (/^\/api\/documents(\?.*)?$/.test(url) && opts?.method !== 'DELETE') return Promise.resolve({ ok: true, json: async () => docs })
      if (/^\/api\/documents\/[^/]+$/.test(url) && opts?.method === 'DELETE') return Promise.resolve({ ok: true, json: async () => ({}) })
      if (/^\/api\/documents\/[^/]+$/.test(url)) return Promise.resolve({ ok: true, json: async () => docs[0] })
      return Promise.resolve({ ok: true, json: async () => [] })
    })
    vi.stubGlobal('fetch', mockFetch)
    render(<DocumentManager />)

    await waitFor(() => expect(screen.getByText('r.pdf')).toBeInTheDocument())
    const checkboxes = screen.getAllByRole('checkbox')
    fireEvent.click(checkboxes[0])
    await waitFor(() => expect(screen.getByText('Analyze Selected (1)')).toBeInTheDocument())

    fireEvent.click(screen.getByText('r.pdf'))
    await waitFor(() => expect(screen.getByText('Delete')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Delete'))

    // After deletion, checkedIds no longer has '1' → button reverts to "Analyze All"
    await waitFor(() => expect(screen.getByText('Analyze All')).toBeInTheDocument())
    expect(screen.queryByText(/analyze selected/i)).not.toBeInTheDocument()
  })

  it('checking a tag checkbox adds all docs with that tag to checkedIds', async () => {
    const docs = [
      { id: '1', original_name: 'r.pdf', stored_name: '1_r.pdf', display_name: 'r.pdf', tags: ['resume'], uploaded_at: '2026-01-01T00:00:00Z', size_bytes: 100, mime_type: 'application/pdf' },
      { id: '2', original_name: 's.pdf', stored_name: '2_s.pdf', display_name: 's.pdf', tags: ['resume'], uploaded_at: '2026-01-01T00:00:00Z', size_bytes: 100, mime_type: 'application/pdf' },
    ]
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url === '/api/tags') return Promise.resolve({ ok: true, json: async () => ['resume'] })
      if (url === '/api/profile') return Promise.resolve({ ok: true, json: async () => emptyProfile })
      if (/^\/api\/documents(\?.*)?$/.test(url)) return Promise.resolve({ ok: true, json: async () => docs })
      return Promise.resolve({ ok: true, json: async () => [] })
    }))
    render(<DocumentManager />)

    await waitFor(() => expect(screen.getByText('resume')).toBeInTheDocument())

    // Click the tag's checkbox — all 2 docs should be checked → button shows (2)
    const tagCheckbox = screen.getByLabelText('Select all resume documents')
    fireEvent.click(tagCheckbox)

    await waitFor(() => expect(screen.getByText('Analyze Selected (2)')).toBeInTheDocument())
  })

  it('checking a tag when all its docs are already checked removes them all', async () => {
    const docs = [
      { id: '1', original_name: 'r.pdf', stored_name: '1_r.pdf', display_name: 'r.pdf', tags: ['resume'], uploaded_at: '2026-01-01T00:00:00Z', size_bytes: 100, mime_type: 'application/pdf' },
    ]
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url === '/api/tags') return Promise.resolve({ ok: true, json: async () => ['resume'] })
      if (url === '/api/profile') return Promise.resolve({ ok: true, json: async () => emptyProfile })
      if (/^\/api\/documents(\?.*)?$/.test(url)) return Promise.resolve({ ok: true, json: async () => docs })
      return Promise.resolve({ ok: true, json: async () => [] })
    }))
    render(<DocumentManager />)

    await waitFor(() => expect(screen.getByText('resume')).toBeInTheDocument())

    const tagCheckbox = screen.getByLabelText('Select all resume documents')
    // First click: adds doc '1'
    fireEvent.click(tagCheckbox)
    await waitFor(() => expect(screen.getByText('Analyze Selected (1)')).toBeInTheDocument())

    // Second click: all docs for 'resume' are checked → removes them → back to "Analyze All"
    fireEvent.click(tagCheckbox)
    await waitFor(() => expect(screen.getByText('Analyze All')).toBeInTheDocument())
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /c/Users/whweb/Code/haid-hunter && npx vitest run src/__tests__/documents/DocumentManager.test.tsx 2>&1 | tail -20
```

Expected: FAIL — "Analyze All" not found (button hidden at 0 checked), `onCheckTag` not passed to TagSidebar, `checkedIds` not passed to TagSidebar.

- [ ] **Step 3: Update `src/components/documents/DocumentManager.tsx`**

Read the current file first. Make two targeted changes:

**Change 1** — Add `handleCheckTag` after `handleCheck`:

```typescript
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

**Change 2** — Add `checkedIds` and `onCheckTag` to the `<TagSidebar>` JSX:

```tsx
        <TagSidebar
          tags={tags}
          allDocuments={allDocuments}
          activeTag={activeTag}
          onSelectTag={setActiveTag}
          onCreateTag={handleCreateTag}
          onDeleteTag={handleDeleteTag}
          checkedIds={checkedIds}
          onCheckTag={handleCheckTag}
        />
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /c/Users/whweb/Code/haid-hunter && npx vitest run src/__tests__/documents/DocumentManager.test.tsx 2>&1 | tail -10
```

Expected: All tests PASS.

- [ ] **Step 5: Run the full test suite**

```bash
cd /c/Users/whweb/Code/haid-hunter && npx vitest run 2>&1 | tail -8
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
cd /c/Users/whweb/Code/haid-hunter && git add src/components/documents/DocumentManager.tsx src/__tests__/documents/DocumentManager.test.tsx && git commit -m "feat: wire tag checkbox selection and analyze all in DocumentManager"
```

---

## Task 4: CSS — tag checkbox style

**Files:**
- Modify: `src/index.css`

- [ ] **Step 1: Find the `.document-checkbox` rule**

Search for:
```css
.document-checkbox {
```

- [ ] **Step 2: Add tag checkbox style immediately after it**

```css
.tag-checkbox { flex-shrink: 0; width: 13px; height: 13px; cursor: pointer; accent-color: var(--color-primary); margin-right: var(--space-xs); }
```

- [ ] **Step 3: Run tests to confirm nothing broke**

```bash
cd /c/Users/whweb/Code/haid-hunter && npx vitest run 2>&1 | tail -5
```

Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
cd /c/Users/whweb/Code/haid-hunter && git add src/index.css && git commit -m "style: add tag-checkbox style"
```
