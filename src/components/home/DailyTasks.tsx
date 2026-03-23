import { useState } from 'react'

interface UserTask {
  id: number
  title: string
  recurrence: string | null
  interval_days: number | null
  is_due: boolean
  completed_today: boolean
}

interface DailyTasksProps {
  dailyTarget: number
  appliedToday: number
  statusesCurrent: boolean
  staleCount: number
  userTasks: UserTask[]
  onToggleTask: (id: number, completed: boolean) => void
  onAddTask: (title: string, recurrence: string | null, intervalDays: number | null) => void
}

function getApplyStatus(applied: number, target: number) {
  if (applied >= target) return 'done'
  if (applied > 0) return 'in progress'
  return 'pending'
}

function getStatusPillClass(status: string) {
  switch (status) {
    case 'done': return 'task-pill task-pill-done'
    case 'in progress': return 'task-pill task-pill-progress'
    default: return 'task-pill task-pill-muted'
  }
}

function recurrenceLabel(task: UserTask) {
  if (!task.recurrence) return 'One-time'
  if (task.recurrence === 'daily') return 'Daily'
  if (task.recurrence === 'weekly') return 'Weekly'
  return `Every ${task.interval_days} days`
}

export function DailyTasks({
  dailyTarget,
  appliedToday,
  statusesCurrent,
  staleCount,
  userTasks,
  onToggleTask,
  onAddTask,
}: DailyTasksProps) {
  const applyStatus = getApplyStatus(appliedToday, dailyTarget)
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
        <div className="card-header">Daily Tasks</div>
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
        {/* Built-in: Apply for positions */}
        <div className={`task-row ${applyStatus === 'done' ? 'task-completed' : ''}`}>
          <div className={`task-checkbox ${applyStatus === 'done' ? 'task-checkbox-done' : ''}`}>
            {applyStatus === 'done' && '✓'}
          </div>
          <div className="task-content">
            <div className="task-title">Apply for positions</div>
            <div className="task-subtitle">{appliedToday} of {dailyTarget} today</div>
          </div>
          <span className={getStatusPillClass(applyStatus)}>{applyStatus}</span>
        </div>

        {/* Built-in: Update statuses */}
        <div className={`task-row ${statusesCurrent ? 'task-completed' : ''}`}>
          <div className={`task-checkbox ${statusesCurrent ? 'task-checkbox-done' : ''}`}>
            {statusesCurrent && '✓'}
          </div>
          <div className="task-content">
            <div className="task-title">Update application statuses</div>
            <div className="task-subtitle">
              {statusesCurrent ? 'All statuses current' : `${staleCount} need update`}
            </div>
          </div>
          <span className={statusesCurrent ? 'task-pill task-pill-done' : 'task-pill task-pill-progress'}>
            {statusesCurrent ? 'done' : 'in progress'}
          </span>
        </div>

        {/* User tasks */}
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
              <div className="task-subtitle">{recurrenceLabel(task)}</div>
            </div>
            <span className={task.completed_today ? 'task-pill task-pill-done' : `task-pill task-pill-muted`}>
              {task.completed_today ? 'done' : (task.recurrence ? 'recurring' : 'one-time')}
            </span>
          </div>
        ))}

        {userTasks.length === 0 && (
          <div className="daily-tasks-empty">No custom tasks yet.</div>
        )}
      </div>
    </div>
  )
}
