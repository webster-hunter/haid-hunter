import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ExtractionResultsPanel from '../../components/documents/ExtractionResultsPanel'
import type { ExtractionResult, SelectionState } from '../../api/extraction'

const fullResult: ExtractionResult = {
  skills: ['Python', 'React'],
  technologies: ['Docker'],
  experience_keywords: ['led team of 5'],
  soft_skills: ['communication'],
}

const allSelected: SelectionState = {
  skills: { Python: true, React: true },
  technologies: { Docker: true },
  experience_keywords: { 'led team of 5': true },
  soft_skills: { communication: true },
}

const baseProps = {
  result: fullResult,
  selection: allSelected,
  existingSkills: [],
  onToggle: vi.fn(),
  onAccept: vi.fn(),
  onReanalyze: vi.fn(),
  onDismiss: vi.fn(),
}

describe('ExtractionResultsPanel', () => {
  it('renders chips for each category', () => {
    render(<ExtractionResultsPanel {...baseProps} />)
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Docker')).toBeInTheDocument()
    expect(screen.getByText('led team of 5')).toBeInTheDocument()
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
      experience_keywords: { 'led team of 5': true },
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
    const empty: ExtractionResult = { skills: [], technologies: [], experience_keywords: [], soft_skills: [] }
    render(<ExtractionResultsPanel {...baseProps} result={empty} selection={{}} />)
    expect(screen.getByText('No suggestions found.')).toBeInTheDocument()
  })

  it('shows all-in-profile message when every item is already in profile', () => {
    const existingSkills = ['Python', 'React', 'Docker', 'led team of 5', 'communication']
    render(<ExtractionResultsPanel {...baseProps} existingSkills={existingSkills} />)
    expect(screen.getByText('All suggestions already in your profile.')).toBeInTheDocument()
  })

  it('renders already-in-profile chips with already-in-profile class and no click handler effect', () => {
    const onToggle = vi.fn()
    render(
      <ExtractionResultsPanel
        {...baseProps}
        existingSkills={['Python']}
        onToggle={onToggle}
      />
    )
    const pythonChip = screen.getByText('Python')
    expect(pythonChip).toHaveClass('already-in-profile')
    fireEvent.click(pythonChip)
    expect(onToggle).not.toHaveBeenCalled()
  })

  it('does not include already-in-profile chips in Accept payload', () => {
    const onToggle = vi.fn()
    render(
      <ExtractionResultsPanel
        {...baseProps}
        existingSkills={['Python']}
        onToggle={onToggle}
      />
    )
    const pythonChip = screen.getByText('Python')
    fireEvent.click(pythonChip)
    expect(onToggle).not.toHaveBeenCalled()
    expect(pythonChip).not.toHaveClass('deselected')
  })
})
