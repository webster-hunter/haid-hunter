import type { Experience } from '../../api/profile'

export default function ExperienceList({ experience }: { experience: Experience[] }) {
  if (experience.length === 0) return <p>No experience added yet.</p>
  return (
    <div className="experience-list">
      {experience.map((e, i) => (
        <div key={i} className="experience-item">
          <div className="experience-header">
            <strong>{e.role}</strong> at {e.company}
            <span className="experience-dates">{e.start_date} — {e.end_date || 'Present'}</span>
          </div>
          {e.accomplishments.length > 0 && (
            <ul>{e.accomplishments.map((a, j) => <li key={j}>{a}</li>)}</ul>
          )}
        </div>
      ))}
    </div>
  )
}
