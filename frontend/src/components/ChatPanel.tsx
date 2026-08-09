import { useState } from 'react'
import { useChat } from '../hooks/useChat'
import { MessageBubble, type ChatMessage } from './MessageBubble'

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [query, setQuery] = useState('')
  const chat = useChat()

  const handleSend = () => {
    const question = query.trim()
    if (!question || chat.isPending) return

    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', content: question }])
    setQuery('')

    chat.mutate(question, {
      onSuccess: (data) => {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: data.answer,
            citationAccuracy: data.citation_accuracy,
          },
        ])
      },
    })
  }

  return (
    <div className="chat-panel">
      <div className="messages">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {chat.isPending && (
          <div className="message assistant">
            <p>Thinking...</p>
          </div>
        )}
        {chat.isError && (
          <div className="message assistant error">
            <p>{chat.error.message}</p>
          </div>
        )}
      </div>

      <div className="input-row">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a question about the uploaded PDF..."
        />
        <button onClick={handleSend} disabled={chat.isPending}>
          Send
        </button>
      </div>
    </div>
  )
}
