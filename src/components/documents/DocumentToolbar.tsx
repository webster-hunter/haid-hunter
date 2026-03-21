import { useRef } from 'react'

interface DocumentToolbarProps {
  search: string
  onSearchChange: (value: string) => void
  onUpload: (files: File[]) => void
  onSync: () => void
}

export function DocumentToolbar({ search, onSearchChange, onUpload, onSync }: DocumentToolbarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? [])
    if (files.length) {
      onUpload(files)
      e.target.value = ''
    }
  }

  return (
    <div className="document-toolbar">
      <input
        className="form-input toolbar-search"
        placeholder="Search documents..."
        value={search}
        onChange={e => onSearchChange(e.target.value)}
      />
      <input
        ref={fileInputRef}
        type="file"
        multiple
        style={{ display: 'none' }}
        onChange={handleFileChange}
        aria-label="Upload files"
      />
      <button
        className="btn btn-primary"
        onClick={() => fileInputRef.current?.click()}
      >
        Upload
      </button>
      <button className="btn btn-secondary" onClick={onSync}>
        Sync
      </button>
    </div>
  )
}
