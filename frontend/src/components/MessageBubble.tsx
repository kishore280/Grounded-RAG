export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citationAccuracy?: number
}

export function MessageBubble({ message }: { message: ChatMessage }) {
  return (
    <div className={`message ${message.role}`}>
      <p>{message.content}</p>
      {message.citationAccuracy !== undefined && (
        <span className="accuracy">
          citation accuracy: {(message.citationAccuracy * 100).toFixed(0)}%
        </span>
      )}
    </div>
  )
}
