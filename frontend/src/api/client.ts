import type { ChatResponse, UploadResponse } from './types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

async function parseOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    throw new Error(`Request to ${res.url} failed with ${res.status}`)
  }
  return res.json() as Promise<T>
}

export function uploadPdf(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  return fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  }).then((res) => parseOrThrow<UploadResponse>(res))
}

export function sendChatQuery(query: string): Promise<ChatResponse> {
  return fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  }).then((res) => parseOrThrow<ChatResponse>(res))
}
