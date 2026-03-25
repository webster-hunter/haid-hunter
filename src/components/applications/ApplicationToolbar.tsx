interface Props {
  search: string
  onSearchChange: (value: string) => void
  statusFilter: string
  onStatusFilterChange: (value: string) => void
  viewMode: 'table' | 'kanban'
  onViewModeChange: (mode: 'table' | 'kanban') => void
  onAdd: () => void
}

export default function ApplicationToolbar({
  search,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  viewMode,
  onViewModeChange,
  onAdd,
}: Props) {
  return (
    <div className="application-toolbar">
      <input
        type="text"
        value={search}
        onChange={e => onSearchChange(e.target.value)}
        placeholder="Search applications..."
        className="search-input form-input"
      />
      <select
        value={statusFilter}
        onChange={e => onStatusFilterChange(e.target.value)}
        className="form-input"
      >
        <option value="">All Statuses</option>
        <option value="bookmarked">Bookmarked</option>
        <option value="applied">Applied</option>
        <option value="in_progress">In Progress</option>
        <option value="interviewing">Interviewing</option>
        <option value="offer">Offer</option>
        <option value="rejected">Rejected</option>
        <option value="closed">Closed</option>
      </select>
      <div className="view-toggle">
        <button
          className={viewMode === 'table' ? 'active' : ''}
          onClick={() => onViewModeChange('table')}
        >
          Table
        </button>
        <button
          className={viewMode === 'kanban' ? 'active' : ''}
          onClick={() => onViewModeChange('kanban')}
        >
          Kanban
        </button>
      </div>
      <button className="btn btn-primary" onClick={onAdd}>+ Add Application</button>
    </div>
  )
}
