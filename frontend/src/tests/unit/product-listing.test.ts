// RED: Tests for product listing page ISR and revalidation in lib/seo.ts and lib/revalidate.ts
// These tests will fail until implementation is written.

import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockFetch = vi.fn()
global.fetch = mockFetch

async function importSeo() {
  vi.resetModules()
  return await import('@/lib/seo')
}

async function importRevalidate() {
  vi.resetModules()
  return await import('@/lib/revalidate')
}

const mockPaddleList = [
  {
    id: 1,
    name: 'Selkirk Vanguard Power Air',
    brand: 'Selkirk',
    model_slug: 'vanguard-power-air',
    image_url: 'https://example.com/selkirk.jpg',
    price_brl: 1299.99,
    created_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'JOOLA Ben Johns Hyperion',
    brand: 'JOOLA',
    model_slug: 'ben-johns-hyperion',
    image_url: 'https://example.com/joola.jpg',
    price_brl: 999.99,
    created_at: '2026-01-02T00:00:00Z',
  },
]

describe('fetchPaddlesList', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('fetches paddles list and returns paddles array', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        paddles: mockPaddleList,
        total: 2,
        page: 1,
        per_page: 50,
      }),
    })
    const { fetchPaddlesList } = await importSeo()
    const result = await fetchPaddlesList({ page: 1, per_page: 50 })
    expect(Array.isArray(result.paddles)).toBe(true)
    expect(result.paddles.length).toBe(2)
    expect(result.total).toBe(2)
  })

  it('returns empty array when fetch fails', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false })
    const { fetchPaddlesList } = await importSeo()
    const result = await fetchPaddlesList({ page: 1, per_page: 50 })
    expect(result.paddles).toEqual([])
    expect(result.total).toBe(0)
  })

  it('handles backend returning items key instead of paddles key', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        items: mockPaddleList,
        total: 2,
        limit: 50,
        offset: 0,
      }),
    })
    const { fetchPaddlesList } = await importSeo()
    const result = await fetchPaddlesList({ page: 1, per_page: 50 })
    expect(result.paddles.length).toBe(2)
  })
})

describe('revalidatePaddlePages', () => {
  it('exports revalidatePaddlePages function', async () => {
    const { revalidatePaddlePages } = await importRevalidate()
    expect(typeof revalidatePaddlePages).toBe('function')
  })

  it('revalidatePaddlePages can be called without error', async () => {
    const { revalidatePaddlePages } = await importRevalidate()
    await expect(revalidatePaddlePages()).resolves.not.toThrow()
  })

  it('revalidatePaddlePages can be called with paddle id without error', async () => {
    const { revalidatePaddlePages } = await importRevalidate()
    await expect(revalidatePaddlePages(1)).resolves.not.toThrow()
  })
})

describe('revalidateWebhook', () => {
  it('exports revalidateWebhook function', async () => {
    const { revalidateWebhook } = await importRevalidate()
    expect(typeof revalidateWebhook).toBe('function')
  })

  it('returns 401 when Authorization header is missing', async () => {
    const { revalidateWebhook } = await importRevalidate()
    const req = new Request('http://localhost/api/webhooks/revalidate', {
      method: 'POST',
      headers: {},
      body: JSON.stringify({}),
    })
    const res = await revalidateWebhook(req)
    expect(res.status).toBe(401)
  })

  it('returns 401 when Authorization header is wrong', async () => {
    const { revalidateWebhook } = await importRevalidate()
    const req = new Request('http://localhost/api/webhooks/revalidate', {
      method: 'POST',
      headers: { authorization: 'Bearer wrong-secret' },
      body: JSON.stringify({}),
    })
    const res = await revalidateWebhook(req)
    expect(res.status).toBe(401)
  })

  it('returns 200 with revalidated:true when secret matches', async () => {
    process.env.REVALIDATE_SECRET = 'test-secret'
    const { revalidateWebhook } = await importRevalidate()
    const req = new Request('http://localhost/api/webhooks/revalidate', {
      method: 'POST',
      headers: { authorization: 'Bearer test-secret' },
      body: JSON.stringify({ paddle_id: 1 }),
    })
    const res = await revalidateWebhook(req)
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.revalidated).toBe(true)
  })
})
