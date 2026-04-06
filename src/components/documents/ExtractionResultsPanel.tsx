import type { ExtractionResult, SelectionState } from '../../api/extraction'

interface ExtractionResultsPanelProps {
  result: ExtractionResult
  selection: SelectionState
  onToggle: (name: string) => void
  onToggleAll: (selectAll: boolean) => void
  onAccept: () => void
  onReanalyze: () => void
  onDismiss: () => void
}

export default function ExtractionResultsPanel({
  result,
  selection,
  onToggle,
  onToggleAll,
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

  const allSelected = result.skills.every(s => selection[s.name])

  return (
    <div className="extraction-panel">
      <div className="extraction-toggle-all">
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => onToggleAll(!allSelected)}
        >
          {allSelected ? 'Deselect All' : 'Select All'}
        </button>
      </div>
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
