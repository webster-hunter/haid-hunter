import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { DocumentPreview } from '../../components/documents/DocumentPreview'
import type { DocumentMeta } from '../../api/documents'

const mockTxtDoc: DocumentMeta = {
  id: '1', original_name: 'notes.txt', stored_name: '1_notes.txt',
  display_name: 'notes.txt', tags: ['resume'], uploaded_at: '2026-03-20T00:00:00Z',
  size_bytes: 500, mime_type: 'text/plain',
}

const mockDocxDoc: DocumentMeta = {
  id: '2', original_name: 'resume.docx', stored_name: '2_resume.docx',
  display_name: 'resume.docx', tags: [], uploaded_at: '2026-03-20T00:00:00Z',
  size_bytes: 38000, mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}

describe('DocumentPreview', () => {
  it('shows document name and metadata', () => {
    render(<DocumentPreview document={mockTxtDoc} allTags={['resume', 'cv']} onUpdate={() => {}} onDelete={() => {}} />)
    expect(screen.getByText('notes.txt')).toBeInTheDocument()
  })

  it('shows download and delete buttons', () => {
    render(<DocumentPreview document={mockTxtDoc} allTags={['resume']} onUpdate={() => {}} onDelete={() => {}} />)
    expect(screen.getByText(/download/i)).toBeInTheDocument()
    expect(screen.getByText(/delete/i)).toBeInTheDocument()
  })

  it('shows file info for non-previewable types', () => {
    render(<DocumentPreview document={mockDocxDoc} allTags={[]} onUpdate={() => {}} onDelete={() => {}} />)
    expect(screen.getByText(/no preview available/i)).toBeInTheDocument()
  })

  it('calls onDelete when delete is clicked', async () => {
    const onDelete = vi.fn()
    render(<DocumentPreview document={mockTxtDoc} allTags={[]} onUpdate={() => {}} onDelete={onDelete} />)
    await userEvent.click(screen.getByText(/delete/i))
    expect(onDelete).toHaveBeenCalled()
  })

  it('shows an Open button that opens file in new tab', () => {
    render(<DocumentPreview document={mockTxtDoc} allTags={[]} onUpdate={() => {}} onDelete={() => {}} />)
    const openLink = screen.getByText(/^open$/i).closest('a')
    expect(openLink).toHaveAttribute('href', '/api/documents/1/content')
    expect(openLink).toHaveAttribute('target', '_blank')
  })

  it('download link uses download param and does not open in new tab', () => {
    render(<DocumentPreview document={mockTxtDoc} allTags={[]} onUpdate={() => {}} onDelete={() => {}} />)
    const downloadLink = screen.getByText(/download/i).closest('a')
    expect(downloadLink).toHaveAttribute('download')
    expect(downloadLink).toHaveAttribute('href', '/api/documents/1/content?download=true')
    expect(downloadLink).not.toHaveAttribute('target', '_blank')
  })
})
