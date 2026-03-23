import { ReactNode } from 'react'

interface Breakdown {
  label: string
  count: number
  color?: string
}

interface StatCardProps {
  title: string
  total: number
  subtitle: string
  breakdowns: Breakdown[]
  action?: ReactNode
  emptyMessage?: string
}

export function StatCard({ title, total, subtitle, breakdowns, action, emptyMessage }: StatCardProps) {
  return (
    <div className="dashboard-card stat-card">
      <div className="stat-card-header">{title}</div>
      <div className="stat-card-total">{total}</div>
      <div className="stat-card-subtitle">{subtitle}</div>
      {total === 0 && (
        <div className="stat-card-empty">{emptyMessage || `No ${title.toLowerCase()} yet`}</div>
      )}
      {breakdowns.length > 0 && (
        <div className="stat-card-breakdowns">
          {breakdowns.map((b) => (
            <span
              key={b.label}
              className="stat-pill"
              style={b.color ? { '--pill-color': b.color } as React.CSSProperties : undefined}
            >
              {b.label} {b.count}
            </span>
          ))}
        </div>
      )}
      {action && <div className="stat-card-action">{action}</div>}
    </div>
  )
}
