import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Cosine similarity utilities for vectors
export function dot(a: number[], b: number[]): number {
  let s = 0
  const len = Math.min(a.length, b.length)
  for (let i = 0; i < len; i++) s += a[i] * b[i]
  return s
}

export function l2Norm(a: number[]): number {
  let s = 0
  for (let i = 0; i < a.length; i++) s += a[i] * a[i]
  return Math.sqrt(s)
}

export function cosineSimilarity(a: number[], b: number[]): number {
  const denom = l2Norm(a) * l2Norm(b)
  if (!denom) return 0
  return dot(a, b) / denom
}

export function normalizeVector(a: number[]): number[] {
  const n = l2Norm(a)
  if (!n) return a.slice()
  return a.map((v) => v / n)
}
