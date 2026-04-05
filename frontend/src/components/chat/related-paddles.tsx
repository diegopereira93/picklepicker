'use client'

import type { Paddle } from '@/types/paddle'
import { SafeImage } from '@/components/ui/safe-image'

interface RelatedPaddlesProps {
  paddles: Paddle[]
  onSelect: (paddle: Paddle) => void
}

function formatPrice(price: number | undefined): string {
  if (price === undefined) return '—'
  return price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function RelatedPaddles({ paddles, onSelect }: RelatedPaddlesProps) {
  if (paddles.length === 0) return null

  return (
    <div className="grid grid-cols-2 lg:grid-cols-2 gap-3">
      {paddles.map((paddle) => {
        const brand = paddle.brand || 'Unknown'
        const name = paddle.name || 'Sem nome'
        const price = formatPrice(paddle.price_min_brl)
        const imageUrl = paddle.image_url

        return (
          <button
            key={paddle.id}
            type="button"
            onClick={() => onSelect(paddle)}
            className="text-left p-3 rounded-sm border transition-all hover:border-[var(--sport-primary)] hover:shadow-sm"
            style={{
              background: 'var(--color-white)',
              borderColor: 'var(--color-gray-border)',
            }}
            aria-label={`Selecionar raquete ${brand} ${name}`}
          >
            <div className="relative mb-2 overflow-hidden rounded-sm" style={{ height: '80px' }}>
              <SafeImage
                src={imageUrl}
                alt={`${brand} ${name}`}
                className="object-cover w-full h-full"
                style={{ borderRadius: 'var(--radius-sharp)' }}
              />
            </div>

            <div
              className="text-[10px] font-bold uppercase tracking-wider"
              style={{ color: 'var(--color-gray-500)' }}
            >
              {brand}
            </div>

            <h4
              className="text-sm font-semibold truncate"
              style={{ color: 'var(--color-black)' }}
            >
              {name}
            </h4>

            <div
              className="text-sm font-bold mt-1"
              style={{
                fontFamily: 'var(--font-data)',
                color: 'var(--data-green)',
              }}
            >
              {price}
            </div>
          </button>
        )
      })}
    </div>
  )
}
