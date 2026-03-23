import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { DailyTasks } from '../../components/home/DailyTasks'

const baseProps = {
  dailyTarget: 5,
  appliedToday: 2,
  statusesCurrent: true,
  staleCount: 0,
  userTasks: [],
  onToggleTask: vi.fn(),
  onAddTask: vi.fn(),
}

describe('DailyTasks', () => {
  it('renders built-in apply goal with progress', () => {
    render(<DailyTasks {...baseProps} />)
    expect(screen.getByText('Apply for positions')).toBeInTheDocument()
    expect(screen.getByText('2 of 5 today')).toBeInTheDocument()
  })

  it('shows done pill when apply target met', () => {
    render(<DailyTasks {...baseProps} appliedToday={5} />)
    expect(screen.getAllByText('done').length).toBeGreaterThan(0)
  })

  it('renders status update goal as current', () => {
    render(<DailyTasks {...baseProps} />)
    expect(screen.getByText('Update application statuses')).toBeInTheDocument()
    expect(screen.getByText('All statuses current')).toBeInTheDocument()
  })

  it('renders stale status count', () => {
    render(<DailyTasks {...baseProps} statusesCurrent={false} staleCount={3} />)
    expect(screen.getByText('3 need update')).toBeInTheDocument()
  })

  it('renders user tasks', () => {
    render(
      <DailyTasks
        {...baseProps}
        userTasks={[
          { id: 1, title: 'Review LinkedIn', recurrence: 'custom', interval_days: 3, is_due: true, completed_today: false },
          { id: 2, title: 'Tailor resume', recurrence: null, interval_days: null, is_due: true, completed_today: false },
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
          { id: 1, title: 'Test task', recurrence: null, interval_days: null, is_due: true, completed_today: false },
        ]}
      />
    )
    fireEvent.click(screen.getByTestId('task-checkbox-1'))
    expect(onToggle).toHaveBeenCalledWith(1, true)
  })

  it('shows empty message with no user tasks', () => {
    render(<DailyTasks {...baseProps} />)
    expect(screen.getByText('No custom tasks yet.')).toBeInTheDocument()
  })
})
