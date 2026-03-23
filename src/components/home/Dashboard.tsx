import { useState, useEffect, useCallback } from 'react'
import { ProfileBanner } from './ProfileBanner'
import { StatCard } from './StatCard'
import { DailyTasks } from './DailyTasks'
import { ReferralPopover } from './ReferralPopover'
import { PlaceholderCard } from './PlaceholderCard'

const STATUS_COLORS: Record<string, string> = {
  bookmarked: 'var(--color-muted)',
  applied: 'var(--color-secondary)',
  in_progress: 'var(--color-accent)',
  offer: 'var(--color-success)',
  closed: 'var(--color-error)',
}

interface DashboardData {
  profile: { summary: string; skills: string[]; current_role: string | null }
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
      interval_days: number | null; is_due: boolean; completed_today: boolean
    }>
  }
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState(false)

  const fetchDashboard = useCallback(async () => {
    setError(false)
    try {
      const res = await fetch('/api/dashboard')
      if (!res.ok) throw new Error('fetch failed')
      setData(await res.json())
    } catch {
      setError(true)
    }
  }, [])

  useEffect(() => { fetchDashboard() }, [fetchDashboard])

  const handleToggleTask = async (id: number, completed: boolean) => {
    await fetch(`/api/tasks/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed }),
    })
    fetchDashboard()
  }

  const handleAddTask = () => {
    // Out of scope for this plan. The add-task modal/form will be implemented
    // as a follow-up after the dashboard is functional. The backend CRUD is ready.
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
    label,
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

      <div className="dashboard-bottom-row">
        <DailyTasks
          dailyTarget={data.tasks.daily_target}
          appliedToday={data.tasks.applied_today}
          statusesCurrent={data.tasks.statuses_current}
          staleCount={data.tasks.stale_count}
          userTasks={data.tasks.user_tasks}
          onToggleTask={handleToggleTask}
          onAddTask={handleAddTask}
        />
        <PlaceholderCard />
      </div>
    </div>
  )
}
