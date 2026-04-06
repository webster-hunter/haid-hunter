import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ExtractionResultsPanel from '../../components/documents/ExtractionResultsPanel'
import type { ExtractionResult, SelectionState } from '../../api/extraction'

const fullResult: ExtractionResult = {
  skills: [
    { name: 'Python', type: 'Programming Languages' },
    { name: 'React', type: 'Frontend' },
    { name: 'Docker', type: 'DevOps & Infrastructure' },
    { name: 'communication', type: 'Interpersonal' },
  ],
}

const allSelected: SelectionState = {
  Python: true,
  React: true,
  Docker: true,
  communication: true,
}

const baseProps = {
  result: fullResult,
  selection: allSelected,
  onToggle: vi.fn(),
  onToggleAll: vi.fn(),
  onAccept: vi.fn(),
  onReanalyze: vi.fn(),
  onDismiss: vi.fn(),
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('ExtractionResultsPanel', () => {
  it('renders chips for each skill', () => {
    render(<ExtractionResultsPanel {...baseProps} />)
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Docker')).toBeInTheDocument()
    expect(screen.getByText('communication')).toBeInTheDocument()
  })

  it('renders type headings', () => {
    render(<ExtractionResultsPanel {...baseProps} />)
    expect(screen.getByText('Programming Languages')).toBeInTheDocument()
    expect(screen.getByText('Frontend')).toBeInTheDocument()
    expect(screen.getByText('DevOps & Infrastructure')).toBeInTheDocument()
    expect(screen.getByText('Interpersonal')).toBeInTheDocument()
  })

  it('calls onToggle with skill name when a chip is clicked', () => {
    const onToggle = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onToggle={onToggle} />)
    fireEvent.click(screen.getByText('Python'))
    expect(onToggle).toHaveBeenCalledWith('Python')
  })

  it('applies deselected class to toggled-off chips', () => {
    const selection: SelectionState = {
      Python: false,
      React: true,
      Docker: true,
      communication: true,
    }
    render(<ExtractionResultsPanel {...baseProps} selection={selection} />)
    expect(screen.getByText('Python')).toHaveClass('deselected')
    expect(screen.getByText('React')).not.toHaveClass('deselected')
  })

  it('calls onAccept when Accept Selected is clicked', () => {
    const onAccept = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onAccept={onAccept} />)
    fireEvent.click(screen.getByText('Accept Selected'))
    expect(onAccept).toHaveBeenCalled()
  })

  it('calls onReanalyze when Re-analyze is clicked', () => {
    const onReanalyze = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onReanalyze={onReanalyze} />)
    fireEvent.click(screen.getByText('Re-analyze'))
    expect(onReanalyze).toHaveBeenCalled()
  })

  it('calls onDismiss when Done is clicked', () => {
    const onDismiss = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onDismiss={onDismiss} />)
    fireEvent.click(screen.getByText('Done'))
    expect(onDismiss).toHaveBeenCalled()
  })

  it('shows No suggestions found when result is empty', () => {
    const empty: ExtractionResult = { skills: [] }
    render(<ExtractionResultsPanel {...baseProps} result={empty} selection={{}} />)
    expect(screen.getByText('No suggestions found.')).toBeInTheDocument()
  })

  it('profile items passed as selected=true start without deselected class', () => {
    const selection: SelectionState = {
      Python: true,
      React: false,
      Docker: true,
      communication: true,
    }
    render(<ExtractionResultsPanel {...baseProps} selection={selection} />)
    expect(screen.getByText('Python')).not.toHaveClass('deselected')
  })

  it('profile items (selected=true) are clickable and call onToggle', () => {
    const onToggle = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onToggle={onToggle} />)
    fireEvent.click(screen.getByText('Python'))
    expect(onToggle).toHaveBeenCalledWith('Python')
  })

  it('deselecting a previously-selected item applies deselected class', () => {
    const selection: SelectionState = {
      Python: false,
      React: true,
      Docker: true,
      communication: true,
    }
    render(<ExtractionResultsPanel {...baseProps} selection={selection} />)
    expect(screen.getByText('Python')).toHaveClass('deselected')
    expect(screen.getByText('React')).not.toHaveClass('deselected')
  })

  it('shows Deselect All when all are selected', () => {
    render(<ExtractionResultsPanel {...baseProps} />)
    expect(screen.getByText('Deselect All')).toBeInTheDocument()
  })

  it('shows Select All when not all are selected', () => {
    const selection: SelectionState = { Python: true, React: false, Docker: true, communication: true }
    render(<ExtractionResultsPanel {...baseProps} selection={selection} />)
    expect(screen.getByText('Select All')).toBeInTheDocument()
  })

  it('calls onToggleAll(false) when Deselect All is clicked', () => {
    const onToggleAll = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onToggleAll={onToggleAll} />)
    fireEvent.click(screen.getByText('Deselect All'))
    expect(onToggleAll).toHaveBeenCalledWith(false)
  })

  it('calls onToggleAll(true) when Select All is clicked', () => {
    const onToggleAll = vi.fn()
    const selection: SelectionState = { Python: false, React: false, Docker: false, communication: false }
    render(<ExtractionResultsPanel {...baseProps} selection={selection} onToggleAll={onToggleAll} />)
    fireEvent.click(screen.getByText('Select All'))
    expect(onToggleAll).toHaveBeenCalledWith(true)
  })
})
