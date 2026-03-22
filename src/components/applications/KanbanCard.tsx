import type { Application } from '../../api/applications'
import StatusBadge from './StatusBadge'

interface Props {
  application: Application
  onClick: (app: Application) => void
  isDragging?: boolean
}

export default function KanbanCard({ application, onClick, isDragging }: Props) {
  const handleDragStart = (e: React.DragEvent<HTMLDivElement>) => {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', String(application.id))
  }

  return (
    <div
      className={`kanban-card${isDragging ? ' dimmed' : ''}`}
      draggable
      onDragStart={handleDragStart}
      onClick={() => onClick(application)}
      role="button"
      tabIndex={0}
      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') onClick(application) }}
    >
      <div className="kanban-card-company">{application.company}</div>
      <div className="kanban-card-position">{application.position}</div>
      <div className="kanban-card-footer">
        <StatusBadge status={application.status} />
        {application.has_referral && application.referral_name && (
          <span className="kanban-card-referral" title={`Referral: ${application.referral_name}`}>
            ★ {application.referral_name}
          </span>
        )}
        {(application.doc_count ?? 0) > 0 && (
          <span className="kanban-card-docs">{application.doc_count} doc{application.doc_count !== 1 ? 's' : ''}</span>
        )}
      </div>
    </div>
  )
}
