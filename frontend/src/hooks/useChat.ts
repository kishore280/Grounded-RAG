import { useMutation } from '@tanstack/react-query'
import { sendChatQuery } from '../api/client'

export function useChat() {
  return useMutation({
    mutationFn: sendChatQuery,
  })
}
