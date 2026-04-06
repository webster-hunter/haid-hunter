import { Link } from 'react-router-dom'
import type { TypedSkill } from '../../api/profile'

interface ProfileBannerProps {
  summary: string
  skills: TypedSkill[]
  currentRole: string | null
}

const MAX_VISIBLE_SKILLS = 3

export function ProfileBanner({ summary, skills, currentRole }: ProfileBannerProps) {
  const isEmpty = !summary && skills.length === 0

  if (isEmpty) {
    return (
      <div className="dashboard-card profile-banner">
        <div className="card-header">Profile</div>
        <div className="profile-banner-empty">
          <Link to="/profile">Set up your profile</Link> to see a summary here
        </div>
      </div>
    )
  }

  const visibleSkills = skills.slice(0, MAX_VISIBLE_SKILLS)
  const overflow = skills.length - MAX_VISIBLE_SKILLS

  return (
    <div className="dashboard-card profile-banner">
      <div className="card-header">Profile</div>
      <div className="profile-banner-summary">{summary}</div>
      {visibleSkills.length > 0 && (
        <div className="profile-banner-skills">
          {visibleSkills.map((s) => (
            <span key={s.name} className="skill-pill">{s.name}</span>
          ))}
          {overflow > 0 && <span className="skill-pill">+{overflow} more</span>}
        </div>
      )}
      {currentRole && <div className="profile-banner-role">{currentRole}</div>}
    </div>
  )
}
