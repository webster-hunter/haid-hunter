import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ReferralPopover } from '../../components/home/ReferralPopover'

const contacts = [
  { name: 'Jane', company: 'Google', application_id: 1 },
  { name: 'Bob', company: 'Meta', application_id: 2 },
]

describe('ReferralPopover', () => {
  it('renders trigger button', () => {
    render(<ReferralPopover contacts={contacts} />)
    expect(screen.getByText('View all referrals →')).toBeInTheDocument()
  })

  it('shows popover with contacts on click', () => {
    render(<ReferralPopover contacts={contacts} />)
    fireEvent.click(screen.getByText('View all referrals →'))
    expect(screen.getByTestId('referral-popover')).toBeInTheDocument()
    expect(screen.getByText('Jane')).toBeInTheDocument()
    expect(screen.getByText('Google')).toBeInTheDocument()
    expect(screen.getByText('Bob')).toBeInTheDocument()
  })

  it('hides popover on second click', () => {
    render(<ReferralPopover contacts={contacts} />)
    const trigger = screen.getByText('View all referrals →')
    fireEvent.click(trigger)
    expect(screen.getByTestId('referral-popover')).toBeInTheDocument()
    fireEvent.click(trigger)
    expect(screen.queryByTestId('referral-popover')).not.toBeInTheDocument()
  })
})
