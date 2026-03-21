// Stub - will be fully implemented in Task 13
import type { DocumentMeta } from '../../api/documents'

interface DocumentListProps {
  documents: DocumentMeta[]
  selectedId: string | null
  onSelect: (id: string) => void
}

export function DocumentList({ documents, selectedId, onSelect }: DocumentListProps) {
  if (!documents.length) {
    return <div className="empty-state">No documents found.</div>
  }

  return (
    <div className="document-list">
      {documents.map(doc => (
        <div
          key={doc.id}
          className={`document-item${selectedId === doc.id ? ' selected' : ''}`}
          onClick={() => onSelect(doc.id)}
        >
          <div className="file-info">
            <div className="file-name">{doc.display_name}</div>
          </div>
        </div>
      ))}
    </div>
  )
}
