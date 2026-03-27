import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import type { PaddleListResponse } from '@/types/paddle'

// Mock global fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('API client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('Test 3: fetchPaddles calls correct URL with query params and returns typed response', async () => {
    const mockResponse: PaddleListResponse = {
      items: [
        {
          id: 1,
          name: 'Test Paddle',
          brand: 'TestBrand',
          created_at: '2024-01-01T00:00:00Z',
        },
      ],
      total: 1,
      limit: 20,
      offset: 0,
    }

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const { fetchPaddles } = await import('@/lib/api')
    const result = await fetchPaddles({ brand: 'TestBrand', limit: 20 })

    expect(mockFetch).toHaveBeenCalledOnce()
    const calledUrl = mockFetch.mock.calls[0][0] as string
    expect(calledUrl).toContain('/paddles')
    expect(calledUrl).toContain('brand=TestBrand')
    expect(calledUrl).toContain('limit=20')
    expect(result.items).toHaveLength(1)
    expect(result.items[0].name).toBe('Test Paddle')
  })

  it('Test 4: fetchPaddles returns empty list on 503 (backend unreachable) — no throw', async () => {
    mockFetch.mockRejectedValueOnce(new Error('ECONNREFUSED'))

    const { fetchPaddles } = await import('@/lib/api')
    const result = await fetchPaddles()

    expect(result.items).toEqual([])
    expect(result.total).toBe(0)
  })

  it('Test 5: API client uses NEXT_PUBLIC_FASTAPI_URL env var as base', async () => {
    // Reset module cache to pick up env var
    vi.resetModules()

    const originalEnv = process.env.NEXT_PUBLIC_FASTAPI_URL
    process.env.NEXT_PUBLIC_FASTAPI_URL = 'http://custom-api:9000'

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items: [], total: 0, limit: 20, offset: 0 }),
    })

    const { fetchPaddles } = await import('@/lib/api')
    await fetchPaddles()

    const calledUrl = mockFetch.mock.calls[0][0] as string
    expect(calledUrl).toContain('http://custom-api:9000')

    process.env.NEXT_PUBLIC_FASTAPI_URL = originalEnv
  })
})
