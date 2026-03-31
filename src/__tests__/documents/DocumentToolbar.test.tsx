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

  it('does not show Analyze Selected when checkedCount is 0', () => {
    render(<DocumentToolbar {...baseProps} checkedCount={0} />)
    expect(screen.queryByText(/analyze selected/i)).not.toBeInTheDocument()
  })

  it('shows Analyze Selected button when checkedCount > 0', () => {
    render(<DocumentToolbar {...baseProps} checkedCount={2} />)
    expect(screen.getByText(/analyze selected/i)).toBeInTheDocument()
  })

  it('Analyze Selected button calls onAnalyze when clicked', async () => {
    const onAnalyze = vi.fn()
    render(<DocumentToolbar {...baseProps} checkedCount={1} onAnalyze={onAnalyze} />)
    await userEvent.click(screen.getByText(/analyze selected/i))
    expect(onAnalyze).toHaveBeenCalled()
  })

  it('Analyze Selected button is disabled while extractionLoading is true', () => {
    render(<DocumentToolbar {...baseProps} checkedCount={1} extractionLoading={true} />)
    expect(screen.getByText(/analyzing/i)).toBeDisabled()
  })
})
