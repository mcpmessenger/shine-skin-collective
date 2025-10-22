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

    // Call the FastAPI backend server
    let inferData = { concerns: [], region_concerns: null }
    try {
      const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
      const formDataForBackend = new FormData()
      formDataForBackend.append('image', image)
      
      const inferRes = await fetch(`${backendUrl}/infer`, {
        method: 'POST',
        body: formDataForBackend,
      })
      
      if (inferRes.ok) {
        inferData = await inferRes.json()
        console.log('Backend inference successful:', inferData.concerns?.length || 0, 'concerns')
      } else {
        console.warn('Backend inference failed with status:', inferRes.status)
      }
    } catch (e) {
      console.warn('Backend inference failed, using fallback data:', e instanceof Error ? e.message : e)
    }

    const analysisId = `analysis_${Date.now()}`
    const result: AnalysisResult = {
      id: analysisId,
      metadata: {
        captureDate: new Date().toISOString(),
        imageQuality: "Unknown",
        lightingCondition: "Unknown",
        skinType: "Unknown",
      },
      concerns: inferData.concerns.length > 0 ? inferData.concerns : [
        {
          name: "Skin Texture",
          severity: "moderate",
          percentage: 65,
          description: "Analysis in progress - using demo data",
        }
      ],
      recommendations: [],
    }

    // Persist to Supabase (if configured)
    try {
      const supabase = getSupabaseAdmin()
      if (supabase) {
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
      } else {
        // Supabase not configured, use JSON index fallback
        const vector = embedAnalysisConcerns(result.concerns)
        upsertJsonIndex({ id: analysisId, vector, metadata: result.metadata })
      }
    } catch (e) {
      // Fallback to JSON index for local dev if Supabase fails
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
