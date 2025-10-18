import { type NextRequest, NextResponse } from "next/server"
import type { AnalysisResponse, AnalysisResult } from "@/lib/types"
import { getSupabaseAdmin } from "@/lib/supabase"
import { embedAnalysisConcerns } from "@/lib/embeddings"
import { upsert as upsertJsonIndex } from "@/lib/vector-index"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const image = formData.get("image") as File

    if (!image) {
      return NextResponse.json({ error: "No image provided" }, { status: 400 })
    }

    // Validate image type
    if (!image.type.startsWith("image/")) {
      return NextResponse.json({ error: "Invalid file type. Please upload an image." }, { status: 400 })
    }

    // Validate image size (max 10MB)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (image.size > maxSize) {
      return NextResponse.json({ error: "Image too large. Maximum size is 10MB." }, { status: 400 })
    }

    // Call Python FastAPI inference server
    const form = new FormData()
    form.append("image", image)
    const PY_API = process.env.PY_INFER_URL || "http://localhost:8000"
    const inferRes = await fetch(`${PY_API}/infer`, { method: 'POST', body: form })
    if (!inferRes.ok) {
      const err = await inferRes.text()
      return NextResponse.json({ error: `Inference failed: ${err}` }, { status: 502 })
    }
    const inferData = await inferRes.json()

    const analysisId = `analysis_${Date.now()}`
    const result: AnalysisResult = {
      id: analysisId,
      metadata: {
        captureDate: new Date().toISOString(),
        imageQuality: "Unknown",
        lightingCondition: "Unknown",
        skinType: "Unknown",
      },
      concerns: inferData.concerns,
      recommendations: [],
    }

    // Persist to Supabase
    try {
      const supabase = getSupabaseAdmin()
      await supabase.from('analyses').insert({
        id: analysisId,
        metadata: result.metadata,
        concerns: result.concerns,
        recommendations: result.recommendations,
      })
      const vector = embedAnalysisConcerns(result.concerns)
      await supabase.from('analysis_embeddings').upsert({
        analysis_id: analysisId,
        vector,
        metadata: result.metadata,
      })
    } catch (e) {
      // Fallback to JSON index for local dev
      try {
        const vector = embedAnalysisConcerns(result.concerns)
        upsertJsonIndex({ id: analysisId, vector, metadata: result.metadata })
      } catch {}
    }

    const response: AnalysisResponse = { analysisId, message: "Analysis complete", status: "completed" }
    return NextResponse.json(response)
  } catch (error) {
    console.error("Analysis error:", error)
    return NextResponse.json(
      {
        error: "Internal server error during analysis",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}

// Health check endpoint
export async function GET() {
  return NextResponse.json({
    status: "ok",
    service: "image-analysis",
    timestamp: new Date().toISOString(),
  })
}
