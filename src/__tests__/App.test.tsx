import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import App from '../App'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      profile: { summary: '', skills: [], current_role: null },
      documents: { total: 0, by_tag: {} },
      applications: { total: 0, by_status: {}, referrals: { total: 0, contacts: [] } },
      tasks: { daily_target: 5, applied_today: 0, statuses_current: true, stale_count: 0, user_tasks: [] },
    }),
  }))
})

describe('App routing', () => {
  it('renders navigation bar', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })

  it('has links to all sections', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )
    expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /documents/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /profile/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /applications/i })).toBeInTheDocument()
  })
})
