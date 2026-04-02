'use client'

import type { ChatRecommendation } from '@/types/paddle'

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
  const effectiveStockLevel: 'available' | 'low' | 'unavailable' =
    stock_level ?? (in_stock === false ? 'unavailable' : 'available')

  // Fallback reason per DESIGN.md
  const displayReason = reason || 'Recomendada para o seu perfil de jogo.'

  return (
    <article
      className="border rounded-xl p-4 bg-card shadow-sm flex flex-col gap-3 transition-transform hover:lift"
      data-testid={`product-card-${paddle_id}`}
      aria-labelledby={`product-title-${paddle_id}`}
    >
      {/* Image placeholder - 80x80 per DESIGN.md */}
      <div
        className="w-20 h-20 bg-muted rounded-lg flex items-center justify-center text-muted-foreground text-xs shrink-0"
        role="img"
        aria-label={`Imagem da raquete ${brand} ${name}`}
      >
        Foto
      </div>

      <div className="flex-1 space-y-1">
        <h3 id={`product-title-${paddle_id}`} className="font-semibold text-base leading-tight">{brand} {name}</h3>
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