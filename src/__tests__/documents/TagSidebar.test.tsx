import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { TagSidebar } from '../../components/documents/TagSidebar'
import type { DocumentMeta } from '../../api/documents'

const mockDocs: DocumentMeta[] = [
  { id: '1', original_name: 'a.txt', stored_name: '1_a.txt', display_name: 'a.txt', tags: ['resume'], uploaded_at: '', size_bytes: 10, mime_type: 'text/plain' },
  { id: '2', original_name: 'b.txt', stored_name: '2_b.txt', display_name: 'b.txt', tags: ['resume', 'cv'], uploaded_at: '', size_bytes: 20, mime_type: 'text/plain' },
]

describe('TagSidebar', () => {
  it('shows All Documents with total count', () => {
    render(<TagSidebar tags={['resume', 'cv']} documents={mockDocs} activeTag={null} onSelectTag={() => {}} onCreateTag={() => {}} onDeleteTag={() => {}} />)
    expect(screen.getByText('All Documents')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('shows tag counts', () => {
    render(<TagSidebar tags={['resume', 'cv']} documents={mockDocs} activeTag={null} onSelectTag={() => {}} onCreateTag={() => {}} onDeleteTag={() => {}} />)
    const resumeItem = screen.getByText('resume').closest('[data-testid]')
    expect(resumeItem).toBeInTheDocument()
  })

  it('calls onSelectTag when tag is clicked', async () => {
    const onSelect = vi.fn()
    render(<TagSidebar tags={['resume', 'cv']} documents={mockDocs} activeTag={null} onSelectTag={onSelect} onCreateTag={() => {}} onDeleteTag={() => {}} />)
    await userEvent.click(screen.getByText('resume'))
    expect(onSelect).toHaveBeenCalledWith('resume')
  })
})
