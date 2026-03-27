/**
 * Affiliate tracking tests
 * TDD: behavior-driven tests for tracking utility, Edge Handler, and AffiliateLink component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'

// ─── Mocks ───────────────────────────────────────────────────────────────────

const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
  }
})()
Object.defineProperty(global, 'localStorage', { value: localStorageMock })

// ─── trackAffiliateClick ─────────────────────────────────────────────────────

describe('trackAffiliateClick', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
    mockFetch.mockResolvedValue({ ok: true, status: 204 })
    // Set a page URL with UTM params
    Object.defineProperty(window, 'location', {
      value: { search: '?utm_source=google&utm_medium=cpc&utm_campaign=summer' },
      writable: true,
    })
  })

  it('Test 1: fires fetch with keepalive:true to /api/track', async () => {
    const { trackAffiliateClick } = await import('@/lib/tracking')
    trackAffiliateClick({ paddle_id: 42, retailer: 'mercadolivre', affiliate_url: 'https://mercadolivre.com.br/paddle/42' })
    expect(mockFetch).toHaveBeenCalledOnce()
    const [url, options] = mockFetch.mock.calls[0]
    expect(url).toBe('/api/track')
    expect(options.keepalive).toBe(true)
    expect(options.method).toBe('POST')
  })

  it('Test 2: sends paddle_id, retailer, timestamp, utm_params, user_id', async () => {
    const { trackAffiliateClick } = await import('@/lib/tracking')
    trackAffiliateClick({ paddle_id: 42, retailer: 'mercadolivre', affiliate_url: 'https://mercadolivre.com.br/paddle/42' })
    const [, options] = mockFetch.mock.calls[0]
    const body = JSON.parse(options.body)
    expect(body.paddle_id).toBe(42)
    expect(body.retailer).toBe('mercadolivre')
    expect(typeof body.timestamp).toBe('string')
    expect(body.utm_source).toBe('google')
    expect(body.utm_medium).toBe('cpc')
    expect(body.utm_campaign).toBe('summer')
    expect(typeof body.user_id).toBe('string')
    expect(body.user_id.length).toBeGreaterThan(0)
  })
})

// ─── appendUtmParams ──────────────────────────────────────────────────────────

describe('appendUtmParams', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'location', {
      value: { search: '?utm_source=facebook&utm_medium=social' },
      writable: true,
    })
  })

  it('Test 3: preserves UTM params from current page URL onto affiliate URL', async () => {
    const { appendUtmParams } = await import('@/lib/tracking')
    const result = appendUtmParams('https://amazon.com.br/product/123')
    const url = new URL(result)
    expect(url.searchParams.get('utm_source')).toBe('facebook')
    expect(url.searchParams.get('utm_medium')).toBe('social')
  })

  it('Test 4: does not duplicate UTM params already on affiliate URL', async () => {
    const { appendUtmParams } = await import('@/lib/tracking')
    const result = appendUtmParams('https://amazon.com.br/product/123?utm_source=existing')
    const url = new URL(result)
    // utm_source from affiliate URL wins (already present, not overwritten)
    const allValues = url.searchParams.getAll('utm_source')
    expect(allValues.length).toBe(1)
    expect(allValues[0]).toBe('existing')
  })
})

// ─── Edge Route Handler ───────────────────────────────────────────────────────

describe('POST /api/track Edge Route Handler', () => {
  it('Test 5: returns 204 on valid payload', async () => {
    const { POST } = await import('@/app/api/track/route')
    const req = new Request('http://localhost/api/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        paddle_id: 42,
        retailer: 'mercadolivre',
        timestamp: new Date().toISOString(),
        page_url: 'https://pickleiq.com',
      }),
    })
    const res = await POST(req)
    expect(res.status).toBe(204)
  })

  it('Test 6: returns 400 on missing paddle_id', async () => {
    const { POST } = await import('@/app/api/track/route')
    const req = new Request('http://localhost/api/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ retailer: 'mercadolivre', timestamp: new Date().toISOString() }),
    })
    const res = await POST(req)
    expect(res.status).toBe(400)
  })
})

// ─── AffiliateLink component ──────────────────────────────────────────────────

describe('AffiliateLink component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
    mockFetch.mockResolvedValue({ ok: true, status: 204 })
    Object.defineProperty(window, 'location', {
      value: { search: '' },
      writable: true,
    })
  })

  it('Test 7: renders as anchor with target="_blank" rel="noopener noreferrer"', async () => {
    const { AffiliateLink } = await import('@/components/shared/affiliate-link')
    render(
      React.createElement(AffiliateLink, {
        href: 'https://mercadolivre.com.br/paddle/42',
        paddle_id: 42,
        retailer: 'mercadolivre',
      }, 'Comprar agora')
    )
    const link = screen.getByRole('link', { name: /comprar agora/i })
    expect(link.tagName).toBe('A')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('Test 8: onClick calls trackAffiliateClick before navigation', async () => {
    const { AffiliateLink } = await import('@/components/shared/affiliate-link')
    render(
      React.createElement(AffiliateLink, {
        href: 'https://mercadolivre.com.br/paddle/42',
        paddle_id: 42,
        retailer: 'mercadolivre',
      }, 'Comprar agora')
    )
    const link = screen.getByRole('link', { name: /comprar agora/i })
    fireEvent.click(link)
    expect(mockFetch).toHaveBeenCalledOnce()
    const [url] = mockFetch.mock.calls[0]
    expect(url).toBe('/api/track')
  })
})

// ─── FtcDisclosure component ──────────────────────────────────────────────────

describe('FtcDisclosure component', () => {
  it('Test 9: renders FTC disclosure text', async () => {
    const { FtcDisclosure } = await import('@/components/shared/affiliate-link')
    render(React.createElement(FtcDisclosure))
    expect(screen.getByText(/comiss/i)).toBeInTheDocument()
    expect(screen.getByText(/afiliados/i)).toBeInTheDocument()
  })
})
