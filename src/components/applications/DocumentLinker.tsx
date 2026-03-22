import { useState } from 'react'
import type { LinkedDocument } from '../../api/applications'
import { linkDocument, unlinkDocument } from '../../api/applications'
import type { DocumentMeta } from '../../api/documents'
import DocumentPicker from './DocumentPicker'

interface Props {
  appId: number
  linkedDocs: LinkedDocument[]
  onUpdate: (docs: LinkedDocument[]) => void
}

export default function DocumentLinker({ appId, linkedDocs, onUpdate }: Props) {
  const [showPicker, setShowPicker] = useState(false)
  const [linking, setLinking] = useState(false)

  const handleLink = async (doc: DocumentMeta) => {
    setLinking(true)
    setShowPicker(false)
    try {
      const linked = await linkDocument(appId, doc.id)
      onUpdate([...linkedDocs, linked])
    } catch (err) {
      console.error('Failed to link document:', err)
    } finally {
      setLinking(false)
    }
  }

  const handleUnlink = async (linkId: number) => {
    try {
      await unlinkDocument(appId, linkId)
      onUpdate(linkedDocs.filter(d => d.id !== linkId))
    } catch (err) {
      console.error('Failed to unlink document:', err)
    }
  }

  const excludeIds = linkedDocs.map(d => d.document_id)

  return (
    <div className="document-linker">
      <div className="linker-header">
        <span className="form-label">Linked Documents</span>
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() => setShowPicker(!showPicker)}
          disabled={linking}
        >
          {showPicker ? 'Cancel' : '+ Link Document'}
        </button>
      </div>
      {showPicker && (
        <DocumentPicker onSelect={handleLink} excludeIds={excludeIds} />
      )}
      {linkedDocs.length === 0 && !showPicker ? (
        <div className="linker-empty">No documents linked yet</div>
      ) : (
        <ul className="linker-list">
          {linkedDocs.map(link => (
            <li key={link.id} className="linker-item">
              <span className="linker-doc-id">{link.document_id}</span>
              {link.role && <span className="linker-role tag-badge">{link.role}</span>}
              <button
                type="button"
                className="btn btn-danger btn-sm linker-remove"
                onClick={() => handleUnlink(link.id)}
                aria-label="Remove link"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
