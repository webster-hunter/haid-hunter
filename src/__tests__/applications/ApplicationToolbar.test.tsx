import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ApplicationToolbar from '../../components/applications/ApplicationToolbar'

describe('ApplicationToolbar', () => {
  it('includes interviewing and rejected in status filter dropdown', () => {
    render(
      <ApplicationToolbar
        search=""
        onSearchChange={() => {}}
        statusFilter=""
        onStatusFilterChange={() => {}}
        viewMode="table"
        onViewModeChange={() => {}}
        onAdd={() => {}}
      />
    )
    const options = screen.getAllByRole('option')
    const values = options.map(o => (o as HTMLOptionElement).value)
    expect(values).toContain('interviewing')
    expect(values).toContain('rejected')
  })
})
