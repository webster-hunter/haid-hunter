export interface Suggestion {
  suggestion_id: string
  section: string
  action: string
  target: Record<string, unknown>
  original: string | null
  proposed: string | null
}

export interface InterviewMessage {
  message: string
  suggestion?: Suggestion | null
}

export async function startInterview(): Promise<{ session_id: string; message: string; suggestions: Suggestion[] }> {
  const res = await fetch('/api/interview/start', { method: 'POST' })
  if (!res.ok) throw new Error('Failed to start interview')
  return res.json()
}

export async function sendMessage(sessionId: string, message: string): Promise<InterviewMessage> {
  const res = await fetch('/api/interview/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  })
  if (!res.ok) throw new Error('Failed to send message')
  return res.json()
}

export async function acceptSuggestion(sessionId: string, suggestionId: string): Promise<void> {
  const res = await fetch('/api/interview/accept', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, suggestion_id: suggestionId }),
  })
  if (!res.ok) throw new Error('Failed to accept suggestion')
}

export async function rejectSuggestion(sessionId: string, suggestionId: string): Promise<void> {
  const res = await fetch('/api/interview/reject', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, suggestion_id: suggestionId }),
  })
  if (!res.ok) throw new Error('Failed to reject suggestion')
}
