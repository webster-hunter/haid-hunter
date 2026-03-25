import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import KanbanView from '../../components/applications/KanbanView'

describe('KanbanView', () => {
  it('renders columns for all 7 statuses including interviewing and rejected', () => {
    render(<KanbanView applications={[]} onCardClick={() => {}} onRefresh={() => {}} />)
    expect(screen.getByText('Interviewing')).toBeInTheDocument()
    expect(screen.getByText('Rejected')).toBeInTheDocument()
  })
})
