import { NextRequest, NextResponse } from "next/server"
import type { AnalysisResult, ProductRecommendation } from "@/lib/types"
import { cosineSimilarity, normalizeVector } from "@/lib/utils"

// Lightweight deterministic embedding: map concerns + severities to a vector
function embedConcerns(concerns: AnalysisResult["concerns"]): number[] {
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
  const vector = keys.map((k) => {
    const c = concerns.find((x) => x.name.toLowerCase().replace(/\s+/g, "_") === k)
    if (!c) return 0
    const sev = sevMap[c.severity] ?? 0.5
    return (c.percentage / 100) * sev
  })
  return normalizeVector(vector)
}

// Simple in-memory catalog; replace with DB later
const catalog: ProductRecommendation[] = [
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
]

// Embed products by mapping concerns into same vector space
function embedProduct(p: ProductRecommendation): number[] {
  const nameToKey = (s: string) => s.toLowerCase().replace(/\s+/g, "_")
  const keys = [
    "acne",
    "aging",
    "fine_lines_wrinkles",
    "hyperpigmentation",
    "pore_size",
    "redness",
    "textured_skin",
  ]
  const mapped = new Set(p.targetConcerns.map(nameToKey))
  const vector = keys.map((k) => (mapped.has(k) || mapped.has("skin_texture") ? 1 : 0))
  return normalizeVector(vector)
}

const catalogEmbeddings = catalog.map((p) => ({ product: p, vector: embedProduct(p) }))

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as { concerns: AnalysisResult["concerns"]; topK?: number }
    if (!body?.concerns || !Array.isArray(body.concerns)) {
      return NextResponse.json({ error: "concerns array required" }, { status: 400 })
    }
    const topK = Math.max(1, Math.min(10, body.topK ?? 4))

    const queryVec = embedConcerns(body.concerns)
    const scored = catalogEmbeddings
      .map((ce) => ({ product: ce.product, score: cosineSimilarity(queryVec, ce.vector) }))
      .sort((a, b) => b.score - a.score)
      .slice(0, topK)

    return NextResponse.json({ recommendations: scored })
  } catch (err) {
    console.error("recommend error", err)
    return NextResponse.json({ error: "internal error" }, { status: 500 })
  }
}

export async function GET() {
  return NextResponse.json({ status: "ok" })
}


