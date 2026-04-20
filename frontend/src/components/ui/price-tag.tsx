'use client'

import { cn } from '@/lib/utils'
import { Clock } from 'lucide-react'

interface PriceTagProps {
  price: number
  previousPrice?: number
  currency?: string
  size?: 'sm' | 'md' | 'lg'
  scrapedAt?: string
  className?: string
}

function formatFreshness(isoDate: string): { text: string; isStale: boolean } {
  const now = Date.now()
  const then = new Date(isoDate).getTime()
  const diffMs = now - then
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))

  if (diffHours < 1) return { text: 'agora', isStale: false }
  if (diffHours < 24) return { text: `${diffHours}h`, isStale: diffHours > 48 }
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 30) return { text: `${diffDays}d`, isStale: true }
  return { text: '+30d', isStale: true }
}

function PriceTag({ price, previousPrice, currency = 'BRL', size = 'md', scrapedAt, className }: PriceTagProps) {
  const hasDiscount = previousPrice && previousPrice > price
  const freshness = scrapedAt ? formatFreshness(scrapedAt) : null

  const sizeClasses = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-4xl',
  }

  const formatPrice = (value: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency, minimumFractionDigits: 2 }).format(value)

  return (
    <div className={cn('flex flex-col gap-0.5', className)}>
      <div className="flex items-baseline gap-2">
        <span
          className={cn(
            'font-mono font-bold text-text-primary',
            sizeClasses[size],
            hasDiscount && 'text-price-down'
          )}
        >
          {formatPrice(price)}
        </span>
        {previousPrice && previousPrice !== price && (
          <span className="font-mono text-sm text-text-muted line-through">
            {formatPrice(previousPrice)}
          </span>
        )}
      </div>
      {freshness && (
        <span
          className={cn(
            'inline-flex items-center gap-1 text-xs font-sans',
            freshness.isStale ? 'text-amber-500' : 'text-text-muted'
          )}
        >
          {freshness.isStale && <Clock className="w-3 h-3" />}
          atualizado há {freshness.text}
        </span>
      )}
    </div>
  )
}

function PriceTagSkeleton({ size = 'md', className }: { size?: 'sm' | 'md' | 'lg'; className?: string }) {
  const sizeClasses = { sm: 'w-20 h-6', md: 'w-28 h-8', lg: 'w-40 h-10' }

  return (
    <div className={cn('flex items-baseline gap-2', className)}>
      <Skeleton className={cn('rounded-sharp', sizeClasses[size])} />
    </div>
  )
}

export { PriceTag, PriceTagSkeleton }
export type { PriceTagProps }
