'use client'

import { ExternalLink } from 'lucide-react'
import { resolveAffiliateUrl, trackAffiliateClick } from '@/lib/affiliate'

interface AffiliateCTAProps {
  affiliateUrl?: string
  paddleId: string
  store?: string
  page?: string
  price?: number
  label?: string
  urgency?: string
  className?: string
  size?: 'default' | 'lg' | 'sm'
}

export function AffiliateCTA({
  affiliateUrl,
  paddleId,
  store,
  page = 'unknown',
  price,
  label = 'Comprar Agora',
  urgency,
  className,
  size = 'default',
}: AffiliateCTAProps) {
  const url = affiliateUrl || resolveAffiliateUrl({
    paddleId,
    store,
    page,
  })

  const handleClick = () => {
    trackAffiliateClick(paddleId, store || 'brazil-store', page)
  }

  return (
    <div className={className}>
      {urgency && (
        <p className="font-sans text-xs text-brand-secondary mb-2 font-medium">
          {urgency}
        </p>
      )}
      {price != null && (
        <p className="font-mono text-sm text-text-muted mb-2">
          a partir de R$ {price.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
        </p>
      )}
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer sponsored"
        onClick={handleClick}
        className={`
          inline-flex items-center justify-center rounded-lg font-medium
          ${size === 'lg' ? 'h-9 px-2.5 gap-1.5 py-6 text-lg font-semibold' : 'h-8 px-2.5 gap-1.5'}
          w-full bg-brand-primary hover:bg-brand-primary/90 text-base
          hover:shadow-glow-green transition-all
          flex items-center justify-center gap-2
        `}
      >
        {label}
        <ExternalLink size={size === 'lg' ? 18 : 16} />
      </a>
    </div>
  )
}
