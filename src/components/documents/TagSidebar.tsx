import { useState } from 'react'
import type { DocumentMeta } from '../../api/documents'

interface TagSidebarProps {
  tags: string[]
  documents: DocumentMeta[]
  activeTag: string | null
  onSelectTag: (tag: string | null) => void
  onCreateTag: (name: string) => void
  onDeleteTag: (name: string) => void
}

export function TagSidebar({ tags, documents, activeTag, onSelectTag, onCreateTag, onDeleteTag }: TagSidebarProps) {
  const [showInput, setShowInput] = useState(false)
  const [newTagName, setNewTagName] = useState('')

  const totalCount = documents.length
  const getTagCount = (tag: string) => documents.filter(d => d.tags.includes(tag)).length

  const handleCreateTag = () => {
    const trimmed = newTagName.trim()
    if (trimmed) {
      onCreateTag(trimmed)
      setNewTagName('')
      setShowInput(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleCreateTag()
    if (e.key === 'Escape') {
      setShowInput(false)
      setNewTagName('')
    }
  }

  return (
    <aside className="tag-sidebar" data-testid="tag-sidebar">
      <div className="tag-sidebar-title">Tags</div>

      <div
        className={`tag-item${activeTag === null ? ' active' : ''}`}
        data-testid="tag-all"
        onClick={() => onSelectTag(null)}
      >
        <span>All Documents</span>
        <span className="tag-count">{totalCount}</span>
      </div>

      {tags.map(tag => (
        <div
          key={tag}
          className={`tag-item${activeTag === tag ? ' active' : ''}`}
          data-testid={`tag-item-${tag}`}
          onClick={() => onSelectTag(tag)}
        >
          <span>{tag}</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span className="tag-count">({getTagCount(tag)})</span>
            <button
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', opacity: 0.5, padding: '0 2px', fontSize: 12 }}
              onClick={e => { e.stopPropagation(); onDeleteTag(tag) }}
              aria-label={`Delete tag ${tag}`}
            >
              ×
            </button>
          </div>
        </div>
      ))}

      {showInput ? (
        <div className="tag-input-row">
          <input
            className="form-input"
            value={newTagName}
            onChange={e => setNewTagName(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Tag name..."
            autoFocus
          />
          <button className="btn btn-primary btn-sm" onClick={handleCreateTag}>Add</button>
          <button className="btn btn-secondary btn-sm" onClick={() => { setShowInput(false); setNewTagName('') }}>✕</button>
        </div>
      ) : (
        <div className="add-tag-btn" onClick={() => setShowInput(true)}>
          + New Tag
        </div>
      )}
    </aside>
  )
}
