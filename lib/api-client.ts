// API client utilities for frontend

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
    this.name = "ApiError"
  }
}

export async function uploadImageForAnalysis(imageBlob: Blob): Promise<{ analysisId: string; message: string }> {
  const formData = new FormData()
  formData.append("image", imageBlob, "face-capture.jpg")

  const response = await fetch("/api/analyze", {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Analysis failed" }))
    throw new ApiError(response.status, error.error || "Failed to analyze image")
  }

  return response.json()
}

export async function fetchAnalysisResults(analysisId: string) {
  const response = await fetch(`/api/results/${analysisId}`)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Failed to fetch results" }))
    throw new ApiError(response.status, error.error || "Failed to fetch analysis results")
  }

  return response.json()
}

export async function fetchRecommendations(input: { concerns: any[]; topK?: number }) {
  const response = await fetch(`/api/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Failed to fetch recommendations' }))
    throw new ApiError(response.status, error.error || 'Failed to fetch recommendations')
  }
  return response.json() as Promise<{ recommendations: { product: any; score: number }[] }>
}
