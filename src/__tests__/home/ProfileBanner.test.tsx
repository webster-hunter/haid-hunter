import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ProfileBanner } from '../../components/home/ProfileBanner'

describe('ProfileBanner', () => {
  it('renders summary and current role', () => {
    render(
      <MemoryRouter>
        <ProfileBanner
          summary="Full-stack engineer with 8 years experience"
          skills={[
            { name: 'TypeScript', type: 'Programming Languages' },
            { name: 'React', type: 'Frontend' },
            { name: 'Python', type: 'Programming Languages' },
            { name: 'Go', type: 'Programming Languages' },
            { name: 'Rust', type: 'Programming Languages' },
          ]}
          currentRole="Senior Dev at Acme (2021 - Present)"
        />
      </MemoryRouter>
    )
    expect(screen.getByText(/Full-stack engineer/)).toBeInTheDocument()
    expect(screen.getByText(/Senior Dev at Acme/)).toBeInTheDocument()
  })

  it('shows first 3 skills plus overflow count', () => {
    render(
      <MemoryRouter>
        <ProfileBanner
          summary="Engineer"
          skills={[
            { name: 'TypeScript', type: 'Programming Languages' },
            { name: 'React', type: 'Frontend' },
            { name: 'Python', type: 'Programming Languages' },
            { name: 'Go', type: 'Programming Languages' },
            { name: 'Rust', type: 'Programming Languages' },
          ]}
          currentRole={null}
        />
      </MemoryRouter>
    )
    expect(screen.getByText('TypeScript')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('+2 more')).toBeInTheDocument()
    expect(screen.queryByText('Go')).not.toBeInTheDocument()
  })

  it('shows empty state when no summary', () => {
    render(
      <MemoryRouter>
        <ProfileBanner summary="" skills={[]} currentRole={null} />
      </MemoryRouter>
    )
    expect(screen.getByText(/Set up your profile/)).toBeInTheDocument()
  })
})
