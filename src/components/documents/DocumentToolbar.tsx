import { useRef } from 'react'

interface DocumentToolbarProps {
  search: string
  onSearchChange: (value: string) => void
  onUpload: (files: File[]) => void
  onSync: () => void
  checkedCount: number
  onAnalyze: () => void
  extractionLoading: boolean
}

export function DocumentToolbar({
  search,
  onSearchChange,
  onUpload,
  onSync,
  checkedCount,
  onAnalyze,
  extractionLoading,
}: DocumentToolbarProps) {
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
      {checkedCount > 0 && (
        <button
          className="btn btn-accent"
          onClick={onAnalyze}
          disabled={extractionLoading}
        >
          {extractionLoading ? 'Analyzing…' : 'Analyze Selected'}
        </button>
      )}
    </div>
  )
}
