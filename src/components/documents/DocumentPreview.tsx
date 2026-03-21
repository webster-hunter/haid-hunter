// Stub - will be fully implemented in Task 14
import type { DocumentMeta } from '../../api/documents'

interface DocumentPreviewProps {
  document: DocumentMeta | null
  allTags: string[]
  onUpdate: (id: string, data: { display_name?: string; tags?: string[] }) => void
  onDelete: (id: string) => void
}

export function DocumentPreview({ document }: DocumentPreviewProps) {
  if (!document) {
    return (
      <div className="document-preview card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-muted)', fontSize: 14 }}>
        Select a document to preview
      </div>
    )
  }

  return (
    <div className="document-preview card">
      <div className="preview-header">
        <div className="preview-filename">{document.display_name}</div>
      </div>
      <div className="preview-content">
        <div className="no-preview">Preview not yet implemented</div>
      </div>
    </div>
  )
}
