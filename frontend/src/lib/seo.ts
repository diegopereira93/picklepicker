import { Metadata } from 'next'
import { Paddle } from '@/types/paddle'

const FASTAPI_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000'
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://pickleiq.com'

export async function fetchProductData(brand: string, modelSlug: string): Promise<Paddle | null> {
  const res = await fetch(
    `${FASTAPI_URL}/api/v1/paddles?brand=${encodeURIComponent(brand)}&model_slug=${encodeURIComponent(modelSlug)}`
  )
  if (!res.ok) return null
  const data = await res.json()
  const paddle = data.data?.[0] ?? data.paddles?.[0] ?? null

  if (!paddle && /^\d+$/.test(modelSlug)) {
    const idRes = await fetch(`${FASTAPI_URL}/api/v1/paddles/${modelSlug}`)
    if (idRes.ok) {
      const idData = await idRes.json()
      return idData.data ?? idData ?? null
    }
  }

  return paddle
}

export async function fetchPaddlesList(params: {
  page?: number
  per_page?: number
}): Promise<{ paddles: Paddle[]; total: number }> {
  const { page = 1, per_page = 50 } = params
  const res = await fetch(
    `${FASTAPI_URL}/paddles?page=${page}&per_page=${per_page}`
  )
  if (!res.ok) return { paddles: [], total: 0 }
  const data = await res.json()
  // Support both {items, total} (existing backend schema) and {paddles, total}
  const paddles = data.paddles ?? data.items ?? []
  return { paddles, total: data.total ?? paddles.length }
}

export async function generateProductMetadata(
  brand: string,
  modelSlug: string,
  paddle: Paddle
): Promise<Metadata> {
  const canonicalUrl = `${SITE_URL}/paddles/${brand}/${modelSlug}`
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
