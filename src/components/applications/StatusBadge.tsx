const STATUS_CLASSES: Record<string, string> = {
  bookmarked: 'status-muted',
  applied: 'status-primary',
  in_progress: 'status-accent',
  offer: 'status-success',
  closed: 'status-error',
}

const STATUS_LABELS: Record<string, string> = {
  bookmarked: 'Bookmarked',
  applied: 'Applied',
  in_progress: 'In Progress',
  offer: 'Offer',
  closed: 'Closed',
}

export default function StatusBadge({ status }: { status: string }) {
  return <span className={`status-badge ${STATUS_CLASSES[status] || ''}`}>{STATUS_LABELS[status] || status}</span>
}
