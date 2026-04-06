import { render, screen } from '@testing-library/react'
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
    expect(screen.getByText('(2)')).toBeInTheDocument() // resume has 2 docs
    expect(screen.getByText('(1)')).toBeInTheDocument() // cv has 1 doc
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
    expect(screen.getByRole('checkbox', { name: 'Select all resume documents' })).toBeChecked()
  })

  it('checkbox is unchecked when only some docs for that tag are in checkedIds', () => {
    render(<TagSidebar {...baseProps} checkedIds={new Set(['1'])} />)
    expect(screen.getByRole('checkbox', { name: 'Select all resume documents' })).not.toBeChecked()
  })

  it('calls onCheckTag with tag name when checkbox is clicked', async () => {
    const onCheckTag = vi.fn()
    render(<TagSidebar {...baseProps} onCheckTag={onCheckTag} />)
    await userEvent.click(screen.getByRole('checkbox', { name: 'Select all resume documents' }))
    expect(onCheckTag).toHaveBeenCalledWith('resume')
  })

  it('clicking tag checkbox does not call onSelectTag', async () => {
    const onSelectTag = vi.fn()
    const onCheckTag = vi.fn()
    render(<TagSidebar {...baseProps} onSelectTag={onSelectTag} onCheckTag={onCheckTag} />)
    await userEvent.click(screen.getByRole('checkbox', { name: 'Select all resume documents' }))
    expect(onSelectTag).not.toHaveBeenCalled()
  })
})
