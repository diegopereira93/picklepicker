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
    <div className="mx-auto max-w-2xl mt-8 hy-animate-card-enter wg-recommendation-card">
      <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] gap-6 items-center">
        <div className="w-[120px] h-[180px] rounded-md overflow-hidden mx-auto md:mx-0 bg-gray-100">
          {paddle.image_url ? (
            <SafeImage
              src={paddle.image_url}
              alt={paddle.name}
              width={120}
              height={180}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-xs text-gray-400">
              Foto
            </div>
          )}
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {paddle.name}
          </h3>
          {paddle.brand && (
            <p className="text-xs font-bold uppercase tracking-wider mb-2 text-[var(--accent-coral)]">
              {paddle.brand}
            </p>
          )}
          <div className="text-2xl font-bold text-[var(--accent-coral)] mb-3" style={{ fontFamily: 'var(--font-data)' }}>
            R$ {paddle.price_min_brl?.toLocaleString('pt-BR') ?? '—'}
          </div>

          {paddle.specs && (
            <div className="flex flex-wrap gap-4 mb-3 text-xs text-gray-500">
              {paddle.specs.weight_oz && <span>• {paddle.specs.weight_oz}oz</span>}
              {paddle.specs.face_material && <span>• {paddle.specs.face_material}</span>}
              {paddle.specs.core_thickness_mm && <span>• {paddle.specs.core_thickness_mm}mm core</span>}
            </div>
          )}

          <p className="mb-4 text-sm text-gray-600">
            Recomendado baseado no seu perfil e orcamento.
          </p>

          <Link
            href={detailUrl}
            className="wg-button-coral inline-block text-sm"
          >
            Ver detalhes
          </Link>
        </div>
      </div>
    </div>
  )
}
