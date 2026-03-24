import type { Education } from '../../api/profile'

export default function EducationList({ education }: { education: Education[] }) {
  if (education.length === 0) return <p>No education added yet.</p>
  return (
    <div className="education-list">
      {education.map((e, i) => (
        <div key={i} className="education-item">
          <div className="education-header">
            <strong>{e.degree}</strong>{e.field ? ` in ${e.field}` : ''} — {e.institution}
            <span className="education-dates">{e.start_date} — {e.end_date ?? 'Present'}</span>
          </div>
          {e.details && e.details.length > 0 && (
            <ul className="item-details">
              {e.details.map((d, j) => <li key={j}>{d}</li>)}
            </ul>
          )}
        </div>
      ))}
    </div>
  )
}
