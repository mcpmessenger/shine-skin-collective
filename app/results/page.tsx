"use client"

import { useEffect, useState } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Sparkles, Loader2, ArrowLeft, Camera, Clock, Droplets, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ProductRecommendations } from "@/components/product-recommendations"
import { fetchAnalysisResults, fetchRecommendations, ApiError } from "@/lib/api-client"
import type { AnalysisResult } from "@/lib/types"

export default function ResultsPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const analysisId = searchParams.get("id")

  const [results, setResults] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [recoLoading, setRecoLoading] = useState(false)
  const [scoredProducts, setScoredProducts] = useState<{ product: any; score: number }[] | null>(null)

  useEffect(() => {
    if (analysisId) {
      loadResults(analysisId)
    } else {
      setLoading(false)
      setError("No analysis ID provided")
    }
  }, [analysisId])

  const loadResults = async (id: string) => {
    try {
      const data = await fetchAnalysisResults(id)
      setResults(data)
      // fetch recommendations based on concerns via cosine similarity API
      setRecoLoading(true)
      const recos = await fetchRecommendations({ concerns: data.concerns, topK: 4 })
      setScoredProducts(recos.recommendations)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError("Failed to load analysis results")
      }
      console.error("Failed to fetch results:", err)
    } finally {
      setLoading(false)
      setRecoLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "mild":
        return "bg-green-500/20 text-green-400 border-green-500/30"
      case "moderate":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
      case "severe":
        return "bg-red-500/20 text-red-400 border-red-500/30"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <p className="text-muted-foreground">Analyzing your skin...</p>
        </div>
      </div>
    )
  }

  if (error || !results) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-center">
          <p className="text-muted-foreground">{error || "No results found"}</p>
          <Button onClick={() => router.push("/")} className="mt-4">
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur-lg">
        <div className="container mx-auto flex items-center justify-between px-4 py-4">
          <Button variant="ghost" size="icon" onClick={() => router.push("/")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <h1 className="text-lg font-bold">Shine Skin Collective</h1>
          </div>
          <div className="w-10" />
        </div>
      </header>

      <main className="container mx-auto max-w-4xl px-4 py-8">
        {results.metadata && (
          <Card className="mb-8 p-6">
            <h3 className="mb-4 text-lg font-semibold">Analysis Details</h3>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">Captured</p>
                  <p className="text-sm font-medium">{results.metadata.captureDate}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Camera className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">Quality</p>
                  <p className="text-sm font-medium">{results.metadata.imageQuality}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Sun className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">Lighting</p>
                  <p className="text-sm font-medium">{results.metadata.lightingCondition}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Droplets className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">Skin Type</p>
                  <p className="text-sm font-medium">{results.metadata.skinType}</p>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Analysis Results */}
        <section className="mb-12">
          <h2 className="mb-6 text-2xl font-bold">Your Skin Analysis</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {results.concerns.map((concern, index) => (
              <Card key={index} className="p-6">
                <div className="mb-3 flex items-start justify-between">
                  <h3 className="text-lg font-semibold">{concern.name}</h3>
                  <Badge className={getSeverityColor(concern.severity)}>{concern.severity}</Badge>
                </div>
                <div className="mb-3">
                  <div className="mb-1 flex justify-between text-sm">
                    <span className="text-muted-foreground">Detected</span>
                    <span className="font-medium">{concern.percentage}%</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div className="h-full bg-primary transition-all" style={{ width: `${concern.percentage}%` }} />
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">{concern.description}</p>

                {concern.affectedAreas && concern.affectedAreas.length > 0 && (
                  <div className="mt-3">
                    <p className="mb-1 text-xs font-medium text-muted-foreground">Affected Areas:</p>
                    <div className="flex flex-wrap gap-1">
                      {concern.affectedAreas.map((area, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {area}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {concern.recommendation && (
                  <div className="mt-3 rounded-lg bg-primary/5 p-3">
                    <p className="text-xs font-medium text-primary">Recommendation</p>
                    <p className="text-sm text-muted-foreground">{concern.recommendation}</p>
                  </div>
                )}
              </Card>
            ))}
          </div>
        </section>

        <ProductRecommendations
          products={(scoredProducts?.map((s) => s.product) ?? results.recommendations) as any}
          concerns={results.concerns.map((c) => c.name)}
        />

        {/* CTA */}
        <div className="mt-12 text-center">
          <Button variant="outline" size="lg" onClick={() => router.push("/")} className="gap-2">
            Analyze Again
          </Button>
        </div>
      </main>
    </div>
  )
}
