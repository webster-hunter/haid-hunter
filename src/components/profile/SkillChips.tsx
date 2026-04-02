import type { TypedSkill } from '../../api/extraction'

export default function SkillChips({ skills }: { skills: TypedSkill[] }) {
  if (skills.length === 0) return <p>No skills added yet.</p>

  const grouped: Record<string, TypedSkill[]> = {}
  for (const s of skills) {
    if (!grouped[s.type]) grouped[s.type] = []
    grouped[s.type].push(s)
  }

  return (
    <div className="skill-chips">
      {Object.entries(grouped).map(([type, items]) => (
        <div key={type} className="skill-type-group">
          <h5 className="skill-type-heading">{type}</h5>
          <div className="skill-type-chips">
            {items.map((s, i) => (
              <span key={i} className="skill-chip">{s.name}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
