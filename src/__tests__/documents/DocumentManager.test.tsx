import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import DocumentManager from '../../components/documents/DocumentManager'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: async () => [],
  }))
})

describe('DocumentManager', () => {
  it('renders the three-panel layout', async () => {
    render(<DocumentManager />)
    expect(screen.getByTestId('tag-sidebar')).toBeInTheDocument()
    expect(screen.getByTestId('document-list-panel')).toBeInTheDocument()
  })

  it('renders the page title', () => {
    render(<DocumentManager />)
    expect(screen.getByText('Documents')).toBeInTheDocument()
  })
})
