import { useState, useEffect, useCallback } from 'react'
import { TagSidebar } from './TagSidebar'
import { DocumentToolbar } from './DocumentToolbar'
import { DropZone } from './DropZone'
import { DocumentList } from './DocumentList'
import { DocumentPreview } from './DocumentPreview'
import {
  fetchDocuments,
  fetchDocument,
  uploadDocuments,
  updateDocument,
  deleteDocument,
  syncDocuments,
} from '../../api/documents'
import { fetchTags, createTag, deleteTag } from '../../api/tags'
import type { DocumentMeta } from '../../api/documents'

export default function DocumentManager() {
  const [documents, setDocuments] = useState<DocumentMeta[]>([])
  const [tags, setTags] = useState<string[]>([])
  const [activeTag, setActiveTag] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [selectedDoc, setSelectedDoc] = useState<DocumentMeta | null>(null)
  const [status, setStatus] = useState('')

  const loadDocuments = useCallback(async () => {
    try {
      const docs = await fetchDocuments(activeTag ?? undefined, search || undefined)
      setDocuments(docs)
    } catch {
      setStatus('Failed to load documents.')
    }
  }, [activeTag, search])

  const loadTags = useCallback(async () => {
    try {
      const t = await fetchTags()
      setTags(t)
    } catch {
      setStatus('Failed to load tags.')
    }
  }, [])

  useEffect(() => {
    loadDocuments()
    loadTags()
  }, [loadDocuments, loadTags])

  useEffect(() => {
    if (!selectedId) { setSelectedDoc(null); return }
    fetchDocument(selectedId).then(setSelectedDoc).catch(() => setSelectedDoc(null))
  }, [selectedId])

  const handleUpload = async (files: File[]) => {
    if (!files.length) return
    try {
      setStatus('Uploading...')
      await uploadDocuments(files, activeTag ? [activeTag] : undefined)
      setStatus('Upload complete.')
      await loadDocuments()
      await loadTags()
    } catch {
      setStatus('Upload failed.')
    }
  }

  const handleDrop = (files: File[]) => handleUpload(files)

  const handleSync = async () => {
    try {
      setStatus('Syncing...')
      const result = await syncDocuments()
      setStatus(`Sync complete. Added: ${result.added.length}, Removed: ${result.removed.length}`)
      await loadDocuments()
      await loadTags()
    } catch {
      setStatus('Sync failed.')
    }
  }

  const handleCreateTag = async (name: string) => {
    try {
      await createTag(name)
      await loadTags()
    } catch {
      setStatus('Failed to create tag.')
    }
  }

  const handleDeleteTag = async (name: string) => {
    try {
      await deleteTag(name)
      if (activeTag === name) setActiveTag(null)
      await loadTags()
      await loadDocuments()
    } catch {
      setStatus('Failed to delete tag.')
    }
  }

  const handleUpdate = async (id: string, data: { display_name?: string; tags?: string[] }) => {
    try {
      const updated = await updateDocument(id, data)
      setDocuments(prev => prev.map(d => d.id === id ? updated : d))
      if (selectedId === id) setSelectedDoc(updated)
      await loadTags()
    } catch {
      setStatus('Failed to update document.')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id)
      setDocuments(prev => prev.filter(d => d.id !== id))
      if (selectedId === id) { setSelectedId(null); setSelectedDoc(null) }
      await loadTags()
    } catch {
      setStatus('Failed to delete document.')
    }
  }

  return (
    <div>
      <h1 style={{ marginBottom: 'var(--space-lg)' }}>Documents</h1>
      <div className="document-manager-layout">
        <TagSidebar
          tags={tags}
          documents={documents}
          activeTag={activeTag}
          onSelectTag={setActiveTag}
          onCreateTag={handleCreateTag}
          onDeleteTag={handleDeleteTag}
        />

        <div className="document-list-panel" data-testid="document-list-panel">
          <DocumentToolbar
            search={search}
            onSearchChange={setSearch}
            onUpload={handleUpload}
            onSync={handleSync}
          />
          <DropZone onDrop={handleDrop} />
          {status && <div className="status-bar">{status}</div>}
          <DocumentList
            documents={documents}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </div>

        <DocumentPreview
          document={selectedDoc}
          allTags={tags}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
        />
      </div>
    </div>
  )
}
