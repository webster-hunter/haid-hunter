import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StatCard } from '../../components/home/StatCard'

describe('StatCard', () => {
  it('renders the title and total', () => {
    render(<StatCard title="Documents" total={12} subtitle="total documents" breakdowns={[]} />)
    expect(screen.getByText('Documents')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('total documents')).toBeInTheDocument()
  })

  it('renders pill badges for breakdowns', () => {
    render(
      <StatCard
        title="Documents"
        total={12}
        subtitle="total documents"
        breakdowns={[
          { label: 'resume', count: 5 },
          { label: 'cover-letter', count: 4 },
        ]}
      />
    )
    expect(screen.getByText('resume 5')).toBeInTheDocument()
    expect(screen.getByText('cover-letter 4')).toBeInTheDocument()
  })

  it('renders zero state when total is 0', () => {
    render(<StatCard title="Documents" total={0} subtitle="total documents" breakdowns={[]} />)
    expect(screen.getByText('0')).toBeInTheDocument()
    expect(screen.getByText('No documents yet')).toBeInTheDocument()
  })

  it('renders action slot when provided', () => {
    render(
      <StatCard
        title="Referrals"
        total={3}
        subtitle="total referrals"
        breakdowns={[]}
        action={<button>View all</button>}
      />
    )
    expect(screen.getByText('View all')).toBeInTheDocument()
  })
})
