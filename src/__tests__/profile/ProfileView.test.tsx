import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ProfileView from '../../components/profile/ProfileView'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ summary: '', skills: [], experience: [], education: [], certifications: [], objectives: [] }),
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
})
