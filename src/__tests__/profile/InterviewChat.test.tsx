import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import InterviewChat from '../../components/profile/InterviewChat'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ session_id: '1', message: 'Hello' }),
  }))
})

describe('InterviewChat', () => {
  it('start button uses btn btn-primary classes', () => {
    render(<InterviewChat onProfileUpdate={() => {}} />)
    const btn = screen.getByRole('button', { name: /start interview/i })
    expect(btn.className).toContain('btn')
    expect(btn.className).toContain('btn-primary')
  })

  it('shows empty chat messages area before interview starts', () => {
    render(<InterviewChat onProfileUpdate={() => {}} />)
    expect(screen.getByTestId('chat-messages')).toBeInTheDocument()
  })

  it('shows a welcome prompt before interview starts', () => {
    render(<InterviewChat onProfileUpdate={() => {}} />)
    expect(screen.getByText(/start an interview/i)).toBeInTheDocument()
  })
})
