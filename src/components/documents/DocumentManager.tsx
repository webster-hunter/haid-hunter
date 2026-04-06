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
import { analyzeDocuments } from '../../api/extraction'
import type { ExtractionResult, SelectionState, TypedSkill } from '../../api/extraction'
import { fetchProfile, patchSection } from '../../api/profile'
import { fetchTags, createTag, deleteTag } from '../../api/tags'
import type { DocumentMeta } from '../../api/documents'

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
  const [profileSkills, setProfileSkills] = useState<TypedSkill[]>([])

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

  const handleCheckTag = (tag: string) => {
    const tagDocs = allDocuments.filter(d => d.tags.includes(tag))
    const allChecked = tagDocs.every(d => checkedIds.has(d.id))
    setCheckedIds(prev => {
      const next = new Set(prev)
      if (allChecked) {
        tagDocs.forEach(d => next.delete(d.id))
      } else {
        tagDocs.forEach(d => next.add(d.id))
      }
      return next
    })
  }

  const handleAnalyze = async () => {
    setExtractionLoading(true)
    try {
      let skills: TypedSkill[] = []
      try {
        const profile = await fetchProfile()
        skills = profile.skills ?? []
      } catch { /* proceed without existing skills */ }

      const data = await analyzeDocuments([...checkedIds])
      setProfileSkills(skills)
      setExtractionResult(data)

      const profileNames = new Set(skills.map(s => s.name))
      const sel: SelectionState = {}
      for (const skill of data.skills) {
        sel[skill.name] = profileNames.has(skill.name)
      }
      setExtractionSelection(sel)
    } catch {
      setStatus('Analysis failed.')
    } finally {
      setExtractionLoading(false)
    }
  }

  const handleToggle = (name: string) => {
    setExtractionSelection(prev => ({
      ...prev,
      [name]: !prev[name],
    }))
  }

  const handleToggleAll = (selectAll: boolean) => {
    if (!extractionResult) return
    const sel: SelectionState = {}
    for (const skill of extractionResult.skills) {
      sel[skill.name] = selectAll
    }
    setExtractionSelection(sel)
  }

  const handleAccept = async () => {
    if (!extractionResult) return
    const updatedSkills = new Map<string, TypedSkill>()
    for (const s of profileSkills) {
      updatedSkills.set(s.name, s)
    }
    for (const skill of extractionResult.skills) {
      if (extractionSelection[skill.name]) {
        updatedSkills.set(skill.name, skill)
      } else {
        updatedSkills.delete(skill.name)
      }
    }
    await patchSection('skills', [...updatedSkills.values()])
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
          checkedIds={checkedIds}
          onCheckTag={handleCheckTag}
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
            onToggle={handleToggle}
            onToggleAll={handleToggleAll}
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
