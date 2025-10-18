import { NextRequest, NextResponse } from "next/server"
import { query as queryJson } from "@/lib/vector-index"
import { embedAnalysisConcerns } from "@/lib/embeddings"
import { getSupabaseAdmin } from "@/lib/supabase"

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const concerns = body?.concerns
    const topK = Math.max(1, Math.min(25, body?.topK ?? 5))
    if (!Array.isArray(concerns)) {
      return NextResponse.json({ error: "concerns array required" }, { status: 400 })
    }
    const vector = embedAnalysisConcerns(concerns)
    // Try Supabase first
    try {
      const supabase = getSupabaseAdmin()
      const { data, error } = await supabase.from('analysis_embeddings').select('*')
      if (!error && data) {
        // Compute cosine in app layer (MVP)
        const neighbors = data
          .map((row: any) => ({ id: row.analysis_id, vector: row.vector, metadata: row.metadata }))
          .map((it: any) => ({ ...it, score: (function(a:number[],b:number[]){
            const dot=(x:number[],y:number[])=>x.reduce((s,xi,i)=>s+xi*(y[i]||0),0)
            const n=(x:number[])=>Math.sqrt(x.reduce((s,xi)=>s+xi*xi,0))
            const d=n(a)*n(b);return d?dot(a,b)/d:0; })(vector, it.vector) }))
          .sort((a:any,b:any)=>b.score-a.score)
          .slice(0, topK)
        return NextResponse.json({ neighbors })
      }
    } catch {}

    // Fallback JSON index
    const results = queryJson(vector, topK)
    return NextResponse.json({ neighbors: results })
  } catch (e) {
    return NextResponse.json({ error: "internal error" }, { status: 500 })
  }
}

// Optional GET for health
export async function GET() {
  return NextResponse.json({ status: "ok" })
}


