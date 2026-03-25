import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ApplicationModal from '../../components/applications/ApplicationModal'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [] }))
})

describe('ApplicationModal', () => {
  it('includes interviewing and rejected in status dropdown', () => {
    render(<ApplicationModal application={null} onClose={() => {}} />)
    const select = screen.getByLabelText('Status')
    const options = select.querySelectorAll('option')
    const values = Array.from(options).map(o => o.value)
    expect(values).toContain('interviewing')
    expect(values).toContain('rejected')
  })
})
