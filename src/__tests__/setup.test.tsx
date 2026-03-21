import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

describe('test setup', () => {
  it('renders a component', () => {
    render(<div>Hello</div>)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
