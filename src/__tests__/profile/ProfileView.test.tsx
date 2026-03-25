import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ProfileView from '../../components/profile/ProfileView'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ summary: '', skills: [], experience: [], activities: [], education: [], certifications: [] }),
  }))
})

describe('ProfileView', () => {
  it('renders profile panel', async () => {
    render(<ProfileView />)
    expect(await screen.findByTestId('profile-panel')).toBeInTheDocument()
  })

  it('renders interview chat', async () => {
    render(<ProfileView />)
    expect(await screen.findByTestId('interview-chat')).toBeInTheDocument()
  })

  it('renders page title', async () => {
    render(<ProfileView />)
    expect(await screen.findByText('Profile')).toBeInTheDocument()
  })

  it('shows error message when fetch fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    }))
    render(<ProfileView />)
    expect(await screen.findByText(/failed to load profile/i)).toBeInTheDocument()
  })

  it('shows retry button on error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    }))
    render(<ProfileView />)
    expect(await screen.findByText(/retry/i)).toBeInTheDocument()
  })
})
