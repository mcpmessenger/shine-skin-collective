import { type NextRequest, NextResponse } from "next/server"
import type { AnalysisResult } from "@/lib/types"

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const { id } = params

    if (!id || id.trim() === "") {
      return NextResponse.json({ error: "Analysis ID is required" }, { status: 400 })
    }

    // TODO: Fetch actual results from database
    // Example with Supabase:
    // const { data, error } = await supabase
    //   .from('analyses')
    //   .select('*')
    //   .eq('id', id)
    //   .single()
    //
    // if (error || !data) {
    //   return NextResponse.json(
    //     { error: 'Analysis not found' },
    //     { status: 404 }
    //   )
    // }
    //
    // return NextResponse.json(data.results)

    // Return mock data for now
    const mockResults: AnalysisResult = {
      id,
      metadata: {
        captureDate: new Date().toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          year: "numeric",
        }),
        imageQuality: "High",
        lightingCondition: "Good",
        skinType: "Combination",
      },
      concerns: [
        {
          name: "Skin Texture",
          severity: "moderate",
          percentage: 65,
          description: "Uneven texture detected with visible pores in T-zone area.",
          affectedAreas: ["Forehead", "Nose", "Chin"],
          recommendation: "Use gentle exfoliants 2-3 times per week to refine texture.",
        },
        {
          name: "Tone Evenness",
          severity: "mild",
          percentage: 35,
          description: "Minor variations in skin tone, particularly around cheeks.",
          affectedAreas: ["Cheeks", "Temples"],
          recommendation: "Apply vitamin C serum daily for brightening effects.",
        },
        {
          name: "Fine Lines",
          severity: "mild",
          percentage: 28,
          description: "Early signs of fine lines around eye area.",
          affectedAreas: ["Eye Area", "Forehead"],
          recommendation: "Use retinol-based products and maintain consistent hydration.",
        },
        {
          name: "Hydration",
          severity: "moderate",
          percentage: 58,
          description: "Skin appears slightly dehydrated, especially in cheek area.",
          affectedAreas: ["Cheeks", "Under Eyes"],
          recommendation: "Increase water intake and use hyaluronic acid-based moisturizers.",
        },
      ],
      recommendations: [
        {
          id: "glymed-1",
          name: "Serious Action Skin Peel #10",
          brand: "Glymed Plus",
          description: "Professional-grade peel to improve texture and tone evenness.",
          price: 68.0,
          image: "/skincare-peel-bottle.jpg",
          targetConcerns: ["Skin Texture", "Tone Evenness"],
        },
        {
          id: "glymed-2",
          name: "Ultra Hydro Gel",
          brand: "Glymed Plus",
          description: "Intensive hydration gel with hyaluronic acid for plump, dewy skin.",
          price: 52.0,
          image: "/hydrating-gel-jar.jpg",
          targetConcerns: ["Hydration"],
        },
        {
          id: "glymed-3",
          name: "Age Defense Renewal Cream",
          brand: "Glymed Plus",
          description: "Anti-aging cream targeting fine lines with peptides and antioxidants.",
          price: 89.0,
          image: "/anti-aging-cream-jar.jpg",
          targetConcerns: ["Fine Lines", "Skin Texture"],
        },
        {
          id: "glymed-4",
          name: "Living Cell Clarifier",
          brand: "Glymed Plus",
          description: "Refining toner to minimize pores and balance skin tone.",
          price: 44.0,
          image: "/toner-bottle.jpg",
          targetConcerns: ["Skin Texture", "Tone Evenness"],
        },
      ],
    }

    return NextResponse.json(mockResults)
  } catch (error) {
    console.error("Results fetch error:", error)
    return NextResponse.json(
      {
        error: "Failed to fetch analysis results",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}
