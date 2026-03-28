'use client'

/**
 * AffiliateLink — reusable anchor component with click tracking + UTM preservation.
 * FtcDisclosure — FTC-required disclosure banner for affiliate pages.
 */

import React from 'react'
import { trackAffiliateClick, appendUtmParams, extractRetailer } from '@/lib/tracking'

// ─── AffiliateLink ────────────────────────────────────────────────────────────

interface AffiliateLinkProps {
  href: string
  paddle_id: number
  retailer?: string
  children: React.ReactNode
  className?: string
}

export function AffiliateLink({
  href,
  paddle_id,
  retailer,
  children,
  className,
}: AffiliateLinkProps) {
  const resolvedRetailer = retailer ?? extractRetailer(href)

  function handleClick() {
    trackAffiliateClick({
      paddle_id,
      retailer: resolvedRetailer,
      affiliate_url: href,
    })
  }

  return (
    <a
      href={appendUtmParams(href)}
      target="_blank"
      rel="noopener noreferrer"
      onClick={handleClick}
      className={className}
    >
      {children}
    </a>
  )
}

// ─── FtcDisclosure ────────────────────────────────────────────────────────────

export function FtcDisclosure() {
  return (
    <p className="text-xs text-muted-foreground flex items-center gap-1 my-2">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-3 w-3 shrink-0"
        viewBox="0 0 20 20"
        fill="currentColor"
        aria-hidden="true"
      >
        <path
          fillRule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
          clipRule="evenodd"
        />
      </svg>
      PickleIQ pode receber comissoes por compras realizadas atraves de links de afiliados nesta pagina.
    </p>
  )
}
