/**
 * Affiliate click tracking utility
 * - trackAffiliateClick: fire-and-forget keepalive fetch to /api/track
 * - appendUtmParams: preserve page UTM params onto affiliate URLs
 * - extractRetailer: extract retailer name from affiliate URL domain
 */

const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'] as const

/** Get or create a persistent anonymous user ID stored in localStorage */
export function getOrCreateUserId(): string {
  if (typeof window === 'undefined') return ''
  try {
    const existing = localStorage.getItem('pickleiq_user_id')
    if (existing) return existing
    const id = crypto.randomUUID()
    localStorage.setItem('pickleiq_user_id', id)
    return id
  } catch {
    return ''
  }
}

/** Extract retailer name from an affiliate URL domain */
export function extractRetailer(url: string): string {
  try {
    const hostname = new URL(url).hostname // e.g. "www.mercadolivre.com.br"
    const parts = hostname.replace(/^www\./, '').split('.')
    // Return first meaningful segment (e.g. "mercadolivre", "amazon", "shopee")
    return parts[0] ?? 'unknown'
  } catch {
    return 'unknown'
  }
}

/**
 * Append UTM params from the current page URL onto an affiliate URL.
 * Skips params that are already present on the affiliate URL.
 */
export function appendUtmParams(affiliateUrl: string): string {
  if (typeof window === 'undefined') return affiliateUrl
  try {
    const pageParams = new URLSearchParams(window.location.search)
    const url = new URL(affiliateUrl)
    for (const key of UTM_KEYS) {
      const pageValue = pageParams.get(key)
      if (pageValue && !url.searchParams.has(key)) {
        url.searchParams.set(key, pageValue)
      }
    }
    return url.toString()
  } catch {
    return affiliateUrl
  }
}

/**
 * Fire-and-forget affiliate click tracking via keepalive fetch.
 * Never throws — errors are console.warn only so navigation is never blocked.
 */
export function trackAffiliateClick(params: {
  paddle_id: number
  retailer: string
  affiliate_url: string
}): void {
  try {
    const pageParams = new URLSearchParams(
      typeof window !== 'undefined' ? window.location.search : ''
    )
    const utmData: Record<string, string> = {}
    for (const key of UTM_KEYS) {
      const val = pageParams.get(key)
      if (val) utmData[key] = val
    }

    const payload = {
      paddle_id: params.paddle_id,
      retailer: params.retailer,
      affiliate_url: params.affiliate_url,
      user_id: getOrCreateUserId(),
      timestamp: new Date().toISOString(),
      page_url: typeof window !== 'undefined' ? window.location.href : '',
      ...utmData,
    }

    fetch('/api/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true,
    }).catch((err) => {
      console.warn('[PickleIQ] Affiliate tracking failed:', err)
    })
  } catch (err) {
    console.warn('[PickleIQ] Affiliate tracking error:', err)
  }
}
