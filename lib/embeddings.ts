import type { AnalysisResult, AnalysisEmbedding } from "./types"
import { normalizeVector } from "./utils"

// Deterministic 7-D embedding based on concerns and severities
export function embedAnalysisConcerns(concerns: AnalysisResult["concerns"]): number[] {
  const keys = [
    "acne",
    "aging",
    "fine_lines_wrinkles",
    "hyperpigmentation",
    "pore_size",
    "redness",
    "textured_skin",
  ]
  const sevMap: Record<string, number> = { slight: 0.2, mild: 0.4, moderate: 0.6, severe: 0.8, advanced: 1.0, early_signs: 0.3 }
  const vec = keys.map((k) => {
    const c = concerns.find((x) => x.name.toLowerCase().replace(/\s+/g, "_") === k)
    if (!c) return 0
    const sev = sevMap[c.severity] ?? 0.5
    return (c.percentage / 100) * sev
  })
  return normalizeVector(vec)
}

export function toAnalysisEmbedding(result: AnalysisResult): AnalysisEmbedding {
  const vector = embedAnalysisConcerns(result.concerns)
  return { id: result.id, vector, concerns: result.concerns }
}


