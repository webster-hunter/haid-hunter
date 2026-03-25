import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import StatusBadge from '../../components/applications/StatusBadge'

describe('StatusBadge', () => {
  it('renders interviewing status with label and class', () => {
    render(<StatusBadge status="interviewing" />)
    const badge = screen.getByText('Interviewing')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('status-badge')
    expect(badge.className).toContain('status-')
  })

  it('renders rejected status with label and class', () => {
    render(<StatusBadge status="rejected" />)
    const badge = screen.getByText('Rejected')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('status-badge')
    expect(badge.className).toContain('status-')
  })
})
