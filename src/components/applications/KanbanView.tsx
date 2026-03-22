import { useState } from 'react'
import type { Application } from '../../api/applications'
import { updateApplicationStatus } from '../../api/applications'
import KanbanColumn from './KanbanColumn'

const STATUSES = [
  { key: 'bookmarked', label: 'Bookmarked' },
  { key: 'applied', label: 'Applied' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'offer', label: 'Offer' },
  { key: 'closed', label: 'Closed' },
]

interface Props {
  applications: Application[]
  onCardClick: (app: Application) => void
  onRefresh: () => void
}

export default function KanbanView({ applications, onCardClick, onRefresh }: Props) {
  const [draggingId, setDraggingId] = useState<number | null>(null)

  const handleDrop = async (status: string, appId: number) => {
    const app = applications.find(a => a.id === appId)
    if (!app || app.status === status) return
    setDraggingId(null)
    try {
      await updateApplicationStatus(appId, status)
      onRefresh()
    } catch (err) {
      console.error('Failed to update status:', err)
    }
  }

  const grouped = STATUSES.reduce<Record<string, Application[]>>((acc, { key }) => {
    acc[key] = applications.filter(a => a.status === key)
    return acc
  }, {})

  return (
    <div
      className="kanban-board"
      onDragStart={e => {
        const id = Number((e.target as HTMLElement).closest('[draggable]')?.getAttribute('data-id'))
        if (!isNaN(id)) setDraggingId(id)
      }}
    >
      {STATUSES.map(({ key, label }) => (
        <KanbanColumn
          key={key}
          status={key}
          label={label}
          applications={grouped[key] || []}
          onCardClick={onCardClick}
          onDrop={handleDrop}
          draggingId={draggingId}
        />
      ))}
    </div>
  )
}
