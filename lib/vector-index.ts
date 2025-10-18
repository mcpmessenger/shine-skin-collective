// JSON-backed vector index for analysis embeddings
export type VectorIndexItem = {
  id: string
  vector: number[]
  metadata?: Record<string, any>
}

const INDEX_PATH = process.env.VECTOR_INDEX_PATH || "./.data/vector-index.json"

import fs from 'fs'
import path from 'path'
import { cosineSimilarity, normalizeVector } from './utils'

function ensureDir(filePath: string) {
  const dir = path.dirname(filePath)
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
}

export function loadIndex(): VectorIndexItem[] {
  try {
    if (!fs.existsSync(INDEX_PATH)) return []
    const raw = fs.readFileSync(INDEX_PATH, 'utf-8')
    const data = JSON.parse(raw)
    if (Array.isArray(data)) return data
    return []
  } catch {
    return []
  }
}

export function saveIndex(items: VectorIndexItem[]) {
  ensureDir(INDEX_PATH)
  fs.writeFileSync(INDEX_PATH, JSON.stringify(items, null, 2), 'utf-8')
}

export function upsert(item: VectorIndexItem) {
  const items = loadIndex()
  const i = items.findIndex((x) => x.id === item.id)
  const normalized = { ...item, vector: normalizeVector(item.vector) }
  if (i >= 0) items[i] = normalized
  else items.push(normalized)
  saveIndex(items)
}

export function query(vector: number[], topK = 5) {
  const items = loadIndex()
  const q = normalizeVector(vector)
  return items
    .map((it) => ({ ...it, score: cosineSimilarity(q, it.vector) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, Math.max(1, Math.min(50, topK)))
}
