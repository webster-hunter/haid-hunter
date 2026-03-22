import type { Application } from '../../api/applications'
import KanbanCard from './KanbanCard'

interface Props {
  status: string
  label: string
  applications: Application[]
  onCardClick: (app: Application) => void
  onDrop: (status: string, appId: number) => void
  draggingId: number | null
}

export default function KanbanColumn({ status, label, applications, onCardClick, onDrop, draggingId }: Props) {
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const id = Number(e.dataTransfer.getData('text/plain'))
    if (!isNaN(id)) {
      onDrop(status, id)
    }
  }

  return (
    <div
      className="kanban-column"
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <div className="column-header">
        <span className="column-label">{label}</span>
        <span className="column-count">{applications.length}</span>
      </div>
      <div className="column-cards">
        {applications.map(app => (
          <KanbanCard
            key={app.id}
            application={app}
            onClick={onCardClick}
            isDragging={draggingId === app.id}
          />
        ))}
        {applications.length === 0 && (
          <div className="column-empty">No applications</div>
        )}
      </div>
    </div>
  )
}
