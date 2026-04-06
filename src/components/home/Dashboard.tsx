import { useState, useEffect, useCallback } from 'react'
import { fetchDashboard as fetchDashboardApi } from '../../api/dashboard'
import { toggleTask, addTask, deleteTask } from '../../api/tasks'
import { ProfileBanner } from './ProfileBanner'
import { StatCard } from './StatCard'
import { DailyTasks } from './DailyTasks'
import { ReferralPopover } from './ReferralPopover'
import { PlaceholderCard } from './PlaceholderCard'
import type { TypedSkill } from '../../api/profile'

const STATUS_COLORS: Record<string, string> = {
  bookmarked: 'var(--color-muted)',
  applied: 'var(--color-secondary)',
  in_progress: 'var(--color-accent)',
  interviewing: 'var(--color-info)',
  offer: 'var(--color-success)',
  rejected: 'var(--color-warning)',
  closed: 'var(--color-error)',
}

interface DashboardData {
  profile: { summary: string; skills: TypedSkill[]; current_role: string | null }
  documents: { total: number; by_tag: Record<string, number> }
  applications: {
    total: number
    by_status: Record<string, number>
    referrals: { total: number; contacts: Array<{ name: string; company: string; application_id: number }> }
  }
  tasks: {
    daily_target: number
    applied_today: number
    statuses_current: boolean
    stale_count: number
    user_tasks: Array<{
      id: number; title: string; recurrence: string | null;
      interval_days: number | null; is_due: boolean; completed_today: boolean;
      completed_at: string | null
    }>
  }
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState(false)
  const [taskError, setTaskError] = useState<string | null>(null)

  const fetchDashboard = useCallback(async () => {
    setError(false)
    try {
      setData(await fetchDashboardApi())
    } catch {
      setError(true)
    }
  }, [])

  useEffect(() => { fetchDashboard() }, [fetchDashboard])

  const handleToggleTask = async (id: number, completed: boolean) => {
    setTaskError(null)
    try {
      await toggleTask(id, completed)
      await fetchDashboard()
    } catch {
      setTaskError('Failed to update task.')
    }
  }

  const handleAddTask = async (title: string, recurrence: string | null, intervalDays: number | null) => {
    setTaskError(null)
    try {
      await addTask(title, recurrence, intervalDays)
      await fetchDashboard()
    } catch {
      setTaskError('Failed to add task.')
    }
  }

  const handleDeleteTask = async (id: number) => {
    setTaskError(null)
    try {
      await deleteTask(id)
      await fetchDashboard()
    } catch {
      setTaskError('Failed to delete task.')
    }
  }

  if (error) {
    return (
      <div className="dashboard" data-testid="dashboard">
        <div className="dashboard-error">
          <p>Failed to load dashboard data.</p>
          <button className="btn btn-primary" onClick={fetchDashboard}>Retry</button>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="dashboard" data-testid="dashboard">
        <div className="loading">Loading...</div>
      </div>
    )
  }

  const docBreakdowns = Object.entries(data.documents.by_tag).map(([label, count]) => ({ label, count }))
  const appBreakdowns = Object.entries(data.applications.by_status).map(([label, count]) => ({
    label: label.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    count,
    color: STATUS_COLORS[label],
  }))

  return (
    <div className="dashboard" data-testid="dashboard">
      <ProfileBanner
        summary={data.profile.summary}
        skills={data.profile.skills}
        currentRole={data.profile.current_role}
      />

      <div className="dashboard-stats-row">
        <StatCard title="Documents" total={data.documents.total} subtitle="total documents" breakdowns={docBreakdowns} />
        <StatCard title="Applications" total={data.applications.total} subtitle="total applications" breakdowns={appBreakdowns} />
        <StatCard
          title="Referrals"
          total={data.applications.referrals.total}
          subtitle="total referrals"
          breakdowns={[]}
          action={
            data.applications.referrals.contacts.length > 0
              ? <ReferralPopover contacts={data.applications.referrals.contacts} />
              : undefined
          }
        />
      </div>

      {taskError && <div className="dashboard-task-error">{taskError}</div>}

      <div className="dashboard-bottom-row">
        <DailyTasks
          userTasks={data.tasks.user_tasks}
          onToggleTask={handleToggleTask}
          onAddTask={handleAddTask}
          onDeleteTask={handleDeleteTask}
        />
        <PlaceholderCard />
      </div>
    </div>
  )
}
