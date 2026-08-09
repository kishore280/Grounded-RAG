export interface UploadResponse {
  chunks_added: number
}

export interface ClaimVerification {
  claim: string
  chunk_ids: string[]
  shared_words: number
  result: boolean
}

export interface ChatResponse {
  answer: string
  citations: {
    citation_accuracy: number
    per_claim_results: ClaimVerification[]
  }
  citation_accuracy: number
}
