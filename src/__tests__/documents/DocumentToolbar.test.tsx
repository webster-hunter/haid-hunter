import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { DocumentToolbar } from '../../components/documents/DocumentToolbar'

describe('DocumentToolbar', () => {
  it('renders search input', () => {
    render(<DocumentToolbar search="" onSearchChange={() => {}} onUpload={() => {}} onSync={() => {}} />)
    expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument()
  })

  it('calls onSearchChange when typing', async () => {
    const onChange = vi.fn()
    render(<DocumentToolbar search="" onSearchChange={onChange} onUpload={() => {}} onSync={() => {}} />)
    await userEvent.type(screen.getByPlaceholderText(/search/i), 'test')
    expect(onChange).toHaveBeenCalled()
  })

  it('has upload and sync buttons', () => {
    render(<DocumentToolbar search="" onSearchChange={() => {}} onUpload={() => {}} onSync={() => {}} />)
    expect(screen.getByText(/upload/i)).toBeInTheDocument()
    expect(screen.getByText(/sync/i)).toBeInTheDocument()
  })
})
