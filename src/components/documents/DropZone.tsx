// Stub - will be fully implemented in Task 13
interface DropZoneProps {
  onDrop: (files: File[]) => void
}

export function DropZone({ onDrop }: DropZoneProps) {
  return (
    <div className="drop-zone">
      <div className="drop-zone-icon">📁</div>
      <div className="drop-zone-text">Drop files here to upload</div>
      <div className="drop-zone-sub">or click Upload above</div>
    </div>
  )
}
