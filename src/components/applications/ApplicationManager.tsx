import { useState, useEffect, useCallback } from 'react'
import { fetchApplications, type Application } from '../../api/applications'
import ApplicationToolbar from './ApplicationToolbar'
import TableView from './TableView'
import KanbanView from './KanbanView'
import ApplicationModal from './ApplicationModal'

export default function ApplicationManager() {
  const [applications, setApplications] = useState<Application[]>([])
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [viewMode, setViewMode] = useState<'table' | 'kanban'>('table')
  const [modalOpen, setModalOpen] = useState(false)
  const [editingApp, setEditingApp] = useState<Application | null>(null)

  const loadApps = useCallback(async () => {
    try {
      const apps = await fetchApplications({
        search: search || undefined,
        status: statusFilter || undefined,
      })
      setApplications(apps)
    } catch (err) {
      console.error('Failed to load applications:', err)
    }
  }, [search, statusFilter])

  useEffect(() => {
    loadApps()
  }, [loadApps])

  const handleEdit = (app: Application) => {
    setEditingApp(app)
    setModalOpen(true)
  }

  const handleAdd = () => {
    setEditingApp(null)
    setModalOpen(true)
  }

  const handleModalClose = () => {
    setModalOpen(false)
    setEditingApp(null)
    loadApps()
  }

  return (
    <div className="application-manager">
      <h1>Applications</h1>
      <ApplicationToolbar
        search={search}
        onSearchChange={setSearch}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        onAdd={handleAdd}
      />
      {viewMode === 'table' ? (
        <TableView applications={applications} onRowClick={handleEdit} />
      ) : (
        <KanbanView applications={applications} onCardClick={handleEdit} onRefresh={loadApps} />
      )}
      {modalOpen && (
        <ApplicationModal application={editingApp} onClose={handleModalClose} />
      )}
    </div>
  )
}
