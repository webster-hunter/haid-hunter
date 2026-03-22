import { useEffect, useState } from 'react'
import { fetchDocuments, type DocumentMeta } from '../../api/documents'

interface Props {
  onSelect: (doc: DocumentMeta) => void
  excludeIds?: string[]
}

export default function DocumentPicker({ onSelect, excludeIds = [] }: Props) {
  const [docs, setDocs] = useState<DocumentMeta[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDocuments().then(setDocs).finally(() => setLoading(false))
  }, [])

  const filtered = docs.filter(d =>
    !excludeIds.includes(d.id) &&
    (d.display_name.toLowerCase().includes(search.toLowerCase()) ||
     d.original_name.toLowerCase().includes(search.toLowerCase()))
  )

  if (loading) return <div className="picker-loading">Loading documents...</div>

  return (
    <div className="document-picker">
      <input
        type="text"
        value={search}
        onChange={e => setSearch(e.target.value)}
        placeholder="Search documents..."
        className="form-input picker-search"
      />
      <div className="picker-list">
        {filtered.length === 0 ? (
          <div className="picker-empty">No documents available</div>
        ) : (
          filtered.map(doc => (
            <div
              key={doc.id}
              className="picker-item"
              onClick={() => onSelect(doc)}
              role="button"
              tabIndex={0}
              onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') onSelect(doc) }}
            >
              <span className="picker-name">{doc.display_name || doc.original_name}</span>
              <span className="picker-tags">
                {doc.tags.map(t => <span key={t} className="tag-badge">{t}</span>)}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
