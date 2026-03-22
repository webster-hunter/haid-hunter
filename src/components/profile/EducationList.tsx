import type { Education } from '../../api/profile'

export default function EducationList({ education }: { education: Education[] }) {
  if (education.length === 0) return <p>No education added yet.</p>
  return (
    <div className="education-list">
      {education.map((e, i) => (
        <div key={i} className="education-item">
          <strong>{e.degree}</strong> — {e.institution}
          <span className="education-dates">{e.start_date} — {e.end_date}</span>
        </div>
      ))}
    </div>
  )
}
