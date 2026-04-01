import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import DocumentManager from '../../components/documents/DocumentManager'

const emptyProfile = { summary: '', skills: [], experience: [], activities: [], education: [], certifications: [] }
const extractionResult = {
  skills: ['Python'],
  technologies: ['Docker'],
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

    await waitFor(() => expect(screen.getByLabelText('Select all resume documents')).toBeInTheDocument())

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

    await waitFor(() => expect(screen.getByLabelText('Select all resume documents')).toBeInTheDocument())

    const tagCheckbox = screen.getByLabelText('Select all resume documents')
    // First click: adds doc '1'
    fireEvent.click(tagCheckbox)
    await waitFor(() => expect(screen.getByText('Analyze Selected (1)')).toBeInTheDocument())

    // Second click: all docs for 'resume' are checked → removes them → back to "Analyze All"
    fireEvent.click(tagCheckbox)
    await waitFor(() => expect(screen.getByText('Analyze All')).toBeInTheDocument())
  })
})
