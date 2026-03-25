import { useState, useEffect } from 'react'
import { fetchProfile, type Profile } from '../../api/profile'
import ProfilePanel from './ProfilePanel'
import InterviewChat from './InterviewChat'

export default function ProfileView() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [chatCollapsed, setChatCollapsed] = useState(false)

  const loadProfile = () => {
    setError(null)
    fetchProfile()
      .then(setProfile)
      .catch(() => setError('Failed to load profile'))
  }

  useEffect(() => {
    loadProfile()
  }, [])

  const handleProfileUpdate = () => {
    fetchProfile().then(setProfile).catch(() => {})
  }

  return (
    <div className="profile-view">
      <h1>Profile</h1>
      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button className="btn btn-primary" onClick={loadProfile}>Retry</button>
        </div>
      )}
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
