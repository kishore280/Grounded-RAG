import type { ChangeEvent } from 'react'
import { useUploadPdf } from '../hooks/useUploadPdf'

export function UploadPanel() {
  const upload = useUploadPdf()

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) upload.mutate(file)
  }

  return (
    <div className="upload-panel">
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      {upload.isPending && <span>Uploading...</span>}
      {upload.isSuccess && <span>{upload.data.chunks_added} chunks added</span>}
      {upload.isError && <span className="error">{upload.error.message}</span>}
    </div>
  )
}
