import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { DropZone } from '../../components/documents/DropZone'

describe('DropZone', () => {
  it('renders drop area text', () => {
    render(<DropZone onDrop={() => {}} />)
    expect(screen.getByText(/drop files/i)).toBeInTheDocument()
  })
})
