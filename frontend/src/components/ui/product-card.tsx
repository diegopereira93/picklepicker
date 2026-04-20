'use client'

import { cn } from '@/lib/utils'
import { GitCompare, Bell, Store } from 'lucide-react'
import type { Paddle } from '@/types/paddle'
import { PriceTag } from './price-tag'
import { PriceDeltaBadge } from './price-delta-badge'
import { MatchScoreBadge } from './match-score-badge'
import { SafeImage } from './safe-image'
import { Button } from './button'
import { Skeleton } from './skeleton'

interface ProductCardProps {
  paddle: Paddle
  mode?: 'catalog' | 'chat' | 'compact'
  matchScore?: number
  priceDelta?: number
  isPricePulsing?: boolean
  onCompare?: () => void
  onAlert?: () => void
  onViewDetails?: () => void
  className?: string
}

function ProductCard({
  paddle,
  mode = 'catalog',
  matchScore,
  priceDelta,
  isPricePulsing = false,
  onCompare,
  onAlert,
  onViewDetails,
  className,
}: ProductCardProps) {
  const price = paddle.price_brl ?? paddle.price_min_brl ?? 0
  const name = paddle.name
  const brand = paddle.brand
  const imageUrl = paddle.image_url

  if (mode === 'chat') {
    return (
      <div
        className={cn(
          'group relative flex gap-3 overflow-hidden rounded-rounded bg-surface p-3',
          'shadow-md transition-all duration-200',
          'hover:-translate-y-0.5 hover:shadow-glow-green cursor-pointer',
          className
        )}
        onClick={onViewDetails}
        role="article"
      >
        <div className="relative shrink-0 w-20 h-20 bg-elevated rounded-sharp overflow-hidden">
          <SafeImage src={imageUrl} alt={`${brand} ${name}`} className="w-full h-full object-contain" />
          {matchScore !== undefined && (
            <div className="absolute -top-1 -left-1">
              <MatchScoreBadge score={matchScore} size="sm" showLabel={false} />
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0 flex flex-col gap-1">
          <p className="text-[10px] font-bold uppercase tracking-wider text-text-muted">{brand}</p>
          <h3 className="font-display text-base text-text-primary truncate">{name}</h3>
          <PriceTag price={price} size="sm" scrapedAt={paddle.latest_scraped_at} />
        </div>
      </div>
    )
  }

  if (mode === 'compact') {
    return (
      <div className={cn('flex gap-3 rounded-rounded bg-surface p-3', className)}>
        <SafeImage
          src={imageUrl}
          alt={name}
          width={80}
          height={80}
          className="h-16 w-16 shrink-0 rounded-sharp object-cover"
        />
        <div className="flex flex-col justify-between min-w-0">
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wider">{brand}</p>
            <p className="font-display text-sm text-text-primary truncate">{name}</p>
          </div>
          <span className="font-mono text-sm font-bold text-brand-primary">
            R$ {price.toFixed(2)}
          </span>
        </div>
      </div>
    )
  }

  return (
    <div
      className={cn(
        'group/card flex flex-col overflow-hidden rounded-rounded bg-surface shadow-md transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer',
        className
      )}
      onClick={onViewDetails}
      role="article"
    >
      <div className="relative aspect-[4/3] bg-elevated overflow-hidden">
        <SafeImage
          src={imageUrl}
          alt={`${brand} ${name}`}
          className="w-full h-full object-cover transition-transform duration-300 group-hover/card:scale-105"
        />
        {priceDelta !== undefined && priceDelta !== 0 && (
          <div className="absolute top-2 right-2">
            <PriceDeltaBadge delta={priceDelta} pulsing={isPricePulsing} />
          </div>
        )}
        {matchScore !== undefined && (
          <div className="absolute top-2 left-2">
            <MatchScoreBadge score={matchScore} size="sm" showLabel={false} />
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-2 p-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-text-muted">{brand}</p>
          <h3 className="font-display text-lg text-text-primary truncate">{name}</h3>
        </div>

        <PriceTag price={price} size="sm" scrapedAt={paddle.latest_scraped_at} />

        {paddle.retailer_count && paddle.retailer_count > 1 && (
          <span className="inline-flex items-center gap-1 text-xs font-sans text-[#76b900]">
            <Store className="w-3 h-3" />
            {paddle.retailer_count} varejistas
          </span>
        )}

        {paddle.specs && (
          <div className="flex gap-3">
            {paddle.specs.weight_oz && (
              <span className="text-xs font-mono text-text-secondary">
                {paddle.specs.weight_oz}oz
              </span>
            )}
            {paddle.skill_level && (
              <span className="text-xs text-text-secondary capitalize">{paddle.skill_level}</span>
            )}
          </div>
        )}

        {mode === 'catalog' && (
          <div className="flex gap-2 pt-2 border-t border-border mt-auto">
            <Button
              variant="outline"
              size="sm"
              className="flex-1 gap-1"
              onClick={(e) => { e.stopPropagation(); onViewDetails?.() }}
            >
              Details
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="gap-1"
              onClick={(e) => { e.stopPropagation(); onCompare?.() }}
            >
              <GitCompare className="w-4 h-4" />
              Compare
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="gap-1"
              onClick={(e) => { e.stopPropagation(); onAlert?.() }}
            >
              <Bell className="w-4 h-4" />
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}

function ProductCardSkeleton() {
  return (
    <div className="flex flex-col overflow-hidden rounded-rounded bg-surface shadow-md">
      <Skeleton className="aspect-[4/3]" />
      <div className="flex flex-col gap-3 p-4">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-6 w-24" />
        <div className="flex gap-2 pt-2 border-t border-border mt-auto">
          <Skeleton className="h-8 flex-1" />
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-8 w-8" />
        </div>
      </div>
    </div>
  )
}

export { ProductCard, ProductCardSkeleton }
