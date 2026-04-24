import type { Paddle, PaddleListResponse, LatestPriceResponse } from '@/types/paddle'

function getApiBase(): string {
  // Server-side (SSR) inside Docker container: use internal Docker service name
  // Client-side (browser): use localhost which reaches host via Docker port mapping
  const baseUrl = typeof window === 'undefined'
    ? process.env.FASTAPI_INTERNAL_URL || process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000'
    : process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000'
  return baseUrl + '/api/v1'
}
const API_BASE = getApiBase()

const EMPTY_LIST: PaddleListResponse = { items: [], total: 0, limit: 20, offset: 0 }

function buildUrl(path: string, params?: Record<string, string | number | boolean | undefined>): string {
  const url = new URL(`${API_BASE}${path}`)
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) {
        url.searchParams.set(key, String(value))
      }
    }
  }
  return url.toString()
}

export async function fetchPaddles(params?: {
  brand?: string
  skill_level?: string
  price_min?: number
  price_max?: number
  in_stock?: boolean
  limit?: number
  offset?: number
}): Promise<PaddleListResponse> {
  try {
    const url = buildUrl('/paddles', params as Record<string, string | number | boolean | undefined>)
    const res = await fetch(url)
    if (!res.ok) return EMPTY_LIST
    return (await res.json()) as PaddleListResponse
  } catch (err) {
    console.error('[fetchPaddles] failed:', err)
    return EMPTY_LIST
  }
}

export async function fetchPaddle(id: number): Promise<Paddle | null> {
  try {
    const res = await fetch(buildUrl(`/paddles/${id}`))
    if (!res.ok) return null
    return (await res.json()) as Paddle
  } catch (err) {
    console.error('[fetchPaddle] failed:', err)
    return null
  }
}

export async function fetchLatestPrices(paddleId: number): Promise<LatestPriceResponse | null> {
  try {
    const res = await fetch(buildUrl(`/paddles/${paddleId}/prices`))
    if (!res.ok) return null
    return (await res.json()) as LatestPriceResponse
  } catch (err) {
    console.error('[fetchLatestPrices] failed:', err)
    return null
  }
}

export async function searchPaddles(query: string, limit = 10): Promise<Paddle[]> {
  try {
    const url = buildUrl('/paddles', { brand: query, limit })
    const res = await fetch(url)
    if (!res.ok) return []
    const data = (await res.json()) as PaddleListResponse
    return data.items
  } catch (err) {
    console.error('[searchPaddles] failed:', err)
    return []
  }
}
