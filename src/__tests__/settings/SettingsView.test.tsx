import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import SettingsView from '../../components/settings/SettingsView'

describe('SettingsView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders settings page title', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ configured: false, source: null }),
    }))
    render(<SettingsView />)
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('shows not configured state', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ configured: false, source: null }),
    }))
    render(<SettingsView />)
    expect(await screen.findByText('Not configured')).toBeInTheDocument()
  })

  it('shows configured state with masked key', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ configured: true, source: 'database', masked: 'sk-a***2345' }),
    }))
    render(<SettingsView />)
    expect(await screen.findByText('sk-a***2345')).toBeInTheDocument()
    expect(await screen.findByText('database')).toBeInTheDocument()
  })

  it('shows env source badge when key is from .env', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ configured: true, source: 'env', masked: 'sk-a***9999' }),
    }))
    render(<SettingsView />)
    expect(await screen.findByText('env')).toBeInTheDocument()
  })

  it('allows saving a new API key', async () => {
    const mockFetch = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({ configured: false, source: null }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ configured: true, source: 'database', masked: 'sk-a***5678' }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ configured: true, source: 'database', masked: 'sk-a***5678' }) })
    vi.stubGlobal('fetch', mockFetch)

    render(<SettingsView />)
    const input = await screen.findByPlaceholderText('sk-ant-...')
    fireEvent.change(input, { target: { value: 'sk-ant-new-key-5678' } })
    fireEvent.click(screen.getByText('Save'))

    await waitFor(() => {
      const putCall = mockFetch.mock.calls.find(c => c[1]?.method === 'PUT')
      expect(putCall).toBeTruthy()
      const body = JSON.parse(putCall![1].body)
      expect(body.api_key).toBe('sk-ant-new-key-5678')
    })
  })

  it('allows testing the API key', async () => {
    const mockFetch = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({ configured: true, source: 'database', masked: 'sk-a***2345' }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ valid: true, source: 'database' }) })
    vi.stubGlobal('fetch', mockFetch)

    render(<SettingsView />)
    const testBtn = await screen.findByText('Test Connection')
    fireEvent.click(testBtn)

    expect(await screen.findByText('Valid')).toBeInTheDocument()
  })

  it('shows error when test fails', async () => {
    const mockFetch = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({ configured: true, source: 'database', masked: 'sk-a***2345' }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ valid: false, error: 'Invalid API key' }) })
    vi.stubGlobal('fetch', mockFetch)

    render(<SettingsView />)
    const testBtn = await screen.findByText('Test Connection')
    fireEvent.click(testBtn)

    expect(await screen.findByText('Invalid')).toBeInTheDocument()
  })
})
