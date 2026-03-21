import type { DocumentMeta } from '../../api/documents'

const EXT_STYLES: Record<string, { bg: string; color: string }> = {
  pdf:  { bg: '#c0392b22', color: '#e74c3c' },
  doc:  { bg: '#2980b922', color: '#3498db' },
  docx: { bg: '#2980b922', color: '#3498db' },
  txt:  { bg: '#27ae6022', color: '#2ecc71' },
  md:   { bg: '#8e44ad22', color: '#9b59b6' },
  png:  { bg: '#e67e2222', color: '#f39c12' },
  jpg:  { bg: '#e67e2222', color: '#f39c12' },
  jpeg: { bg: '#e67e2222', color: '#f39c12' },
}

function getExtStyle(filename: string) {
  const ext = filename.split('.').pop()?.toLowerCase() ?? ''
  return EXT_STYLES[ext] ?? { bg: '#6b7fa322', color: '#6b7fa3' }
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

interface DocumentItemProps {
  doc: DocumentMeta
  selected: boolean
  onSelect: (id: string) => void
}

function DocumentItem({ doc, selected, onSelect }: DocumentItemProps) {
  const ext = doc.display_name.split('.').pop()?.toUpperCase() ?? '?'
  const style = getExtStyle(doc.display_name)

  return (
    <div
      className={`document-item${selected ? ' selected' : ''}`}
      onClick={() => onSelect(doc.id)}
    >
      <div
        className="file-icon"
        style={{ background: style.bg, color: style.color }}
      >
        {ext.slice(0, 4)}
      </div>
      <div className="file-info">
        <div className="file-name">{doc.display_name}</div>
        <div className="file-meta">
          {formatBytes(doc.size_bytes)} &middot; {formatDate(doc.uploaded_at)}
        </div>
      </div>
      {doc.tags.length > 0 && (
        <div className="file-tags">
          {doc.tags.slice(0, 2).map(tag => (
            <span key={tag} className="tag-badge">{tag}</span>
          ))}
          {doc.tags.length > 2 && (
            <span className="tag-badge">+{doc.tags.length - 2}</span>
          )}
        </div>
      )}
    </div>
  )
}

interface DocumentListProps {
  documents: DocumentMeta[]
  selectedId: string | null
  onSelect: (id: string) => void
}

export function DocumentList({ documents, selectedId, onSelect }: DocumentListProps) {
  if (!documents.length) {
    return <div className="empty-state">No documents found. Upload a file or sync your documents folder.</div>
  }

  return (
    <div className="document-list">
      {documents.map(doc => (
        <DocumentItem
          key={doc.id}
          doc={doc}
          selected={selectedId === doc.id}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}
