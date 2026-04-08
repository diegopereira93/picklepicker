import { Metadata } from 'next'
import { Paddle } from '@/types/paddle'

const FASTAPI_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000'
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://pickleiq.com'

export async function fetchProductData(brand: string, modelSlug: string): Promise<Paddle | null> {
  try {
    const res = await fetch(
      `${FASTAPI_URL}/api/v1/paddles?brand=${encodeURIComponent(brand)}&model_slug=${encodeURIComponent(modelSlug)}`
    )
    if (!res.ok) return null
    const data = await res.json()
    const items = data.data ?? data.paddles ?? data.items ?? []
    const requestedSlug = modelSlug.toLowerCase()
    const matches = items.filter(
      (item: Record<string, unknown>) =>
        item.model_slug?.toLowerCase() === requestedSlug ||
        item.name?.toString().toLowerCase().replace(/\s+/g, '-') === requestedSlug
    )
    // Prefer paddle with a real image when duplicates exist
    const paddle = matches.find((item: Record<string, unknown>) => item.image_url) ?? matches[0] ?? null

    if (!paddle && /^\d+$/.test(modelSlug)) {
      const idRes = await fetch(`${FASTAPI_URL}/api/v1/paddles/${modelSlug}`)
      if (idRes.ok) {
        const idData = await idRes.json()
        return idData.data ?? idData ?? null
      }
    }

    return paddle
  } catch (error) {
    console.error('[fetchProductData] Fetch failed (backend unavailable):', error)
    return null
  }
}

export async function fetchPaddlesList(params: {
  page?: number
  per_page?: number
}): Promise<{ paddles: Paddle[]; total: number }> {
  const { page = 1, per_page = 50 } = params
  const url = `${FASTAPI_URL}/api/v1/paddles?page=${page}&per_page=${per_page}`
  console.log('[fetchPaddlesList] Fetching:', url)
  try {
    const res = await fetch(url)
    console.log('[fetchPaddlesList] Response status:', res.status)
    if (!res.ok) {
      console.error('[fetchPaddlesList] Response not OK:', res.status, res.statusText)
      return { paddles: [], total: 0 }
    }
    const data = await res.json()
    console.log('[fetchPaddlesList] Response data keys:', Object.keys(data))
    // Support both {items, total} (existing backend schema) and {paddles, total}
    const paddles = data.paddles ?? data.items ?? data.data ?? []
    console.log('[fetchPaddlesList] Extracted paddles count:', paddles.length)
    return { paddles, total: data.total ?? paddles.length }
  } catch (error) {
    console.error('[fetchPaddlesList] Fetch failed (backend unavailable):', error)
    return { paddles: [], total: 0 }
  }
}

export async function generateProductMetadata(
  brand: string,
  modelSlug: string,
  paddle: Paddle
): Promise<Metadata> {
  const canonicalUrl = `${SITE_URL}/catalog/${modelSlug}`
  const title = `${paddle.name} - PickleIQ`
  const pricePart =
    paddle.price_brl != null
      ? `R$ ${paddle.price_brl.toFixed(2)}. `
      : paddle.price_min_brl != null
      ? `R$ ${paddle.price_min_brl.toFixed(2)}. `
      : ''
  const swPart =
    paddle.specs?.swingweight != null
      ? `${paddle.specs.swingweight} sw. `
      : ''
  const description = `${paddle.brand} ${paddle.name}: ${swPart}${pricePart}${paddle.description ?? ''}`

  return {
    title,
    description,
    robots: 'index, follow',
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: {
      type: 'website',
      url: canonicalUrl,
      title,
      description: `Análise detalhada: ${paddle.name}`,
      images: paddle.image_url
        ? [
            {
              url: paddle.image_url,
              width: 1200,
              height: 630,
              alt: paddle.name,
            },
          ]
        : [],
    },
  } as Metadata & { robots: string }
}
