export interface ExtractionResult {
  skills: string[]
  technologies: string[]
  experience_keywords: string[]
  soft_skills: string[]
}

export async function analyzeDocuments(): Promise<ExtractionResult> {
  const res = await fetch('/api/extraction/analyze', { method: 'POST' })
  if (!res.ok) throw new Error('Failed to analyze documents')
  return res.json()
}

export async function acceptSuggestions(suggestions: ExtractionResult): Promise<unknown> {
  const res = await fetch('/api/extraction/accept', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(suggestions),
  })
  if (!res.ok) throw new Error('Failed to accept suggestions')
  return res.json()
}
