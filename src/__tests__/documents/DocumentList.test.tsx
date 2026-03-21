import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { DocumentList } from '../../components/documents/DocumentList'
import type { DocumentMeta } from '../../api/documents'

const mockDocs: DocumentMeta[] = [
  { id: '1', original_name: 'resume.pdf', stored_name: '1_resume.pdf', display_name: 'resume.pdf', tags: ['resume'], uploaded_at: '2026-03-20T00:00:00Z', size_bytes: 245000, mime_type: 'application/pdf' },
  { id: '2', original_name: 'notes.txt', stored_name: '2_notes.txt', display_name: 'notes.txt', tags: [], uploaded_at: '2026-03-19T00:00:00Z', size_bytes: 500, mime_type: 'text/plain' },
]

describe('DocumentList', () => {
  it('renders document items', () => {
    render(<DocumentList documents={mockDocs} selectedId={null} onSelect={() => {}} />)
    expect(screen.getByText('resume.pdf')).toBeInTheDocument()
    expect(screen.getByText('notes.txt')).toBeInTheDocument()
  })

  it('highlights selected document', () => {
    render(<DocumentList documents={mockDocs} selectedId="1" onSelect={() => {}} />)
    const item = screen.getByText('resume.pdf').closest('.document-item')
    expect(item).toHaveClass('selected')
  })

  it('calls onSelect when item is clicked', async () => {
    const onSelect = vi.fn()
    render(<DocumentList documents={mockDocs} selectedId={null} onSelect={onSelect} />)
    await userEvent.click(screen.getByText('resume.pdf'))
    expect(onSelect).toHaveBeenCalledWith('1')
  })
})
