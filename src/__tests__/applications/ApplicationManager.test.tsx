import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ApplicationManager from '../../components/applications/ApplicationManager'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [] }))
})

describe('ApplicationManager', () => {
  it('renders page title', async () => {
    render(<ApplicationManager />)
    expect(await screen.findByText('Applications')).toBeInTheDocument()
  })

  it('renders toolbar with add button', async () => {
    render(<ApplicationManager />)
    expect(await screen.findByText(/add application/i)).toBeInTheDocument()
  })

  it('renders view toggle', async () => {
    render(<ApplicationManager />)
    expect(await screen.findByText(/table/i)).toBeInTheDocument()
    expect(await screen.findByText(/kanban/i)).toBeInTheDocument()
  })
})
