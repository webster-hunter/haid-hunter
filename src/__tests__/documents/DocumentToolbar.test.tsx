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
