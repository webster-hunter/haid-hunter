import type { Activity } from '../../api/profile'

export default function ActivityList({ activities }: { activities: Activity[] }) {
  if (!activities || activities.length === 0) return <p>No projects or activities yet.</p>
  return (
    <div className="activity-list">
      {activities.map((a, i) => (
        <div key={i} className="activity-item">
          <div className="activity-header">
            <strong>{a.name}</strong>
            {a.category && <span className="activity-category">{a.category}</span>}
            {a.start_date && (
              <span className="activity-dates">{a.start_date}{a.end_date !== undefined ? ` — ${a.end_date ?? 'Present'}` : ''}</span>
            )}
          </div>
          {a.url && <a className="activity-url" href={a.url} target="_blank" rel="noopener noreferrer">{a.url}</a>}
          {a.details && a.details.length > 0 && (
            <ul className="item-details">
              {a.details.map((d, j) => <li key={j}>{d}</li>)}
            </ul>
          )}
        </div>
      ))}
    </div>
  )
}
