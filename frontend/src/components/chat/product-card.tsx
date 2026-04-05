'use client'

import { useEffect, useState } from 'react'
import type { ChatRecommendation, Paddle } from '@/types/paddle'
import { fetchPaddle } from '@/lib/api'
import { SafeImage } from '@/components/ui/safe-image'

interface ProductCardProps extends ChatRecommendation {
  in_stock?: boolean
  stock_level?: 'available' | 'low' | 'unavailable'
  reason?: string
}

function formatPrice(price: number): string {
  return price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function StockIndicator({ level }: { level: 'available' | 'low' | 'unavailable' }) {
  const config = {
    available: { color: 'bg-green-500', label: 'Disponivel' },
    low: { color: 'bg-yellow-500', label: 'Poucas unidades' },
    unavailable: { color: 'bg-red-500', label: 'Indisponivel' },
  }
  const { color, label } = config[level]
  return (
    <span className="flex items-center gap-1 text-xs text-muted-foreground">
      <span className={`inline-block w-2 h-2 rounded-full ${color}`} />
      {label}
    </span>
  )
}

export function ProductCard({
  paddle_id,
  name,
  brand,
  price_min_brl,
  affiliate_url,
  similarity_score,
  in_stock,
  stock_level,
  reason,
}: ProductCardProps) {
  const [paddleDetails, setPaddleDetails] = useState<Paddle | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchPaddleDetails = async () => {
      try {
        const details = await fetchPaddle(paddle_id)
        setPaddleDetails(details)
      } catch (error) {
        console.error(`Failed to fetch paddle details for ID ${paddle_id}:`, error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchPaddleDetails()
  }, [paddle_id])

  const effectiveStockLevel: 'available' | 'low' | 'unavailable' =
    stock_level ?? (in_stock === false ? 'unavailable' : 'available')

  // Fallback reason per DESIGN.md
  const displayReason = reason || 'Recomendada para o seu perfil de jogo.'

  return (
    <article
      className="relative border rounded-lg p-4 bg-card shadow-sm flex flex-col gap-3 transition-transform hover:lift"
      data-testid={`product-card-${paddle_id}`}
      aria-labelledby={`product-title-${paddle_id}`}
    >
      {similarity_score > 0.8 && (
        <div 
          className="absolute top-2 right-2 bg-primary text-primary-foreground text-[10px] font-bold px-2 py-0.5 rounded-sm"
          data-testid="recommended-badge"
        >
          Recomendado
        </div>
      )}

      {isLoading ? (
        <div
          className="w-20 h-20 bg-muted rounded-lg flex items-center justify-center text-muted-foreground text-xs shrink-0 animate-pulse"
          role="img"
          aria-label={`Carregando imagem da raquete ${brand} ${name}`}
        >
          <div className="w-4 h-4 bg-muted-foreground/20 rounded" />
        </div>
      ) : (
        <SafeImage 
          src={paddleDetails?.image_url || null} 
          alt={`${brand} ${name}`}
          className="w-20 h-20 object-contain rounded-lg shrink-0"
          fallbackClassName="w-20 h-20 bg-muted rounded-lg flex items-center justify-center text-muted-foreground text-xs shrink-0"
        />
      )}

      <div className="flex-1 space-y-1">
        <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">{brand}</div>
        <h3 id={`product-title-${paddle_id}`} className="font-semibold text-base leading-tight">{name}</h3>
        <div className="text-lg font-bold">{formatPrice(price_min_brl)}</div>
      </div>

      {/* "Por que essa raquete?" section per DESIGN.md */}
      <div className="space-y-1">
        <div className="text-xs font-medium text-muted-foreground">Por que essa raquete?</div>
        <div className="text-sm text-foreground">{displayReason}</div>
      </div>

      <StockIndicator level={effectiveStockLevel} />

      <a
        href={affiliate_url}
        target="_blank"
        rel="noopener noreferrer"
        className="block w-full text-center bg-primary text-primary-foreground rounded-lg py-2 text-sm font-semibold hover:bg-primary/90 transition-colors"
        aria-label={`Ver ${name} no site`}
      >
        VER NO SITE →
      </a>
    </article>
  )
}