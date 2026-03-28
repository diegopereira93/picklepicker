import { describe, it, expect, vi, beforeEach } from 'vitest'
import { percentile20, isGoodTimeToBuy, getPriceHistory } from '@/lib/price-history'

// ---------------------------------------------------------------------------
// percentile20()
// ---------------------------------------------------------------------------

describe('percentile20', () => {
  it('returns the 20th percentile of a sorted array', () => {
    // [100, 200, 300, 400, 500] → idx = floor(5 * 0.2) = 1 → 200
    expect(percentile20([100, 200, 300, 400, 500])).toBe(200)
  })

  it('handles unsorted input by sorting first', () => {
    // same values, different order → same result
    expect(percentile20([500, 100, 300, 200, 400])).toBe(200)
  })

  it('returns the only element for a single-item array', () => {
    expect(percentile20([350])).toBe(350)
  })

  it('handles two-element array: idx=0 so returns first (lower) value', () => {
    // floor(2 * 0.2) = 0 → sorted[0]
    expect(percentile20([600, 400])).toBe(400)
  })

  it('handles 10 elements correctly', () => {
    // idx = floor(10 * 0.2) = 2 → sorted[2] = 550 (from [450, 500, 550, 600, ...])
    const prices = [900, 850, 800, 750, 700, 650, 600, 550, 500, 450]
    expect(percentile20(prices)).toBe(550)
  })

  it('does not mutate the input array', () => {
    const prices = [500, 100, 300]
    const original = [...prices]
    percentile20(prices)
    expect(prices).toEqual(original)
  })
})

// ---------------------------------------------------------------------------
// isGoodTimeToBuy()
// ---------------------------------------------------------------------------

describe('isGoodTimeToBuy', () => {
  it('returns true when price is below p20', () => {
    expect(isGoodTimeToBuy(180, 200)).toBe(true)
  })

  it('returns true when price equals p20', () => {
    expect(isGoodTimeToBuy(200, 200)).toBe(true)
  })

  it('returns false when price is above p20', () => {
    expect(isGoodTimeToBuy(250, 200)).toBe(false)
  })

  it('handles zero price correctly', () => {
    expect(isGoodTimeToBuy(0, 200)).toBe(true)
  })

  it('handles equal prices at the boundary', () => {
    expect(isGoodTimeToBuy(199.99, 200)).toBe(true)
    expect(isGoodTimeToBuy(200.01, 200)).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// getPriceHistory() — mocked fetch
// ---------------------------------------------------------------------------

describe('getPriceHistory', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('fetches from /api/paddles/[id]/price-history with default 90 days', async () => {
    const mockData = [
      { retailer: 'Mercado Livre', date: '2024-01-01', price: 350, p20: 300, is_good_time: false },
    ]
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    } as Response)

    const result = await getPriceHistory(42)

    expect(fetch).toHaveBeenCalledWith('/api/paddles/42/price-history?days=90')
    expect(result).toEqual(mockData)
  })

  it('passes custom days parameter', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [],
    } as Response)

    await getPriceHistory(7, 180)

    expect(fetch).toHaveBeenCalledWith('/api/paddles/7/price-history?days=180')
  })

  it('returns empty array when fetch fails (non-ok response)', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({ error: 'Not found' }),
    } as Response)

    const result = await getPriceHistory(99)
    expect(result).toEqual([])
  })

  it('returns empty array when fetch throws a network error', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'))

    const result = await getPriceHistory(99)
    expect(result).toEqual([])
  })
})
