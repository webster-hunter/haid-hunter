import { useState, useEffect } from 'react'
import { fetchProfile, type Profile } from '../../api/profile'
import ProfilePanel from './ProfilePanel'
import InterviewChat from './InterviewChat'

export default function ProfileView() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [chatCollapsed, setChatCollapsed] = useState(false)

  useEffect(() => {
    fetchProfile().then(setProfile)
  }, [])

  const handleProfileUpdate = () => {
    fetchProfile().then(setProfile)
  }

  return (
    <div className="profile-view">
      <h1>Profile</h1>
      <div className="profile-layout">
        <div className="profile-main" data-testid="profile-panel">
          {profile && <ProfilePanel profile={profile} onUpdate={handleProfileUpdate} />}
        </div>
        <div className={`profile-chat ${chatCollapsed ? 'collapsed' : ''}`} data-testid="interview-chat">
          <button className="chat-toggle" onClick={() => setChatCollapsed(!chatCollapsed)}>
            {chatCollapsed ? '◀' : '▶'}
          </button>
          {!chatCollapsed && <InterviewChat onProfileUpdate={handleProfileUpdate} />}
        </div>
      </div>
    </div>
  )
}
