import type { Suggestion } from '../../api/interview'

interface Props {
  suggestion: Suggestion
  onAccept: (id: string) => void
  onReject: (id: string) => void
}

export default function SuggestionCard({ suggestion, onAccept, onReject }: Props) {
  return (
    <div className="suggestion-card">
      <div className="suggestion-header">
        Suggested {suggestion.action} for <strong>{suggestion.section}</strong>
      </div>
      {suggestion.original && (
        <div className="suggestion-original">
          <label>Current:</label>
          <p>{typeof suggestion.original === 'string' ? suggestion.original : JSON.stringify(suggestion.original)}</p>
        </div>
      )}
      {suggestion.proposed && (
        <div className="suggestion-proposed">
          <label>Proposed:</label>
          <p>{typeof suggestion.proposed === 'string' ? suggestion.proposed : JSON.stringify(suggestion.proposed)}</p>
        </div>
      )}
      <div className="suggestion-actions">
        <button className="btn-accept" onClick={() => onAccept(suggestion.suggestion_id)}>Accept</button>
        <button className="btn-reject" onClick={() => onReject(suggestion.suggestion_id)}>Reject</button>
      </div>
    </div>
  )
}
