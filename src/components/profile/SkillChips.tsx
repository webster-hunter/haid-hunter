export default function SkillChips({ skills }: { skills: string[] }) {
  if (skills.length === 0) return <p>No skills added yet.</p>
  return (
    <div className="skill-chips">
      {skills.map((s, i) => (
        <span key={i} className="skill-chip">{s}</span>
      ))}
    </div>
  )
}
