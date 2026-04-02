import type { ExtractionResult, SelectionState } from '../../api/extraction'

interface ExtractionResultsPanelProps {
  result: ExtractionResult
  selection: SelectionState
  onToggle: (name: string) => void
  onAccept: () => void
  onReanalyze: () => void
  onDismiss: () => void
}

export default function ExtractionResultsPanel({
  result,
  selection,
  onToggle,
  onAccept,
  onReanalyze,
  onDismiss,
}: ExtractionResultsPanelProps) {
  if (result.skills.length === 0) {
    return (
      <div className="extraction-panel">
        <p>No suggestions found.</p>
        <button className="btn btn-secondary" onClick={onDismiss}>Done</button>
      </div>
    )
  }

  // Group skills by type
  const grouped: Record<string, typeof result.skills> = {}
  for (const skill of result.skills) {
    if (!grouped[skill.type]) grouped[skill.type] = []
    grouped[skill.type].push(skill)
  }

  return (
    <div className="extraction-panel">
      {Object.entries(grouped).map(([type, skills]) => (
        <div key={type} className="extraction-category">
          <h4>{type}</h4>
          <div className="extraction-chips">
            {skills.map(skill => {
              const selected = selection[skill.name] ?? false
              return (
                <span
                  key={skill.name}
                  className={`extraction-chip${selected ? '' : ' deselected'}`}
                  onClick={() => onToggle(skill.name)}
                >
                  {skill.name}
                </span>
              )
            })}
          </div>
        </div>
      ))}
      <div className="extraction-actions">
        <button className="btn btn-primary" onClick={onAccept}>Accept Selected</button>
        <button className="btn btn-secondary" onClick={onReanalyze}>Re-analyze</button>
        <button className="btn btn-secondary" onClick={onDismiss}>Done</button>
      </div>
    </div>
  )
}
