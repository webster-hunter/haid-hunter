import { useState, useEffect } from 'react'
import type { DocumentMeta } from '../../api/documents'
import { getContentUrl } from '../../api/documents'

const PREVIEWABLE_TEXT = [
  'text/plain',
  'text/markdown',
  'text/csv',
  'application/json',
]

const PREVIEWABLE_PDF = ['application/pdf']

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
}

interface DocumentPreviewProps {
  document: DocumentMeta | null
  allTags: string[]
  onUpdate: (id: string, data: { display_name?: string; tags?: string[] }) => void
  onDelete: (id: string) => void
}

export function DocumentPreview({ document, allTags, onUpdate, onDelete }: DocumentPreviewProps) {
  const [textContent, setTextContent] = useState<string | null>(null)
  const [loadingText, setLoadingText] = useState(false)

  useEffect(() => {
    if (!document) { setTextContent(null); return }
    if (PREVIEWABLE_TEXT.includes(document.mime_type)) {
      setLoadingText(true)
      fetch(getContentUrl(document.id))
        .then(r => r.text())
        .then(setTextContent)
        .catch(() => setTextContent('Failed to load preview.'))
        .finally(() => setLoadingText(false))
    } else {
      setTextContent(null)
    }
  }, [document])

  const handleRemoveTag = (tag: string) => {
    if (!document) return
    const newTags = document.tags.filter(t => t !== tag)
    onUpdate(document.id, { tags: newTags })
  }

  const handleAddTag = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (!document) return
    const tag = e.target.value
    if (!tag || document.tags.includes(tag)) return
    onUpdate(document.id, { tags: [...document.tags, tag] })
    e.target.value = ''
  }

  if (!document) {
    return (
      <div
        className="document-preview card"
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-muted)', fontSize: 14 }}
      >
        Select a document to preview
      </div>
    )
  }

  const availableTags = allTags.filter(t => !document.tags.includes(t))
  const isPdf = PREVIEWABLE_PDF.includes(document.mime_type)
  const isText = PREVIEWABLE_TEXT.includes(document.mime_type)
  const isPreviewable = isPdf || isText

  return (
    <div className="document-preview card">
      <div className="preview-header">
        <div className="preview-filename">{document.display_name}</div>
        <div className="preview-meta">
          {formatBytes(document.size_bytes)} &middot; {formatDate(document.uploaded_at)}
        </div>
        <div className="preview-tags">
          {document.tags.map(tag => (
            <span key={tag} className="preview-tag">
              {tag}
              <span
                className="remove"
                onClick={() => handleRemoveTag(tag)}
                role="button"
                aria-label={`Remove tag ${tag}`}
              >
                ×
              </span>
            </span>
          ))}
          {availableTags.length > 0 && (
            <select
              className="add-tag-select"
              onChange={handleAddTag}
              defaultValue=""
              aria-label="Add tag"
            >
              <option value="" disabled>+ tag</option>
              {availableTags.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          )}
        </div>
      </div>

      <div className="preview-content">
        {isPdf && (
          <iframe
            className="pdf-preview"
            src={getContentUrl(document.id)}
            title={document.display_name}
          />
        )}
        {isText && (
          loadingText
            ? <div style={{ color: 'var(--color-muted)', fontSize: 14 }}>Loading...</div>
            : <pre className="text-preview">{textContent}</pre>
        )}
        {!isPreviewable && (
          <div className="no-preview">No preview available for this file type.</div>
        )}
      </div>

      <div className="preview-actions">
        <a
          className="btn btn-secondary"
          href={getContentUrl(document.id)}
          download={document.display_name}
        >
          Download
        </a>
        <button
          className="btn btn-danger"
          onClick={() => onDelete(document.id)}
        >
          Delete
        </button>
      </div>
    </div>
  )
}
