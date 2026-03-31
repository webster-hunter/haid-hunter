import type { ExtractionResult, SelectionState } from '../../api/extraction'

const CATEGORIES: { key: keyof ExtractionResult; label: string }[] = [
  { key: 'skills', label: 'Skills' },
  { key: 'technologies', label: 'Technologies' },
  { key: 'experience_keywords', label: 'Experience Keywords' },
  { key: 'soft_skills', label: 'Soft Skills' },
]

interface ExtractionResultsPanelProps {
  result: ExtractionResult
  selection: SelectionState
  existingSkills: string[]
  onToggle: (category: keyof ExtractionResult, item: string) => void
  onAccept: () => void
  onReanalyze: () => void
  onDismiss: () => void
}

export default function ExtractionResultsPanel({
  result,
  selection,
  existingSkills,
  onToggle,
  onAccept,
  onReanalyze,
  onDismiss,
}: ExtractionResultsPanelProps) {
  const isEmpty = CATEGORIES.every(({ key }) => result[key].length === 0)
  const allInProfile =
    !isEmpty &&
    CATEGORIES.every(({ key }) =>
      result[key].every(item => existingSkills.includes(item))
    )

  if (isEmpty) {
    return (
      <div className="extraction-panel">
        <p>No suggestions found.</p>
        <button className="btn btn-secondary" onClick={onDismiss}>Done</button>
      </div>
    )
  }

  if (allInProfile) {
    return (
      <div className="extraction-panel">
        <p>All suggestions already in your profile.</p>
        <button className="btn btn-secondary" onClick={onDismiss}>Done</button>
      </div>
    )
  }

  return (
    <div className="extraction-panel">
      {CATEGORIES.map(({ key, label }) =>
        result[key].length > 0 ? (
          <div key={key} className="extraction-category">
            <h4>{label}</h4>
            <div className="extraction-chips">
              {result[key].map(item => {
                const inProfile = existingSkills.includes(item)
                if (inProfile) {
                  return (
                    <span key={item} className="extraction-chip already-in-profile">
                      {item}
                    </span>
                  )
                }
                const selected = selection[key]?.[item] ?? false
                return (
                  <span
                    key={item}
                    className={`extraction-chip${selected ? '' : ' deselected'}`}
                    onClick={() => onToggle(key, item)}
                  >
                    {item}
                  </span>
                )
              })}
            </div>
          </div>
        ) : null
      )}
      <div className="extraction-actions">
        <button className="btn btn-primary" onClick={onAccept}>Accept Selected</button>
        <button className="btn btn-secondary" onClick={onReanalyze}>Re-analyze</button>
        <button className="btn btn-secondary" onClick={onDismiss}>Done</button>
      </div>
    </div>
  )
}
