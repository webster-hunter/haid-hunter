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
