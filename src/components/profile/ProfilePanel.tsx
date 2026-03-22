import type { Profile } from '../../api/profile'
import ProfileSection from './ProfileSection'
import SkillChips from './SkillChips'
import ExperienceList from './ExperienceList'
import EducationList from './EducationList'
import CertificationList from './CertificationList'

interface Props {
  profile: Profile
  onUpdate: () => void
}

export default function ProfilePanel({ profile, onUpdate: _onUpdate }: Props) {
  return (
    <div className="profile-panel-inner">
      <ProfileSection title="Summary">
        <p>{profile.summary || 'No summary yet.'}</p>
      </ProfileSection>
      <ProfileSection title="Skills">
        <SkillChips skills={profile.skills} />
      </ProfileSection>
      <ProfileSection title="Experience">
        <ExperienceList experience={profile.experience} />
      </ProfileSection>
      <ProfileSection title="Education">
        <EducationList education={profile.education} />
      </ProfileSection>
      <ProfileSection title="Certifications">
        <CertificationList certifications={profile.certifications} />
      </ProfileSection>
      <ProfileSection title="Objectives">
        <p>{profile.objectives || 'No objectives yet.'}</p>
      </ProfileSection>
    </div>
  )
}
