import type { Profile } from '../../api/profile'
import ProfileSection from './ProfileSection'
import SectionEditor from './SectionEditor'
import SkillChips from './SkillChips'
import ExperienceList from './ExperienceList'
import EducationList from './EducationList'
import CertificationList from './CertificationList'

interface Props {
  profile: Profile
  onUpdate: () => void
}

export default function ProfilePanel({ profile, onUpdate }: Props) {
  const objectives = Array.isArray(profile.objectives) ? profile.objectives : []
  const editor = (section: string, data: unknown) => (close: () => void) => (
    <SectionEditor section={section} data={data} onSave={() => { onUpdate(); close() }} onCancel={close} />
  )

  return (
    <div className="profile-panel-inner">
      <ProfileSection title="Summary" renderEditor={editor('summary', profile.summary)}>
        <p>{profile.summary || 'No summary yet.'}</p>
      </ProfileSection>
      <ProfileSection title="Skills" renderEditor={editor('skills', profile.skills)}>
        <SkillChips skills={profile.skills} />
      </ProfileSection>
      <ProfileSection title="Experience" renderEditor={editor('experience', profile.experience)}>
        <ExperienceList experience={profile.experience} />
      </ProfileSection>
      <ProfileSection title="Education" renderEditor={editor('education', profile.education)}>
        <EducationList education={profile.education} />
      </ProfileSection>
      <ProfileSection title="Certifications" renderEditor={editor('certifications', profile.certifications)}>
        <CertificationList certifications={profile.certifications} />
      </ProfileSection>
      <ProfileSection title="Objectives" renderEditor={editor('objectives', objectives)}>
        {objectives.length > 0 ? (
          <ul className="objectives-list">
            {objectives.map((obj, i) => <li key={i}>{obj}</li>)}
          </ul>
        ) : (
          <p>No objectives yet.</p>
        )}
      </ProfileSection>
    </div>
  )
}
