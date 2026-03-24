import { useState, type ReactNode } from 'react'

interface Props {
  title: string
  children: ReactNode
  renderEditor?: (close: () => void) => ReactNode
}

export default function ProfileSection({ title, children, renderEditor }: Props) {
  const [editing, setEditing] = useState(false)
  const close = () => setEditing(false)

  return (
    <div className="profile-section">
      <div className="section-header">
        <h3>{title}</h3>
        {!editing && renderEditor && (
          <button onClick={() => setEditing(true)}>Edit</button>
        )}
      </div>
      {editing && renderEditor ? renderEditor(close) : children}
    </div>
  )
}
