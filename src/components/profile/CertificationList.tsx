import type { Certification } from '../../api/profile'

export default function CertificationList({ certifications }: { certifications: Certification[] }) {
  if (certifications.length === 0) return <p>No certifications added yet.</p>
  return (
    <div className="certification-list">
      {certifications.map((c, i) => (
        <div key={i} className="certification-item">
          <strong>{c.name}</strong>{c.issuer ? ` — ${c.issuer}` : ''}
          {c.in_progress
            ? <span className="certification-in-progress">In Progress</span>
            : <span className="certification-date">{c.date}</span>}
        </div>
      ))}
    </div>
  )
}
