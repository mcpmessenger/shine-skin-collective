"use client"

import { useState } from "react"
import { ShoppingBag, Sparkles, Filter } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface Product {
  id: string
  name: string
  brand: string
  description: string
  price: number
  image: string
  targetConcerns: string[]
}

interface ProductRecommendationsProps {
  products: Product[]
  concerns: string[]
}

export function ProductRecommendations({ products, concerns }: ProductRecommendationsProps) {
  const [selectedConcern, setSelectedConcern] = useState<string | null>(null)

  const filteredProducts = selectedConcern
    ? products.filter((p) => p.targetConcerns.includes(selectedConcern))
    : products

  return (
    <section>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold">Recommended for You</h2>
          <p className="text-sm text-muted-foreground">Personalized products based on your skin analysis</p>
        </div>
        <Badge variant="secondary" className="w-fit gap-1">
          <Sparkles className="h-3 w-3" />
          Glymed Plus
        </Badge>
      </div>

      {/* Filter by concern */}
      {concerns.length > 0 && (
        <div className="mb-6 flex flex-wrap gap-2">
          <Button
            variant={selectedConcern === null ? "default" : "outline"}
            size="sm"
            onClick={() => setSelectedConcern(null)}
            className="gap-2"
          >
            <Filter className="h-3 w-3" />
            All Products
          </Button>
          {concerns.map((concern) => (
            <Button
              key={concern}
              variant={selectedConcern === concern ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedConcern(concern)}
            >
              {concern}
            </Button>
          ))}
        </div>
      )}

      {/* Product Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {filteredProducts.map((product) => (
          <Card key={product.id} className="overflow-hidden transition-shadow hover:shadow-lg">
            <div className="aspect-square bg-muted">
              <img
                src={product.image || "/placeholder.svg?height=400&width=400&query=skincare product"}
                alt={product.name}
                className="h-full w-full object-cover"
              />
            </div>
            <div className="p-6">
              <div className="mb-2 flex items-start justify-between gap-2">
                <div>
                  <p className="text-xs text-muted-foreground">{product.brand}</p>
                  <h3 className="font-semibold leading-tight">{product.name}</h3>
                </div>
                <p className="text-lg font-bold text-primary">${product.price}</p>
              </div>

              <p className="mb-4 text-sm text-muted-foreground">{product.description}</p>

              <div className="mb-4 flex flex-wrap gap-2">
                {product.targetConcerns.map((concern, idx) => (
                  <Badge key={idx} variant="outline" className="text-xs">
                    {concern}
                  </Badge>
                ))}
              </div>

              <Button className="w-full gap-2" size="lg">
                <ShoppingBag className="h-4 w-4" />
                Shop Now
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {filteredProducts.length === 0 && (
        <div className="py-12 text-center">
          <p className="text-muted-foreground">No products found for this concern.</p>
        </div>
      )}
    </section>
  )
}
