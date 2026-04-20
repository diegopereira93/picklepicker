'use client'

import { useEffect, useState } from 'react'
import { ExternalLink } from 'lucide-react'
import { MatchScoreBadge } from '@/components/ui/match-score-badge'
import { PriceTag } from '@/components/ui/price-tag'
import { SafeImage } from '@/components/ui/safe-image'
import { fetchPaddle } from '@/lib/api'
import type { ChatRecommendation, Paddle } from '@/types/paddle'
import { cn } from '@/lib/utils'

interface InlinePaddleCardProps extends ChatRecommendation {
  compact?: boolean
}

export function InlinePaddleCard({
  paddle_id,
  name,
  brand,
  price_min_brl,
  affiliate_url,
  similarity_score,
  compact = false,
}: InlinePaddleCardProps) {
  const [details, setDetails] = useState<Paddle | null>(null)
  const matchPct = Math.round(similarity_score * 100)

  useEffect(() => {
    let cancelled = false
    fetchPaddle(paddle_id)
      .then((p) => { if (!cancelled) setDetails(p) })
      .catch(() => {})
    return () => { cancelled = true }
  }, [paddle_id])

  return (
    <article
      data-testid={`inline-paddle-${paddle_id}`}
      className={cn(
        'group relative flex gap-3 bg-surface rounded-rounded',
        'shadow-md transition-all duration-200',
        'hover:-translate-y-0.5 hover:shadow-glow-green',
        compact ? 'p-2 gap-2' : 'p-3'
      )}
    >
      <div className={cn(
        'shrink-0 bg-elevated rounded-sharp overflow-hidden relative',
        compact ? 'w-14 h-14' : 'w-20 h-20'
      )}>
        <SafeImage
          src={details?.image_url ?? null}
          alt={`${brand} ${name}`}
          className="w-full h-full object-contain"
        />
        <div className="absolute -top-1 -left-1">
          <MatchScoreBadge score={matchPct} size="sm" showLabel={false} />
        </div>
      </div>

      <div className="flex-1 min-w-0 flex flex-col gap-1">
        <p className="text-[10px] font-bold uppercase tracking-wider text-text-muted">{brand}</p>
        <h4 className={cn(
          'font-display tracking-wide text-text-primary truncate',
          compact ? 'text-sm' : 'text-base'
        )}>
          {name}
        </h4>
        <PriceTag price={price_min_brl} size="sm" />
        {!compact && (
          <a
            href={affiliate_url}
            target="_blank"
            rel="noopener noreferrer nofollow sponsored"
            onClick={(e) => e.stopPropagation()}
            className="mt-1 inline-flex items-center gap-1 self-start text-xs font-semibold text-brand-primary hover:text-brand-primary/80 transition-colors"
          >
            Ver ofertas <ExternalLink size={12} />
          </a>
        )}
      </div>
    </article>
  )
}
