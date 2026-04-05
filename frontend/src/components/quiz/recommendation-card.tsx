'use client'

import Link from 'next/link'
import type { Paddle } from '@/types/paddle'
import { SafeImage } from '@/components/ui/safe-image'

interface RecommendationCardProps {
  paddle: Paddle
}

export function RecommendationCard({ paddle }: RecommendationCardProps) {
  const detailUrl = paddle.model_slug && paddle.brand
    ? `/paddles/${encodeURIComponent(paddle.brand.toLowerCase())}/${encodeURIComponent(paddle.model_slug)}`
    : `/paddles`

  return (
    <div className="mx-auto max-w-2xl mt-8 hy-animate-card-enter"
         style={{
           backgroundColor: 'var(--color-near-black)',
           border: '2px solid var(--sport-primary)',
           borderRadius: 'var(--radius-sharp)',
           padding: 'var(--space-md)',
         }}>
      <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] gap-6 items-center">
        <div className="w-[120px] h-[180px] rounded-sm overflow-hidden mx-auto md:mx-0"
             style={{ backgroundColor: 'var(--color-gray-border)' }}>
          {paddle.image_url ? (
            <SafeImage
              src={paddle.image_url}
              alt={paddle.name}
              width={120}
              height={180}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-xs"
                 style={{ color: 'var(--color-gray-500)' }}>
              Foto
            </div>
          )}
        </div>

        <div>
          <h3 className="hy-card-title-text" style={{ fontSize: '1.5rem', border: 'none' }}>
            {paddle.name}
          </h3>
          {paddle.brand && (
            <p className="text-xs font-bold uppercase tracking-wider mb-2"
               style={{ color: 'var(--data-green)' }}>
              {paddle.brand}
            </p>
          )}
          <div className="hy-product-card-price" style={{ fontSize: '1.5rem', marginBottom: '12px' }}>
            R$ {paddle.price_min_brl?.toLocaleString('pt-BR') ?? '—'}
          </div>

          {paddle.specs && (
            <div className="flex flex-wrap gap-4 mb-3" style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-gray-300)' }}>
              {paddle.specs.weight_oz && <span>• {paddle.specs.weight_oz}oz</span>}
              {paddle.specs.face_material && <span>• {paddle.specs.face_material}</span>}
              {paddle.specs.core_thickness_mm && <span>• {paddle.specs.core_thickness_mm}mm core</span>}
            </div>
          )}

          <p className="mb-4" style={{ fontSize: '14px', color: 'var(--color-gray-300)' }}>
            Recomendado baseado no seu perfil e orcamento.
          </p>

          <Link
            href={detailUrl}
            className="hy-button hy-button-primary inline-block"
          >
            Ver detalhes
          </Link>
        </div>
      </div>
    </div>
  )
}
