import { useState, useRef } from 'react'

interface DropZoneProps {
  onDrop: (files: File[]) => void
}

export function DropZone({ onDrop }: DropZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const dragCounter = useRef(0)

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    dragCounter.current++
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    dragCounter.current--
    if (dragCounter.current === 0) setIsDragging(false)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    dragCounter.current = 0
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    if (files.length) onDrop(files)
  }

  return (
    <div
      className={`drop-zone${isDragging ? ' active' : ''}`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <div className="drop-zone-icon">📁</div>
      <div className="drop-zone-text">Drop files here to upload</div>
      <div className="drop-zone-sub">Supports PDF, DOCX, TXT, and more</div>
    </div>
  )
}
