import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { DailyTasks } from '../../components/home/DailyTasks'

const baseProps = {
  userTasks: [],
  onToggleTask: vi.fn(),
  onAddTask: vi.fn(),
  onDeleteTask: vi.fn(),
}

describe('DailyTasks', () => {
  it('renders user tasks', () => {
    render(
      <DailyTasks
        {...baseProps}
        userTasks={[
          { id: 1, title: 'Review LinkedIn', recurrence: 'custom', interval_days: 3, is_due: true, completed_today: false, completed_at: null },
          { id: 2, title: 'Tailor resume', recurrence: null, interval_days: null, is_due: true, completed_today: false, completed_at: null },
        ]}
      />
    )
    expect(screen.getByText('Review LinkedIn')).toBeInTheDocument()
    expect(screen.getByText('Tailor resume')).toBeInTheDocument()
  })

  it('calls onToggleTask when checkbox clicked', () => {
    const onToggle = vi.fn()
    render(
      <DailyTasks
        {...baseProps}
        onToggleTask={onToggle}
        userTasks={[
          { id: 1, title: 'Test task', recurrence: null, interval_days: null, is_due: true, completed_today: false, completed_at: null },
        ]}
      />
    )
    fireEvent.click(screen.getByTestId('task-checkbox-1'))
    expect(onToggle).toHaveBeenCalledWith(1, true)
  })

  it('calls onDeleteTask when delete button clicked', () => {
    const onDelete = vi.fn()
    render(
      <DailyTasks
        {...baseProps}
        onDeleteTask={onDelete}
        userTasks={[
          { id: 1, title: 'Test task', recurrence: null, interval_days: null, is_due: true, completed_today: false, completed_at: null },
        ]}
      />
    )
    fireEvent.click(screen.getByTestId('task-delete-1'))
    expect(onDelete).toHaveBeenCalledWith(1)
  })

  it('shows last completion date when present', () => {
    render(
      <DailyTasks
        {...baseProps}
        userTasks={[
          { id: 1, title: 'Daily review', recurrence: 'daily', interval_days: 1, is_due: true, completed_today: false, completed_at: '2026-03-22T14:30:00' },
        ]}
      />
    )
    expect(screen.getByText(/Last completed: Mar 22/)).toBeInTheDocument()
  })

  it('shows empty message with no user tasks', () => {
    render(<DailyTasks {...baseProps} />)
    expect(screen.getByText('No custom tasks yet.')).toBeInTheDocument()
  })
})
