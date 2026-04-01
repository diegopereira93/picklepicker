'use client'

import type { ChatRecommendation } from '@/types/paddle'

interface ProductCardProps extends ChatRecommendation {
  in_stock?: boolean
  stock_level?: 'available' | 'low' | 'unavailable'
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
}: ProductCardProps) {
  const effectiveStockLevel: 'available' | 'low' | 'unavailable' =
    stock_level ?? (in_stock === false ? 'unavailable' : 'available')

  return (
    <article
      className="border rounded-xl p-4 bg-card shadow-sm flex flex-col gap-3 transition-transform hover:lift"
      data-testid={`product-card-${paddle_id}`}
      aria-labelledby={`product-title-${paddle_id}`}
    >
      {/* Placeholder image with proper accessibility */}
      <div
        className="w-full h-32 bg-muted rounded-lg flex items-center justify-center text-muted-foreground text-sm"
        role="img"
        aria-label={`Imagem da raquete ${brand} ${name}`}
      >
        Foto em breve
      </div>

      <div className="flex-1 space-y-1">
        <h3 id={`product-title-${paddle_id}`} className="font-semibold text-base leading-tight">{name}</h3>
        <div className="text-sm text-muted-foreground">{brand}</div>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-lg font-bold">{formatPrice(price_min_brl)}</span>
        {similarity_score > 0.8 && (
          <span className="text-xs bg-primary/10 text-primary rounded-full px-2 py-0.5 font-medium">
            Recomendado
          </span>
        )}
      </div>

      <StockIndicator level={effectiveStockLevel} />

      <a
        href={affiliate_url}
        target="_blank"
        rel="noopener noreferrer"
        className="block w-full text-center bg-primary text-primary-foreground rounded-lg py-2 text-sm font-semibold hover:bg-primary/90 transition-colors"
        aria-label={`Comprar ${name}`}
      >
        Comprar
      </a>
    </article>
  )
}
