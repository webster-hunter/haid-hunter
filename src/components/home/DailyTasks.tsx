import { useState } from 'react'

interface UserTask {
  id: number
  title: string
  recurrence: string | null
  interval_days: number | null
  is_due: boolean
  completed_today: boolean
  completed_at: string | null
}

interface DailyTasksProps {
  userTasks: UserTask[]
  onToggleTask: (id: number, completed: boolean) => void
  onAddTask: (title: string, recurrence: string | null, intervalDays: number | null) => void
  onDeleteTask: (id: number) => void
}

function recurrenceLabel(task: UserTask) {
  if (!task.recurrence) return 'One-time'
  if (task.recurrence === 'daily') return 'Daily'
  if (task.recurrence === 'weekly') return 'Weekly'
  return `Every ${task.interval_days} days`
}

function formatCompletedAt(dateStr: string | null): string | null {
  if (!dateStr) return null
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export function DailyTasks({
  userTasks,
  onToggleTask,
  onAddTask,
  onDeleteTask,
}: DailyTasksProps) {
  const [showForm, setShowForm] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newRecurrence, setNewRecurrence] = useState<string>('one-time')
  const [newInterval, setNewInterval] = useState('')
  const [newUnit, setNewUnit] = useState<string>('days')

  const handleSubmit = () => {
    const title = newTitle.trim()
    if (!title) return

    let recurrence: string | null = null
    let intervalDays: number | null = null

    if (newRecurrence === 'daily') {
      recurrence = 'daily'
    } else if (newRecurrence === 'weekly') {
      recurrence = 'weekly'
    } else if (newRecurrence === 'custom') {
      recurrence = 'custom'
      const n = parseInt(newInterval) || 1
      const multiplier = newUnit === 'weeks' ? 7 : newUnit === 'months' ? 30 : 1
      intervalDays = n * multiplier
    }

    onAddTask(title, recurrence, intervalDays)
    setNewTitle('')
    setNewRecurrence('one-time')
    setNewInterval('')
    setNewUnit('days')
    setShowForm(false)
  }

  return (
    <div className="dashboard-card daily-tasks">
      <div className="daily-tasks-header">
        <div className="card-header">Tasks</div>
        <button className="daily-tasks-add" onClick={() => setShowForm(!showForm)}>+ Add Task</button>
      </div>

      {showForm && (
        <div className="add-task-form">
          <input
            className="add-task-input"
            type="text"
            placeholder="Task title..."
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            autoFocus
          />
          <div className="add-task-options">
            <select
              className="add-task-select"
              value={newRecurrence}
              onChange={(e) => setNewRecurrence(e.target.value)}
            >
              <option value="one-time">One-time</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="custom">Custom</option>
            </select>
            {newRecurrence === 'custom' && (
              <>
                <input
                  className="add-task-interval"
                  type="text"
                  inputMode="numeric"
                  placeholder="N"
                  value={newInterval}
                  onChange={(e) => setNewInterval(e.target.value.replace(/\D/g, ''))}
                />
                <select
                  className="add-task-select"
                  value={newUnit}
                  onChange={(e) => setNewUnit(e.target.value)}
                >
                  <option value="days">days</option>
                  <option value="weeks">weeks</option>
                  <option value="months">months</option>
                </select>
              </>
            )}
            <button className="add-task-submit" onClick={handleSubmit}>Add</button>
            <button className="add-task-cancel" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      <div className="daily-tasks-list">
        {userTasks.map((task) => (
          <div key={task.id} className={`task-row ${task.completed_today ? 'task-completed' : ''}`}>
            <div
              data-testid={`task-checkbox-${task.id}`}
              className={`task-checkbox ${task.completed_today ? 'task-checkbox-done' : ''}`}
              onClick={() => onToggleTask(task.id, !task.completed_today)}
            >
              {task.completed_today && '✓'}
            </div>
            <div className="task-content">
              <div className="task-title">{task.title}</div>
              <div className="task-subtitle">
                {recurrenceLabel(task)}
                {task.completed_at && ` · Last completed: ${formatCompletedAt(task.completed_at)}`}
              </div>
            </div>
            <span className={task.completed_today ? 'task-pill task-pill-done' : `task-pill task-pill-muted`}>
              {task.completed_today ? 'done' : (task.recurrence ? 'recurring' : 'one-time')}
            </span>
            <button
              className="task-delete"
              data-testid={`task-delete-${task.id}`}
              onClick={() => onDeleteTask(task.id)}
              aria-label={`Delete ${task.title}`}
            >
              ✕
            </button>
          </div>
        ))}

        {userTasks.length === 0 && (
          <div className="daily-tasks-empty">No custom tasks yet.</div>
        )}
      </div>
    </div>
  )
}
