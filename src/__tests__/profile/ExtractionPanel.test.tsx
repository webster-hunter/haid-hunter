import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ExtractionPanel from '../../components/profile/ExtractionPanel'

describe('ExtractionPanel', () => {
  const mockOnAccept = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders analyze button', () => {
    render(<ExtractionPanel onAccept={mockOnAccept} />)
    expect(screen.getByText('Analyze Documents')).toBeInTheDocument()
  })

  it('shows loading state while analyzing', async () => {
    vi.stubGlobal('fetch', vi.fn().mockReturnValue(new Promise(() => {})))
    render(<ExtractionPanel onAccept={mockOnAccept} />)
    fireEvent.click(screen.getByText('Analyze Documents'))
    expect(await screen.findByText('Analyzing...')).toBeInTheDocument()
  })

  it('displays extracted suggestions after analysis', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        skills: ['Python', 'React'],
        technologies: ['Docker'],
        experience_keywords: ['led team of 5'],
        soft_skills: ['collaboration'],
      }),
    }))

    render(<ExtractionPanel onAccept={mockOnAccept} />)
    fireEvent.click(screen.getByText('Analyze Documents'))

    expect(await screen.findByText('Python')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Docker')).toBeInTheDocument()
    expect(screen.getByText('collaboration')).toBeInTheDocument()
    expect(screen.getByText('led team of 5')).toBeInTheDocument()
  })

  it('allows toggling individual suggestions off', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        skills: ['Python', 'React'],
        technologies: [],
        experience_keywords: [],
        soft_skills: [],
      }),
    }))

    render(<ExtractionPanel onAccept={mockOnAccept} />)
    fireEvent.click(screen.getByText('Analyze Documents'))

    const pythonChip = await screen.findByText('Python')
    fireEvent.click(pythonChip)
    expect(pythonChip).toHaveClass('deselected')
  })

  it('calls onAccept with only selected suggestions', async () => {
    const analyzeResponse = {
      ok: true,
      json: async () => ({
        skills: ['Python', 'React'],
        technologies: [],
        experience_keywords: [],
        soft_skills: [],
      }),
    }
    const acceptResponse = {
      ok: true,
      json: async () => ({ skills: ['Python'] }),
    }
    const mockFetch = vi.fn()
      .mockResolvedValueOnce(analyzeResponse)
      .mockResolvedValueOnce(acceptResponse)
    vi.stubGlobal('fetch', mockFetch)

    render(<ExtractionPanel onAccept={mockOnAccept} />)
    fireEvent.click(screen.getByText('Analyze Documents'))

    // Deselect React
    const reactChip = await screen.findByText('React')
    fireEvent.click(reactChip)

    // Accept
    fireEvent.click(screen.getByText('Accept Selected'))

    await waitFor(() => {
      expect(mockOnAccept).toHaveBeenCalled()
    })

    // Verify the accept call excluded React
    const acceptCall = mockFetch.mock.calls[1]
    const body = JSON.parse(acceptCall[1].body)
    expect(body.skills).toEqual(['Python'])
    expect(body.skills).not.toContain('React')
  })

  it('shows empty state when no suggestions found', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        skills: [],
        technologies: [],
        experience_keywords: [],
        soft_skills: [],
      }),
    }))

    render(<ExtractionPanel onAccept={mockOnAccept} />)
    fireEvent.click(screen.getByText('Analyze Documents'))

    expect(await screen.findByText('No suggestions found.')).toBeInTheDocument()
  })
})
