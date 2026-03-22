import { useState, type ReactNode } from 'react'

interface Props {
  title: string
  children: ReactNode
  editor?: ReactNode
}

export default function ProfileSection({ title, children, editor }: Props) {
  const [editing, setEditing] = useState(false)
  return (
    <div className="profile-section">
      <div className="section-header">
        <h3>{title}</h3>
        <button onClick={() => setEditing(!editing)}>{editing ? 'Cancel' : 'Edit'}</button>
      </div>
      {editing ? editor : children}
    </div>
  )
}
