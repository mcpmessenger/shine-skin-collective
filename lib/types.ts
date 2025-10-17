// Shared types for the application

export interface SkinConcern {
  name: string
  severity: "mild" | "moderate" | "severe"
  percentage: number
  description: string
  affectedAreas?: string[]
  recommendation?: string
}

export interface ProductRecommendation {
  id: string
  name: string
  brand: string
  description: string
  price: number
  image: string
  targetConcerns: string[]
}

export interface AnalysisMetadata {
  captureDate: string
  imageQuality: string
  lightingCondition: string
  skinType: string
}

export interface AnalysisResult {
  id: string
  metadata?: AnalysisMetadata
  concerns: SkinConcern[]
  recommendations: ProductRecommendation[]
}

export interface AnalysisResponse {
  analysisId: string
  message: string
  status: "processing" | "completed" | "failed"
}
