import { useState, useRef, useEffect } from 'react'
import { startInterview, sendMessage, acceptSuggestion, rejectSuggestion, type Suggestion } from '../../api/interview'
import ChatMessage from './ChatMessage'
import SuggestionCard from './SuggestionCard'

interface ChatEntry {
  role: 'user' | 'assistant'
  content: string
  suggestion?: Suggestion | null
}

interface Props {
  onProfileUpdate: () => void
}

export default function InterviewChat({ onProfileUpdate }: Props) {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatEntry[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (bottomRef.current && typeof bottomRef.current.scrollIntoView === 'function') {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  const handleStart = async () => {
    setLoading(true)
    const { session_id, message } = await startInterview()
    setSessionId(session_id)
    setMessages([{ role: 'assistant', content: message }])
    setLoading(false)
  }

  const handleSend = async () => {
    if (!sessionId || !input.trim()) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)
    const result = await sendMessage(sessionId, userMsg)
    setMessages(prev => [...prev, { role: 'assistant', content: result.message, suggestion: result.suggestion }])
    setLoading(false)
  }

  const handleAccept = async (suggestionId: string) => {
    if (!sessionId) return
    await acceptSuggestion(sessionId, suggestionId)
    onProfileUpdate()
  }

  const handleReject = async (suggestionId: string) => {
    if (!sessionId) return
    await rejectSuggestion(sessionId, suggestionId)
  }

  return (
    <div className="interview-chat-inner">
      <h3>Interview</h3>
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i}>
            <ChatMessage role={m.role} content={m.content} />
            {m.suggestion && (
              <SuggestionCard suggestion={m.suggestion} onAccept={handleAccept} onReject={handleReject} />
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      {!sessionId ? (
        <button onClick={handleStart} disabled={loading}>Start Interview</button>
      ) : (
        <div className="chat-input">
          <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSend()} placeholder="Type a message..." />
          <button onClick={handleSend} disabled={loading || !input.trim()}>Send</button>
        </div>
      )}
    </div>
  )
}
