import type { Skill } from '../../api/profile'

const PROFICIENCY_CLASSES: Record<string, string> = {
  beginner: 'badge-muted',
  intermediate: 'badge-accent',
  advanced: 'badge-success',
  expert: 'badge-secondary',
}

export default function SkillChips({ skills }: { skills: Skill[] }) {
  if (skills.length === 0) return <p>No skills added yet.</p>
  return (
    <div className="skill-chips">
      {skills.map((s, i) => (
        <span key={i} className="skill-chip">
          {s.name}
          <span className={`proficiency-badge ${PROFICIENCY_CLASSES[s.proficiency] || ''}`}>
            {s.proficiency}
          </span>
        </span>
      ))}
    </div>
  )
}
