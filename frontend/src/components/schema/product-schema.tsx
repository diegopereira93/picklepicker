import { Paddle } from '@/types/paddle'

interface ProductSchemaProps {
  paddle: Paddle & {
    price_brl?: number
    rating?: number
    review_count?: number
    in_stock?: boolean
    description?: string
  }
  url: string
}

export function ProductSchema({ paddle, url }: ProductSchemaProps) {
  const price =
    paddle.price_brl != null
      ? paddle.price_brl.toString()
      : paddle.price_min_brl != null
      ? paddle.price_min_brl.toString()
      : '0'

  const schema: Record<string, unknown> = {
    '@context': 'https://schema.org/',
    '@type': 'Product',
    name: paddle.name,
    brand: { '@type': 'Brand', name: paddle.brand },
    description: paddle.description ?? '',
    image: paddle.image_url ?? '',
    offers: {
      '@type': 'AggregateOffer',
      priceCurrency: 'BRL',
      price,
      availability:
        paddle.in_stock === false
          ? 'https://schema.org/OutOfStock'
          : 'https://schema.org/InStock',
    },
    url,
  }

  if (paddle.rating != null && paddle.review_count != null) {
    schema.aggregateRating = {
      '@type': 'AggregateRating',
      ratingValue: paddle.rating.toString(),
      reviewCount: paddle.review_count.toString(),
    }
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  )
}
