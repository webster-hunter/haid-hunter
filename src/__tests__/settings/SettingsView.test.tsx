import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import SettingsView from '../../components/settings/SettingsView'

describe('SettingsView', () => {
  it('shows Claude Code integration status', () => {
    render(<SettingsView />)
    expect(screen.getByText('Claude Integration')).toBeInTheDocument()
    expect(screen.getAllByText(/Claude Code/).length).toBeGreaterThan(0)
  })

  it('does not show API key input', () => {
    render(<SettingsView />)
    expect(screen.queryByPlaceholderText('sk-ant-...')).not.toBeInTheDocument()
  })
})
