import type { Certification } from '../../api/profile'

export default function CertificationList({ certifications }: { certifications: Certification[] }) {
  if (certifications.length === 0) return <p>No certifications added yet.</p>
  return (
    <div className="certification-list">
      {certifications.map((c, i) => (
        <div key={i} className="certification-item">
          <strong>{c.name}</strong> — {c.issuer} ({c.date})
        </div>
      ))}
    </div>
  )
}
