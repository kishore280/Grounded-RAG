import { useMutation } from '@tanstack/react-query'
import { uploadPdf } from '../api/client'

export function useUploadPdf() {
  return useMutation({
    mutationFn: uploadPdf,
  })
}
