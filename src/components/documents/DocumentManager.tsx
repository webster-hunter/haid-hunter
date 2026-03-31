import { useState, useEffect, useCallback } from 'react'
import { TagSidebar } from './TagSidebar'
import { DocumentToolbar } from './DocumentToolbar'
import { DropZone } from './DropZone'
import { DocumentList } from './DocumentList'
import { DocumentPreview } from './DocumentPreview'
import ExtractionResultsPanel from './ExtractionResultsPanel'
import {
  fetchDocuments,
  fetchDocument,
  uploadDocuments,
  updateDocument,
  deleteDocument,
  syncDocuments,
} from '../../api/documents'
import { analyzeDocuments, acceptSuggestions } from '../../api/extraction'
import type { ExtractionResult, SelectionState } from '../../api/extraction'
import { fetchProfile } from '../../api/profile'
import { fetchTags, createTag, deleteTag } from '../../api/tags'
import type { DocumentMeta } from '../../api/documents'

const CATEGORIES = ['skills', 'technologies', 'experience_keywords', 'soft_skills'] as const

export default function DocumentManager() {
  const [documents, setDocuments] = useState<DocumentMeta[]>([])
  const [allDocuments, setAllDocuments] = useState<DocumentMeta[]>([])
  const [tags, setTags] = useState<string[]>([])
  const [activeTag, setActiveTag] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [selectedDoc, setSelectedDoc] = useState<DocumentMeta | null>(null)
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(true)

  // Extraction state
  const [checkedIds, setCheckedIds] = useState<Set<string>>(new Set())
  const [extractionResult, setExtractionResult] = useState<ExtractionResult | null>(null)
  const [extractionSelection, setExtractionSelection] = useState<SelectionState>({})
  const [extractionLoading, setExtractionLoading] = useState(false)
  const [profileSkills, setProfileSkills] = useState<string[]>([])

  const loadDocuments = useCallback(async () => {
    try {
      const docs = await fetchDocuments(activeTag ?? undefined, search || undefined)
      setDocuments(docs)
    } catch {
      setStatus('Failed to load documents.')
    }
  }, [activeTag, search])

  const loadAllDocuments = useCallback(async () => {
    try {
      const docs = await fetchDocuments()
      setAllDocuments(docs)
    } catch { /* counts will be stale but not break */ }
  }, [])

  const loadTags = useCallback(async () => {
    try {
      const t = await fetchTags()
      setTags(t)
    } catch {
      setStatus('Failed to load tags.')
    }
  }, [])

  useEffect(() => {
    Promise.all([loadDocuments(), loadTags(), loadAllDocuments()]).finally(() => setLoading(false))
  }, [loadDocuments, loadTags, loadAllDocuments])

  useEffect(() => {
    if (!selectedId) { setSelectedDoc(null); return }
    fetchDocument(selectedId).then(setSelectedDoc).catch(() => setSelectedDoc(null))
  }, [selectedId])

  const handleSelectDoc = (id: string) => {
    setSelectedId(id)
    setExtractionResult(null)
  }

  const handleCheck = (id: string) => {
    setCheckedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const handleAnalyze = async () => {
    setExtractionLoading(true)
    try {
      let skills: string[] = []
      try {
        const profile = await fetchProfile()
        skills = profile.skills ?? []
      } catch { /* proceed without existing skills */ }

      const data = await analyzeDocuments([...checkedIds])
      setProfileSkills(skills)
      setExtractionResult(data)

      const sel: SelectionState = {}
      for (const key of CATEGORIES) {
        sel[key] = {}
        for (const item of data[key]) {
          if (!skills.includes(item)) {
            sel[key][item] = true
          }
        }
      }
      setExtractionSelection(sel)
    } catch {
      setStatus('Analysis failed.')
    } finally {
      setExtractionLoading(false)
    }
  }

  const handleToggle = (category: string, item: string) => {
    setExtractionSelection(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [item]: !prev[category]?.[item],
      },
    }))
  }

  const handleAccept = async () => {
    if (!extractionResult) return
    const filtered: ExtractionResult = {
      skills: [],
      technologies: [],
      experience_keywords: [],
      soft_skills: [],
    }
    for (const key of CATEGORIES) {
      filtered[key] = extractionResult[key].filter(
        item => !profileSkills.includes(item) && extractionSelection[key]?.[item]
      )
    }
    await acceptSuggestions(filtered)
    setExtractionResult(null)
  }

  const handleDismiss = () => {
    setExtractionResult(null)
  }

  const handleUpload = async (files: File[]) => {
    if (!files.length) return
    try {
      setStatus('Uploading...')
      await uploadDocuments(files, activeTag ? [activeTag] : undefined)
      setStatus('Upload complete.')
      await loadDocuments()
      await loadAllDocuments()
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
      await loadAllDocuments()
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
      await loadAllDocuments()
    } catch {
      setStatus('Failed to delete tag.')
    }
  }

  const handleUpdate = async (id: string, data: { display_name?: string; tags?: string[] }) => {
    try {
      const updated = await updateDocument(id, data)
      setDocuments(prev => prev.map(d => d.id === id ? updated : d))
      setAllDocuments(prev => prev.map(d => d.id === id ? updated : d))
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
      setAllDocuments(prev => prev.filter(d => d.id !== id))
      if (selectedId === id) { setSelectedId(null); setSelectedDoc(null) }
      setCheckedIds(prev => { const next = new Set(prev); next.delete(id); return next })
      await loadTags()
    } catch {
      setStatus('Failed to delete document.')
    }
  }

  if (loading) {
    return (
      <div className="document-manager">
        <h1>Documents</h1>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="document-manager">
      <h1>Documents</h1>
      <div className="document-manager-layout">
        <TagSidebar
          tags={tags}
          allDocuments={allDocuments}
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
            checkedCount={checkedIds.size}
            onAnalyze={handleAnalyze}
            extractionLoading={extractionLoading}
          />
          <DropZone onDrop={handleDrop} />
          {status && <div className="status-bar">{status}</div>}
          <DocumentList
            documents={documents}
            selectedId={selectedId}
            checkedIds={checkedIds}
            onSelect={handleSelectDoc}
            onCheck={handleCheck}
          />
        </div>

        {extractionResult ? (
          <ExtractionResultsPanel
            result={extractionResult}
            selection={extractionSelection}
            existingSkills={profileSkills}
            onToggle={handleToggle}
            onAccept={handleAccept}
            onReanalyze={handleAnalyze}
            onDismiss={handleDismiss}
          />
        ) : (
          <DocumentPreview
            document={selectedDoc}
            allTags={tags}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
          />
        )}
      </div>
    </div>
  )
}
