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
    render(<DocumentList documents={mockDocs} selectedId={null} onSelect={() => {}} checkedIds={new Set()} onCheck={() => {}} />)
    expect(screen.getByText('resume.pdf')).toBeInTheDocument()
    expect(screen.getByText('notes.txt')).toBeInTheDocument()
  })

  it('highlights selected document', () => {
    render(<DocumentList documents={mockDocs} selectedId="1" onSelect={() => {}} checkedIds={new Set()} onCheck={() => {}} />)
    const item = screen.getByText('resume.pdf').closest('.document-item')
    expect(item).toHaveClass('selected')
  })

  it('calls onSelect when item row is clicked', async () => {
    const onSelect = vi.fn()
    render(<DocumentList documents={mockDocs} selectedId={null} onSelect={onSelect} checkedIds={new Set()} onCheck={() => {}} />)
    await userEvent.click(screen.getByText('resume.pdf'))
    expect(onSelect).toHaveBeenCalledWith('1')
  })

  it('renders a checkbox for each document', () => {
    render(<DocumentList documents={mockDocs} selectedId={null} onSelect={() => {}} checkedIds={new Set()} onCheck={() => {}} />)
    const checkboxes = screen.getAllByRole('checkbox')
    expect(checkboxes).toHaveLength(2)
  })

  it('checkbox is checked when id is in checkedIds', () => {
    render(<DocumentList documents={mockDocs} selectedId={null} onSelect={() => {}} checkedIds={new Set(['1'])} onCheck={() => {}} />)
    const checkboxes = screen.getAllByRole('checkbox')
    expect(checkboxes[0]).toBeChecked()
    expect(checkboxes[1]).not.toBeChecked()
  })

  it('calls onCheck with document id when checkbox is clicked', async () => {
    const onCheck = vi.fn()
    render(<DocumentList documents={mockDocs} selectedId={null} onSelect={() => {}} checkedIds={new Set()} onCheck={onCheck} />)
    const checkboxes = screen.getAllByRole('checkbox')
    await userEvent.click(checkboxes[0])
    expect(onCheck).toHaveBeenCalledWith('1')
  })

  it('clicking checkbox does not also call onSelect', async () => {
    const onSelect = vi.fn()
    const onCheck = vi.fn()
    render(<DocumentList documents={mockDocs} selectedId={null} onSelect={onSelect} checkedIds={new Set()} onCheck={onCheck} />)
    const checkboxes = screen.getAllByRole('checkbox')
    await userEvent.click(checkboxes[0])
    expect(onCheck).toHaveBeenCalledWith('1')
    expect(onSelect).not.toHaveBeenCalled()
  })
})
