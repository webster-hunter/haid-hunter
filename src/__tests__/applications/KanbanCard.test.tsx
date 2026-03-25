import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import KanbanCard from '../../components/applications/KanbanCard'

const mockApp = {
  id: 42,
  company: 'Acme',
  position: 'Engineer',
  status: 'applied',
  posting_url: null,
  login_page_url: null,
  login_email: null,
  login_password: null,
  closed_reason: null,
  has_referral: false,
  referral_name: null,
  notes: null,
  created_at: '2026-01-01',
  doc_count: 0,
}

describe('KanbanCard', () => {
  it('sets data-id attribute on draggable element', () => {
    render(<KanbanCard application={mockApp} onClick={() => {}} />)
    const card = screen.getByRole('button')
    expect(card.getAttribute('data-id')).toBe('42')
  })
})
