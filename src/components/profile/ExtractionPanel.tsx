import { useState } from 'react'
import { analyzeDocuments, acceptSuggestions, type ExtractionResult } from '../../api/extraction'

interface Props {
  onAccept: () => void
}

type SelectionState = Record<string, Record<string, boolean>>

const CATEGORIES: { key: keyof ExtractionResult; label: string }[] = [
  { key: 'skills', label: 'Skills' },
  { key: 'technologies', label: 'Technologies' },
  { key: 'experience_keywords', label: 'Experience Keywords' },
  { key: 'soft_skills', label: 'Soft Skills' },
]

export default function ExtractionPanel({ onAccept }: Props) {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ExtractionResult | null>(() => {
    const cached = localStorage.getItem('extraction_result')
    if (cached) {
      localStorage.removeItem('extraction_result')
      try { return JSON.parse(cached) } catch { return null }
    }
    return null
  })
  const [selection, setSelection] = useState<SelectionState>(() => {
    const cached = localStorage.getItem('extraction_result')
    if (cached) {
      try {
        const data = JSON.parse(cached) as ExtractionResult
        const sel: SelectionState = {}
        for (const { key } of CATEGORIES) {
          sel[key] = {}
          for (const item of data[key]) {
            sel[key][item] = true
          }
        }
        return sel
      } catch { return {} }
    }
    return {}
  })

  const handleAnalyze = async () => {
    setLoading(true)
    try {
      const data = await analyzeDocuments()
      setResult(data)
      const sel: SelectionState = {}
      for (const { key } of CATEGORIES) {
        sel[key] = {}
        for (const item of data[key]) {
          sel[key][item] = true
        }
      }
      setSelection(sel)
    } finally {
      setLoading(false)
    }
  }

  const toggleItem = (category: string, item: string) => {
    setSelection(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [item]: !prev[category][item],
      },
    }))
  }

  const handleAccept = async () => {
    if (!result) return
    const filtered: ExtractionResult = {
      skills: [],
      technologies: [],
      experience_keywords: [],
      soft_skills: [],
    }
    for (const { key } of CATEGORIES) {
      filtered[key] = result[key].filter(item => selection[key]?.[item])
    }
    await acceptSuggestions(filtered)
    onAccept()
  }

  const isEmpty = result && CATEGORIES.every(({ key }) => result[key].length === 0)

  return (
    <div className="extraction-panel">
      {!result && !loading && (
        <button className="btn btn-primary" onClick={handleAnalyze}>
          Analyze Documents
        </button>
      )}
      {loading && <p>Analyzing...</p>}
      {result && isEmpty && <p>No suggestions found.</p>}
      {result && !isEmpty && (
        <>
          {CATEGORIES.map(({ key, label }) =>
            result[key].length > 0 ? (
              <div key={key} className="extraction-category">
                <h4>{label}</h4>
                <div className="extraction-chips">
                  {result[key].map(item => (
                    <span
                      key={item}
                      className={`extraction-chip ${selection[key]?.[item] ? '' : 'deselected'}`}
                      onClick={() => toggleItem(key, item)}
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ) : null
          )}
          <div className="extraction-actions">
            <button className="btn btn-primary" onClick={handleAccept}>
              Accept Selected
            </button>
            <button className="btn btn-secondary" onClick={handleAnalyze}>
              Re-analyze
            </button>
          </div>
        </>
      )}
    </div>
  )
}
