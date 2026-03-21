// Stub - will be fully implemented in Task 13
interface DocumentToolbarProps {
  search: string
  onSearchChange: (value: string) => void
  onUpload: (files: File[]) => void
  onSync: () => void
}

export function DocumentToolbar({ search, onSearchChange, onUpload, onSync }: DocumentToolbarProps) {
  return (
    <div className="document-toolbar">
      <input
        className="form-input toolbar-search"
        placeholder="Search documents..."
        value={search}
        onChange={e => onSearchChange(e.target.value)}
      />
      <button className="btn btn-primary" onClick={() => onUpload([])}>Upload</button>
      <button className="btn btn-secondary" onClick={onSync}>Sync</button>
    </div>
  )
}
