import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ExtractionResultsPanel from '../../components/documents/ExtractionResultsPanel'
import type { ExtractionResult, SelectionState } from '../../api/extraction'

const fullResult: ExtractionResult = {
  skills: ['Python', 'React'],
  technologies: ['Docker'],
  soft_skills: ['communication'],
}

const allSelected: SelectionState = {
  skills: { Python: true, React: true },
  technologies: { Docker: true },
  soft_skills: { communication: true },
}

const baseProps = {
  result: fullResult,
  selection: allSelected,
  onToggle: vi.fn(),
  onAccept: vi.fn(),
  onReanalyze: vi.fn(),
  onDismiss: vi.fn(),
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('ExtractionResultsPanel', () => {
  it('renders chips for each category', () => {
    render(<ExtractionResultsPanel {...baseProps} />)
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Docker')).toBeInTheDocument()
    expect(screen.getByText('communication')).toBeInTheDocument()
  })

  it('calls onToggle when a chip is clicked', () => {
    const onToggle = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onToggle={onToggle} />)
    fireEvent.click(screen.getByText('Python'))
    expect(onToggle).toHaveBeenCalledWith('skills', 'Python')
  })

  it('applies deselected class to toggled-off chips', () => {
    const selection: SelectionState = {
      skills: { Python: false, React: true },
      technologies: { Docker: true },
            soft_skills: { communication: true },
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
    const empty: ExtractionResult = { skills: [], technologies: [], soft_skills: [] }
    render(<ExtractionResultsPanel {...baseProps} result={empty} selection={{}} />)
    expect(screen.getByText('No suggestions found.')).toBeInTheDocument()
  })

  it('profile items passed as selected=true start without deselected class', () => {
    const selection: SelectionState = {
      skills: { Python: true, React: false },
      technologies: { Docker: true },
            soft_skills: { communication: true },
    }
    render(<ExtractionResultsPanel {...baseProps} selection={selection} />)
    expect(screen.getByText('Python')).not.toHaveClass('deselected')
  })

  it('profile items (selected=true) are clickable and call onToggle', () => {
    const onToggle = vi.fn()
    render(<ExtractionResultsPanel {...baseProps} onToggle={onToggle} />)
    fireEvent.click(screen.getByText('Python'))
    expect(onToggle).toHaveBeenCalledWith('skills', 'Python')
  })

  it('deselecting a previously-selected item applies deselected class', () => {
    const selection: SelectionState = {
      skills: { Python: false, React: true },
      technologies: { Docker: true },
            soft_skills: { communication: true },
    }
    render(<ExtractionResultsPanel {...baseProps} selection={selection} />)
    expect(screen.getByText('Python')).toHaveClass('deselected')
    expect(screen.getByText('React')).not.toHaveClass('deselected')
  })
})
