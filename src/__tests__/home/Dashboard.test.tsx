import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import Dashboard from '../../components/home/Dashboard'

const mockDashboardData = {
  profile: {
    summary: 'Full-stack engineer with 8 years experience',
    skills: ['TypeScript', 'React', 'Python', 'Go'],
    current_role: 'Senior Dev at Acme (2021 - Present)',
  },
  documents: {
    total: 12,
    by_tag: { resume: 5, 'cover-letter': 4, cv: 3 },
  },
  applications: {
    total: 23,
    by_status: { bookmarked: 8, applied: 5, in_progress: 6, offer: 2, closed: 2 },
    referrals: {
      total: 2,
      contacts: [
        { name: 'Jane', company: 'Google', application_id: 1 },
        { name: 'Bob', company: 'Meta', application_id: 2 },
      ],
    },
  },
  tasks: {
    daily_target: 5,
    applied_today: 2,
    statuses_current: true,
    stale_count: 0,
    user_tasks: [
      { id: 1, title: 'Review LinkedIn', recurrence: 'custom', interval_days: 3, is_due: true, completed_today: false, completed_at: null },
    ],
  },
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: async () => mockDashboardData,
  }))
})

describe('Dashboard', () => {
  it('renders profile banner after loading', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText(/Full-stack engineer/)).toBeInTheDocument()
  })

  it('renders document stat card', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText('Documents')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
  })

  it('renders application stat card', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText('Applications')).toBeInTheDocument()
    expect(screen.getByText('23')).toBeInTheDocument()
  })

  it('renders referrals card with popover trigger', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText('Referrals')).toBeInTheDocument()
    expect(screen.getByText('View all referrals →')).toBeInTheDocument()
  })

  it('opens referral popover on click', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    const trigger = await screen.findByText('View all referrals →')
    fireEvent.click(trigger)
    expect(screen.getByTestId('referral-popover')).toBeInTheDocument()
    expect(screen.getByText('Jane')).toBeInTheDocument()
  })

  it('renders daily tasks section', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText('Tasks')).toBeInTheDocument()
    expect(screen.getByText('Review LinkedIn')).toBeInTheDocument()
  })

  it('renders phase II placeholder', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText('Phase II')).toBeInTheDocument()
    expect(screen.getByText('Next Steps')).toBeInTheDocument()
  })

  it('shows error state on fetch failure', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false }))
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText(/failed to load/i)).toBeInTheDocument()
    expect(screen.getByText('Retry')).toBeInTheDocument()
  })

  it('shows task error when toggle fails', async () => {
    let callCount = 0
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string, opts?: RequestInit) => {
      callCount++
      if (opts?.method === 'PATCH') {
        return Promise.resolve({ ok: false, status: 500 })
      }
      return Promise.resolve({ ok: true, json: async () => mockDashboardData })
    }))
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    await screen.findByText('Review LinkedIn')
    const checkbox = screen.getByTestId('task-checkbox-1')
    fireEvent.click(checkbox)
    expect(await screen.findByText(/failed/i)).toBeInTheDocument()
  })
})
