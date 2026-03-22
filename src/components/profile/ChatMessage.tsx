interface Props {
  role: 'user' | 'assistant'
  content: string
}

export default function ChatMessage({ role, content }: Props) {
  return <div className={`chat-message ${role}`}>{content}</div>
}
